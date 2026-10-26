# Lesson 02 Reliable tools and MCP integration

*Instructor guide for the L3 agentic platform programme*

**Outcome** Validated local and MCP tools share an application-owned permission boundary, exact-action approval and idempotent mock writes, and the platform gets its first console, where runs and tool decisions are visible.

Duration: 120 minutes. Starting checkpoint: lesson-01. Ending checkpoint: lesson-02 (7bbf4af).

Word version: [02 Reliable tools and MCP integration.docx](02%20Reliable%20tools%20and%20MCP%20integration.docx)

## Where this session sits in the platform

This session builds the platform's tool boundary: validated contracts, application-owned authorization, exact-action approval, an idempotent effect ledger and a real MCP transport. Each client launches its own MCP stdio server, which is deliberately simple; Session 09 replaces that with a central MCP tool gateway with shared upstream sessions, policy, audit and pinned tool definitions. From this session the platform also has a face: the kit gives a small run API and console, given rather than built, where each run's event timeline and the Tools view show the allow and deny decisions ToolExecutor makes. Session 08 replaces the in-memory shell with the platform core and learners extend the console from there; Session 09 adds a Gateway view, and Session 10 backs these decisions with delegated credentials.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary, MCP transport and the first console | **This session** |
| 03 | Context selection, retrieval, memory and versioned artifacts | Later session |
| 04 | Evaluation harness and single-agent baseline | Later session |
| 05 | Durable runs, crash recovery and exact-action approval | Later session |
| 06 | Supervisor, scoped subagents and parallel coordination | Later session |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, durable run API, registry and approval views | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 01 checkpoint. Review JSON Schema, tool contracts and MCP architecture. Pin compatible SDK/protocol versions. Mentor supplies client/server scaffolding; install and smoke-test it before class.

Learners need two things: their own project repository in the course GitLab group on gitlab.ciklum.net, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 02. Open my project repository in my course GitLab group on gitlab.ciklum.net, cloning it into ~/agentic-course/my-platform if it is not there, read its AGENTS.md first if it has one and follow it, and confirm it holds my completed lesson-01 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing, and tell me the commit it was at before and after the update and which files under learner-kit/lessons/02 changed; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Lesson 01 projects keep everything in incident/. Before the check pack, one prompt moves the project to the layout it keeps from now on (the agent runtime in agent_runtime/, the course scaffolding in course/), copies the given platform shell into agentic_platform/, adds AGENTS.md (the briefing every later coding-agent session reads first) and starts the platform. Learners sign in and see their own Lesson 01 agent run INC-001 in the console; the Tools view says the tool boundary is not built yet, which is this session's work.

> **PROMPT** Move my learner project to the course layout and start the platform, without adding this lesson's work, as the first section of learner-kit/lessons/02/README.md in the course repository describes. Move incident/core.py and incident/providers.py into a new agent_runtime/ package, and incident/__init__.py with my LESSON value, incident/lab.py and incident/fixtures.py into a new course/ package. Replace my tests with test_setup.py and test_lesson01.py from learner-kit/lessons/02/checks/tests, and incident/labs/ with __init__.py and l01.py from learner-kit/lessons/02/checks/course/labs, unchanged. Update the imports in my own modules, remove the empty incident/ folder, run the full test suite, which must still report 7 passed, and commit the move on its own. Then copy the given platform shell, everything under learner-kit/lessons/02/given/agentic_platform, into a top-level agentic_platform/ folder unchanged and commit it on its own. Then add learner-kit/lessons/02/AGENTS.template.md to my project root as AGENTS.md, fill in its Lesson 01 entry from my checkpoint and the test result you just saw, add a pointer file if your tool reads a different instruction file (for Claude Code, a CLAUDE.md containing @AGENTS.md), and commit that on its own. Start the platform API on loopback with the offline mock provider, keep it running and give me the console address: I will sign in as demo-astro, submit INC-001 in Runs and open the Tools view. Tell me how to stop it.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/02 in the course repository: its README, the given files and the check pack. The platform shell under given/agentic_platform is already in my project from the previous prompt; leave it unchanged. Copy the remaining given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

**Instructor readiness** Rehearse the session with a learner project built from the course kit, so you see what learners see: the check pack fails until each capability is built. The reference checkpoint remains your answer key for the excerpts below. In class, use one bounded prompt at a time; learners inspect the change, explain the control decision and review the check evidence.

**Offline fallback** Have the coding agent use the offline mock provider for class. If live access fails, restore that configuration and continue. Keep credentials in secure configuration. Adapter request shapes were tested with mock HTTP; live account access was not exercised.

Pinned versions in pyproject.toml and uv.lock: Python 3.12, MCP 2.2.0, A2A SDK 1.1.2, httpx 0.28.1, FastAPI 0.141.1, uvicorn 0.52.4, jsonschema 4.26.0, pytest 9.1.1 and pytest-asyncio 1.4.0. Have the coding agent manage their installation.

## Timed agenda

| Minutes | Activity | Format |
|---|---|---|
| 00 to 10 | Reconnect to the incident and prior checkpoint | Discussion |
| 10 to 30 | Concept script and architecture questions | Discussion |
| 30 to 50 | Prompts and code review for steps 1 and 2 | Agent build |
| 50 to 75 | Prompts and code review for steps 3 and 4 | Agent build |
| 75 to 100 | Learner exercise and fault injection | Practice |
| 100 to 115 | Acceptance checks and result interpretation | Verification |
| 115 to 120 | Questions and checkpoint handoff | Discussion |

## Instructor script and code walkthrough

Use SAY for instructor narration, SHOW and REVIEW for the code and evidence participants examine, PROMPT for text they give their coding agents, and PAUSE for discussion. Prompts define scope and expected behaviour; the agent handles command execution. Code excerpts remain as reading and review material from the exact reference checkpoint, not manual typing instructions.

### Opening and orientation

**SAY** Open yesterday's loop and identify its most consequential line: the executor call. A model can produce malformed arguments, repeat a request or propose a capability it does not possess. Today we turn that line into a predictable boundary. We will validate arguments, reject unauthorized operations, classify errors and prevent duplicate mock effects. Then we expose the read-only capabilities through MCP and use a real client transport. The investigation should still produce the same cited answer. Protocol adoption changes how we discover and reach a tool; our application still decides what a run may do.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw two paths from the same ToolExecutor: one to an in-process function and one to MCPReadAdapter. Put authorization and schema validation before both paths. Explain host, client and server roles, and distinguish tools from resources. The demo uses stdio, with tenant identity bound by the trusted process launcher. That is a deliberate local trust boundary. Launching one MCP stdio server per client is also deliberately simple: in Session 09 a central tool gateway shares upstream sessions, applies policy, audits every call and pins tool definitions. A remotely deployed HTTP MCP server would require its own authentication, token validation and authorization integration; the course does not claim to exercise OAuth. Discuss retryability before running anything: a transient read failure can be retried, while a permission rejection should not be retried. A write needs an idempotency design and exact approval, even if the model insists it is harmless.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Validate before dispatch

**SAY** Read the executor in order. First check that the tool exists, then check the run's capabilities, then validate the arguments. This sequence matters: we do not let the model expand its permissions by naming a tool. Show an extra tenant argument in a log_lookup request. additionalProperties is false, so the model cannot select another tenant through an otherwise legitimate tool. A denied request returns a structured terminal error. The agent can observe that error, but observing it does not change the permission decision. Ask learners to point to the exact branch that would stop an injected request for mock_remediate from a read-only investigator.

**SHOW** The current learner implementation and `agent_runtime/tools.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement ToolExecutor in agent_runtime/tools.py. Check tool existence, application-owned capabilities and JSON arguments before dispatch. Reject unexpected tenant arguments and oversized results. Return structured errors that distinguish terminal failures from retryable read failures. Preserve the existing agent loop. Demonstrate malformed arguments and a tool the run was not granted being rejected before a handler runs. The check pack needs ToolExecutor(db=":memory:", read_handler=simple_tools, output_limit=6000), whose output_limit attribute a test changes; available(context), which returns only the schemas the context allows; and async execute(name, args, context), which returns the handler's result or {"ok": false, "error": code, "retryable": true or false}. Use the codes unknown_tool, permission_denied, invalid_arguments and output_too_large (all terminal), and tool_unavailable (retryable) when a read still times out or loses its connection after one retry. Check the permission before validating the arguments. The given platform shell also creates ToolExecutor() with no arguments, so give every parameter a default (an in-memory database and the Session 01 readers), and it lists the tool catalogue from a schemas attribute: every tool the executor knows, which gains mock_remediate in the next step. This lesson's test file cannot import until action_key exists in the next step, so check this step with your demonstration and the Session 01 tests. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 34 to 51 at lesson-02; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
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
```

**Explain the choice** The same checks apply regardless of transport. Schemas provide predictable interfaces, while Context supplies authority. Output-size limits prevent an unexpectedly large result from consuming the whole conversation.

**ASK** Can a correct JSON Schema make a tool safe by itself?

**Likely answer** No. A well-formed request can still be unauthorized or harmful. Authorization, effect ownership and operational limits are separate checks.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Bind approval and deduplicate effects

**SAY** Approval must identify the actual action we reviewed. Our key includes tenant, run identifier, tool name and canonical arguments. Approving a rollback for INC-001 does not approve INC-002. Walk through the mock-effect transaction: either the idempotency record already exists, or we insert the effect and its result atomically. Restart the executor and make the same approved request again. The second result says replayed, and the ledger still contains one effect. Make clear that this is a local SQLite demonstration. For an external service, the receiver must support idempotency or an equivalent reconciliation design; a local flag cannot make an arbitrary remote operation exactly once.

**SHOW** The current learner implementation and `agent_runtime/tools.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Add exact-action approval and idempotent mock remediation to ToolExecutor. Add a mock_remediate tool schema with incident_id (INC- followed by three digits) and action (only rollback), and add it to schemas. Use ApprovalRequired in agent_runtime/core.py, adding it if your core does not have it yet: an exception whose action attribute holds the proposed key, name and args. action_key(name, args, context) returns the key; execute raises ApprovalRequired when that key is not in context.approved, and an approved write returns its result with replayed false the first time and the stored result with replayed true after that. Bind the action key to tenant, run, tool name and canonical arguments. Commit the local mock effect and its deduplication record atomically in SQLite. Test the same approved write after reopening the executor and test changed arguments against the original approval. Show that only one local effect exists, and explain the limit of this guarantee for external APIs. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 19 to 21 at lesson-02; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def action_key(name, args, context):
    payload = [context.tenant, context.run_id, name, args]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
```

**Explain the choice** The action key prevents approval from drifting to different arguments. The database transaction gives the simulated effect and deduplication record one commit boundary.

**ASK** Why is checking a dictionary before a remote write insufficient?

**Likely answer** The process can crash between the write and recording success. A durable receiver-side idempotency key or reconciliation mechanism is needed.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Expose capabilities with MCP

**SAY** Create the MCP server using the pinned SDK. The decorated functions call the same fixture-backed readers, and the resource exposes a runbook index. Tenant identity is fixed when the server starts. The model supplies an incident or query, never the tenant. Explain the transport before launching it: stdout is reserved for the protocol, so diagnostic logging belongs on stderr. Show the resource URI and ask how it differs from calling runbook_search. The resource is addressable content, while the tool performs a parameterized operation. Authentication for this stdio demonstration is the trusted process boundary; do not present it as a tested remote identity flow.

**SHOW** The current learner implementation and `agent_runtime/mcp_bridge.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement the MCP server in agent_runtime/mcp_bridge.py with the pinned SDK. Expose the existing tenant-scoped log and runbook readers plus the runbook resource. Bind tenant identity in trusted launcher configuration, keep protocol stdout clean, and serve only the two read tools and the runbook resource: no write tool and no prompts. If the pinned SDK still advertises an empty capability, report it rather than working around it. Explain the host, client, server and resource roles before demonstrating discovery. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 11 to 29 at lesson-02; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def make_server(tenant="astro"):
    server = MCPServer("incident-tools")
    context = Context(tenant=tenant)

    @server.tool()
    async def log_lookup(incident_id: str) -> dict:
        """Read diagnostic incident evidence in the launcher's tenant."""
        return await simple_tools("log_lookup", {"incident_id": incident_id}, context)

    @server.tool()
    async def runbook_search(query: str) -> dict:
        """Find relevant runbook evidence in the launcher's tenant."""
        return await simple_tools("runbook_search", {"query": query}, context)

    @server.resource("incident://runbooks")
    def runbooks() -> str:
        return json.dumps([r for r in RUNBOOKS if r["tenant"] == tenant])

    return server
```

**Explain the choice** MCP standardizes discovery and access without supplying the application's scheduler or permission policy. The reference pins mcp 2.2.0 and the exercised connection negotiates protocol 2026-07-28.

**ASK** Who is responsible for preventing this client from launching an arbitrary process?

**Likely answer** The host application or operator. Our launcher uses a fixed module and the current interpreter; model output cannot choose the command.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Run through the client adapter

**SAY** Replace only the read handler with MCPReadAdapter and run the original investigation. The executor still validates and authorizes calls before the adapter sends them. Inspect the discovered names and negotiated protocol, then compare the final source IDs with Session 01. Highlight the SDK's snake_case result fields, including is_error and structured_content. A version mismatch here is an integration problem, not an agent reasoning problem. Finally, test denied writes, extra arguments and oversized results. Pause until each participant can explain where an MCP failure becomes an application error and why terminal failures should not trigger a retry storm.

**SHOW** The current learner implementation and `agent_runtime/mcp_bridge.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement the MCP read adapter and connect it behind ToolExecutor. The check pack needs stdio_client(tenant="astro"), which returns the pinned SDK's Client for a server started as python -m agent_runtime.mcp_bridge with INCIDENT_TENANT set by the launcher, and MCPReadAdapter(client), a read handler that returns the result's structured content when present and otherwise parses its JSON text content. Use the real local stdio transport and the pinned SDK's result shapes. A lost or closed MCP connection must reach ToolExecutor as a retryable read failure, so the executor returns tool_unavailable; the pinned SDK does not raise ConnectionError for it, so check what it does raise and show the result by stopping the server. Make the Session 02 check pack pass, show the negotiated protocol and discovered tools with your own short script (python -m course.lab 2 runs only once the verify step raises LESSON), and run the same investigation through the adapter. Confirm that transport discovery does not grant new permissions and show the unchanged cited outcome. Build to the interfaces the Lesson 02 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 39 to 50 at lesson-02; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
class MCPReadAdapter:
    def __init__(self, client):
        self.client = client

    async def __call__(self, name, args, context):
        # Use behind ToolExecutor, which validates and authorizes every dispatch.
        result = await self.client.call_tool(name, args)
        if result.is_error:
            return {"ok": False, "error": "mcp_tool_error"}
        if result.structured_content is not None:
            return result.structured_content
        return json.loads(next(c.text for c in result.content if c.type == "text"))
```

**Explain the choice** The real stdio test starts a subprocess and exercises the protocol. It complements unit tests of local validation and effect handling. HTTP MCP authentication and third-party MCP servers are not part of the verified demo.

**ASK** If the MCP server advertises a new write tool, does the agent automatically gain that capability?

**Likely answer** No. Discovery is information. The application's allowed capability set and validation policy must explicitly permit use.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 02 learner exercise in my existing project: Add an unexpected tenant argument to a log request, call mock_remediate with a read-only Context, lower output_limit, and repeat an approved mock write after reopening the SQLite executor. Record the error category or replay behaviour for each case; the replay case stays in the script, because the console's Tools view never approves a write. Then start the platform API on loopback with the offline provider and give me the console address: I will sign in as demo-astro and then demo-operator, submit INC-001 in Runs, and repeat the denied and approval cases in the Tools view. Tell me that console runs use the in-process readers rather than MCP, and that the Overview shows checkpoint lesson-01 until the verify step raises LESSON. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 02 implementation against its completion criteria. Update the checkpoint indicator in course/__init__.py to 2 only when the required capability is present. Run the full test suite, which includes the Lesson 02 check pack and every earlier lesson's tests, and then the Session 02 demonstration with python -m course.lab 2, all unchanged and using the offline provider (MODEL_PROVIDER unset or set to mock). Confirm that the passing count matches the one in the Lesson 02 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result. When the checks pass, add this lesson's entry to the progress log in AGENTS.md: the checkpoint, the test result you observed and what the lesson added, named as in the Lesson 02 check pack README, and nothing you did not see. Then commit my work and push it to my repository on gitlab.ciklum.net; if glab is also signed in to other GitLab hosts, make sure the push goes to gitlab.ciklum.net. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "tools": [
    "log_lookup",
    "runbook_search"
  ],
  "protocol": "2026-07-28",
  "answer": {
    "status": "complete",
    "cause": "connection_pool_exhaustion",
    "summary": "INC-001: connection_pool_exhaustion",
    "evidence": [
      "log-astro-001",
      "rb-pool-v1"
    ]
  },
  "write_without_capability": {
    "ok": false,
    "error": "permission_denied",
    "retryable": false
  }
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- The real stdio client discovers log_lookup and runbook_search.
- The investigation still cites the observed log and runbook.
- Malformed and denied requests fail before dispatch.
- Changing an approved action's arguments requires a new approval.
- A duplicate approved mock write produces one stored effect.
- The given console shows a completed run's timeline and each Tools check's decision for the signed-in role.

The independently unpacked lesson-02 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 02 check pack from the course kit. Recorded test result: 12 passed in 3.27s. Learners commit and push their checkpoint to their GitLab repository; lesson-02 (7bbf4af) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 02 check pack. Ask the agent to explain any additional file changes it needs.

- `README.md`
- `agent_runtime/__init__.py`
- `agent_runtime/core.py`
- `agent_runtime/mcp_bridge.py`
- `agent_runtime/providers.py`
- `agent_runtime/tools.py`
- `agentic_platform/__init__.py`
- `agentic_platform/api.py`
- `agentic_platform/blueprint.py`
- `agentic_platform/console/app.js`
- `agentic_platform/console/console.css`
- `agentic_platform/console/index.html`
- `agentic_platform/console/views/index.js`
- `agentic_platform/console/views/overview.js`
- `agentic_platform/console/views/runs.js`
- `agentic_platform/console/views/tools.js`
- `course/__init__.py`
- `course/fixtures.py`
- `course/lab.py`
- `course/labs/__init__.py`
- `course/labs/l01.py`
- `course/labs/l02.py`
- `incident/__init__.py`
- `tests/test_lesson01.py`
- `tests/test_lesson02.py`
- `tests/test_setup.py`

> **PROMPT** Review my completed Lesson 02 work against the Lesson 02 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### MCP startup or parsing fails

> **PROMPT** I am working on Lesson 02. The symptom is: MCP startup or parsing fails. Diagnostic focus: Look for debug output written to stdout or a process started from the wrong repository directory. Recovery guidance: Keep protocol stdout clean, use stderr logging and rerun the isolated stdio test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Result-field attribute error

> **PROMPT** I am working on Lesson 02. The symptom is: Result-field attribute error. Diagnostic focus: Compare the installed MCP version with the lock file and the result field names in the adapter. Recovery guidance: Restore the pinned Python 3.12 environment from the project lock file. Avoid mixing 1.x tutorial code with the 2.2.0 adapter. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Tool exists but returns permission_denied

> **PROMPT** I am working on Lesson 02. The symptom is: Tool exists but returns permission_denied. Diagnostic focus: Inspect Context.allowed rather than the server's discovery list. Recovery guidance: Use the intended read-only investigator or construct an operator-owned context explicitly for the mock-approval exercise. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A changed schema breaks an integration

> **PROMPT** I am working on Lesson 02. The symptom is: A changed schema breaks an integration. Diagnostic focus: The client-side tool contract and the discovered server contract differ. Recovery guidance: Pin the compatible server/client versions, update the adapter deliberately and rerun contract tests before using the changed tool. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Inject one transient read failure, verify the bounded retry, then make the failure terminal and confirm that it is not retried.
- Sketch the additional identity and token-validation controls required for a remote HTTP MCP deployment, and mark which of them the tool gateway (Session 09) and delegated credentials (Session 10) will provide.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 53 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

## Session close

**SAY** Your platform now has a tested tool boundary and a real protocol adapter. Keep that boundary intact as the platform grows: Session 09 centralizes it in a tool gateway, and Session 10 backs today's application-owned authorization with delegated, short-lived credentials. Next we decide which evidence enters the model's context and how to keep stored artifacts and memory separate from authority.

## References and further study

- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture)
