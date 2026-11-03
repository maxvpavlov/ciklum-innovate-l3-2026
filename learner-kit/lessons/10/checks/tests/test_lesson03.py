import json
import httpx
import pytest
from agent_runtime.context import EvidenceStore, context_tools, retrieve, select_context
from agent_runtime.core import Context, run_agent
from agent_runtime.providers import HTTPProvider
from agent_runtime.tools import ToolExecutor
from course.fixtures import SCHEMAS, simple_tools


def test_retrieval_provenance_and_tenant():
    assert retrieve("connection_pool_exhaustion", "astro")[0]["source_id"] == "rb-pool-v1"
    assert all(r["tenant"] == "locomotive" for r in retrieve("payments", "locomotive"))


def test_version_conflict_and_expired_memory():
    store = EvidenceStore()
    store.save_artifact("astro", "report", {"source": "log-astro-001"})
    with pytest.raises(ValueError, match="stale_artifact"):
        store.save_artifact("astro", "report", {})
    assert store.artifact("locomotive", "report") is None
    store.remember("astro", "report", {"answer": "stale"}, ttl=-1)
    assert store.recall("astro", "report") is None


def test_compaction_retains_complete_rounds():
    head = [{"role": "system", "content": "rules"}, {"role": "user", "content": "task"}]
    rounds = sum(([{"role": "assistant", "tool_calls": [{"id": str(i)}]},
                   {"role": "tool", "tool_call_id": str(i), "content": "x"*100}] for i in range(10)), [])
    selected = select_context(head+rounds, 600)
    ids = {c["id"] for m in selected for c in m.get("tool_calls", [])}
    assert all(m["tool_call_id"] in ids for m in selected if m["role"] == "tool")
    assert len(selected) < len(head+rounds)


async def test_real_model_reply_is_hardened():
    """A fenced answer after a sentence completes, a reply with no JSON fails, and model events name the model."""
    requests = []

    def handler(request):
        requests.append(json.loads(request.content))
        if len(requests) == 1:
            message = {"role": "assistant", "content": None, "tool_calls": [{"id": "c1", "type": "function",
                       "function": {"name": "log_lookup", "arguments": json.dumps({"incident_id": "INC-001"})}}]}
        else:
            answer = {"status": "complete", "cause": "connection_pool_exhaustion",
                      "summary": "INC-001: pool exhausted", "evidence": ["log-astro-001"]}
            message = {"role": "assistant",
                       "content": "The log names the cause.\n```json\n" + json.dumps(answer) + "\n```"}
        return httpx.Response(200, json={"model": "served-model", "choices": [{"message": message}],
                                         "usage": {"prompt_tokens": 90, "completion_tokens": 10}})

    provider = HTTPProvider("openai-compatible", "test-model", "test-only", transport=httpx.MockTransport(handler),
                            reasoning_effort="low")
    tools, ctx = ToolExecutor(read_handler=context_tools), Context()
    run = await run_agent(provider, tools.execute, tools.available(ctx), "INC-001", ctx)
    assert run.status == "completed" and run.answer["evidence"] == ["log-astro-001"]
    system = requests[0]["messages"][0]["content"]
    assert "no Markdown code fence" in system and "exactly the argument names" in system
    assert requests[0]["reasoning_effort"] == "low"
    # The model reads a description of every argument it may send.
    assert all(arg.get("description") for tool in requests[0]["tools"]
               for arg in tool["function"]["parameters"]["properties"].values())
    models = [e for e in run.events if e["kind"] == "model"]
    assert [(e["model"], e["host"], e["tokens"]) for e in models] == [("served-model", "api.openai.com", 100)] * 2

    def prose(request):
        message = {"role": "assistant", "content": "The cause is unclear."}
        return httpx.Response(200, json={"choices": [{"message": message}]})
    provider = HTTPProvider("openai-compatible", "test-model", "test-only", transport=httpx.MockTransport(prose))
    run = await run_agent(provider, simple_tools, SCHEMAS, "INC-001")
    assert (run.status, run.error) == ("failed", "invalid_final_answer")


async def test_real_model_failures_are_named():
    """Rate limits, outages, rejected keys or tool calls and timeouts end the run with a code that says why."""
    def failing(outcome):
        def handler(request):
            if isinstance(outcome, Exception):
                raise outcome
            return httpx.Response(outcome, json={"error": {"message": "provider detail"}})
        return HTTPProvider("openai-compatible", "test-model", "test-only", transport=httpx.MockTransport(handler))

    for outcome, code in [(429, "provider_rate_limited"), (503, "provider_unavailable"),
                          (401, "provider_http_401"), (400, "provider_http_400"),
                          (httpx.ReadTimeout("slow"), "provider_timeout")]:
        run = await run_agent(failing(outcome), simple_tools, SCHEMAS, "INC-001")
        assert run.status == "failed" and run.error == code

    # A tool call the endpoint refuses is asked for again, at most twice, before the run names it.
    def rejecting(valid_after):
        sent = []

        def handler(request):
            sent.append(request)
            if len(sent) <= valid_after:
                return httpx.Response(400, json={"error": {"code": "tool_use_failed", "message": "provider detail"}})
            answer = {"status": "insufficient_evidence", "cause": "unknown", "summary": "none", "evidence": []}
            return httpx.Response(200, json={"choices": [{"message": {"role": "assistant",
                                                                      "content": json.dumps(answer)}}]})
        transport = httpx.MockTransport(handler)
        return HTTPProvider("openai-compatible", "test-model", "test-only", transport=transport), sent

    for valid_after, status, error, calls in [(2, "completed", None, 3),
                                              (3, "failed", "provider_tool_call_invalid", 3)]:
        provider, sent = rejecting(valid_after)
        run = await run_agent(provider, simple_tools, SCHEMAS, "INC-001")
        assert (run.status, run.error, len(sent)) == (status, error, calls)
