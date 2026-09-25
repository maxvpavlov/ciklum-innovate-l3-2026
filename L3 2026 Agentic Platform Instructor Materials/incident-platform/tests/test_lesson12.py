import json
import pytest
from incident.core import Reply
from incident.tuning import CachedProvider, RoutingProvider


async def test_tuning_keeps_quality_on_same_cases():
    from incident.labs.l12 import demo
    report = await demo()
    assert report["baseline_success"] == report["candidate_success"] == 1
    assert report["candidate_mean_tokens"] < report["baseline_mean_tokens"]


async def test_cache_separates_tenants_versions_and_expiry():
    class Counting:
        calls = 0
        async def complete(self, *args):
            self.calls += 1
            return Reply({"role": "assistant", "content": "{}"}, 10)
    source, cache = Counting(), {}
    one = CachedProvider(source, "acme", "v1", cache)
    await one.complete([], []); assert (await one.complete([], [])).tokens == 0
    await CachedProvider(source, "globex", "v1", cache).complete([], [])
    await CachedProvider(source, "acme", "v2", cache).complete([], [])
    expired = CachedProvider(source, "acme", "expired", cache, ttl=-1)
    await expired.complete([], []); await expired.complete([], [])
    assert source.calls == 5


async def test_routing_escalates_uncertainty():
    class Provider:
        async def complete(self, *args): return Reply({"role": "assistant", "content": "{}"})
    router = RoutingProvider(Provider(), Provider())
    await router.complete([], []); assert router.last_route == "fast"
    await router.complete([{"role": "tool", "content": json.dumps({"ok": False, "error": "not_found"})}], [])
    assert router.last_route == "careful"

