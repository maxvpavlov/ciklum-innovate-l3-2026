# Lesson 05 Checkpoints, recovery and human approval

*Instructor guide for the L3 agentic platform programme*

**Outcome** Runs persist across worker loss, pause for exact-action approval, resume safely and reject denied or expired approvals.

Duration: 90 minutes. Starting checkpoint: lesson-04. Ending checkpoint: lesson-05 (ac763f6).

Word version: [05 Checkpoints recovery and human approval.docx](05%20Checkpoints%20recovery%20and%20human%20approval.docx)

## Where this session sits in the platform

This session builds the platform's durable run state: stored run snapshots, exact-action approval decisions and the effect ledger. Session 08 adds the console's Approvals view, where only an operator identity can decide and the decision must echo the current proposal key, while the Runs view flags a waiting run. Session 10 makes users and agents platform principals, so the operator can present a signed, short-lived token instead of a demo credential.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary and MCP transport | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | Built earlier |
| 04 | Evaluation harness and single-agent baseline | Built earlier |
| 05 | Durable runs, crash recovery and exact-action approval | **This session** |
| 06 | Supervisor, scoped subagents and parallel coordination | Later session |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, run API and platform console | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 04 checkpoint. Review transactions, idempotency and durable job processing. Study persistence and interrupts as design examples for your custom runtime.

Learners need two things: their own project repository in the course GitLab group, and the public [course kit](https://github.com/maxvpavlov/agentic-platforms-kit), which holds the starter project and, for each lesson, the given files and the check pack. The kit contains no solutions; the reference checkpoints stay with the instructor as the answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 05. Open my project repository in my course GitLab group, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-04 work with all its checks passing. Update my read-only copy of the course kit in ~/agentic-course/kit, cloning it from https://github.com/maxvpavlov/agentic-platforms-kit if it is missing. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read lessons/05 in the course kit: its README, the given files and the check pack. Copy the given files and the check pack into my project exactly as the README says, without changing them, and commit that. Then list the interfaces my code must provide, which checks now fail and why, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

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

**SAY** An agent can fail after deciding what to do, during a tool call or after an external effect has happened. A restart must distinguish those situations. Today we persist the same runtime state and demonstrate a deliberately difficult boundary: a worker disappears after a mock write but before it records the tool result. We will restart the executor, resume the run and prove that the effect ledger still contains one action. This lesson is about explicit ownership and recovery semantics, not merely saving a chat transcript.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw three durable records: the run snapshot, the approval decision and the effect ledger. They answer different questions. The snapshot says where execution stopped. Approval says which exact action a trusted operator accepted and until when. The ledger says whether the simulated effect already committed. Explain why persisting a pending call before dispatch matters. If the process crashes after the write, the pending call is still present and will be retried, so the receiver-side idempotency key must make that retry safe. Cancellation and denial are terminal control decisions. An expired approval should leave the operation waiting rather than silently renewing authority.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Persist reconstructible state

**SAY** Save the full Run snapshot under tenant and run ID, then reconstruct Context explicitly when loading. We are preserving messages, pending calls, counters, status and answer. The store does not infer authority from text. Show a lookup from the wrong tenant and confirm that it fails as run_not_found. Ask learners which fields must survive a crash before the model receives its tool result. The pending call and its identifier must survive, because they connect the stored assistant request to the eventual observation. The local file is our durable boundary for the exercise; process memory is not sufficient.

**SHOW** The current learner implementation and `incident/durable.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 05, continue in my learner project. Implement RunStore in incident/durable.py so it persists and reconstructs the current runtime state under tenant and run ID. Preserve messages, pending calls, usage counters and control state. Use a persistent local database for restart checks. Show which data must survive a crash before a tool observation is recorded, and demonstrate that another tenant cannot load the run. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 16 to 18 at lesson-05; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def save(self, run):
    self.db.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?)",
        (run.context.tenant, run.context.run_id, run.status, json.dumps(run.snapshot())))
```

**Explain the choice** A restart can rebuild the run without replaying every previous model decision. Tenant-scoped keys preserve the access boundary during recovery.

**ASK** Is saving only the final answer enough for recovery?

**Likely answer** No. A run may not have a final answer, and we must know pending calls, counters and control state to resume safely.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Store the exact approval decision

**SAY** Start the remediation fixture and observe waiting_approval. No effect has happened. The trusted operator now approves the proposed tool name and arguments, whose canonical action key is stored with an expiry. Read the denial branch and the approved_keys query. Approval is a separate durable record and must still be valid when execution resumes. This is also where we distinguish operator action from model preference. RemediationProvider is a deterministic fixture used to reach the approval branch; it is not a real operational recommendation. All effects remain in the local mock ledger.

**SHOW** The current learner implementation and `incident/durable.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 05, continue in my learner project. Implement durable approval decisions with exact action keys, expiry and denial. Reach the waiting state using the clearly labelled remediation fixture, with no real external action. Show the exact proposed tool and arguments. Keep the human decision separate from execution: do not approve on my behalf while preparing the demonstration. Explain how the stored decision is checked again at resume time. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 27 to 39 at lesson-05; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def decide(self, tenant, run_id, decision="approve", ttl=300):
    if decision not in {"approve", "deny"}:
        raise ValueError("invalid_decision")
    run = self.load(tenant, run_id)
    if run.status != "waiting_approval" or not run.pending:
        raise ValueError("no_pending_approval")
    call = run.pending[0]
    key = action_key(call["name"], call["args"], run.context)
    self.db.execute("INSERT OR REPLACE INTO approvals VALUES (?,?,?,?,?)",
                    (tenant, run_id, key, time.time()+ttl, decision))
    if decision == "deny":
        run.status = "denied"; self.save(run)
    return {"key": key, "name": call["name"], "args": call["args"], "decision": decision}
```

**Explain the choice** Binding approval to tenant, run, tool and arguments prevents a decision from being reused for a different action. Expiry and denial remain enforceable after restart.

**ASK** Why not simply store approved=true on the run?

**Likely answer** That flag would not identify which operation and arguments were reviewed. A changed proposal could inherit an unrelated approval.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Resume from the pending boundary

**SAY** Load the snapshot, reject terminal denial or cancellation, and refresh approved keys from the current approval records. Then call the same run_agent function with initial state and the save callback. The runtime processes the stored pending call before requesting another model decision. Walk through the before-write crash first, then the after-write crash. In the second case, the ledger recognizes the action key and returns the committed result. The resumed conversation can append the missing tool observation and finish. Ask participants to explain why we do not ask the model to reconstruct whether the earlier write succeeded.

**SHOW** The current learner implementation and `incident/durable.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 05, continue in my learner project. Implement resume_run using the stored pending call and the same run_agent loop. Refresh currently valid approvals, reject denied or cancelled work and use the local effect ledger to reconcile a replay. Demonstrate why recovery consults durable application evidence rather than asking a model whether an earlier write succeeded. Preserve the original tenant and action boundaries. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 47 to 56 at lesson-05; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def resume_run(store, tenant, run_id, provider, tools):
    run = store.load(tenant, run_id)
    if run.status == "completed":
        return run
    if run.status in {"denied", "cancelled"}:
        raise PermissionError("terminal_run")
    run.context = replace(run.context, approved=store.approved_keys(tenant, run_id))
    task = next(m["content"] for m in run.messages if m["role"] == "user")
    return await run_agent(provider, tools.execute, tools.available(run.context), task,
                           initial=run, checkpoint=store.save)
```

**Explain the choice** Recovery uses durable application evidence. The model does not decide transaction history. The local exactly-once demonstration depends on the mock effect and idempotency record sharing a SQLite transaction.

**ASK** Does this guarantee exactly-once execution for every external API?

**Likely answer** No. External effects require receiver-supported idempotency, transactional messaging or reconciliation. The demo proves the local ledger's boundary.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Inject a crash after the effect

**SAY** Read the injected failure before running it. The wrapper deliberately executes the approved effect and then raises WorkerCrash before the runtime saves the observation. We reopen the database and create a new executor, then resume. Inspect the final status and count the effects table. The result must be completed with exactly one effect. Next, expire an approval and repeat. This time the run must remain waiting. Finally, deny the proposal and show that resume is rejected. Pause until a learner can place each failure on the state diagram and name the durable record used to resolve it.

**SHOW** The current learner implementation and `incident/labs/l05.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 05, continue in my learner project. Make the Session 05 check pack pass, including its crash-injection demonstration. Simulate worker loss after a committed mock effect but before the result checkpoint, reopen the database and resume. Prove that there is one effect. Also demonstrate expired and denied approvals. Separate this automated fixture test from my manually controlled demonstration, and explain why the local transaction does not guarantee exactly-once behaviour for arbitrary remote APIs. Build to the interfaces the Lesson 05 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 37 to 39 at lesson-05; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def crash_after_write(name, args, context):
    await original(name, args, context)
    raise WorkerCrash()
```

**Explain the choice** Fault injection tests the exact interval that ordinary happy-path checks miss. The crash fixture derives from BaseException so the runtime does not accidentally convert a simulated process loss into a normal recoverable error.

**ASK** What evidence distinguishes a safe retry from an unknown remote effect?

**Likely answer** A durable receiver-side result for the same idempotency key. Without it, recovery must reconcile the external state before proceeding.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 05 learner exercise in my existing project: Run the crash-after-effect demonstration, then inspect the stored snapshot and effect count. Repeat with an expired approval and a denied proposal. Change the incident arguments and verify that the earlier approval does not authorize the new action. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 05 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 5 only when the required capability is present. Run the Lesson 05 check pack, which includes tests/test_lesson05.py and the Session 05 demonstration, and the full regression suite, all unchanged and using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my GitLab repository. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "paused": "waiting_approval",
  "approval": {
    "key": "3a03de7b22629d992680bdc2797f877955bf26bcfb0b8b4db3e5c9ac4a31db4d",
    "name": "mock_remediate",
    "args": {
      "incident_id": "INC-001",
      "action": "rollback"
    },
    "decision": "approve"
  },
  "resumed": "completed",
  "effects_after_crash_and_resume": 1
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- The initial remediation run waits for approval and has no write effect.
- An approved action survives a simulated worker crash and resumes.
- Crash-after-write recovery leaves exactly one mock effect.
- An expired approval does not execute the action.
- Denied and cancelled runs cannot be resumed as approved work.

The independently unpacked lesson-05 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 05 check pack from the course kit. Recorded test result: 17 passed in 1.24s. Learners commit and push their checkpoint to their GitLab repository; lesson-05 (ac763f6) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 05 check pack. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/durable.py`
- `incident/labs/l05.py`
- `tests/test_lesson05.py`

> **PROMPT** Review my completed Lesson 05 work against the Lesson 05 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out where my design makes a different choice from the one the lesson presents, and what that choice costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### Resume still waits after approval

> **PROMPT** I am working on Lesson 05. The symptom is: Resume still waits after approval. Diagnostic focus: Check expiry, tenant, run ID and the action key against the pending arguments. Recovery guidance: Review the current proposal and issue a fresh, exact decision if appropriate. Do not copy an old approval flag. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A restart loses the run

> **PROMPT** I am working on Lesson 05. The symptom is: A restart loses the run. Diagnostic focus: The store may have used :memory: or a temporary directory that was removed. Recovery guidance: Use the same persistent database path for both processes. Temporary demo directories are intentionally cleaned up after the assertion. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Two effects appear

> **PROMPT** I am working on Lesson 05. The symptom is: Two effects appear. Diagnostic focus: The effect and idempotency record may no longer share a transaction, or the action key changed. Recovery guidance: Restore the transaction boundary and canonical key, then rerun the crash test. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A remote effect cannot be reconciled

> **PROMPT** I am working on Lesson 05. The symptom is: A remote effect cannot be reconciled. Diagnostic focus: The external receiver does not provide durable idempotency evidence. Recovery guidance: Stop automatic replay and implement explicit reconciliation. Do not infer success from the model's narrative. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Add a crash before the write and compare its stored state with the after-write case.
- Write a short recovery runbook describing which operations can be retried automatically and which require reconciliation.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

The SQLite mock-effect ledger proves its local transaction boundary. It does not guarantee exactly-once effects for arbitrary external APIs. The A2A specialist task store is in memory. The restricted Compose sandbox uses temporary writable state; persistent deployment storage requires separate configuration and validation.

## Session close

**SAY** Your platform can now pause and recover with explicit action ownership. Have your coding agent save the checkpoint with its failure tests. In Session 08 these approvals get a console Approvals view that only an operator can act on, and in Session 10 that operator can authenticate with a signed, short-lived token. In the next session we apply the same runtime and authority boundaries to delegated child agents.

## References and further study

- [Checkpoint persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Interrupts and human approval](https://docs.langchain.com/oss/python/langgraph/interrupts)
