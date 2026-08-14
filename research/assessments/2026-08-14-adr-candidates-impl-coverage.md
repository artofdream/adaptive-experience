# Coherence assessment — 2026-08-14

tags: #aea #coherence-assessment
status: intake
assessed_ref: branch `docs/adr-013-confirmation-driven-experience` @ 5bec246; `origin/main` @ 996e301
assessed_by: cursor-agent

## Scope

- Paths reviewed: `docs/06-adr/`, `research/adr-candidates/`, `research/design-notes/`
  (post-move), `docs/02-business-analysis/requirements.md`, `platform/`, `edge/`,
  `research/coherence-findings-loop.md`, GitLab open issues (`scope::mvp` /
  `scope::future`)
- Checks executed: ADR candidate consolidation review; FR/NFR implementation
  coverage vs platform/edge/tests; `glab issue list` for open MVP/Future
- Exclusions: production SLO evidence; real PSP/catalog backends; live wiki
  (repo `wiki/` only)

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-043 | `research/adr-candidates/` mixed issue design notes with ADR Drafts, inviting CF-014-style renumber confusion | Low | Former `edge-workspace-projection-contract.md` et al. under `adr-candidates/`; edge README pointed there | — (fixed this pass → `research/design-notes/`) |
| CF-044 | FR-018 requires itemized taxes, discounts, and customization charges; `PricingService` implements product + flat delivery (+ $0 card message) only | Medium | `docs/02-business-analysis/requirements.md` FR-018; `platform/aea_platform/pricing.py` | — |
| CF-045 | NFR-007 / NFR-012 require encryption at rest for preference / delivery data; ADRs cite it but platform code shows references/TLS only, no encryption evidence | Medium | ADR-009/011; requirements NFR-007/012; no encrypt/TDE/KMS usage under `platform/` | — |
| CF-046 | ADR-013 Accepted on branch for confirmation-driven T-05…T-07 UX; T-07 still blank `payment_reference` re-entry (docs ahead of UX) | Low | `docs/06-adr/ADR-013-…`; `edge/gateway/ui/assets/app.js` checkout | Pending ADR-013 MR |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-043 | new | in-progress | Consolidation moved design notes; verify after merge |
| CF-044 | new | queued | Docs vs pricing depth gap; not covered by prior CFs |
| CF-045 | new | queued | Encryption claim vs code; distinct from privacy least-data CFs |
| CF-046 | new | queued | Activate after ADR-013 merges to `main`; else docs-only on branch |

## Assessment conclusion

- New findings added: CF-043…CF-046
- Regressions reopened: none
- Duplicates linked: none (CF-014 related cleanup continued as CF-043)
- Queue reordered: yes (medium before low among new queued)
- Next queued finding: **CF-044** (after CF-043 verify)
- Implementation coverage: MVP FR skeletons largely integration-tested; **0 open
  MVP issues**; open Future `#25 #27 #29 #31 #35 #36 #56`
- ADR candidates after consolidation: 3 active Drafts (pgvector, RAG, agentic);
  2 historical (confirmation→013, kafka→012); design notes relocated
