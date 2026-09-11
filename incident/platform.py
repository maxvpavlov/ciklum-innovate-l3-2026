"""Reusable run service combining model, tool, state and artifact adapters."""
import asyncio
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import uuid
from incident.core import Context, Run, SYSTEM, run_agent
from incident.context import EvidenceStore, context_tools, select_context
from incident.durable import RunStore, resume_run
from incident.mcp_bridge import MCPReadAdapter, stdio_client
from incident.providers import MockProvider, provider_from_env
from incident.supervisor import Supervisor, SupervisorProvider
from incident.tools import ToolExecutor


class Definitions:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS definitions (name TEXT, version INT, body TEXT, hash TEXT, PRIMARY KEY(name,version))")

    def put(self, name, version, spec):
        body = json.dumps(spec, sort_keys=True)
        digest = hashlib.sha256(body.encode()).hexdigest()
        old = self.db.execute("SELECT hash FROM definitions WHERE name=? AND version=?", (name,version)).fetchone()
        if old and old[0] != digest:
            raise ValueError("immutable_definition")
        self.db.execute("INSERT OR IGNORE INTO definitions VALUES (?,?,?,?)", (name,version,body,digest))

    def get(self, name, version=1):
        row = self.db.execute("SELECT body,hash FROM definitions WHERE name=? AND version=?", (name,version)).fetchone()
        if not row:
            raise KeyError("unknown_agent_version")
        return {"name": name, "version": version, "spec": json.loads(row[0]), "sha256": row[1]}


class HybridSupervisor(Supervisor):
    def __init__(self, remote, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remote = remote

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


class Platform:
    def __init__(self, path="var/platform.db", remote_url=None, factory=provider_from_env):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path, self.factory = path, factory
        self.store, self.evidence, self.definitions = RunStore(path), EvidenceStore(path), Definitions(path)
        self.remote_url = remote_url
        self.tasks, self.owner = {}, uuid.uuid4().hex
        for name, kind, allowed in [
            ("single", "single", ["log_lookup", "runbook_search"]),
            ("team", "team", ["log_lookup", "runbook_search"]),
            ("remediator", "remediator", ["mock_remediate"]),
        ]:
            self.definitions.put(name, 1, {"kind": kind, "allowed": allowed,
                                          "prompt": SYSTEM, "context_chars": 6000})

    def submit(self, tenant, role, incident_id, agent="single", version=1):
        config = self.definitions.get(agent, version)
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
                    if self.remote_url:
                        from incident.a2a_client import RemoteSpecialist
                        supervisor = HybridSupervisor(RemoteSpecialist(self.remote_url, os.getenv("A2A_TOKEN", "demo-specialist-token")), **kwargs)
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
                    from incident.labs.l05 import RemediationProvider
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

