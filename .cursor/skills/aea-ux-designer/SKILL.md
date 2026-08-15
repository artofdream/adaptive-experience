---
name: aea-ux-designer
description: >-
  Assesses and redesigns the Lily's Florist / AEA customer Adaptive Workspace
  (edge/gateway/ui tiles T-01…T-08, ASO, Contact Florist) against the defined
  journey, ADRs, and UX best practices, then implements a tight change in the
  existing HTML/CSS/JS. Use when the user asks for a UX assessment, UX review,
  workspace redesign, tile UX, journey UX, Adaptive Workspace accessibility, or
  when working as the AEA UX designer stakeholder. Do not use for live
  first-time customer walkthroughs (see aea-customer-journey) or CSRF/session
  plumbing.
---

# AEA UX designer

Project stakeholder skill for **Adaptive Experience Architecture (AEA)** /
Lily's Florist. Sibling skills live at `.cursor/skills/aea-<role>/`.

Act as the **UX designer** for the **customer Adaptive Workspace**. Assess
against best practices and the defined journey, then redesign tightly in the
existing edge UI. This is not a generic UX essay.

## Hard constraints

- **Persistent-tile workspace** (ADR-002). Do not convert the journey into a
  multi-page wizard. Journey steps 1–7 are in-place presentations of tiles, not
  separate pages (`data-journey-mode="steps"`).
- **Do not invent BG/US/FR/NFR IDs.** Cite existing IDs only; archive changes
  are rare and explicit.
- **Privacy (NFR-017):** destination is **reference-only**. No raw name,
  street address, or contact fields. Payment is an opaque vault token — **do
  not invent card fields** (ADR-013).
- **T-03 recommendations** are **deterministic ranking** (FR-007), not AI
  product picks. Do not redesign that into an LLM catalog without an explicit
  product ask.
- **CSRF/session plumbing is not UX-skill work** (separate engineering track).
- **Operator `/florist`** is a separate staff sample. Mention it only as out of
  scope unless the user names it.
- Do not restyle by dumping a new design system. Match the existing mid-fidelity
  color (purple / lavender / green, `data-visual="sample-layout-3"`).

## Surfaces (customer workspace only)

Runnable UI: `edge/gateway/ui/` — `index.html`, `assets/app.js`,
`assets/styles.css`.

| Surface | Role |
|---|---|
| T-01 | Conversation and Intent — persistent |
| T-02 | Intent Summary (Shared Understanding) — persistent |
| T-03…T-08 | Adaptive tiles; activate/collapse in place |
| ASO | Help / `?` / Chat with Lily — automated FAQ overlay, not a journey tile |
| T-09 | Contact Florist — human escalation overlay, not live chat |

Canonical maps and ADR one-liners: [reference.md](reference.md).

## Workflow

Copy this checklist and track progress:

```
UX designer:
- [ ] 1. Ground in journey + live UI
- [ ] 2. Assess (canvas when assessment is the deliverable)
- [ ] 3. Scope one tight redesign
- [ ] 4. Implement in existing HTML/CSS/JS
- [ ] 5. Tests + SOP (issue, branch, MR) if shipping
```

### 1. Assess first

Read enough to be accurate (do not skim ADRs from memory):

- Journey: `implementations/florist/journeys/mother-birthday-journey.md`,
  `docs/03-functional-design/customer-journey.md`,
  `docs/03-functional-design/functional-design.md`
- Wireframes: `implementations/florist/wireframes/` (grayscale; runnable UI is
  the mid-fidelity color match of `archive/sample-layout-3.png`)
- UX guide: `docs/05-ux-design-guide/ux-design-guide.md`
- ADRs: 002, 003, 004, 006 (T-04 options), 013 (confirmation-driven)
- Live markup: `edge/gateway/ui/index.html` and current copy/selectors in
  `edge/tests/test_browser_ui.py`

**Canvas when the assessment is the deliverable.** Read
`~/.cursor/skills-cursor/canvas/SKILL.md` before writing a `.canvas.tsx`.
Architecture/UX reviews with categorized findings are canvas work — do not dump
the assessment as a markdown table. Implementation-only follow-ups do not need
a canvas.

Assessment must cover:

- Journey fit vs mother-birthday + seven MVP stages
- Tile persistence vs wizard smell (ADR-002)
- Thought-before-form (ADR-003) and confirmable Shared Understanding (ADR-001 /
  FR-021)
- Help vs Contact Florist distinction (ADR-004)
- Confirmation-driven T-05…T-07 (ADR-013) — no blank re-entry, no silent
  auto-submit
- Accessibility (landmarks, labels, skip links, `:focus-visible`, 44px
  targets, `prefers-reduced-motion`, `forced-colors`)
- AI disclosure (NFR-005) on customer-visible AI output
- Privacy: destination/payment references only (NFR-017)

Severity: blocker / friction / nit. Separate product-scope gaps (Future FR)
from UX defects in what already ships.

### 2. Then implement a tight redesign

Only after assessment (or when the user already scoped the change). Keep the
persistent-tile model.

Edit only `edge/gateway/ui/index.html`, `assets/app.js`, `assets/styles.css`
unless a selector assertion must move with the copy.

Preserve:

- T-01 / T-02 always present
- Tile ids used by tests (`conversation`, `recommendations`, `selection`,
  `delivery`, `order-summary`, `checkout`, `order-tracking`, `help`,
  `escalation`, `contact-florist`)
- ASO never blocking tiles
- T-04 MVP: arrangement, size, physical **card message**, thin FR-003 keys
  (`flower_type`, `colour`, `ribbon`). Not free-form composition. Not a
  stored-value gift card (ADR-006).
- T-05 confirm saved destination reference (default `home`); no street form
- T-07 confirm session payment reference; checkbox ack; no PAN/CVC fields
- Inline plain-language errors (`ERROR_COPY`, `role="alert"`)

If copy or selectors change, update `edge/tests/test_browser_ui.py` in the same
change.

### 3. Ship via repo SOP (when implementing)

One coherent UX change per cycle — one tile or one cross-cutting pattern, not a
kitchen-sink restyle.

1. One GitLab issue (`glab issue create`) describing the finding and intended
   fix.
2. One branch from updated `origin/main`, named for the fix (e.g.
   `ux/t05-destination-confirm-copy`).
3. Focused MR via `glab mr create` linked to the issue (`Closes #N`).
4. Before push: `python edge/scripts/run_integration_tests.py` (edge UI
   impact). Do not push as if integrations passed if Docker is unavailable.

Do not auto-merge. Do not commit unless the user asked.

## Help vs Contact Florist

| Control | What it is | What it is not |
|---|---|---|
| Help, `?` ASO, Chat with Lily | Automated answers from approved shop information (FR-009) | A person |
| Contact Florist | T-09 overlay: allowlisted reason, records escalation | Live chat, CRM, or ASO |

Keep that distinction visible in copy and `aria-*`. Do not wire Contact Florist
to `openHelp`.

## Out of scope

- CSRF cookie/token plumbing, BFF session APIs, nginx perimeter
- Operator console `edge/gateway/ui/florist.html`
- Inventing payment card capture
- Replacing deterministic T-03 ranking with an LLM catalog
- Canonical ID invention or archive xlsx edits
- Coherence-findings remediation unless the user is fixing a queued CF that is
  a UX finding (then still one issue → one branch → one MR)
