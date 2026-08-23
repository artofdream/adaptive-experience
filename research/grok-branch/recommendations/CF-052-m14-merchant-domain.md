# Recommendation: CF-052 — M14 merchant-domain claim

> **Finding:** CF-052 (Medium)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner:** `@aea-coherence-guardian` / `@aea-devsecops-platform`  
> **Suggested branch:** `fix/cf-052-m14-merchant-domain`  
> **Do not merge from this sandbox.**

## Problem

Roadmap **M14** claims “merchant domain config” as part of Production Go-Live & FinOps (Reference Extension).

Committed Terraform examples/defaults use **`aea.artof.link`** (and pilot exception flags)—not a multi-merchant domain configuration model for Lily’s Florist (or others).

## Desired outcome

Roadmap describes what is actually in tree: single canonical pilot domain example, PaymentSimulationEngine / Stripe **mock**, FinOps right-sizing notes. Live multi-merchant domains and live Stripe remain Future.

## Proposed change (focused)

### `docs/07-roadmap/roadmap.md` — M14 row

Adjust focus text, e.g.:

- PaymentSimulationEngine / Stripe **mock**, Terraform **example** domain `aea.artof.link` (pilot), FinOps right-sizing policies.
- **Not claimed:** multi-merchant domain matrix, live Stripe SDK, staff OAuth2.

Optional: one sentence under Notes pointing at `infra/aws/terraform.tfvars.example` as the example host.

## Out of scope

- Implementing multi-tenant DNS/domain routing
- Live Stripe integration

## Acceptance checks

- [ ] M14 no longer implies multi-merchant domain config is present
- [ ] Terraform example paths cited accurately if mentioned
- [ ] Doc-only MR; guards green

## Manual GitLab steps

1. Issue CF-052 → `fix/cf-052-m14-merchant-domain`
2. Roadmap (and optional infra README cross-link) only
3. MR

## Evidence paths

- `docs/07-roadmap/roadmap.md` (M14)
- `infra/aws/terraform.tfvars.example`
- `infra/aws/variables.tf` (default `domain_name`)
