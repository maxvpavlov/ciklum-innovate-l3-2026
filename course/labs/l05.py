import json
import tempfile
from pathlib import Path
from agent_runtime.core import Context, Reply, run_agent
from agent_runtime.durable import RunStore, resume_run
from agent_runtime.tools import ToolExecutor


class RemediationProvider:
    """Deterministic fixture for the approval workflow; never a live recommendation."""
    async def complete(self, messages, tools, max_tokens=500):
        if not any(m["role"] == "tool" for m in messages):
            return Reply({"role": "assistant", "content": None, "tool_calls": [{
                "id": "rollback-1", "type": "function", "function": {
                    "name": "mock_remediate", "arguments": json.dumps({
                        "incident_id": "INC-001", "action": "rollback"})}}]}, 20)
        return Reply({"role": "assistant", "content": json.dumps({"status": "complete",
            "cause": "simulated_remediation", "summary": "Mock rollback recorded", "evidence": []})}, 20)


class WorkerCrash(BaseException):
    pass


async def demo():
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory)/"platform.db")
        store, tools = RunStore(path), ToolExecutor(path)
        ctx = Context(allowed=("mock_remediate",))
        provider = RemediationProvider()
        waiting = await run_agent(provider, tools.execute, tools.available(ctx), "Simulate INC-001 rollback", ctx,
                                  checkpoint=store.save)
        assert waiting.status == "waiting_approval"
        approval = store.decide(ctx.tenant, ctx.run_id)
        # Simulate loss of the process after the write but before result checkpoint.
        original = tools.execute
        async def crash_after_write(name, args, context):
            await original(name, args, context)
            raise WorkerCrash()
        tools.execute = crash_after_write
        try:
            await resume_run(store, ctx.tenant, ctx.run_id, provider, tools)
        except WorkerCrash:
            pass
        restarted = ToolExecutor(path)
        completed = await resume_run(RunStore(path), ctx.tenant, ctx.run_id, provider, restarted)
        effects = restarted.db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
        assert completed.status == "completed" and effects == 1
        return {"paused": waiting.status, "approval": approval,
                "resumed": completed.status, "effects_after_crash_and_resume": effects}

