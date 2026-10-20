from dataclasses import replace
import pytest
from incident.core import ApprovalRequired, Context
from incident.tools import ToolExecutor, action_key


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
    from incident.labs.l02 import demo
    result = await demo()
    assert set(result["tools"]) == {"log_lookup", "runbook_search"}

