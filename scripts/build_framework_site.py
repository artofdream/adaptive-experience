#!/usr/bin/env python3
"""Build architecture.artof.link from an allowlist of docs/framework markdown.

Stdlib only. Adding a page means changing PAGES below. Do not glob the repo.
Images and short local videos may only come from docs/framework/assets/ with a safe filename.
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
    ('stack', 'stack.md', 'Stack'),
    ('comparison', 'comparison.md', 'Comparison'),
    ('path-b', 'path-b.md', 'Path B case study'),
    ('glossary', 'glossary.md', 'Glossary'),
    ('journal', 'journal.md', 'Journal'),
    ('companion', 'companion.md', 'Companion'),
    ('crm', 'crm.md', 'Privacy CRM'),
]
SITE = 'architecture.artof.link'
CSS = (
    ':root{color-scheme:light dark;--bg:#fbf8f1;--fg:#1c2024;--muted:#6b665c;'
    '--rule:#e3ded2;--accent:#9c7c38;--link:#1b6b93;--warn:#b85c1c;--code-bg:#efebe0;'
    '--focus-ring:#9c7c38}'
    '@media(prefers-color-scheme:dark){:root{--bg:#121417;--fg:#e7e4dc;--muted:#9a9588;'
    '--rule:#2a2e33;--accent:#c4b08a;--link:#d7c49a;--warn:#d4a07a;--code-bg:#1c2024;'
    '--focus-ring:#c4b08a}}'
    '*{box-sizing:border-box}html{font-size:18px}'
    'body{margin:0;background:var(--bg);color:var(--fg);'
    'font-family:Palatino,Times New Roman,serif;line-height:1.55;'
    'transition:background-color .15s ease,color .15s ease}'
    '.skip-link{position:absolute;top:-999px;left:1rem;background:var(--bg);'
    'color:var(--link);padding:.5rem 1rem;border:1px solid var(--accent);'
    'border-radius:4px;z-index:100;font-family:ui-sans-serif,system-ui,sans-serif;'
    'font-size:.85rem;text-decoration:none}'
    '.skip-link:focus-visible{top:1rem}'
    ':focus-visible{outline:2px solid var(--focus-ring);outline-offset:2px}'
    'header,main,footer{max-width:40rem;margin:0 auto;padding:0 1.25rem}'
    'header{padding-top:2.5rem;padding-bottom:1.25rem;border-bottom:1px solid var(--rule)}'
    'header a,nav.site a{color:var(--muted);text-decoration:none;'
    'font-family:ui-sans-serif,system-ui,sans-serif;font-size:.85rem;'
    'display:inline-flex;align-items:center;min-height:44px;padding:.25rem 0}'
    'header a:hover,nav.site a:hover{color:var(--fg);text-decoration:underline}'
    'nav.site a[aria-current="page"]{color:var(--fg);font-weight:600}'
    'h1{font-size:2rem}h2{font-size:1.25rem;margin:2rem 0 .6rem}'
    'a{color:var(--link)}a[href^="http"]:not([href*="architecture.artof.link"])::after{'
    'content:" ↗";font-size:.8em;vertical-align:super;text-decoration:none}'
    'code{font-family:ui-monospace,Menlo,monospace;'
    'background:var(--code-bg);padding:.1em .35em;border-radius:3px}'
    '.formula{border-left:3px solid var(--accent);padding-left:1rem}'
    '.warn{color:var(--warn)}nav.site{display:flex;flex-wrap:wrap;gap:1rem;margin-top:.5rem}'
    'html{scroll-behavior:smooth}'
    'p.toc{margin:1.25rem 0 2rem;padding:.75rem 1rem;background:var(--code-bg);'
    'border:1px solid var(--rule);border-radius:4px;font-family:ui-sans-serif,system-ui,sans-serif;'
    'font-size:.85rem;display:flex;flex-wrap:wrap;gap:.75rem}'
    'p.toc a{text-decoration:none}'
    'p.toc a:hover{text-decoration:underline}'
    'figure{margin:1.75rem 0}figure img,figure video{max-width:100%;height:auto;display:block;'
    'border:1px solid var(--rule);border-radius:4px}'
    'figure figcaption{margin-top:.5rem;color:var(--muted);'
    'font-family:ui-sans-serif,system-ui,sans-serif;font-size:.82rem}'
    '@media(max-width:480px){figure{margin:1.25rem -0.5rem}figure img,figure video{border-radius:0}}'
    'pre{background:var(--code-bg);border:1px solid var(--rule);border-radius:4px;'
    'padding:.75rem 1rem;overflow-x:auto;font-family:ui-monospace,Menlo,monospace;'
    'font-size:.76rem;line-height:1.35;margin:1.25rem 0}'
    '.table-wrap{overflow-x:auto;margin:1.25rem 0;-webkit-overflow-scrolling:touch}'
    'table{width:100%;border-collapse:collapse;font-family:ui-sans-serif,system-ui,sans-serif;'
    'font-size:.82rem;line-height:1.4}'
    'th,td{border:1px solid var(--rule);padding:.45rem .65rem;text-align:left;vertical-align:top;'
    'word-break:break-word;overflow-wrap:anywhere}'
    'th{background:var(--code-bg);font-weight:600}'
    '@media(max-width:640px){'
    'pre{font-size:clamp(.58rem,.9vw,.76rem);padding:.6rem .7rem}}'
    'blockquote.callout{background:var(--code-bg);border-left:3px solid var(--accent);'
    'margin:1.25rem 0;padding:.85rem 1.1rem;border-radius:0 4px 4px 0}'
    'blockquote.callout p{margin:0}'
    'footer{margin-top:3rem;padding:1.5rem 1.25rem 3rem;border-top:1px solid var(--rule);'
    'color:var(--muted);font-family:ui-sans-serif,system-ui,sans-serif;font-size:.82rem}'
    '@media(max-width:768px){'
    '.jump-nav{position:fixed;right:max(.75rem,env(safe-area-inset-right));'
    'bottom:max(1rem,env(safe-area-inset-bottom));z-index:50;'
    'display:flex;flex-direction:column;gap:.4rem}'
    '.jump-nav a{display:inline-flex;align-items:center;justify-content:center;'
    'min-width:44px;min-height:44px;padding:.35rem .55rem;'
    'border:1px solid var(--rule);border-radius:999px;'
    'background:color-mix(in srgb,var(--bg) 92%,transparent);'
    'backdrop-filter:blur(6px);color:var(--fg);text-decoration:none;'
    'font-family:ui-sans-serif,system-ui,sans-serif;font-size:.72rem;font-weight:600;'
    'box-shadow:0 1px 4px color-mix(in srgb,var(--fg) 12%,transparent)}'
    '.jump-nav a:hover{border-color:var(--accent);color:var(--accent)}}'
    '@media(min-width:769px){.jump-nav{display:none}}'
)
INLINE = re.compile(
    r'`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*|\*([^*]+)\*'
)
IMG_LINE = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)$')
SAFE_ASSET = re.compile(r'^assets/[A-Za-z0-9._-]+\.(?:png|jpe?g|webp|svg|mp4|webm)$')
SAFE_VIDEO = re.compile(r'^assets/[A-Za-z0-9._-]+\.(?:mp4|webm)$')
LOCAL_PAGE = re.compile(r'^(?:index|[A-Za-z0-9._-]+)\.html$')


def site_href(href: str) -> str:
    """Root-relative for Pages pretty URLs (/journal must not resolve schema.html to /journal/schema.html)."""
    if href.startswith(('/', 'http://', 'https://', 'mailto:', '#')):
        return href
    if SAFE_ASSET.match(href) or LOCAL_PAGE.match(href):
        return '/' + href
    return href


def inline_md(text: str) -> str:
    parts = []
    i = 0
    for m in INLINE.finditer(text):
        parts.append(html.escape(text[i:m.start()]))
        if m.group(1) is not None:
            parts.append('<code>' + html.escape(m.group(1)) + '</code>')
        elif m.group(2) is not None:
            href = html.escape(site_href(m.group(3)), quote=True)
            parts.append('<a href="' + href + '">' + inline_md(m.group(2)) + '</a>')
        elif m.group(4) is not None:
            parts.append('<strong>' + inline_md(m.group(4)) + '</strong>')
        else:
            parts.append('<em>' + inline_md(m.group(5)) + '</em>')
        i = m.end()
    parts.append(html.escape(text[i:]))
    return ''.join(parts)


def md_to_html(source: str) -> str:
    out: list[str] = []
    in_list: str | None = None
    in_code: bool = False
    code_lines: list[str] = []
    in_table: bool = False
    table_headers: list[str] = []
    table_rows: list[list[str]] = []

    def close() -> None:
        nonlocal in_list, in_table, table_headers, table_rows
        if in_list:
            out.append('</' + in_list + '>')
            in_list = None
        if in_table:
            t = ['<div class="table-wrap"><table>']
            if table_headers:
                t.append('<thead><tr>' + ''.join('<th>' + inline_md(h) + '</th>' for h in table_headers) + '</tr></thead>')
            if table_rows:
                t.append('<tbody>')
                for row in table_rows:
                    t.append('<tr>' + ''.join('<td>' + inline_md(c) + '</td>' for c in row) + '</tr>')
                t.append('</tbody>')
            t.append('</table></div>')
            out.append(''.join(t))
            in_table = False
            table_headers = []
            table_rows = []

    clean_source = source.lstrip('\ufeff')
    for raw in clean_source.splitlines():
        if raw.strip().startswith('```'):
            if in_code:
                out.append('<pre><code>' + html.escape('\n'.join(code_lines)) + '</code></pre>')
                code_lines = []
                in_code = False
            else:
                close()
                in_code = True
            continue
        if in_code:
            code_lines.append(raw)
            continue

        line = raw.strip()
        if not line:
            close()
            continue

        if line.startswith('> '):
            close()
            out.append('<blockquote class="callout"><p>' + inline_md(line[2:].strip()) + '</p></blockquote>')
            continue

        if line.startswith('|') and line.endswith('|') and '|' in line[1:-1]:
            if in_list:
                close()
            cells = [c.strip() for c in line[1:-1].split('|')]
            if all(re.match(r'^:?-+:?$', c) for c in cells if c):
                continue
            if not in_table:
                in_table = True
                table_headers = cells
            else:
                table_rows.append(cells)
            continue
        else:
            if in_table:
                close()

        img = IMG_LINE.match(line)
        if img:
            close()
            alt, src = img.group(1), img.group(2)
            if SAFE_VIDEO.match(src):
                href = src if src.startswith('/') else '/' + src
                poster = re.sub(r'\.(mp4|webm)$', '.jpg', src)
                poster_href = poster if poster.startswith('/') else '/' + poster
                mime = 'video/webm' if src.endswith('.webm') else 'video/mp4'
                poster_attr = ''
                if SAFE_ASSET.match(poster):
                    poster_attr = ' poster="' + html.escape(poster_href, quote=True) + '"'
                out.append(
                    '<figure><video controls preload="metadata" playsinline'
                    + poster_attr
                    + '><source src="'
                    + html.escape(href, quote=True)
                    + '" type="'
                    + mime
                    + '"></video><figcaption>'
                    + html.escape(alt)
                    + '</figcaption></figure>'
                )
            elif SAFE_ASSET.match(src):
                href = src if src.startswith('/') else '/' + src
                out.append(
                    '<figure><img src="'
                    + html.escape(href, quote=True)
                    + '" alt="'
                    + html.escape(alt, quote=True)
                    + '"></figure>'
                )
            else:
                out.append('<p>' + html.escape(line) + '</p>')
            continue
        h = re.match(r'^(#{1,3})\s+(.*)$', line)
        if h:
            close()
            n = str(len(h.group(1)))
            raw_title = h.group(2)
            slug = re.sub(r'[^a-z0-9]+', '-', raw_title.lower()).strip('-')
            id_attr = f' id="{slug}"' if slug and len(h.group(1)) > 1 else ''
            out.append('<h' + n + id_attr + '>' + inline_md(raw_title) + '</h' + n + '>')
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
        elif line.startswith('[') and '](#' in line:
            cls = ' class="toc"'
        elif 'CF-054' in line and 'regressed' in line.lower():
            cls = ' class="warn"'
        out.append('<p' + cls + '>' + inline_md(line) + '</p>')
    close()
    return '\n'.join(out)


def wrap(title: str, slug: str, body: str) -> str:
    nav = []
    for other, _src, other_title in PAGES:
        href = site_href('index.html' if other == 'index' else other + '.html')
        cur = ' aria-current="page"' if other == slug else ''
        label = 'Framework' if other == 'index' else other_title
        nav.append('<a href="' + href + '"' + cur + '>' + html.escape(label) + '</a>')
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">'
        '<title>' + html.escape(title) + ' — ' + html.escape(SITE) + '</title>'
        '<style>' + CSS + '</style></head><body>'
        '<a href="#main" class="skip-link">Skip to content</a><header>'
        '<a href="' + html.escape(site_href('index.html'), quote=True) + '">' + html.escape(SITE) + '</a>'
        '<nav class="site">' + ''.join(nav) + '</nav></header><main id="main">'
        + body +
        '</main><footer id="site-footer">Public framework surface. Allowlisted markdown on GitLab main. '
        'Updated: 3 Sep 2026. Path B shop stays at <a href="https://aea.artof.link">aea.artof.link</a>. '
        'Merge publishes. No CMS.</footer>'
        '<nav class="jump-nav" aria-label="Page jump">'
        '<a href="#top" id="jump-top" title="Top of page">Top</a>'
        '<a href="#site-footer" id="jump-bottom" title="Bottom of page">Bottom</a></nav>'
        '<script>(function(){var n=document.querySelector(".jump-nav");if(!n)return;'
        'document.documentElement.id="top";'
        'function sync(){var long=(document.documentElement.scrollHeight-window.innerHeight)>480;'
        'n.hidden=!long;}sync();window.addEventListener("resize",sync);'
        'n.addEventListener("click",function(e){var a=e.target.closest("a");if(!a)return;'
        'e.preventDefault();var id=a.getAttribute("href").slice(1);'
        'var el=document.getElementById(id)||(id==="top"?document.body:null);'
        'if(el)el.scrollIntoView({behavior:"smooth",block:id==="top"?"start":"end"});});'
        '})();</script>'
        '</body></html>'
    )


def copy_assets() -> None:
    src = SRC / 'assets'
    dest = OUT / 'assets'
    if not src.is_dir():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.iterdir():
        if not path.is_file():
            continue
        rel = 'assets/' + path.name
        if SAFE_ASSET.match(rel):
            (dest / path.name).write_bytes(path.read_bytes())
            print('ok: ' + str(path.relative_to(ROOT)) + ' -> ' + str((dest / path.name).relative_to(ROOT)))


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fail = 0
    copy_assets()
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
