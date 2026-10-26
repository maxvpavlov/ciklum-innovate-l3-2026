# Lesson 02 check pack

## First: move to the course layout and start the platform

Before the check pack, move your Lesson 01 project out of `incident/`: the runtime
(`core.py`, `providers.py`) into `agent_runtime/`, and `__init__.py` (with your `LESSON`),
`lab.py` and `fixtures.py` into `course/`. Take `tests/test_setup.py`, `tests/test_lesson01.py`
and `course/labs/` (`__init__.py`, `l01.py`) from `checks/` rather than editing them, and
update the imports in your own modules. The suite must still report 7 passed.

Then copy everything under `given/agentic_platform/` into a top-level `agentic_platform/`
folder: that folder is the platform, and the agent runtime you build stays in
`agent_runtime/`. Start it on loopback with the offline mock provider and sign in as
`demo-astro`. The platform map shows checkpoint lesson-01, INC-001 completes with cited
evidence, and the Tools view says the tool boundary is not built yet: this lesson builds it.

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

The `agentic_platform/` files below are the platform shell you copied in the first step;
leave them unchanged.

- `given/agentic_platform/blueprint.py`: copy to `agentic_platform/blueprint.py`.
- `given/agentic_platform/console/views/tools.js`: copy to `agentic_platform/console/views/tools.js`.
- `given/agentic_platform/__init__.py`: copy to `agentic_platform/__init__.py`.
- `given/agentic_platform/api.py`: copy to `agentic_platform/api.py`.
- `given/agentic_platform/console/app.js`: copy to `agentic_platform/console/app.js`.
- `given/agentic_platform/console/console.css`: copy to `agentic_platform/console/console.css`.
- `given/agentic_platform/console/index.html`: copy to `agentic_platform/console/index.html`.
- `given/agentic_platform/console/views/index.js`: copy to `agentic_platform/console/views/index.js`.
- `given/agentic_platform/console/views/overview.js`: copy to `agentic_platform/console/views/overview.js`.
- `given/agentic_platform/console/views/runs.js`: copy to `agentic_platform/console/views/runs.js`.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 2` in `course/__init__.py`. The full
suite should then report **12 passed**, and `python -m course.lab 2`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.core`: `ApprovalRequired`, `Context`, `Limits`, `run_agent`
- `agent_runtime.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `agent_runtime.tools`: `ToolExecutor`, `action_key`
- `course`: `LESSON`

The given platform shell (`agentic_platform/api.py`) also uses `agent_runtime.tools`:

- `ToolExecutor()` with no arguments, so every parameter needs a default (an in-memory
  database and the Session 01 readers);
- `ToolExecutor.schemas`, every tool the executor knows, including `mock_remediate`; the
  Tools view lists it, and a shell test checks it.

Along the way: this lesson's test file cannot import until `agent_runtime.tools` provides
`action_key` (build step 2), the MCP test passes only after build step 4, and
`python -m course.lab 2` runs only once `LESSON = 2`. Until then the console's Overview
shows checkpoint lesson-01.
