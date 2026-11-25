"""Remove hover tooltips from a page's diagrams, keeping their text for screen readers.

    python3 no_svg_tooltips.py 05-checkpoints-and-approval.html ...

Browsers show an SVG <title> as a tooltip, which on a large diagram hides the parts a presenter points at.
So a diagram's title and description go in aria-label (read by screen readers, never shown) and no <title> or <desc>
stays inside an <svg>. The page's own <title> in its head is untouched. Idempotent.
"""
import html
import re
import sys
from pathlib import Path

SVG = re.compile(r"<svg\b.*?</svg>", re.S)


def strip(page):
    def fix(match):
        svg = match.group(0)
        texts = dict(re.findall(r'<(?:title|desc) id="([^"]+)">(.*?)</(?:title|desc)>', svg, re.S))
        def label(m):
            parts = [" ".join(html.unescape(texts[i]).split()) for i in m.group(1).split() if i in texts]
            parts = [p if p.endswith((".", "!", "?")) else p + "." for p in parts]
            return f'aria-label="{html.escape(" ".join(parts), quote=True)}"' if parts else m.group(0)
        svg = re.sub(r'aria-labelledby="([^"]+)"', label, svg)
        return re.sub(r"\s*<(title|desc)\b[^>]*>.*?</\1>", "", svg, flags=re.S)
    return SVG.sub(fix, page)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for name in sys.argv[1:]:
        path = here / name
        before = path.read_text(encoding="utf-8")
        after = strip(before)
        path.write_text(after, encoding="utf-8")
        print(name, "svg titles removed:", len(re.findall(r"<svg\b.*?</svg>", before, re.S)) and
              sum(s.count("<title") for s in SVG.findall(before)))
