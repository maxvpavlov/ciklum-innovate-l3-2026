import httpx
import pytest
from incident.api import create_app
from incident.platform import Platform


async def test_two_configs_and_tenant_boundary():
    from incident.labs.l09 import demo
    assert len((await demo())["configurations"]) == 2


async def test_approval_api_binds_reviewed_key(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_app(platform)), base_url="http://test",
        headers={"Authorization": "Bearer demo-operator"}) as client:
        response = await client.post("/runs", json={"incident_id": "INC-001", "agent": "remediator"})
        run_id = response.json()["id"]
        await platform.wait("acme", run_id)
        report = (await client.get(f"/runs/{run_id}")).json()
        assert report["status"] == "waiting_approval"
        assert (await client.post(f"/runs/{run_id}/decision", json={"key": "wrong"})).status_code == 409
        assert (await client.post(f"/runs/{run_id}/decision", json={"key": report["proposal"]["key"]})).status_code == 200
        await client.post(f"/runs/{run_id}/resume")
        assert (await platform.wait("acme", run_id)).status == "completed"


def test_definition_versions_and_lease_ownership(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    with pytest.raises(ValueError, match="immutable"):
        platform.definitions.put("single", 1, {"kind": "changed"})
    platform.store.claim("acme", "example", "worker-a")
    with pytest.raises(ValueError, match="already_owned"):
        platform.store.claim("acme", "example", "worker-b")

