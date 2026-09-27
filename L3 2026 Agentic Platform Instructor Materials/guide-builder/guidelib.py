"""Shared helpers for the instructor-guide builder: paths, git access, specs and docx reading.

extract.py, build.py and check.py all import this module. It has no dependency beyond
python-docx (run the scripts with `uv run --with python-docx python ...`).
"""

import json
import subprocess
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATERIALS = HERE.parent
GUIDES_DIR = MATERIALS / "instructor-guides"
PROMPTS_FILE = MATERIALS / "incident-platform" / "LEARNER_PROMPTS.md"
SPECS_DIR = HERE / "specs"
COMMON_FILE = SPECS_DIR / "_common.json"
LESSONS = range(1, 13)


# ---------------------------------------------------------------- git

def git(*args):
    """Run git in this repository and return stdout (text, trailing newline kept)."""
    return subprocess.run(["git", *args], cwd=HERE, check=True,
                          capture_output=True, text=True).stdout


def tag_name(n):
    return f"lesson-{n:02d}"


def tag_hash(n):
    """Short commit hash of a lesson tag, as quoted in the guide header."""
    return git("rev-parse", "--short=7", tag_name(n) + "^{commit}").strip()


def tag_file_lines(n, path):
    """Lines of a file at a lesson tag (tags hold the platform at tree root)."""
    return git("show", f"{tag_name(n)}:{path}").split("\n")


def files_changed(n):
    """Sorted paths changed between lesson-(n-1) and lesson-n."""
    out = git("diff", "--name-only", tag_name(n - 1), tag_name(n))
    return sorted(line for line in out.splitlines() if line)


def excerpt(n, path, start, end):
    """Source lines start..end (1-based, inclusive) at lesson-n, common indentation removed."""
    lines = tag_file_lines(n, path)[start - 1:end]
    return textwrap.dedent("\n".join(lines))


# ---------------------------------------------------------------- specs

def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def to_json(data, indent=0):
    """json.dumps(indent=2), except short lists of scalars stay on one line."""
    pad, inner = "  " * indent, "  " * (indent + 1)
    if isinstance(data, dict) and data:
        items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: {to_json(v, indent + 1)}"
                 for k, v in data.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(data, list) and data:
        flat = json.dumps(data, ensure_ascii=False)
        if all(not isinstance(x, (dict, list)) for x in data) and len(flat) + len(inner) <= 100:
            return flat
        return "[\n" + ",\n".join(inner + to_json(x, indent + 1) for x in data) + "\n" + pad + "]"
    return json.dumps(data, ensure_ascii=False)


def write_json(path, data):
    Path(path).write_text(to_json(data) + "\n", encoding="utf-8")


def load_common():
    return load_json(COMMON_FILE)


def load_spec(n, specs_dir=SPECS_DIR):
    return load_json(Path(specs_dir) / f"{n:02d}.json")


def guide_title(spec):
    """Title shown in the guide: the canonical title, as in the workbook and prompts file."""
    return spec["title"]


def guide_filename(spec):
    """Guide filenames drop commas and colons from the canonical title."""
    return f"{spec['number']:02d} {spec['title'].replace(',', '').replace(':', '')}.docx"


def lesson_vars(n):
    """Placeholder values shared by every template for lesson n."""
    return {
        "n": n,
        "nn": f"{n:02d}",
        "tag": tag_name(n),
        "prev_tag": tag_name(n - 1),
    }


def template(common, spec, key):
    """A boilerplate template, unless the spec overrides it for this lesson."""
    return spec.get("overrides", {}).get(key, common["templates"][key])


def expected_json_text(spec):
    return json.dumps(spec["expected_json"], indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- docx reading

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _run_text(r):
    parts = []
    for child in r:
        if child.tag == W + "t":
            parts.append(child.text or "")
        elif child.tag in (W + "br", W + "cr"):
            parts.append("\n")
        elif child.tag == W + "tab":
            parts.append("\t")
    return "".join(parts)


def _run_bold(r):
    rpr = r.find(W + "rPr")
    return rpr is not None and rpr.find(W + "b") is not None


def read_blocks(path):
    """Read a guide into a flat list of blocks.

    Paragraph: {"kind": "p", "style", "text", "runs": [{"text", "bold", "url"}]}.
    Table:     {"kind": "tbl", "rows": [[cell text, ...], ...]}.
    """
    import docx  # imported lazily so git-only helpers work without python-docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = docx.Document(str(path))
    rels = doc.part.rels
    blocks = []
    for el in doc.element.body.iterchildren():
        if el.tag == W + "p":
            runs = []
            for child in el.iterchildren():
                if child.tag == W + "r":
                    runs.append({"text": _run_text(child), "bold": _run_bold(child), "url": None})
                elif child.tag == W + "hyperlink":
                    url = rels[child.get(R_ID)].target_ref
                    text = "".join(_run_text(r) for r in child.iter(W + "r"))
                    runs.append({"text": text, "bold": False, "url": url})
            style = Paragraph(el, doc).style.name
            blocks.append({"kind": "p", "style": style, "runs": runs,
                           "text": "".join(r["text"] for r in runs)})
        elif el.tag == W + "tbl":
            table = Table(el, doc)
            blocks.append({"kind": "tbl", "style": table.style.name if table.style else None,
                           "rows": [[c.text for c in row.cells] for row in table.rows]})
    return blocks


def labelled(block):
    """Split a paragraph whose first run is a bold label ("SAY ", "PROMPT ", ...)."""
    runs = block["runs"]
    if block["kind"] == "p" and runs and runs[0]["bold"]:
        return runs[0]["text"], "".join(r["text"] for r in runs[1:])
    return None, block.get("text")
