# Lesson 03 check pack

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability. Never edit them to
make them pass.

When everything is built, set `LESSON = 3` in `incident/__init__.py`. The full
suite should then report **13 passed**, and `python -m incident.lab 3`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your `incident` package. Read the tests to see
how each one is called and what it must return.

- `incident`: `LESSON`
- `incident.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `incident.core`: `ApprovalRequired`, `Context`, `Limits`, `run_agent`
- `incident.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `incident.providers`: `HTTPProvider`, `provider_from_env`
- `incident.tools`: `ToolExecutor`, `action_key`
