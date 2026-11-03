# Lesson 03 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

- `given/course/fixtures.py`: copy to `course/fixtures.py`.
- `given/agentic_platform/console/views/runs.js`: copy to `agentic_platform/console/views/runs.js`.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 3` in `course/__init__.py`. The full
suite should then report **17 passed**, and `python -m course.lab 3`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `run_agent`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `course`: `LESSON`

The checks also call these, beyond the imported names:

- `run_agent(..., select_messages=...)`: the selection the next model request gets, while
  the run keeps its full history; `run_agent` calls it with the messages alone, so
  `select_context(messages, max_chars=6000)` needs a default allowance, and a system prompt
  and task that cannot fit raise `ValueError`;
- `Reply.model` and `Reply.host` (default `mock` and `offline`), recorded with `elapsed_ms` in
  every model event; a request that fails still records a model event with its `error` code;
- `HTTPProvider(kind, model, key, ..., transport=..., reasoning_effort=...)` and its failure codes
  `provider_rate_limited`, `provider_unavailable`, `provider_http_<status>`, `provider_timeout`
  and `provider_tool_call_invalid`, plus `invalid_final_answer` for a reply with no JSON object.

Along the way: this lesson's test file cannot import until `agent_runtime.context` provides
every name above (build step 3), and its two real-model tests pass only after the hardening
prompt.
