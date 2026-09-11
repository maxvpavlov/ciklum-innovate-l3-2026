"""Client adapter: discovery, capability checks, streaming and cancellation."""
import json
import uuid
import os
from urllib.parse import urlparse
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import a2a_pb2 as p
from google.protobuf.json_format import MessageToDict


async def discover_client(http, url, streaming=True, polling=False):
    from incident.security import validate_endpoint
    validate_endpoint(url, set(os.getenv("A2A_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")), allow_loopback=True)
    card = await A2ACardResolver(http, base_url=url).get_agent_card()
    # Discovery metadata must not redirect an authenticated client to another host.
    if any(urlparse(i.url).netloc != urlparse(url).netloc for i in card.supported_interfaces):
        raise ValueError("untrusted_agent_interface")
    if not any(skill.id == "runbooks" for skill in card.skills):
        raise ValueError("unsupported_capability")
    return ClientFactory(ClientConfig(httpx_client=http, streaming=streaming, polling=polling)).create(card)


def request_for(task):
    return p.SendMessageRequest(message=p.Message(message_id=uuid.uuid4().hex,
        role=p.Role.ROLE_USER, parts=[p.Part(text=task)]))


class RemoteSpecialist:
    def __init__(self, url, token="demo-specialist-token"):
        self.url, self.token = url, token

    async def investigate(self, task, context):
        if context.tenant != "acme":
            raise PermissionError("specialist_tenant_mismatch")
        async with httpx.AsyncClient(headers={"Authorization": "Bearer "+self.token}, timeout=10) as http:
            client = await discover_client(http, self.url)
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
    async with httpx.AsyncClient(headers={"Authorization": "Bearer demo-specialist-token"}, timeout=10) as http:
        client = await discover_client(http, url, streaming=False, polling=True)
        try:
            async for event in client.send_message(request_for("SLOW INC-001 payments")):
                task_id = event.task.id
                break
            task = await client.cancel_task(p.CancelTaskRequest(id=task_id))
            return p.TaskState.Name(task.status.state)
        finally:
            await client.close()
