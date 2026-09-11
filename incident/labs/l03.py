from incident.context import EvidenceStore, context_tools, select_context
from incident.core import Context, run_agent
from incident.providers import MockProvider
from incident.tools import ToolExecutor


async def demo():
    tools, ctx, store = ToolExecutor(read_handler=context_tools), Context(), EvidenceStore()
    run = await run_agent(MockProvider(), tools.execute, tools.available(ctx), "INC-001", ctx,
                          select_messages=select_context)
    version = store.save_artifact(ctx.tenant, "investigation", run.answer)
    store.remember(ctx.tenant, "last_incident", {"id": "INC-001"}, ttl=-1)
    assert store.artifact("globex", "investigation") is None
    assert store.recall(ctx.tenant, "last_incident") is None
    return {"answer": run.answer, "artifact_version": version, "expired_memory": None,
            "cross_tenant_artifact": None}

