from pathlib import Path
import httpx
import pytest
from incident.api import create_app
from incident.core import Context
from incident.gateway import GatewayPolicy, ToolGateway
from incident.platform import Platform


async def test_shared_sessions_policy_and_pinned_definitions():
    from incident.labs.l09 import demo
    report = await demo()
    assert report["mcp_sessions_launched"] == {"incident-tools/astro": 1}
    assert report["changed_definition"]["server_status"] == "quarantined"
    assert set(report["denials"].values()) == {"not_granted", "write_role_required", "argument_policy"}


async def test_denials_are_audited_before_any_upstream_connection(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    gateway = ToolGateway(platform.registry, str(tmp_path/"platform.db"), policy=GatewayPolicy(max_calls_per_run=1))
    context = Context(tenant="initech")
    assert (await gateway.execute("log_lookup", {"incident_id": "INC-001"}, context))["error"] == "tenant_not_served"
    assert (await gateway.execute("shell_exec", {}, Context()))["error"] == "unknown_tool"
    assert gateway.launches == {}
    ctx = Context()
    assert (await gateway.execute("log_lookup", {"incident_id": "INC-001"}, ctx))["ok"]
    assert (await gateway.execute("runbook_search", {"query": "pool"}, ctx))["error"] == "tool_call_budget"
    await gateway.close()
    rows = gateway.recent("initech")
    assert [(r["decision"], r["reason"]) for r in rows] == [("deny", "tenant_not_served")]
    assert all(len(r["args_sha256"]) == 64 for r in gateway.recent("astro"))


async def test_workers_reach_tools_only_through_the_gateway(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    try:
        run_id = platform.submit("astro", "analyst", "INC-001", "team")
        run = await platform.wait("astro", run_id)
        assert run.status == "completed"
        audited = {(r["role"], r["tool"]) for r in platform.gateway.recent("astro")}
        assert audited == {("logs", "log_lookup"), ("runbooks", "runbook_search")}
        assert [s["function"]["name"] for s in platform.gateway.available(Context(allowed=("runbook_search",)))] == ["runbook_search"]
    finally:
        await platform.close()


async def test_gateway_view_is_tenant_scoped(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(create_app(platform)), base_url="http://test") as client:
            run_id = (await client.post("/runs", json={"incident_id": "INC-001"}, headers={"Authorization": "Bearer demo-astro"})).json()["id"]
            await platform.wait("astro", run_id)
            astro = (await client.get("/gateway", headers={"Authorization": "Bearer demo-astro"})).json()
            locomotive = (await client.get("/gateway", headers={"Authorization": "Bearer demo-locomotive"})).json()
        assert {a["run_id"] for a in astro["audit"]} == {run_id} and locomotive["audit"] == []
        server = next(s for s in astro["servers"] if s["name"] == "incident-tools")
        assert server["status"] == "pinned" and server["sessions_launched"] == 1
        assert all(t["pinned_sha256"] for t in server["tools"])
    finally:
        await platform.close()
    views = (Path(__file__).parents[1]/"incident"/"console"/"views"/"index.js").read_text()
    assert "gateway" in views
