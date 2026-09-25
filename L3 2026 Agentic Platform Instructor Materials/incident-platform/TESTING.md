# Verification record

The implementation was tested before the instructor guides were written. Each
guide extracts its code excerpts from the exact ending Git tag.

| Checkpoint | Passing tests |
|---|---:|
| lesson-00 | 1 |
| lesson-01 | 7 |
| lesson-02 | 10 |
| lesson-03 | 13 |
| lesson-04 | 15 |
| lesson-05 | 17 |
| lesson-06 | 20 |
| lesson-07 | 24 |
| lesson-08 | 26 |
| lesson-09 | 29 |
| lesson-10 | 32 |
| lesson-11 | 36 |
| lesson-12 | 39 |

Every checkpoint was unpacked independently using git archive. Its full test
suite and its lesson demonstration passed. The final suite includes repeated
trial grading, real MCP stdio, real A2A HTTP streaming and cancellation,
crash-after-effect recovery, permission boundaries, tenant isolation,
concurrency and deadline checks, stale artifact detection, queue cleanup,
release gates, cache partitioning and a measured tuning comparison.

Additional checks: a Linux ARM64 Docker image built successfully from the
Dockerfile, installing runtime dependencies from package indexes. Lessons 11
and 12 passed as the non-root user in a read-only container with only temporary
writable directories, no external network, dropped capabilities and
no-new-privileges enabled. The normal live API adapters were tested with mock
HTTP request/response contracts, not real model credentials.

Not exercised: paid/live model calls, external model judging, third-party MCP or
A2A deployments, remote MCP OAuth, enterprise identity, production persistence,
cloud rollout or a production observability collector. The local MCP connection
negotiated 2026-07-28 using mcp 2.2.0. The A2A service used protocol 1.0 and
a2a-sdk 1.1.2. Local protocol verification does not imply third-party
interoperability with all implementations or versions.

The fixture model is deterministic. Its reported usage is a teaching metric,
not a tokenizer count or paid API cost. The final tuning experiment preserved
fixture success and reduced mean simulated usage from 75 to 63 across the same
five cases with three trials per case. The warm-cache demonstration is reported
separately and is not used to inflate that 16% comparison.

All test data are synthetic. All remediation effects remain in a local SQLite
ledger. The container Compose sandbox uses ephemeral state; durable deployment
storage and production authentication must be configured and verified for the
target environment.
