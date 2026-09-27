"""Parse the existing instructor guides into structured specs (specs/NN.json).

Usage:
    uv run --with python-docx python extract.py [--guides DIR] [--prompts FILE] [--out DIR]

Boilerplate that matches specs/_common.json is left out of the spec. Where a guide
deviates from a template, the literal text is stored under "overrides" so the builder
still reproduces it. Facts the builder derives (tag hash, code excerpts, files changed)
are checked here against git and not stored.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from guidelib import (COMMON_FILE, GUIDES_DIR, LESSONS, PROMPTS_FILE, SPECS_DIR, excerpt,
                      expected_json_text, files_changed, git, lesson_vars, load_json,
                      read_blocks, tag_file_lines, tag_hash, write_json)


class ParseError(Exception):
    pass


class Reader:
    """Cursor over a guide's blocks with small expectation helpers."""

    def __init__(self, blocks, common, n):
        self.blocks = blocks
        self.i = 0
        self.common = common
        self.labels = common["labels"]
        self.headings = common["headings"]
        self.vars = lesson_vars(n)
        self.overrides = {}
        self.warnings = []

    def peek(self):
        return self.blocks[self.i] if self.i < len(self.blocks) else None

    def next(self):
        block = self.peek()
        if block is None:
            raise ParseError("unexpected end of document")
        self.i += 1
        return block

    def para(self, style="Normal"):
        block = self.next()
        if block["kind"] != "p" or block["style"] != style:
            raise ParseError(f"expected {style} paragraph at block {self.i - 1}, got {block}")
        return block

    def heading(self, key, level=1):
        block = self.para(f"Heading {level}")
        if block["text"] != self.headings[key]:
            raise ParseError(f"expected heading {self.headings[key]!r}, got {block['text']!r}")

    def labelled(self, label_key, style="Normal"):
        block = self.para(style)
        label = self.labels[label_key]
        runs = block["runs"]
        if not runs or not runs[0]["bold"] or runs[0]["text"] != label:
            raise ParseError(f"expected label {label!r} at block {self.i - 1}: "
                             f"{block['text'][:80]!r}")
        return "".join(r["text"] for r in runs[1:])

    def is_labelled(self, label_key):
        block = self.peek()
        return (block is not None and block["kind"] == "p" and block["runs"]
                and block["runs"][0]["bold"] and block["runs"][0]["text"] == self.labels[label_key])

    def is_style(self, style):
        block = self.peek()
        return block is not None and block["kind"] == "p" and block["style"] == style

    def boilerplate(self, key, text, **extra):
        """Compare text with a template; record an override for this lesson if different."""
        tmpl = self.common["templates"][key]
        if tmpl.format(**self.vars, **extra) != text:
            self.overrides[key] = text

    def match(self, key, text, *fields):
        """Match text against a template with open {fields}; return their values or None."""
        return match_template(self.common["templates"][key], text, self.vars, fields)


def match_template(tmpl, text, values, fields):
    """Fields of `tmpl` named in `fields` become lazy groups; other placeholders are filled."""
    sentinels = {f: f"\x00{i}\x00" for i, f in enumerate(fields)}
    pattern = re.escape(tmpl.format(**values, **sentinels))
    for field, sentinel in sentinels.items():
        pattern = pattern.replace(re.escape(sentinel), f"(?P<{field}>.+?)")
    m = re.fullmatch(pattern, text, re.S)
    return m.groupdict() if m else None


def find_excerpt(n, text, show_file, start, end):
    """Locate which file at lesson-n holds the excerpt; prefer the SHOW file."""
    if excerpt(n, show_file, start, end) == text:
        return show_file
    listing = git("ls-tree", "-r", "--name-only", f"lesson-{n:02d}")
    for path in listing.splitlines():
        if path.endswith(".py"):
            lines = tag_file_lines(n, path)
            if end <= len(lines) and excerpt(n, path, start, end) == text:
                return path
    raise ParseError(f"excerpt lines {start}-{end} not found at lesson-{n:02d}")


def parse_guide(path, n, common):
    r = Reader(read_blocks(path), common, n)
    spec = {"number": n}

    title = r.para("Title")["text"]
    m = r.match("title", title, "title")
    if not m:
        raise ParseError(f"bad title {title!r}")
    spec["title"] = m["title"]
    r.boilerplate("subtitle", r.para()["text"])
    spec["outcome"] = r.labelled("outcome")

    header = r.para()["text"]
    m = r.match("header", header, "duration", "hash")
    if not m:
        raise ParseError(f"bad header {header!r}")
    spec["duration"] = int(m["duration"])
    hash_ = m["hash"]
    if hash_ != tag_hash(n):
        r.warnings.append(f"header hash {hash_} != git {tag_hash(n)}")

    # Preparation: lesson paragraphs, then the access paragraph with the hyperlink.
    r.heading("preparation")
    spec["preparation"] = []
    while not any(run["url"] for run in r.peek()["runs"]):
        spec["preparation"].append(r.para()["text"])
    runs = r.para()["runs"]
    if len(runs) != 3:
        raise ParseError("access paragraph shape changed")
    for key, run in zip(["access_before", "access_link", "access_after"], runs):
        r.boilerplate(key, run["text"])
    r.boilerplate("access_url", runs[1]["url"])
    r.boilerplate("agent_role", r.para()["text"])
    r.boilerplate("prepare_prompt", r.labelled("prompt", "Agent Prompt"))
    r.boilerplate("orient_intro", r.para()["text"])
    r.boilerplate("orient_prompt", r.labelled("prompt", "Agent Prompt"))
    r.boilerplate("readiness", r.labelled("readiness"))
    notes = []
    while not r.is_labelled("offline"):
        notes.append(r.para()["text"])
    if notes:
        spec["readiness_notes"] = notes
    r.boilerplate("offline", r.labelled("offline"))
    r.boilerplate("pinned", r.para()["text"])

    # Agenda table; the default for the duration is used unless overridden.
    r.heading("agenda")
    table = r.next()
    if table["kind"] != "tbl":
        raise ParseError("agenda table missing")
    if table["rows"][0] != common["agenda_header"]:
        raise ParseError("agenda header changed")
    rows = table["rows"][1:]
    if rows != common["agenda"].get(str(spec["duration"])):
        spec["agenda"] = rows
    if r.para()["text"] != "":
        raise ParseError("expected empty paragraph after the agenda")

    r.heading("script")
    r.boilerplate("script_intro", r.para()["text"])
    r.heading("opening", 2)
    spec["opening_say"] = r.labelled("say")
    r.boilerplate("opening_show", r.labelled("show"))
    r.heading("concept", 2)
    spec["concept_say"] = r.labelled("say")
    r.boilerplate("concept_pause", r.labelled("pause"))

    # Four build steps.
    spec["steps"] = []
    for k in range(1, 5):
        step = {}
        heading = r.para("Heading 2")["text"]
        m = match_template(common["templates"]["step_heading"], heading, {"k": k},
                           ["step_title"])
        if not m:
            raise ParseError(f"bad step heading {heading!r}")
        step["title"] = m["step_title"]
        step["say"] = r.labelled("say")
        show = r.labelled("show")
        m = r.match("step_show", show, "file")
        if not m:
            raise ParseError(f"step {k} SHOW does not match the template: {show!r}")
        step["file"] = m["file"]
        prompt = r.labelled("prompt", "Agent Prompt")
        m = r.match("step_prompt", prompt, "body")
        if not m:
            raise ParseError(f"step {k} prompt frame differs: {prompt!r}")
        step["prompt"] = m["body"]
        review = r.labelled("review")
        m = r.match("review", review, "start", "end")
        if not m:
            raise ParseError(f"step {k} REVIEW text differs: {review!r}")
        start, end = int(m["start"]), int(m["end"])
        code = r.para("Code")["text"]
        excerpt_file = find_excerpt(n, code, step["file"], start, end)
        step["excerpt"] = {"start": start, "end": end}
        if excerpt_file != step["file"]:
            step["excerpt"]["file"] = excerpt_file
        step["explain"] = r.labelled("explain")
        step["ask"] = r.labelled("ask")
        step["answer"] = r.labelled("answer")
        pause = r.labelled("pause")
        if pause != common["templates"]["step_pause"]:
            step["pause"] = pause
        spec["steps"].append(step)

    # Learner practice.
    r.heading("practice_checkpoints")
    prompt = r.labelled("prompt", "Agent Prompt")
    m = r.match("exercise_prompt", prompt, "body")
    if not m:
        raise ParseError(f"exercise prompt frame differs: {prompt!r}")
    spec["exercise"] = m["body"]
    r.boilerplate("verify", r.labelled("verify"))
    r.boilerplate("verify_prompt", r.labelled("prompt", "Agent Prompt"))
    r.boilerplate("expected_behaviour", r.labelled("expected"))
    expected = r.para("Code")["text"]
    spec["expected_json"] = json.loads(expected)
    if expected_json_text(spec) != expected:
        raise ParseError("expected JSON does not round-trip through json.dumps(indent=2)")
    r.boilerplate("practice_pause", r.labelled("pause"))

    r.heading("completion")
    spec["completion_criteria"] = []
    while r.is_style("List Bullet"):
        spec["completion_criteria"].append(r.para("List Bullet")["text"])
    recorded = r.para()["text"]
    m = re.search(r"Recorded test result: (\d+) passed in ([\d.]+)s\.", recorded)
    spec["recorded_test_result"] = {"passed": int(m.group(1)), "seconds": m.group(2)}
    r.boilerplate("recorded", recorded, hash=hash_, passed=m.group(1), seconds=m.group(2))

    r.heading("files_changed", 2)
    r.boilerplate("files_intro", r.para()["text"])
    listed = []
    while r.is_style("List Bullet"):
        listed.append(r.para("List Bullet")["text"])
    if listed != files_changed(n):
        r.warnings.append(f"files changed list {listed} != git diff {files_changed(n)}")
    r.boilerplate("review_prompt", r.labelled("prompt", "Agent Prompt"))

    r.heading("troubleshooting")
    spec["troubleshooting"] = []
    while r.is_style("Heading 2"):
        entry = {"heading": r.para("Heading 2")["text"]}
        prompt = r.labelled("prompt", "Agent Prompt")
        m = r.match("recovery_prompt", prompt, "symptom", "diagnostic", "recovery")
        if m:
            entry["diagnostic"], entry["recovery"] = m["diagnostic"], m["recovery"]
            if m["symptom"] != entry["heading"] + ".":
                entry["symptom"] = m["symptom"]
        else:
            entry["prompt"] = prompt
        spec["troubleshooting"].append(entry)

    r.heading("practice")
    spec["practice"] = []
    while r.is_style("List Bullet"):
        spec["practice"].append(r.para("List Bullet")["text"])
    r.boilerplate("discussion", r.labelled("discussion"))

    r.heading("verification_scope")
    scope_keys = {v: k for k, v in common["verification_scope"].items()}
    spec["verification_scope"] = []
    while r.is_style("Normal"):
        text = r.para()["text"]
        spec["verification_scope"].append("@" + scope_keys[text] if text in scope_keys else text)

    r.heading("close")
    spec["close_say"] = r.labelled("say")

    r.heading("references")
    spec["references"] = []
    while r.is_style("List Bullet"):
        runs = r.para("List Bullet")["runs"]
        if len(runs) != 1 or not runs[0]["url"]:
            raise ParseError("reference is not a single hyperlink")
        spec["references"].append({"title": runs[0]["text"], "url": runs[0]["url"]})
    if r.peek() is not None:
        raise ParseError(f"unexpected trailing content: {r.peek()}")

    if r.overrides:
        spec["overrides"] = r.overrides
    return spec, r.warnings


def parse_prompts_titles(prompts_file):
    """Lesson titles as written in LEARNER_PROMPTS.md ("## 03. Context, retrieval and memory")."""
    titles = {}
    for line in Path(prompts_file).read_text(encoding="utf-8").splitlines():
        m = re.fullmatch(r"## (\d\d)\. (.+)", line)
        if m:
            titles[int(m.group(1))] = m.group(2)
    return titles


def reorder(spec):
    """Stable, readable key order for the JSON file."""
    order = ["number", "title", "guide_title", "duration", "outcome", "preparation",
             "readiness_notes", "agenda", "opening_say", "concept_say", "steps", "exercise",
             "expected_json", "completion_criteria", "recorded_test_result", "troubleshooting",
             "practice", "verification_scope", "close_say", "references", "overrides"]
    return {k: spec[k] for k in order if k in spec}


def extract_all(guides_dir=GUIDES_DIR, prompts_file=PROMPTS_FILE, out_dir=SPECS_DIR,
                log=print):
    """Write specs/NN.json for every guide; return True when all 12 parsed."""
    common = load_json(COMMON_FILE)
    md_titles = parse_prompts_titles(prompts_file)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ok = True
    for n in LESSONS:
        matches = sorted(Path(guides_dir).glob(f"{n:02d} *.docx"))
        if len(matches) != 1:
            log(f"{n:02d}: expected one guide, found {matches}")
            ok = False
            continue
        try:
            spec, warnings = parse_guide(matches[0], n, common)
        except ParseError as exc:
            log(f"{n:02d}: parse error: {exc}")
            ok = False
            continue
        # The canonical title is the one used in LEARNER_PROMPTS.md (and the workbook).
        if md_titles.get(n) and md_titles[n] != spec["title"]:
            spec["guide_title"] = spec["title"]
            spec["title"] = md_titles[n]
        write_json(out / f"{n:02d}.json", reorder(spec))
        overrides = ", ".join(spec.get("overrides", {}))
        log(f"{n:02d}: ok" + (f" (overrides: {overrides})" if overrides else ""))
        for w in warnings:
            log(f"    warning: {w}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--guides", default=str(GUIDES_DIR), help="directory holding the guides")
    ap.add_argument("--prompts", default=str(PROMPTS_FILE), help="LEARNER_PROMPTS.md (for titles)")
    ap.add_argument("--out", default=str(SPECS_DIR), help="directory for NN.json specs")
    args = ap.parse_args()
    sys.exit(0 if extract_all(args.guides, args.prompts, args.out) else 1)


if __name__ == "__main__":
    main()
