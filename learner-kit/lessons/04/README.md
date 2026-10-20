# Lesson 04 check pack

## Given files

Copy these into your project unchanged. They are data and test doubles that
everyone shares, so results are comparable; they are not what this lesson teaches.

- `given/MockProvider.py`: replace `MockProvider` in `incident/providers.py` with this version.
- `given/CASES.py`: add `CASES` to `incident/evaluate.py` in the build step that creates that file.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 4` in `incident/__init__.py`. The full
suite should then report **15 passed**, and `python -m incident.lab 4`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your `incident` package. Read the tests to see
how each one is called and what it must return.

- `incident`: `LESSON`
- `incident.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `incident.core`: `ApprovalRequired`, `Context`, `Limits`, `Run`, `run_agent`
- `incident.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `incident.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `incident.providers`: `HTTPProvider`, `provider_from_env`
- `incident.tools`: `ToolExecutor`, `action_key`
