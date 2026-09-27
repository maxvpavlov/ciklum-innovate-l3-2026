"""Admission controls, evidence-based releases, and safe trace presentation."""
from collections import defaultdict, deque
import hashlib
import html
import json
import sqlite3
import statistics
import time
from agent_runtime.security import redact


class CapacityError(RuntimeError):
    pass


class Admission:
    def __init__(self, max_pending=8, per_second=5):
        self.max_pending, self.per_second = max_pending, per_second
        self.pending = 0
        self.arrivals = defaultdict(deque)

    def enter(self, tenant):
        if self.pending >= self.max_pending:
            raise CapacityError("queue_full")
        times, now = self.arrivals[tenant], time.monotonic()
        while times and times[0] <= now-1:
            times.popleft()
        if len(times) >= self.per_second:
            raise CapacityError("rate_limited")
        times.append(now); self.pending += 1

    def leave(self):
        self.pending -= 1


def build_trace(store, tenant, run_id):
    parent = store.load(tenant, run_id)
    children = []
    for row in store.db.execute("SELECT body FROM runs WHERE tenant=?", (tenant,)):
        body = json.loads(row[0])
        if body["context"].get("parent_id") == run_id:
            children.append(body)
    nodes = [parent.snapshot()] + children
    return redact({"root_id": run_id, "status": parent.status,
        "total_tokens": sum(n["tokens"] for n in nodes),
        "nodes": [{"id": n["context"]["run_id"], "parent_id": n["context"]["parent_id"],
                   "role": n["context"]["role"], "status": n["status"], "tokens": n["tokens"],
                   "events": n["events"]} for n in nodes]})


def trace_html(trace):
    rows = []
    for node in trace["nodes"]:
        for event in node["events"]:
            values = [node["role"], node["id"][:12], (node["parent_id"] or "")[:12],
                event["kind"], event.get("name", ""), event.get("tokens", ""),
                round(event.get("elapsed_ms", 0), 2), event.get("code", node["status"])]
            rows.append("<tr>"+"".join("<td>"+html.escape(str(v))+"</td>" for v in values)+"</tr>")
    return ('<!doctype html><meta charset="utf-8"><title>Incident run trace</title>'
        '<style>body{font:16px system-ui;margin:32px;color:#17202a}table{border-collapse:collapse;width:100%}'
        'td,th{border:1px solid #ddd;padding:8px;text-align:left}th{background:#eef2f5}</style>'
        '<h1>Incident run trace</h1><p>Status: '+html.escape(trace["status"])+
        ' | Parent and child tokens: '+str(trace["total_tokens"])+
        '</p><table><tr>'+''.join('<th>'+h+'</th>' for h in
        ['Role','Run','Parent','Event','Tool','Tokens','Tool ms','Status'])+'</tr>'+''.join(rows)+'</table>')


def release_gate(baseline, candidate, min_success=1.0, max_latency_ms=1000, max_tokens=200):
    checks = {
        "same_dataset": baseline["dataset_sha256"] == candidate["dataset_sha256"],
        "same_split": baseline["split"] == candidate["split"],
        "quality": candidate["success_rate"] >= max(min_success, baseline["success_rate"]),
        "latency": candidate["mean_latency_ms"] <= max_latency_ms,
        "tokens": candidate["mean_tokens"] <= max_tokens,
    }
    return {"approved": all(checks.values()), "checks": checks}


async def evaluate_platform(platform, name, version, trials=1):
    from agent_runtime.evaluate import CASES, grade
    rows = []
    for case in CASES:
        for trial in range(trials):
            started = time.perf_counter()
            run_id = platform.submit(case["tenant"], "analyst", case["incident"], name, version)
            run = await platform.wait(case["tenant"], run_id)
            rows.append({"case": case["id"], "trial": trial,
                         "passed": all(grade(run, case).values()), "tokens": run.tokens,
                         "elapsed_ms": (time.perf_counter()-started)*1000})
    return {"dataset_sha256": hashlib.sha256(json.dumps(CASES, sort_keys=True).encode()).hexdigest(),
        "configuration": platform.registry.get(name, version), "split": "all",
        "trials": trials, "success_rate": sum(r["passed"] for r in rows)/len(rows),
        "mean_tokens": statistics.mean(r["tokens"] for r in rows),
        "mean_latency_ms": statistics.mean(r["elapsed_ms"] for r in rows), "rows": rows}



class ReleaseLog:
    """Every release decision keeps its evidence, whether or not the candidate was activated."""

    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS releases (ts REAL, agent TEXT, baseline INT, candidate INT, "
                        "approved INT, activated INT, report TEXT)")

    def record(self, baseline, candidate, gate, activated):
        summary = lambda r: {k: r[k] for k in ["success_rate", "mean_tokens", "mean_latency_ms", "trials", "split"]}
        self.db.execute("INSERT INTO releases VALUES (?,?,?,?,?,?,?)", (time.time(), candidate["configuration"]["name"],
            baseline["configuration"]["version"], candidate["configuration"]["version"], int(gate["approved"]),
            int(activated), json.dumps({"checks": gate["checks"], "baseline": summary(baseline),
                                        "candidate": summary(candidate), "dataset_sha256": candidate["dataset_sha256"]})))

    def list(self, limit=20):
        rows = self.db.execute("SELECT ts,agent,baseline,candidate,approved,activated,report FROM releases "
                               "ORDER BY rowid DESC LIMIT ?", (limit,))
        return [{"ts": r[0], "agent": r[1], "baseline_version": r[2], "candidate_version": r[3], "approved": bool(r[4]),
                 "activated": bool(r[5]), **json.loads(r[6])} for r in rows]
