import asyncio
import time
from incident.coordination import WorkItem, bounded_review, schedule
from incident.context import EvidenceStore
from incident.providers import MockProvider
from incident.supervisor import Supervisor


async def demo():
    timings = {}
    for parallel in [False, True]:
        supervisor = Supervisor(worker_factory=lambda: MockProvider(latency=.02))
        start = time.monotonic()
        run = await supervisor.investigate(parallel=parallel)
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
    store = EvidenceStore()
    version = store.save_artifact("acme", "reviewed-report", review["artifact"])
    assert partial["status"] == "partial" and review["status"] == "escalated"
    return {"timings_ms": timings, "partial": partial, "review": review["status"], "artifact_version": version}

