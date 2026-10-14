# Lesson 04 Build the agent evaluation harness

*Instructor guide for the L3 agentic platform programme*

**Outcome** A reproducible evaluation harness records single-agent quality, usage and latency, with held-out cases and a calibrated-judge workflow.

Duration: 90 minutes. Starting checkpoint: lesson-03. Ending checkpoint: lesson-04 (585a04a).

Word version: [04 Build the agent evaluation harness.docx](04%20Build%20the%20agent%20evaluation%20harness.docx)

## Where this session sits in the platform

This session builds the platform's measuring instrument: a dataset with a recorded identity, repeated trials, a held-out split and per-trial quality, usage and latency. In Session 11 the same harness becomes the release gate that decides whether a new agent version may be activated, and the console's Operations view lists those release decisions. The single-agent baseline recorded today is also the comparison point for the Session 12 capstone.

| Session | Platform component | Status |
|---|---|---|
| 01 | Agent runtime: bounded ReAct loop, typed run state, event log | Built earlier |
| 02 | Tool contracts, approval boundary and MCP transport | Built earlier |
| 03 | Context selection, retrieval, memory and versioned artifacts | Built earlier |
| 04 | Evaluation harness and single-agent baseline | **This session** |
| 05 | Durable runs, crash recovery and exact-action approval | Later session |
| 06 | Supervisor, scoped subagents and parallel coordination | Later session |
| 07 | Remote agents over A2A | Later session |
| 08 | Platform core: agent registry, run API and platform console | Later session |
| 09 | MCP tool gateway: policy, audit and shared upstream sessions | Later session |
| 10 | Agent identity, delegated credentials and credential store | Later session |
| 11 | Operations: traces, admission control and evaluated releases | Later session |
| 12 | Tuning, before/after evidence and the capstone presentation | Later session |

## Preparation

Bring your Session 03 checkpoint, acceptance scenarios and recorded runs. Read the evaluation reference and tool-evaluation guidance.

Give your coding agent access to the supplied incident-platform.zip or the reference repository in the [course materials folder](https://drive.google.com/drive/u/0/folders/1wos8PjyC0mTDQxrcZ89b9mG0yYV57Zr3). Ask it to preserve the embedded checkpoint history and identify the learner project separately from the reference.

Your coding agent handles preparation, implementation and execution. You set the scope, inspect its changes and explain the evidence. This development assistant is separate from the investigation agents inside the platform.

> **PROMPT** Prepare my Python learner project for Lesson 04, starting from lesson-03. Locate the supplied reference repository and my existing work; ask for their locations if needed. Preserve my changes and handle repository setup, dependency installation and environment configuration yourself. Use the pinned Python 3.12 environment and offline mock provider. Establish the starting checkpoint without adding this lesson yet. Run the baseline checks and report the workspace, checkpoint, results and any missing prerequisites. Do not ask me to run terminal commands.

Next, orient the coding agent to the reference while preserving your work.

> **PROMPT** Compare my current project with lesson-03 and prepare a read-only view of lesson-04 for this lesson. Preserve my work while arranging any isolation needed. Identify differences, relevant files and the expected capability. Explain the implementation sequence before we begin; do not replace my project with the finished reference or add later lessons.

**Instructor readiness** Have your coding agent rehearse the completed reference and prepare the current tests, fixtures and lab runner before class. Tests may fail until the capability is implemented. During class, use one bounded prompt at a time; learners inspect the change, explain the control decision and review the check evidence.

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

**SAY** Before adding more agents, we need evidence that complexity helps. Today we build the measuring instrument we will use for the rest of the programme. The current platform can investigate several incidents, including missing or ambiguous evidence. We will define success independently of the agent's preferred sequence of tool calls, run repeated trials and retain a held-out partition. The baseline becomes a reference point for parallel orchestration, provider changes, context policies and capstone tuning.

**SHOW** The coding agent’s baseline report, current learner project, synthetic incident records and lesson outcome. Ask participants to explain what already works before authorizing the next bounded change.

### Concept discussion

**SAY** Separate task outcome, evidence quality and policy compliance. A correct cause without supporting evidence is incomplete; a supported answer that used an unauthorized write is unacceptable. Our deterministic checks compare structured outcomes and inspect observable tool behaviour. A model judge can help with semantic questions, but it introduces another fallible model. Use paired human labels to measure agreement and inspect disagreements before relying on it. Walk through the five fixture cases and their development or held-out status. Explain that repeated offline trials should be stable, while repeated live trials reveal variation. Dataset identity, provider configuration, sampling choices and pricing assumptions all belong in the benchmark record.

**PAUSE** Invite one learner to trace the control flow and another to identify a failure boundary. Resolve different interpretations before opening the implementation.

### 1 Define cases before scoring runs

**SAY** Read each case as a requirement. The missing incident should not inherit the most common runbook's cause. The ambiguous case should finish with insufficient evidence. The other-tenant case should use a different source population. Mark the held-out cases before tuning, and do not repeatedly edit them to accommodate a favoured implementation. Show the dataset hash in the result. It is a practical way to detect whether two reports evaluated the same case definitions. Ask learners to propose one additional failure case and state its expected outcome before running the agent.

**SHOW** The current learner implementation and `incident/evaluate.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 04, continue in my learner project. Create the versioned evaluation cases in incident/evaluate.py. Cover supported diagnoses, missing evidence, ambiguity and another tenant, with explicit expected outcomes and development versus held-out partitions. Preserve the supplied acceptance scenarios and record dataset identity. Explain each case before running the agent. Do not change expected answers simply to make the current implementation pass. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 14 to 20 at lesson-04; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
CASES = [
    {"id": "pool", "tenant": "acme", "incident": "INC-001", "cause": "connection_pool_exhaustion", "split": "development"},
    {"id": "clock", "tenant": "acme", "incident": "INC-002", "cause": "clock_skew", "split": "development"},
    {"id": "missing", "tenant": "acme", "incident": "INC-404", "cause": "unknown", "split": "development"},
    {"id": "ambiguous", "tenant": "acme", "incident": "INC-003", "cause": "unknown", "split": "held_out"},
    {"id": "other_tenant", "tenant": "globex", "incident": "INC-001", "cause": "quota_exhaustion", "split": "held_out"},
]
```

**Explain the choice** Expected outcomes are independent of implementation details. Cases can remain stable while a valid agent changes its path or uses a different provider.

**ASK** Why not require exactly two tool calls in every successful case?

**Likely answer** Different valid strategies can reach the same supported result. Check essential policy requirements and outcome evidence rather than one incidental trajectory.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 2 Grade outcomes and policy separately

**SAY** Inspect the three checks returned by grade. The outcome check includes both cause and evidence-sufficiency status. The evidence check requires support for a known cause. The policy check rejects remediation during an investigation. Run the intentionally wrong answer test: it sounds plausible but names the wrong cause, so it fails. Explain the correction made to the offline provider in this checkpoint. A generic runbook is not proof of an incident's cause. The missing-evidence case exposed that mistaken inference, and the fixture now preserves unknown when diagnostic log evidence is absent.

**SHOW** The current learner implementation and `incident/evaluate.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 04, continue in my learner project. Implement separate outcome, evidence and tool-policy checks in grade. Demonstrate rejection of a plausible but wrong diagnosis. Check the offline provider's missing-evidence behaviour and make the smallest required correction in incident/providers.py so a generic runbook does not become proof of an incident cause. Preserve the original test expectations and show the regression evidence. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 23 to 30 at lesson-04; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def grade(run, case):
    answer = run.answer or {}
    evidence = answer.get("evidence", [])
    expected_status = "insufficient_evidence" if case["cause"] == "unknown" else "complete"
    return {"outcome": run.status == "completed" and answer.get("cause") == case["cause"]
                        and answer.get("status") == expected_status,
            "evidence": case["cause"] == "unknown" or bool(evidence),
            "tool_policy": all(e.get("name") != "mock_remediate" for e in run.events if e["kind"] == "tool")}
```

**Explain the choice** Separate checks explain failures instead of hiding them behind one score. The mock-provider correction is a regression example, not a claim that a live model was improved.

**ASK** Can one aggregate success percentage tell us whether a regression is acceptable?

**Likely answer** Not by itself. Inspect which cases failed and whether evidence, permissions or a critical scenario regressed.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 3 Record repeated measurements

**SAY** Follow the loop over cases and trials. Each run gets a fresh executor and context. We record checks, usage, steps and elapsed time, and retain the individual rows so a mean does not hide a bad case. Run development and held-out partitions separately, then run the full fixture set. The reference mock reports usage units chosen by the fixture; they are not tokenizer measurements or paid API charges. In live mode, usage comes from the provider, and cost is only available when pricing rates are configured. Ask participants to identify which numbers should be stable offline and which may vary with machine scheduling.

**SHOW** The current learner implementation and `incident/evaluate.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 04, continue in my learner project. Implement repeated evaluation with fresh execution context per trial, per-case result rows, dataset identity, selected partition, quality, usage and latency measurements. Keep live cost unavailable when pricing is missing, and clearly label offline fixture usage. Run two trials on the held-out partition and show the four underlying rows, including failures rather than only a favourable aggregate. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 40 to 62 at lesson-04; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
async def evaluate(factory=MockProvider, trials=3, split="all", judge=None):
    if trials < 1:
        raise ValueError("trials must be positive")
    rows = []
    cases = [c for c in CASES if split == "all" or c["split"] == split]
    for case in cases:
        for trial in range(trials):
            tools, ctx = ToolExecutor(read_handler=context_tools), Context(tenant=case["tenant"])
            provider = factory()
            started = time.perf_counter()
            run = await run_agent(provider, tools.execute, tools.available(ctx), case["incident"], ctx)
            checks = grade(run, case)
            rows.append({"case": case["id"], "split": case["split"], "trial": trial,
                "passed": all(checks.values()), "checks": checks, "tokens": run.tokens,
                "steps": run.steps, "elapsed_ms": (time.perf_counter()-started)*1000,
                "cost_usd": run.cost_usd if isinstance(provider, MockProvider) or
                   provider.input_rate+provider.output_rate > 0 else None,
                "judge": await judge(case, run) if judge else None})
    return {"dataset_sha256": hashlib.sha256(json.dumps(CASES, sort_keys=True).encode()).hexdigest(),
            "provider": type(factory()).__name__, "trials": trials, "split": split,
            "success_rate": sum(r["passed"] for r in rows)/len(rows),
            "mean_tokens": statistics.mean(r["tokens"] for r in rows),
            "mean_steps": statistics.mean(r["steps"] for r in rows),
```

**Explain the choice** Per-trial rows support inspection and later comparisons. A held-out partition separates tuning feedback from an additional evaluation check. Unknown pricing remains unavailable rather than being reported as a free live call.

**ASK** Why retain raw trial rows when we already have means?

**Likely answer** They expose variation, case-specific failures, outliers and accidental changes in the tested population.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

### 4 Calibrate an optional model judge

**SAY** Use a small labelled set to demonstrate agreement calculation and inspect the disagreement index. Then open model_judge. The expected outcome and agent answer are sent as data with a bounded grading request. The agent answer remains untrusted even inside an evaluation prompt. A judge response must have the expected type. Explain that deterministic checks remain useful even when a judge is present, especially for permission violations and missing source IDs. For this session, the optional live judge is not required: use the supplied labelled example and show where real human labels and a verified live adapter would enter.

**SHOW** The current learner implementation and `incident/evaluate.py`. Use the following prompt to make the bounded change, then inspect the agent’s result.

> **PROMPT** For Lesson 04, continue in my learner project. Implement paired human-versus-judge agreement checks and the optional model_judge interface. Validate judge output, treat the agent answer as untrusted grading input and expose disagreements for human review. Complete the Session 04 lab and tests using offline calibration examples. Explain what is verified locally and what would still require a calibrated live judge and authorized provider access. Use lesson-04 read-only to check compatibility. Preserve earlier behaviour, run relevant checks and show the change and observed evidence. Stop at this step.

**REVIEW** Compare the coding agent’s change with this reference excerpt. It covers source lines 33 to 37 at lesson-04; common indentation is reduced for display. Ask the agent to explain material differences in behaviour.

```python
def judge_agreement(human_labels, judge_labels):
    if not human_labels or len(human_labels) != len(judge_labels):
        raise ValueError("paired_calibration_labels_required")
    disagreements = [i for i, (a, b) in enumerate(zip(human_labels, judge_labels)) if a != b]
    return {"agreement": 1-len(disagreements)/len(human_labels), "review_indices": disagreements}
```

**Explain the choice** A judge is a measurement component that needs validation. Agreement on a tiny example illustrates the process but cannot establish reliable judge performance for a production workload.

**ASK** What should we do with judge disagreements?

**Likely answer** Review the underlying cases and rubric. Correct ambiguous labels or an inadequate judge before changing the agent merely to satisfy the judge.

**PAUSE** Have learners identify the boundary in their agent’s change and explain the expected failure behaviour. Compare it with the reference snapshot before accepting the change.

## Learner practice and checkpoints

> **PROMPT** Help me carry out the Lesson 04 learner exercise in my existing project: Add one unsupported-answer case and one tool-policy violation to a local test. Verify that the relevant check fails. Run two repeated trials on the held-out partition and locate every per-case result. Use the calibration example to explain why the flagged disagreement needs human review. First state the expected outcomes, then run the experiment in a recoverable state. Show the observed results and explain any discrepancy. Keep the original acceptance criteria and restore temporary experiments when finished.

**VERIFY** Give the coding agent the verification prompt below, then inspect its evidence and explain the result in your own words.

> **PROMPT** Verify my Lesson 04 implementation against its completion criteria. Update the checkpoint indicator in incident/__init__.py to 4 only when the required capability is present. Run tests/test_lesson04.py, the Session 04 demonstration and the existing regression suite using the offline provider. Keep the expected outcomes unchanged. Report checks actually executed, failures, relevant output and any untested integration. Explain the result and save a recoverable checkpoint of my work. Do not equate an unrun or skipped check with a pass.

**Expected behaviour** The coding agent returns actual check results and the demonstration’s structured output. Run identifiers and elapsed times vary. Compare the status and capability outcomes with the recorded reference below, and investigate differences.

```json
{
  "dataset_sha256": "90d1f50a6663c9e7ec24a2d3951b0238d92114eefc8797c5317a42c428ddbc3f",
  "provider": "MockProvider",
  "trials": 2,
  "split": "all",
  "success_rate": 1.0,
  "mean_tokens": 75,
  "mean_steps": 3,
  "mean_latency_ms": 0.8998957055155188,
  "calibration": {
    "agreement": 0.6666666666666667,
    "review_indices": [
      1
    ]
  },
  "interpretation": "Offline fixture results validate wiring and checks, not live model quality."
}
```

**PAUSE** Ask learners to explain the evidence before accepting the checkpoint. If a check fails, use the specific recovery prompt below and review the resulting correction.

## Completion criteria

- Two held-out cases with two trials produce four result rows.
- A plausible but wrong cause is rejected.
- Missing or ambiguous evidence is not reported as a supported diagnosis.
- Reports identify the dataset and retain per-trial results.
- Judge calibration identifies the mismatching labels.

The independently unpacked lesson-04 checkpoint passed its full test suite and this lesson demo. Recorded test result: 15 passed in 1.08s. Have your coding agent save a recoverable learner checkpoint and retain the comparison with lesson-04 (585a04a).

### Files changed in this checkpoint

Use this inventory to scope the coding agent’s work. It includes core files, lab scaffolding, acceptance tests and checkpoint metadata. Ask the agent to explain any additional file changes it needs.

- `incident/__init__.py`
- `incident/evaluate.py`
- `incident/labs/l04.py`
- `incident/providers.py`
- `tests/test_lesson04.py`

> **PROMPT** Compare my completed Lesson 04 work with reference lesson-04. Show the changed files, interfaces and important behavioural differences. Explain how each completion criterion is met with code or test evidence. Preserve deliberate learner improvements and earlier capabilities; do not overwrite my work merely to obtain a textually identical copy.

## Demo troubleshooting

### A comparison improves after changing the cases

> **PROMPT** I am working on Lesson 04. The symptom is: A comparison improves after changing the cases. Diagnostic focus: The dataset hash or partition differs. Recovery guidance: Restore the same dataset and compare like-for-like before attributing an improvement to the implementation. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### Live cost appears unavailable

> **PROMPT** I am working on Lesson 04. The symptom is: Live cost appears unavailable. Diagnostic focus: Input and output pricing rates are not configured. Recovery guidance: Provide explicit current rates in the environment and rerun. Keep cost unavailable until then. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### One live trial passes and another fails

> **PROMPT** I am working on Lesson 04. The symptom is: One live trial passes and another fails. Diagnostic focus: Inspect outcome variation and the individual traces. Recovery guidance: Increase representative trials and investigate the failure mode rather than selecting only a favourable run. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

### The judge disagrees with an obvious check

> **PROMPT** I am working on Lesson 04. The symptom is: The judge disagrees with an obvious check. Diagnostic focus: The rubric, human label or judge may be wrong. Recovery guidance: Review the example manually. Keep deterministic permission and schema checks authoritative for those properties. Reproduce the issue, make the smallest necessary correction and rerun affected checks. Report the cause, changed files and observed outcome. Preserve security controls and acceptance criteria.

## Practice and discussion

- Create a versioned dataset extension with a clear rationale and retain the previous baseline.
- Compare full history and bounded context using the same cases and report both outcome quality and usage.

**Discussion prompt** Which decision would change for a larger or more sensitive workload, and what additional evidence would you require before changing it? Tie the answer to the code, the task requirements and the acceptance checks.

## Verification scope

All course tags were independently unpacked and tested. The completed repository has 51 passing tests. Real local MCP stdio, the tool gateway's shared sessions and pinned definitions, A2A HTTP discovery, streaming, delegated-token authentication and cancellation were exercised. The platform console was driven in a headless Chromium browser against every checkpoint from lesson-08 onward.

Live model credentials, paid provider calls, live model judging, third-party MCP or A2A services, remote MCP OAuth, an enterprise identity provider, a managed secret vault, production cloud rollout and an external observability collector were not tested. The offline provider is a deterministic fixture, so its usage and quality results are teaching measurements. Read TESTING.md for the full scope and environment details.

## Session close

**SAY** Save the baseline report with its dataset identity and configuration. We will keep using this harness as the platform becomes more capable: in Session 11 it becomes the release gate for new agent versions, and the console's Operations view keeps the log of release decisions. Next we make a run survive interruption without duplicating its effects.

## References and further study

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Evaluating tool effectiveness](https://www.anthropic.com/engineering/writing-tools-for-agents)
