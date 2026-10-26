# AGENTS.md

Briefing for any coding agent working in this project. Read it at the start of every session and
follow it; the prompt for the current lesson says what to do next.

## What this project is

My incident-investigation agent platform for the course *Building Agentic Platforms* (Ciklum
Innovate, L3 2026), built one lesson at a time from the course kit. All data are synthetic, and the
model is an offline, deterministic mock unless I say otherwise.

- Course kit (read-only): `~/agentic-course/course/learner-kit`. Each `lessons/NN/README.md` lists
  that lesson's given files, its checks and the interfaces the checks import.
- My repository: the `origin` remote, in my course group on gitlab.ciklum.net. Push there when a
  lesson is verified.

## Layout

| Folder | What it holds |
|---|---|
| `agent_runtime/` | The agent runtime I build: the loop, model providers, tools and the MCP bridge, and later context, durable runs, evaluation, the supervisor and A2A. |
| `agentic_platform/` | The platform: the run API and console, given in Lesson 02 and unchanged until Lesson 08; then the registry, tool gateway, identity and operations I build. |
| `course/` | Course scaffolding: `LESSON` in `__init__.py` (the checkpoint marker), the lab runner, the lesson demos in `labs/` and the given data. |
| `tests/` | The checks, one file per lesson. |

## Rules

- The checks (`tests/`, `course/labs/`) and the given files come from the course kit unchanged.
  Never edit them to get a pass, and never change an expected outcome.
- Build from the kit and my own code. The course repository also holds a finished reference
  implementation: do not read, copy or search it.
- Use the offline mock model. Never call a paid or remote model unless I ask for it.
- Python 3.12 with uv, using the pinned lock file. Run the tests with `uv run python -m pytest -q`,
  not bare `pytest`.
- A completion message is not evidence. Show the change and the test output, and say plainly what
  was not run or did not pass.
- Raise `LESSON` in `course/__init__.py` only when that lesson's checks pass.
- Do not ask me to run terminal commands.

## Running it

- Tests: `uv run python -m pytest -q`
- A lesson's demo: `uv run python -m course.lab N`, for N up to `LESSON`
- Platform and console: `uv run uvicorn agentic_platform.api:app --port 8000` on loopback, console at
  `http://127.0.0.1:8000/console/`; sign in as `demo-astro`, `demo-operator` or `demo-locomotive`.
  When I ask for it, keep it running in the background and tell me how to stop it.

## Progress log

One entry per verified lesson, added by the Verify prompt. Facts only: the checkpoint, the test
result actually observed, and what the lesson added, named as in that lesson's check-pack README.

- Lesson 01: LESSON = 1, 7 passed. <what Lesson 01 added: the run contract and run_agent in agent_runtime/core.py, the providers in agent_runtime/providers.py>
