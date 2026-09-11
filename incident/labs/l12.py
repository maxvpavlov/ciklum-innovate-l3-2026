import json
import tempfile
from pathlib import Path
from incident.core import Context, run_agent
from incident.context import context_tools
from incident.operations import Admission, evaluate_platform, release_gate
from incident.platform import Platform
from incident.providers import MockProvider
from incident.tools import ToolExecutor
from incident.tuning import CachedProvider


async def demo():
    with tempfile.TemporaryDirectory() as directory:
        platform = Platform(str(Path(directory)/"platform.db"), admission=Admission(per_second=1000))
        baseline = await evaluate_platform(platform, "single", 1, trials=3)
        original = platform.definitions.get("single", 1)["spec"]
        platform.definitions.put("single", 2, {**original, "provider_profile": "efficient"})
        candidate = await evaluate_platform(platform, "single", 2, trials=3)
        gate = release_gate(baseline, candidate)
        assert gate["approved"] and candidate["mean_tokens"] < baseline["mean_tokens"]
        tools, ctx = ToolExecutor(read_handler=context_tools), Context()
        cached = CachedProvider(MockProvider(), "acme", "single-v1")
        cold = await run_agent(cached, tools.execute, tools.available(ctx), "INC-001", ctx)
        warm = await run_agent(cached, tools.execute, tools.available(ctx), "INC-001", ctx)
        report = {"interpretation": "Synthetic fixture policy experiment; not a live model benchmark.",
            "baseline": baseline, "candidate": candidate, "release_gate": gate,
            "token_reduction_percent": round(100*(1-candidate["mean_tokens"]/baseline["mean_tokens"]),2),
            "cache_experiment": {"cold_tokens": cold.tokens, "warm_tokens": warm.tokens, "hits": cached.hits}}
        path = Path("var/capstone-comparison.json"); path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(report, indent=2))
        return {"baseline_success": baseline["success_rate"], "candidate_success": candidate["success_rate"],
                "baseline_mean_tokens": baseline["mean_tokens"], "candidate_mean_tokens": candidate["mean_tokens"],
                "token_reduction_percent": report["token_reduction_percent"],
                "cache_experiment": report["cache_experiment"], "report_file": str(path),
                "interpretation": report["interpretation"]}

