from incident.supervisor import Supervisor


async def demo():
    supervisor = Supervisor()
    parent = await supervisor.investigate()
    assert len(supervisor.children) == 2 and parent.answer["cause"] == "connection_pool_exhaustion"
    assert all(c.context.parent_id == parent.context.run_id for c in supervisor.children)
    return {"parent": parent.context.run_id, "answer": parent.answer,
            "children": [{"role": c.context.role, "tools": c.context.allowed,
                          "tokens": c.tokens} for c in supervisor.children],
            "shared_tokens_spent": supervisor.budget.spent}

