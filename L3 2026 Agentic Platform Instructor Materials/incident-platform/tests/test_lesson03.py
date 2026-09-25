import pytest
from incident.context import EvidenceStore, retrieve, select_context


def test_retrieval_provenance_and_tenant():
    assert retrieve("connection_pool_exhaustion", "acme")[0]["source_id"] == "rb-pool-v1"
    assert all(r["tenant"] == "globex" for r in retrieve("payments", "globex"))


def test_version_conflict_and_expired_memory():
    store = EvidenceStore()
    store.save_artifact("acme", "report", {"source": "log-acme-001"})
    with pytest.raises(ValueError, match="stale_artifact"):
        store.save_artifact("acme", "report", {})
    assert store.artifact("globex", "report") is None
    store.remember("acme", "report", {"answer": "stale"}, ttl=-1)
    assert store.recall("acme", "report") is None


def test_compaction_retains_complete_rounds():
    head = [{"role": "system", "content": "rules"}, {"role": "user", "content": "task"}]
    rounds = sum(([{"role": "assistant", "tool_calls": [{"id": str(i)}]},
                   {"role": "tool", "tool_call_id": str(i), "content": "x"*100}] for i in range(10)), [])
    selected = select_context(head+rounds, 600)
    ids = {c["id"] for m in selected for c in m.get("tool_calls", [])}
    assert all(m["tool_call_id"] in ids for m in selected if m["role"] == "tool")
    assert len(selected) < len(head+rounds)

