# Given for Lesson 04. Paste this definition unchanged into incident/evaluate.py.
# Keep or add the imports it needs in that file.

CASES = [
    {"id": "pool", "tenant": "astro", "incident": "INC-001", "cause": "connection_pool_exhaustion", "split": "development"},
    {"id": "clock", "tenant": "astro", "incident": "INC-002", "cause": "clock_skew", "split": "development"},
    {"id": "missing", "tenant": "astro", "incident": "INC-404", "cause": "unknown", "split": "development"},
    {"id": "ambiguous", "tenant": "astro", "incident": "INC-003", "cause": "unknown", "split": "held_out"},
    {"id": "other_tenant", "tenant": "locomotive", "incident": "INC-001", "cause": "quota_exhaustion", "split": "held_out"},
]
