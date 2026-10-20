"""Build the public learner kit from the reference checkpoints.

Learners do not clone the reference. They start from the kit's starter project, copy each
lesson's given files and check pack into their own project, and build the rest themselves.

    uv run python kit.py            # regenerate learner-kit/ at the repository root from the lesson tags
    uv run python kit.py --verify   # also run every lesson's checks against its reference tag

For lesson N the kit holds:
  given/   data and deterministic test doubles that every learner must use unchanged, so
           everyone gets the same results (whole files, or one definition to paste in)
  checks/  the lesson's lab and the cumulative tests at lesson-N, copied unchanged
Plus README.md with the interfaces the checks import from the learner's code.
"""

import argparse
import ast
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from guidelib import HERE as REPO, MATERIALS, tag_name

KIT = MATERIALS.parent / "learner-kit"
KIT_URL = "https://github.com/maxvpavlov/ciklum-innovate-l3-2026/tree/main/learner-kit"

# What is given rather than built: synthetic data, deterministic model doubles and the
# local service launcher. (path, definition) with definition None for a whole file.
GIVEN = [
    ("incident/fixtures.py", None),
    ("incident/providers.py", "MockProvider"),
    ("incident/evaluate.py", "CASES"),
    ("incident/supervisor.py", "SupervisorProvider"),
    ("incident/local_service.py", None),
    ("incident/tuning.py", "EfficientMockProvider"),
]
STARTER_FILES = [".gitignore", "pyproject.toml", "uv.lock", "incident/__init__.py",
                 "incident/lab.py", "incident/labs/__init__.py", "tests/test_setup.py"]
TEST_COUNTS = [1, 7, 10, 13, 15, 17, 25, 27, 33, 37, 43, 48, 51]


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def show(n, path):
    try:
        return git("show", f"{tag_name(n)}:{path}")
    except subprocess.CalledProcessError:
        return None


def ls(n, prefix):
    return [p for p in git("ls-tree", "-r", "--full-tree", "--name-only", tag_name(n), "--", prefix).split()
            if p.endswith(".py")]


def definition(source, name):
    """Source text of a top-level class, function or assignment, decorators included."""
    tree = ast.parse(source)
    for node in tree.body:
        names = [node.name] if hasattr(node, "name") else \
            [t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)]
        if name in names:
            start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
            return "\n".join(source.splitlines()[start - 1:node.end_lineno]) + "\n"
    return None


def given_text(n, path, name):
    source = show(n, path)
    if source is None:
        return None
    return source if name is None else definition(source, name)


def given_for(n):
    """Given items that first appear, or change, at lesson n."""
    items = []
    for path, name in GIVEN:
        now, before = given_text(n, path, name), given_text(n - 1, path, name) if n > 1 else None
        if now is not None and now != before:
            items.append((path, name, now, before is not None))
    return items


def interfaces(n, given_names):
    """{module: [names]} that lesson n's checks import from the learner's incident package."""
    found = {}
    for path in ls(n, "tests") + ls(n, "incident/labs"):
        for node in ast.walk(ast.parse(show(n, path))):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("incident"):
                if node.module.startswith("incident.labs"):
                    continue
                for alias in node.names:
                    if (node.module, alias.name) not in given_names:
                        found.setdefault(node.module, set()).add(alias.name)
    return {m: sorted(v) for m, v in sorted(found.items())}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_starter():
    out = KIT / "starter"
    for f in STARTER_FILES:
        write(out / f, show(0, f))
    write(out / "README.md", "\n".join([
        "# Incident platform: your project",
        "",
        "This is the starting point for your own agentic platform in the course *Building Agentic",
        "Platforms*. Your coding agent copies it into a new repository in your course GitLab group,",
        "and every session adds to it.",
        "",
        "The default model is an offline, deterministic mock, so the checks need no API keys and",
        "everyone sees the same results. Its usage figures are teaching measurements, not costs.",
        "",
        "Each lesson's given files and checks are in the learner kit of the course repository:",
        KIT_URL,
        "",
    ]))


def build_lesson(n, known_given):
    nn = f"{n:02d}"
    out = KIT / "lessons" / nn
    items = given_for(n)
    for path, name, text, changed in items:
        if name is None:
            write(out / "given" / path, text)
        else:
            header = (f"# Given for Lesson {nn}. Paste this definition unchanged into {path}"
                      f"{', replacing the earlier version' if changed else ''}.\n"
                      "# Keep or add the imports it needs in that file.\n\n")
            write(out / "given" / f"{name}.py", header + text)
        known_given.add((path[:-3].replace("/", "."), name or "*"))
    for path in ls(n, "tests") + ls(n, "incident/labs"):
        write(out / "checks" / path, show(n, path))

    given_names = {(m, d) for m, d in known_given}
    whole = {m for m, d in known_given if d == "*"}
    contract = {m: names for m, names in interfaces(n, given_names).items() if m not in whole}
    lines = [f"# Lesson {nn} check pack", ""]
    if items:
        lines += ["## Given files", "",
                  "Copy these into your project unchanged. They are data and test doubles that",
                  "everyone shares, so results are comparable; they are not what this lesson teaches.",
                  ""]
        for path, name, _, changed in items:
            if name is None:
                lines.append(f"- `given/{path}`: copy to `{path}`.")
            else:
                if changed:
                    lines.append(f"- `given/{name}.py`: replace `{name}` in `{path}` with this version.")
                else:
                    lines.append(f"- `given/{name}.py`: add `{name}` to `{path}` in the build step that creates that file.")
        lines.append("")
    lines += ["## Checks", "",
              "Copy `checks/` into your project root unchanged: it holds this lesson's demo in",
              "`incident/labs/` and the tests for this lesson and every earlier one in `tests/`.",
              "This lesson's tests fail until you have built the capability; at first its test file may",
              "fail to import, because the modules it needs do not exist yet. Never edit the tests to",
              "make them pass.", "",
              f"When everything is built, set `LESSON = {n}` in `incident/__init__.py`. The full",
              f"suite should then report **{TEST_COUNTS[n]} passed**, and `python -m incident.lab {n}`",
              "prints the lesson's demo result.", "",
              "## Interfaces your code must provide", "",
              "The checks import these names from your `incident` package. Read the tests to see",
              "how each one is called and what it must return.", ""]
    lines += [f"- `{m}`: " + ", ".join(f"`{x}`" for x in names) for m, names in contract.items()]
    write(out / "README.md", "\n".join(lines) + "\n")


def build_readme():
    write(KIT / "README.md", "\n".join([
        "# Building Agentic Platforms: learner kit",
        "",
        "Everything you need to build your own incident-investigation agent platform, one session at",
        "a time, by prompting your own coding agent. The kit contains no solutions: you build the",
        "platform yourself and prove it with the checks.",
        "",
        "| Folder | What it is |",
        "|---|---|",
        "| `starter/` | The starting project (checkpoint lesson-00). Your coding agent copies it into a new private repository in your course GitLab group. |",
        "| `lessons/NN/given/` | Synthetic data and deterministic test doubles, such as the mock model, that everyone uses unchanged. |",
        "| `lessons/NN/checks/` | The lesson's demo and tests, cumulative. Copy them unchanged; they fail until you build the capability. |",
        "| `lessons/NN/README.md` | What to copy where, and the interfaces your code must provide. |",
        "",
        "The prompts for each session are on the session page your instructor shares, and in the",
        "course's learner prompts. All data is synthetic, and nothing here touches a real system.",
        "",
    ]))


def verify():
    ok = True
    for n in range(1, 13):
        with tempfile.TemporaryDirectory() as tmp:
            top = git("rev-parse", "--show-toplevel").strip()
            subprocess.run(f"git archive {tag_name(n)} | tar -x -C {tmp}", shell=True, cwd=top, check=True)
            shutil.copytree(KIT / "lessons" / f"{n:02d}" / "checks", tmp, dirs_exist_ok=True)
            r = subprocess.run(["uv", "run", "-q", "--python", "3.12", "python", "-m", "pytest", "-q"],
                               cwd=tmp, capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or r.stderr.strip().splitlines() or ["no output"])[-1]
            good = r.returncode == 0 and re.match(rf"{TEST_COUNTS[n]} passed\b", last)
            ok &= bool(good)
            print(f"{n:02d}: {'ok ' if good else 'FAIL'} {last}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if KIT.exists():
        shutil.rmtree(KIT)
    build_readme()
    build_starter()
    known = set()
    for n in range(1, 13):
        build_lesson(n, known)
    print(f"wrote {KIT}")
    if args.verify and not verify():
        sys.exit(1)


if __name__ == "__main__":
    main()
