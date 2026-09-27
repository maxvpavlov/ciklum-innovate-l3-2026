import asyncio
import tempfile
from pathlib import Path
from incident.local_service import local_service
from incident.operations import Admission, CapacityError, build_trace, evaluate_platform, release_gate, trace_html
from incident.platform import Platform


async def demo():
    with tempfile.TemporaryDirectory() as directory:
        async with local_service("incident.a2a_service:app", "/.well-known/agent-card.json") as url:
            platform = Platform(str(Path(directory)/"platform.db"),
                                admission=Admission(max_pending=2, per_second=1000))
            try:
                await platform.register_remote_agent(url)
                run_id = platform.submit("acme", "analyst", "INC-001", "team", subject="user:dana")
                run = await platform.wait("acme", run_id)
                assert run.status == "completed", run.snapshot()
                trace = build_trace(platform.store, "acme", run_id)
                assert len(trace["nodes"]) == 3
                output = Path("var/trace.html"); output.parent.mkdir(exist_ok=True)
                output.write_text(trace_html(trace))
                ids, rejected = [], 0
                for _ in range(6):
                    try: ids.append(platform.submit("acme", "analyst", "INC-001"))
                    except CapacityError: rejected += 1
                await asyncio.gather(*(platform.wait("acme", key) for key in ids))
                assert rejected == 4
                baseline = await evaluate_platform(platform, "single", 1)
                spec = platform.registry.get("single", 1)["spec"]
                platform.registry.register("single", 2, {**spec, "context_chars": 4500})
                candidate = await evaluate_platform(platform, "single", 2)
                gate = release_gate(baseline, candidate)
                assert gate["approved"]
                platform.registry.activate("single", 2)
                platform.releases.record(baseline, candidate, gate, activated=True)
                active = platform.registry.get("single")["version"]
                platform.registry.activate("single", 1)
                return {"end_to_end": run.answer, "trace_nodes": len(trace["nodes"]),
                    "trace_roles": sorted(n["role"] for n in trace["nodes"]),
                    "trace_file": str(output), "total_tokens": trace["total_tokens"],
                    "overload_rejected": rejected, "release_gate": gate,
                    "activated_version": active, "rollback_version": platform.registry.get("single")["version"],
                    "recorded_releases": len(platform.releases.list())}
            finally:
                await platform.close()
