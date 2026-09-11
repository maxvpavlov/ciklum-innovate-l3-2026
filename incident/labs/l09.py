import tempfile
from pathlib import Path
import httpx
from incident.api import create_app
from incident.platform import Platform


async def demo():
    with tempfile.TemporaryDirectory() as directory:
        platform = Platform(str(Path(directory)/"platform.db"))
        app = create_app(platform)
        reports = []
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test",
                                     headers={"Authorization": "Bearer demo-acme"}) as client:
            for agent in ["single", "team"]:
                response = await client.post("/runs", json={"incident_id": "INC-001", "agent": agent})
                assert response.status_code == 202
                run_id = response.json()["id"]
                await platform.wait("acme", run_id)
                report = (await client.get(f"/runs/{run_id}")).json()
                assert report["status"] == "completed", report
                reports.append({"agent": agent, "status": report["status"],
                                "definition_version": report["configuration"]["version"]})
            foreign = await client.get(f"/runs/{run_id}", headers={"Authorization": "Bearer demo-globex"})
            assert foreign.status_code == 404
        return {"configurations": reports, "cross_tenant_status": foreign.status_code}

