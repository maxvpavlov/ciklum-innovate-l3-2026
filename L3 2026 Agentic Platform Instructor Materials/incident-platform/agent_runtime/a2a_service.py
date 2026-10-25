"""A real A2A 1.0 service using the official Python SDK's JSON-RPC routes."""
import asyncio
from contextvars import ContextVar
import json
import os
from fastapi import FastAPI
from starlette.responses import JSONResponse
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.routes.fastapi_routes import add_a2a_routes_to_fastapi
from a2a.types import a2a_pb2 as p
from agent_runtime.core import Context, run_agent
from agentic_platform.identity import TokenIssuer
from agent_runtime.context import context_tools
from agent_runtime.providers import provider_from_env
from agent_runtime.tools import ToolExecutor


AUDIENCE = "agent:runbook-specialist"
caller = ContextVar("caller")


class SpecialistExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await event_queue.enqueue_event(p.Task(id=context.task_id, context_id=context.context_id,
            status=p.TaskStatus(state=p.TaskState.TASK_STATE_SUBMITTED)))
        await updater.start_work()
        task = context.get_user_input()
        if "SLOW" in task:
            await asyncio.sleep(2)
        claims = caller.get()
        # Tenant and delegating subject come from the verified token, never from the message.
        ctx = Context(tenant=claims["tenant"], role="remote_runbooks", allowed=("runbook_search",),
                      subject=claims["sub"])
        tools = ToolExecutor(read_handler=context_tools)
        run = await run_agent(provider_from_env(), tools.execute, tools.available(ctx), task, ctx)
        if run.status != "completed":
            await updater.failed(); return
        await updater.add_artifact([p.Part(text=json.dumps({"answer": run.answer,
            "tokens": run.tokens, "run_id": run.context.run_id}))], name="runbook-evidence")
        await updater.complete()

    async def cancel(self, context, event_queue):
        await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()


def make_app(base_url=None, issuer=None):
    base_url = base_url or os.getenv("A2A_BASE_URL", "http://127.0.0.1:8010")
    issuer = issuer or TokenIssuer()
    card = p.AgentCard(name="Runbook specialist", description="Read-only Astro runbook evidence",
        version="1.0.0", default_input_modes=["text/plain"], default_output_modes=["application/json"],
        supported_interfaces=[p.AgentInterface(url=base_url+"/a2a", protocol_binding="JSONRPC", protocol_version="1.0")],
        capabilities=p.AgentCapabilities(streaming=True),
        skills=[p.AgentSkill(id="runbooks", name="Runbook investigation", description="Find cited runbook guidance", tags=["incident"])],
        security_schemes={"bearer": p.SecurityScheme(http_auth_security_scheme=p.HTTPAuthSecurityScheme(scheme="bearer"))})
    handler = DefaultRequestHandler(SpecialistExecutor(), InMemoryTaskStore(), card)
    app = FastAPI(title="Course A2A specialist")

    @app.middleware("http")
    async def authenticate(request, call_next):
        if request.url.path == "/a2a":
            header = request.headers.get("authorization", "")
            try:
                claims = issuer.verify(header.removeprefix("Bearer "), AUDIENCE)
            except PermissionError as exc:
                return JSONResponse({"error": "unauthorized", "reason": str(exc)}, status_code=401)
            if "runbook_search" not in claims["scope"].split():
                return JSONResponse({"error": "forbidden", "reason": "scope_denied"}, status_code=403)
            caller.set(claims)
        return await call_next(request)

    add_a2a_routes_to_fastapi(app, agent_card_routes=create_agent_card_routes(card),
                             jsonrpc_routes=create_jsonrpc_routes(handler, rpc_url="/a2a"))
    return app


app = make_app()
