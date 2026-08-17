# Coherence finding — GitLab group milestone descriptions stale

tags: #aea #coherence
finding_id: CF-047
status: in-mr
severity: medium
source_assessment: research/assessments/2026-08-16-coherence-impl-status.md
issue: "#206"
branch: docs/restore-roadmap-m8-m12
merge_request: "!211"
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

- Canonical source: GitLab group milestones M8–M12 / Future as landed in !195
- Conflicting or incomplete path: `docs/07-roadmap/roadmap.md` @ `origin/main` `0d86918`
- Verification command: `git show origin/main:docs/07-roadmap/roadmap.md` (no M8–M12 table rows)

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

## Assessment history

| Assessment | Result | Notes |
|------------|--------|-------|
| 2026-08-16-coherence-impl-status | first-seen | GitLab descriptions stale vs CF-041 roadmap |
| 2026-08-17 verify tick | still open | Descriptions fixed; published M8–M12 table missing on main |

## Completion

- [x] Finding reproduced against updated `main`
- [x] Not already covered by an open issue or MR
- [x] GitLab issue created
- [x] Dedicated branch created from updated `main`
- [ ] Focused fix committed and pushed
- [ ] Relevant checks passed
- [ ] MR includes `Closes #N`, summary, and test plan
- [ ] MR merged
- [ ] Post-merge verification passed on `main`
