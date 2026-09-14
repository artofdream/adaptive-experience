# Session Memory Log: Path B dual-viewport LIVE probe (2026-09-14)

> **Tags**: #aea #session-memory #path-b #ux #dual-viewport #honesty #second-brain #knowledge-first
> **Captured**: 2026-09-14
> **Author**: `@aea-knowledge-guardian` with `@aea-ux-designer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **GitLab**: [#440](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/440) (this vault MR) · related open [!518](https://gitlab.com/artof-group/adaptive-experience-architecture/-/merge_requests/518) / [#439](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/439) (CSS rem bumps — **open/pending** at time of writing)
> **Related**: [[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] · [[2026-09-14-session-memory-log-migrate-on-deploy-438-prove]]
> **This node is knowledge, not a UI restyle.** Screenshots lived under session `pathb-probe/` on the probe box; they are **not** committed here — text evidence only.

---

## 1. Why this note exists

Earlier vault status treated LIVE AEA dual layout as **Unknown** for this session class. On 2026-09-14 the Grok box probed LIVE `https://aea.artof.link` at two widths. This node records what was measured. It does **not** close #439. Do not invent image paths in GitLab.

## 2. What was probed (honest)

| Target | Viewport | Layout seen |
|---|---|---|
| `https://aea.artof.link` | ~1280px | Adaptive Workspace **7-step** |
| `https://aea.artof.link` | ~390px | Need→Pick→Pay **concierge** |
| `https://architecture.artof.link/path-b.html` | both widths | Page **renders** both viewports |

Mobile overflow (aea): `scrollWidth = clientWidth = 375` — **no horizontal overflow** this session.

## 3. Pre-fix computed mobile chrome (LIVE, before !518)

Measured computed font sizes on mobile Path B chrome (pre-fix):

| Element | Computed size |
|---|---|
| labels | 11.2px |
| step-num | 10.88px |
| caption | 12.8px |
| eyebrow | 11.52px |
| helper | 13.6px |

These sit below the preferred ≥14px chrome bar that DSO / UX called out. Fix slice is CSS rem bumps in **!518 / #439** — **still open/pending** when this vault note was written (not yet merged). Re-probe after merge before claiming chrome ≥14px live.

## 4. Still Unknown / not fully verified in docs

- Continuous dual-view **walkthrough** (same journey script recorded on both viewports end-to-end with clip evidence) remains **Unknown / not fully verified** in committed docs this session.
- architecture `path-b.html` rendering both viewports ≠ a full AEA continuous dual-view walkthrough prove.

## 5. Tracker honesty

- This vault MR closes **#440 only**.
- Do **not** `Closes #439` from this note. !518 owns the CSS fix.
- Do not claim !518 merged until it is merged on `main`.

## 6. Wikilinks

[[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] · [[2026-09-14-session-memory-log-migrate-on-deploy-438-prove]] · [[2026-09-14-session-memory-log-deploy-ecs-describetasks-accessdenied]]
