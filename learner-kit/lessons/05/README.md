# Lesson 05 check pack

This lesson has no given files: copy `checks/` only.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 5` in `course/__init__.py`. The full
suite should then report **21 passed**, and `python -m course.lab 5`
prints the lesson's demo result.

## Completion criteria

The Verify prompt checks your work against these, as well as the passing count:

- The initial remediation run waits for approval and has no write effect.
- An approved action survives a simulated worker crash and resumes.
- Crash-after-write recovery leaves exactly one mock effect.
- An expired approval does not execute the action.
- Denied and cancelled runs cannot be resumed as approved work.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `Reply`, `Run`, `run_agent`
- `agent_runtime.durable`: `RunStore`, `resume_run`
- `agent_runtime.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `course`: `LESSON`

The checks also rely on these, beyond the imported names:

- `run_agent(..., initial=..., checkpoint=...)`: tool calls are recorded in `run.pending` and
  `checkpoint(run)` is called before they are dispatched; when `execute` raises `ApprovalRequired`
  the run stops with status `waiting_approval`, keeps the call pending and is saved; and
  `initial=run` continues a stored run by dispatching its pending calls before the next model call;
- `Run.snapshot()`, a JSON-serialisable dict from which `Run(**snapshot)` rebuilds the run once
  its `context` dict is turned back into a `Context`;
- `RunStore(path)` with `save(run)` (passed as `checkpoint`), `load(tenant, run_id)` raising
  `KeyError` (`run_not_found`) for a run another tenant owns, and
  `decide(tenant, run_id, decision="approve", ttl=300)` returning the pending call's `key`, `name`,
  `args` and `decision`; it accepts only `approve` or `deny` and refuses a run that is not
  `waiting_approval` with a pending call; `deny` makes the run `denied`, and a negative `ttl` stores
  an approval that has already expired;
- `resume_run(store, tenant, run_id, provider, tools)`: a completed run is returned unchanged, a
  denied or cancelled one raises `PermissionError`, and otherwise the run continues in the same
  `run_agent` with only the approvals still valid, so an expired one leaves it `waiting_approval`;
  whether a `failed` run may resume is your choice, so explain the one you make;
- `ToolExecutor(path)` on the same database file as the store, with `tools.available(context)`
  and the `db` connection in which the demo counts rows of `effects`.

Along the way: this lesson's test file and demo cannot import until `agent_runtime.durable`
provides `RunStore` and `resume_run`, which stops the whole test run; until build step 1 adds
them (`resume_run` as a placeholder), run the earlier tests with `--ignore tests/test_lesson05.py`
(19 pass). Both new checks pass once build step 3 implements `resume_run`.
