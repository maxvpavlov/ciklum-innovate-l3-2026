# Lesson 03 Context, retrieval and memory

*Instructor guide for the L3 agentic platform programme*

**Outcome** Tenant-scoped retrieval, bounded conversation context, expiring memory and versioned evidence artifacts extend the same platform.

Duration: 90 minutes. Starting checkpoint: lesson-02. Ending checkpoint: lesson-03 (60fbebf).

Word version: [03 Context retrieval and memory.docx](03%20Context%20retrieval%20and%20memory.docx)

## Where this session sits in the platform

This session builds the platform's evidence layer: tenant-scoped retrieval, bounded context selection, expiring memory and versioned artifacts. From Session 08 the platform saves each run's answer as a versioned artifact in this store, and the console's Runs view shows that answer with its cited source IDs beside the run's event timeline. Memory stays a tenant-scoped convenience with a retention policy; the console does not display it.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary, MCP transport and the first console | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | **This session** |
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

Bring your Session 02 checkpoint. Refresh retrieval and embeddings from 2025. Review context engineering and the distinction between session state and long-term memory stores.

Learners need two things: their own project repository in the course GitLab group on gitlab.ciklum.net, and the [learner kit](https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit) in the public course repository, which holds the starter project and, for each lesson, the given files and the check pack. Learners build their own implementation; the reference checkpoints in the same repository are the instructor's answer key.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my learner project for Lesson 03. Open my project repository in my course GitLab group on gitlab.ciklum.net, cloning it into ~/agentic-course/my-platform if it is not there, and confirm it holds my completed lesson-02 work with all its checks passing. Update my read-only copy of the course repository in ~/agentic-course/course, cloning it from https://github.com/maxvpavlov/ciklum-innovate-l3-2026 if it is missing; its learner-kit folder is the course kit. Use the pinned Python 3.12 environment and the offline mock provider. Do not add this lesson's work yet. Report the project location, its current checkpoint, the test results and any missing prerequisites. Do not ask me to run terminal commands.

Next, have the coding agent read this lesson's check pack and add it to the project before any code is written.

> **PROMPT** Read learner-kit/lessons/03 in the course repository: its README, the given files and the check pack. Copy the whole given files and the check pack into my project exactly as the README says, without changing them, and commit that; a given definition that must be pasted into a module is added in the build step that creates or changes that module. Then run the tests and report what fails and why: at first this lesson's test file may fail to import, because the modules it needs do not exist yet. List the interfaces my code must provide, with the exact names, signatures, fields and error codes the tests use, and the capability they verify. Explain the implementation sequence before we begin. Do not write the implementation yet, and do not look for or use a finished solution.

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

**SAY** A larger context window does not decide which information is relevant, current or authorized. We now have a working agent and reliable tools; today we control the evidence they exchange. Use the payments incident to distinguish a transient tool observation, a reusable runbook, the current task state and a saved investigation artifact. Each has a different lifetime. Our goal is to retrieve the right tenant's sources, retain enough complete conversation rounds for valid tool use, and detect stale writes when artifacts are revised.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Draw four stores: the current message history, runbook source records, persistent memory and versioned artifacts. Keep permissions in execution context outside these stores. The retrieval example uses transparent lexical matching so participants can inspect why a source was selected. It is not an embeddings implementation. The design leaves a clear tool boundary where a vector or hybrid retriever can later be substituted. Explain that compaction must preserve complete assistant/tool rounds. Dropping the assistant request but keeping its tool result can invalidate the next model call. Memory is a convenience with a retention policy, not permanent truth. A retained summary should carry provenance and be rechecked when it conflicts with current evidence.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Retrieve within the tenant boundary

**SAY** Read the tenant filter before discussing ranking quality. We filter the source population by the authenticated tenant and only then rank the remaining runbooks. The score is the overlap between query words and source text, with a deterministic source-ID tie break. Show the same payments query for Astro and Locomotive. The results must differ because the permitted data differs. Keep source IDs and versions in the returned records. A downstream explanation can then cite the exact evidence it used. Ask a learner to replace the query and predict the leading source before running it.

**SHOW** The current learner implementation and `incident/context.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 03, continue in my learner project. Implement tenant-scoped runbook retrieval and context_tools in incident/context.py. Filter authorized sources before ranking and retain source IDs and versions. Use transparent lexical ranking for this lesson so I can inspect why a record was selected. Compare the same payments query for Astro and Locomotive. Keep the tool contract compatible with the existing executor and explain the returned evidence. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 9 to 13 at lesson-03; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def retrieve(query, tenant, limit=2):
    words = set(re.findall(r"[a-z]+", query.lower().replace("_", " ")))
    ranked = [(len(words & set(r["text"].split())), r) for r in RUNBOOKS if r["tenant"] == tenant]
    return [r for score, r in sorted(ranked, key=lambda x: (-x[0], x[1]["source_id"]))
            if score > 0][:limit]
```

**Explain the choice** A simple visible ranking function keeps the lesson focused on evidence boundaries and evaluation. Swapping retrieval algorithms later should preserve tenant filtering, provenance and the return contract.

**ASK** Should tenant filtering happen after a global top-k search?

**Likely answer** That can return too few authorized results and risks exposing metadata. Apply the access boundary to the searched population or enforce an equivalent secure retrieval design.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 2 Select complete conversation rounds

**SAY** Start with the system instruction and original task, then group the remaining messages into complete rounds. The selector works backward from the newest round while staying within its character budget. This preserves request/result relationships. Show the test that constructs ten rounds and verifies that every retained tool result has a matching call identifier. We are selecting context for the next model request, not deleting the full run history. That full history remains available for persistence and diagnosis. Ask participants what happens if the original task alone exceeds the budget: the selector rejects it rather than silently truncating the instruction or producing malformed state.

**SHOW** The current learner implementation and `incident/context.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 03, continue in my learner project. Add select_context and connect it to the runtime as selection for the next model request. Preserve the instruction and original task, retain complete assistant/tool rounds within the configured allowance, and keep the full run history separately. Reject a task that cannot fit. Demonstrate a reduced conversation with no orphaned tool-call IDs and explain the evidence that was omitted. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 22 to 40 at lesson-03; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def select_context(messages, max_chars=6000):
    """Keep instruction/task and newest COMPLETE tool rounds; never orphan tool IDs."""
    head, rounds, current = messages[:2], [], []
    for message in messages[2:]:
        if message["role"] == "assistant" and current:
            rounds.append(current)
            current = []
        current.append(message)
    if current:
        rounds.append(current)
    retained = []
    for group in reversed(rounds):
        candidate = head + group + retained
        if len(json.dumps(candidate)) > max_chars:
            break
        retained = group + retained
    if len(json.dumps(head)) > max_chars:
        raise ValueError("task_exceeds_context_budget")
    return head + retained
```

**Explain the choice** Keeping the full history separate from the selected model input supports both traceability and bounded prompts. A character budget is an approximation, so live-provider token usage still needs measurement.

**ASK** Is a shorter prompt always a better prompt?

**Likely answer** No. It may discard necessary evidence. Compare task outcomes and context size on the same cases before adopting a compaction policy.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 3 Version artifacts explicitly

**SAY** An investigation report is an artifact with an identity and version. Read the optimistic version check: a writer states which version it expects to replace, and the transaction rejects a stale expectation. Create version one, then attempt another write that still expects version zero. The failure is useful because silently overwriting newer evidence would hide a coordination problem. Later, the supervisor will give one component ownership of shared artifact writes. For now, make sure each learner can read the current version and explain how to retry a legitimate update after inspecting the newer artifact.

**SHOW** The current learner implementation and `incident/context.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 03, continue in my learner project. Implement EvidenceStore's versioned artifact operations. Scope identities by tenant, require the writer's expected version and reject stale updates in a transaction. Demonstrate version one, a conflicting update and a cross-tenant lookup. Preserve newer evidence rather than automatically overwriting it after a conflict. Show how a caller should inspect and reconcile the current artifact before retrying. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 49 to 62 at lesson-03; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def save_artifact(self, tenant, artifact_id, body, expected_version=0):
    self.db.execute("BEGIN IMMEDIATE")
    try:
        version = self.db.execute("SELECT COALESCE(MAX(version),0) FROM artifacts WHERE tenant=? AND id=?",
                                  (tenant, artifact_id)).fetchone()[0]
        if version != expected_version:
            raise ValueError("stale_artifact_version")
        self.db.execute("INSERT INTO artifacts VALUES (?,?,?,?)",
                        (tenant, artifact_id, version+1, json.dumps(body)))
        self.db.execute("COMMIT")
        return version+1
    except BaseException:
        self.db.execute("ROLLBACK")
        raise
```

**Explain the choice** The version is a concurrency contract. It detects conflicts instead of pretending that the last write is necessarily the correct one. Tenant and artifact ID form the lookup boundary.

**ASK** Should a failed version check automatically retry with the latest version?

**Likely answer** Not without examining the new content. That would turn conflict detection into an unconditional overwrite.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

### 4 Apply memory retention and verify provenance

**SAY** Store a small memory record with an expiry, then read it from the correct and wrong tenants. An expired value returns no result. Explain why a memory store and an artifact store are different: an artifact is a versioned output that we may audit; a memory entry is selected context that can become stale. Run the completed investigation, save its answer as an artifact and inspect the cited source IDs. End by comparing the full-history and selected-context paths. Keep the outcome test alongside any reduction in context size so that optimization does not quietly remove necessary information.

**SHOW** The current learner implementation and `incident/context.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 03, continue in my learner project. Add expiring tenant-scoped memory and make the Session 03 check pack pass. Compare memory with versioned artifacts and the current task history. Demonstrate expiration, provenance and access boundaries, then compare the investigation with full history and bounded context. Report the outcome as well as context size; do not call a smaller prompt an improvement if required evidence is lost. Build to the interfaces the Lesson 03 check pack uses, and do not edit the check pack or the given files. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 69 to 71 at lesson-03; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def remember(self, tenant, key, body, ttl=3600):
    self.db.execute("INSERT OR REPLACE INTO memories VALUES (?,?,?,?)",
                    (tenant, key, json.dumps(body), time.time()+ttl))
```

**Explain the choice** Retention and provenance make memory behaviour explicit. The example implements expiration on read; production cleanup, encryption and storage policy require additional operational decisions.

**ASK** What should the agent do when memory conflicts with current logs?

**Likely answer** Preserve the conflict as evidence, prefer appropriately verified current sources, and avoid treating memory as an instruction or authorization.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference excerpt before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 03 learner exercise in my existing project: Run the same retrieval for Astro and Locomotive, inspect source IDs, and attempt a stale artifact write. Build a long synthetic conversation and reduce max_chars while checking valid tool-call pairs. Compare the investigation outcome before and after context selection. First state the expected outcomes, then run the experiment in a throwaway script outside tests/, or from a clean Git state you can restore. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 03 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 3 only when the required capability is present. Run the full test suite, which includes the Lesson 03 check pack and every earlier lesson's tests, and then the Session 03 demonstration with python -m incident.lab 3, all unchanged and using the offline provider (MODEL_PROVIDER unset or set to mock). Confirm that the passing count matches the one in the Lesson 03 check pack README. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result, then commit my work and push it to my repository on gitlab.ciklum.net; if glab is also signed in to other GitLab hosts, make sure the push goes to gitlab.ciklum.net. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "answer": {
    "status": "complete",
    "cause": "connection_pool_exhaustion",
    "summary": "INC-001: connection_pool_exhaustion",
    "evidence": [
      "log-astro-001",
      "rb-pool-v1"
    ]
  },
  "artifact_version": 1,
  "expired_memory": null,
  "cross_tenant_artifact": null
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- Retrieval returns only the selected tenant's source records.
- Compaction retains matching assistant/tool pairs.
- Expired memory is unavailable, including after a database reopen.
- Cross-tenant artifact lookup returns no artifact.
- A stale artifact update fails rather than overwriting the current version.

The independently unpacked lesson-03 checkpoint passed its full test suite and this lesson demo, and so does the Lesson 03 check pack from the course kit. Recorded test result: 15 passed in 3.60s. Learners commit and push their checkpoint to their GitLab repository; lesson-03 (60fbebf) remains the instructor's answer key.

### Files changed in this checkpoint

In the reference, this checkpoint changed the files below. Learners write the implementation files themselves; the lab, the tests and any given files arrive in the Lesson 03 check pack. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/context.py`
- `incident/core.py`
- `incident/labs/l03.py`
- `tests/test_lesson03.py`

> **PROMPT** Review my completed Lesson 03 work against the Lesson 03 check pack and completion criteria. Show the files I changed and the interfaces I provide, and explain how each completion criterion is met with code or test evidence. Point out the design choices I made that the check pack does not force, and what each one costs or gains. Preserve deliberate improvements and earlier capabilities.

## Demo troubleshooting

### No runbook matches

> **PROMPT** I am working on Lesson 03. The symptom is: No runbook matches. Diagnostic focus: Inspect the tokenized query and the authorized source population. Recovery guidance: Use a diagnostic term from the fixture, then expand evaluation cases before changing ranking. Do not remove the tenant filter to obtain a result. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### A provider rejects conversation history

> **PROMPT** I am working on Lesson 03. The symptom is: A provider rejects conversation history. Diagnostic focus: Check that retained tool messages have their matching assistant calls. Recovery guidance: Run the complete-round test and restore the grouping logic before tuning the budget. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### An artifact update reports stale_artifact_version

> **PROMPT** I am working on Lesson 03. The symptom is: An artifact update reports stale_artifact_version. Diagnostic focus: Another write has advanced the artifact version. Recovery guidance: Read the latest artifact, reconcile the content and submit the correct expected version. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Memory seems to disappear

> **PROMPT** I am working on Lesson 03. The symptom is: Memory seems to disappear. Diagnostic focus: Check TTL and tenant identity. Recovery guidance: Use a non-expired test value in the same tenant. Treat expiry as intended retention behaviour rather than bypassing it. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Substitute a different ranking function behind context_tools and compare supported outcomes, not just retrieval scores.
- Add a conflicting-memory case and document which source should take precedence and why.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 53 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

## Session close

**SAY** Your platform now manages evidence as a first-class part of execution. Keep the source IDs, version checks and tenant boundaries when adding more sophisticated retrieval. From Session 08 the platform saves every run's answer in this artifact store, and the console shows it per run with its cited sources. Next we turn these cases into a repeatable evaluation harness.

## References and further study

- [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Persistence and memory stores](https://docs.langchain.com/oss/python/langgraph/persistence)
