"""Validate guide-repo coupling for a set of guides and a LEARNER_PROMPTS.md.

Usage:
    uv run --with python-docx python check.py [--guides DIR] [--prompts FILE] [--specs DIR]

Checks, per lesson:
  * the header names lesson-(N-1) and lesson-N, and its hash equals `git rev-parse` of the tag
    (as does the hash in the "Recorded test result" paragraph);
  * exactly 13 PROMPT paragraphs, all present verbatim, in order, in that lesson's section of
    LEARNER_PROMPTS.md (and that section holds no other prompts);
  * exactly 4 REVIEW excerpts, each citing lesson-N, whose Code paragraph equals the dedented
    source lines at the tag (file = the step's SHOW file, or the spec's excerpt.file);
  * the "Files changed in this checkpoint" bullets equal `git diff --name-only`;
  * the expected-behaviour block is valid JSON.
Exits non-zero when any check fails.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from guidelib import (GUIDES_DIR, LESSONS, PROMPTS_FILE, SPECS_DIR, excerpt, files_changed,
                      labelled, load_common, read_blocks, tag_hash, tag_name)


def prompts_by_lesson(prompts_file):
    """{lesson number: [prompt text, ...]} from the '> ' lines of LEARNER_PROMPTS.md."""
    sections, current = {}, None
    for line in Path(prompts_file).read_text(encoding="utf-8").splitlines():
        m = re.fullmatch(r"## (\d\d)\. .+", line)
        if m:
            current = sections.setdefault(int(m.group(1)), [])
        elif line.startswith("> ") and current is not None:
            current.append(line[2:])
    return sections


def excerpt_file_override(specs_dir, n, step_index):
    path = Path(specs_dir) / f"{n:02d}.json"
    if path.exists():
        steps = json.loads(path.read_text(encoding="utf-8")).get("steps", [])
        if step_index < len(steps):
            return steps[step_index].get("excerpt", {}).get("file")
    return None


def check_guide(path, n, md_prompts, common, specs_dir):
    errors = []
    blocks = read_blocks(path)
    labels = common["labels"]
    tag, prev = tag_name(n), tag_name(n - 1)
    short = tag_hash(n)

    # Header and recorded-result hash.
    header = next((b["text"] for b in blocks if b["kind"] == "p"
                   and b["text"].startswith("Duration: ")), "")
    m = re.fullmatch(r"Duration: \d+ minutes\. Starting checkpoint: (\S+)\. "
                     r"Ending checkpoint: (\S+) \((\w+)\)\.", header)
    if not m:
        errors.append(f"header not found or malformed: {header!r}")
    elif (m.group(1), m.group(2), m.group(3)) != (prev, tag, short):
        errors.append(f"header {m.groups()} != expected {(prev, tag, short)}")
    for b in blocks:
        if b["kind"] == "p" and "Recorded test result:" in b["text"]:
            if f"{tag} ({short})" not in b["text"]:
                errors.append(f"recorded-result paragraph does not cite {tag} ({short})")

    # Prompts.
    prompts = [text for b in blocks if b["kind"] == "p" and b["style"] == "Agent Prompt"
               for label, text in [labelled(b)] if label == labels["prompt"]]
    spec = json.loads((Path(specs_dir) / f"{n:02d}.json").read_text(encoding="utf-8"))
    expected = 13 + ("layout_prompt" in spec)
    if len(prompts) != expected:
        errors.append(f"{len(prompts)} PROMPT paragraphs, expected {expected}")
    if prompts != md_prompts:
        missing = [p for p in prompts if p not in md_prompts]
        extra = [p for p in md_prompts if p not in prompts]
        for p in missing:
            errors.append(f"prompt missing from LEARNER_PROMPTS.md: {p[:90]!r}")
        for p in extra:
            errors.append(f"LEARNER_PROMPTS.md prompt not in guide: {p[:90]!r}")
        if not missing and not extra:
            errors.append("prompts appear in a different order in LEARNER_PROMPTS.md")

    # Code excerpts: REVIEW paragraph, then a Code paragraph; SHOW names the file.
    show_file, reviews = None, 0
    for i, b in enumerate(blocks):
        label, text = labelled(b) if b["kind"] == "p" else (None, None)
        if label == labels["show"]:
            m = re.search(r"implementation and (\S+)\. Use the following", text)
            show_file = m.group(1) if m else None
        if label != labels["review"]:
            continue
        m = re.search(r"source lines (\d+) to (\d+) at (lesson-\d\d);", text)
        if not m:
            errors.append(f"REVIEW without a line range: {text[:80]!r}")
            continue
        start, end, cited = int(m.group(1)), int(m.group(2)), m.group(3)
        if cited != tag:
            errors.append(f"REVIEW {reviews + 1} cites {cited}, expected {tag}")
        code = blocks[i + 1] if i + 1 < len(blocks) else None
        if not code or code["kind"] != "p" or code["style"] != "Code":
            errors.append(f"REVIEW {reviews + 1} is not followed by a Code paragraph")
        else:
            file = excerpt_file_override(specs_dir, n, reviews) or show_file
            if not file:
                errors.append(f"REVIEW {reviews + 1} has no SHOW file")
            elif code["text"] != excerpt(n, file, start, end):
                errors.append(f"REVIEW {reviews + 1}: excerpt differs from {file} "
                              f"lines {start}-{end} at {tag}")
        reviews += 1
    if reviews != 4:
        errors.append(f"{reviews} REVIEW excerpts, expected 4")

    # Files changed.
    heading = common["headings"]["files_changed"]
    idx = next((i for i, b in enumerate(blocks) if b["kind"] == "p"
                and b["style"] == "Heading 2" and b["text"] == heading), None)
    if idx is None:
        errors.append("files-changed heading missing")
    else:
        listed = []
        for b in blocks[idx + 2:]:
            if b["kind"] != "p" or b["style"] != "List Bullet":
                break
            listed.append(b["text"])
        if listed != files_changed(n):
            errors.append(f"files changed {listed} != git diff {files_changed(n)}")

    # Expected JSON (the Code paragraph after "Expected behaviour").
    for i, b in enumerate(blocks):
        if b["kind"] == "p" and labelled(b)[0] == labels["expected"]:
            try:
                json.loads(blocks[i + 1]["text"])
            except (ValueError, IndexError, KeyError):
                errors.append("expected-behaviour block is not valid JSON")
    return errors


def check_all(guides_dir=GUIDES_DIR, prompts_file=PROMPTS_FILE, specs_dir=SPECS_DIR, log=print):
    common = load_common()
    md = prompts_by_lesson(prompts_file)
    ok = True
    if sorted(md) != list(LESSONS):
        log(f"LEARNER_PROMPTS.md lesson sections: {sorted(md)}")
        ok = False
    for n in LESSONS:
        matches = sorted(Path(guides_dir).glob(f"{n:02d} *.docx"))
        if len(matches) != 1:
            log(f"{n:02d}: expected one guide, found {len(matches)}")
            ok = False
            continue
        errors = check_guide(matches[0], n, md.get(n, []), common, specs_dir)
        log(f"{n:02d}: {'ok' if not errors else 'FAIL'}  {matches[0].name}")
        for e in errors:
            log(f"    {e}")
        ok = ok and not errors
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--guides", default=str(GUIDES_DIR))
    ap.add_argument("--prompts", default=str(PROMPTS_FILE))
    ap.add_argument("--specs", default=str(SPECS_DIR), help="for excerpt.file overrides")
    args = ap.parse_args()
    sys.exit(0 if check_all(args.guides, args.prompts, args.specs) else 1)


if __name__ == "__main__":
    main()
