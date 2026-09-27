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



async def test_operations_view_trace_and_release_log(tmp_path):
    import httpx
    from pathlib import Path
    from incident.api import create_app
    from incident.operations import evaluate_platform
    platform = Platform(str(tmp_path/"test.db"), admission=Admission(per_second=1000))
    try:
        baseline = await evaluate_platform(platform, "single", 1)
        platform.releases.record(baseline, {**baseline, "success_rate": .8}, release_gate(baseline, {**baseline, "success_rate": .8}), False)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(create_app(platform)), base_url="http://test",
                                     headers={"Authorization": "Bearer demo-acme"}) as client:
            run_id = (await client.post("/runs", json={"incident_id": "INC-001", "agent": "team"})).json()["id"]
            await platform.wait("acme", run_id)
            trace = (await client.get(f"/runs/{run_id}/trace")).json()
            assert [n["role"] for n in trace["nodes"]][0] == "analyst" and len(trace["nodes"]) == 3
            assert (await client.get(f"/runs/{run_id}/trace", headers={"Authorization": "Bearer demo-globex"})).status_code == 404
            ops = (await client.get("/operations")).json()
        assert ops["admission"]["pending"] == 0 and ops["run_status_counts"]["completed"] >= 1
        assert ops["releases"][0]["approved"] is False and ops["releases"][0]["checks"]["quality"] is False
    finally:
        await platform.close()
    views = (Path(__file__).parents[1]/"incident"/"console"/"views"/"index.js").read_text()
    assert "operations" in views
