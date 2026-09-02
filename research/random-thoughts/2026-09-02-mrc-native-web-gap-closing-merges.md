# MRC — native↔web gap-closing merges (2026-09-02)

> **Tags**: #aea #mrc #native-web #florist #companion
> **When**: 2026-09-02 evening Europe/Berlin

## Goal

Close native↔web gaps. MRC merges green GitLab MRs on project `85239039` (author-of-MR is not a gate).

## Merged this session

| MR | Issue | Merge SHA | Notes |
|---|---|---|---|
| !410 | #387 | `ec265d308e0c` | Companion inclusive budget band hides under-floor SKUs |
| !414 | #388 | `931a9a5bcb8b` | Preserve budget chip label through Pick/Pay (combined with band logic) |
| !417 | #380 | `bd473b817ebc` | Florist remove local-only Claim/Resolve (already green; merged during session) |
| !418 / session-facts | #383 #385 | on main earlier | Card/total/channel operator summary (pre-session) |

## Also merged (same evening)

| MR | Issue | Merge SHA | Notes |
|---|---|---|---|
| !408 | #389 | `6f1e1d8720d0` | Occasion-aware Pay card default |
| !419 | #390 (Related, left open) | `c1bd0cd16555` | Explicit release `isDebuggable=false` + Play honesty docs |
| !425 | docs | `e1ab229f89b5` | This knowledge brief |

!416 bundle closed as superseded by splits.

## #384 channel (aea_client) — still open

Code on `main` (!409 migration 023 + operator session-facts) shapes `channel`, but **live** `aea.artof.link`:

- `GET /api/v1/operator/sessions/{id}` order payload lacks `channel`
- `GET /api/v1/operator/orders` → HTTP 500

**Remaining:** platform redeploy + migration 023; confirm edge; live prove channel allowlist. Optional ROG `companion-android` (#381).

## Redeploy note (#383–#385 on florist)

Edge/florist **assets** already show Channel in sample UI, but operator API enrichment is not live. **Yes — edge + platform redeploy** (especially platform/DB migration) is required for #383–#385 fixes to show on live `aea.artof.link/florist` for real sessions (not sample-only).
