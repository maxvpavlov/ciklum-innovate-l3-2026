"""Round-trip proof: extract the current guides, rebuild them into a work directory, compare.

Usage:
    uv run --with python-docx python roundtrip.py --work DIR

Nothing outside DIR is written. For each guide it compares, against the original:
  * the sequence of (style name, full paragraph text), including table cell texts;
  * hyperlink texts and URLs;
  * every part of the .docx package, byte for byte (zip timestamps are ignored).
LEARNER_PROMPTS.md must be byte-identical. It also reports whether the checked-in
specs/ differ from the freshly extracted ones. Exits non-zero on any mismatch.
"""

import argparse
import filecmp
import sys
import zipfile
from pathlib import Path

from build import build_all
from extract import extract_all
from guidelib import GUIDES_DIR, LESSONS, PROMPTS_FILE, SPECS_DIR, read_blocks


def sequence(path):
    """(style, text) per paragraph; tables contribute one entry per cell."""
    seq = []
    for b in read_blocks(path):
        if b["kind"] == "p":
            seq.append((b["style"], b["text"]))
        else:
            seq += [("table-cell", cell) for row in b["rows"] for cell in row]
    return seq


def links(path):
    return [(r["text"], r["url"]) for b in read_blocks(path) if b["kind"] == "p"
            for r in b["runs"] if r["url"]]


def part_differences(a, b):
    with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
        names_a, names_b = set(za.namelist()), set(zb.namelist())
        diffs = [f"only in original: {n}" for n in sorted(names_a - names_b)]
        diffs += [f"only in rebuilt: {n}" for n in sorted(names_b - names_a)]
        diffs += [f"part differs: {n}" for n in sorted(names_a & names_b)
                  if za.read(n) != zb.read(n)]
    return diffs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--work", required=True, help="scratch directory for specs and outputs")
    ap.add_argument("--guides", default=str(GUIDES_DIR))
    ap.add_argument("--prompts", default=str(PROMPTS_FILE))
    args = ap.parse_args()
    work = Path(args.work)
    quiet = lambda *_: None  # noqa: E731

    if not extract_all(args.guides, args.prompts, work / "specs", log=print):
        sys.exit(1)
    build_all(work / "specs", work / "guides", work / "LEARNER_PROMPTS.md", log=quiet)

    ok = True
    for n in LESSONS:
        original = next(Path(args.guides).glob(f"{n:02d} *.docx"))
        rebuilt = work / "guides" / original.name
        problems = []
        if not rebuilt.exists():
            problems.append(f"not rebuilt under the same filename: {original.name}")
        else:
            sa, sb = sequence(original), sequence(rebuilt)
            if sa != sb:
                i = next((i for i, (x, y) in enumerate(zip(sa, sb)) if x != y),
                         min(len(sa), len(sb)))
                problems.append(f"paragraph sequence differs at item {i}: "
                                f"{sa[i:i + 1]} vs {sb[i:i + 1]}")
            if links(original) != links(rebuilt):
                problems.append("hyperlinks differ")
            problems += part_differences(original, rebuilt)
        print(f"{n:02d}: {'match' if not problems else 'MISMATCH'}  {original.name}")
        for p in problems:
            print(f"    {p}")
        ok = ok and not problems

    same = Path(args.prompts).read_bytes() == (work / "LEARNER_PROMPTS.md").read_bytes()
    print(f"LEARNER_PROMPTS.md: {'byte-identical' if same else 'MISMATCH'}")
    ok = ok and same

    stale = [p.name for p in sorted((work / "specs").glob("*.json"))
             if not (SPECS_DIR / p.name).exists()
             or not filecmp.cmp(p, SPECS_DIR / p.name, shallow=False)]
    print("checked-in specs: " + ("up to date" if not stale else f"differ: {', '.join(stale)}"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
