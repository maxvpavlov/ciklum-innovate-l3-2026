# Lesson 06 Supervisor, subagents and parallel coordination

*Instructor guide for the L3 agentic platform programme*

**Outcome** A supervisor delegates bounded work to isolated log and runbook agents under typed contracts and a shared budget, runs independent work concurrently with a deadline, and coordinates correlated replies, versioned artifacts and bounded review.

Duration: 120 minutes. Starting checkpoint: lesson-05. Ending checkpoint: lesson-06 (48d171c).

Word version: [06 Supervisor subagents and parallel coordination.docx](06%20Supervisor%20subagents%20and%20parallel%20coordination.docx)

## Where this session sits in the platform

This session turns the single runtime into a small multi-agent system: a supervisor whose only tool is delegate, child runs that are ordinary run_agent calls with a narrowed Context, and one shared budget. The console's Runs view shows runs started from the platform API, not these child runs yet. In Session 08 the Runs view lists each child with a link to its parent, and in Session 11 those identifiers become the correlated trace. Session 09 routes child tool calls through the gateway, and Session 10 gives each child a delegated credential narrower than its parent's.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary, MCP transport and the first console | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | Built earlier |
| 04 | Evaluation harness and single-agent baseline | Built earlier |
| 05 | Durable runs, crash recovery and exact-action approval | Built earlier |
| 06 | Supervisor, scoped subagents and parallel coordination | **This session** |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, durable run API, registry and approval views | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 05 checkpoint and the Session 04 single-agent evaluation baseline. Review multi-agent design, context isolation and Python asyncio tasks, timeouts and cancellation. Prepare two bounded tasks for the demo, log analysis and runbook investigation, and decide before class which component owns the reviewed report artifact.

Learners need two things: their own project repository in the course GitLab group on gitlab.ciklum.net, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 06. Open my project repository in my course GitLab group on gitlab.ciklum.net, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-05 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing, and tell me the commit it was at before and after the update and which files under learner-kit/lessons/06 changed; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/06 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

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

**SAY** We now have a single agent, reliable tools, context controls, evaluation and recovery. Today we add delegation and then make it concurrent without losing those foundations. The supervisor asks one child to inspect logs and another to investigate runbooks. Each child uses the same run_agent function with a separate context and narrower capabilities. We run delegation sequentially first, so the contracts are easy to inspect, then schedule the same tasks in parallel. Ask what evidence would justify the extra agent calls, and what the platform should report when a worker is slow, a result arrives twice or a reviewer never accepts.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw the parent above two workers and label each arrow with task ID, role, objective and expected result. A subagent is not a differently worded prompt in a shared transcript: it has its own messages, scoped tools, run ID and parent ID. The offline supervisor provider produces a prescribed plan; a live model can propose calls with the same delegate schema, but the application validates them. Budget reservations stop concurrent workers each assuming they own the full allowance. Then draw a dependency graph. A task is ready when its predecessors have completed; the concurrency limit decides how many ready tasks run at once; a deadline bounds the whole operation. Replies carry correlation and artifact identity, artifacts have one writer and an expected version, and review has a round limit.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Define the delegation contract and scoped child

**SAY** The model may propose a task ID, a role and a bounded objective. It cannot invent a role or attach permissions. Read DELEGATE_SCHEMA and name the two allowed roles, then follow delegate. The contract is serialised with sorted keys: an identical contract reuses its result, while a changed objective under the same task ID is rejected as task_id_conflict. The application maps the role to a fixed tool set and refuses a child that would hold a tool its parent lacks. The child Context gets a new run ID, the parent's run ID as parent_id, the role's tools and no approvals. The parent's conversation is not copied. Ask why the objective is capped at 500 characters.

**SHOW** The current learner implementation and `agent_runtime/supervisor.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 06, continue in my learner project. Implement the bounded delegate schema, the given offline planning fixture, SupervisorProvider, and the delegate method in agent_runtime/supervisor.py. Accept only known roles, stable task IDs and bounded objectives. Map each role to a fixed tool set, refuse capabilities the parent lacks, reuse identical contracts and reject a changed objective under the same task ID. Give each child a new run ID, the parent's ID, only its role's tools and no approvals. Label offline planning separately from live model planning. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 79 to 95 at lesson-06; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
identity = args["task_id"]
contract = json.dumps(args, sort_keys=True)
if identity in self.contracts:
    if self.contracts[identity] != contract:
        return {"ok": False, "error": "task_id_conflict"}
    return self.results.get(identity, {"ok": False, "error": "duplicate_in_flight"})
capabilities = ("log_lookup",) if args["role"] == "logs" else ("runbook_search",)
if not set(capabilities) <= set(parent.allowed):
    return {"ok": False, "error": "child_privilege_escalation"}
reserved = 1800
try:
    await self.budget.reserve(reserved, depth=1)
except ValueError as exc:
    return {"ok": False, "error": str(exc)}
self.contracts[identity] = contract
child = replace(parent, run_id=uuid.uuid4().hex, parent_id=parent.run_id,
                role=args["role"], allowed=capabilities, approved=())
```

**Explain the choice** The schema bounds proposed decomposition, and the role-to-tool mapping keeps authority with the application. Children never receive the delegate tool, so they cannot spawn further agents.

**ASK** Should a worker choose its own permissions after reading its objective?

**Likely answer** No. The application maps the validated role to a fixed capability set and checks that it does not exceed the parent's authority.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Reserve shared capacity and bound each child

**SAY** Inspect SharedBudget. The lock makes reservation atomic, which matters once children run concurrently. A child must fit the depth, agent-count and token limits before it starts. delegate reserves 1,800 fixture tokens, runs the child with its own limits of that allowance and four steps, and settles in a finally block from reported usage; a child that produced no run is charged the full reservation. Lower max_agents to one: the second delegation fails with delegation_budget, and the parent reports insufficient_evidence while keeping the log evidence. Name one honest gap: the parent's own calls sit outside this pool. Session 11 reserves them from the same budget.

**SHOW** The current learner implementation and `agent_runtime/supervisor.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 06, continue in my learner project. Implement shared budget reservation and settlement with depth, agent-count and token limits. Reserve before starting a child, give it bounded limits, settle from reported usage and charge the full reservation when usage is missing. Demonstrate a plan that exceeds the agent-count allowance, preserving completed evidence and reporting the incomplete result honestly. Note that the parent's own usage is outside this pool. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 22 to 41 at lesson-06; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
@dataclass
class SharedBudget:
    remaining: int = 5000
    max_agents: int = 2
    max_depth: int = 1
    spawned: int = 0
    spent: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def reserve(self, tokens, depth):
        async with self.lock:
            if depth > self.max_depth or self.spawned >= self.max_agents or tokens > self.remaining:
                raise ValueError("delegation_budget")
            self.spawned += 1
            self.remaining -= tokens

    async def settle(self, reserved, used):
        async with self.lock:
            self.remaining = max(0, self.remaining + reserved - used)
            self.spent += used
```

**Explain the choice** Reservation before launch prevents oversubscription under concurrency, and agent count bounds total child creation, not only simultaneous activity. Settlement cannot make an inaccurate usage report exact.

**ASK** Why reserve before spawning instead of checking usage afterward?

**Likely answer** By then concurrent children may already have spent more than the allowance. Admission must happen before the work begins.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Schedule independent work with a deadline

**SAY** Open coordination.py. schedule rejects duplicate IDs, unknown dependencies and cycles before any work starts. The loop launches ready tasks up to the concurrency limit, marks dependants of a failed task as blocked, and waits for the first completion or the deadline. Unfinished tasks are recorded as cancelled with reason deadline, then cancelled and awaited so their cleanup runs. The overall status is partial unless everything completed. Next show the execute_batch hook in core.run_agent and Supervisor.batch: pending delegate calls become WorkItems, each still passes through delegate, and results return by tool-call ID. Compare sequential and parallel runs with the same injected latency; judge the direction, not exact milliseconds.

**SHOW** The current learner implementation and `agent_runtime/coordination.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 06, continue in my learner project. Implement WorkItem and schedule in agent_runtime/coordination.py. Reject duplicate IDs, unknown dependencies and cycles before launching work, respect the concurrency limit, block dependants of failed work, and at the deadline keep completed results, cancel and await the rest and report partial status. Add an optional batch hook to the runtime and a supervisor adapter that sends pending delegate calls through the scheduler without bypassing delegate's checks. Compare sequential and parallel runs with the same injected latency. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 48 to 72 at lesson-06; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
            if any(dep in results and results[dep]["status"] != "completed" for dep in deps):
                results[key] = {"status": "blocked", "error": "dependency_failed"}
                pending.remove(key)
            elif all(dep in results for dep in deps) and len(active) < concurrency:
                active[asyncio.create_task(wrapped(specs[key]))] = key
                pending.remove(key)
        remaining = expires-time.monotonic()
        if remaining <= 0:
            break
        if active:
            done, _ = await asyncio.wait(active, timeout=remaining,
                                         return_when=asyncio.FIRST_COMPLETED)
            if not done:
                break
            for task in done:
                results[active.pop(task)] = task.result()
        elif pending:
            continue
    for key in pending | set(active.values()):
        results[key] = {"status": "cancelled", "error": "deadline"}
finally:
    for task in active:
        task.cancel()
    if active:
        await asyncio.gather(*active, return_exceptions=True)
```

**Explain the choice** A generic runner keeps scheduling testable with small asynchronous fixtures. Parallelism is enabled only through the supervisor's batch adapter; the general tool executor does not become a concurrent write engine.

**ASK** Should a partial result carry the same success status as a complete result?

**Likely answer** No. The consumer needs an explicit completeness state and the outcome of each required task, keyed by task ID rather than arrival order.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Correlate replies, version artifacts and bound review

**SAY** Read Envelope and accept_reply. Correlation, task and artifact IDs must match the request, and the reply must advance the version by exactly one, so a reply for another request or a stale version cannot overwrite newer evidence. Then read bounded_review: the reviewer decides, the producer revises, and after max_rounds without acceptance the status is escalated with the artifact and review history preserved. The lab's reviewer always reports contradictory evidence, the review escalates, and the single owning component saves the report as version 1. Ask how learners would tell a genuine evidence conflict from a reviewer whose criteria keep changing. Both need explicit acceptance rules; the corrective action differs.

**SHOW** The current learner implementation and `agent_runtime/coordination.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 06, continue in my learner project. Implement typed reply correlation and bounded producer-reviewer coordination in agent_runtime/coordination.py. Require matching correlation, task and artifact identity and the next version. Give one component ownership of saving the reviewed artifact and escalate review that does not converge within its round limit, keeping the history. Make the Session 06 check pack pass, including a deadline-cancelled worker, a stale reply and a reviewer that never accepts. Build to the interfaces the Lesson 06 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 86 to 104 at lesson-06; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def accept_reply(request, reply):
    if (reply.correlation_id, reply.task_id, reply.artifact_id) != (
        request.correlation_id, request.task_id, request.artifact_id):
        raise ValueError("mismatched_reply")
    if reply.version != request.version+1:
        raise ValueError("stale_or_unexpected_artifact")
    return reply.body


async def bounded_review(artifact, producer, reviewer, max_rounds=2):
    history = []
    for number in range(max_rounds):
        decision = await reviewer(artifact)
        history.append(decision)
        if decision["accepted"]:
            return {"status": "accepted", "artifact": artifact, "rounds": number+1, "reviews": history}
        if number+1 < max_rounds:
            artifact = await producer(artifact, decision)
    return {"status": "escalated", "artifact": artifact, "rounds": max_rounds, "reviews": history}
```

**Explain the choice** Typed envelopes and artifact versions fix coordination errors that prompt changes cannot. A finite review loop turns disagreement into an escalation with evidence.

**ASK** When should a review loop stop even if the reviewer has not accepted?

**Likely answer** When its round, time or cost allowance is exhausted, or when the conflict needs a human decision. Preserve the unresolved evidence and escalate.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 06 learner exercise in my existing project: Reduce max_agents to one, request a log worker from a parent with only runbook access, and reuse a task ID with a changed objective. Then schedule two independent tasks and one dependent task, inject a slow worker and a failed predecessor, and submit a stale reply. Explain each result and compare the two-worker run with the single-agent baseline. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 06 implementation against its completion criteria. Update the checkpoint indicator in course/__init__.py to 6 only when the required capability is present. Run the full test suite, which includes the Lesson 06 check pack and every earlier lesson's tests, and then the Session 06 demonstration with python -m course.lab 6, all unchanged and using the offline provider (MODEL_PROVIDER unset or set to mock). Confirm that the passing count matches the one in the Lesson 06 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my repository on gitlab.ciklum.net; if glab is also signed in to other GitLab hosts, make sure the push goes to gitlab.ciklum.net. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "parent": "96d1e86ac800431fbe178032bcc6f40a",
  "answer": {
    "status": "complete",
    "cause": "connection_pool_exhaustion",
    "summary": "Combined bounded worker evidence",
    "evidence": [
      "log-astro-001",
      "rb-pool-v1"
    ]
  },
  "children": [
    {
      "role": "logs",
      "tools": [
        "log_lookup"
      ],
      "tokens": 55
    },
    {
      "role": "runbooks",
      "tools": [
        "runbook_search"
      ],
      "tokens": 55
    }
  ],
  "shared_tokens_spent": 110,
  "timings_ms": {
    "sequential": 86.15,
    "parallel": 44.64
  },
  "partial": {
    "status": "partial",
    "results": {
      "fast": {
        "status": "completed",
        "data": {
          "ok": true,
          "source": "fast"
        }
      },
      "slow": {
        "status": "cancelled",
        "error": "deadline"
      }
    }
  },
  "review": "escalated",
  "artifact_version": 1
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- Children have distinct run IDs, the correct parent ID, only their role's tools and no inherited approvals.
- A child cannot exceed its parent's capabilities; identical contracts are reused and changed ones rejected.
- The shared budget enforces agent-count, depth and token limits before launch.
- Concurrency never exceeds its limit and dependent work waits for successful predecessors.
- A deadline preserves completed results and cancels unfinished work; cycles are rejected.
- Mismatched or stale replies fail validation, and non-converging review escalates.

The independently unpacked lesson-06 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 06 check pack from the course kit. Recorded test result: 27 passed in 4.41s. Learners commit and push their checkpoint to their GitLab repository; lesson-06 (48d171c) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 06 check pack. Ask the agent to explain any additional file changes it needs.

- `agent_runtime/coordination.py`
- `agent_runtime/core.py`
- `agent_runtime/supervisor.py`
- `course/__init__.py`
- `course/labs/l06.py`
- `tests/test_lesson06.py`

> **PROMPT** Review my completed Lesson 06 work against the Lesson 06 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### Delegation fails before a child starts

> **PROMPT** I am working on Lesson 06. The symptom is: Delegation fails before a child starts. Diagnostic focus: Read the code: invalid_delegation, task_id_conflict, child_privilege_escalation or delegation_budget each name a different check. Recovery guidance: Use a bounded objective, a fresh task ID for new work and an allowance that fits the plan. Keep the permission check intact. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The parent declares success with one failed child

> **PROMPT** I am working on Lesson 06. The symptom is: The parent declares success with one failed child. Diagnostic focus: The aggregation may ignore failed or missing observations. Recovery guidance: Keep partial evidence but report insufficient_evidence unless every delegated outcome succeeded. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The scheduler appears to hang

> **PROMPT** I am working on Lesson 06. The symptom is: The scheduler appears to hang. Diagnostic focus: Check for a cycle, an unknown dependency or a runner that ignores cancellation. Recovery guidance: Validate the graph first and reproduce with a small asynchronous fixture. Keep the deadline and the await after cancellation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Parallel execution is not faster

> **PROMPT** I am working on Lesson 06. The symptom is: Parallel execution is not faster. Diagnostic focus: The batch hook may be disabled, the work CPU-bound, or the fixture short of independent waiting time. Recovery guidance: Confirm both runs use the same injected latency and that parallel mode uses the batch adapter. Record the result honestly; a slower multi-agent run is a valid finding. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Design a third worker on paper, with objective, inputs, tools and acceptance criteria, and decide which tasks may run in parallel with it.
- Compare two concurrency limits on the same fixtures, and add a contradictory-evidence review case with an explicit acceptance rule.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 53 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

The SQLite mock-effect ledger proves its local transaction boundary. It does not guarantee exactly-once effects for arbitrary external APIs. The A2A specialist task store is in memory. The restricted Compose sandbox uses temporary writable state; persistent deployment storage requires separate configuration and validation.

## Session close

**SAY** You have added scoped delegation and bounded concurrency while keeping the runtime's control boundaries. Keep the single-agent baseline and the contract and scheduling tests. Next session a specialist moves behind its own service boundary and we reach it over A2A.

## References and further study

- [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Context isolation and subagents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Parallel and evaluator-optimizer patterns](https://www.anthropic.com/engineering/building-effective-agents)
- [Async tasks, timeouts and cancellation](https://docs.python.org/3/library/asyncio-task.html)
