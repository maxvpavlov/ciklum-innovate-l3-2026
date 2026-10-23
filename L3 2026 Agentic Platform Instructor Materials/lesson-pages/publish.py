"""Publish the session pages to docs/ for GitHub Pages.

    python3 publish.py

Each page in this folder is an HTML fragment (title, styles, body, script). GitHub Pages needs a full
document, so wrap() adds the doctype, charset, viewport and the course icon. build_prompts_page.py uses
the same wrap() for the prompts-only pages.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent.parent / "docs"
PAGES = {"01-agent-runtime.html": "lesson-01", "02-tools-and-mcp.html": "lesson-02"}

# Pages live one folder below docs/, so the icons are one level up.
ICONS = ('<link rel="icon" href="../favicon.svg" type="image/svg+xml">\n'
         '<link rel="icon" href="../favicon-32.png" sizes="32x32" type="image/png">\n'
         '<link rel="apple-touch-icon" href="../apple-touch-icon.png">\n')


def wrap(page):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + ICONS + '</head>\n<body>\n' + page.rstrip("\n") + '\n</body>\n</html>\n')


def publish(source, folder):
    out = DOCS / folder / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(wrap((HERE / source).read_text(encoding="utf-8")), encoding="utf-8")
    return out


if __name__ == "__main__":
    for source, folder in PAGES.items():
        print("wrote", publish(source, folder).relative_to(DOCS.parent))
