"""Dependency-aware scheduling and bounded evidence review."""
import asyncio
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class WorkItem:
    id: str
    payload: dict
    depends_on: tuple[str, ...] = ()


async def schedule(items, runner, concurrency=2, deadline=5):
    if concurrency < 1 or deadline <= 0:
        raise ValueError("invalid_scheduler_limits")
    specs = {item.id: item for item in items}
    if len(specs) != len(items):
        raise ValueError("duplicate_task_id")
    visited, visiting = set(), set()
    def visit(key):
        if key not in specs:
            raise ValueError("unknown_dependency")
        if key in visiting:
            raise ValueError("dependency_cycle")
        if key in visited:
            return
        visiting.add(key)
        for dep in specs[key].depends_on:
            visit(dep)
        visiting.remove(key); visited.add(key)
    for key in specs:
        visit(key)
    pending, active, results = set(specs), {}, {}
    expires = time.monotonic()+deadline

    async def wrapped(item):
        try:
            data = await runner(item)
            return {"status": "completed" if data.get("ok", True) else "failed", "data": data}
        except Exception as exc:
            return {"status": "failed", "error": type(exc).__name__}

    try:
        while pending or active:
            for key in sorted(pending):
                deps = specs[key].depends_on
                if any(dep in results and results[dep]["status"] != "completed" for dep in deps):
                    results[key] = {"status": "blocked", "error": "dependency_failed"}
                    pending.remove(key)
                elif all(dep in results for dep in deps) and len(active) < concurrency:
                    active[asyncio.create_task(wrapped(specs[key]))] = key
                    pending.remove(key)
            remaining = expires-time.monotonic()
            if remaining <= 0:
                break
            if active:
                done, _ = await asyncio.wait(active, timeout=remaining,
                                             return_when=asyncio.FIRST_COMPLETED)
                if not done:
                    break
                for task in done:
                    results[active.pop(task)] = task.result()
            elif pending:
                continue
        for key in pending | set(active.values()):
            results[key] = {"status": "cancelled", "error": "deadline"}
    finally:
        for task in active:
            task.cancel()
        if active:
            await asyncio.gather(*active, return_exceptions=True)
    return {"status": "completed" if all(r["status"] == "completed" for r in results.values()) else "partial",
            "results": results}


@dataclass(frozen=True)
class Envelope:
    correlation_id: str
    task_id: str
    artifact_id: str
    version: int
    body: dict


def accept_reply(request, reply):
    if (reply.correlation_id, reply.task_id, reply.artifact_id) != (
        request.correlation_id, request.task_id, request.artifact_id):
        raise ValueError("mismatched_reply")
    if reply.version != request.version+1:
        raise ValueError("stale_or_unexpected_artifact")
    return reply.body


async def bounded_review(artifact, producer, reviewer, max_rounds=2):
    history = []
    for number in range(max_rounds):
        decision = await reviewer(artifact)
        history.append(decision)
        if decision["accepted"]:
            return {"status": "accepted", "artifact": artifact, "rounds": number+1, "reviews": history}
        if number+1 < max_rounds:
            artifact = await producer(artifact, decision)
    return {"status": "escalated", "artifact": artifact, "rounds": max_rounds, "reviews": history}

