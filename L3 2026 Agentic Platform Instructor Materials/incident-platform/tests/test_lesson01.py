import json
import httpx
import pytest
from incident.core import Limits, run_agent
from incident.fixtures import SCHEMAS, simple_tools
from incident.providers import HTTPProvider, MockProvider


async def test_loop_uses_evidence_and_stops():
    run = await run_agent(MockProvider(), simple_tools, SCHEMAS, "INC-001")
    assert run.status == "completed"
    assert run.answer["cause"] == "connection_pool_exhaustion"
    assert "log-acme-001" in run.answer["evidence"]
    assert run.steps == 3


@pytest.mark.parametrize("limits,expected", [
    (Limits(steps=1), "step_budget"), (Limits(tokens=1), "token_budget"),
    (Limits(seconds=0.001), "TimeoutError")])
async def test_limits(limits, expected):
    run = await run_agent(MockProvider(latency=.01), simple_tools, SCHEMAS, "INC-001", limits=limits)
    assert run.status == "failed" and run.error == expected


async def test_openai_wire_contract_without_network():
    def handler(request):
        body = json.loads(request.content)
        assert body["tools"][0]["function"]["name"] == "log_lookup"
        assert request.headers["Authorization"] == "Bearer test-only"
        return httpx.Response(200, json={"choices": [{"message": {
            "role": "assistant", "content": "{}"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}})
    provider = HTTPProvider("openai", "test-model", "test-only", transport=httpx.MockTransport(handler))
    reply = await provider.complete([{"role": "system", "content": "test"}], SCHEMAS)
    assert reply.tokens == 15


async def test_anthropic_wire_contract_without_network():
    def handler(request):
        body = json.loads(request.content)
        assert body["tools"][0]["input_schema"]["required"] == ["incident_id"]
        assert body["system"] == "test"
        return httpx.Response(200, json={"content": [{"type": "tool_use", "id": "1",
            "name": "log_lookup", "input": {"incident_id": "INC-001"}}],
            "usage": {"input_tokens": 10, "output_tokens": 4}})
    provider = HTTPProvider("anthropic", "test-model", "test-only", transport=httpx.MockTransport(handler))
    reply = await provider.complete([{"role": "system", "content": "test"},
                                    {"role": "user", "content": "INC-001"}], SCHEMAS)
    assert reply.message["tool_calls"][0]["function"]["name"] == "log_lookup"

