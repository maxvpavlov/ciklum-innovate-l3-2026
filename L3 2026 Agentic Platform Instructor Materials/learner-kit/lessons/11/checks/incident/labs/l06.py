import asyncio
import time
from incident.coordination import WorkItem, bounded_review, schedule
from incident.context import EvidenceStore
from incident.providers import MockProvider
from incident.supervisor import Supervisor


async def demo():
    supervisor = Supervisor()
    parent = await supervisor.investigate()
    assert len(supervisor.children) == 2 and parent.answer["cause"] == "connection_pool_exhaustion"
    assert all(c.context.parent_id == parent.context.run_id for c in supervisor.children)
    timings = {}
    for parallel in [False, True]:
        timed = Supervisor(worker_factory=lambda: MockProvider(latency=.02))
        start = time.monotonic()
        run = await timed.investigate(parallel=parallel)
        timings["parallel" if parallel else "sequential"] = round((time.monotonic()-start)*1000, 2)
        assert run.answer["cause"] == "connection_pool_exhaustion"
    async def worker(item):
        await asyncio.sleep(item.payload["delay"])
        return {"ok": True, "source": item.id}
    partial = await schedule([WorkItem("fast", {"delay": .001}),
                              WorkItem("slow", {"delay": .2})], worker, deadline=.03)
    async def reject(artifact):
        return {"accepted": False, "reason": "contradictory evidence"}
    async def unchanged(artifact, decision):
        return artifact
    review = await bounded_review(run.answer, unchanged, reject)
    version = EvidenceStore().save_artifact("astro", "reviewed-report", review["artifact"])
    assert partial["status"] == "partial" and review["status"] == "escalated"
    return {"parent": parent.context.run_id, "answer": parent.answer,
            "children": [{"role": c.context.role, "tools": c.context.allowed,
                          "tokens": c.tokens} for c in supervisor.children],
            "shared_tokens_spent": supervisor.budget.spent, "timings_ms": timings,
            "partial": partial, "review": review["status"], "artifact_version": version}
