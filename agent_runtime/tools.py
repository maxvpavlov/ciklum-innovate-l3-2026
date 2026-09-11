"""Application-owned authorization, schema checks, errors and mock effects."""
import asyncio
import hashlib
import json
import sqlite3
from jsonschema import ValidationError, validate
from agent_runtime.core import ApprovalRequired
from course.fixtures import SCHEMAS, simple_tools


WRITE_SCHEMA = {"type": "function", "function": {
    "name": "mock_remediate", "description": "Record a simulated rollback; requires exact-action approval.",
    "parameters": {"type": "object", "properties": {
        "incident_id": {"type": "string", "pattern": "^INC-[0-9]{3}$"},
        "action": {"type": "string", "enum": ["rollback"]}},
        "required": ["incident_id", "action"], "additionalProperties": False}}}


def action_key(name, args, context):
    payload = [context.tenant, context.run_id, name, args]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class ToolExecutor:
    def __init__(self, db=":memory:", read_handler=simple_tools, output_limit=6000):
        self.db = sqlite3.connect(db, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS effects (key TEXT PRIMARY KEY, tenant TEXT, result TEXT)")
        self.read_handler, self.output_limit = read_handler, output_limit
        self.schemas = SCHEMAS + [WRITE_SCHEMA]

    def available(self, context):
        return [s for s in self.schemas if s["function"]["name"] in context.allowed]

    async def execute(self, name, args, context):
        schemas = {s["function"]["name"]: s["function"]["parameters"] for s in self.schemas}
        if name not in schemas:
            return {"ok": False, "error": "unknown_tool", "retryable": False}
        if name not in context.allowed:
            return {"ok": False, "error": "permission_denied", "retryable": False}
        try:
            validate(args, schemas[name])
        except ValidationError:
            return {"ok": False, "error": "invalid_arguments", "retryable": False}
        if name == "mock_remediate":
            key = action_key(name, args, context)
            if key not in context.approved:
                raise ApprovalRequired({"key": key, "name": name, "args": args})
            # Effect and deduplication record commit in the SAME local transaction.
            self.db.execute("BEGIN IMMEDIATE")
            try:
                row = self.db.execute("SELECT result FROM effects WHERE key=?", (key,)).fetchone()
                if row:
                    result = {**json.loads(row[0]), "replayed": True}
                else:
                    result = {"ok": True, "simulated": True, "action": args["action"],
                              "incident_id": args["incident_id"], "replayed": False}
                    self.db.execute("INSERT INTO effects VALUES (?,?,?)",
                                    (key, context.tenant, json.dumps(result)))
                self.db.execute("COMMIT")
                return result
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
        for attempt in range(2):
            try:
                async with asyncio.timeout(2):
                    result = await self.read_handler(name, args, context)
                if len(json.dumps(result)) > self.output_limit:
                    return {"ok": False, "error": "output_too_large", "retryable": False}
                return result
            except (TimeoutError, ConnectionError):
                if attempt:
                    return {"ok": False, "error": "tool_unavailable", "retryable": True}
                await asyncio.sleep(.01)

