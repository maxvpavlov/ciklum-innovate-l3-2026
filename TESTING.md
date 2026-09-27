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
| lesson-06 | 25 |
| lesson-07 | 27 |
| lesson-08 | 33 |
| lesson-09 | 37 |
| lesson-10 | 43 |
| lesson-11 | 48 |
| lesson-12 | 51 |

Every checkpoint was unpacked independently using git archive. Its full test
suite and its lesson demonstration passed. The final suite includes repeated
trial grading, real MCP stdio, real A2A HTTP streaming and cancellation,
crash-after-effect recovery, permission boundaries, tenant isolation,
concurrency and deadline checks, stale artifact detection, queue cleanup,
release gates, cache partitioning and a measured tuning comparison. The
platform components added in the reframed course are covered too:

- **Registry:** schema validation, immutable versions, lifecycle (retired versions
  cannot run), discovery by skill and a pinned A2A Agent Card that rejects a change.
- **Tool gateway:** every policy denial, the audit ledger, one shared MCP session for
  several workers, and quarantine after a changed tool definition.
- **Identity:** tampered, expired and wrong-audience tokens, delegation chains that only
  narrow, tenant mismatch, the A2A specialist accepting only delegated tokens, and no
  token or model key in stored run state.
- **Console:** CSP headers, tenant-scoped views, operator-only actions, a static check
  that no console script renders HTML from data, and a check that API handlers run
  on the event loop (they share one SQLite connection with the workers).

The console itself was driven in headless Chromium against the lesson-08 to
lesson-12 checkpoints: sign-in, each view, run submission, approval and
resumption, with no failed requests or script errors.

The container recipe was verified for the previous version of the reference: a
Linux ARM64 image built from the Dockerfile, and lessons 11 and 12 passed as the
non-root user in a read-only container with only temporary writable directories,
no external network, dropped capabilities and no-new-privileges enabled. The
Dockerfile and Compose file are unchanged, but the container was not rebuilt
after the reframing, so repeat that check before relying on it. The normal live API adapters were tested with mock
HTTP request/response contracts, not real model credentials.

Not exercised: paid/live model calls, external model judging, third-party MCP or
A2A deployments, remote MCP OAuth, an enterprise identity provider, a managed
secret vault, production persistence, cloud rollout or a production
observability collector. Tokens use one shared HMAC development key; the
credential store is in process memory; the gateway runs inside the platform
process and pins tool definitions on first connection. The local MCP connection
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
