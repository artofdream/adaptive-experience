# Support coordinator — routing map

GitLab project: `artof-group/adaptive-experience-architecture` (`glab`).

Run `glab label list` before applying labels. Prefer existing labels
(`scope::mvp`, `scope::future`, `type::chore`, plus any category/priority
labels already in the project). If a category label is absent, write it in
the issue body.

## Categories

| Category | Typical symptoms | Default owner track |
|---|---|---|
| support | ASO FAQ wrong/missing; T-09 escalation; Help vs Contact Florist confusion | FAQ content / ADR-004; florist inbox follow-up |
| inventory | T-03 unknown/unavailable; Select 409; seeder vs production feed | inventory / FR-011; forecasts FR-012 are Future-depth |
| recommendations | Ranking/empty cards; treating T-03 as LLM picks | FR-007 deterministic ranking — not an LLM catalog |
| ordering/delivery | T-05 destination, T-06 summary, T-07 confirm, T-08 tracking | ADR-013 confirmation; no raw PII/card fields |
| workspace/UX | Tile persistence, copy, a11y, journey chrome | `aea-ux-designer` — do not restyle here |
| security/privacy | CSRF/`csrf_rejected`, session cookie, NFR-017 PII, destination refs | platform/edge engineering; **blockers** |
| platform/edge | BFF, gateway, Compose, session boot, perimeter | engineering; Docker integration before MR |
| docs/coherence | ID/count drift, wiki vs docs, CF queue | coherence SOP; one CF per MR |

## Known program classes

| Class | Route | Priority hint |
|---|---|---|
| CSRF/session after `/florist` minted a cookie (`!165` / `#171`) | security/privacy | **blocker** (customer cannot Send / Confirm Delivery) |
| UX redesign of Adaptive Workspace | workspace/UX | high if a journey step is wrong; else medium/low |
| E2E mother-birthday pain points | map each row; do not batch | blocker vs friction from the walk |
| Future FRs (FR-008 history recs; remaining FR-010/012 depth; FR-016/017 CRM) | docs/coherence or backlog `scope::future` | not an MVP blocker |
| Depth leftovers (PSP, live RAG, ML demand) | platform/edge + `scope::future` | low unless the user promoted them |

Thin FR-010 situational ASO and thin FR-012 forecasts already have a local
path. Do not reopen them as “missing CRM.” Remaining depth is not a support
outage.

## Florist inbox → issue

`https://localhost:8443/florist` (local sample). APIs (same bearer + session
as Edge, fail closed if operator flag off):

- `GET /api/v1/operator/escalations`
- `GET /api/v1/operator/sessions/{id}` (least-data)

Map each live row: allowlisted **reason** + opaque **session** → search
GitLab → reuse or open **one** issue in **support**. Next action is a human
follow-up on that session, not a chat widget.

Do not implement assignment, SLA, or ticketing fields.

## glab follow-up (no merge)

```bash
glab issue list --repo artof-group/adaptive-experience-architecture
glab issue view <n>
glab mr list --repo artof-group/adaptive-experience-architecture
glab mr view <n>
```

Create only when dedup misses:

```bash
glab issue create --repo artof-group/adaptive-experience-architecture \
  --title "<category>: <customer-visible problem>" \
  --label "scope::mvp" \
  --description "<priority, category, evidence, next action, related !MR>"
```

Omit `--label` values that `glab label list` does not show. Link MRs; never
`glab mr merge` from this skill.

## Hand-off

| If the next action is… | Invoke |
|---|---|
| Product accept/reject, slice in vs out, should we ship | `@aea-product-owner` |
| Walk the live shop to reproduce | `@aea-customer-journey` |
| Tight UI redesign in `edge/gateway/ui/` | `@aea-ux-designer` |
| One coherence gap on docs/IDs | coherence SOP, one CF |
| CSRF/session or BFF cookie | engineering — not UX copy |
| Process / bench / sequencing | `@aea-project-manager` |
| Secrets, budget, `terraform destroy` | Sponsor (human) |
