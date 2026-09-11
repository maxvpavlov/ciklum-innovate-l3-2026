# Incident platform course

An evolving Python reference implementation for the 12-session instructor-led
course. Work in your own repository while following the guided demonstrations.
The default model is an offline deterministic fixture provider. It tests system
behavior, not the reasoning quality of a live language model.

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
git diff lesson-00 lesson-01 -- incident tests
```

The final README and guides describe all services, demonstrations, and limits.
No external systems are modified: remediation only writes to a local mock ledger.

