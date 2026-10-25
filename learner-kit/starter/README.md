# Incident platform: your project

This is the starting point for your own agentic platform in the course *Building Agentic
Platforms*. Your coding agent copies it into a new repository in your course GitLab group on
gitlab.ciklum.net, and every session adds to it.

The default model is an offline, deterministic mock, so the checks need no API keys and
everyone sees the same results. Its usage figures are teaching measurements, not costs.

## Layout

| Folder | What it holds |
|---|---|
| `agent_runtime/` | The agent runtime you build in Sessions 01-07: the loop, model providers, tools and the MCP bridge, context, durable runs, evaluation, supervisor and A2A. |
| `agentic_platform/` | The platform around the runtime. Its shell (run API and console) is copied from the kit in Session 02; you extend it from Session 08 with the registry, tool gateway, identity and operations. |
| `course/` | Course scaffolding: `LESSON` (the checkpoint marker), the lab runner and lesson demos, and given synthetic data. |
| `tests/` | The checks, one file per lesson. |

Each lesson's given files and checks are in the learner kit of the course repository:
https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit
