"""Run, registry and console API. Demo bearer identities are explicit and intended for loopback use."""
from contextlib import asynccontextmanager
from dataclasses import asdict
import json
import os
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import RedirectResponse
from incident.blueprint import platform_map
from incident.platform import Platform
from incident.tools import action_key

DEMO_IDENTITIES = {
    "demo-acme": {"tenant": "acme", "role": "analyst"},
    "demo-operator": {"tenant": "acme", "role": "operator"},
    "demo-globex": {"tenant": "globex", "role": "analyst"},
}
CONSOLE = Path(__file__).parent/"console"
# The console renders model output and tool evidence, so it treats both as untrusted text.
CONSOLE_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
               "img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


class Submit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: str = Field(pattern=r"^INC-\d{3}$")
    agent: str = "single"
    version: int | None = None


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    decision: str = "approve"


class VersionChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int


def create_app(platform=None, identities=None):
    platform = platform or Platform(os.getenv("PLATFORM_DB", "var/platform.db"))
    identities = identities or json.loads(os.getenv("PLATFORM_IDENTITIES", json.dumps(DEMO_IDENTITIES)))

    @asynccontextmanager
    async def lifespan(app):
        if os.getenv("A2A_URL"):
            await platform.register_remote_agent(os.environ["A2A_URL"])
        yield
        await platform.close()

    app = FastAPI(title="Incident agentic platform", lifespan=lifespan)
    app.state.platform = platform

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

    def operator(who=Depends(identity)):
        if who["role"] != "operator":
            raise HTTPException(403, "operator_required")
        return who

    def load(who, run_id):
        try:
            return platform.store.load(who["tenant"], run_id)
        except KeyError:
            raise HTTPException(404, "run_not_found") from None

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
        runs = platform.store.summaries(who["tenant"], limit=1000)
        return {**platform_map(), "counts": {
            "agent_versions": len(platform.registry.agents()),
            "remote_agents": len(platform.registry.remotes()),
            "runs": len(runs),
            "waiting_approval": sum(r["status"] == "waiting_approval" for r in runs)}}

    @app.get("/registry")
    async def registry(who=Depends(identity)):
        return {"agents": platform.registry.agents(),
                "remote_agents": [{k: r[k] for k in ["name", "url", "sha256", "skills"]}
                                  for r in platform.registry.remotes()]}

    @app.post("/registry/agents/{name}/activate")
    async def activate(name: str, body: VersionChoice, who=Depends(operator)):
        try:
            platform.registry.activate(name, body.version)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from None
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from None
        return platform.registry.get(name)

    @app.get("/gateway")
    async def gateway(who=Depends(identity)):
        launched = platform.gateway.launches
        servers = [{"name": s["name"], "transport": s["transport"], "tenants": s["tenants"], "status": s["status"],
                    "sessions_launched": sum(n for (server, _), n in launched.items() if server == s["name"]),
                    "tools": [{"name": tool, "risk": meta["risk"], "pinned_sha256": s["pins"].get(tool)}
                              for tool, meta in s["tools"].items()]}
                   for s in platform.registry.tool_servers()]
        return {"policy": asdict(platform.gateway.policy), "servers": servers,
                "audit": platform.gateway.recent(who["tenant"])}

    @app.get("/runs")
    async def runs(who=Depends(identity)):
        return platform.store.summaries(who["tenant"])

    @app.post("/runs", status_code=202)
    async def submit(body: Submit, who=Depends(identity)):
        try:
            run_id = platform.submit(who["tenant"], who["role"], body.incident_id, body.agent, body.version)
            return {"id": run_id, "status": "queued"}
        except PermissionError as exc:
            raise HTTPException(403, str(exc)) from None
        except (KeyError, ValueError) as exc:
            raise HTTPException(400, str(exc)) from None

    @app.get("/runs/{run_id}")
    async def inspect(run_id: str, who=Depends(identity)):
        run = load(who, run_id)
        proposal = None
        if run.pending and run.status == "waiting_approval":
            call = run.pending[0]
            proposal = {"key": action_key(call["name"], call["args"], run.context),
                        "name": call["name"], "args": call["args"]}
        return {"id": run_id, "status": run.status, "answer": run.answer, "error": run.error,
                "configuration": run.configuration, "tokens": run.tokens, "proposal": proposal,
                "approved": bool(proposal) and proposal["key"] in platform.store.approved_keys(who["tenant"], run_id),
                "role": run.context.role, "parent_id": run.context.parent_id, "events": run.events,
                "children": platform.store.summaries(who["tenant"], parent_id=run_id)}

    @app.post("/runs/{run_id}/cancel")
    async def cancel(run_id: str, who=Depends(identity)):
        load(who, run_id)
        try:
            await platform.cancel(who["tenant"], run_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from None
        return {"status": "cancelled"}

    @app.post("/runs/{run_id}/decision")
    async def decision(run_id: str, body: Decision, who=Depends(operator)):
        run = load(who, run_id)
        if not run.pending:
            raise HTTPException(409, "no_pending_action")
        call = run.pending[0]
        if action_key(call["name"], call["args"], run.context) != body.key:
            raise HTTPException(409, "proposal_changed")
        try:
            return platform.store.decide(who["tenant"], run_id, body.decision)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from None

    @app.post("/runs/{run_id}/resume", status_code=202)
    async def resume(run_id: str, who=Depends(identity)):
        run = load(who, run_id)
        if run.status in {"denied", "cancelled", "completed"}:
            raise HTTPException(409, "terminal_run")
        try:
            platform.launch(who["tenant"], run_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from None
        return {"id": run_id, "status": "queued"}

    app.mount("/console", StaticFiles(directory=CONSOLE, html=True), name="console")
    return app


app = create_app()
