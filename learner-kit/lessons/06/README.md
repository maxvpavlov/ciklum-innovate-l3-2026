# Lesson 06 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

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
