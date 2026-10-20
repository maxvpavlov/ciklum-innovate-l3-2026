# Lesson 07 A2A across independent agent services

*Instructor guide for the L3 agentic platform programme*

**Outcome** An independently hosted runbook specialist is discovered and invoked through the official A2A SDK, with streamed artifacts, authentication and remote cancellation.

Duration: 90 minutes. Starting checkpoint: lesson-06. Ending checkpoint: lesson-07 (974fd16).

Word version: [07 A2A across independent agent services.docx](07%20A2A%20across%20independent%20agent%20services.docx)

## Where this session sits in the platform

This session adds the first agent the platform does not run itself: a runbook specialist behind its own HTTP service, reached over A2A. In Session 08 its Agent Card becomes a registry entry pinned by hash, and the console's run detail shows the remote specialist as a child of the team run. Today's static demo bearer token is deliberately temporary: Session 10 replaces it with a delegated, audience-bound token from which the specialist derives the tenant.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary and MCP transport | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | Built earlier |
| 04 | Evaluation harness and single-agent baseline | Built earlier |
| 05 | Durable runs, crash recovery and exact-action approval | Built earlier |
| 06 | Supervisor, scoped subagents and parallel coordination | Built earlier |
| 07 | Remote agents over A2A | **This session** |
| 08 | Platform core: agent registry, run API and platform console | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 06 checkpoint. Read the current A2A specification and SDK documentation. Pin compatible SDK and protocol versions and prepare the service and client environment.

Learners need two things: their own project repository in the course GitLab group, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 07. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-06 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/07 in the course repository: its README, the given files and the check pack. Copy the given files and the check pack into my project exactly as the README says, without changing them, and commit that. Then list the interfaces my code must provide, which checks now fail and why, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

**Instructor readiness** Rehearse the session with a learner project built from the course kit, so you see what learners see: the check pack fails until each capability is built. The reference checkpoint remains your answer key for the excerpts below. In class, use one bounded prompt at a time; learners inspect the change, explain the control decision and review the check evidence.

**Offline fallback** Have the coding agent use the offline mock provider for class. If live access fails, restore that configuration and continue. Keep credentials in secure configuration. Adapter request shapes were tested with mock HTTP; live account access was not exercised.

Pinned versions in pyproject.toml and uv.lock: Python 3.12, MCP 2.2.0, A2A SDK 1.1.2, httpx 0.28.1, FastAPI 0.141.1, uvicorn 0.52.4, jsonschema 4.26.0, pytest 9.1.1 and pytest-asyncio 1.4.0. Have the coding agent manage their installation.

## Timed agenda

| Minutes | Activity | Format |
|---|---|---|
| 00 to 10 | Reconnect to the incident and prior checkpoint | Discussion |
| 10 to 30 | Concept script and architecture questions | Discussion |
| 30 to 45 | Prompts and code review for steps 1 and 2 | Agent build |
| 45 to 60 | Prompts and code review for steps 3 and 4 | Agent build |
| 60 to 75 | Learner exercise and fault injection | Practice |
| 75 to 85 | Acceptance checks and result interpretation | Verification |
| 85 to 90 | Questions and checkpoint handoff | Discussion |

## Instructor script and code walkthrough

Use SAY for instructor narration, SHOW and REVIEW for the code and evidence participants examine, PROMPT for text they give their coding agents, and PAUSE for discussion. Prompts define scope and expected behaviour; the agent handles command execution. Code excerpts remain as reading and review material from the exact reference checkpoint, not manual typing instructions.

### Opening and orientation

**SAY** So far, the platform owns the workers it launches. Today we connect a specialist that runs behind a separate service boundary. The runbook specialist advertises what it can do, accepts an A2A task and streams status and evidence back to our client adapter. The local demo uses a real HTTP server and the official SDK. We will also reject an unauthenticated request and cancel a deliberately slow remote task. Keep the distinction clear: internal scheduling, MCP tool integration and A2A service interoperability solve different parts of the platform problem.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw the platform client, Agent Card endpoint and A2A task endpoint. The card advertises interfaces, protocol version, capabilities and a runbook skill. A task has a lifecycle and may produce artifacts as it progresses. The application must still validate the discovered capability, authenticate requests, respect tenant boundaries and decide how remote failure affects the parent. The reference pins a2a-sdk 1.1.2 and uses its A2A 1.0 JSON-RPC binding. Its public types are Protocol Buffer messages, so request and response construction differs from older 0.3 examples. The specialist is deliberately bound to Astro and read-only runbook tools. Its remote task store is in memory; durable production task storage is a separate service responsibility. Nothing pins the card yet, and one shared token identifies no caller; Sessions 08 and 10 close those gaps.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Advertise the specialist capability

**SAY** Read the card as a contract rather than a marketing description. It identifies the supported interface, JSON-RPC binding, protocol version, streaming capability and runbooks skill. The advertised bearer scheme documents the authentication mechanism, while the middleware below it actually enforces it with a constant-time comparison. Show the well-known card endpoint and explain why clients should inspect capabilities before assuming that any remote agent can perform any task. The demo token is a plainly labelled local teaching credential shared by every caller, unsuitable for a public deployment; Session 10 replaces it with a short-lived token issued for this specialist's audience. Ask learners what should happen if the card changes between two calls.

**SHOW** The current learner implementation and `incident/a2a_service.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 07, continue in my learner project. Create the independent runbook specialist in incident/a2a_service.py with the pinned A2A SDK. Advertise the expected skill, interface, protocol and streaming capability through an Agent Card. Enforce the local teaching bearer credential at the endpoint and keep the service read-only and tenant-scoped. Explain what the card advertises, what application code actually enforces, and why this shared credential is temporary. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 45 to 59 at lesson-07; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
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
    if request.url.path == "/a2a" and not hmac.compare_digest(
        request.headers.get("authorization", ""), "Bearer "+token):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)
```

**Explain the choice** Discovery gives clients a typed description of a service. It does not grant authority or provide the platform's scheduler. The pinned SDK avoids mixing incompatible request shapes across A2A versions.

**ASK** Does advertising a security scheme protect the endpoint?

**Likely answer** No. The server must enforce authentication and authorization. The card describes the contract; middleware and service policy implement it.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Publish task lifecycle events and artifacts

**SAY** The executor first enqueues a Task, then sends a working status. That ordering is required by the SDK's event flow. It runs the same agent loop with runbook-only capabilities and publishes the result as an artifact before marking completion. Walk through the slow-task branch used by the cancellation test. Ask what the client should report if the stream ends before a completed status or before the evidence artifact arrives. It must not manufacture a successful result from a partial stream. Also point out that failure and completion are distinct terminal states. The tenant is hard-coded to Astro here; in Session 10 it comes from verified token claims, never from the message.

**SHOW** The current learner implementation and `incident/a2a_service.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 07, continue in my learner project. Implement SpecialistExecutor's task lifecycle using the SDK's event flow. Enqueue the initial task before status updates, run the existing agent loop with runbook-only access, publish evidence as an artifact and report the correct terminal state. Add the deterministic slow-task fixture for cancellation. Demonstrate incomplete execution without manufacturing a successful answer. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 21 to 36 at lesson-07; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def execute(self, context, event_queue):
    updater = TaskUpdater(event_queue, context.task_id, context.context_id)
    await event_queue.enqueue_event(p.Task(id=context.task_id, context_id=context.context_id,
        status=p.TaskStatus(state=p.TaskState.TASK_STATE_SUBMITTED)))
    await updater.start_work()
    task = context.get_user_input()
    if "SLOW" in task:
        await asyncio.sleep(2)
    ctx = Context(tenant="astro", allowed=("runbook_search",))
    tools = ToolExecutor(read_handler=context_tools)
    run = await run_agent(provider_from_env(), tools.execute, tools.available(ctx), task, ctx)
    if run.status != "completed":
        await updater.failed(); return
    await updater.add_artifact([p.Part(text=json.dumps({"answer": run.answer,
        "tokens": run.tokens, "run_id": run.context.run_id}))], name="runbook-evidence")
    await updater.complete()
```

**Explain the choice** Status and artifacts can arrive at different moments. Correct task initialization and terminal-state handling make that flow observable and testable.

**ASK** Why enqueue a Task before a status update?

**Likely answer** The task manager needs the task identity and initial state before applying lifecycle updates. The SDK rejects an invalid event sequence.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Normalize the remote result into the platform

**SAY** The client verifies the tenant boundary before making a request, resolves the card and checks the runbooks skill. It then consumes StreamResponse events, collecting the evidence artifact and terminal status. Only a completed task with an artifact becomes a successful platform result. This adapter keeps transport-specific protobuf objects out of the rest of our incident code. Show the normalized answer, source IDs and remote run ID. From Session 08 the platform records this call as a child of the team run; A2A itself provides neither that scheduler nor that trace.

**SHOW** The current learner implementation and `incident/a2a_client.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 07, continue in my learner project. Implement the platform-facing RemoteSpecialist adapter in incident/a2a_client.py. Check the allowed tenant, discover the expected capability, consume streamed artifacts and status, and normalize a completed result into the platform contract. Reject an incomplete stream. Show the evidence and remote run identifier, and explain what must be retained for later reconciliation. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 26 to 46 at lesson-07; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def investigate(self, task, context):
    if context.tenant != "astro":
        raise PermissionError("specialist_tenant_mismatch")
    async with httpx.AsyncClient(headers={"Authorization": "Bearer "+self.token}, timeout=10) as http:
        client = await discover_client(http, self.url)
        evidence, final, events = None, None, []
        try:
            async for event in client.send_message(request_for(task)):
                data = MessageToDict(event, preserving_proto_field_name=True)
                events.append(data)
                if event.HasField("artifact_update"):
                    for part in event.artifact_update.artifact.parts:
                        if part.text:
                            evidence = json.loads(part.text)
                if event.HasField("status_update"):
                    final = event.status_update.status.state
            if final != p.TaskState.TASK_STATE_COMPLETED or evidence is None:
                raise RuntimeError("incomplete_remote_task")
            return {**evidence, "events": events}
        finally:
            await client.close()
```

**Explain the choice** A narrow adapter isolates protocol details and makes incomplete remote execution an explicit error. The service remains independently deployable.

**ASK** Can we treat an artifact alone as proof that the remote task completed?

**Likely answer** No. It may be a partial artifact. Require the appropriate lifecycle state and the evidence contract.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Exercise real HTTP authentication and cancellation

**SAY** Run the complete demo and inspect four streamed events, the cited runbook result, HTTP 401 for the unauthorized request and TASK_STATE_CANCELED for the slow task. The helper starts an ephemeral loopback service and terminates it after the checks. For cancellation, the client first obtains a task ID using return-immediately polling and then sends CancelTask. Ask participants to describe what information must be retained if the client disconnects and later wants to inspect or cancel the task. A transport disconnect does not itself prove that remote execution stopped.

**SHOW** The current learner implementation and `incident/a2a_client.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 07, continue in my learner project. Make the Session 07 check pack pass with the real local HTTP demonstration, using the given service launcher for cleanup. Show discovery, streamed progress and evidence, rejection of an unauthenticated request, and confirmed cancellation of a slow remote task. Keep third-party services and live model calls out of this local check. Explain why a disconnected client is not proof that remote work has stopped. Build to the interfaces the Lesson 07 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 49 to 59 at lesson-07; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def cancel_slow_task(url):
    async with httpx.AsyncClient(headers={"Authorization": "Bearer demo-specialist-token"}, timeout=10) as http:
        client = await discover_client(http, url, streaming=False, polling=True)
        try:
            async for event in client.send_message(request_for("SLOW INC-001 payments")):
                task_id = event.task.id
                break
            task = await client.cancel_task(p.CancelTaskRequest(id=task_id))
            return p.TaskState.Name(task.status.state)
        finally:
            await client.close()
```

**Explain the choice** The acceptance test uses a real local HTTP connection and the official client and server protocol implementation. It does not verify third-party A2A agents, enterprise identity providers or cross-network deployment.

**ASK** If the network drops, is the remote task cancelled?

**Likely answer** Not necessarily. Reconcile the remote task state using its identifier and issue cancellation when required.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 07 learner exercise in my existing project: Run the local service separately, fetch its Agent Card and call the client adapter. Try a missing bearer credential, an unsupported skill declaration and a deliberately slow task. Record the distinction between authentication failure, capability mismatch, incomplete streaming and confirmed cancellation. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 07 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 7 only when the required capability is present. Run the Lesson 07 check pack, which includes tests/test_lesson07.py and the Session 07 demonstration, and the full regression suite, all unchanged and using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "protocol": "A2A 1.0 JSON-RPC",
  "answer": {
    "status": "complete",
    "cause": "connection_pool_exhaustion",
    "summary": "INC-001: connection_pool_exhaustion",
    "evidence": [
      "rb-pool-v1"
    ]
  },
  "stream_events": 4,
  "unauthorized_status": 401,
  "remote_cancellation": "TASK_STATE_CANCELED"
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- The card is fetched from the well-known endpoint and advertises the expected skill.
- The real HTTP stream contains task progress, an evidence artifact and completion.
- Unauthenticated task requests receive HTTP 401.
- The client rejects an incompatible tenant before making a request.
- The slow remote task reaches TASK_STATE_CANCELED.

The independently unpacked lesson-07 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 07 check pack from the course kit. Recorded test result: 27 passed in 2.88s. Learners commit and push their checkpoint to their GitLab repository; lesson-07 (974fd16) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 07 check pack. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/a2a_client.py`
- `incident/a2a_service.py`
- `incident/labs/l07.py`
- `incident/local_service.py`
- `tests/test_lesson07.py`

> **PROMPT** Review my completed Lesson 07 work against the Lesson 07 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out where my design makes a different choice from the one the lesson presents, and what that choice costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### An old tutorial's types or imports fail

> **PROMPT** I am working on Lesson 07. The symptom is: An old tutorial's types or imports fail. Diagnostic focus: Check whether it targets A2A 0.3 rather than the pinned 1.1.2 SDK and 1.0 protocol. Recovery guidance: Use the repository's protobuf request types, factory API and generated routes. Restore the lock file before debugging application logic. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The server rejects a status event

> **PROMPT** I am working on Lesson 07. The symptom is: The server rejects a status event. Diagnostic focus: A Task may not have been enqueued before the status update. Recovery guidance: Restore the initial Task event and rerun the lifecycle test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The stream ends with no complete answer

> **PROMPT** I am working on Lesson 07. The symptom is: The stream ends with no complete answer. Diagnostic focus: Inspect terminal status and whether an artifact was received. Recovery guidance: Report incomplete_remote_task and reconcile by task ID. Do not treat a disconnected stream as success. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A local port is already occupied

> **PROMPT** I am working on Lesson 07. The symptom is: A local port is already occupied. Diagnostic focus: Another process is using the fixed manual-demo port. Recovery guidance: Use the ephemeral-port lab helper or choose a different explicit loopback port and update the advertised base URL. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Compare local and remote specialist execution on the same task and record the additional failure modes.
- Decide which Agent Card fields a registry should pin, and what review should happen before a changed card is trusted again.
- Design a persistent task store and a per-caller service credential for the specialist without changing the platform-facing adapter contract.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

The SQLite mock-effect ledger proves its local transaction boundary. It does not guarantee exactly-once effects for arbitrary external APIs. The A2A specialist task store is in memory. The restricted Compose sandbox uses temporary writable state; persistent deployment storage requires separate configuration and validation.

## Session close

**SAY** Your platform can now exchange tasks and evidence with an independent agent service. Retain remote identifiers and explicit lifecycle checks. Next session we build the platform core: an agent registry that pins this specialist's card, a run API and the first views of the platform console.

## References and further study

- [A2A protocol specification](https://a2a-protocol.org/latest/specification/)
- [A2A Agent Discovery](https://a2a-protocol.org/latest/topics/agent-discovery/)
- [A2A Python SDK documentation](https://a2a-protocol.org/dev/sdk/python/api/index.html)
