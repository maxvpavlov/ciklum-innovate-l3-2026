from pathlib import Path
import httpx
import pytest
from agentic_platform.api import create_app
from agentic_platform.platform import Platform


async def test_two_configs_registry_and_console():
    from course.labs.l08 import demo
    report = await demo()
    assert len(report["configurations"]) == 2 and report["cross_tenant_status"] == 404
    assert report["active_single_version"] == 1 and report["versions_of_single"] == [1, 2]
    assert "registry" in report["console"]["built_components"]


async def test_approval_api_binds_reviewed_key(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_app(platform)), base_url="http://test",
        headers={"Authorization": "Bearer demo-operator"}) as client:
        response = await client.post("/runs", json={"incident_id": "INC-001", "agent": "remediator"})
        run_id = response.json()["id"]
        await platform.wait("astro", run_id)
        report = (await client.get(f"/runs/{run_id}")).json()
        assert report["status"] == "waiting_approval" and not report["approved"]
        assert (await client.post(f"/runs/{run_id}/decision", json={"key": "wrong"})).status_code == 409
        assert (await client.post(f"/runs/{run_id}/decision", json={"key": report["proposal"]["key"]})).status_code == 200
        assert (await client.get(f"/runs/{run_id}")).json()["approved"]
        await client.post(f"/runs/{run_id}/resume")
        assert (await platform.wait("astro", run_id)).status == "completed"


def test_definition_validation_immutability_and_lease_ownership(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    spec = platform.registry.get("single", 1)["spec"]
    with pytest.raises(ValueError, match="immutable"):
        platform.registry.register("single", 1, {**spec, "context_chars": 4000})
    with pytest.raises(ValueError, match="invalid_definition"):
        platform.registry.register("single", 2, {**spec, "api_key": "sk-inline-secret"})
    with pytest.raises(ValueError, match="unknown_tool"):
        platform.registry.register("single", 2, {**spec, "allowed": ["shell_exec"]})
    platform.store.claim("astro", "example", "worker-a")
    with pytest.raises(ValueError, match="already_owned"):
        platform.store.claim("astro", "example", "worker-b")


async def test_lifecycle_discovery_and_pinned_remote_card(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    registry = platform.registry
    registry.register("single", 2, {**registry.get("single", 1)["spec"], "context_chars": 4500})
    with pytest.raises(ValueError, match="active_version"):
        registry.retire("single", 1)
    registry.activate("single", 2)
    registry.retire("single", 1)
    with pytest.raises(ValueError, match="retired_version"):
        platform.submit("astro", "analyst", "INC-001", "single", 1)
    with pytest.raises(ValueError, match="retired_version"):
        registry.activate("single", 1)
    card = {"name": "Runbook specialist", "skills": [{"id": "runbooks"}]}
    registry.register_remote("runbook-specialist", "http://127.0.0.1:8010", card)
    assert [a["name"] for a in registry.discover("runbooks")] == ["runbook-specialist"]
    assert {a["name"] for a in registry.discover("incident-investigation")} == {"single", "team"}
    with pytest.raises(ValueError, match="agent_card_changed"):
        registry.register_remote("runbook-specialist", "http://127.0.0.1:8010", {**card, "name": "Impostor"})


async def test_console_is_tenant_scoped_and_renders_text_only(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    transport = httpx.ASGITransport(create_app(platform))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/runs")).status_code == 401
        astro = {"Authorization": "Bearer demo-astro"}
        run_id = (await client.post("/runs", json={"incident_id": "INC-001"}, headers=astro)).json()["id"]
        await platform.wait("astro", run_id)
        assert [r["id"] for r in (await client.get("/runs", headers=astro)).json()] == [run_id]
        assert (await client.get("/runs", headers={"Authorization": "Bearer demo-locomotive"})).json() == []
        assert (await client.post("/registry/agents/single/activate", json={"version": 1}, headers=astro)).status_code == 403
        page = await client.get("/console/")
        assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    console = Path(__file__).parents[1]/"agentic_platform"/"console"
    for script in console.rglob("*.js"):
        text = script.read_text()
        assert not any(unsafe in text for unsafe in ["innerHTML", "outerHTML", "insertAdjacentHTML", "eval(", "http://", "https://"]), script


def test_api_handlers_run_on_the_event_loop(tmp_path):
    """Workers and handlers share one SQLite connection, so no handler may run in a thread pool."""
    import inspect
    from fastapi.routing import APIRoute
    app = create_app(Platform(str(tmp_path/"platform.db")))
    handlers = [route.endpoint for route in app.routes if isinstance(route, APIRoute)]
    assert handlers and all(inspect.iscoroutinefunction(handler) for handler in handlers)
