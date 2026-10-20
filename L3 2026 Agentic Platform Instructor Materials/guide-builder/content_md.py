"""Regenerate the Markdown twin of a content-development document from its .docx.

    uv run --with python-docx python content_md.py "../content-development/01 … - content development.docx"

The .docx in the repository is the single source of truth for L&D; edit it, then run this.
"""
import re
import sys
import docx
from docx.oxml.ns import qn

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"\.docx$", ".md", src)
d = docx.Document(src)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
out = [f"> Markdown copy of [`{src.split('/')[-1]}`]({src.split('/')[-1].replace(' ', '%20')}) for reading on GitHub. "
       "The Word document in this repository is the single source of truth; edit it, then regenerate this page with "
       "`guide-builder/content_md.py`."]
for el in d.element.body.iterchildren():
    if el.tag == W + "p":
        p = docx.text.paragraph.Paragraph(el, d)
        lines = []
        for r in el.iter(W + "r"):
            for child in r:
                if child.tag == W + "t":
                    text = child.text or ""
                    bold = r.find(W + "rPr") is not None and r.find(W + "rPr").find(W + "b") is not None
                    lines.append(f"**{text.strip()}** " if bold and text.strip() else text)
                elif child.tag == W + "br":
                    lines.append("\n")
        text = "".join(lines).strip()
        if not text:
            continue
        style = p.style.name
        if style == "Heading 1":
            out.append("## " + p.text.strip())
        elif style == "Heading 2":
            out.append("### " + p.text.strip())
        elif el.find(f"{W}pPr/{W}numPr") is not None:
            out.append("- " + text.replace("\n", " "))
        else:
            out.append(text.replace("\n", "  \n"))
    elif el.tag == W + "tbl":
        rows = [[c.text.replace("|", "\\|") for c in r.cells] for r in docx.table.Table(el, d).rows]
        out.append("\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
                             + ["| " + " | ".join(r) + " |" for r in rows[1:]]))
m = re.match(r"(\d\d) (.+) - content development\.docx$", src.split("/")[-1])
title = f"# Session {m.group(1)} content development: {m.group(2)}"
text = "\n\n".join([title] + out) + "\n"
# Merge consecutive bullet lines into one list block.
open(dst, "w", encoding="utf-8").write(text.replace("\n\n- ", "\n- ").replace(":\n- ", ":\n\n- "))
