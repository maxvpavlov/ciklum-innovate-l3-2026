"""Platform shell: the run API and console, given from Session 02. Demo bearer identities are for loopback use.

Runs live in memory and execute in this process. Session 05 makes runs durable, and Session 08 replaces
this module with the platform core (registry, run lifecycle, approvals), keeping these routes,
identities and response shapes.
"""
import asyncio
from collections import deque
from dataclasses import replace
import json
import os
from pathlib import Path
import time
import uuid
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import RedirectResponse
from incident.blueprint import platform_map
from incident.core import SYSTEM, ApprovalRequired, Context, Run, run_agent
from incident.providers import provider_from_env
from incident.tools import ToolExecutor, action_key

DEMO_IDENTITIES = {
    "demo-astro": {"tenant": "astro", "role": "analyst"},
    "demo-operator": {"tenant": "astro", "role": "operator"},
    "demo-locomotive": {"tenant": "locomotive", "role": "analyst"},
}
# The platform maps a signed-in role to the tools its runs may use; the model never chooses them.
ROLE_TOOLS = {"analyst": ("log_lookup", "runbook_search"),
              "operator": ("log_lookup", "runbook_search", "mock_remediate")}
CONSOLE = Path(__file__).parent/"console"
# The console renders model output and tool evidence, so it treats both as untrusted text.
CONSOLE_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
               "img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


class Submit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str = Field(pattern=r"^INC-\d{3}$")
    agent: str = "single"


class ToolCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z_]{1,40}$")
    args: dict = Field(default_factory=dict)


class Shell:
    """In-memory runs and tool decisions, kept per tenant."""

    def __init__(self):
        self.runs, self.incidents, self.decisions, self.tasks = {}, {}, {}, set()

    def summaries(self, tenant):
        return [{"id": run_id, "incident": self.incidents[(t, run_id)], "role": run.context.role,
                 "status": run.status, "tokens": run.tokens, "error": run.error, "parent_id": None}
                for (t, run_id), run in reversed(self.runs.items()) if t == tenant]

    async def close(self):
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)


def context_for(who, run_id=None):
    context = Context(tenant=who["tenant"], role=who["role"], allowed=ROLE_TOOLS.get(who["role"], ()))
    return replace(context, run_id=run_id) if run_id else context


def tool_outcome(result):
    if result.get("ok", True):
        return "allow"
    return "retry" if result.get("retryable") else "deny"


def create_app(platform=None, identities=None):
    shell = platform or Shell()
    identities = identities or json.loads(os.getenv("PLATFORM_IDENTITIES", json.dumps(DEMO_IDENTITIES)))
    tools = ToolExecutor()
    app = FastAPI(title="Incident agentic platform")
    app.state.platform = shell

    @app.middleware("http")
    async def console_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/console"):
            response.headers["Content-Security-Policy"] = CONSOLE_CSP
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["Cache-Control"] = "no-store"
        return response

    def identity(request: Request):
        header = request.headers.get("authorization", "")
        if not header.startswith("Bearer "):
            raise HTTPException(401, "bearer_required")
        token = header.removeprefix("Bearer ")
        if token not in identities:
            raise HTTPException(401, "unauthorized")
        return identities[token]

    def load(who, run_id):
        try:
            return shell.runs[(who["tenant"], run_id)]
        except KeyError:
            raise HTTPException(404, "run_not_found") from None

    async def investigate(run):
        await run_agent(provider_from_env(), tools.execute, tools.available(run.context),
                        run.messages[-1]["content"], run.context, initial=run)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse("/console/")

    @app.get("/whoami")
    async def whoami(who=Depends(identity)):
        return who

    @app.get("/platform")
    async def overview(who=Depends(identity)):
        runs = shell.summaries(who["tenant"])
        return {**platform_map(), "counts": {
            "runs": len(runs),
            "waiting_approval": sum(r["status"] == "waiting_approval" for r in runs),
            "tool_decisions": len(shell.decisions.get(who["tenant"], ()))}}

    @app.get("/runs")
    async def runs(who=Depends(identity)):
        return shell.summaries(who["tenant"])

    @app.post("/runs", status_code=202)
    async def submit(body: Submit, who=Depends(identity)):
        if body.agent != "single":
            raise HTTPException(400, "unknown_agent")
        run_id = uuid.uuid4().hex
        run = Run(context_for(who, run_id), [{"role": "system", "content": SYSTEM},
                                              {"role": "user", "content": f"Investigate {body.incident_id}"}])
        run.status = "queued"
        shell.runs[(who["tenant"], run_id)] = run
        shell.incidents[(who["tenant"], run_id)] = body.incident_id
        task = asyncio.create_task(investigate(run))
        shell.tasks.add(task)
        task.add_done_callback(shell.tasks.discard)
        return {"id": run_id, "status": "queued"}

    @app.get("/runs/{run_id}")
    async def inspect(run_id: str, who=Depends(identity)):
        run = load(who, run_id)
        proposal = None
        if run.pending and run.status == "waiting_approval":
            call = run.pending[0]
            proposal = {"key": action_key(call["name"], call["args"], run.context),
                        "name": call["name"], "args": call["args"]}
        return {"id": run_id, "status": run.status, "answer": run.answer, "error": run.error,
                "incident": shell.incidents[(who["tenant"], run_id)], "tokens": run.tokens,
                "proposal": proposal, "role": run.context.role, "parent_id": None,
                "events": run.events, "children": []}

    @app.get("/tools")
    async def catalogue(who=Depends(identity)):
        allowed = context_for(who).allowed
        return {"tools": [{"name": s["function"]["name"], "description": s["function"]["description"],
                           "kind": "write" if s["function"]["name"] == "mock_remediate" else "read",
                           "allowed": s["function"]["name"] in allowed} for s in tools.schemas],
                "decisions": list(shell.decisions.get(who["tenant"], ()))}

    @app.post("/tools/check")
    async def check(body: ToolCheck, who=Depends(identity)):
        """Send one call through the tool boundary as the signed-in role. A write is never approved here."""
        context = context_for(who, "console-check")
        entry = {"at": time.time(), "role": who["role"], "name": body.name, "args": body.args, "error": None}
        result = None
        try:
            result = await tools.execute(body.name, body.args, context)
            entry |= {"decision": tool_outcome(result), "error": result.get("error")}
        except ApprovalRequired as exc:
            entry |= {"decision": "approval_required", "key": exc.action["key"]}
        shell.decisions.setdefault(who["tenant"], deque(maxlen=50)).appendleft(entry)
        return {**entry, "result": result}

    app.mount("/console", StaticFiles(directory=CONSOLE, html=True), name="console")
    return app


app = create_app()
