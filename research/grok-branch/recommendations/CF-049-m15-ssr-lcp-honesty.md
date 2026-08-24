# Recommendation: CF-049 — M15 SSR / LCP honesty

> **Finding:** CF-049 (High)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner:** `@aea-coherence-guardian` (+ `@aea-performance-guardian` for copy)  
> **Suggested branch:** `fix/cf-049-m15-ssr-lcp-honesty`  
> **Depends on:** Prefer after CF-048 (brief will keep re-stating M15 claims otherwise)  
> **Do not merge from this sandbox.**

## Problem

1. Roadmap titles **M15** as “Edge SSR & Progressive Hydration” and cites “sub-100ms LCP benchmark scripts.”
2. `scripts/audit_lcp_performance.py` sets `lcp_score = t_first_byte` and prints “ESTIMATED LCP SCORE.”
3. Edge reality: Nginx `try_files /index.html =404` serves a **static SPA shell**; `edge/gateway/ui/index.html` loads `app.js` client-side. That is not session-aware SSR and TTFB is not browser LCP.

## Desired outcome

- Roadmap and scripts describe what exists: static shell + TTFB/DOM-marker audit helpers.
- No claim that browser LCP or SSR is measured or shipped until Web Vitals instrumentation and (optional) real SSR exist.
- Product work for true SSR/LCP remains a **separate** future issue—not this MR.

## Proposed change (focused)

### A. `docs/07-roadmap/roadmap.md` — M15 row

Replace title/focus wording along these lines:

- **Title:** e.g. `Edge static shell & TTFB audit helpers (Reference Extension)`
- **Focus:** Nginx static HTML shell, client hydration hooks as present in UI assets, TTFB/DOM-presence audit script. **Browser LCP and true SSR remain Future.**
- Keep NFR-002/NFR-004 as related NFRs without asserting they are fully met by TTFB.

### B. `scripts/audit_lcp_performance.py`

- Rename user-facing strings: “TTFB audit” not “LCP performance audit.”
- Keep measuring TTFB; label output `ttfb_ms` only.
- Remove or clearly qualify “ESTIMATED LCP SCORE” (e.g. delete LCP grade, or print `NOTE: TTFB is not browser LCP`).
- Docstring: state that browser LCP requires Web Vitals (lab or RUM), not this script.

### C. Optional one-line cross-refs

- If `scripts/generate_daily_brief.py` still mentions M15 after CF-048, ensure neutral wording matches A.
- Do not change Nginx routing or implement SSR in this MR.

## Out of scope

- Implementing SSR, progressive hydration product behavior, or CI Web Vitals.
- Changing NFR definitions in the workbook.

## Acceptance checks

- [ ] Roadmap M15 does not claim shipped SSR or measured browser LCP
- [ ] Audit script does not present TTFB as LCP
- [ ] `python scripts/run_all_guards.py` still clean (or only expected doc-related noise)
- [ ] Single finding only in the MR

## Manual GitLab steps

1. Issue linked to CF-049 → branch `fix/cf-049-m15-ssr-lcp-honesty` from `main`
2. Apply A + B
3. Focused MR → `@aea-mr-coordinator` when green

## Evidence paths

- `docs/07-roadmap/roadmap.md` (M15 row)
- `scripts/audit_lcp_performance.py`
- `edge/gateway/nginx.conf` (`try_files /index.html`)
- `edge/gateway/ui/index.html` (client `app.js`)
