"""Fold a page's "Ask yourself" questions: each run of adjacent question blocks becomes one collapsed group.

    python3 group_asks.py 04-evaluation-harness.html 05-checkpoints-and-approval.html

Few learners answer these questions, so they must not flood the page. A question block is a
<div class="ask"> whose label has the Read/Present pair (<span class="self">Ask yourself</span>
<span class="room">Ask the room</span>); "Read your code", "After class" and "Next session" blocks
are left alone. Blocks separated only by whitespace share one <details class="askgroup">, collapsed
in Read and Present and open in the Instructor view. The script is idempotent: it adds its CSS and
its line of script once, and a page that already has groups is left as it is.
"""
import re
import sys
from pathlib import Path

CSS = """/* "Ask yourself" questions fold into one collapsed group per row (see group_asks.py) */
.askgroup { max-width: 68ch; background: var(--sheet); border: 1px solid var(--rule); border-radius: 10px; }
.askgroup > summary { cursor: pointer; padding: 12px 20px; font: 600 11.5px var(--mono); letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); }
.askgroup > summary .room { display: none; }
.present .askgroup > summary .room, .instructor-view .askgroup > summary .room { display: inline; }
.present .askgroup > summary .self, .instructor-view .askgroup > summary .self { display: none; }
.askgroup > .askbody { display: grid; gap: 18px; padding: 2px 20px 18px; }
.askgroup .ask { padding: 0; background: none; border: 0; border-radius: 0; }
.askgroup .ask > .label { display: none; }
"""
CSS_ANCHOR = "/* Read your code:"
JS_OLD = 'document.querySelectorAll(".ask details").forEach((d) => { d.open = view === "instructor"; });'
JS_NEW = ('document.querySelectorAll(".ask details, details.askgroup").forEach((d) => { d.open = view === "instructor"; });')
OPEN = '<div class="ask"><span class="label"><span class="self">'


def block_end(html, start):
    """Index just past the </div> that closes the <div> starting at start."""
    depth = 0
    for m in re.compile(r"<div\b|</div>").finditer(html, start):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return m.end()
    raise ValueError(f"unclosed div at {start}")


def group(html):
    if ".askgroup {" not in html:
        assert CSS_ANCHOR in html, "page has no Read your code CSS to anchor on"
        html = html.replace(CSS_ANCHOR, CSS + CSS_ANCHOR, 1)
    if JS_NEW not in html:
        assert JS_OLD in html, "page script differs from the Session 04 page"
        html = html.replace(JS_OLD, JS_NEW, 1)
    if '<details class="askgroup">' in html:
        return html  # already grouped
    pos = 0
    while True:
        start = html.find(OPEN, pos)
        if start < 0:
            break
        blocks, end = [], start
        while True:
            stop = block_end(html, end)
            blocks.append(html[end:stop])
            gap = re.match(r"\s*", html[stop:]).end()
            if html.startswith(OPEN, stop + gap):
                end = stop + gap
                continue
            end = stop
            break
        indent = html[html.rfind("\n", 0, start) + 1:start]
        n = len(blocks)
        summary = (f'<summary><span class="self">Ask yourself</span><span class="room">Ask the room</span>'
                   f' · {n} question{"s" if n != 1 else ""}</summary>')
        body = f"\n{indent}  ".join(blocks)
        wrapped = (f'<details class="askgroup">{summary}<div class="askbody">\n{indent}  {body}\n'
                   f'{indent}</div></details>')
        html = html[:start] + wrapped + html[end:]
        pos = start + len(wrapped)
    return html


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for name in sys.argv[1:]:
        path = here / name
        before = path.read_text(encoding="utf-8")
        after = group(before)
        path.write_text(after, encoding="utf-8")
        print(name, "groups:", after.count('<details class="askgroup">'))
