import asyncio
from dataclasses import replace
import pytest
from incident.coordination import Envelope, WorkItem, accept_reply, bounded_review, schedule


async def test_scheduler_enforces_dependencies_and_concurrency():
    active, peak, ended = 0, 0, set()
    async def worker(item):
        nonlocal active, peak
        assert set(item.depends_on) <= ended
        active += 1; peak = max(peak, active)
        await asyncio.sleep(.005)
        active -= 1; ended.add(item.id)
        return {"ok": True}
    report = await schedule([WorkItem("a", {}), WorkItem("b", {}),
                             WorkItem("c", {}, ("a", "b"))], worker, concurrency=2)
    assert peak == 2 and report["status"] == "completed"


async def test_deadline_keeps_fast_result_and_cancels_worker():
    cancelled = []
    async def worker(item):
        try:
            await asyncio.sleep(item.payload["delay"])
            return {"ok": True}
        except asyncio.CancelledError:
            cancelled.append(item.id); raise
    report = await schedule([WorkItem("fast", {"delay": 0}), WorkItem("slow", {"delay": 1})], worker, deadline=.01)
    assert report["status"] == "partial"
    assert report["results"]["fast"]["status"] == "completed"
    assert cancelled == ["slow"]


async def test_cycles_failed_dependencies_and_review_bound():
    async def fail(item):
        raise RuntimeError("worker failed")
    with pytest.raises(ValueError, match="dependency_cycle"):
        await schedule([WorkItem("a", {}, ("b",)), WorkItem("b", {}, ("a",))], fail)
    report = await schedule([WorkItem("a", {}), WorkItem("b", {}, ("a",))], fail)
    assert report["results"]["b"]["status"] == "blocked"
    async def reject(value): return {"accepted": False}
    async def produce(value, decision): return value
    assert (await bounded_review({}, produce, reject))["status"] == "escalated"


def test_reply_correlation_and_stale_artifact():
    request = Envelope("corr", "task", "report", 1, {})
    assert accept_reply(request, replace(request, version=2, body={"ok": True}))["ok"]
    with pytest.raises(ValueError): accept_reply(request, request)
    with pytest.raises(ValueError): accept_reply(request, replace(request, correlation_id="wrong", version=2))

