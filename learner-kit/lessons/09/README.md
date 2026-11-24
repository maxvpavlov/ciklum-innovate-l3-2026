# Lesson 09 check pack

This lesson has no given files: copy `checks/` only.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 9` in `course/__init__.py`. The full
suite should then report **41 passed**, and `python -m course.lab 9`
prints the lesson's demo result.

## Completion criteria

The Verify prompt checks your work against these, as well as the passing count:

- Two team runs and one single run complete for Astro through one shared upstream MCP session.
- Ungranted tools, writes without an operator role and oversized arguments are denied with stable reason codes before any upstream connection.
- A changed tool description quarantines the server, and later calls to it are denied.
- Every decision is audited with an argument hash, and the Gateway view is tenant-scoped.
- Workers reach tools only through the gateway, and the platform closes upstream sessions on shutdown.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.a2a_client`: `RemoteSpecialist`, `cancel_slow_task`
- `agent_runtime.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `agent_runtime.coordination`: `Envelope`, `WorkItem`, `accept_reply`, `bounded_review`, `schedule`
- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `Reply`, `Run`, `run_agent`
- `agent_runtime.durable`: `RunStore`, `resume_run`
- `agent_runtime.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.supervisor`: `SharedBudget`, `Supervisor`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `agentic_platform.api`: `create_app`
- `agentic_platform.gateway`: `GatewayPolicy`, `ToolGateway`
- `agentic_platform.platform`: `Platform`
- `course`: `LESSON`
