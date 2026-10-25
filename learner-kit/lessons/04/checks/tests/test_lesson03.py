import pytest
from agent_runtime.context import EvidenceStore, retrieve, select_context


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

