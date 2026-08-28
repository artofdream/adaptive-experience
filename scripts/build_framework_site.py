#!/usr/bin/env python3
"""Build architecture.artof.link from an allowlist of docs/framework markdown.

Stdlib only. Adding a page means changing PAGES below. Do not glob the repo.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'docs' / 'framework'
OUT = ROOT / 'public'
PAGES = [
    ('index', 'index.md', 'Adaptive Experience Architecture'),
    ('schema', 'schema.md', 'Schema'),
    ('path-b', 'path-b.md', 'Path B case study'),
]
SITE = 'architecture.artof.link'
CSS = (
    ':root{color-scheme:dark;--bg:#121417;--fg:#e7e4dc;--muted:#9a9588;'
    '--rule:#2a2e33;--accent:#c4b08a;--link:#d7c49a;--warn:#d4a07a}'
    '*{box-sizing:border-box}html{font-size:18px}'
    'body{margin:0;background:var(--bg);color:var(--fg);'
    'font-family:Palatino,Times New Roman,serif;line-height:1.55}'
    'header,main,footer{max-width:40rem;margin:0 auto;padding:0 1.25rem}'
    'header{padding-top:2.5rem;padding-bottom:1.25rem;border-bottom:1px solid var(--rule)}'
    'header a,nav.site a{color:var(--muted);text-decoration:none;'
    'font-family:ui-sans-serif,system-ui,sans-serif;font-size:.85rem}'
    'h1{font-size:2rem}h2{font-size:1.25rem;margin:2rem 0 .6rem}'
    'a{color:var(--link)}code{font-family:ui-monospace,Menlo,monospace;'
    'background:#1c2024;padding:.1em .35em}'
    '.formula{border-left:3px solid var(--accent);padding-left:1rem}'
    '.warn{color:var(--warn)}nav.site{display:flex;gap:1rem;margin-top:.75rem}'
    'footer{margin-top:3rem;padding:1.5rem 1.25rem 3rem;border-top:1px solid var(--rule);'
    'color:var(--muted);font-family:ui-sans-serif,system-ui,sans-serif;font-size:.82rem}'
)
INLINE = re.compile(
    r'`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*'
)


def inline_md(text: str) -> str:
    parts = []
    i = 0
    for m in INLINE.finditer(text):
        parts.append(html.escape(text[i:m.start()]))
        if m.group(1) is not None:
            parts.append('<code>' + html.escape(m.group(1)) + '</code>')
        elif m.group(2) is not None:
            href = html.escape(m.group(3), quote=True)
            parts.append('<a href="' + href + '">' + html.escape(m.group(2)) + '</a>')
        elif m.group(4) is not None:
            parts.append('<strong>' + html.escape(m.group(4)) + '</strong>')
        else:
            parts.append('<em>' + html.escape(m.group(5)) + '</em>')
        i = m.end()
    parts.append(html.escape(text[i:]))
    return ''.join(parts)


def md_to_html(source: str) -> str:
    out: list[str] = []
    in_list: str | None = None

    def close() -> None:
        nonlocal in_list
        if in_list:
            out.append('</' + in_list + '>')
            in_list = None

    for raw in source.splitlines():
        line = raw.strip()
        if not line:
            close()
            continue
        h = re.match(r'^(#{1,3})\s+(.*)$', line)
        if h:
            close()
            n = str(len(h.group(1)))
            out.append('<h' + n + '>' + inline_md(h.group(2)) + '</h' + n + '>')
            continue
        ul = re.match(r'^[-*]\s+(.*)$', line)
        ol = re.match(r'^\d+\.\s+(.*)$', line)
        if ul or ol:
            kind = 'ul' if ul else 'ol'
            item = (ul or ol).group(1)
            if in_list != kind:
                close()
                out.append('<' + kind + '>')
                in_list = kind
            out.append('<li>' + inline_md(item) + '</li>')
            continue
        close()
        cls = ''
        if line.startswith('**Adaptive Experience ='):
            cls = ' class="formula"'
        if 'CF-054' in line and 'regressed' in line.lower():
            cls = ' class="warn"'
        out.append('<p' + cls + '>' + inline_md(line) + '</p>')
    close()
    return '\n'.join(out)


def wrap(title: str, slug: str, body: str) -> str:
    nav = []
    for other, _src, other_title in PAGES:
        href = 'index.html' if other == 'index' else other + '.html'
        cur = ' aria-current="page"' if other == slug else ''
        label = 'Framework' if other == 'index' else other_title
        nav.append('<a href="' + href + '"' + cur + '>' + html.escape(label) + '</a>')
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + html.escape(title) + ' — ' + html.escape(SITE) + '</title>'
        '<style>' + CSS + '</style></head><body><header>'
        '<a href="index.html">' + html.escape(SITE) + '</a>'
        '<nav class="site">' + ''.join(nav) + '</nav></header><main>'
        + body +
        '</main><footer>Public framework surface. Allowlisted markdown on GitLab main. '
        'Path B shop stays at aea.artof.link. Merge publishes. No CMS.</footer>'
        '</body></html>'
    )


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fail = 0
    for slug, name, title in PAGES:
        path = SRC / name
        if not path.is_file():
            print('FAIL: missing ' + str(path), file=sys.stderr)
            fail = 1
            continue
        dest = OUT / ('index.html' if slug == 'index' else slug + '.html')
        dest.write_text(wrap(title, slug, md_to_html(path.read_text(encoding='utf-8'))), encoding='utf-8')
        print('ok: ' + str(path.relative_to(ROOT)) + ' -> ' + str(dest.relative_to(ROOT)))
    return fail


if __name__ == '__main__':
    raise SystemExit(build())
