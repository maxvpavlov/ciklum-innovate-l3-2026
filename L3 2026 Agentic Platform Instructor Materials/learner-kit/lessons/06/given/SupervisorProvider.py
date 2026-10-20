# Given for Lesson 06. Paste this definition unchanged into incident/supervisor.py.
# Keep or add the imports it needs in that file.

class SupervisorProvider:
    """Offline plan fixture; a live provider can use the identical delegate schema."""
    async def complete(self, messages, tools, max_tokens=500):
        observations = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
        if not observations:
            task = messages[1]["content"]
            incident = (re.search(r"INC-\d+", task) or re.search(r"INC-\d+", "INC-001")).group()
            calls = [{"id": role, "type": "function", "function": {"name": "delegate",
                "arguments": json.dumps({"task_id": role, "role": role,
                    "objective": f"Investigate {incident} payments latency using {role} evidence"})}}
                for role in ["logs", "runbooks"]]
            return Reply({"role": "assistant", "content": None, "tool_calls": calls}, 30)
        answers = [o["data"] for o in observations if o.get("ok") and o.get("data")]
        causes = {a["cause"] for a in answers if a["cause"] != "unknown"}
        cause = next(iter(causes)) if len(causes) == 1 else "unknown"
        complete = len(answers) == len(observations) and cause != "unknown"
        return Reply({"role": "assistant", "content": json.dumps({
            "status": "complete" if complete else "insufficient_evidence", "cause": cause,
            "summary": "Combined bounded worker evidence",
            "evidence": sorted({s for a in answers for s in a["evidence"]})})}, 30)
