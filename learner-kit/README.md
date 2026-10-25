# Building Agentic Platforms: learner kit

Everything you need to build your own incident-investigation agent platform, one session at
a time, by prompting your own coding agent. The kit contains no solutions: you build the
platform yourself and prove it with the checks.

| Folder | What it is |
|---|---|
| `starter/` | The starting project (checkpoint lesson-00). Your coding agent copies it into a new private repository in your course GitLab group on gitlab.ciklum.net. |
| `lessons/NN/given/` | Synthetic data, deterministic test doubles such as the mock model, and the platform shell (run API and console, from Session 02, copied into `agentic_platform/`) that everyone uses unchanged until Session 08. |
| `lessons/NN/checks/` | The lesson's demo and tests, cumulative. Copy them unchanged; they fail until you build the capability. |
| `lessons/NN/README.md` | What to copy where, and the interfaces your code must provide. |

From Session 02 your project keeps the agent runtime in `agent_runtime/`, the platform in
`agentic_platform/` and the course scaffolding in `course/`; the starter README describes the layout.

The prompts for each session are on the session page your instructor shares, and in the
course's learner prompts. All data is synthetic, and nothing here touches a real system.
