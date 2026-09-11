from incident.core import Context
from incident.supervisor import SharedBudget, Supervisor


async def test_child_isolation_and_budgets():
    supervisor = Supervisor(budget=SharedBudget(max_agents=1))
    parent = await supervisor.investigate()
    assert len(supervisor.children) == 1
    assert parent.answer["status"] == "insufficient_evidence"
    child = supervisor.children[0]
    assert child.context.allowed == ("log_lookup",)
    assert "delegate" not in child.context.allowed
    assert child.context.approved == ()
    assert child.messages[0]["role"] == "system"


async def test_no_child_privilege_escalation():
    result = await Supervisor().delegate("delegate", {"task_id": "x", "role": "logs",
        "objective": "Read INC-001"}, Context(allowed=("runbook_search",)))
    assert result["error"] == "child_privilege_escalation"


async def test_duplicate_contract_is_reused_but_changed_contract_denied():
    supervisor, context = Supervisor(), Context()
    args = {"task_id": "same", "role": "logs", "objective": "INC-001"}
    a = await supervisor.delegate("delegate", args, context)
    b = await supervisor.delegate("delegate", args, context)
    assert a == b and supervisor.budget.spawned == 1
    assert (await supervisor.delegate("delegate", {**args, "objective": "INC-002"}, context))["error"] == "task_id_conflict"

