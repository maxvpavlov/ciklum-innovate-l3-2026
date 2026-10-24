# Lesson 11 check pack

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 11` in `incident/__init__.py`. The full
suite should then report **50 passed**, and `python -m incident.lab 11`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your `incident` package. Read the tests to see
how each one is called and what it must return.

- `incident`: `LESSON`
- `incident.a2a_client`: `RemoteSpecialist`, `cancel_slow_task`
- `incident.api`: `create_app`
- `incident.context`: `EvidenceStore`, `context_tools`, `retrieve`, `select_context`
- `incident.coordination`: `Envelope`, `WorkItem`, `accept_reply`, `bounded_review`, `schedule`
- `incident.core`: `ApprovalRequired`, `Context`, `Limits`, `Reply`, `Run`, `run_agent`
- `incident.durable`: `RunStore`, `resume_run`
- `incident.evaluate`: `evaluate`, `grade`, `judge_agreement`
- `incident.gateway`: `GatewayPolicy`, `ToolGateway`
- `incident.identity`: `CredentialStore`, `TokenIssuer`, `actor_chain`
- `incident.mcp_bridge`: `MCPReadAdapter`, `stdio_client`
- `incident.operations`: `Admission`, `CapacityError`, `build_trace`, `evaluate_platform`, `release_gate`, `trace_html`
- `incident.platform`: `Platform`
- `incident.providers`: `HTTPProvider`, `provider_from_env`
- `incident.security`: `redact`, `sandbox_path`, `validate_answer`, `validate_endpoint`
- `incident.supervisor`: `SharedBudget`, `Supervisor`
- `incident.tools`: `ToolExecutor`, `action_key`
