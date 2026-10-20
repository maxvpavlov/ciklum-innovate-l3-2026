from dataclasses import replace
from incident.core import ApprovalRequired, Context, run_agent
from incident.mcp_bridge import MCPReadAdapter, stdio_client
from incident.providers import MockProvider
from incident.tools import ToolExecutor, action_key


async def demo():
    async with stdio_client() as client:
        listing = await client.list_tools()
        tools = ToolExecutor(read_handler=MCPReadAdapter(client))
        ctx = Context()
        run = await run_agent(MockProvider(), tools.execute, tools.available(ctx), "INC-001", ctx)
        assert run.answer["cause"] == "connection_pool_exhaustion", run.snapshot()
        denied = await tools.execute("mock_remediate", {"incident_id": "INC-001", "action": "rollback"}, ctx)
        assert denied["error"] == "permission_denied"
        return {"tools": [t.name for t in listing.tools], "protocol": client.protocol_version,
                "answer": run.answer, "write_without_capability": denied}

