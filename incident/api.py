"""Run API. Demo bearer identities are explicit and intended for loopback use."""
import os
import json
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from incident.platform import Platform
from incident.tools import action_key

DEMO_IDENTITIES = {
    "demo-acme": {"tenant": "acme", "role": "analyst"},
    "demo-operator": {"tenant": "acme", "role": "operator"},
    "demo-globex": {"tenant": "globex", "role": "analyst"},
}


class Submit(BaseModel):
    incident_id: str = Field(pattern=r"^INC-\d{3}$")
    agent: str = "single"
    version: int = 1


class Decision(BaseModel):
    key: str
    decision: str = "approve"


def create_app(platform=None, identities=None):
    platform = platform or Platform(os.getenv("PLATFORM_DB", "var/platform.db"), os.getenv("A2A_URL"))
    identities = identities or json.loads(os.getenv("PLATFORM_IDENTITIES", json.dumps(DEMO_IDENTITIES)))
    app = FastAPI(title="Incident agentic platform")
    app.state.platform = platform

    def identity(request: Request):
        token = request.headers.get("authorization", "").removeprefix("Bearer ")
        if token not in identities:
            raise HTTPException(401, "unauthorized")
        return identities[token]

    def load(who, run_id):
        try:
            return platform.store.load(who["tenant"], run_id)
        except KeyError:
            raise HTTPException(404, "run_not_found") from None

    @app.get("/health")
    def health():
        return {"status": "ok"}

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
    def inspect(run_id: str, who=Depends(identity)):
        run = load(who, run_id)
        proposal = None
        if run.pending and run.status == "waiting_approval":
            call = run.pending[0]
            proposal = {"key": action_key(call["name"], call["args"], run.context),
                        "name": call["name"], "args": call["args"]}
        return {"id": run_id, "status": run.status, "answer": run.answer, "error": run.error,
                "configuration": run.configuration, "tokens": run.tokens, "proposal": proposal}

    @app.post("/runs/{run_id}/cancel")
    async def cancel(run_id: str, who=Depends(identity)):
        load(who, run_id)
        try:
            await platform.cancel(who["tenant"], run_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from None
        return {"status": "cancelled"}

    @app.post("/runs/{run_id}/decision")
    def decision(run_id: str, body: Decision, who=Depends(identity)):
        if who["role"] != "operator":
            raise HTTPException(403, "operator_required")
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

    return app


app = create_app()

