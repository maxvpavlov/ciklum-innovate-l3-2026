# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

Authoring workspace for the Ciklum internal course **Innovate: Building Agentic Platforms** (L3, 2026): 12 sessions, 20 contact hours. Learners build a sandboxed *incident-investigation* agent platform step by step. They do it by prompting their own coding agent, not by typing commands. The work here is mostly course design and content; the code is a teaching reference.

| Path | What it is |
|---|---|
| `L3 Update.xlsx` | Curriculum workbook (see "Curriculum workbook" below) |
| `L3 Content Development.docx` | L&D per-topic content-development template (overview, objectives, agenda, activities, wrap-up, e-learning, assets); partly filled for session 01 "Agent foundations" |
| `L3 2026 Agentic Platform Instructor Materials/instructor-guides/NN <title>.docx` | One instructor guide per session (01–12) |
| `L3 2026 Agentic Platform Instructor Materials/incident-platform/` | Python reference implementation (see "Git layout" below) |

## Git layout

- The whole workspace is one repo: `github.com/maxvpavlov/ciklum-innovate-l3-2026` (private).
- `incident-platform` used to be a standalone repo. Its history was subtree-merged in, and its tags (`lesson-00`…`lesson-12`, `course-complete`) now live in this repo.
- Those tags point at the original standalone commits, where the platform files sit at the tree root. So `git archive lesson-05` produces the platform checkpoint alone, not the whole course.
- To compare a tag with the current platform subdirectory, compare trees: `git diff lesson-12 "HEAD:L3 2026 Agentic Platform Instructor Materials/incident-platform"`.

The xlsx/docx files are binary. Read them with the docx/xlsx skills, `textutil -convert txt` (macOS), or `uv run --with openpyxl` / `--with python-docx`. Convert into the scratchpad, never next to the originals.

### Curriculum workbook (`L3 Update.xlsx`)

- **`Curriculum scope 2026`** is the source of truth for this course.
  - Columns: Category, Lesson, Description, Guided demo / Build, Session Materials / References, Mentor(s), Prework, Practice / Tuning, Platform milestone, Date, Audience, Level, Estimated Duration (min), Week Date Start/End.
  - The 12 sessions match the guide filenames and the repo's `lesson-NN` tags one-to-one: eight of 90 min and four of 120 min (01, 02, 07, 11), 1200 min in total.
  - A 120-min session is "30 min discussion + 90 min guided build". Every session ends in a runnable platform checkpoint.
  - The capstone (12) is a tuned repo, a runbook, a demo and a before/after comparison of quality, cost and latency against the single-agent baseline.
- **`Effort coord`** holds the audience, entry criteria, "About L3" copy and Bloom's verbs. **`Selection`** holds the application form and timeline, with the first session on 2026-10-28. **`Sheet5`** is the project plan. **`Sheet1`** lists open design questions.
- **`Curriculum scope 2025`** and **`Curriculum materials 2025`** are hidden sheets from the previous, unrelated GenAI-survey edition. Use them only for history.
- Known inconsistencies, worth fixing rather than copying:
  - The session-count formula counts an unnumbered "mindset" row and shows 13.
  - `Selection` says "35 h".
  - Mentor and date columns are empty; a mentor name sits in unlabeled column P.
  - Several reference cells list 2–3 titles but link only one URL, sometimes a mismatched one.

## incident-platform: commands

Run everything from `L3 2026 Agentic Platform Instructor Materials/incident-platform/` (quote the path because it contains spaces). Pinned deps are in `uv.lock`. The course materials and the Dockerfile target Python 3.12, but `pyproject.toml` allows `>=3.12,<3.15` and there is no `.python-version`, so pass `--python 3.12` or uv may choose 3.14.

```bash
uv sync --python 3.12                                # create .venv (gitignored)
uv run python -m pytest -q                           # full suite: 39 tests, ~8s, fully offline
uv run python -m pytest -q tests/test_lesson05.py    # one lesson's tests
uv run python -m pytest -q tests/test_lesson05.py -k approval   # one test
uv run python -m incident.lab 8                      # run a lesson demo (1..LESSON), prints JSON
uv run python -m incident.evaluate --trials 3 --split held_out  # writes var/evaluation.json
uv run uvicorn incident.api:app --port 8000          # platform run API
A2A_BASE_URL=http://127.0.0.1:8010 uv run uvicorn incident.a2a_service:app --port 8010  # remote specialist
A2A_URL=http://127.0.0.1:8010 uv run uvicorn incident.api:app   # API with the hybrid (A2A) team
uv run python -m incident.client submit INC-001 --agent team --wait   # CLI client (PLATFORM_TOKEN, default demo-acme)
docker compose up --build                            # restricted container: read-only, no egress, tmpfs state
```

- **Run `python -m pytest`, not bare `pytest`.** `pyproject.toml` has no `[build-system]`, so uv never installs the `incident` package. Bare `pytest` fails every file with `ModuleNotFoundError: No module named 'incident'`; `python -m` puts the cwd on `sys.path`.
- There is no linter or formatter config.
- Labs 11 and 12 write `var/trace.html` and `var/capstone-comparison.json` relative to the cwd. Labs 8 and 11 start a uvicorn subprocess on an ephemeral loopback port (`incident/local_service.py`) and clean it up themselves.

## incident-platform: checkpoint model

- Git tags `lesson-00` … `lesson-12` mark the end state of each session. `course-complete` sits on top; the commits after it change only `README.md` and `LEARNER_PROMPTS.md`. Each lesson adds one module/lab plus `tests/test_lessonNN.py`.
- `incident/__init__.py` sets `LESSON = N`. `incident.lab` refuses any lesson above it, and learners raise it only when the capability is verified.
- `TESTING.md` records the expected passing-test count per tag (1, 7, 10, 13, 15, 17, 20, 24, 26, 29, 32, 36, 39). To check a checkpoint in isolation, unpack it the way the reference was verified: `git archive lesson-05 | tar -x -C <tmpdir>`, then run the suite there.
- **Treat the reference as frozen unless the user explicitly wants to change it.** A code change in lesson N has to reach the `lesson-N` tag and every later tag (they sit on the standalone line, so this means rebuilding that line and re-tagging), plus the guide excerpts (see "Guide–repo coupling" below). It also has to reach the numbers quoted in README, TESTING and the guides: the 39 tests, and a capstone mean usage drop from 75 to 63 (16%).

## incident-platform: architecture

Everything is built on one loop, `core.run_agent(provider, execute, schemas, task, context, limits, …)`:

- **Provider protocol:** `async complete(messages, tools, max_tokens) -> Reply(message, tokens, cost_usd)`. Messages and tool schemas use OpenAI chat format internally. `HTTPProvider` converts to Anthropic Messages when `kind="anthropic"`. `provider_from_env()` returns `MockProvider` unless `MODEL_PROVIDER` is set.
- **Executor protocol:** `async execute(name, args, context) -> dict`. A supervisor's `delegate` tool and the tool executor both plug into this same slot.
- **Loop behavior:** pending tool calls are saved via the `checkpoint` callback *before* dispatch, and `ApprovalRequired` pauses the run as `waiting_approval`. Guards fail the run with a code: `step_budget`, `token_budget`, `TimeoutError`, `repeated_action`. The token budget is checked before the call using `len(json)//3` plus `max_output_tokens`. The final JSON answer goes through `security.validate_answer`, which rejects citations of source IDs that were never observed.
- **`Context` is application-owned identity:** tenant, role, allowed tools, approved action keys, and parent_id. The model never controls it; child runs get a narrowed copy through `dataclasses.replace`.

The layers on top, in lesson order:

- **Tools (`tools.py`).** `ToolExecutor` handles authorization (`context.allowed`), jsonschema validation, output-size limits and one retry. Reads go through a pluggable `read_handler`, which evolves from `fixtures.simple_tools` to `context.context_tools` (ranked retrieval) to `mcp_bridge.MCPReadAdapter`. The MCP adapter talks to a real MCP stdio subprocess, and the launcher binds the tenant via `INCIDENT_TENANT`. The only write tool is `mock_remediate`. It requires `action_key` (sha256 of tenant, run_id, name, args) in `context.approved`, and it records the effect in an SQLite `effects` ledger within the same transaction, so a replay after a crash is idempotent.
- **Context and durability.** `context.py` handles message selection that never orphans tool-call IDs, the versioned artifact store (optimistic `expected_version`) and TTL memory. `durable.py` provides `RunStore`, with `runs`, `approvals` and `leases` tables, and `resume_run`.
- **Multi-agent.** `supervisor.Supervisor` runs its own `run_agent` with a single `delegate` tool. Each child is another `run_agent` with a narrowed Context, all under a lock-guarded `SharedBudget` (tokens, max agents, depth). Parallel delegation goes through `coordination.schedule`, a dependency-aware scheduler with a deadline. `platform.HybridSupervisor` sends the `runbooks` role to the remote A2A specialist (`a2a_service.py` server, `a2a_client.RemoteSpecialist`), using bearer auth, streaming and cancellation.
- **Platform (`platform.py`).** `Definitions` holds immutable, versioned agent specs (`single`, `team`, `remediator` seeded at v1; `activate` switches versions). `Platform.submit` queues a run, and a worker then goes through `operations.Admission` (queue and rate limits), a lease and a semaphore. It dispatches by `spec.kind`; `team` uses Supervisor with MCP workers, plus A2A when `remote_url` is set. All stores share one SQLite file (`var/platform.db`, or `PLATFORM_DB`).
- **API and ops.** `api.py` is FastAPI with demo bearer identities: `demo-acme` (analyst), `demo-operator`, `demo-globex`, overridable via `PLATFORM_IDENTITIES`. Only operators may decide approvals, and a decision must echo the current proposal key. `operations.py` provides traces built from parent/child runs, `release_gate` (which requires the same `dataset_sha256` and split) and `evaluate_platform`. `tuning.py` contains the capstone experiments: `EfficientMockProvider`, the tenant/config-partitioned `CachedProvider` and `RoutingProvider`.
- **Labs.** `incident/labs/lNN.py` each expose `async demo()`. It asserts the lesson's guarantees and returns a JSON-able dict, and most `test_lessonNN.py` files simply call it.

Fixture facts that other material depends on:

- All data are synthetic (`fixtures.py`). Tenants are `acme` (INC-001 pool exhaustion, INC-002 clock skew, INC-003 unknown) and `globex` (INC-001 quota exhaustion).
- `evaluate.CASES` holds 5 cases split into `development` and `held_out`. Their hash is the dataset identity, so editing cases breaks comparability.
- Mock providers are deterministic policies, and the "tokens" they report (20 per tool call, 35 per answer) are teaching metrics, not tokenizer counts or cost. Changing them silently changes the published capstone numbers.

Configuration comes from environment variables only; no `.env` file is loaded:

| Area | Variables |
|---|---|
| Model provider | `MODEL_PROVIDER` (`mock` \| `openai` \| `openai-compatible` \| `anthropic`), `MODEL_NAME`, `MODEL_API_KEY`, `MODEL_BASE_URL`, `MODEL_ALLOWED_HOSTS` |
| Pricing | `MODEL_INPUT_USD_PER_MILLION`, `MODEL_OUTPUT_USD_PER_MILLION` |
| A2A | `A2A_URL`, `A2A_BASE_URL`, `A2A_TOKEN`, `A2A_ALLOWED_HOSTS` |
| Platform | `PLATFORM_DB`, `PLATFORM_IDENTITIES`, `PLATFORM_TOKEN` (client) |

The live adapters were tested only against mock HTTP. Default to `mock`, and never run a paid call without explicit authorization.

## Course content conventions

- **Learners drive their own coding agents.** Learner-facing material gives *prompts*, not terminal command snippets, as stated in the README. The executable CLIs, labs and tests exist for the coding agents to use.
- **`LEARNER_PROMPTS.md` follows a fixed shape per lesson.** Each lesson has a starting/ending reference tag, then `Prepare the workspace`, `Orient to the reference`, `Build step 1–4`, `Learner exercise`, `Verify the checkpoint`, `Review the result`, and several `Recover when …` troubleshooting prompts. Keep new or edited lessons in this shape.
- **Recurring teaching stances to preserve:**
  - A coding agent's completion message is not evidence.
  - Unrun or skipped checks are not passes.
  - Report failures honestly.
  - Fixture metrics are not live-model or cost claims.
  - Local guarantees such as idempotent effects do not automatically extend to external APIs.
  - Never alter expected outcomes to get a pass.
- **Instructor guides share one template.** They were generated with python-docx, and no generator script is present. Each is about 3.3–3.5k words:
  - Header: outcome, duration, and starting/ending checkpoint with the tag hash.
  - Preparation, which holds two setup prompts plus readiness, offline-fallback and pinned-version notes.
  - Timed agenda table.
  - Instructor script: four build steps, each written as SAY → SHOW → PROMPT → REVIEW → "Explain the choice" → ASK/"Likely answer" → PAUSE.
  - Learner practice: exercise, VERIFY and expected JSON.
  - Completion criteria, including the recorded test count and the files changed.
  - Demo troubleshooting, verification scope, session close, and references.
- **Guide–repo coupling is currently exact.** Every guide has 13 prompts and 4 code excerpts.
  - Each REVIEW excerpt cites "source lines X to Y at lesson-NN" and matches that tag exactly.
  - Each "Files changed" list equals `git diff lesson-(N-1)..lesson-N`.
  - Expected JSON matches the lab output.
  - All 156 prompts appear verbatim in `LEARNER_PROMPTS.md`.

  Keep all four in sync when editing any of them.
- **Known content gaps, as of the first review:**
  - The guides are destined for Google Docs in the course Drive folder; the README says that publication is still pending.
  - The `instructor-guides.zip` and `incident-platform.zip` files referenced in the text do not exist.
  - Guide 12's agenda has no build slot, yet it keeps the four build-step prompts.
  - Several guides promise mentor-supplied "scaffolding" that has no separate artifact: 01's workflow baseline, and scaffolding in 02, 07 and 11.
  - Guide 11 mentions optional Kubernetes, but there are no Kubernetes files.
  - Titles 03 and 05 drop commas that the workbook and prompts use.
  - Neither the guides nor the README use the "Innovate"/Ciklum branding.
