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
            registry = (await client.get("/registry")).json()
            for agent in ["single", "team"]:
                response = await client.post("/runs", json={"incident_id": "INC-001", "agent": agent})
                assert response.status_code == 202
                run_id = response.json()["id"]
                await platform.wait("acme", run_id)
                report = (await client.get(f"/runs/{run_id}")).json()
                assert report["status"] == "completed", report
                reports.append({"agent": agent, "status": report["status"],
                                "definition_version": report["configuration"]["version"],
                                "child_runs": len(report["children"])})
            foreign = await client.get(f"/runs/{run_id}", headers={"Authorization": "Bearer demo-globex"})
            assert foreign.status_code == 404
            platform.registry.register("single", 2, {**platform.registry.get("single", 1)["spec"], "context_chars": 4500})
            pinned = (await client.post("/runs", json={"incident_id": "INC-001", "agent": "single", "version": 1})).json()
            await platform.wait("acme", pinned["id"])
            console = await client.get("/console/")
            overview = (await client.get("/platform")).json()
            assert console.status_code == 200 and "script-src 'self'" in console.headers["content-security-policy"]
        return {"registered_agents": sorted({a["name"] for a in registry["agents"]}),
                "configurations": reports, "cross_tenant_status": foreign.status_code,
                "versions_of_single": [a["version"] for a in platform.registry.agents() if a["name"] == "single"],
                "active_single_version": platform.registry.get("single")["version"],
                "console": {"status": console.status_code, "content_security_policy": True,
                            "built_components": [c["id"] for c in overview["components"] if c["status"] == "built"]}}
