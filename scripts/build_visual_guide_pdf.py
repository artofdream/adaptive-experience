#!/usr/bin/env python3
"""Build Plain-English Visual Guide PDF for AEA Harness Engineering (Playwright via Edge)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"c:\projects\code\adaptive-experience")
PDF_DIR = ROOT / "research" / "pdf-export"
ARTIFACT_DIR = Path(r"C:\Users\claud\.gemini\antigravity\brain\9b179aea-00e2-4505-853b-9ccfa0c57ae0")

PDF_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Adaptive Experience Architecture — The Plain-English Visual Guide to Harness Engineering</title>
<style>
@page {
    size: A4 portrait;
    margin-top: 16mm;
    margin-bottom: 16mm;
    margin-left: 15mm;
    margin-right: 15mm;
    @top-center {
        content: "Adaptive Experience Architecture — Plain-English Executive Guide";
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 8pt;
        color: #666666;
    }
    @bottom-left {
        content: counter(page) " of " counter(pages);
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 8pt;
        color: #666666;
    }
    @bottom-right {
        content: "Art of Group — September 2026";
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 8pt;
        color: #666666;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 9.2pt;
    line-height: 1.45;
    color: #1e293b;
    margin: 0;
    padding: 0;
}

.header-banner {
    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
    color: #ffffff;
    padding: 16pt 18pt;
    border-radius: 8px;
    margin-bottom: 14pt;
}

h1.main-title {
    font-size: 19pt;
    font-weight: 800;
    margin: 0 0 4pt 0;
    color: #ffffff;
    line-height: 1.2;
    letter-spacing: -0.3px;
}

.sub-title {
    font-size: 11pt;
    font-weight: 500;
    color: #93c5fd;
    margin: 0 0 8pt 0;
}

.meta-bar {
    font-size: 7.5pt;
    color: #cbd5e1;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding-top: 6pt;
    margin-top: 6pt;
}

h2.section-title {
    font-size: 12.5pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 4pt;
    margin-top: 14pt;
    margin-bottom: 6pt;
    display: flex;
    align-items: center;
}

h3.sub-section-title {
    font-size: 10pt;
    font-weight: 600;
    color: #1e40af;
    margin-top: 8pt;
    margin-bottom: 3pt;
}

p {
    margin-top: 0;
    margin-bottom: 6pt;
}

.card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8pt 10pt;
    margin-bottom: 8pt;
    break-inside: avoid;
}

.card-title {
    font-weight: 700;
    color: #0f172a;
    font-size: 9pt;
    margin-bottom: 4pt;
}

.formula-box {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 10pt 14pt;
    border-radius: 0 6px 6px 0;
    margin: 10pt 0;
    font-size: 11pt;
    font-weight: 700;
    color: #1e3a8a;
    text-align: center;
}

.diagram-pre {
    background-color: #0f172a;
    color: #38bdf8;
    border-radius: 6px;
    padding: 8pt 12pt;
    font-family: ui-monospace, "Cascadia Code", "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
    font-size: 7.2pt;
    line-height: 1.25;
    margin: 8pt 0;
    overflow-x: auto;
    white-space: pre;
    break-inside: avoid;
}

table.visual-table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0;
    font-size: 8pt;
    break-inside: avoid;
}

table.visual-table th, table.visual-table td {
    border: 1px solid #cbd5e1;
    padding: 5pt 7pt;
    text-align: left;
}

table.visual-table th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}

table.visual-table tr:nth-child(even) {
    background-color: #f8fafc;
}

.badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7pt;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-blue { background-color: #dbeafe; color: #1e40af; }
.badge-green { background-color: #dcfce7; color: #15803d; }
.badge-amber { background-color: #fef3c7; color: #b45309; }
.badge-red { background-color: #fee2e2; color: #b91c1c; }

ul {
    margin: 3pt 0 6pt 14pt;
    padding: 0;
}

li {
    margin-bottom: 2pt;
}

.footer-callout {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    padding: 10pt;
    margin-top: 12pt;
    color: #166534;
    font-size: 8.5pt;
    line-height: 1.4;
}
</style>
</head>
<body>

<div class="header-banner">
    <h1 class="main-title">Adaptive Experience Architecture</h1>
    <div class="sub-title">The Plain-English Visual Guide to Harness Engineering</div>
    <div class="meta-bar">
        Art of Group • September 2026 • Designed for Product Leaders, Executives & General Audiences • Canonical Reference: <code>aea.artof.link</code>
    </div>
</div>

<div class="card" style="background-color: #fffbeb; border-color: #fde68a;">
    <div class="card-title" style="color: #92400e;">💡 Why Most AI Prototypes Never Make It to Production</div>
    <p style="margin: 0; font-size: 8.8pt; color: #78350f;">
        A chatbot that talks charmingly in a demo is not a finished business. When real customers order flowers, the system must check physical cooler inventory, calculate delivery routes, itemize taxes, and process payments without leaking data. AI language models are probabilistic word predictors—they cannot manage a real warehouse. <strong>The Outer Harness</strong> is the software factory built around the AI to guarantee real-world honesty and safety.
    </p>
</div>

<h2 class="section-title">1. The Core Formula in Everyday Terms</h2>

<div class="formula-box">
    Adaptive Experience = Shared Understanding + Domain Services + Outer Harness
</div>

<div class="diagram-pre">┌────────────────────────────────────────────────────────────────────────┐
│ 1. THE CUSTOMER TALKS                                                  │
│    Shopper: "I need bright birthday flowers for my mom today in Berlin"│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. THE AI INTERPRETER & LIVE NOTEPAD                                   │
│    • AI Concierge: Listens and extracts intent (Occasion, Date, Color) │
│    • Shared Understanding: A digital notepad visible to both parties   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. THE REAL-WORLD SERVICES (The Source of Truth)                       │
│    • Warehouse: Validates real physical inventory (Fail-Closed)        │
│    • Delivery Engine: Calculates realistic driver routing & cutoffs    │
│    • Cash Register: Itemizes pricing, taxes, and zero-PII payment      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. THE OUTER HARNESS (The Factory & Quality Inspectors)                │
│    • 14 Automated Quality Guards: Verifies facts before showing them   │
│    • Independent Gatekeeper: Ensures no untested changes reach customers│
└────────────────────────────────────────────────────────────────────────┘</div>

<h3 class="sub-section-title">The Three Golden Rules:</h3>
<ul>
    <li><strong>AI Interprets, Domain Services Decide:</strong> The AI suggests flowers, but only the database confirms they are in stock.</li>
    <li><strong>Fail-Closed Availability:</strong> If the inventory server is unreachable, the purchase button turns off. It is far better to say "Checking stock..." than to sell bouquets you cannot deliver.</li>
    <li><strong>No Self-Approval:</strong> The engineer or AI that writes code is never the one who signs off on pushing it to customers.</li>
</ul>

<h2 class="section-title">2. The Three Eras of Building with AI (2023 &rarr; 2026)</h2>

<table class="visual-table">
<thead>
<tr>
    <th>Era</th>
    <th>Core Focus</th>
    <th>What It Optimized</th>
    <th>The Fatal Flaw</th>
</tr>
</thead>
<tbody>
<tr>
    <td><strong>Era 1: Prompting (2023–24)</strong></td>
    <td>Single Utterance</td>
    <td>Magic prompt keywords, tone, phrasing</td>
    <td>The AI forgets everything the second the chat window closes.</td>
</tr>
<tr>
    <td><strong>Era 2: Context / RAG (2025)</strong></td>
    <td>What the AI sees</td>
    <td>Stuffing large PDF manuals and search results</td>
    <td>Information overload; the AI knows facts but lacks real actions.</td>
</tr>
<tr>
    <td><strong>Era 3: Harness Eng. (2026)</strong></td>
    <td>The Entire System</td>
    <td>Automated test guards, databases, merge gates</td>
    <td>None. The AI is bounded by real-world software engineering.</td>
</tr>
</tbody>
</table>

<h2 class="section-title">3. The 5 Concentric Floors (Why AI Apps Break)</h2>

<p>Think of an AI system like a 5-story building. <strong>Each floor rests on the one below it.</strong> If you skip the lower floors, the top floor collapses.</p>

<div class="diagram-pre">┌────────────────────────────────────────────────────────────────────────┐
│ 🏢 FLOOR 05: THE AGENT TEAM & GOVERNANCE (Graph Engineering)           │
│    Specialized human/agent roles + an Independent Reviewer.            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 🔄 FLOOR 04: THE GOAL RUN & RETRIES (Loop Engineering)           │  │
│  │    Clear objectives, execution budgets, and single-task focus.   │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ ⚙️ FLOOR 03: THE MACHINE & TESTS (Harness Engineering)     │  │  │
│  │  │    Connecting AI to real tools + automated quality guards. │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │  │
│  │  │  │ 🧠 FLOOR 02: THE MEMORY CURATOR (Context Engineering)│  │  │  │
│  │  │  │    Filters noise, keeps lessons, manages active window.│  │  │
│  │  │  │  ┌────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │ 💬 FLOOR 01: THE MESSAGE (Prompt Engineering)  │  │  │  │  │
│  │  │  │  │    Clear role, single objective, strict rules. │  │  │  │  │
│  │  │  │  └────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Built On Real Infrastructure
┌────────────────────────────────────────────────────────────────────────┐
│ 🏛️ SOLID FOUNDATION: REAL DATABASES & INVENTORY (PostgreSQL & Kafka)   │
└────────────────────────────────────────────────────────────────────────┘</div>

<ul>
    <li><strong>The Dependency Law:</strong> If your multi-agent team keeps failing, don't blame the agents—check your memory filter. Bad input on Floor 2 ruins everything above it.</li>
    <li><strong>The Economic Law:</strong> Swapping the AI model (like switching from Claude to GPT or Gemini) takes <strong>1 afternoon</strong>. Rebuilding your 5-floor operational harness takes <strong>3 months</strong>. The harness is your real intellectual property.</li>
</ul>

<h2 class="section-title">4. How the "Second Brain" Solves AI Amnesia</h2>

<p>Without engineered memory, an AI starts every new conversation from scratch. Dumping hundreds of pages of past chat logs into the prompt makes the AI slow, expensive, and confused. AEA organizes memory into <strong>4 clean vaults</strong>:</p>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8pt; margin: 8pt 0;">
    <div class="card">
        <div class="card-title">📖 1. Procedure Memory (Skills)</div>
        <p style="margin: 0; font-size: 8pt; color: #475569;">Step-by-step playbooks for repeatable workflows (e.g., how to build an Android app or run tests).</p>
    </div>
    <div class="card">
        <div class="card-title">🚫 2. Correction Memory (Constraints)</div>
        <p style="margin: 0; font-size: 8pt; color: #475569;">Hard rules learned from past mistakes (e.g., "Never invent fake requirement IDs").</p>
    </div>
    <div class="card">
        <div class="card-title">🕸️ 3. Relationship Memory (Graph)</div>
        <p style="margin: 0; font-size: 8pt; color: #475569;">Links showing how features, requirements, customer occasions, and code connect.</p>
    </div>
    <div class="card">
        <div class="card-title">📅 4. Daily Brief (Handoff)</div>
        <p style="margin: 0; font-size: 8pt; color: #475569;">A clean 1-page summary of exactly where the team left off today so work resumes instantly.</p>
    </div>
</div>

<h2 class="section-title">5. Team Organization: 14 Hats Mapped to 6 Functions</h2>

<table class="visual-table">
<thead>
<tr>
    <th>Function</th>
    <th>Stakeholder Roles</th>
    <th>Core Responsibility</th>
</tr>
</thead>
<tbody>
<tr>
    <td><span class="badge badge-blue">1. Discovery</span></td>
    <td>UX Designer, Customer Journey, Support Coordinator</td>
    <td>Identify shopper friction, design mobile/web flows, and intake customer needs.</td>
</tr>
<tr>
    <td><span class="badge badge-blue">2. Strategy</span></td>
    <td>Product Owner, Project Manager</td>
    <td>Set business priorities, manage milestone delivery, and enforce scope gates.</td>
</tr>
<tr>
    <td><span class="badge badge-red">3. Safety</span></td>
    <td>Security Auditor, Cost Guardian, Performance Guardian, Coherence Guardian</td>
    <td>Block prompt injection, enforce cloud spending caps, guarantee fast loading times.</td>
</tr>
<tr>
    <td><span class="badge badge-green">4. Builders</span></td>
    <td>Senior Software Engineer, AI Engineer, DevSecOps Platform</td>
    <td>Build backend services, native Android apps, cloud infrastructure, and AI models.</td>
</tr>
<tr>
    <td><span class="badge badge-amber">5. Gatekeeper</span></td>
    <td>Merge Request Coordinator (@aea-mrc)</td>
    <td><strong>Independent Review:</strong> Verifies all tests pass before code touches production.</td>
</tr>
<tr>
    <td><span class="badge badge-blue">6. Knowledge</span></td>
    <td>Knowledge Guardian (@aea-kg)</td>
    <td>Records every breakthrough and lesson into the Second Brain for future sessions.</td>
</tr>
</tbody>
</table>

<h2 class="section-title">6. The Six Layers of the Outer Harness in Practice</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8pt;">
    <div class="card">
        <div class="card-title">1. Guides (The Rulebook)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Clear instructions, role limits, and playbooks loaded before starting any task.</p>
    </div>
    <div class="card">
        <div class="card-title">2. Sensors (The Smoke Alarms)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Automated tests and fail-closed checks that detect errors before customers see them.</p>
    </div>
    <div class="card">
        <div class="card-title">3. The Loop (The Factory Line)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Disciplined workflow: One issue &rarr; one branch &rarr; one merge request.</p>
    </div>
    <div class="card">
        <div class="card-title">4. Memory (The Vault)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Preserves lessons and daily handoffs so past mistakes are never repeated.</p>
    </div>
    <div class="card">
        <div class="card-title">5. Permissions (The Keycard)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Strict controls over who can touch sensitive customer data, budgets, or servers.</p>
    </div>
    <div class="card">
        <div class="card-title">6. Observability (The Dashboard)</div>
        <p style="margin: 0; font-size: 7.8pt; color: #475569;">Real-time Grafana telemetry proving the entire system is healthy with hard facts.</p>
    </div>
</div>

<div class="footer-callout">
    <strong>✨ Core Philosophy:</strong> "The engineers who thrive in the AI era are not the ones who write the most code. They are the ones who build the best environments for AI agents and human teams to stay honest."
</div>

</body>
</html>
"""

HTML_OUT = PDF_DIR / "aea-framework-harness-engineering-visual-guide-2026-09-01.html"
HTML_CANON = PDF_DIR / "aea-framework-harness-engineering-visual-guide.html"
PDF_OUT = PDF_DIR / "aea-framework-harness-engineering-visual-guide-2026-09-01.pdf"
PDF_CANON = PDF_DIR / "aea-framework-harness-engineering-visual-guide.pdf"
PDF_ARTIFACT = ARTIFACT_DIR / "aea_framework_harness_engineering_visual_guide_2026_09_01.pdf"

HTML_OUT.write_text(html_content, encoding='utf-8')
shutil.copy2(HTML_OUT, HTML_CANON)

print(f"Generating PDF: {PDF_OUT}...")
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=True
    )
    page = browser.new_page()
    page.goto(HTML_OUT.resolve().as_uri(), wait_until='networkidle')
    page.pdf(
        path=str(PDF_OUT),
        format='A4',
        print_background=True,
        margin={'top': '16mm', 'bottom': '16mm', 'left': '15mm', 'right': '15mm'}
    )
    browser.close()

shutil.copy2(PDF_OUT, PDF_CANON)
shutil.copy2(PDF_OUT, PDF_ARTIFACT)

print(f"Generated: {PDF_OUT}")
print(f"Generated: {PDF_CANON}")
print(f"Copied to artifact: {PDF_ARTIFACT}")
