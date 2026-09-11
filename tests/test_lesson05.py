import pytest
from incident.core import Context, run_agent
from incident.durable import RunStore, resume_run
from incident.labs.l05 import RemediationProvider, demo
from incident.tools import ToolExecutor


async def test_crash_after_effect_does_not_duplicate():
    assert (await demo())["effects_after_crash_and_resume"] == 1


async def test_expired_and_denied_approvals(tmp_path):
    path = str(tmp_path/"runs.db")
    store, tools, provider = RunStore(path), ToolExecutor(path), RemediationProvider()
    ctx = Context(allowed=("mock_remediate",))
    await run_agent(provider, tools.execute, tools.available(ctx), "rollback", ctx, checkpoint=store.save)
    store.decide(ctx.tenant, ctx.run_id, ttl=-1)
    assert (await resume_run(store, ctx.tenant, ctx.run_id, provider, tools)).status == "waiting_approval"
    store.decide(ctx.tenant, ctx.run_id, "deny")
    with pytest.raises(PermissionError):
        await resume_run(store, ctx.tenant, ctx.run_id, provider, tools)
    with pytest.raises(KeyError):
        store.load("globex", ctx.run_id)

