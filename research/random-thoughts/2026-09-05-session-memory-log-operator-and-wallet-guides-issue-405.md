# Session Memory Log: Florist Operator and Customer Edge Wallet User Guides (Issue #405)

> **Tags**: #aea #session-memory #operator-guide #edge-wallet #customer-guide #fr-013 #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-05 ~09:50 Europe/Berlin (07:50 UTC)
> **Author**: `@aea-knowledge-guardian` & `@aea-ux-designer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[2026-09-04-session-memory-log-florist-operator-mobile-ux]] · [[2026-09-04-session-memory-log-companion-edge-wallet-reorder-issue-404]] · `docs/05-ux-design-guide/florist-operator-guide.md` · `docs/05-ux-design-guide/customer-edge-wallet-guide.md` · `docs/framework/path-b.md` · `docs/framework/companion.md` · `edge/gateway/ui/florist.html`

---

## 1. Context & Motivation

While the underlying architecture, data schemas, and UI components for both the **Florist Operator Console** (`/florist`, FR-013) and the **Customer Edge Wallet** (ADR-020, FR-008) were fully implemented and verified in code and physical device testing, the project lacked dedicated, human-facing operational guides:
- The website explained the *architectural theory* (thin clients, Tink hardware encryption, least-data models), but did not provide a step-by-step *shift runbook* for atelier staff working on the floor.
- Shoppers using the companion app had no clear, plain-language customer guide explaining why Lily's Florist doesn't require a password/account, what stays strictly on their phone, and how 1-tap reordering works.
- GitLab Issue [#405](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/405) was opened to author both guides across a unified 3-tier delivery: canonical reference manuals, public website integration, and in-console operator ergonomics.

---

## 2. Key Architectural Decisions & Deliverables

### A. Canonical Operator Manual (`docs/05-ux-design-guide/florist-operator-guide.md`)
- Detailed operational guide for atelier florists, managers, and fulfillment staff across desktop, tablet, and mobile phone.
- Documents the **4-Step Daily Shift Routine**:
  1. *Morning Batching (`#prepare`)*: Tallying arrangements, delivery windows (Morning, Afternoon, Evening), and tapping `Details ↗` to view and transcribe full handwritten enclosure card messages in the bottom sheet.
  2. *Order Assembly (`#orders`)*: Working through the `Today` queue, checking channel badges (`web` vs `companion-android`), and matching cards to physical delivery boxes.
  3. *Customer Inquiries (`#inbox`)*: Triaging real-time Contact Florist escalations (T-09) and navigating directly to customer session transcripts.
  4. *End-of-Day Review*: Filtering by `Delayed` to confirm zero missed orders, and checking `3 days` / `7 days` to plan flower cooler replenishment.
- Multi-device ergonomics: explains the 9-column desktop table vs. the 3-column mobile phone collapse, jump navigation pills, and circular floating scroll buttons (`↑` / `↓`).
- Reassures staff regarding least-data privacy (zero PII, NFR-017).

### B. Canonical Customer Privacy & Edge Wallet Guide (`docs/05-ux-design-guide/customer-edge-wallet-guide.md`)
- Explains in reassuring, plain language why Lily's Florist avoids centralized customer CRM honeypots.
- Breaks down the **exact boundary** between what stays on the phone (recipient names like *"Mom"*, card message drafts, local receipts) and what is sent to the atelier (anonymous session ID, arrangement SKU, scheduled delivery time, and the physical message to print).
- Details the **1-Tap Reorder Flow (FR-008)**: how opening the app or starting over surfaces the private returning customer card, checks cooler stock via the BFF without transmitting PII, and transitions directly to `PICK`.
- Details customer sovereignty and the **Right to be Forgotten**: automatic 14-day address shredding and on-demand local wallet wipes.

### C. Public Framework Website Integration
- Enriched [`docs/framework/path-b.md`](file:///c:/projects/code/adaptive-experience/docs/framework/path-b.md) with a dedicated sub-section: *"Atelier Shift Routine: 4 Daily Steps for Shop Staff"*.
- Enriched [`docs/framework/companion.md`](file:///c:/projects/code/adaptive-experience/docs/framework/companion.md) with a dedicated sub-section: *"Shopper Privacy & Edge Wallet Guide: How Reordering Works"*.
- Rebuilt all 9 public HTML pages via `python scripts/build_framework_site.py`.

### D. In-Product Operator Ergonomics (`edge/gateway/ui/`)
- Added an accessible `? Help` button to `.operator-nav` in `florist.html`.
- Implemented `<dialog id="operator-help-dialog">` displaying the 4 shift steps and navigation/privacy tips with a clean "Got it" primary button.
- Wired open/close and backdrop click listeners in `florist.js` adhering to WCAG 2.1 touch target (min 44px) and keyboard accessibility (`Esc` dismiss).
- Styled dialog list and note elements in `styles.css`.
- Added unit tests in `edge/tests/test_browser_ui.py` asserting the dialog, triggers, and CSS classes.

---

## 3. Evidence & Verification

- **Edge Browser UI Tests**: `python -m unittest edge/tests/test_browser_ui.py` -> **Ran 26 tests in 0.020s, OK**.
- **Public Site Generator**: `python scripts/build_framework_site.py` -> **All 9 pages built cleanly in `public/`**.
- **Unified Quality Guards**: `python scripts/run_all_guards.py` -> **14/14 pre-flight quality guards passed cleanly**.

---

## 4. Architectural Invariants Preserved

| Principle | Enforcement |
|---|---|
| **Zero-PII / NFR-017** | Guides reinforce that no customer names, phones, or permanent profiles are collected or exposed. |
| **Fail-Closed Availability** | Documented that operator APIs fail closed (`404` / `403`) unless `AEA_FLORIST_OPERATOR=1` is explicitly enabled. |
| **Traceability & No ID Invention** | Cites only canonical IDs: FR-013, FR-012, FR-008, T-09, ADR-020, NFR-017. |
