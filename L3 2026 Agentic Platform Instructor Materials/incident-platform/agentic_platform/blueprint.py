"""The platform map that the console renders: what this checkpoint has built so far."""
from course import LESSON

COMPONENTS = [
    (1, "runtime", "Agent runtime", "Bounded model, tool and observation loop with step, token and time limits"),
    (2, "tools", "Tool contracts, MCP and console", "Validated tools, application-owned permissions, approval gate, MCP transport, and this console"),
    (3, "context", "Context and memory", "Ranked retrieval, bounded context, versioned artifacts and expiring memory"),
    (4, "evaluation", "Evaluation harness", "Repeated trials, held-out cases and calibrated judges"),
    (5, "durability", "Durable runs and approvals", "Checkpoints, crash recovery and exact-action approval"),
    (6, "orchestration", "Supervisor and subagents", "Scoped children, shared budgets, parallel scheduling and bounded review"),
    (7, "a2a", "Remote agents over A2A", "Independent specialist with discovery, streaming, authentication and cancellation"),
    (8, "registry", "Registry and run lifecycle", "Versioned agent definitions, pinned remote agents, durable run API, registry and approval views"),
    (9, "gateway", "Tool gateway", "One policy and audit point for every tool call over shared MCP sessions"),
    (10, "identity", "Identity and credentials", "User and agent principals, delegated tokens, credential store and containment"),
    (11, "operations", "Operations and releases", "Correlated traces, admission control, evaluated releases and rollback"),
    (12, "tuning", "Tuning and capstone", "Measured before and after comparison of quality, usage and latency"),
]


def platform_map(lesson=LESSON):
    return {"checkpoint": lesson, "components": [
        {"lesson": number, "id": key, "name": name, "summary": summary,
         "status": "built" if number <= lesson else "planned"}
        for number, key, name, summary in COMPONENTS]}
