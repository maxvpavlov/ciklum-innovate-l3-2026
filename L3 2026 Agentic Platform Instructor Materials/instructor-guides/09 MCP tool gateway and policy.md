# Lesson 09 MCP tool gateway and policy

*Instructor guide for the L3 agentic platform programme*

**Outcome** Every agent tool call passes one gateway that applies policy, audits the decision, shares one upstream MCP session per server and tenant, and quarantines a server whose pinned tool definitions change.

Duration: 90 minutes. Starting checkpoint: lesson-08. Ending checkpoint: lesson-09 (ffd4ea9).

Word version: [09 MCP tool gateway and policy.docx](09%20MCP%20tool%20gateway%20and%20policy.docx)

## Where this session sits in the platform

This session builds the MCP tool gateway, which sits between every agent the platform runs and every tool server in the registry. Until now each team run launched its own MCP process and each worker checked permissions alone. The console gains a Gateway view: the policy in force, each tool server with its risk levels and pinned definition hashes, and a tenant-scoped audit of allow and deny decisions.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary and MCP transport | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | Built earlier |
| 04 | Evaluation harness and single-agent baseline | Built earlier |
| 05 | Durable runs, crash recovery and exact-action approval | Built earlier |
| 06 | Supervisor, scoped subagents and parallel coordination | Built earlier |
| 07 | Remote agents over A2A | Built earlier |
| 08 | Platform core: agent registry, run API and platform console | Built earlier |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | **This session** |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 08 checkpoint with the registry, run API and console working. Read the MCP tools and security best-practices pages, especially tool poisoning and token passthrough. Prepare one example of a tool your organization would let analysts read but only operators write.

Learners need two things: their own project repository in the course GitLab group, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 09. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-08 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/09 in the course repository: its README, the given files and the check pack. Copy the given files and the check pack into my project exactly as the README says, without changing them, and commit that. Then list the interfaces my code must provide, which checks now fail and why, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

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

**SAY** In Session 08 the platform learned which agents exist. It still has no single view of the tools they call. Each team run starts its own MCP subprocess, each worker enforces its own allowed list, and nothing records a denied call. Today we put one gateway in front of every tool. It checks policy before any upstream connection, audits every decision, shares one MCP session per server and tenant, and pins each tool definition on first connection. If a server later changes a tool description, the gateway quarantines it instead of passing the new text to a model.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw agents on the left, tool servers on the right and one box between them. The gateway decides and enforces policy in the same place. The registry supplies the catalog: which server owns a tool, its risk and the tenants it serves. The run's Context supplies identity: tenant, role, granted tools and run ID. The model supplies only a tool name and arguments, and both are untrusted input. Then add the threat behind pinning. An MCP tool description goes straight into the model's prompt, so a server that changes a description changes agent behaviour without any code change on our side: the rug-pull or tool-poisoning problem. Our gateway runs in the platform process to keep the course offline; production gateways are usually separate services that speak MCP on both sides.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Register tool servers and their manifests

**SAY** Start with the catalog, because a gateway cannot decide anything about a tool it cannot name. A manifest has exactly three keys: transport, tenants served and tools, each tool with a risk of read or write. The platform seeds two servers: incident-tools, the real MCP stdio server with log_lookup and runbook_search, and platform-actions, a local handler for the write tool mock_remediate. Like agent definitions in Session 08, registration is immutable: a different manifest under an existing name fails with server_manifest_changed. Show catalog(), which maps each tool name to its server, risk, tenants and status. Every gateway decision starts from that map.

**SHOW** The current learner implementation and `incident/registry.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 09, continue in my learner project. Extend the registry with tool-server records whose manifest names the transport, the tenants served and each tool's risk as read or write. Validate the name and manifest shape, reject a changed manifest under an existing name, and add a catalog from tool to server, risk, tenants and status. Seed the MCP read server and the local write-action server. Show the catalog and one rejected manifest. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 111 to 122 at lesson-09; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def register_tool_server(self, name, manifest):
    """A server manifest names its transport, served tenants and each tool's risk."""
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", name):
        raise ValueError("invalid_server_identity")
    if set(manifest) != {"transport", "tenants", "tools"} or not all(
            t.get("risk") in {"read", "write"} for t in manifest["tools"].values()):
        raise ValueError("invalid_server_manifest")
    old = self.db.execute("SELECT manifest FROM tool_servers WHERE name=?", (name,)).fetchone()
    if old and json.loads(old[0]) != manifest:
        raise ValueError("server_manifest_changed")
    self.db.execute("INSERT OR IGNORE INTO tool_servers VALUES (?,?,?,?)",
                    (name, json.dumps(manifest, sort_keys=True), "{}", "registered"))
```

**Explain the choice** Risk and served tenants are declared once by the platform owner. Keeping them in the registry means a model cannot turn a write tool into a read tool or add a tenant by describing it differently.

**ASK** Why is a changed manifest rejected rather than updated in place?

**Likely answer** Policy decisions and audit rows refer to what the manifest said at the time. A silent update would change their meaning, so a real change needs a new, reviewed registration.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Decide and audit every call in one place

**SAY** Open ToolGateway.check and read the order aloud: unknown tool, not granted to this run, tenant not served, quarantined server, write tool without an operator role, oversized arguments, then the per-run call budget. Each denial returns a stable reason code, and no deny path opens an upstream connection. Then read execute. A denial is audited and returned to the loop as a non-retryable error. An allowed call goes to the existing ToolExecutor, so schema validation, exact-action approval from Session 05 and the effect ledger are unchanged. Each audit row records tenant, run, parent run, role, tool, server, decision and reason, plus a SHA-256 of the arguments instead of the arguments.

**SHOW** The current learner implementation and `incident/gateway.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 09, continue in my learner project. Create a ToolGateway with an explicit policy: a per-run call budget, a maximum argument size and the roles allowed to use write tools. Check each call in a fixed order, returning a stable reason code for every denial before any upstream connection. Audit every decision with an argument hash, not the raw arguments. Wrap the existing executor for allowed calls so validation, approval and effects stay unchanged. Show one allowed call and three denials with their audit rows. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 37 to 53 at lesson-09; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def check(self, name, args, context):
    entry = self.registry.catalog().get(name)
    if entry is None:
        return "deny", "unknown_tool", None
    if name not in context.allowed:
        return "deny", "not_granted", entry["server"]
    if context.tenant not in entry["tenants"]:
        return "deny", "tenant_not_served", entry["server"]
    if entry["status"] == "quarantined":
        return "deny", "tool_definition_changed", entry["server"]
    if entry["risk"] == "write" and context.role not in self.policy.write_roles:
        return "deny", "write_role_required", entry["server"]
    if len(json.dumps(args)) > self.policy.max_argument_chars:
        return "deny", "argument_policy", entry["server"]
    if self.calls[context.run_id] >= self.policy.max_calls_per_run:
        return "deny", "tool_call_budget", entry["server"]
    return "allow", "policy_passed", entry["server"]
```

**Explain the choice** Checks that need no network run first, so a denied call costs nothing upstream and sends nothing to a server. Reusing the executor keeps one implementation of validation and approval instead of two that can drift.

**ASK** Why does the audit store an argument hash instead of the arguments?

**Likely answer** Arguments can contain customer data or secrets. A hash still lets an investigator match a call to a known input without making the audit a second copy of sensitive data.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Share upstream MCP sessions safely

**SAY** Before today every team run launched its own MCP subprocess, so ten concurrent runs meant ten processes. The gateway keeps one session per server and tenant, created under a lock and shared by all workers. The launcher still binds the tenant, as in Session 02, so no session crosses tenants. Now the owner task. The MCP client is an async context manager built on anyio cancel scopes, and a cancel scope must be exited by the task that entered it. If one worker opened the client and cleanup closed it from another task, shutdown would fail or hang. So one owner task opens the client, lists and pins the tools, publishes the client through a future and waits for a stop event. close() sets each stop event and awaits each owner.

**SHOW** The current learner implementation and `incident/gateway.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 09, continue in my learner project. Replace per-run MCP clients with one upstream session per server and tenant in the gateway, created under a lock and shared by all workers. Open and close each client in a single owner task so its cancel scopes are entered and exited by the same task. Stop waiting callers from cancelling the shared session, drop a session after an upstream error and close all sessions at shutdown. Show the launch count after several runs. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 92 to 116 at lesson-09; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
    if key not in self.sessions:
        ready, stop = asyncio.get_running_loop().create_future(), asyncio.Event()

        async def owner():
            # The task that opens the MCP client is also the task that closes it.
            try:
                async with self.launcher(tenant) as client:
                    listing = await client.list_tools()
                    try:
                        self.registry.pin_tools(server, {t.name: digest(t.model_dump(mode="json", exclude_none=True))
                                                         for t in listing.tools})
                    except ValueError as exc:
                        ready.set_exception(exc)
                        return
                    ready.set_result(client)
                    await stop.wait()
            except BaseException as exc:
                if not ready.done():
                    ready.set_exception(exc)
                if not isinstance(exc, Exception):
                    raise

        self.sessions[key] = (ready, stop, asyncio.create_task(owner()))
        self.launches[key] += 1
return await asyncio.shield(self.sessions[key][0])
```

**Explain the choice** Sharing sessions cuts process launches without widening access, because the key includes the tenant. The owner task respects the anyio rule that a cancel scope belongs to one task, and asyncio.shield stops one cancelled worker from cancelling the session for everyone.

**ASK** Why not share one MCP session across Astro and Locomotive to save another process?

**Likely answer** The tenant is bound when the server starts. A shared session would let one tenant's calls read the other's data, which is the boundary the platform exists to keep.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Pin tool definitions and route every worker through the gateway

**SAY** On first connection the owner task hashes each tool definition and the registry records the hashes as pins. On a later connection any difference marks the server quarantined and raises tool_definition_changed, and check() then denies every tool on that server before connecting. The lab proves it with a fixture that appends one sentence to a tool description. Be honest about the limit: these pins are trust-on-first-connect, so a server that is hostile on first contact is pinned as it is. Production pins come from a reviewed definition. Finally, the platform hands the gateway to single runs, team workers and the remediator, so no worker can reach a tool around it. The MCP server now uses the ranked retrieval from Session 03, so single runs give the same answers through MCP.

**SHOW** The current learner implementation and `incident/registry.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 09, continue in my learner project. Pin each MCP tool definition by hash on the gateway's first connection to a server, and quarantine the server if a later connection reports different definitions. Deny every tool on a quarantined server before any upstream call. Route single runs, team workers and remediation through the gateway, and add the Gateway console view. Show a changed-definition fixture and the resulting quarantine. Build to the interfaces the Lesson 09 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 124 to 131 at lesson-09; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def pin_tools(self, name, pins):
    """Record reviewed tool definitions; later differences quarantine the server."""
    current = self.tool_server(name)
    if current["pins"] and current["pins"] != pins:
        self.db.execute("UPDATE tool_servers SET status='quarantined' WHERE name=?", (name,))
        raise ValueError("tool_definition_changed")
    self.db.execute("UPDATE tool_servers SET pins=?, status=? WHERE name=? AND status!='quarantined'",
                    (json.dumps(pins, sort_keys=True), "pinned", name))
```

**Explain the choice** A tool description is part of the prompt, so a changed description is an unreviewed prompt change. Quarantine stops use until a person decides, rather than trusting whatever the server says today.

**ASK** Does pinning prove that the tool server is safe?

**Likely answer** No. It proves only that the definitions have not changed since the first connection. Whether they were safe then still needs review, and pinning says nothing about what the server does with the arguments.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

![Point at the policy tiles, then at incident-tools with one session launched and a pinned hash per tool (a pinned server shows the active badge). In the audit, the logs and runbooks rows are a team run's child workers and the analyst rows are a single run; each row has an argument hash, never the arguments.](../console-screenshots/09-gateway.png)

**CONSOLE** Point at the policy tiles, then at incident-tools with one session launched and a pinned hash per tool (a pinned server shows the active badge). In the audit, the logs and runbooks rows are a team run's child workers and the analyst rows are a single run; each row has an argument hash, never the arguments.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 09 learner exercise in my existing project: Create a second gateway over the same registry with a lower per-run call budget and a tighter argument limit, leaving the platform's policy unchanged. Predict which calls of one investigation and three hand-written calls will be denied, and with which reason codes. Run them, compare the audit rows with your prediction and view the platform's audit in the console Gateway view. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 09 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 9 only when the required capability is present. Run the Lesson 09 check pack, which includes tests/test_lesson09.py and the Session 09 demonstration, and the full regression suite, all unchanged and using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "completed_runs": [
    "team",
    "team",
    "single"
  ],
  "mcp_sessions_launched": {
    "incident-tools/astro": 1
  },
  "denials": {
    "not_granted": "not_granted",
    "write_role_required": "write_role_required",
    "argument_policy": "argument_policy"
  },
  "changed_definition": {
    "first_call": "tool_definition_changed",
    "next_call": "tool_definition_changed",
    "server_status": "quarantined"
  },
  "audit_decisions": {
    "deny": 4,
    "allow": 7
  }
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- Two team runs and one single run complete for Astro through one shared upstream MCP session.
- Ungranted tools, writes without an operator role and oversized arguments are denied with stable reason codes before any upstream connection.
- A changed tool description quarantines the server, and later calls to it are denied.
- Every decision is audited with an argument hash, and the Gateway view is tenant-scoped.
- Workers reach tools only through the gateway, and the platform closes upstream sessions on shutdown.

The independently unpacked lesson-09 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 09 check pack from the course kit. Recorded test result: 37 passed in 9.91s. Learners commit and push their checkpoint to their GitLab repository; lesson-09 (ffd4ea9) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 09 check pack. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/api.py`
- `incident/console/views/gateway.js`
- `incident/console/views/index.js`
- `incident/gateway.py`
- `incident/labs/l09.py`
- `incident/mcp_bridge.py`
- `incident/platform.py`
- `incident/registry.py`
- `incident/supervisor.py`
- `tests/test_lesson09.py`

> **PROMPT** Review my completed Lesson 09 work against the Lesson 09 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out where my design makes a different choice from the one the lesson presents, and what that choice costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### The session count is higher than one per tenant

> **PROMPT** I am working on Lesson 09. The symptom is: The session count is higher than one per tenant. Diagnostic focus: A run path still creates its own MCP client or tool executor, the supervisor ignores the injected gateway, or sessions are created outside the gateway lock. Recovery guidance: Pass the platform's gateway to every run kind and to the supervisor, and create sessions only inside the locked session method. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Shutdown hangs or reports a cancel scope exited in a different task

> **PROMPT** I am working on Lesson 09. The symptom is: Shutdown hangs or reports a cancel scope exited in a different task. Diagnostic focus: The MCP client is opened in one task and closed in another, or a waiting caller cancels the shared session future. Recovery guidance: Keep open, listing, pinning and close in one owner task per session, signal it with a stop event, shield the shared future and close the platform from the API lifespan. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Every call to incident-tools is denied as tool_definition_changed

> **PROMPT** I am working on Lesson 09. The symptom is: Every call to incident-tools is denied as tool_definition_changed. Diagnostic focus: The server was quarantined earlier, often by the changed-definition fixture writing to the same platform database. Recovery guidance: Find which definition changed and why. For a local experiment use a fresh database. Do not overwrite the pins or weaken the quarantine check to get a pass. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A normal investigation is denied by gateway policy

> **PROMPT** I am working on Lesson 09. The symptom is: A normal investigation is denied by gateway policy. Diagnostic focus: Read the audit reason: tool_call_budget counts allowed calls per run ID, argument_policy measures serialized arguments and not_granted means the agent definition lacks the tool. Recovery guidance: Change the policy or agent definition deliberately with a recorded reason, or fix the caller. Do not bypass the gateway. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Propose one policy rule for your organization, such as a per-tenant daily budget, and say where it belongs in the check order.
- Describe what a production MCP gateway adds: a separate MCP-speaking service, OAuth per the MCP authorization specification without token passthrough, reviewed pins instead of trust-on-first-connect, and approval-bound write tools.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

The SQLite mock-effect ledger proves its local transaction boundary. It does not guarantee exactly-once effects for arbitrary external APIs. The A2A specialist task store is in memory. The restricted Compose sandbox uses temporary writable state; persistent deployment storage requires separate configuration and validation.

Tokens are HMAC-signed with one shared development key so the course runs offline; a production issuer signs asymmetrically and publishes verification keys. The credential store keeps values in process memory and is not a vault. The gateway runs in the platform process; production gateways are usually separate network services.

## Session close

**SAY** The platform now has one place where tool use is decided, recorded and connected, and a changed tool description stops a server instead of reaching a model. The gateway still trusts the Context it is given. In Session 10 users and agents get real identities and short-lived delegated credentials, and the gateway checks a delegated token alongside the Context.

## References and further study

- [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP security best practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [MCP authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
