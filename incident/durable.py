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
        self.db.execute("CREATE TABLE IF NOT EXISTS leases (tenant TEXT, run_id TEXT, owner TEXT, expires REAL, PRIMARY KEY(tenant,run_id))")

    def claim(self, tenant, run_id, owner, seconds=30):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT owner,expires FROM leases WHERE tenant=? AND run_id=?", (tenant,run_id)).fetchone()
            if row and row[1] > time.time():
                raise ValueError("run_already_owned")
            self.db.execute("INSERT OR REPLACE INTO leases VALUES (?,?,?,?)", (tenant,run_id,owner,time.time()+seconds))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK"); raise

    def release(self, tenant, run_id, owner):
        self.db.execute("DELETE FROM leases WHERE tenant=? AND run_id=? AND owner=?", (tenant,run_id,owner))

    def save(self, run):
        self.db.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?)",
            (run.context.tenant, run.context.run_id, run.status, json.dumps(run.snapshot())))

    def load(self, tenant, run_id):
        row = self.db.execute("SELECT body FROM runs WHERE tenant=? AND id=?", (tenant, run_id)).fetchone()
        if not row:
            raise KeyError("run_not_found")
        body = json.loads(row[0]); body["context"] = Context(**body["context"])
        return Run(**body)

    def summaries(self, tenant, parent_id=None, limit=50):
        """Most recently saved runs first, for one tenant only; the console never reads other tenants."""
        rows = self.db.execute("SELECT body FROM runs WHERE tenant=? ORDER BY rowid DESC", (tenant,))
        result = []
        for (body,) in rows:
            run = json.loads(body)
            if parent_id is not None and run["context"]["parent_id"] != parent_id:
                continue
            config = run.get("configuration") or {}
            result.append({"id": run["context"]["run_id"], "status": run["status"],
                           "role": run["context"]["role"], "parent_id": run["context"]["parent_id"],
                           "agent": config.get("name"), "version": config.get("version"),
                           "tokens": run["tokens"], "error": run["error"]})
            if len(result) >= limit:
                break
        return result

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
