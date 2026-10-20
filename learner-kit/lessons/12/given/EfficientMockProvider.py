# Given for Lesson 12. Paste this definition unchanged into incident/tuning.py.
# Keep or add the imports it needs in that file.

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
