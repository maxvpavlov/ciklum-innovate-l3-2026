"""Principals, signed short-lived tokens, delegation chains and a credential store."""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time

DEV_SIGNING_KEY = "dev-only-signing-key-change-me"


def _encode(value):
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


class TokenIssuer:
    """HMAC-signed, JWT-shaped tokens for a single trust domain.

    Production issuers sign with asymmetric keys and publish verification keys, so a
    verifier cannot also mint tokens. The shared key here keeps the course offline."""

    def __init__(self, key=None, issuer="incident-platform"):
        key = key or os.getenv("PLATFORM_SIGNING_KEY", DEV_SIGNING_KEY)
        self.key, self.issuer = key.encode() if isinstance(key, str) else key, issuer

    def issue(self, claims, ttl=300):
        now = int(time.time())
        payload = {**claims, "iss": self.issuer, "iat": now, "exp": now+ttl, "jti": secrets.token_hex(8)}
        signing_input = _encode({"alg": "HS256", "typ": "JWT"})+"."+_encode(payload)
        return signing_input+"."+_encode(hmac.new(self.key, signing_input.encode(), hashlib.sha256).digest())

    def verify(self, token, audience):
        try:
            header, payload, signature = token.split(".")
            expected = hmac.new(self.key, (header+"."+payload).encode(), hashlib.sha256).digest()
            valid = hmac.compare_digest(_decode(signature), expected)
            claims = json.loads(_decode(payload))
        except (ValueError, TypeError, AttributeError):
            raise PermissionError("malformed_token") from None
        if not valid:
            raise PermissionError("bad_signature")
        if claims.get("iss") != self.issuer:
            raise PermissionError("wrong_issuer")
        if claims.get("exp", 0) <= time.time():
            raise PermissionError("token_expired")
        if claims.get("aud") != audience:
            raise PermissionError("wrong_audience")
        return claims


def actor_chain(claims):
    """Current actor first, then each earlier actor, ending with the human subject."""
    chain, actor = [], claims.get("act")
    while actor:
        chain.append(actor["sub"])
        actor = actor.get("act")
    return chain+[claims["sub"]]


class Delegation:
    """Mints narrowed, audience-bound tokens for runs. Tokens stay in memory, never in run state."""

    def __init__(self, issuer, path=":memory:", ttl=300):
        self.issuer, self.ttl, self.tokens, self.delegated = issuer, ttl, {}, {}
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS grants (jti TEXT PRIMARY KEY, tenant TEXT, run_id TEXT, "
                        "subject TEXT, actors TEXT, audience TEXT, scope TEXT, expires REAL)")

    def _mint(self, run_id, claims):
        token = self.issuer.issue(claims, self.ttl)
        issued = self.issuer.verify(token, claims["aud"])
        self.db.execute("INSERT INTO grants VALUES (?,?,?,?,?,?,?,?)", (issued["jti"], issued["tenant"], run_id,
                        issued["sub"], json.dumps(actor_chain(issued)[:-1]), issued["aud"], issued["scope"], issued["exp"]))
        self.tokens[(run_id, claims["aud"])] = token
        return token

    def for_run(self, context, subject, agent, audience="tool-gateway"):
        return self._mint(context.run_id, {"sub": subject, "tenant": context.tenant, "role": context.role,
            "aud": audience, "scope": " ".join(sorted(context.allowed)), "act": {"sub": agent}})

    def for_child(self, parent, child, audience="tool-gateway", actor=None):
        """A child token can only narrow the parent's scope and extends the actor chain."""
        token = self.tokens.get((parent.run_id, "tool-gateway"))
        if token is None:
            raise PermissionError("no_parent_grant")
        claims = self.issuer.verify(token, "tool-gateway")
        requested = set(child.allowed)
        if not requested <= set(claims["scope"].split()) or child.tenant != claims["tenant"]:
            raise PermissionError("delegation_exceeds_parent")
        self.delegated.setdefault(parent.run_id, []).append(child.run_id)
        return self._mint(child.run_id, {"sub": claims["sub"], "tenant": claims["tenant"], "role": child.role,
            "aud": audience, "scope": " ".join(sorted(requested)),
            "act": {"sub": actor or f"worker:{child.role}", "act": claims["act"]}})

    def token(self, run_id, audience="tool-gateway"):
        return self.tokens.get((run_id, audience))

    def revoke(self, run_id):
        """Revoking a run also revokes every grant delegated beneath it."""
        for child in self.delegated.pop(run_id, []):
            self.revoke(child)
        for key in [k for k in self.tokens if k[0] == run_id]:
            del self.tokens[key]

    def grants(self, tenant, limit=100):
        keys = ["jti", "run_id", "subject", "actors", "audience", "scope", "expires"]
        rows = self.db.execute("SELECT jti,run_id,subject,actors,audience,scope,expires FROM grants WHERE tenant=? "
                               "ORDER BY rowid DESC LIMIT ?", (tenant, limit))
        return [{**dict(zip(keys, row)), "actors": json.loads(row[3]), "live": (row[1], row[4]) in self.tokens}
                for row in rows]


class Secret:
    """A credential value that refuses to be printed, logged or serialized by accident."""
    __slots__ = ("_value",)

    def __init__(self, value):
        self._value = value

    def reveal(self):
        return self._value

    def __repr__(self):
        return "Secret('[REDACTED]')"

    __str__ = __repr__


class CredentialStore:
    """Upstream credentials by reference. Values reach only named consumers and every release is audited.

    This teaching store keeps values in process memory. It is not a vault: production
    deployments use a managed secret store or KMS with rotation and access policies."""

    def __init__(self, path=":memory:"):
        self.values = {}
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS secret_access (ts REAL, ref TEXT, consumer TEXT, decision TEXT)")

    def put(self, ref, value, consumers):
        if not re.fullmatch(r"secret://[a-z0-9/_-]+", ref):
            raise ValueError("invalid_secret_ref")
        self.values[ref] = (Secret(value), frozenset(consumers))

    def lease(self, ref, consumer):
        stored = self.values.get(ref)
        allowed = stored is not None and consumer in stored[1]
        self.db.execute("INSERT INTO secret_access VALUES (?,?,?,?)", (time.time(), ref, consumer,
                        "released" if allowed else "denied"))
        if not allowed:
            raise PermissionError("secret_access_denied")
        return stored[0]

    def refs(self):
        return [{"ref": ref, "consumers": sorted(consumers)} for ref, (_, consumers) in sorted(self.values.items())]

    def accesses(self, limit=50):
        rows = self.db.execute("SELECT ts,ref,consumer,decision FROM secret_access ORDER BY rowid DESC LIMIT ?", (limit,))
        return [dict(zip(["ts", "ref", "consumer", "decision"], row)) for row in rows]
