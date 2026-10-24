# Lesson 07 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

- `given/incident/local_service.py`: copy to `incident/local_service.py`.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 7` in `incident/__init__.py`. The full
suite should then report **29 passed**, and `python -m incident.lab 7`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your `incident` package. Read the tests to see
how each one is called and what it must return.

- `incident`: `LESSON`
- `incident.a2a_client`: `RemoteSpecialist`, `cancel_slow_task`
- `incident.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `incident.coordination`: `Envelope`, `WorkItem`, `accept_reply`, `bounded_review`, `schedule`
- `incident.core`: `ApprovalRequired`, `Context`, `Limits`, `Reply`, `Run`, `run_agent`
- `incident.durable`: `RunStore`, `resume_run`
- `incident.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `incident.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `incident.providers`: `HTTPProvider`, `provider_from_env`
- `incident.supervisor`: `SharedBudget`, `Supervisor`
- `incident.tools`: `ToolExecutor`, `action_key`
