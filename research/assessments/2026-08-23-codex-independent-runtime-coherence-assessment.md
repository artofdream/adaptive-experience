# Coherence assessment — 2026-08-23 Codex independent runtime reconciliation

tags: #aea #coherence-assessment #runtime #milestones #codex
status: intake
assessed_ref: 9dfe00e9294beff8dfca09fbd7dcf9c28ec5c6a1
assessed_by: Codex / @aea-coherence-guardian

## Scope

- Paths reviewed: canonical requirements and roadmap, functional design, edge
  gateway/UI, platform services and migrations, AWS Terraform, reporting and
  performance scripts, tests, prior assessments, the CF queue, and live GitLab
  issue/MR metadata.
- Checks executed: `git fetch origin main`; `python scripts/run_all_guards.py`
  (14/14 passed); platform unit discovery (245 passed, 48 skipped); edge unit
  discovery (68 passed); targeted text/code inspection; live GitLab searches
  for equivalent issues; MR !267, !270, and !271 state inspection.
- Exclusions or limitations: no live browser/Web-Vitals trace, AWS inspection,
  Terraform apply, Docker integration run, archive mutation, or product-feature
  remediation. PostgreSQL integration tests were among the 48 environment-
  dependent skips. This assessment records intake only.

## Executive verdict

The repository is mechanically healthy but delivery-claim coherence is not.
The guard and unit suites establish internal consistency for the surfaces they
cover; they do not establish production SSR/LCP, applied extension migrations,
or correct milestone reporting. Six new, falsifiable coherence findings remain
after reconciliation against CF-001–047 and live GitLab.

## Findings

| Finding ID | Claim | Severity | Evidence paths | Existing issue / MR |
|------------|-------|----------|----------------|---------------------|
| CF-048 | The daily-brief publisher hardcodes `15/16` completed plus shipped M15 pre-render/sub-100ms claims, so regeneration overwrites honest runtime status with unsupported claims. | High | `scripts/generate_daily_brief.py`; `research/daily-briefs/2026-08-23-daily-brief.md`; `edge/gateway/nginx.conf`; `scripts/audit_lcp_performance.py` | No equivalent issue found; stale report MR !270 remains open. |
| CF-049 | M15 is titled Edge SSR and its audit labels TTFB as an estimated LCP score, although Nginx serves static SPA HTML and the script does not measure browser LCP. | High | `docs/07-roadmap/roadmap.md`; `edge/gateway/nginx.conf`; `edge/gateway/nginx-alb.conf`; `scripts/audit_lcp_performance.py` | No equivalent issue found. |
| CF-050 | Extension migrations 019–022 are outside the only migration runner's directory and therefore cannot be applied by the documented runtime path, while the roadmap cites their schemas as delivered reference-extension artifacts. | High | `platform/scripts/apply_migrations.py`; `platform/migrations/`; `platform/aea_platform/migrations/019_live_chat_tickets.sql` through `022_multi_tenant_isolation.sql`; `docs/07-roadmap/roadmap.md` | No equivalent issue found. |
| CF-051 | Published requirements narrative says “Staff CRM and live chat remain out of scope (FR-016 / FR-017),” but the canonical rows define FR-016 as reminders and FR-017 as engagement analytics; the roadmap simultaneously marks M12 completed against both IDs while excluding staff chat/ticketing. | Medium | `docs/02-business-analysis/requirements.md`; `archive/canonical-requirements.csv`; `docs/07-roadmap/roadmap.md`; `platform/aea_platform/crm.py` | No equivalent issue found; MR !267 is open and explicitly calls its implementation thin. |
| CF-052 | M14 says merchant-domain configuration is present, but committed Terraform defaults and examples configure only `aea.artof.link`; no Lily's Florist merchant domain is represented. | Medium | `docs/07-roadmap/roadmap.md`; `infra/aws/terraform.tfvars.example`; `infra/aws/variables.tf`; `infra/aws/outputs.tf` | No equivalent issue found. |
| CF-053 | M17 says the `pgvector` extension remains Future although migration 013 and both local Compose files already enable pgvector for the existing retrieval boundary. | Medium | `docs/07-roadmap/roadmap.md`; `platform/migrations/013_retrieval_pgvector.sql`; `platform/docker-compose.yml`; `edge/docker-compose.yml`; `docs/06-adr/ADR-014-postgresql-pgvector.md` | No equivalent issue found. |

## Intake reconciliation

| Finding ID | Decision | Queue status | Reason |
|------------|----------|--------------|--------|
| CF-048 | new | queued | No equivalent CF or GitLab issue; directly reproduced on assessed `origin/main`. |
| CF-049 | new | queued | No earlier CF covers measurement semantics or the SSR naming mismatch. |
| CF-050 | new | queued | No earlier CF covers the split migration roots or unreachable versions 019–022. |
| CF-051 | new | queued | CF-047 covers milestone descriptions generally, not this FR-016/017 semantic contradiction. |
| CF-052 | new | queued | No earlier CF covers the M14 merchant-domain artifact claim. |
| CF-053 | new | queued | No earlier CF covers the M17 pgvector-Future contradiction. |

## Reconciliation path

1. **CF-048 first:** make the daily-brief generator derive factual status and
   prevent it from republishing unsupported M15 assertions. Close or supersede
   stale MR !270 before it can restore stale output.
2. **CF-049:** separate browser-observed LCP from TTFB and rename M15 evidence
   honestly until a real SSR/progressive-hydration implementation and Web
   Vitals trace exist.
3. **CF-050:** choose one governed migration root and add coverage proving
   019–022 are discoverable and ordered. This is an engineering-boundary fix,
   not evidence that the related product features are complete.
4. **CF-051:** align FR-016/017 prose and M12 completion wording with the
   canonical reminder/analytics definitions and the actual thin service.
5. **CF-052 and CF-053:** correct the M14/M17 artifact descriptions against
   committed infrastructure and retrieval reality.

Each item requires its own later issue → branch → focused MR cycle. Product
hardening (Stripe, WebSocket chat, WebRTC, cross-region RDS) remains outside
this coherence intake and requires the owning stakeholder/product decision.

## Assessment conclusion

- New findings added: CF-048, CF-049, CF-050, CF-051, CF-052, CF-053
- Regressions reopened: none
- Duplicates linked: none
- Queue reordered: yes — High before Medium, publisher before dependent claims
- Next queued finding: CF-048

