# Incident platform course

An evolving Python reference implementation for the 12-session instructor-led
course. Work in your own repository while following the guided demonstrations.
The default model is an offline deterministic fixture provider. It tests system
behavior, not the reasoning quality of a live language model.

## Layout

| Folder | What it holds |
|---|---|
| `agent_runtime/` | The agent runtime: the loop, model providers, tools and the MCP bridge, context, durable runs, evaluation, supervisor and A2A (Sessions 01-07). |
| `agentic_platform/` | The platform around it: the run API and console (given from Session 02), then the agent registry, tool gateway, identity and operations (Sessions 08-11). |
| `course/` | Course scaffolding: `LESSON` (the checkpoint marker), the lab runner and lesson demos, synthetic fixtures and the local service launcher. |
| `tests/` | One test file per lesson. |

## Setup

Use Python 3.12 and uv. From this directory:

```sh
uv sync --frozen
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
git diff lesson-00 lesson-01 -- agent_runtime agentic_platform course tests
```

The final README and guides describe all services, demonstrations, and limits.
No external systems are modified: remediation only writes to a local mock ledger.

