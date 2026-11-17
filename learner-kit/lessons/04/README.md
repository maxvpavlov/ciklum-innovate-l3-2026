# Lesson 04 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

- `given/MockProvider.py`: replace `MockProvider` in `agent_runtime/providers.py` with this version.
- `given/CASES.py`: add `CASES` to `agent_runtime/evaluate.py` in the build step that creates that file.
- `given/agentic_platform/console/app.js`: copy to `agentic_platform/console/app.js`.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 4` in `course/__init__.py`. The full
suite should then report **19 passed**, and `python -m course.lab 4`
prints the lesson's demo result.

## Completion criteria

The Verify prompt checks your work against these, as well as the passing count:

- Two held-out cases with two trials produce four result rows.
- A plausible but wrong cause is rejected.
- Missing or ambiguous evidence is not reported as a supported diagnosis.
- Reports identify the dataset and retain per-trial results.
- Judge calibration identifies the mismatching labels.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `Run`, `run_agent`
- `agent_runtime.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `course`: `LESSON`

The checks also rely on these, beyond the imported names:

- `CASES` (given): the five cases, pasted into `agent_runtime/evaluate.py` unchanged;
- `evaluate(trials=..., split="all")`, also called with no split, returning a report with
  `dataset_sha256`, `success_rate` and `rows`, one per trial, each with its `split`;
- `grade(run, case)`, returning a dict whose `outcome`, `evidence` and `tool_policy` are booleans;
- `judge_agreement(human_labels, judge_labels)`, returning `agreement` and `review_indices`.

Optional and not checked: `model_judge(provider, case, run)`, returning
`{"pass": true or false, "reason": ...}` and raising `invalid_judge_verdict` for any other reply.

Along the way: this lesson's test file cannot import until `agent_runtime.evaluate` provides
`evaluate`, `grade` and `judge_agreement`, so it imports only after build step 4.
