"""Check a session page against the learner kit: full file paths, and the completion criteria quoted verbatim.

    python3 check_paths.py 05            # one page
    python3 check_paths.py 04 05         # several

Homework checkers read the pages literally: a bare "core.py", or a file indented under a folder in a tree,
reads as a required file at the project root. So every file a page names must be a full path from the
learner project's root, and that path must be one the kit knows for this lesson or an earlier one:

- a file in learner-kit/starter, or in a lesson's given/ or checks/ folder (at its place in the project);
- a module the lesson READMEs list under "Interfaces your code must provide" (agent_runtime.core means
  agent_runtime/core.py, course means course/__init__.py);
- a file in this lesson's kit folder, written as given/... or checks/...;
- a path in ALLOWED below (files the prompts create that no interface names, and course-repository files).

The page must also quote every line of the lesson README's "Completion criteria" word for word.

Only the page's visible text is checked, not its links, styles or script. Exit status 1 on any problem.
"""
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent.parent / "learner-kit"
EXT = r"(?:py|js|md|json|toml|env|css|html)"
TOKEN = re.compile(r"(?<![\w./~-])((?:~/)?[\w.-]+(?:/[\w.-]+)*\." + EXT + r")(?![\w/])")
ALLOWED = {
    "AGENTS.md", "README.md", "pyproject.toml", "uv.lock",       # the learner project's root files
    "LEARNER_PROMPTS.md",                                         # the course repository's prompts file
    "~/agentic-course/groq.env",                                  # the learner's key file, outside the project
    "var/evaluation.json",                                        # a file a lesson writes under var/
}


def known_paths(n):
    paths = {str(p.relative_to(KIT / "starter")) for p in (KIT / "starter").rglob("*") if p.is_file()}
    for lesson in sorted((KIT / "lessons").iterdir()):
        if not lesson.name.isdigit() or int(lesson.name) > n:
            continue
        for part in ("given", "checks"):
            root = lesson / part
            if root.is_dir():
                paths |= {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
        readme = (lesson / "README.md").read_text(encoding="utf-8")
        for module in re.findall(r"^- `([\w.]+)`: ", readme, re.M):
            parts = module.split(".")
            paths.add("/".join(parts) + ".py")
            paths.add("/".join(parts) + "/__init__.py")
    return paths


def page_for(n):
    pages = sorted(HERE.glob(f"{n:02d}-*.html"))
    pages = [p for p in pages if not p.name.endswith("-just-prompts.html")]
    return pages[0]


def visible_text(page):
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def check(n):
    page = page_for(n)
    known = known_paths(n) | ALLOWED
    problems = []
    for name in sorted(set(TOKEN.findall(visible_text(page.read_text(encoding="utf-8"))))):
        if name.startswith(("learner-kit/", "L3 2026")):
            continue  # a path in the course repository, not the learner's project
        if name.startswith(("given/", "checks/")):
            if not (KIT / "lessons" / f"{n:02d}" / name).is_file():
                problems.append(f"{name!r} is not in learner-kit/lessons/{n:02d}")
            continue  # a file in this lesson's kit folder
        if "/" not in name and name not in ALLOWED:
            problems.append(f"bare file name {name!r}: write its full path from the project root")
        elif name not in known:
            problems.append(f"{name!r} is not a file the kit knows by lesson {n:02d}")
    readme = (KIT / "lessons" / f"{n:02d}" / "README.md").read_text(encoding="utf-8")
    criteria = readme.split("## Completion criteria", 1)[-1].split("\n## ", 1)[0]
    text = " ".join(visible_text(page.read_text(encoding="utf-8")).split())
    for criterion in re.findall(r"^- (.+)$", criteria, re.M):
        if " ".join(criterion.split()) not in text:
            problems.append(f"completion criterion not quoted word for word: {criterion!r}")
    print(f"{page.name}: {'ok' if not problems else str(len(problems)) + ' problem(s)'}")
    for p in problems:
        print("  -", p)
    return not problems


if __name__ == "__main__":
    ok = all([check(int(a)) for a in sys.argv[1:]])
    sys.exit(0 if ok else 1)
