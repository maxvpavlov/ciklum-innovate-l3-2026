import asyncio
import pytest
from incident.operations import Admission, CapacityError, release_gate, trace_html
from incident.platform import Platform
from incident.providers import MockProvider


async def test_end_to_end_mcp_a2a_and_rollout():
    from incident.labs.l11 import demo
    report = await demo()
    assert report["trace_nodes"] == 3 and report["rollback_version"] == 1


async def test_worker_cancellation_releases_capacity(tmp_path):
    platform = Platform(str(tmp_path/"test.db"), factory=lambda: MockProvider(latency=1),
                        admission=Admission(max_pending=1, per_second=100))
    run_id = platform.submit("acme", "analyst", "INC-001")
    await asyncio.sleep(.01)
    with pytest.raises(CapacityError): platform.submit("acme", "analyst", "INC-001")
    await platform.cancel("acme", run_id)
    assert platform.admission.pending == 0
    assert platform.store.load("acme", run_id).status == "cancelled"


async def test_shared_parent_child_budget(tmp_path):
    platform = Platform(str(tmp_path/"test.db"), total_token_budget=100)
    run_id = platform.submit("acme", "analyst", "INC-001", "team")
    assert (await platform.wait("acme", run_id)).status == "failed"


def test_rate_limit_and_quality_gate():
    gate = Admission(per_second=1); gate.enter("acme"); gate.leave()
    with pytest.raises(CapacityError, match="rate_limited"): gate.enter("acme")
    base = {"dataset_sha256": "a", "split": "all", "success_rate": 1,
            "mean_latency_ms": 5, "mean_tokens": 75}
    assert not release_gate(base, {**base, "success_rate": .8})["approved"]
    assert not release_gate(base, {**base, "dataset_sha256": "b"})["approved"]

