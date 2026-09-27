"""Registry: immutable agent versions, lifecycle state, pinned remote agents and tool servers."""
import hashlib
import json
import re
import sqlite3
import time
from jsonschema import ValidationError, validate

AGENT_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"enum": ["single", "team", "remediator"]},
        "description": {"type": "string", "minLength": 1, "maxLength": 300},
        "owner": {"type": "string", "pattern": "^[a-z0-9-]{1,40}$"},
        "allowed": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "skills": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        "prompt": {"type": "string", "minLength": 1},
        "context_chars": {"type": "integer", "minimum": 1000, "maximum": 20000},
        "provider_profile": {"enum": ["default", "efficient"]},
        # Definitions may name credentials only by reference; values live in the credential store.
        "credentials": {"type": "object", "propertyNames": {"pattern": "^[a-z-]{1,40}$"},
                        "additionalProperties": {"type": "string", "pattern": "^secret://[a-z0-9/_-]+$"}},
    },
    "required": ["kind", "description", "owner", "allowed", "skills", "prompt", "context_chars"],
    "additionalProperties": False,
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class Registry:
    def __init__(self, path=":memory:", known_tools=()):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self.known_tools = set(known_tools)
        self.db.execute("CREATE TABLE IF NOT EXISTS agents (name TEXT, version INT, body TEXT, sha256 TEXT, state TEXT, registered REAL, PRIMARY KEY(name,version))")
        self.db.execute("CREATE TABLE IF NOT EXISTS active_versions (name TEXT PRIMARY KEY, version INT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS remote_agents (name TEXT PRIMARY KEY, url TEXT, card TEXT, sha256 TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS tool_servers (name TEXT PRIMARY KEY, manifest TEXT, pins TEXT, status TEXT)")

    def register(self, name, version, spec):
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", name) or not isinstance(version, int) or version < 1:
            raise ValueError("invalid_agent_identity")
        try:
            validate(spec, AGENT_SCHEMA)
        except ValidationError:
            raise ValueError("invalid_definition") from None
        if self.known_tools and not set(spec["allowed"]) <= self.known_tools:
            raise ValueError("unknown_tool")
        body, sha = json.dumps(spec, sort_keys=True), digest(spec)
        old = self.db.execute("SELECT sha256 FROM agents WHERE name=? AND version=?", (name, version)).fetchone()
        if old and old[0] != sha:
            raise ValueError("immutable_definition")
        self.db.execute("INSERT OR IGNORE INTO agents VALUES (?,?,?,?,?,?)",
                        (name, version, body, sha, "available", time.time()))
        self.db.execute("INSERT OR IGNORE INTO active_versions VALUES (?,?)", (name, version))
        return self.get(name, version)

    def get(self, name, version=None):
        if version is None:
            active = self.db.execute("SELECT version FROM active_versions WHERE name=?", (name,)).fetchone()
            if not active:
                raise KeyError("unknown_agent")
            version = active[0]
        row = self.db.execute("SELECT body,sha256,state FROM agents WHERE name=? AND version=?", (name, version)).fetchone()
        if not row:
            raise KeyError("unknown_agent_version")
        return {"name": name, "version": version, "spec": json.loads(row[0]), "sha256": row[1], "state": row[2]}

    def activate(self, name, version):
        if self.get(name, version)["state"] == "retired":
            raise ValueError("retired_version")
        self.db.execute("UPDATE active_versions SET version=? WHERE name=?", (version, name))

    def retire(self, name, version):
        self.get(name, version)
        if self.get(name)["version"] == version:
            raise ValueError("active_version")
        self.db.execute("UPDATE agents SET state='retired' WHERE name=? AND version=?", (name, version))

    def agents(self):
        active = dict(self.db.execute("SELECT name,version FROM active_versions"))
        return [{**self.get(name, version), "active": active.get(name) == version} for name, version in
                self.db.execute("SELECT name,version FROM agents ORDER BY name,version")]

    def register_remote(self, name, url, card, accept_change=False):
        """Pin an A2A Agent Card; a changed card needs an explicit review decision."""
        sha = digest(card)
        old = self.db.execute("SELECT sha256 FROM remote_agents WHERE name=?", (name,)).fetchone()
        if old and old[0] != sha and not accept_change:
            raise ValueError("agent_card_changed")
        self.db.execute("INSERT OR REPLACE INTO remote_agents VALUES (?,?,?,?)", (name, url, json.dumps(card), sha))
        return self.remote(name)

    def remote(self, name):
        row = self.db.execute("SELECT url,card,sha256 FROM remote_agents WHERE name=?", (name,)).fetchone()
        if not row:
            raise KeyError("unknown_remote_agent")
        card = json.loads(row[1])
        return {"name": name, "url": row[0], "sha256": row[2], "card": card,
                "skills": [s["id"] for s in card.get("skills", [])]}

    def remotes(self):
        return [self.remote(r[0]) for r in self.db.execute("SELECT name FROM remote_agents ORDER BY name")]

    def discover(self, skill):
        local = [{"type": "local", "name": a["name"], "version": a["version"]} for a in self.agents()
                 if a["active"] and skill in a["spec"]["skills"]]
        remote = [{"type": "remote", "name": r["name"], "url": r["url"], "sha256": r["sha256"]}
                  for r in self.remotes() if skill in r["skills"]]
        return local + remote

    def register_tool_server(self, name, manifest):
        """A server manifest names its transport, served tenants and each tool's risk."""
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", name):
            raise ValueError("invalid_server_identity")
        if set(manifest) != {"transport", "tenants", "tools"} or not all(
                t.get("risk") in {"read", "write"} for t in manifest["tools"].values()):
            raise ValueError("invalid_server_manifest")
        old = self.db.execute("SELECT manifest FROM tool_servers WHERE name=?", (name,)).fetchone()
        if old and json.loads(old[0]) != manifest:
            raise ValueError("server_manifest_changed")
        self.db.execute("INSERT OR IGNORE INTO tool_servers VALUES (?,?,?,?)",
                        (name, json.dumps(manifest, sort_keys=True), "{}", "registered"))

    def pin_tools(self, name, pins):
        """Record reviewed tool definitions; later differences quarantine the server."""
        current = self.tool_server(name)
        if current["pins"] and current["pins"] != pins:
            self.db.execute("UPDATE tool_servers SET status='quarantined' WHERE name=?", (name,))
            raise ValueError("tool_definition_changed")
        self.db.execute("UPDATE tool_servers SET pins=?, status=? WHERE name=? AND status!='quarantined'",
                        (json.dumps(pins, sort_keys=True), "pinned", name))

    def tool_server(self, name):
        row = self.db.execute("SELECT manifest,pins,status FROM tool_servers WHERE name=?", (name,)).fetchone()
        if not row:
            raise KeyError("unknown_tool_server")
        return {"name": name, **json.loads(row[0]), "pins": json.loads(row[1]), "status": row[2]}

    def tool_servers(self):
        return [self.tool_server(r[0]) for r in self.db.execute("SELECT name FROM tool_servers ORDER BY name")]

    def catalog(self):
        """Map every registered tool name to its server and risk."""
        return {tool: {"server": s["name"], "risk": meta["risk"], "transport": s["transport"],
                       "tenants": s["tenants"], "status": s["status"]}
                for s in self.tool_servers() for tool, meta in s["tools"].items()}
