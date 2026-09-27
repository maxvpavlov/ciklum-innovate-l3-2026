"""Supervisor delegates through typed contracts to isolated agent runs."""
import asyncio
from dataclasses import dataclass, field, replace
import json
import re
import uuid
from jsonschema import validate, ValidationError
from agent_runtime.core import Context, Limits, Reply, run_agent
from agent_runtime.context import context_tools
from agent_runtime.providers import MockProvider
from agent_runtime.tools import ToolExecutor

DELEGATE_SCHEMA = {"type": "function", "function": {
    "name": "delegate", "description": "Delegate one bounded read-only investigation task to logs or runbooks.",
    "parameters": {"type": "object", "properties": {
        "task_id": {"type": "string", "minLength": 1},
        "role": {"type": "string", "enum": ["logs", "runbooks"]},
        "objective": {"type": "string", "maxLength": 500}},
        "required": ["task_id", "role", "objective"], "additionalProperties": False}}}


@dataclass
class SharedBudget:
    remaining: int = 6000
    max_agents: int = 2
    max_depth: int = 1
    spawned: int = 0
    spent: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def reserve(self, tokens, depth, count_agent=True):
        async with self.lock:
            if depth > self.max_depth or (count_agent and self.spawned >= self.max_agents) or tokens > self.remaining:
                raise ValueError("delegation_budget")
            self.spawned += int(count_agent)
            self.remaining -= tokens

    async def settle(self, reserved, used):
        async with self.lock:
            self.remaining = max(0, self.remaining + reserved - used)
            self.spent += used


class SupervisorProvider:
    """Offline plan fixture; a live provider can use the identical delegate schema."""
    async def complete(self, messages, tools, max_tokens=500):
        observations = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if not observations:
            task = messages[1]["content"]
            incident = (re.search(r"INC-\d+", task) or re.search(r"INC-\d+", "INC-001")).group()
            calls = [{"id": role, "type": "function", "function": {"name": "delegate",
                "arguments": json.dumps({"task_id": role, "role": role,
                    "objective": f"Investigate {incident} payments latency using {role} evidence"})}}
                for role in ["logs", "runbooks"]]
            return Reply({"role": "assistant", "content": None, "tool_calls": calls}, 30)
        answers = [o["data"] for o in observations if o.get("ok") and o.get("data")]
        causes = {a["cause"] for a in answers if a["cause"] != "unknown"}
        cause = next(iter(causes)) if len(causes) == 1 else "unknown"
        complete = len(answers) == len(observations) and cause != "unknown"
        return Reply({"role": "assistant", "content": json.dumps({
            "status": "complete" if complete else "insufficient_evidence", "cause": cause,
            "summary": "Combined bounded worker evidence",
            "evidence": sorted({s for a in answers for s in a["evidence"]})})}, 30)


class Supervisor:
    def __init__(self, worker_factory=MockProvider, budget=None, read_handler=context_tools, tools=None, grant=None):
        self.worker_factory = worker_factory
        self.budget = budget or SharedBudget()
        self.children, self.results, self.contracts = [], {}, {}
        self.read_handler, self.tools, self.grant = read_handler, tools, grant

    async def delegate(self, name, args, parent):
        if name != "delegate":
            return {"ok": False, "error": "unknown_tool"}
        try:
            validate(args, DELEGATE_SCHEMA["function"]["parameters"])
        except ValidationError:
            return {"ok": False, "error": "invalid_delegation"}
        identity = args["task_id"]
        contract = json.dumps(args, sort_keys=True)
        if identity in self.contracts:
            if self.contracts[identity] != contract:
                return {"ok": False, "error": "task_id_conflict"}
            return self.results.get(identity, {"ok": False, "error": "duplicate_in_flight"})
        capabilities = ("log_lookup",) if args["role"] == "logs" else ("runbook_search",)
        if not set(capabilities) <= set(parent.allowed):
            return {"ok": False, "error": "child_privilege_escalation"}
        reserved = 1800
        child = replace(parent, run_id=uuid.uuid4().hex, parent_id=parent.run_id,
                        role=args["role"], allowed=capabilities, approved=())
        try:
            if self.grant:
                # The child's credential can only narrow what the parent holds.
                self.grant(parent, child)
            await self.budget.reserve(reserved, depth=1)
        except (PermissionError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}
        self.contracts[identity] = contract
        tools = self.tools or ToolExecutor(read_handler=self.read_handler)
        run = None
        try:
            run = await run_agent(self.worker_factory(), tools.execute, tools.available(child),
                args["objective"], child, Limits(tokens=reserved, steps=4))
            self.children.append(run)
            result = {"ok": run.status == "completed", "data": run.answer,
                      "child_run_id": child.run_id, "task_id": identity,
                      "error": run.error, "status": run.status}
            self.results[identity] = result
            return result
        finally:
            await self.budget.settle(reserved, run.tokens if run else reserved)

    async def batch(self, calls, parent):
        from agent_runtime.coordination import WorkItem, schedule
        async def runner(item):
            call = item.payload
            return await self.delegate(call["name"], call["args"], parent)
        report = await schedule([WorkItem(c["id"], c) for c in calls], runner)
        return {key: value.get("data", {"ok": False, "error": value.get("error", "incomplete")})
                for key, value in report["results"].items()}

    async def investigate(self, task="Investigate INC-001 payments latency", context=None, provider=None,
                          parallel=False, initial=None, checkpoint=None):
        parent = context or Context()
        await self.budget.reserve(1800, depth=0, count_agent=False)
        run = None
        try:
            run = await run_agent(provider or SupervisorProvider(), self.delegate,
                               [DELEGATE_SCHEMA], task, parent,
                               execute_batch=self.batch if parallel else None,
                               initial=initial, checkpoint=checkpoint, limits=Limits(tokens=1800))
            return run
        finally:
            await self.budget.settle(1800, run.tokens if run else 1800)
