"""Reusable run service combining registry, gateway, identity, model, state and artifact adapters."""
import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import uuid
from incident.core import Context, Run, SYSTEM, run_agent
from incident.context import EvidenceStore, select_context
from incident.durable import RunStore, resume_run
from incident.gateway import ToolGateway
from incident.identity import DEV_SIGNING_KEY, CredentialStore, Delegation, TokenIssuer
from incident.operations import Admission, CapacityError, ReleaseLog
from incident.providers import MockProvider, provider_from_env
from incident.registry import Registry
from incident.supervisor import Supervisor, SupervisorProvider
from incident.tools import WRITE_SCHEMA
from incident.fixtures import SCHEMAS


class HybridSupervisor(Supervisor):
    def __init__(self, remote, *args, remote_grant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote, self.remote_grant = remote, remote_grant

    async def delegate(self, name, args, parent):
        if args.get("role") != "runbooks":
            return await super().delegate(name, args, parent)
        from jsonschema import validate, ValidationError
        from incident.supervisor import DELEGATE_SCHEMA
        try:
            validate(args, DELEGATE_SCHEMA["function"]["parameters"])
            if name != "delegate" or "runbook_search" not in parent.allowed:
                raise ValueError("child_privilege_escalation")
            if args["task_id"] in self.contracts:
                raise ValueError("duplicate_remote_task")
            context = replace(parent, run_id=uuid.uuid4().hex, parent_id=parent.run_id,
                              role="remote_runbooks", allowed=("runbook_search",), approved=())
            token = self.remote_grant(parent, context) if self.remote_grant else None
            await self.budget.reserve(1800, depth=1)
        except (ValidationError, ValueError, PermissionError) as exc:
            return {"ok": False, "error": type(exc).__name__}
        self.contracts[args["task_id"]] = json.dumps(args, sort_keys=True)
        used = 1800
        try:
            result = await self.remote.investigate(args["objective"], parent, token=token)
            used = result["tokens"]
            child = Run(context, [], status="completed", answer=result["answer"], tokens=used)
            child.event("remote", protocol="A2A", remote_run_id=result["run_id"], event_count=len(result["events"]))
            self.children.append(child)
            return {"ok": True, "data": child.answer, "child_run_id": context.run_id,
                    "task_id": args["task_id"], "status": "completed"}
        finally:
            await self.budget.settle(1800, used)


SEED_AGENTS = {
    "single": {"kind": "single", "description": "One agent reads logs and runbooks and cites evidence.",
               "owner": "platform-team", "allowed": ["log_lookup", "runbook_search"],
               "skills": ["incident-investigation"]},
    "team": {"kind": "team", "description": "A supervisor delegates log and runbook work to scoped workers.",
             "owner": "platform-team", "allowed": ["log_lookup", "runbook_search"],
             "skills": ["incident-investigation", "delegation"]},
    "remediator": {"kind": "remediator", "description": "Operator-only mock rollback behind exact-action approval.",
                   "owner": "sre-team", "allowed": ["mock_remediate"], "skills": ["mock-remediation"]},
}

SEED_TOOL_SERVERS = {
    "incident-tools": {"transport": "mcp-stdio", "tenants": ["astro", "locomotive"],
                       "tools": {"log_lookup": {"risk": "read"}, "runbook_search": {"risk": "read"}}},
    "platform-actions": {"transport": "local", "tenants": ["astro", "locomotive"],
                         "tools": {"mock_remediate": {"risk": "write"}}},
}


class Platform:
    def __init__(self, path="var/platform.db", factory=None, admission=None, workers=2, total_token_budget=6000):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.admission, self.semaphore = admission or Admission(), asyncio.Semaphore(workers)
        self.workers, self.total_token_budget = workers, total_token_budget
        self.store, self.evidence, self.releases = RunStore(path), EvidenceStore(path), ReleaseLog(path)
        self.secrets = CredentialStore(path)
        self.secrets.put("secret://platform/signing-key", os.getenv("PLATFORM_SIGNING_KEY", DEV_SIGNING_KEY), {"identity"})
        if os.getenv("MODEL_API_KEY"):
            self.secrets.put("secret://model/api-key", os.environ["MODEL_API_KEY"], {"model-adapter"})
        self.factory = factory or (lambda: provider_from_env(self.secrets))
        self.issuer = TokenIssuer(self.secrets.lease("secret://platform/signing-key", "identity").reveal())
        self.credentials = Delegation(self.issuer, path)
        self.registry = Registry(path, known_tools=[s["function"]["name"] for s in SCHEMAS+[WRITE_SCHEMA]])
        for name, manifest in SEED_TOOL_SERVERS.items():
            self.registry.register_tool_server(name, manifest)
        self.gateway = ToolGateway(self.registry, path, credentials=self.credentials)
        self.tasks, self.owner = {}, uuid.uuid4().hex
        for name, spec in SEED_AGENTS.items():
            self.registry.register(name, 1, {**spec, "prompt": SYSTEM, "context_chars": 6000})

    async def close(self):
        await self.gateway.close()

    async def register_remote_agent(self, url, name="runbook-specialist"):
        """Discover an A2A service and pin its Agent Card in the registry."""
        from incident.a2a_client import fetch_card
        return self.registry.register_remote(name, url, await fetch_card(url))

    def submit(self, tenant, role, incident_id, agent="single", version=None, subject=None):
        config = self.registry.get(agent, version)
        if config["state"] == "retired":
            raise ValueError("retired_version")
        if config["spec"]["kind"] == "remediator" and role != "operator":
            raise PermissionError("operator_required")
        context = Context(tenant=tenant, role=role, allowed=tuple(config["spec"]["allowed"]),
                          subject=subject or f"user:{tenant}-{role}")
        run = Run(context, [{"role": "system", "content": config["spec"]["prompt"]},
                           {"role": "user", "content": f"Investigate {incident_id} payments latency"}],
                  status="queued", configuration=config)
        self.store.save(run)
        try:
            self.launch(tenant, context.run_id)
        except CapacityError as exc:
            run.status, run.error = "rejected", str(exc)
            self.store.save(run)
            raise
        return context.run_id

    def launch(self, tenant, run_id):
        self.admission.enter(tenant)
        try:
            self.store.claim(tenant, run_id, self.owner)
        except BaseException:
            self.admission.leave(); raise
        key = (tenant, run_id)
        self.tasks[key] = asyncio.create_task(self._worker(tenant, run_id))
        return self.tasks[key]

    async def _worker(self, tenant, run_id):
        try:
            async with self.semaphore:
                return await self._execute(tenant, run_id)
        finally:
            self.admission.leave()
            self.store.release(tenant, run_id, self.owner)
            self.tasks.pop((tenant,run_id), None)

    async def _execute(self, tenant, run_id):
        run = self.store.load(tenant, run_id)
        tools = self.gateway
        try:
            config = run.configuration
            # Delegated credentials are minted per execution and are never saved with the run.
            self.credentials.for_run(run.context, run.context.subject or f"user:{tenant}",
                                     f"agent:{config['name']}@v{config['version']}")
            kind = config["spec"]["kind"]
            if kind == "team":
                from incident.supervisor import SharedBudget
                kwargs = {"worker_factory": self.factory, "tools": self.gateway, "grant": self.credentials.for_child,
                          "budget": SharedBudget(remaining=self.total_token_budget)}
                remote = [a for a in self.registry.discover("runbooks") if a["type"] == "remote"]
                if remote:
                    from incident.a2a_client import RemoteSpecialist
                    specialist = RemoteSpecialist(remote[0]["url"], card_sha256=remote[0]["sha256"])
                    supervisor = HybridSupervisor(specialist, **kwargs, remote_grant=lambda parent, child:
                        self.credentials.for_child(parent, child, audience="agent:runbook-specialist",
                                                   actor="agent:runbook-specialist"))
                else:
                    supervisor = Supervisor(**kwargs)
                parent_provider = self.factory()
                if isinstance(parent_provider, MockProvider):
                    parent_provider = SupervisorProvider()
                run = await supervisor.investigate(context=run.context, provider=parent_provider,
                    parallel=True, initial=run, checkpoint=self.store.save)
                for child in supervisor.children:
                    self.store.save(child)
                run.event("delegation_summary", shared_tokens_spent=supervisor.budget.spent,
                          children=[c.context.run_id for c in supervisor.children])
            else:
                if kind == "remediator":
                    from incident.labs.l05 import RemediationProvider
                    provider = RemediationProvider()
                else:
                    provider = self.factory()
                    if isinstance(provider, MockProvider) and config["spec"].get("provider_profile") == "efficient":
                        from incident.tuning import EfficientMockProvider
                        provider = EfficientMockProvider()
                if run.status == "waiting_approval" or run.pending:
                    run = await resume_run(self.store, tenant, run_id, provider, tools)
                else:
                    run = await run_agent(provider, tools.execute, tools.available(run.context),
                        run.messages[1]["content"], initial=run, checkpoint=self.store.save,
                        select_messages=lambda messages: select_context(messages, run.configuration["spec"]["context_chars"]))
            if run.answer:
                previous = self.evidence.artifact(tenant, run_id)
                self.evidence.save_artifact(tenant, run_id, run.answer,
                    expected_version=previous["version"] if previous else 0)
            self.store.save(run)
            return run
        except asyncio.CancelledError:
            run.status = "cancelled"; self.store.save(run); raise
        except Exception as exc:
            run.status, run.error = "failed", type(exc).__name__
            run.event("failure", code=run.error); self.store.save(run)
            return run
        finally:
            self.credentials.revoke(run_id)
            self.store.release(tenant, run_id, self.owner)
            self.tasks.pop((tenant,run_id), None)

    async def wait(self, tenant, run_id):
        task = self.tasks.get((tenant,run_id))
        if task:
            await task
        return self.store.load(tenant, run_id)

    async def cancel(self, tenant, run_id):
        run = self.store.load(tenant, run_id)
        if run.status in {"completed", "denied", "cancelled"}:
            raise ValueError("terminal_run")
        task = self.tasks.get((tenant,run_id))
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        run = self.store.load(tenant, run_id)
        run.status = "cancelled"; self.store.save(run)

