"""Tool gateway: the single policy, audit and connection point for every agent tool call."""
import asyncio
from collections import Counter
from dataclasses import dataclass
import json
import sqlite3
import time
from incident.core import ApprovalRequired
from incident.mcp_bridge import MCPReadAdapter, stdio_client
from incident.registry import digest
from incident.tools import ToolExecutor


@dataclass(frozen=True)
class GatewayPolicy:
    max_calls_per_run: int = 6
    max_argument_chars: int = 300
    write_roles: tuple[str, ...] = ("operator",)


class ToolGateway:
    def __init__(self, registry, path=":memory:", launcher=stdio_client, policy=GatewayPolicy()):
        self.registry, self.launcher, self.policy = registry, launcher, policy
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS gateway_audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, "
                        "tenant TEXT, run_id TEXT, parent_id TEXT, role TEXT, tool TEXT, server TEXT, "
                        "decision TEXT, reason TEXT, args_sha256 TEXT)")
        # Validation, exact-action approval and the effect ledger stay in the executor.
        self.executor = ToolExecutor(path, read_handler=self._upstream)
        self.sessions, self.launches, self.calls = {}, Counter(), Counter()
        self.lock = asyncio.Lock()

    def available(self, context):
        catalog = self.registry.catalog()
        return [s for s in self.executor.available(context) if s["function"]["name"] in catalog]

    def check(self, name, args, context):
        entry = self.registry.catalog().get(name)
        if entry is None:
            return "deny", "unknown_tool", None
        if name not in context.allowed:
            return "deny", "not_granted", entry["server"]
        if context.tenant not in entry["tenants"]:
            return "deny", "tenant_not_served", entry["server"]
        if entry["status"] == "quarantined":
            return "deny", "tool_definition_changed", entry["server"]
        if entry["risk"] == "write" and context.role not in self.policy.write_roles:
            return "deny", "write_role_required", entry["server"]
        if len(json.dumps(args)) > self.policy.max_argument_chars:
            return "deny", "argument_policy", entry["server"]
        if self.calls[context.run_id] >= self.policy.max_calls_per_run:
            return "deny", "tool_call_budget", entry["server"]
        return "allow", "policy_passed", entry["server"]

    def audit(self, context, name, server, decision, reason, args):
        self.db.execute("INSERT INTO gateway_audit (ts,tenant,run_id,parent_id,role,tool,server,decision,reason,args_sha256) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?)", (time.time(), context.tenant, context.run_id, context.parent_id,
                        context.role, name, server, decision, reason, digest(args)))

    async def execute(self, name, args, context):
        decision, reason, server = self.check(name, args, context)
        if decision == "deny":
            self.audit(context, name, server, decision, reason, args)
            return {"ok": False, "error": reason, "retryable": False}
        self.calls[context.run_id] += 1
        try:
            result = await self.executor.execute(name, args, context)
        except ApprovalRequired:
            self.audit(context, name, server, "approval_required", "exact_action_approval", args)
            raise
        outcome = "ok" if result.get("ok", True) else result.get("error", "error")
        self.audit(context, name, server, "allow", outcome, args)
        return result

    async def _upstream(self, name, args, context):
        entry = self.registry.catalog()[name]
        try:
            client = await self._session(entry["server"], context.tenant)
            return await MCPReadAdapter(client)(name, args, context)
        except ValueError as exc:
            # A changed upstream definition is a terminal policy failure, not a retry.
            await self._drop(entry["server"], context.tenant)
            return {"ok": False, "error": str(exc), "retryable": False}
        except Exception as exc:
            await self._drop(entry["server"], context.tenant)
            raise ConnectionError(type(exc).__name__) from None

    async def _session(self, server, tenant):
        """One upstream MCP session per server and tenant, shared by every worker."""
        key = (server, tenant)
        async with self.lock:
            if key not in self.sessions:
                ready, stop = asyncio.get_running_loop().create_future(), asyncio.Event()

                async def owner():
                    # The task that opens the MCP client is also the task that closes it.
                    try:
                        async with self.launcher(tenant) as client:
                            listing = await client.list_tools()
                            try:
                                self.registry.pin_tools(server, {t.name: digest(t.model_dump(mode="json", exclude_none=True))
                                                                 for t in listing.tools})
                            except ValueError as exc:
                                ready.set_exception(exc)
                                return
                            ready.set_result(client)
                            await stop.wait()
                    except BaseException as exc:
                        if not ready.done():
                            ready.set_exception(exc)
                        if not isinstance(exc, Exception):
                            raise

                self.sessions[key] = (ready, stop, asyncio.create_task(owner()))
                self.launches[key] += 1
        return await asyncio.shield(self.sessions[key][0])

    async def _drop(self, server, tenant):
        async with self.lock:
            session = self.sessions.pop((server, tenant), None)
        if session:
            session[1].set()
            await asyncio.gather(session[2], return_exceptions=True)

    async def close(self):
        for server, tenant in list(self.sessions):
            await self._drop(server, tenant)

    def recent(self, tenant, limit=100):
        rows = self.db.execute("SELECT seq,ts,run_id,parent_id,role,tool,server,decision,reason,args_sha256 FROM gateway_audit "
                               "WHERE tenant=? ORDER BY seq DESC LIMIT ?", (tenant, limit))
        keys = ["seq", "ts", "run_id", "parent_id", "role", "tool", "server", "decision", "reason", "args_sha256"]
        return [dict(zip(keys, row)) for row in rows]
