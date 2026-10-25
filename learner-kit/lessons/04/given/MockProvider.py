# Given for Lesson 04. Paste this definition unchanged into agent_runtime/providers.py, replacing the earlier version.
# Keep or add the imports it needs in that file.

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
