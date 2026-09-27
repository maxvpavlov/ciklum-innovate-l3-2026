"""A deterministic teaching provider and real configurable HTTP adapters."""
import json
import os
import re
import httpx
from incident.core import Reply


class MockProvider:
    """Deterministic tool policy, not a simulated claim of LLM intelligence."""
    def __init__(self, repeat=False, latency=0):
        self.repeat, self.latency = repeat, latency

    async def complete(self, messages, tools, max_tokens=500):
        import asyncio
        await asyncio.sleep(self.latency)
        names = [t["function"]["name"] for t in tools]
        observations = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        user = next(m["content"] for m in messages if m["role"] == "user")
        incident = (re.search(r"INC-\d+", user) or re.search(r"INC-\d+", "INC-001")).group()
        if (not observations or self.repeat) and "log_lookup" in names:
            name, args = "log_lookup", {"incident_id": incident}
        elif len(observations) < (2 if "log_lookup" in names else 1) and "runbook_search" in names:
            data = observations[0].get("data") if observations else None
            query = data.get("cause", "payments") if isinstance(data, dict) else "payments"
            name, args = "runbook_search", {"query": query}
        else:
            evidence, causes = [], []
            for obs in observations:
                data = obs.get("data")
                for item in data if isinstance(data, list) else [data]:
                    if isinstance(item, dict) and item.get("source_id"):
                        evidence.append(item["source_id"])
                        causes.append(item.get("cause", "unknown"))
            cause = next((c for c in causes if c != "unknown"), "unknown")
            # A generic runbook is not proof that an incident has that cause.
            if "log_lookup" in names:
                first = observations[0].get("data") if observations else None
                if not isinstance(first, dict) or first.get("cause") == "unknown":
                    cause = "unknown"
            answer = {"status": "complete" if cause != "unknown" else "insufficient_evidence",
                      "cause": cause, "summary": f"{incident}: {cause}", "evidence": evidence}
            return Reply({"role": "assistant", "content": json.dumps(answer)}, 35)
        call = {"id": f"call-{len(observations)}", "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)}}
        return Reply({"role": "assistant", "content": None, "tool_calls": [call]}, 20)


class HTTPProvider:
    """OpenAI-compatible chat or Anthropic Messages; never log credentials."""
    def __init__(self, kind, model, key, base_url=None, transport=None,
                 input_rate=0.0, output_rate=0.0):
        self.kind, self.model, self.key = kind, model, key
        self.base_url = (base_url or ("https://api.anthropic.com/v1" if kind == "anthropic"
                                     else "https://api.openai.com/v1")).rstrip("/")
        self.transport = transport
        self.input_rate, self.output_rate = input_rate, output_rate
        from incident.security import validate_endpoint
        hosts = set(os.getenv("MODEL_ALLOWED_HOSTS", "api.openai.com,api.anthropic.com").split(","))
        validate_endpoint(self.base_url, hosts, allow_loopback=True)

    async def complete(self, messages, tools, max_tokens=500):
        headers = {"Authorization": f"Bearer {self.key}"}
        body = {"model": self.model, "messages": messages, "tools": tools,
                "max_completion_tokens": max_tokens}
        path = "/chat/completions"
        if self.kind == "anthropic":
            headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
            converted = []
            for m in messages:
                if m["role"] == "system":
                    continue
                if m["role"] == "tool":
                    converted.append({"role": "user", "content": [{"type": "tool_result",
                        "tool_use_id": m["tool_call_id"], "content": m["content"]}]})
                elif m.get("tool_calls"):
                    converted.append({"role": "assistant", "content": [{"type": "tool_use",
                        "id": c["id"], "name": c["function"]["name"],
                        "input": json.loads(c["function"]["arguments"])} for c in m["tool_calls"]]})
                else:
                    converted.append({"role": m["role"], "content": m["content"]})
            body = {"model": self.model, "system": messages[0]["content"],
                    "messages": converted, "max_tokens": max_tokens,
                    "tools": [{"name": t["function"]["name"],
                               "description": t["function"]["description"],
                               "input_schema": t["function"]["parameters"]} for t in tools]}
            path = "/messages"
        async with httpx.AsyncClient(transport=self.transport, timeout=15,
                                     follow_redirects=False) as client:
            try:
                response = await client.post(self.base_url+path, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                # Avoid copying response bodies or header material into logs.
                raise RuntimeError(f"provider_{type(exc).__name__}") from None
        usage = data.get("usage", {})
        if self.kind == "anthropic":
            calls = [{"id": c["id"], "type": "function", "function": {
                     "name": c["name"], "arguments": json.dumps(c["input"])}}
                     for c in data["content"] if c["type"] == "tool_use"]
            message = {"role": "assistant", "content": "".join(
                c["text"] for c in data["content"] if c["type"] == "text")}
            if calls:
                message["tool_calls"] = calls
            ins, outs = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        else:
            raw = data["choices"][0]["message"]
            message = {k: v for k, v in raw.items() if k in {"role", "content", "tool_calls"}}
            ins, outs = usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        return Reply(message, ins+outs, (ins*self.input_rate+outs*self.output_rate)/1_000_000)


def provider_from_env(credentials=None):
    kind = os.getenv("MODEL_PROVIDER", "mock")
    if kind == "mock":
        return MockProvider()
    if kind not in {"openai", "openai-compatible", "anthropic"}:
        raise ValueError("Unsupported MODEL_PROVIDER")
    model = os.getenv("MODEL_NAME")
    if credentials is not None:
        # The platform releases the key to the adapter by reference; runs never hold it.
        key = credentials.lease("secret://model/api-key", "model-adapter").reveal()
    else:
        key = os.getenv("MODEL_API_KEY")
    if not key or not model:
        raise ValueError("Live mode requires MODEL_API_KEY and MODEL_NAME")
    return HTTPProvider(kind, model, key, os.getenv("MODEL_BASE_URL"),
                        input_rate=float(os.getenv("MODEL_INPUT_USD_PER_MILLION", "0")),
                        output_rate=float(os.getenv("MODEL_OUTPUT_USD_PER_MILLION", "0")))
