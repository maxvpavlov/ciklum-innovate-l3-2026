import httpx
from agent_runtime.core import Context
from agent_runtime.a2a_client import RemoteSpecialist, cancel_slow_task
from course.local_service import local_service


async def demo():
    async with local_service("agent_runtime.a2a_service:app", "/.well-known/agent-card.json") as url:
        result = await RemoteSpecialist(url).investigate("INC-001 payments latency", Context())
        async with httpx.AsyncClient() as http:
            unauthorized = await http.post(url+"/a2a", json={})
        cancelled = await cancel_slow_task(url)
        assert unauthorized.status_code == 401
        assert cancelled == "TASK_STATE_CANCELED"
        assert result["answer"]["cause"] == "connection_pool_exhaustion"
        return {"protocol": "A2A 1.0 JSON-RPC", "answer": result["answer"],
                "stream_events": len(result["events"]), "unauthorized_status": 401,
                "remote_cancellation": cancelled}

