# Lesson 06 check pack

## Given files

Copy these into your project as described. They are data and test doubles that everyone
shares, so results are comparable; they are not what this lesson teaches.

- `given/SupervisorProvider.py`: add `SupervisorProvider` to `agent_runtime/supervisor.py` in the build step that creates that file.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 6` in `course/__init__.py`. The full
suite should then report **29 passed**, and `python -m course.lab 6`
prints the lesson's demo result.

## Completion criteria

The Verify prompt checks your work against these, as well as the passing count:

- Children have distinct run IDs, the correct parent ID, only their role's tools and no inherited approvals.
- A child cannot exceed its parent's capabilities; identical contracts are reused and changed ones rejected.
- The shared budget enforces agent-count, depth and token limits before launch.
- Concurrency never exceeds its limit and dependent work waits for successful predecessors.
- A deadline preserves completed results and cancels unfinished work; cycles are rejected.
- Mismatched or stale replies fail validation, and non-converging review escalates.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `agent_runtime.coordination`: `Envelope`, `WorkItem`, `accept_reply`, `bounded_review`, `schedule`
- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `Reply`, `Run`, `run_agent`
- `agent_runtime.durable`: `RunStore`, `resume_run`
- `agent_runtime.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.supervisor`: `SharedBudget`, `Supervisor`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `course`: `LESSON`

The checks also rely on these, beyond the imported names:

- `run_agent(..., execute_batch=None)`: when given, the loop hands all pending calls to
  `execute_batch(pending, context)` at once, which returns a result per tool-call ID; without it the
  loop behaves as before;
- `Supervisor(worker_factory=MockProvider, budget=None)` with `children` (the child runs, in start
  order), `budget`, `delegate(name, args, parent)` and
  `investigate(task="Investigate INC-001 payments latency", context=None, provider=None, parallel=False)`,
  which runs the supervisor with the given `SupervisorProvider` unless a provider is passed, and uses
  the batch hook only when `parallel` is true;
- `delegate` returns the child's answer as `data` with `ok`, `child_run_id`, `task_id`, `status` and
  `error`, or `{"ok": false, "error": ...}` with `invalid_delegation`, `task_id_conflict`,
  `child_privilege_escalation` or `delegation_budget`; a child gets a new run ID, the parent's run ID
  as `parent_id`, its role name as `role`, only its role's tool (`logs`: `log_lookup`, `runbooks`:
  `runbook_search`) and no approvals, and never the `delegate` tool; each started child counts once
  in `budget.spawned`, and reusing an identical contract starts no child and does not count;
- `SharedBudget(remaining=5000, max_agents=2, max_depth=1)` with `spawned`, `spent`,
  `reserve(tokens, depth)` and `settle(reserved, used)`. Reserve enough for a child's whole run:
  the loop's token guard counts the request plus `max_output_tokens` (500) before every model call,
  so a child on the mock needs about 1,500 (it then settles to 55); a smaller reservation fails
  every child with `token_budget`;
- `WorkItem(id, payload, depends_on=())` and `schedule(items, runner, concurrency=2, deadline=5)`,
  returning `status` (`completed` or `partial`) and `results` by item ID, each with a `status` of
  `completed`, `failed` (the runner raised or returned `ok: false`), `blocked` (a predecessor did not
  complete) or `cancelled` (unfinished or not started at the deadline); a cycle raises `ValueError`
  (`dependency_cycle`) before any work starts;
- `Envelope(correlation_id, task_id, artifact_id, version, body)`; `accept_reply(request, reply)`
  returns the reply's `body` and raises `ValueError` for another request's reply or a version other
  than the next one; `bounded_review(artifact, producer, reviewer, max_rounds=2)` returns `status`
  (`accepted` or `escalated`), the final `artifact`, the `rounds` used and every review;
- `MockProvider(latency=...)`, given since Lesson 04, which the demo uses to compare sequential and
  parallel runs.

Along the way: this lesson's test file imports `Envelope`, `WorkItem`, `accept_reply`,
`bounded_review` and `schedule` from `agent_runtime.coordination`, so it cannot import until build
step 4 completes that module. Until then run the earlier tests with
`--ignore tests/test_lesson06.py` (21 pass), and prove each step with a throwaway script outside
`tests/`.
