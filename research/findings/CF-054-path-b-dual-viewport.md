# Coherence finding — Path B dual viewport (phone linear, desktop workspace)

tags: #aea #coherence-finding
finding_id: CF-054
status: in-mr
severity: medium
source_assessment: 2026-08-27 J1–J4 live clips on https://aea.artof.link
supersedes:
issue: #272
branch: docs/272-path-b-dual-viewport-ux-loop
merge_request: !298

## Claim

On live Path B, the phone viewport copies the seven-step desktop Adaptive
Workspace (Start / Intent / Pick / Edit / Ship / Pay / Track) instead of a
linear concierge. Desktop and phone also use different step names for the
same flow. Dual presentation (one session, two layouts) is not implemented.

## Evidence

- Canonical source: live `https://aea.artof.link` (Lily's Florist), session
  cookie / `local-browser-token`, no password, no money spent. 2026-08-27
  evening Europe/Berlin.
- Conflicting or incomplete path: phone 375×667 device mode vs desktop
  1280×800. Phone 30s clips J1–J4 plus J1 E2E phone (~2:40) and desktop
  (~4:40). Vault note `research/random-thoughts/2026-08-27-path-b-dual-viewport-ux-loop-j1-j4.md`.
- Verification command: re-record the same J1 script on phone 9:16 and
  desktop 16:9 after a product UX merge. Unknown until those clips exist.

Honest leftovers in the 2026-08-27 tapes (not faked): J3 recall works, no
reorder badge. J4 is ASO fail-closed, not T-08. Track / Contact Florist stay
locked until checkout.

## Intended fix

This MR (!298) is knowledge and loop intake only: CF-054 row, Path B evidence
path in the coherence loop, finding note, session-memory log. No CSS/JS
restyle.

Product fix (later issue/branch/MR, same CF-054, `@aea-ux-designer`):
phone linear concierge (need → pick → pay, short progress, one primary CTA);
desktop keeps Adaptive Workspace; same step names on both. Do not shrink
the workspace onto 375px.

## Boundaries

- Included: queue row, SOP Path B paragraph, finding note, vault notes.
- Excluded: shop restyle, CRM #254, HLD #231, !297, DATE_RE, 15th hat.
- ID impact: none (existing [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] only)

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-27 | in-mr | #272 / !298 knowledge + loop; product UX still open |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-27 J1–J4 clips | first-seen | Sponsor asked to fold the clip loop into the coherence loop |

## Completion

- [x] Finding reproduced against live shop (clips, not docs)
- [x] Not already covered by an open issue or MR (new #272)
- [x] GitLab issue created (#272)
- [x] Dedicated branch created from updated `main`
- [x] Focused knowledge fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan (knowledge MR must **not** close the product finding)
- [ ] MR merged
- [ ] Post-merge verification passed on `main` (re-record both viewports after the **product** MR)
