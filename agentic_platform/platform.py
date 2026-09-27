"""Reusable run service combining registry, model, tool, state and artifact adapters."""
import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import uuid
from agent_runtime.core import Context, Run, SYSTEM, run_agent
from agent_runtime.context import EvidenceStore, context_tools, select_context
from agent_runtime.durable import RunStore, resume_run
from agent_runtime.mcp_bridge import MCPReadAdapter, stdio_client
from agent_runtime.providers import MockProvider, provider_from_env
from agentic_platform.registry import Registry
from agent_runtime.supervisor import Supervisor, SupervisorProvider
from agent_runtime.tools import WRITE_SCHEMA, ToolExecutor
from course.fixtures import SCHEMAS


class HybridSupervisor(Supervisor):
    def __init__(self, remote, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote = remote

    async def delegate(self, name, args, parent):
        if args.get("role") != "runbooks":
            return await super().delegate(name, args, parent)
        from jsonschema import validate, ValidationError
        from agent_runtime.supervisor import DELEGATE_SCHEMA
        try:
            validate(args, DELEGATE_SCHEMA["function"]["parameters"])
            if name != "delegate" or "runbook_search" not in parent.allowed:
                raise ValueError("child_privilege_escalation")
            if args["task_id"] in self.contracts:
                raise ValueError("duplicate_remote_task")
            await self.budget.reserve(1800, depth=1)
        except (ValidationError, ValueError) as exc:
            return {"ok": False, "error": type(exc).__name__}
        self.contracts[args["task_id"]] = json.dumps(args, sort_keys=True)
        used = 1800
        try:
            result = await self.remote.investigate(args["objective"], parent)
            used = result["tokens"]
            context = replace(parent, run_id=result["run_id"], parent_id=parent.run_id,
                              role="remote_runbooks", allowed=("runbook_search",), approved=())
            child = Run(context, [], status="completed", answer=result["answer"], tokens=used)
            child.event("remote", protocol="A2A", event_count=len(result["events"]))
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


class Platform:
    def __init__(self, path="var/platform.db", factory=provider_from_env):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path, self.factory = path, factory
        self.store, self.evidence = RunStore(path), EvidenceStore(path)
        self.registry = Registry(path, known_tools=[s["function"]["name"] for s in SCHEMAS+[WRITE_SCHEMA]])
        self.tasks, self.owner = {}, uuid.uuid4().hex
        for name, spec in SEED_AGENTS.items():
            self.registry.register(name, 1, {**spec, "prompt": SYSTEM, "context_chars": 6000})

    async def register_remote_agent(self, url, name="runbook-specialist"):
        """Discover an A2A service and pin its Agent Card in the registry."""
        from agent_runtime.a2a_client import fetch_card
        return self.registry.register_remote(name, url, await fetch_card(url))

    def submit(self, tenant, role, incident_id, agent="single", version=None):
        config = self.registry.get(agent, version)
        if config["state"] == "retired":
            raise ValueError("retired_version")
        if config["spec"]["kind"] == "remediator" and role != "operator":
            raise PermissionError("operator_required")
        context = Context(tenant=tenant, role=role, allowed=tuple(config["spec"]["allowed"]))
        run = Run(context, [{"role": "system", "content": config["spec"]["prompt"]},
                           {"role": "user", "content": f"Investigate {incident_id} payments latency"}],
                  status="queued", configuration=config)
        self.store.save(run)
        self.launch(tenant, context.run_id)
        return context.run_id

    def launch(self, tenant, run_id):
        self.store.claim(tenant, run_id, self.owner)
        key = (tenant, run_id)
        self.tasks[key] = asyncio.create_task(self._execute(tenant, run_id))
        return self.tasks[key]

    async def _execute(self, tenant, run_id):
        run = self.store.load(tenant, run_id)
        tools = ToolExecutor(self.path, read_handler=context_tools)
        try:
            kind = run.configuration["spec"]["kind"]
            if kind == "team":
                async with stdio_client(tenant) as client:
                    kwargs = {"worker_factory": self.factory, "read_handler": MCPReadAdapter(client)}
                    remote = [a for a in self.registry.discover("runbooks") if a["type"] == "remote"]
                    if remote:
                        from agent_runtime.a2a_client import RemoteSpecialist
                        specialist = RemoteSpecialist(remote[0]["url"], os.getenv("A2A_TOKEN", "demo-specialist-token"),
                                                      card_sha256=remote[0]["sha256"])
                        supervisor = HybridSupervisor(specialist, **kwargs)
                    else:
                        supervisor = Supervisor(**kwargs)
                    parent_provider = self.factory()
                    if isinstance(parent_provider, MockProvider):
                        parent_provider = SupervisorProvider()
                    run = await supervisor.investigate(context=run.context, provider=parent_provider,
                        parallel=True, initial=run, checkpoint=self.store.save)
                    for child in supervisor.children:
                        self.store.save(child)
                    run.event("delegation_summary", child_tokens=supervisor.budget.spent,
                              children=[c.context.run_id for c in supervisor.children])
            else:
                if kind == "remediator":
                    from course.labs.l05 import RemediationProvider
                    provider = RemediationProvider()
                else:
                    provider = self.factory()
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

