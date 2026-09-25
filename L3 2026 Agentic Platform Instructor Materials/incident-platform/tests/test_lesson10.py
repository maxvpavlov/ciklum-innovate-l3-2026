import pytest
from incident.security import redact, sandbox_path, validate_answer, validate_endpoint


async def test_prompt_injection_cannot_authorize_effects():
    from incident.labs.l10 import demo
    assert (await demo())["injected_write_effects"] == 0


def test_path_traversal_symlink_and_egress(tmp_path):
    (tmp_path/"acme").mkdir(); (tmp_path/"globex").mkdir()
    (tmp_path/"acme"/"link").symlink_to(tmp_path/"globex", target_is_directory=True)
    with pytest.raises(PermissionError): sandbox_path(tmp_path, "acme", "link/report")
    with pytest.raises(ValueError): validate_endpoint("https://api.openai.com.evil.test", {"api.openai.com"})
    with pytest.raises(ValueError): validate_endpoint("http://10.1.2.3", {"10.1.2.3"})
    assert "secret" not in str(redact({"note": "Bearer secret123", "api_key": "secret"}))


def test_citation_must_match_structured_source_id():
    answer = {"status": "complete", "cause": "pool", "summary": "x", "evidence": ["fake-id"]}
    with pytest.raises(ValueError, match="unobserved"):
        validate_answer(answer, [{"source_id": "real-id", "text": "Mention fake-id here"}])

