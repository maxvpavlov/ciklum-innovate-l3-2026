# Course reframe: from agent engineering to agentic platform

September 2026. The course still has 12 sessions and 1200 contact minutes (eight of 90 minutes,
four of 120). What changed is where the time goes: the platform around the agent runtime is now
taught and built explicitly, and the platform has a web console that shows what has been built.

## Session map

| New | Title | Min | Was | What changed |
|---|---|---:|---|---|
| 01 | Agent architecture and the ReAct runtime | 120 | 01 | Code unchanged. The guide draws the target platform blueprint (runtime, registry, gateway, identity, console, operations). |
| 02 | Reliable tools and MCP integration | 120 | 02 | Code unchanged. Per-worker MCP is framed as the thing the gateway centralizes in 09. |
| 03 | Context, retrieval and memory | 90 | 03 | Code unchanged; platform framing only. |
| 04 | Build the agent evaluation harness | 90 | 04 | Code unchanged; the harness is framed as the future release gate. |
| 05 | Checkpoints, recovery and human approval | 90 | 05 | Code unchanged; approvals are framed as a console view. |
| 06 | Supervisor, subagents and parallel coordination | 120 | 06 + 07 | Old sessions 06 (90) and 07 (120) merged into one 120-minute session. |
| 07 | A2A across independent agent services | 90 | 08 | Renumbered. |
| 08 | Platform core, agent registry and console | 90 | 09 | **New:** agent registry and the first platform console views. |
| 09 | MCP tool gateway and policy | 90 | — | **New session.** |
| 10 | Agent identity, delegated credentials and containment | 90 | 10 | **New:** identity and credential store; old security content folded in. |
| 11 | Operating and releasing agent platforms | 120 | 11 | Adds the release log and the console Operations view and trace. |
| 12 | Tune and present your agentic platform | 90 | 12 | The capstone is presented through the console. Numbers unchanged (75 → 63, 16%). |

## The four platform components

- **Agent registry** (`incident/registry.py`, session 08): schema-validated, immutable, versioned
  agent definitions with a content hash; activation and retirement; remote A2A agents pinned by
  Agent Card hash; tool servers with manifests; discovery by skill.
- **MCP tool gateway** (`incident/gateway.py`, session 09): every agent tool call passes one policy
  and audit point; one shared upstream MCP session per server and tenant instead of one process per
  worker; tool definitions pinned on first connection, and a server whose definitions change is
  quarantined.
- **Agent identity and credentials** (`incident/identity.py`, session 10): users and agents are
  principals; short-lived, audience-bound signed tokens; each child or remote agent gets a narrower
  token that extends the actor chain; tokens never enter stored run state; secrets are released by
  `secret://` reference to named consumers, with an audit trail. The A2A specialist now derives the
  tenant from the verified token instead of a hard-coded value.
- **Platform console** (`incident/console/`, sessions 08–12): a web UI served at `/console`.
  Its Overview shows a live platform map of built and planned components; further views cover the
  Registry, Runs (answer, event timeline, correlated trace), Approvals, Gateway, Identity and
  Operations. It renders every API value as text under a strict Content-Security-Policy.
  Screenshots: `L3 2026 Agentic Platform Instructor Materials/console-screenshots/`.

## Where things are

- Reference code: `lesson-06`…`lesson-12` and `course-complete` point at the rebuilt checkpoints.
  The previous checkpoints are preserved as `v1/lesson-06`…`v1/lesson-12` and `v1/course-complete`.
  Test counts per tag: 1, 7, 10, 13, 15, 17, 25, 27, 33, 37, 43, 48, 51.
- Instructor guides are now generated from `L3 2026 Agentic Platform Instructor Materials/guide-builder/specs/`
  by `build.py`, and `check.py` enforces the guide–code coupling (13 prompts and 4 exact code
  excerpts per guide, files-changed lists, tag hashes, prompts present in `LEARNER_PROMPTS.md`).
  Every guide now opens with "Where this session sits in the platform".
- `L3 Update.xlsx`, sheet `Curriculum scope 2026`: rows 01, 02 and 06–12 were rewritten; the
  session-count formula now shows 12; the mentor name in column P now sits on rows 06 and 07
  (the old multi-agent and A2A sessions). Only that sheet and its hyperlinks were changed.

## Bug found and fixed on the way

Synchronous FastAPI handlers ran in the thread pool while run workers used the same SQLite
connection on the event loop, which raised "bad parameter or other API misuse" under console
polling. All route handlers are now `async def`, and a lesson-08 test enforces it. The original
reference had the same latent race.

## Worth reviewing

- The container recipe is unchanged but was not rebuilt after the reframe (no Docker daemon in the
  authoring environment); repeat the restricted-container check before relying on it.
- Tokens use one shared HMAC development key, the credential store is in memory and the gateway
  runs in-process. The guides state these simplifications and what production systems use instead.
- `L3 Content Development.docx` was not edited.
