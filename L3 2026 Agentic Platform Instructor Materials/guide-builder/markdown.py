"""Render an instructor guide as GitHub-flavoured Markdown from the same spec as the .docx.

The Markdown mirrors the .docx section by section and uses the same templates, excerpts,
files-changed list and expected JSON, so the two formats cannot drift apart.
"""

from pathlib import PurePosixPath
from urllib.parse import quote

from guidelib import excerpt, expected_json_text, files_changed, guide_filename

CODE_LANG = {".py": "python", ".js": "javascript", ".css": "css", ".html": "html", ".json": "json"}


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def table(header, rows):
    lines = ["| " + " | ".join(cell(h) for h in header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def code(text, lang=""):
    fence = "````" if "```" in text else "```"
    return f"{fence}{lang}\n{text}\n{fence}"


def build_markdown(spec, common, T, troubleshooting_prompt):
    """Return the guide as Markdown. T renders a lesson template, as in build.py."""
    n = spec["number"]
    L, H = common["labels"], common["headings"]
    out = []
    add = out.append

    def labelled(label, text):
        add(f"**{label.strip()}** {text}")

    def prompt(text):
        add(f"> **{L['prompt'].strip()}** {text}")

    def figures(after):
        for fig in [f for f in spec.get("figures", []) if f["after"] == after]:
            add(f"![{cell(fig['caption'])}](../console-screenshots/{quote(fig['image'])})")
            labelled(L["figure"], fig["caption"])

    # Header
    add(f"# {T('title')}")
    add(f"*{T('subtitle')}*")
    labelled(L["outcome"], spec["outcome"])
    add(T("header"))
    add(f"Word version: [{guide_filename(spec)}]({quote(guide_filename(spec))})")

    if "platform_role" in spec:
        add(f"## {H['platform_map']}")
        add(spec["platform_role"])
        status = lambda k: "Built earlier" if k < n else "**This session**" if k == n else "Later session"
        add(table(common["platform_map_header"],
                  [[f"{k:02d}", name, status(k)] for k, name in common["platform_components"]]))

    # Preparation
    add(f"## {H['preparation']}")
    out.extend(spec["preparation"])
    add(T("access_before") + f"[{T('access_link')}]({T('access_url')})" + T("access_after"))
    add(T("agent_role"))
    prompt(T("prepare_prompt"))
    add(T("orient_intro"))
    prompt(T("orient_prompt"))
    labelled(L["readiness"], T("readiness"))
    out.extend(spec.get("readiness_notes", []))
    labelled(L["offline"], T("offline"))
    add(T("pinned"))

    # Agenda
    add(f"## {H['agenda']}")
    add(table(common["agenda_header"], spec.get("agenda") or common["agenda"][str(spec["duration"])]))

    # Instructor script
    add(f"## {H['script']}")
    add(T("script_intro"))
    add(f"### {H['opening']}")
    labelled(L["say"], spec["opening_say"])
    labelled(L["show"], T("opening_show"))
    add(f"### {H['concept']}")
    labelled(L["say"], spec["concept_say"])
    labelled(L["pause"], T("concept_pause"))
    figures("concept")
    for k, step in enumerate(spec["steps"], 1):
        ex = step["excerpt"]
        path = ex.get("file", step["file"])
        add(f"### {T('step_heading', k=k, step_title=step['title'])}")
        labelled(L["say"], step["say"])
        labelled(L["show"], T("step_show", file=f"`{step['file']}`"))
        prompt(T("step_prompt", body=step["prompt"]))
        labelled(L["review"], T("review", start=ex["start"], end=ex["end"]))
        add(code(excerpt(n, path, ex["start"], ex["end"]), CODE_LANG.get(PurePosixPath(path).suffix, "")))
        labelled(L["explain"], step["explain"])
        labelled(L["ask"], step["ask"])
        labelled(L["answer"], step["answer"])
        labelled(L["pause"], step.get("pause") or T("step_pause"))
        figures(f"step{k}")

    # Learner practice
    add(f"## {H['practice_checkpoints']}")
    prompt(T("exercise_prompt", body=spec["exercise"]))
    labelled(L["verify"], T("verify"))
    prompt(T("verify_prompt"))
    labelled(L["expected"], T("expected_behaviour"))
    add(code(expected_json_text(spec), "json"))
    labelled(L["pause"], T("practice_pause"))
    figures("practice")

    # Completion and files changed
    add(f"## {H['completion']}")
    add("\n".join(f"- {c}" for c in spec["completion_criteria"]))
    result = spec["recorded_test_result"]
    add(T("recorded", passed=result["passed"], seconds=result["seconds"]))
    add(f"### {H['files_changed']}")
    add(T("files_intro"))
    add("\n".join(f"- `{f}`" for f in files_changed(n)))
    prompt(T("review_prompt"))

    # Troubleshooting
    add(f"## {H['troubleshooting']}")
    for entry in spec["troubleshooting"]:
        add(f"### {entry['heading']}")
        prompt(troubleshooting_prompt(entry, T))

    # Practice, scope, close, references
    add(f"## {H['practice']}")
    add("\n".join(f"- {p}" for p in spec["practice"]))
    labelled(L["discussion"], T("discussion"))
    add(f"## {H['verification_scope']}")
    for item in spec["verification_scope"]:
        add(common["verification_scope"][item[1:]] if item.startswith("@") else item)
    add(f"## {H['close']}")
    labelled(L["say"], spec["close_say"])
    add(f"## {H['references']}")
    add("\n".join(f"- [{r['title']}]({r['url']})" for r in spec["references"]))
    return "\n\n".join(out) + "\n"


def build_index(specs, common):
    """README for the instructor-guides folder: one row per session."""
    rows = []
    for spec in specs:
        name = guide_filename(spec)
        md = name[:-len(".docx")] + ".md"
        rows.append([f"{spec['number']:02d}", f"[{spec['title']}]({quote(md)})", spec["duration"],
                     f"[.docx]({quote(name)})"])
    total = sum(s["duration"] for s in specs)
    return "\n\n".join([
        "# Instructor guides",
        "One guide per session of *Building Agentic Platforms*. Each guide is published twice from the same "
        "source: a Word document for printing and sharing, and a Markdown page for reading on GitHub. Both are "
        "generated by [`guide-builder`](../guide-builder/README.md) from `guide-builder/specs/`; edit the specs, "
        "not these files.",
        table(["#", "Session", "Minutes", "Word"], rows),
        f"Total: {len(specs)} sessions, {total} minutes. Learner prompts for every session are in "
        "[`LEARNER_PROMPTS.md`](../incident-platform/LEARNER_PROMPTS.md).",
    ]) + "\n"
