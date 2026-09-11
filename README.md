# Incident platform course

An evolving Python reference implementation for the 12-session instructor-led
course. Work in your own repository while following the guided demonstrations.
The default model is an offline deterministic fixture provider. It tests system
behavior, not the reasoning quality of a live language model.

## Setup

Use Python 3.12 and uv. From this directory:

```sh
uv sync --python 3.12 --frozen
uv run python -m pytest -q
```

Git tags `lesson-00` through `lesson-12` are runnable checkpoints. To start a
lesson without altering your work, create a separate worktree:

```sh
git worktree add ../lesson01-start lesson-00
cd ../lesson01-start
uv sync --frozen
```

To inspect what the instructor will add:

```sh
git diff lesson-00 lesson-01 -- incident tests
```

The final README and guides describe all services, demonstrations, and limits.
No external systems are modified: remediation only writes to a local mock ledger.

## Instructor documents

The destination for the twelve Google Docs is the
[instructor materials folder](https://drive.google.com/drive/u/0/folders/1wos8PjyC0mTDQxrcZ89b9mG0yYV57Zr3).
Native publication is pending browser upload access. The prepared guides are
also available in the companion instructor-guides.zip archive.
Each guide names its starting and ending checkpoint, exact source files,
demonstration commands, learner pauses, expected outcomes and failure exercises.

## Checkpoint sequence

| End tag | Capability | Minutes |
|---|---|---:|
| lesson-01 | Bounded ReAct runtime and configurable provider adapters | 120 |
| lesson-02 | Tool contracts, approval boundary, idempotent mock effects and real MCP stdio | 120 |
| lesson-03 | Context selection, retrieval, expiring memory and versioned artifacts | 90 |
| lesson-04 | Repeated evaluation, held-out cases and optional judge calibration | 90 |
| lesson-05 | Durable checkpoints, crash recovery and exact-action approval | 90 |
| lesson-06 | Supervisor, isolated child runs and shared worker budgets | 90 |
| lesson-07 | Parallel scheduling, typed replies and bounded review | 120 |
| lesson-08 | Independent A2A specialist, streaming, authentication and cancellation | 90 |
| lesson-09 | Reusable platform core, run API and immutable definitions | 90 |
| lesson-10 | Adversarial containment, paths, egress, provenance and redaction | 90 |
| lesson-11 | End-to-end platform, traces, admission controls and evaluated releases | 120 |
| lesson-12 | Tuning, before/after comparison and presentation evidence | 90 |

Total: 12 sessions and 20 contact hours. Preparation and practice are additional.
At each checkpoint, run that lesson with `uv run python -m incident.lab 7`
(replace 7 with the lesson number). The checkpoint includes earlier lessons.
Use a fresh worktree for comparisons rather than discarding your learner branch.

## Run the complete platform

Terminal one starts the optional independent specialist:

```sh
uv run uvicorn incident.a2a_service:app --host 127.0.0.1 --port 8010
```

Terminal two starts the platform. Set `A2A_URL` to use the remote specialist in a
team run. Without it, both workers remain local and use MCP tools.

```sh
export MODEL_PROVIDER=mock
export A2A_URL=http://127.0.0.1:8010
uv run uvicorn incident.api:app --host 127.0.0.1 --port 8000
```

Terminal three:

```sh
uv run python -m incident.client submit INC-001 --agent team --wait
uv run python -m incident.client inspect RUN_ID
uv run python -m incident.client trace RUN_ID --output var/trace.html
```

Replace RUN_ID with the returned identifier. Open the generated HTML in a
browser. The API also exposes `/docs`, `/health`, and authenticated run endpoints.
For a self-contained end-to-end demonstration with automatic local-service
cleanup, run `uv run python -m incident.lab 11`.

## Approval and recovery

The default analyst identity cannot submit the remediation configuration.
Use the deliberately named local operator identity for the simulated exercise:

```sh
export PLATFORM_TOKEN=demo-operator
uv run python -m incident.client submit INC-001 --agent remediator --wait
uv run python -m incident.client inspect RUN_ID
uv run python -m incident.client approve RUN_ID
uv run python -m incident.client resume RUN_ID
```

The approve command prints and submits the exact currently pending action key.
`deny`, `cancel`, and `inspect` are also available. The remediation configuration
uses a scripted fixture to reach the approval branch. It does not recommend or
perform a real rollback. Session 05 deliberately crashes after a committed mock
effect and proves that resume does not create a duplicate.

## Model configuration

Default: `MODEL_PROVIDER=mock`. No model credentials are needed for the labs.
HTTP adapters support OpenAI-compatible Chat Completions and Anthropic Messages.
Choose a tool-capable model you are authorized to use:

```sh
export MODEL_PROVIDER=openai
export MODEL_NAME=YOUR_TOOL_CAPABLE_MODEL
export MODEL_API_KEY=YOUR_KEY
uv run python -m incident.lab 1
```

For Anthropic, use `MODEL_PROVIDER=anthropic`. For an OpenAI-compatible endpoint,
use `MODEL_PROVIDER=openai-compatible`, set `MODEL_BASE_URL` to its API root and
set `MODEL_ALLOWED_HOSTS` to the exact trusted hostname. This is not a universal
adapter for every vendor-specific API. Public endpoints require HTTPS; explicit
loopback endpoints may use HTTP for local teaching.

Optional pricing: `MODEL_INPUT_USD_PER_MILLION` and
`MODEL_OUTPUT_USD_PER_MILLION`. Live cost remains unavailable in evaluation
reports if rates are not configured. Credentials are not read from `.env`
automatically; export environment variables or use your normal secret-management
workflow. Do not commit keys. PowerShell uses `$env:NAME='value'` instead of
`export NAME=value`.

The self-contained MCP/A2A and end-to-end lab helpers intentionally select the
offline fixture provider. To exercise live models across services, start the
services manually with the intended environment and run an explicit benchmark.

## Evaluation and capstone

```sh
uv run python -m incident.evaluate --trials 3 --output var/baseline.json
uv run python -m incident.evaluate --split held_out --trials 3
uv run python -m incident.lab 12
```

Session 12 writes `var/capstone-comparison.json`. In the deterministic fixture,
the candidate preserves success on five cases and reduces mean simulated usage
from 75 to 63 (16%). Cold and warm cache results are reported separately.
These are fixture-policy measurements, not live model-quality or cost claims.
Use `--live` on the evaluator only after configuring the provider and accepting
the costs of those calls. The optional model judge must be calibrated against
human labels on representative cases.

## Container demonstration

```sh
docker build -t l3-incident-course:local .
docker run --rm --network none --read-only --tmpfs /tmp \
  --tmpfs /app/var:uid=1000,gid=1000 --cap-drop ALL \
  --security-opt no-new-privileges:true \
  l3-incident-course:local python -m incident.lab 11
```

The image and restricted end-to-end demo were tested on Linux ARM64. The
Compose recipe binds only loopback, uses an internal network and temporary
writable state. That temporary container sandbox is intentionally ephemeral.
Use the normal local SQLite file for durable worker-recovery demonstrations.
A persistent deployment requires a provisioned volume, real identity, secrets,
storage protection and infrastructure-specific validation. The course's path
and capability checks do not sandbox arbitrary Python execution.

## Verification and limits

See [TESTING.md](TESTING.md) for exact verification scope. The final suite has
39 tests. Every tag from lesson-00 through lesson-12 was independently unpacked
and tested, and each lesson demo was run at its own tag. MCP and A2A transport
tests use actual local connections. Live model accounts, third-party MCP/A2A
services, OAuth identity providers and production cloud deployment were not
tested. SQLite state is not an encrypted secret store. The A2A specialist's
remote task store is in memory. Local demo bearer tokens are deliberately public
fixtures and must not be used to secure an exposed deployment.

The native macOS test environment used packaged Python 3.12.14 with the pinned
SDKs and packaged native dependencies after a local binary-wheel loading issue.
The Linux Docker build separately installed dependencies from package indexes
and successfully ran the end-to-end and capstone demos.
