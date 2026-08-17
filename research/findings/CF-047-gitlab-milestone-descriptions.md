# Coherence finding — GitLab group milestone descriptions stale

tags: #aea #coherence
finding_id: CF-047
status: verified
severity: medium
source_assessment: research/assessments/2026-08-16-coherence-impl-status.md
issue: "#206"
branch: docs/restore-roadmap-m8-m12
merge_request: "!211"
verified_on_main: 7cae086
supersedes:

## Claim

Group milestone *descriptions* for M4–M7, Future Backlog, and UX alignment
still list pre-CF-041 coverage (M5 NFR-014, M6 NFR-008, M7 NFR-010; Future
names FR-003 type/colour/ribbon as undelivered) and UX alignment still says
current #154 / #148. After !195 those GitLab descriptions and M8–M12
milestones match the roadmap as landed in !195. Published
`docs/07-roadmap/roadmap.md` on `origin/main` (`0d86918`) does **not**:
`#190` merge `542ec78` overwrote the !195 table. Main still has the old
Future Backlog row (FR-008, FR-016, FR-017, NFR-008, NFR-010 in that cell)
and no M8–M12 table rows.

## Evidence

- Canonical source: `docs/07-roadmap/roadmap.md` on `origin/main` `7cae086`
  (`Merge branch 'docs/restore-roadmap-m8-m12' into 'main'`, !211 / #206)
- Prior cycle: #191 / !195 (GitLab descriptions + M8–M12 milestones created)
- Conflicting path (resolved): published table missing M8–M12 after `542ec78`
- Verification command: `git show origin/main:docs/07-roadmap/roadmap.md`
  plus `glab api groups/artof-group/milestones?per_page=100`

Post-merge verify 2026-08-17 against `origin/main` `7cae086`: GitLab group
milestone descriptions for M4–M7, M8–M12, Future Backlog, and UX alignment
match the published roadmap coverage. Original stale claims are gone
(M5 no longer lists NFR-014 as current; M6 NFR-008 → M9; M7 NFR-010 → M11;
Future no longer names FR-003 type/colour/ribbon as undelivered; UX lists
#153 / #154 / #148 as closed). M8–M12 table rows are restored. Extra GitLab
notes (#190 / !194 first slice, #50 on M9, do-not-start-M12-while-M8-open)
are consistent with roadmap Notes.

## Intended fix

Restore the published M8–M12 rows and Future Backlog remainder wording from
!195. Do not reuse merged !195 / closed #191. Keep later notes about M8
first slices (#190 / #193). Workbook scopes unchanged.

## Boundaries

- Included: `docs/07-roadmap/roadmap.md` table rows M8–M12 + Future Backlog remainder
- Excluded: GitLab milestone APIs (already aligned); M12 CRM implementation; #196 / #204 / #205
- ID impact: none / existing IDs only

## Iteration log

| Date | State | Evidence / action |
|------|-------|-------------------|
| 2026-08-16 | in-mr | #191 / !195 named M8–M12 and aligned GitLab descriptions |
| 2026-08-17 | investigating | Post-merge verify: GitLab descriptions match !195; published table on main does not (`542ec78` overwrite). Status not verified. |
| 2026-08-17 | in-mr | New cycle: #206 / !211 on `docs/restore-roadmap-m8-m12` restores the published table. Status not verified. |
| 2026-08-17 | verified | !211 merged to main (`7cae086`). GitLab M4–M7 / M8–M12 / Future / UX descriptions match `docs/07-roadmap/roadmap.md` on `origin/main`. |

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-16-coherence-impl-status | first-seen | GitLab descriptions stale vs CF-041 roadmap |
| 2026-08-17 verify tick | still open | Descriptions fixed; published M8–M12 table missing on main |
| 2026-08-17 verify tick | resolved | !211 on main `7cae086`; GitLab descriptions match published table |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created
- [x] Dedicated branch created from updated `main`
- [x] Focused fix committed and pushed
- [x] Relevant checks passed
- [x] MR includes `Closes #N`, summary, and test plan
- [x] MR merged
- [x] Post-merge verification passed on `main`
