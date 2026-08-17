# Design note — Florist operator UI (#170)

status: accepted (2026-08-15)
for_issues: "#170 (florist operator surface; not FR-016/017 CRM); #209 (named aea-pilot Path B exception)"
affects: "local Edge console; named aea-pilot BFF exception; thin operator reads; T-09 / FR-006 follow-up"
author: claude
date: 2026-08-15

> **Decisions (2026-08-15):**
> 1. Define a **staff operator possibility**, not a CRM product. #35 / #36
>    (FR-016 / FR-017) stay Future.
> 2. Separate route `/florist`, not a customer journey tile. Fail closed
>    unless `AEA_FLORIST_OPERATOR=1` and `AEA_ENVIRONMENT` is not `production`.
> 3. Thin **read** APIs over existing outbox + workspace/conversation
>    projections. No PII dump (NFR-017 / PayloadPrivacyGuard).
> 4. Order status mutation stays on existing internal fulfillment POSTs;
>    this slice does not call them.
>
> **Decision (2026-08-17, #209):** Path B `aea-pilot` keeps
> `AEA_ENVIRONMENT=production` (seeder fail-closed). Generic production still
> 404s florist even if the flag is set. A **named exception**
> `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot` may enable read-only operator
> GETs on that stack only. This does **not** write inventory, unblock T-03
> Select, or unpark FR-016 / FR-017. Do not open `/florist` in the same
> browser as the shop (CSRF).

## Grounding

- FR-006 / T-09: customer Contact Florist records
  `support.escalation.requested` (!159 / #25). Staff workspace was deferred.
- ADR-004: ASO (Lily / Help, FR-009) is distinct from T-09 human escalation.
  Live chat, staff CRM, and ticketing remain Future.
- FR-016 / FR-017 (#35 / #36): engagement reminders and CRM analytics — do
  not implement here.
- NFR-017: least-data payloads; opaque session/context references.

## Screens → routes vs gaps

| Operator view | Existing route | This slice | Gap (later) |
|---|---|---|---|
| Contact Florist inbox | Outbox rows for `support.escalation.requested` (write: `POST /internal/v1/sessions/{id}/support/escalation`) | `GET /internal/v1/operator/escalations` → BFF `GET /api/v1/operator/escalations` when enabled | Assignment, SLA, ticketing |
| Conversation transcript | `GET .../sessions/{id}/conversation` (least-data messages) | Included in `GET /internal/v1/operator/sessions/{id}` | Redaction workflow |
| Prior ASO answers | Outbox `support.faq.answered` / `support.situation.answered` | Included in the same session read (`support_answers`) | Unified support desk |
| Shared Understanding | `GET .../shared-understanding` (six facets) | Occasion/budget/etc. only | Staff edit of customer intent |
| Order / status / delay | Workspace `order` facet; internal `POST .../order/status` and `POST .../order/delay` | **Read** order_id, status, delayed, authoritative_status | Staff UI that POSTs fulfillment transitions |
| Inventory / availability | Workspace `recommendations[].availability_status` (`available` / `unknown` / unavailable) | Product id + status list | Catalog admin, production feed |
| Inventory forecast (FR-012) | Validated snapshot history (`inventory.availability_observation`) | `GET /internal/v1/operator/forecasts` → BFF `GET /api/v1/operator/forecasts` | ML demand models, purchase orders |
| FAQ vs escalation split | ASO `POST /api/v1/support` vs T-09 `POST /api/v1/support/escalation` | Explainer on `/florist`; inbox is T-09 only; session read shows prior ASO answers | Unified support desk |
| Live chat / billing CRM / FR-016/017 | None | Out of scope | #35 / #36 |

## Perimeter

- Gateway serves `/florist` → `florist.html` (labeled local sample). Customer
  `/` is unchanged.
- BFF operator GETs require the same bearer + session cookie as other Edge
  APIs, then look up **other** opaque session ids. Disabled → **404**.
- Production: `AEA_ENVIRONMENT=production` 404s florist even if
  `AEA_FLORIST_OPERATOR=1`, unless the named exception
  `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot` is also set. Generic production
  has no exception. Path B Terraform sets those two vars only when
  `local.prefix` is `aea-pilot`.
- Responses omit `subject_reference`, email, address, payment, and extra
  envelope fields.

## Not changing

- Customer T-03 Select, inventory seeder, PSP, AgentRuntime. #209 does not
  change that: the aea-pilot inbox still only **reads** availability already
  on the session.
- FR-006 write path (already delivered).
- Canonical requirement IDs (none invented).
