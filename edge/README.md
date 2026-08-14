# BFF and Edge API Gateway

This directory implements the M1 browser perimeter defined by ADR-007 and
ADR-010. Browser traffic terminates at the TLS gateway and reaches the BFF;
neither component owns experience state, workflow, context versions, or domain
validation.

## Local startup

```sh
docker compose -f edge/docker-compose.yml up --build --wait
```

The integration runner (`python edge/scripts/run_integration_tests.py`) also
builds the stack, then tears it down.

The local HTTPS endpoint is `https://localhost:8443`. Its certificate is
ephemeral and self-signed. The local bearer token is a non-production fixture
declared in Compose; production authentication material must come from the
deployment environment.

The root URL serves the florist Adaptive Workspace from Figma Discovery v0.1
(`adaptive-workspace-mvp`): permanent Discovery (T-01 conversation + T-02 Shared
Understanding), a seven-stage journey navigator (ADR-002 /
`customer-journey.md`), and in-place activation of Adaptive Workspace tiles
T-03…T-08 (only the active stage’s tiles are shown). ASO remains a help overlay,
not a journey step. Visual chrome matches `archive/sample-layout-3.png` (purple /
lavender / green). The shell is driven by the Edge APIs (`/api/v1/session`,
conversation, shared-understanding, workspace, stream, selection, delivery,
order, checkout, support). NFR-001 landmarks, correction reassurance, keyboard
focus, and the help dialog remain; usability research remains the production
validation method. T-04 exposes Arrangement, Size, Card message, and thin
FR-003 selects (flower type, colour, ribbon) per ADR-006 amended. GitLab #155
tracks the seven-step navigation shell.

The UI uses standards-based HTML, CSS, and JavaScript for current evergreen
desktop, tablet, and mobile browsers. Its tested viewport contract is:

- desktop above 960px: conversation and Shared Understanding remain side by side;
- tablet from 641px to 960px: primary regions form one column and tiles form two;
- mobile through 640px: one-column reading order, full-width primary action,
  minimum 44px interactive targets, wrapping user content, and compact progress.

Reduced-motion and forced-colour preferences are preserved. Release validation
must cover the current two major versions of Chrome, Edge, Firefox, and Safari,
plus Chrome on Android and Safari on iOS; automated structural assertions guard
the responsive contract in every pipeline.

The BFF container has no host port. Nginx is the only published backend entry
point and strips internal identity headers before proxying. Browser assets,
responses, and logs contain no PostgreSQL or Kafka connection details.

## API boundary

Wired end-to-end through authenticated `HttpOrchestration` to Internal
Orchestration (M2 Conversation and Shared Understanding):

- `POST /api/v1/session` creates an opaque browser session and CSRF token, then
  ensures the matching internal experience session.
- `POST /api/v1/conversation/messages` accepts a T-01 customer message and
  returns its message ID, correlation ID, and new context version immediately;
  AI processing continues asynchronously through `customer.message.submitted`.
- `GET /api/v1/conversation` returns the authenticated session's least-data
  conversation projection (up to 50 visible messages).
- `GET /api/v1/shared-understanding` returns only the six governed intent facets,
  current context version, and up to three thought-completion suggestions.
- `PATCH /api/v1/shared-understanding` delegates partial corrections with the
  authenticated subject, correlation ID, and observed context version.
- AI-derived conversation acknowledgements and Shared Understanding projections
  always include `ai_generated`, the active `assistant_mode`, and a plain-language
  disclosure telling customers to review and correct the interpretation
  (NFR-005). These fields remain present when the availability fallback is used.
- `GET /healthz` is an unauthenticated liveness check without dependency data.

Reactive workspace substrate, wired end-to-end through `HttpOrchestration` to
Internal Orchestration (#144; contract in
`research/adr-candidates/edge-workspace-projection-contract.md`):

- `GET /api/v1/workspace` returns one least-data aggregate projection at the
  current context version. Tiles are namespaced facets: `conversation`,
  `shared_understanding`, `recommendations` (T-03, availability-aware, each item
  carrying a real-time `available` badge from `InventoryAvailabilityService` -
  FR-011/FR-007), `selection` once a product is chosen, `delivery` once scheduled,
  `order_summary` (T-06, the itemized FR-018 breakdown recomputed from the current
  decisions), and `order` (T-08 tracking: order_id, status, delayed, and the
  latest `authoritative_status` per FR-023). The browser renders one coherent
  snapshot instead of racing per-tile fetches.
- `POST /api/v1/selection` selects a recommended product (`product_id`,
  `observed_context_version`, and optional `options` for eligible `size`,
  physical `card_message`, and thin FR-003 keys `flower_type` / `colour` /
  `ribbon` per ADR-006 amended -
  `docs/04-technical-architecture/t04-card-message-contract.md`). Unknown keys
  and gift-card value fields are rejected at the edge.
  Orchestration revalidates availability authoritatively at selection time,
  records `decisions.product`, and emits the governed `product.selected` event
  exactly once at the new context version. Unavailable/stale inventory returns
  409; the recommendations read surface stays the workspace facet (there is no
  standalone `GET /api/v1/recommendations`).
- `POST /api/v1/delivery` records the FR-014 delivery decision (`timing` = date +
  window, and an opaque `destination_reference`). Recipient details are
  reference-only: raw recipient name/address/contact are rejected at the edge, so
  no personally identifiable recipient data enters experience state or the
  governed `delivery.details.updated` event. The workspace `delivery` facet
  exposes only the timing and the reference.
- `POST /api/v1/order` creates the FR-013 order once the product and delivery
  decisions are assembled; it returns the `order_id` and `status`. Missing
  decisions return 422 `order_incomplete`. Creation is idempotent per session, and
  the workspace `order` facet surfaces `order_id` + `status`.
- `POST /api/v1/support` answers a customer question (FR-009/FR-005). It accepts
  only `{question}` and returns `{answer, approved_source_references, matched}`.
  Answers come only from approved product/policy information; an unmatched question
  returns a safe no-approved-information answer (never fabricated). Human
  escalation is Future (FR-006).
- `POST /api/v1/checkout` performs FR-019 payment and checkout. It accepts only a
  `payment_reference` (an opaque vault token) and the `observed_total`; raw card
  fields (`card_number`, `cvv`, ...) are rejected at the edge (NFR-013). Checkout
  returns `202 accepted` with `pending: true`; authorization runs in the payment
  consumer (#148). Observe `order.confirmed` (or a decline) via workspace/stream.
  A stale `observed_total` or an already-confirmed order returns 409.
- `GET /api/v1/stream` is the reconnectable SSE contract. A cold connection
  receives one `snapshot` event carrying the workspace; a reconnection with
  `Last-Event-ID` (or `?after=`) receives only the `invalidation` deltas it
  missed, each naming the projections that must regenerate (derived from the
  `projection_dependency` registry). Event IDs are the monotonic context version.

`POST /api/v1/commands` is intentionally deferred: selection and later actions
use dedicated endpoints (e.g. `POST /api/v1/selection`, #142). The generic
command envelope is not adopted until deliberately standardized, so the route
validates transport shape and fails closed (`orchestration_unavailable`).

The integration runner builds the containers, waits for both health checks,
verifies the HTTPS gateway, and executes ten standard assistant queries through
the real TLS, authentication, BFF, and Orchestration path. The run reports p95
and maximum latency and fails if any measured response exceeds the NFR-004
three-second limit. This reference-path guard complements the 2.5-second maximum
AI-provider timeout; production deployments must retain equivalent percentile
telemetry for their configured provider and infrastructure. The runner always
tears the stack down. Run
`python -m unittest discover -s edge/tests -v` for the same security and
boundary suite used by GitLab CI. The BFF
uses an authenticated `HttpOrchestration` adapter. Runtime configuration
requires `AEA_ORCHESTRATION_URL` and `AEA_ORCHESTRATION_TOKEN` and fails closed
without them. The BFF holds no PostgreSQL or Kafka credentials; validation and
mutation authority remain in the internal Orchestration service.
