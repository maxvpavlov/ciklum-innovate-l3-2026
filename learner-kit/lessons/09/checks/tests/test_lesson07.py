import pytest
from agent_runtime.core import Context


async def test_real_a2a_discovery_stream_auth_and_cancel():
    from course.labs.l07 import demo
    result = await demo()
    assert result["stream_events"] >= 3


async def test_remote_adapter_rejects_wrong_tenant_before_network():
    from agent_runtime.a2a_client import RemoteSpecialist
    with pytest.raises(PermissionError, match="tenant_mismatch"):
        await RemoteSpecialist("http://127.0.0.1:1").investigate("INC-001", Context(tenant="locomotive"))

