"""Real MCP SDK server/client. Stdio identity is bound by its trusted launcher."""
import json
import os
import sys
from mcp import Client, StdioServerParameters
from mcp.server import MCPServer
from agent_runtime.core import Context
from course.fixtures import RUNBOOKS, simple_tools


def make_server(tenant="astro"):
    server = MCPServer("incident-tools")
    context = Context(tenant=tenant)

    @server.tool()
    async def log_lookup(incident_id: str) -> dict:
        """Read diagnostic incident evidence in the launcher's tenant."""
        return await simple_tools("log_lookup", {"incident_id": incident_id}, context)

    @server.tool()
    async def runbook_search(query: str) -> dict:
        """Find relevant runbook evidence in the launcher's tenant."""
        return await simple_tools("runbook_search", {"query": query}, context)

    @server.resource("incident://runbooks")
    def runbooks() -> str:
        return json.dumps([r for r in RUNBOOKS if r["tenant"] == tenant])

    return server


def stdio_client(tenant="astro"):
    return Client(StdioServerParameters(command=sys.executable,
        args=["-m", "agent_runtime.mcp_bridge"], env={"INCIDENT_TENANT": tenant,
        **({"PYTHONPATH": os.environ["PYTHONPATH"]} if "PYTHONPATH" in os.environ else {})}),
        read_timeout_seconds=5)


class MCPReadAdapter:
    def __init__(self, client):
        self.client = client

    async def __call__(self, name, args, context):
        # Use behind ToolExecutor, which validates and authorizes every dispatch.
        result = await self.client.call_tool(name, args)
        if result.is_error:
            return {"ok": False, "error": "mcp_tool_error"}
        if result.structured_content is not None:
            return result.structured_content
        return json.loads(next(c.text for c in result.content if c.type == "text"))


if __name__ == "__main__":
    make_server(os.getenv("INCIDENT_TENANT", "astro")).run(transport="stdio")
