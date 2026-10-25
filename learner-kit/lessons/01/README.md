# Lesson 01 check pack

## Given files

Copy these into your project unchanged. They are data, test doubles and the platform
shell (run API and console) that everyone shares, so results are comparable; they are
not what this lesson teaches.

- `given/course/fixtures.py`: copy to `course/fixtures.py`.
- `given/MockProvider.py`: add `MockProvider` to `agent_runtime/providers.py` in the build step that creates that file.

## Checks

Copy `checks/` into your project root unchanged: it holds this lesson's demo in
`course/labs/` and the tests for this lesson and every earlier one in `tests/`.
This lesson's tests fail until you have built the capability; at first its test file may
fail to import, because the modules it needs do not exist yet. Never edit the tests to
make them pass.

When everything is built, set `LESSON = 1` in `course/__init__.py`. The full
suite should then report **7 passed**, and `python -m course.lab 1`
prints the lesson's demo result.

## Interfaces your code must provide

The checks import these names from your packages. Read the tests to see
how each one is called and what it must return.

- `agent_runtime.core`: `Limits`, `run_agent`
- `agent_runtime.providers`: `HTTPProvider`, `provider_from_env`
- `course`: `LESSON`
