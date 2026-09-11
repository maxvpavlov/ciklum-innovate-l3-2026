"""Synthetic data. Tenant identity is supplied by application code."""
INCIDENTS = {
    "astro": {
        "INC-001": {"source_id": "log-astro-001", "service": "payments",
                    "cause": "connection_pool_exhaustion", "signal": "DB pool wait 900ms after deploy d42"},
        "INC-002": {"source_id": "log-astro-002", "service": "login",
                    "cause": "clock_skew", "signal": "Token expiry errors; host clock +180s"},
        "INC-003": {"source_id": "log-astro-003", "service": "payments",
                    "cause": "unknown", "signal": "Latency elevated; no diagnostic logs"},
    },
    "locomotive": {"INC-001": {"source_id": "log-locomotive-001", "service": "payments",
                           "cause": "quota_exhaustion", "signal": "Provider quota exhausted"}},
}
RUNBOOKS = [
    {"source_id": "rb-pool-v1", "tenant": "astro", "version": 1,
     "text": "payments connection pool exhaustion DB wait after deployment",
     "cause": "connection_pool_exhaustion", "action": "Consider rollback after approval"},
    {"source_id": "rb-clock-v1", "tenant": "astro", "version": 1,
     "text": "login token expiration clock skew time sync",
     "cause": "clock_skew", "action": "Check time synchronization"},
    {"source_id": "rb-quota-v1", "tenant": "locomotive", "version": 1,
     "text": "payments provider quota exhausted",
     "cause": "quota_exhaustion", "action": "Check tenant quota"},
]


async def simple_tools(name, args, context):
    if name == "log_lookup":
        item = INCIDENTS.get(context.tenant, {}).get(args["incident_id"])
        return {"ok": True, "data": item} if item else {"ok": False, "error": "not_found"}
    if name == "runbook_search":
        words = set(args["query"].lower().replace("_", " ").split())
        found = [r for r in RUNBOOKS if r["tenant"] == context.tenant
                 and words.intersection(r["text"].split())]
        return {"ok": True, "data": found[:2]}
    return {"ok": False, "error": "unknown_tool"}


# What the model reads about each tool: what it returns, and every argument with a description and an
# example. Real models write malformed calls far more often without them (Session 03).
SCHEMAS = [
    {"type": "function", "function": {"name": "log_lookup",
     "description": "Read the diagnostic log record of one incident in the current tenant. It returns "
                    "the record's source_id, service, cause and signal, or not_found.",
     "parameters": {"type": "object", "properties": {"incident_id": {"type": "string",
                    "description": "The incident ID exactly as the task writes it, for example INC-007."}},
                    "required": ["incident_id"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "runbook_search",
     "description": "Search the current tenant's runbooks by keywords. It returns up to two matching "
                    "runbooks, each with its source_id, the cause it describes and a suggested action.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string",
                    "description": "A few plain keywords taken from the log, such as the service and "
                                   "the cause, for example: checkout disk full."}},
                    "required": ["query"], "additionalProperties": False}}},
]

