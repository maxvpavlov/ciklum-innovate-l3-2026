"""Tenant-scoped retrieval, complete message rounds and versioned artifacts."""
import json
import re
import sqlite3
import time
from incident.fixtures import RUNBOOKS, simple_tools


def retrieve(query, tenant, limit=2):
    words = set(re.findall(r"[a-z]+", query.lower().replace("_", " ")))
    ranked = [(len(words & set(r["text"].split())), r) for r in RUNBOOKS if r["tenant"] == tenant]
    return [r for score, r in sorted(ranked, key=lambda x: (-x[0], x[1]["source_id"]))
            if score > 0][:limit]


async def context_tools(name, args, context):
    if name == "runbook_search":
        return {"ok": True, "data": retrieve(args["query"], context.tenant)}
    return await simple_tools(name, args, context)


def select_context(messages, max_chars=6000):
    """Keep instruction/task and newest COMPLETE tool rounds; never orphan tool IDs."""
    head, rounds, current = messages[:2], [], []
    for message in messages[2:]:
        if message["role"] == "assistant" and current:
            rounds.append(current)
            current = []
        current.append(message)
    if current:
        rounds.append(current)
    retained = []
    for group in reversed(rounds):
        candidate = head + group + retained
        if len(json.dumps(candidate)) > max_chars:
            break
        retained = group + retained
    if len(json.dumps(head)) > max_chars:
        raise ValueError("task_exceeds_context_budget")
    return head + retained


class EvidenceStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS artifacts (tenant TEXT, id TEXT, version INT, body TEXT, PRIMARY KEY(tenant,id,version))")
        self.db.execute("CREATE TABLE IF NOT EXISTS memories (tenant TEXT, key TEXT, body TEXT, expires REAL, PRIMARY KEY(tenant,key))")

    def save_artifact(self, tenant, artifact_id, body, expected_version=0):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            version = self.db.execute("SELECT COALESCE(MAX(version),0) FROM artifacts WHERE tenant=? AND id=?",
                                      (tenant, artifact_id)).fetchone()[0]
            if version != expected_version:
                raise ValueError("stale_artifact_version")
            self.db.execute("INSERT INTO artifacts VALUES (?,?,?,?)",
                            (tenant, artifact_id, version+1, json.dumps(body)))
            self.db.execute("COMMIT")
            return version+1
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def artifact(self, tenant, artifact_id):
        row = self.db.execute("SELECT version,body FROM artifacts WHERE tenant=? AND id=? ORDER BY version DESC LIMIT 1",
                              (tenant, artifact_id)).fetchone()
        return {"version": row[0], "body": json.loads(row[1])} if row else None

    def remember(self, tenant, key, body, ttl=3600):
        self.db.execute("INSERT OR REPLACE INTO memories VALUES (?,?,?,?)",
                        (tenant, key, json.dumps(body), time.time()+ttl))

    def recall(self, tenant, key):
        row = self.db.execute("SELECT body FROM memories WHERE tenant=? AND key=? AND expires>?",
                              (tenant, key, time.time())).fetchone()
        return json.loads(row[0]) if row else None

