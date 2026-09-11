"""Persist run snapshots separately from approval decisions and mock effects."""
from dataclasses import replace
import json
import sqlite3
import time
from incident.core import Context, Run, run_agent
from incident.tools import action_key


class RunStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS runs (tenant TEXT, id TEXT, status TEXT, body TEXT, PRIMARY KEY(tenant,id))")
        self.db.execute("CREATE TABLE IF NOT EXISTS approvals (tenant TEXT, run_id TEXT, key TEXT, expires REAL, decision TEXT, PRIMARY KEY(tenant,run_id,key))")

    def save(self, run):
        self.db.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?)",
            (run.context.tenant, run.context.run_id, run.status, json.dumps(run.snapshot())))

    def load(self, tenant, run_id):
        row = self.db.execute("SELECT body FROM runs WHERE tenant=? AND id=?", (tenant, run_id)).fetchone()
        if not row:
            raise KeyError("run_not_found")
        body = json.loads(row[0]); body["context"] = Context(**body["context"])
        return Run(**body)

    def decide(self, tenant, run_id, decision="approve", ttl=300):
        if decision not in {"approve", "deny"}:
            raise ValueError("invalid_decision")
        run = self.load(tenant, run_id)
        if run.status != "waiting_approval" or not run.pending:
            raise ValueError("no_pending_approval")
        call = run.pending[0]
        key = action_key(call["name"], call["args"], run.context)
        self.db.execute("INSERT OR REPLACE INTO approvals VALUES (?,?,?,?,?)",
                        (tenant, run_id, key, time.time()+ttl, decision))
        if decision == "deny":
            run.status = "denied"; self.save(run)
        return {"key": key, "name": call["name"], "args": call["args"], "decision": decision}

    def approved_keys(self, tenant, run_id):
        return tuple(r[0] for r in self.db.execute(
            "SELECT key FROM approvals WHERE tenant=? AND run_id=? AND decision='approve' AND expires>?",
            (tenant, run_id, time.time())))


async def resume_run(store, tenant, run_id, provider, tools):
    run = store.load(tenant, run_id)
    if run.status == "completed":
        return run
    if run.status in {"denied", "cancelled"}:
        raise PermissionError("terminal_run")
    run.context = replace(run.context, approved=store.approved_keys(tenant, run_id))
    task = next(m["content"] for m in run.messages if m["role"] == "user")
    return await run_agent(provider, tools.execute, tools.available(run.context), task,
                           initial=run, checkpoint=store.save)

