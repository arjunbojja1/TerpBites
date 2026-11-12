#!/usr/bin/env python3
"""Build report/findings.html from content.md + data.json + style.css.

The GitHub Action runs this, then prints the HTML to report/TerpBites_Findings.pdf with Chrome.
Locally: pip install markdown && python3 report/build.py
"""
import html
import json
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
esc = html.escape

data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
css = (HERE / "style.css").read_text(encoding="utf-8")
text = (HERE / "content.md").read_text(encoding="utf-8")
text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # drop the editing notes

fig_no = 0


def bars(c):
    rows, total = c["rows"], c["total"]
    mx = max(v for _, v in rows) or 1
    hl = set(c.get("highlight", []))
    out = []
    for label, v in rows:
        cls = " hl" if label in hl else ""
        out.append(
            f'<div class="row{cls}"><span class="lab">{esc(label)}</span>'
            f'<span class="track"><span class="fill" style="width:{v / mx * 100:.1f}%"></span></span>'
            f'<span class="val"><b>{v}</b> <i>{v / total:.0%}</i></span></div>'
        )
    return '<div class="bars">' + "".join(out) + "</div>"


def split_bar(c):
    (a_label, a), (b_label, b) = c["rows"][:2]
    total = a + b
    first = a_label.split(" (")[0]
    second = b_label.split(" (")[0]
    return (f'<div class="split-bar"><span style="width:{a / total * 100:.2f}%;background:var(--berry)">{esc(first)} {a}</span>'
            f'<span style="width:{b / total * 100:.2f}%;background:var(--mango);color:var(--ink)">{esc(second)} {b}</span></div>')


def card(title, sub, body, note):
    global fig_no
    fig_no += 1
    return (f'<figure class="card"><header><span class="num">{fig_no}</span><div><h4>{esc(title)}</h4>'
            f'<p class="sub">{esc(sub)}</p></div></header>{body}<figcaption>{esc(note)}</figcaption></figure>')


def chart(name):
    c = data["charts"][name]
    body = (split_bar(c) if c.get("split") else "") + bars(c)
    return card(c["title"], c.get("sub", ""), body, c.get("note", ""))


def charts(names):
    cards = [chart(n) for n in names]
    return f'<div class="grid2">{"".join(cards)}</div>' if len(cards) > 1 else cards[0]


def figure(name):
    f = data["images"][name]
    return card(f["title"], f.get("sub", ""), f'<img src="{esc(f["src"])}" alt="{esc(f["title"])}">', f.get("note", "")).replace(
        '<figure class="card">', '<figure class="card aff">', 1)


def tiles():
    t = "".join(f'<div class="tile"><div class="big">{esc(x["big"])}</div><p>{esc(x["text"])}</p></div>' for x in data["tiles"])
    return f'<div class="tiles">{t}</div>'


# Swap {{...}} blocks for tokens, render Markdown, then put the HTML back (in order, so figures number correctly).
blocks = []


def stash(m):
    kind, _, arg = m.group(1).partition(":")
    kind, arg = kind.strip().lower(), arg.strip()
    blocks.append((kind, arg))
    return f"\n\nBLOCKTOKEN{len(blocks) - 1}\n\n"


text = re.sub(r"\{\{\s*(.*?)\s*\}\}", stash, text)
body = markdown.markdown(text, extensions=["tables", "sane_lists"])


def render(kind, arg):
    if kind == "tiles":
        return tiles()
    if kind in ("chart", "charts"):
        return charts([n.strip() for n in arg.split(",") if n.strip()])
    if kind == "figure":
        return figure(arg)
    raise SystemExit(f"Unknown block {{{{{kind}: {arg}}}}} in content.md")


rendered = {}


def unstash(m):
    i = int(m.group(1))
    if i not in rendered:
        rendered[i] = render(*blocks[i])
    return rendered[i]


# Render in document order so figure numbers count up from the top.
for i in range(len(blocks)):
    rendered[i] = render(*blocks[i])
body = re.sub(r"<p>BLOCKTOKEN(\d+)</p>", unstash, body)

# Research questions list gets the pill style.
body = re.sub(r"(<h2>Research questions</h2>\s*)<ol>", r'\1<ol class="rq">', body)

# "Done: 23 responses" / "In progress" table cells become status pills.
def status(m):
    word, extra = m.group(1), (m.group(2) or "").strip()
    cls = "done" if word.lower() == "done" else "todo"
    count = f'<span class="count">{esc(extra)}</span>' if extra else ""
    return f'<td><span class="status {cls}">{word}</span>{count}</td>'


body = re.sub(r"<td>(Done|In progress)(?::\s*([^<]*))?</td>", status, body)
body = body.replace("<th>Status</th>", '<th class="st">Status</th>')

cv = data["cover"]
cover = f"""<div class="cover">
  <div class="brand"><svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="16" fill="#ffb23f"/><path d="M9 17a7 7 0 0 0 14 0H9Z" fill="#24122e"/><path d="M13 13c0-2 1.5-2.5 1.5-4.5M17.5 13c0-2 1.5-2.5 1.5-4.5" stroke="#24122e" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>TerpBites</div>
  <p class="pill">{esc(cv["pill"])}</p>
  <h1>{esc(cv["title"])}</h1>
  <p class="meta"><b>Members:</b> {esc(cv["members"])}</p>
  <p class="meta"><b>Project website:</b> {esc(cv["website"])}</p>
</div>"""

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TerpBites_Findings</title>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Figtree:wght@400;500;600;700&display=block" rel="stylesheet">
<style>{css}</style></head>
<body>{cover}
{body}
</body></html>"""

(HERE / "findings.html").write_text(page, encoding="utf-8")
words = len(re.sub(r"<[^>]+>", " ", body).split())
print(f"Built report/findings.html ({fig_no} figures, about {words} words of body text)")
