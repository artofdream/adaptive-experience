import os
import re
import html
import shutil
import time
import subprocess
from playwright.sync_api import sync_playwright

def convert_md_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    in_mermaid = False
    in_table = False
    mermaid_code = []

    for line in lines:
        if line.startswith('```'):
            if in_mermaid:
                html_lines.append('<pre class="mermaid">\n' + '\n'.join(mermaid_code) + '\n</pre>')
                in_mermaid = False
                mermaid_code = []
            elif in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                lang = line[3:].strip()
                if lang == 'mermaid':
                    in_mermaid = True
                    mermaid_code = []
                else:
                    html_lines.append(f'<pre><code class="{lang}">')
                    in_code_block = True
            continue

        if in_mermaid:
            mermaid_code.append(line)
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            continue

        if line.startswith('|') and '|' in line[1:]:
            if '---' in line:
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
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{html.escape(line[2:])}</blockquote>')
        elif line.strip() == '---':
            html_lines.append('<hr>')
        elif line.strip():
            l_escaped = html.escape(line)
            l_escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', l_escaped)
            l_escaped = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', l_escaped)
            l_escaped = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', l_escaped)
            html_lines.append(f'<p>{l_escaped}</p>')

    if in_table:
        html_lines.append('</tbody></table>')

    return '\n'.join(html_lines)


def build_pdf():
    md_file = os.path.abspath('docs/aea-system-documentation.md')
    html_file = os.path.abspath('docs/aea-system-documentation.html')
    rendered_html_file = os.path.abspath('docs/aea-system-documentation-rendered.html')
    pdf_file = os.path.abspath('docs/aea-system-documentation.pdf')
    artifact_pdf = os.path.abspath(r'C:\Users\claud\.gemini\antigravity\brain\be5d2f05-8481-4eb9-9f7e-221c87a64aa2\aea_system_documentation.pdf')

    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    body_html = convert_md_to_html(md_text)

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Adaptive Experience Architecture (AEA) — System Documentation</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
@page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
}}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    line-height: 1.6;
    font-size: 10pt;
    margin: 0;
}}
h1 {{
    font-size: 22pt;
    color: #1e3a8a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
}}
h2 {{
    font-size: 14pt;
    color: #1e40af;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 18pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 11pt;
    color: #334155;
    margin-top: 12pt;
    page-break-after: avoid;
}}
code {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 9pt;
    padding: 2px 5px;
    border-radius: 4px;
}}
pre {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 10px 14px;
    border-radius: 6px;
    overflow: auto;
    font-size: 8.5pt;
    page-break-inside: avoid;
}}
pre.mermaid {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    text-align: center;
    padding: 16px;
    margin: 14pt 0;
    page-break-inside: avoid;
}}
pre code {{
    background-color: transparent;
    padding: 0;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
}}
th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
}}
blockquote {{
    border-left: 4px solid #2563eb;
    background-color: #eff6ff;
    color: #1e40af;
    padding: 8px 12px;
    margin: 12pt 0;
    border-radius: 0 4px 4px 0;
}}
hr {{
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 16pt 0;
}}
.footer {{
    text-align: center;
    font-size: 8pt;
    color: #64748b;
    margin-top: 24pt;
}}
</style>
</head>
<body>
{body_html}
<div class="footer">
    <p>Adaptive Experience Architecture (AEA) — Reference Implementation: Lily's Florist | Canonical Architecture Document</p>
</div>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: 'default', securityLevel: 'loose' }});
</script>
</body>
</html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    # Launch Edge via Playwright using local executable_path
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=edge_exe, headless=True)
        page = browser.new_page()
        page.goto(f"file:///{html_file.replace(os.sep, '/')}")
        # Wait for Mermaid to render SVG elements into DOM
        page.wait_for_selector("pre.mermaid svg", timeout=20000)
        time.sleep(2)
        # Save fully rendered HTML with inline SVGs
        rendered_content = page.content()
        with open(rendered_html_file, 'w', encoding='utf-8') as rf:
            rf.write(rendered_content)
        browser.close()

    print(f"Rendered HTML with embedded Mermaid SVGs saved to: {rendered_html_file}")

    # Convert rendered HTML to PDF using Edge headless print
    cmd = [
        edge_exe,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        f"--print-to-pdf={pdf_file}",
        rendered_html_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated repository PDF: {pdf_file}")

    shutil.copyfile(pdf_file, artifact_pdf)
    print(f"Copied to artifact PDF: {artifact_pdf}")

if __name__ == "__main__":
    build_pdf()
