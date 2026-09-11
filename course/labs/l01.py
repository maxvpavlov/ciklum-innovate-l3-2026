from agent_runtime.core import Limits, run_agent
from course.fixtures import SCHEMAS, simple_tools
from agent_runtime.providers import MockProvider, provider_from_env


async def demo():
    run = await run_agent(provider_from_env(), simple_tools, SCHEMAS, "Investigate INC-001")
    repeated = await run_agent(MockProvider(repeat=True), simple_tools, SCHEMAS, "INC-001")
    assert run.status == "completed", run.error
    assert repeated.error == "repeated_action"
    return {"capability": "bounded ReAct loop", "answer": run.answer,
            "model_steps": run.steps, "repeated_action": repeated.error}

