"""Explicit boundaries for credentials, endpoints, files and cited evidence."""
import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse


def redact(value):
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in {
            "authorization", "api_key", "password", "secret", "access_token"} else redact(item)
            for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", value)
        return re.sub(r"\bsk-[A-Za-z0-9_-]{8,}", "[REDACTED]", value)
    return value


def validate_endpoint(url, allowed_hosts, allow_loopback=False):
    parsed = urlparse(url)
    if parsed.username or parsed.password or not parsed.hostname or parsed.fragment:
        raise ValueError("invalid_endpoint")
    host = parsed.hostname.lower()
    if host not in allowed_hosts:
        raise ValueError("egress_host_denied")
    loopback = host in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (allow_loopback and loopback and parsed.scheme == "http"):
        raise ValueError("https_required")
    try:
        address = ipaddress.ip_address(host)
        if not address.is_global and not (allow_loopback and address.is_loopback):
            raise ValueError("private_address_denied")
    except ValueError as exc:
        if str(exc) == "private_address_denied":
            raise
    return url


def sandbox_path(root, tenant, relative):
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", tenant):
        raise PermissionError("invalid_tenant")
    base = (Path(root)/tenant).resolve()
    candidate = (base/relative).resolve()
    if Path(relative).is_absolute() or not candidate.is_relative_to(base):
        raise PermissionError("sandbox_escape")
    return candidate


def observed_source_ids(value):
    if isinstance(value, dict):
        ids = {value["source_id"]} if isinstance(value.get("source_id"), str) else set()
        if isinstance(value.get("evidence"), list):
            ids.update(s for s in value["evidence"] if isinstance(s, str))
        return ids | set().union(*(observed_source_ids(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(observed_source_ids(v) for v in value))
    return set()


def validate_answer(answer, observations):
    if not isinstance(answer, dict) or answer.get("status") not in {"complete", "insufficient_evidence"}:
        raise ValueError("invalid_final_answer")
    if not all(isinstance(answer.get(k), str) for k in ["cause", "summary"]):
        raise ValueError("invalid_final_answer")
    evidence = answer.get("evidence")
    if not isinstance(evidence, list) or len(evidence) > 32 or not all(isinstance(s, str) for s in evidence):
        raise ValueError("invalid_evidence")
    if not set(evidence) <= observed_source_ids(observations):
        raise ValueError("unobserved_citation")

