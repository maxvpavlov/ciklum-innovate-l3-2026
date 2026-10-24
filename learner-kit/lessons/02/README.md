# Lesson 02 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

- `given/incident/blueprint.py`: copy to `incident/blueprint.py`.
- `given/incident/console/views/tools.js`: copy to `incident/console/views/tools.js`.
- `given/incident/api.py`: copy to `incident/api.py`.
- `given/incident/console/app.js`: copy to `incident/console/app.js`.
- `given/incident/console/console.css`: copy to `incident/console/console.css`.
- `given/incident/console/index.html`: copy to `incident/console/index.html`.
- `given/incident/console/views/index.js`: copy to `incident/console/views/index.js`.
- `given/incident/console/views/overview.js`: copy to `incident/console/views/overview.js`.
- `given/incident/console/views/runs.js`: copy to `incident/console/views/runs.js`.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 2` in `incident/__init__.py`. The full
suite should then report **12 passed**, and `python -m incident.lab 2`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your `incident` package. Read the tests to see
how each one is called and what it must return.

- `incident`: `LESSON`
- `incident.core`: `ApprovalRequired`, `Context`, `Limits`, `run_agent`
- `incident.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `incident.providers`: `HTTPProvider`, `provider_from_env`
- `incident.tools`: `ToolExecutor`, `action_key`
