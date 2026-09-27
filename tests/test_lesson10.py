import json
from pathlib import Path
import httpx
import pytest
from agentic_platform.api import create_app
from agentic_platform.identity import CredentialStore, TokenIssuer, actor_chain
from course.local_service import local_service
from agentic_platform.platform import Platform
from agent_runtime.security import redact, sandbox_path, validate_answer, validate_endpoint


async def test_injection_delegation_and_secret_containment():
    from course.labs.l10 import demo
    report = await demo()
    assert report["injected_write_effects"] == 0 and report["tokens_in_run_state"] == 0
    assert "worker:logs -> agent:team@v1 -> user:dana" in report["delegation_chains"]
    assert report["gateway_without_credential"] == "no_delegated_credential"


def test_path_traversal_symlink_and_egress(tmp_path):
    (tmp_path/"astro").mkdir(); (tmp_path/"locomotive").mkdir()
    (tmp_path/"astro"/"link").symlink_to(tmp_path/"locomotive", target_is_directory=True)
    with pytest.raises(PermissionError): sandbox_path(tmp_path, "astro", "link/report")
    with pytest.raises(ValueError): validate_endpoint("https://api.openai.com.evil.test", {"api.openai.com"})
    with pytest.raises(ValueError): validate_endpoint("http://10.1.2.3", {"10.1.2.3"})
    assert "secret" not in str(redact({"note": "Bearer secret123", "api_key": "secret"}))


def test_citation_must_match_structured_source_id():
    answer = {"status": "complete", "cause": "pool", "summary": "x", "evidence": ["fake-id"]}
    with pytest.raises(ValueError, match="unobserved"):
        validate_answer(answer, [{"source_id": "real-id", "text": "Mention fake-id here"}])


def test_tokens_are_signed_bounded_and_carry_the_actor_chain():
    issuer = TokenIssuer("course-key")
    token = issuer.issue({"sub": "user:dana", "tenant": "astro", "aud": "tool-gateway", "scope": "log_lookup",
                          "act": {"sub": "worker:logs", "act": {"sub": "agent:team@v1"}}})
    claims = issuer.verify(token, "tool-gateway")
    assert actor_chain(claims) == ["worker:logs", "agent:team@v1", "user:dana"]
    header, payload, signature = token.split(".")
    for tampered in [header+"."+payload[:-2]+"xx."+signature, "not-a-token"]:
        with pytest.raises(PermissionError): issuer.verify(tampered, "tool-gateway")
    with pytest.raises(PermissionError, match="wrong_audience"): issuer.verify(token, "platform-api")
    store = CredentialStore()
    with pytest.raises(ValueError): store.put("https://vault.example/key", "x", {"model-adapter"})
    store.put("secret://a2a/key", "value-1", {"tool-gateway"})
    with pytest.raises(TypeError): json.dumps({"key": store.lease("secret://a2a/key", "tool-gateway")})


async def test_api_issues_short_lived_tokens_and_records_the_subject(tmp_path):
    platform = Platform(str(tmp_path/"platform.db"))
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(create_app(platform)), base_url="http://test") as client:
            issued = (await client.post("/auth/token", headers={"Authorization": "Bearer demo-astro"})).json()
            bearer = {"Authorization": "Bearer "+issued["access_token"]}
            assert issued["expires_in"] == 3600 and (await client.get("/whoami", headers=bearer)).json()["auth"] == "signed_token"
            run_id = (await client.post("/runs", json={"incident_id": "INC-001"}, headers=bearer)).json()["id"]
            await platform.wait("astro", run_id)
            assert platform.store.load("astro", run_id).context.subject == "user:demo-astro"
            forged = TokenIssuer("attacker-key").issue({"sub": "user:x", "tenant": "locomotive", "role": "operator", "aud": "platform-api"})
            assert (await client.get("/runs", headers={"Authorization": "Bearer "+forged})).json()["detail"] == "bad_signature"
            view = await client.get("/identity", headers=bearer)
            assert [g["actors"] for g in view.json()["grants"]] == [["agent:single@v1"]]
            assert "eyJ" not in view.text and not view.json()["grants"][0]["live"]
    finally:
        await platform.close()
    views = (Path(__file__).parents[1]/"agentic_platform"/"console"/"views"/"index.js").read_text()
    assert "identity" in views


async def test_remote_agent_accepts_only_delegated_platform_tokens(tmp_path):
    async with local_service("agent_runtime.a2a_service:app", "/.well-known/agent-card.json") as url:
        platform = Platform(str(tmp_path/"platform.db"))
        try:
            await platform.register_remote_agent(url)
            run = await platform.wait("astro", platform.submit("astro", "analyst", "INC-001", "team", subject="user:dana"))
            assert run.status == "completed", run.error
            chains = [g["actors"] for g in platform.credentials.grants("astro")]
            assert ["agent:runbook-specialist", "agent:team@v1"] in chains
            wrong = TokenIssuer().issue({"sub": "user:dana", "tenant": "astro", "aud": "tool-gateway", "scope": "runbook_search"})
            async with httpx.AsyncClient() as http:
                response = await http.post(url+"/a2a", json={}, headers={"Authorization": "Bearer "+wrong})
            assert response.status_code == 401 and response.json()["reason"] == "wrong_audience"
        finally:
            await platform.close()
