"""Capstone experiments applied to the completed platform."""
import copy
import hashlib
import json
import time
from agent_runtime.core import Reply
from agent_runtime.providers import MockProvider


class EfficientMockProvider(MockProvider):
    """Fixture-only policy experiment: sufficient structured log evidence can finish early."""
    async def complete(self, messages, tools, max_tokens=500):
        observations = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if observations:
            item = observations[0].get("data")
            if isinstance(item, dict) and item.get("cause") not in {None, "unknown"}:
                return Reply({"role": "assistant", "content": json.dumps({"status": "complete",
                    "cause": item["cause"], "summary": "Sufficient diagnostic log evidence",
                    "evidence": [item["source_id"]]})}, 35)
        return await super().complete(messages, tools, max_tokens)


class CachedProvider:
    def __init__(self, inner, tenant, config_hash, cache=None, ttl=60):
        self.inner, self.tenant, self.config_hash = inner, tenant, config_hash
        self.cache, self.ttl, self.hits = cache if cache is not None else {}, ttl, 0

    async def complete(self, messages, tools, max_tokens=500):
        if any(t["function"]["name"] == "mock_remediate" for t in tools):
            return await self.inner.complete(messages, tools, max_tokens)
        key = hashlib.sha256(json.dumps([self.tenant, self.config_hash, messages, tools, max_tokens],
                                         sort_keys=True).encode()).hexdigest()
        cached = self.cache.get(key)
        if cached and cached[0] > time.monotonic():
            self.hits += 1
            return Reply(copy.deepcopy(cached[1].message), tokens=0, cost_usd=0)
        result = await self.inner.complete(messages, tools, max_tokens)
        self.cache[key] = (time.monotonic()+self.ttl, copy.deepcopy(result))
        return result


class RoutingProvider:
    """Start with the fast provider; escalate incomplete/error observations."""
    def __init__(self, fast, careful):
        self.fast, self.careful, self.last_route = fast, careful, None

    async def complete(self, messages, tools, max_tokens=500):
        observations = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        uncertain = any(not o.get("ok", True) or o.get("data") is None or
            (isinstance(o.get("data"), dict) and o["data"].get("cause") == "unknown") for o in observations)
        self.last_route = "careful" if uncertain else "fast"
        return await (self.careful if uncertain else self.fast).complete(messages, tools, max_tokens)

