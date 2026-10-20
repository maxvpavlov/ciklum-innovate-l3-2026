# Lesson 02 Reliable tools and MCP integration

*Instructor guide for the L3 agentic platform programme*

**Outcome** Validated local and MCP tools share an application-owned permission boundary, exact-action approval and idempotent mock writes.

Duration: 120 minutes. Starting checkpoint: lesson-01. Ending checkpoint: lesson-02 (384c2fb).

Word version: [02 Reliable tools and MCP integration.docx](02%20Reliable%20tools%20and%20MCP%20integration.docx)

## Where this session sits in the platform

This session builds the platform's tool boundary: validated contracts, application-owned authorization, exact-action approval, an idempotent effect ledger and a real MCP transport. Each client launches its own MCP stdio server, which is deliberately simple; Session 09 replaces that with a central MCP tool gateway with shared upstream sessions, policy, audit and pinned tool definitions. The console's Gateway view (Session 09) will show the allow and deny decisions that ToolExecutor makes privately today, and Session 10 backs them with delegated credentials.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary and MCP transport | **This session** |
| 03 | Context selection, retrieval, memory and versioned artifacts | Later session |
| 04 | Evaluation harness and single-agent baseline | Later session |
| 05 | Durable runs, crash recovery and exact-action approval | Later session |
| 06 | Supervisor, scoped subagents and parallel coordination | Later session |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, run API and platform console | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 01 checkpoint. Review JSON Schema, tool contracts and MCP architecture. Pin compatible SDK/protocol versions. Mentor supplies client/server scaffolding; install and smoke-test it before class.

Give your coding agent access to the supplied incident-platform.zip or the reference repository in the [course materials folder](https://drive.google.com/drive/u/0/folders/1wos8PjyC0mTDQxrcZ89b9mG0yYV57Zr3). Ask it to preserve the embedded checkpoint history and identify the learner project separately from the reference.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my Python learner project for Lesson 02, starting from lesson-01. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

Next, orient the coding agent to the reference while preserving your work.

> **PROMPT** Compare my current project with lesson-01 and prepare a read-only view of lesson-02 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

**Instructor readiness** Have your coding agent rehearse the completed reference and prepare the current tests, fixtures and lab runner before class. Tests may fail until the capability is implemented. During class, use one bounded prompt at a time; learners inspect the change, explain the control decision and review the check evidence.

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

**SHOW** The current learner implementation and `incident/tools.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement ToolExecutor in incident/tools.py. Check tool existence, application-owned capabilities and JSON arguments before dispatch. Reject unexpected tenant arguments and oversized results. Return structured errors that distinguish terminal failures from retryable read failures. Preserve the existing agent loop. Demonstrate malformed arguments and an unauthorized write proposal being rejected before a handler performs an effect. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

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

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 2 Bind approval and deduplicate effects

**SAY** Approval must identify the actual action we reviewed. Our key includes tenant, run identifier, tool name and canonical arguments. Approving a rollback for INC-001 does not approve INC-002. Walk through the mock-effect transaction: either the idempotency record already exists, or we insert the effect and its result atomically. Restart the executor and make the same approved request again. The second result says replayed, and the ledger still contains one effect. Make clear that this is a local SQLite demonstration. For an external service, the receiver must support idempotency or an equivalent reconciliation design; a local flag cannot make an arbitrary remote operation exactly once.

**SHOW** The current learner implementation and `incident/tools.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Add exact-action approval and idempotent mock remediation to ToolExecutor. Bind the action key to tenant, run, tool name and canonical arguments. Commit the local mock effect and its deduplication record atomically in SQLite. Test the same approved write after reopening the executor and test changed arguments against the original approval. Show that only one local effect exists, and explain the limit of this guarantee for external APIs. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 19 to 21 at lesson-02; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def action_key(name, args, context):
    payload = [context.tenant, context.run_id, name, args]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
```

**Explain the choice** The action key prevents approval from drifting to different arguments. The database transaction gives the simulated effect and deduplication record one commit boundary.

**ASK** Why is checking a dictionary before a remote write insufficient?

**Likely answer** The process can crash between the write and recording success. A durable receiver-side idempotency key or reconciliation mechanism is needed.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 3 Expose capabilities with MCP

**SAY** Create the MCP server using the pinned SDK. The decorated functions call the same fixture-backed readers, and the resource exposes a runbook index. Tenant identity is fixed when the server starts. The model supplies an incident or query, never the tenant. Explain the transport before launching it: stdout is reserved for the protocol, so diagnostic logging belongs on stderr. Show the resource URI and ask how it differs from calling runbook_search. The resource is addressable content, while the tool performs a parameterized operation. Authentication for this stdio demonstration is the trusted process boundary; do not present it as a tested remote identity flow.

**SHOW** The current learner implementation and `incident/mcp_bridge.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement the MCP server in incident/mcp_bridge.py with the pinned SDK. Expose the existing tenant-scoped log and runbook readers plus the runbook resource. Bind tenant identity in trusted launcher configuration, keep protocol stdout clean, and limit the server to the capabilities required by this lesson. Explain the host, client, server and resource roles before demonstrating discovery. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

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

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 4 Run through the client adapter

**SAY** Replace only the read handler with MCPReadAdapter and run the original investigation. The executor still validates and authorizes calls before the adapter sends them. Inspect the discovered names and negotiated protocol, then compare the final source IDs with Session 01. Highlight the SDK's snake_case result fields, including is_error and structured_content. A version mismatch here is an integration problem, not an agent reasoning problem. Finally, test denied writes, extra arguments and oversized results. Pause until each participant can explain where an MCP failure becomes an application error and why terminal failures should not trigger a retry storm.

**SHOW** The current learner implementation and `incident/mcp_bridge.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 02, continue in my learner project. Implement the MCP read adapter and connect it behind ToolExecutor. Use the real local stdio transport and the pinned SDK's result shapes. Complete the Session 02 lab and contract tests, show the negotiated protocol and discovered tools, and run the same investigation through the adapter. Confirm that transport discovery does not grant new permissions and show the unchanged cited outcome. Use lesson-02 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

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

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 02 learner exercise in my existing project: Add an unexpected tenant argument to a log request, call mock_remediate with a read-only Context, lower output_limit, and repeat an approved mock write after reopening the SQLite executor. Record the error category or replay behaviour for each case. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 02 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 2 only when the required capability is present. Run tests/test_lesson02.py, the Session 02 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

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

The independently unpacked lesson-02 checkpoint passed its full test suite and this lesson demo. Recorded test result: 10 passed in 1.96s. Have your coding agent save a recoverable learner checkpoint and retain the comparison with lesson-02 (384c2fb).

### Files changed in this checkpoint

Use this inventory to scope the coding agent’s work. It includes core files, lab scaffolding, acceptance tests and checkpoint metadata. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/labs/l02.py`
- `incident/mcp_bridge.py`
- `incident/tools.py`
- `tests/test_lesson02.py`

> **PROMPT** Compare my completed Lesson 02 work with reference lesson-02. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

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

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

## Session close

**SAY** Your platform now has a tested tool boundary and a real protocol adapter. Keep that boundary intact as the platform grows: Session 09 centralizes it in a tool gateway, and Session 10 backs today's application-owned authorization with delegated, short-lived credentials. Next we decide which evidence enters the model's context and how to keep stored artifacts and memory separate from authority.

## References and further study

- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture)
