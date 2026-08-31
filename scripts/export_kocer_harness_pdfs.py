import os
import re
import html
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "research" / "pdf-export"
ARTIFACT_DIR = Path(r"C:\Users\claud\.gemini\antigravity\brain\9b179aea-00e2-4505-853b-9ccfa0c57ae0")

PDF_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def md_to_html_body(md_text: str) -> str:
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_lines = []
    in_table = False

    for line in lines:
        if line.startswith('```'):
            if in_code_block:
                html_lines.append('<pre><code>' + html.escape('\n'.join(code_lines)) + '</code></pre>')
                in_code_block = False
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if line.startswith('|') and '|' in line[1:]:
            if re.match(r'^[|\s:-]+$', line):
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not in_table:
                html_lines.append('<table><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                in_table = True
            else:
                html_lines.append('<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in cells) + '</tr>')
            continue
        elif in_table:
            html_lines.append('</tbody></table>')
            in_table = False

        if line.startswith('# '):
            html_lines.append(f'<h1>{html.escape(line[2:])}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{html.escape(line[3:])}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{html.escape(line[4:])}</h3>')
        elif line.startswith('#### '):
            html_lines.append(f'<h4>{html.escape(line[5:])}</h4>')
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{html.escape(line[2:])}</blockquote>')
        elif line.strip() == '---':
            html_lines.append('<hr>')
        elif line.strip():
            l_escaped = html.escape(line)
            l_escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', l_escaped)
            l_escaped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', l_escaped)
            l_escaped = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', l_escaped)
            l_escaped = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', l_escaped)
            html_lines.append(f'<p>{l_escaped}</p>')

    if in_table:
        html_lines.append('</tbody></table>')
    if in_code_block:
        html_lines.append('<pre><code>' + html.escape('\n'.join(code_lines)) + '</code></pre>')

    return '\n'.join(html_lines)

def generate_pdf(md_path: Path, output_pdf: Path, artifact_pdf: Path, title: str):
    md_text = md_path.read_text(encoding='utf-8')
    body_html = md_to_html_body(md_text)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
@page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 8pt;
        color: #6b665c;
    }}
}}
body {{
    font-family: Palatino, "Times New Roman", Georgia, serif;
    color: #1c2024;
    background-color: #ffffff;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
}}
h1 {{
    font-size: 18pt;
    color: #1c2024;
    border-bottom: 2px solid #9c7c38;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 12pt;
    font-family: Palatino, serif;
}}
h2 {{
    font-size: 13pt;
    color: #9c7c38;
    border-bottom: 1px solid #e3ded2;
    padding-bottom: 4px;
    margin-top: 16pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 11pt;
    color: #1c2024;
    margin-top: 12pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}}
h4 {{
    font-size: 10pt;
    color: #6b665c;
    margin-top: 10pt;
    margin-bottom: 4pt;
}}
code {{
    background-color: #efebe0;
    color: #1c2024;
    font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
    font-size: 8.5pt;
    padding: 1px 4px;
    border-radius: 3px;
}}
pre {{
    background-color: #fbf8f1;
    border: 1px solid #e3ded2;
    padding: 8px 12px;
    border-radius: 4px;
    overflow: auto;
    font-size: 8pt;
    font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
    line-height: 1.35;
    page-break-inside: avoid;
    white-space: pre-wrap;
}}
pre code {{
    background-color: transparent;
    padding: 0;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 8.5pt;
    font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #e3ded2;
    padding: 5px 8px;
    text-align: left;
}}
th {{
    background-color: #efebe0;
    color: #1c2024;
    font-weight: 600;
}}
blockquote {{
    border-left: 3px solid #9c7c38;
    background-color: #fbf8f1;
    color: #6b665c;
    margin: 10pt 0;
    padding: 6px 12px;
    font-style: italic;
    font-size: 9pt;
}}
a {{
    color: #1b6b93;
    text-decoration: none;
}}
hr {{
    border: 0;
    border-top: 1px solid #e3ded2;
    margin: 16pt 0;
}}
p {{
    margin: 6pt 0;
}}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    temp_html = output_pdf.with_suffix('.html')
    temp_html.write_text(full_html, encoding='utf-8')

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True
        )
        page = browser.new_page()
        page.goto(temp_html.as_uri(), wait_until='networkidle')
        page.pdf(
            path=str(output_pdf),
            format='A4',
            print_background=True,
            margin={'top': '20mm', 'bottom': '20mm', 'left': '15mm', 'right': '15mm'}
        )
        browser.close()

    shutil.copy2(output_pdf, artifact_pdf)
    print(f"Generated PDF: {output_pdf}")
    print(f"Copied to artifact: {artifact_pdf}")

def main():
    doc1_md = ROOT / "research" / "random-thoughts" / "2026-08-31-aea-framework-harness-engineering.md"
    doc1_pdf = PDF_DIR / "aea-framework-harness-engineering-2026-08-31.pdf"
    doc1_artifact = ARTIFACT_DIR / "aea_framework_harness_engineering_2026_08_31.pdf"
    generate_pdf(doc1_md, doc1_pdf, doc1_artifact, "Adaptive Experience Architecture — Harness Engineering (31 Aug 2026)")

    doc2_md = ROOT / "research" / "random-thoughts" / "2026-08-31-aea-vs-kocer-five-layers-agent-engineering.md"
    doc2_pdf = PDF_DIR / "aea-harness-vs-kocer-five-layers-2026-08-31.pdf"
    doc2_artifact = ARTIFACT_DIR / "aea_harness_vs_kocer_five_layers_2026_08_31.pdf"
    generate_pdf(doc2_md, doc2_pdf, doc2_artifact, "AEA vs Kocer Five Layers of Agent Engineering (31 Aug 2026)")

if __name__ == "__main__":
    main()
