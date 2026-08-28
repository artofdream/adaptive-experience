# Coherence finding — Path B dual viewport (phone linear, desktop workspace)

tags: #aea #coherence-finding
finding_id: CF-054
status: regressed
severity: medium
source_assessment: 2026-08-27 J1–J4 live clips on https://aea.artof.link
supersedes:
issue: #273 (related; #272 was closed by spec)
branch: docs/273-cf054-clip-verify-after-css
merge_request:

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
  Live J1 phone+desktop re-record after CSS !300 (`63aaa4ce`): **Unknown**.

Honest leftovers in the 2026-08-27 tapes (not faked): J3 recall works, no
reorder badge. J4 is ASO fail-closed, not T-08. Track / Contact Florist stay
locked until checkout.

## Intended fix

This MR is SOP and queue honesty only: set CF-054 `regressed` because
`verified` was claimed without a journey×viewport clip dated after the
product/CSS merge. No CSS/JS restyle.

Path B `verified` requires a clip dated after CSS. Closing GitLab from a
spec or CSS MR is not verification. #272 was closed by spec !299; CSS
!300 merged; clip after CSS remains Unknown. Treat as CF-054 regression,
not a new CF-055.

Product/clip work stays with `@aea-ux-designer` / `@aea-customer-journey`.

## Boundaries

- Included: queue row, SOP Path B paragraph, finding note, vault notes.
- Excluded: shop restyle, 3DX Lab, #274, #275, CRM #254, HLD #231, DATE_RE, 15th hat.
- ID impact: none (existing [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] only)

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-27 | in-mr | #272 / !298 knowledge + loop; product UX still open |
| 2026-08-28 | regressed | CSS !299/!300 merged; queue said verified without post-CSS clip; set regressed; #273 SOP |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-27 J1–J4 clips | first-seen | Sponsor asked to fold the clip loop into the coherence loop |
| 2026-08-28 honesty probe | regression | Queue `verified` with no clip dated after CSS !300; CF-048-class honesty miss |

## Completion

- [x] Finding reproduced against live shop (clips, not docs)
- [x] Not already covered by an open issue or MR (new #273; #272 closed by spec)
- [x] GitLab issue created (#273 related; #272 closed by spec)
- [x] Dedicated branch created from updated `main`
- [x] Focused knowledge fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan (this SOP MR must **not** `Closes #273`; clip after CSS does not exist)
- [ ] MR merged
- [ ] Post-merge verification passed on `main` (re-record both viewports after the **product** MR; clip after CSS **Unknown**)
