from dataclasses import replace
import pytest
from agent_runtime.core import ApprovalRequired, Context
from agent_runtime.tools import ToolExecutor, action_key


async def test_authorization_schema_and_bounded_output():
    tools, ctx = ToolExecutor(), Context()
    assert (await tools.execute("log_lookup", {"incident_id": "INC-001", "tenant": "locomotive"}, ctx))["error"] == "invalid_arguments"
    assert (await tools.execute("mock_remediate", {}, ctx))["error"] == "permission_denied"
    tools.output_limit = 10
    assert (await tools.execute("log_lookup", {"incident_id": "INC-001"}, ctx))["error"] == "output_too_large"


async def test_exact_approval_and_durable_duplicate_write(tmp_path):
    ctx = Context(allowed=("mock_remediate",))
    args = {"incident_id": "INC-001", "action": "rollback"}
    tools = ToolExecutor(str(tmp_path/"effects.db"))
    with pytest.raises(ApprovalRequired):
        await tools.execute("mock_remediate", args, ctx)
    approved = replace(ctx, approved=(action_key("mock_remediate", args, ctx),))
    assert not (await tools.execute("mock_remediate", args, approved))["replayed"]
    restarted = ToolExecutor(str(tmp_path/"effects.db"))
    assert (await restarted.execute("mock_remediate", args, approved))["replayed"]
    with pytest.raises(ApprovalRequired):
        await tools.execute("mock_remediate", {**args, "incident_id": "INC-002"}, approved)


async def test_mcp_stdio_transport():
    from course.labs.l02 import demo
    result = await demo()
    assert set(result["tools"]) == {"log_lookup", "runbook_search"}



async def _wait(client, run_id, headers):
    import asyncio
    for _ in range(200):
        report = (await client.get(f"/runs/{run_id}", headers=headers)).json()
        if report["status"] not in {"queued", "running"}:
            return report
        await asyncio.sleep(0.05)
    raise AssertionError("run did not finish")


async def test_platform_shell_runs_are_tenant_scoped(tmp_path, monkeypatch):
    from pathlib import Path
    import httpx
    from agentic_platform.api import create_app
    monkeypatch.setenv("PLATFORM_DB", str(tmp_path/"platform.db"))
    app = create_app()
    astro = {"Authorization": "Bearer demo-astro"}
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
            assert (await client.get("/runs")).status_code == 401
            response = await client.post("/runs", json={"incident_id": "INC-001"}, headers=astro)
            assert response.status_code == 202
            report = await _wait(client, response.json()["id"], astro)
            assert report["status"] == "completed" and report["answer"]["cause"] == "connection_pool_exhaustion"
            assert any(event["kind"] == "tool" for event in report["events"])
            other = {"Authorization": "Bearer demo-locomotive"}
            assert (await client.get(f"/runs/{report['id']}", headers=other)).status_code == 404
            assert (await client.get("/runs", headers=other)).json() == []
            page = await client.get("/console/")
            assert "frame-ancestors 'none'" in page.headers["content-security-policy"]
    finally:
        close = getattr(app.state.platform, "close", None)
        if close:
            await close()
    console = Path(__file__).parents[1]/"agentic_platform"/"console"
    for script in console.rglob("*.js"):
        text = script.read_text()
        assert not any(unsafe in text for unsafe in ["innerHTML", "outerHTML", "insertAdjacentHTML", "eval("]), script


async def test_console_tool_checks_use_the_boundary(tmp_path, monkeypatch):
    import httpx
    from agentic_platform.api import create_app
    monkeypatch.setenv("PLATFORM_DB", str(tmp_path/"platform.db"))
    app = create_app()
    analyst, operator = {"Authorization": "Bearer demo-astro"}, {"Authorization": "Bearer demo-operator"}
    rollback = {"name": "mock_remediate", "args": {"incident_id": "INC-001", "action": "rollback"}}
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://test") as client:
            check = lambda body, who: client.post("/tools/check", json=body, headers=who)
            denied = (await check(rollback, analyst)).json()
            assert denied["decision"] == "deny" and denied["error"] == "permission_denied"
            extra = (await check({"name": "log_lookup", "args": {"incident_id": "INC-001", "tenant": "locomotive"}}, analyst)).json()
            assert extra["decision"] == "deny" and extra["error"] == "invalid_arguments"
            read = (await check({"name": "log_lookup", "args": {"incident_id": "INC-001"}}, analyst)).json()
            assert read["decision"] == "allow" and read["result"]["data"]["source_id"] == "log-astro-001"
            proposed = (await check(rollback, operator)).json()
            assert proposed["decision"] == "approval_required" and len(proposed["key"]) == 64
            listing = (await client.get("/tools", headers=analyst)).json()
            assert {t["name"]: t["allowed"] for t in listing["tools"]}["mock_remediate"] is False
            assert [d["decision"] for d in listing["decisions"]][:3] == ["approval_required", "allow", "deny"]
    finally:
        close = getattr(app.state.platform, "close", None)
        if close:
            await close()
