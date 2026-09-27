"""Client adapter: discovery, capability checks, streaming and cancellation."""
import json
import uuid
import os
from urllib.parse import urlparse
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import a2a_pb2 as p
from google.protobuf.json_format import MessageToDict


def card_dict(card):
    return MessageToDict(card, preserving_proto_field_name=True)


async def fetch_card(url):
    """Read the public Agent Card so the platform registry can pin it."""
    async with httpx.AsyncClient(timeout=10) as http:
        return card_dict(await A2ACardResolver(http, base_url=url).get_agent_card())


async def discover_client(http, url, streaming=True, polling=False, pinned=None):
    from incident.security import validate_endpoint
    validate_endpoint(url, set(os.getenv("A2A_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")), allow_loopback=True)
    card = await A2ACardResolver(http, base_url=url).get_agent_card()
    # Discovery metadata must not redirect an authenticated client to another host.
    if any((urlparse(i.url).scheme, urlparse(i.url).netloc) !=
           (urlparse(url).scheme, urlparse(url).netloc) for i in card.supported_interfaces):
        raise ValueError("untrusted_agent_interface")
    if pinned:
        from incident.registry import digest
        if digest(card_dict(card)) != pinned:
            raise ValueError("agent_card_changed")
    if not any(skill.id == "runbooks" for skill in card.skills):
        raise ValueError("unsupported_capability")
    return ClientFactory(ClientConfig(httpx_client=http, streaming=streaming, polling=polling)).create(card)


def request_for(task):
    return p.SendMessageRequest(message=p.Message(message_id=uuid.uuid4().hex,
        role=p.Role.ROLE_USER, parts=[p.Part(text=task)]))


def lab_token(context, audience="agent:runbook-specialist"):
    """A short-lived delegated token for local labs; the platform mints its own grants."""
    from incident.identity import TokenIssuer
    return TokenIssuer().issue({"sub": "user:local-lab", "tenant": context.tenant, "role": context.role,
        "aud": audience, "scope": "runbook_search", "act": {"sub": "agent:local-lab"}}, ttl=60)


class RemoteSpecialist:
    def __init__(self, url, token_source=lab_token, card_sha256=None):
        self.url, self.token_source, self.card_sha256 = url, token_source, card_sha256

    async def investigate(self, task, context, token=None):
        if context.tenant != "acme":
            raise PermissionError("specialist_tenant_mismatch")
        token = token or self.token_source(context)
        async with httpx.AsyncClient(headers={"Authorization": "Bearer "+token}, timeout=10) as http:
            client = await discover_client(http, self.url, pinned=self.card_sha256)
            evidence, final, events = None, None, []
            try:
                async for event in client.send_message(request_for(task)):
                    data = MessageToDict(event, preserving_proto_field_name=True)
                    events.append(data)
                    if event.HasField("artifact_update"):
                        for part in event.artifact_update.artifact.parts:
                            if part.text:
                                evidence = json.loads(part.text)
                    if event.HasField("status_update"):
                        final = event.status_update.status.state
                if final != p.TaskState.TASK_STATE_COMPLETED or evidence is None:
                    raise RuntimeError("incomplete_remote_task")
                return {**evidence, "events": events}
            finally:
                await client.close()


async def cancel_slow_task(url):
    from incident.core import Context
    async with httpx.AsyncClient(headers={"Authorization": "Bearer "+lab_token(Context())}, timeout=10) as http:
        client = await discover_client(http, url, streaming=False, polling=True)
        try:
            async for event in client.send_message(request_for("SLOW INC-001 payments")):
                task_id = event.task.id
                break
            task = await client.cancel_task(p.CancelTaskRequest(id=task_id))
            return p.TaskState.Name(task.status.state)
        finally:
            await client.close()

