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

## Optional live intent (LiteLLM)

Default Compose leaves `AEA_AI_*` unset, so orchestration uses
`ReferenceIntentInterpreter` (regex). That is a supported mode.

To opt in to the live OpenAI-compatible path, create `platform/.env` from
`platform/.env.example` (never commit it), put an Anthropic key from
[console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
in `ANTHROPIC_API_KEY`, and start the overlay:

```sh
docker compose --env-file platform/.env -f edge/docker-compose.yml -f edge/docker-compose.litellm.yml up --build --wait
```

The overlay starts LiteLLM (`ghcr.io/berriai/litellm:main-latest`, rolling tag
for current Anthropic ids) and sets all three `AEA_AI_*` on orchestration to
`http://litellm:4000/v1/chat/completions`, the local `LITELLM_MASTER_KEY`
fixture, and `AEA_AI_MODEL` (default `claude-sonnet-5`). Anthropic native
`/v1/messages` will not work with `OpenAICompatibleIntentInterpreter`.
`localhost:4000` from inside the orchestration container will not reach the
proxy; Compose DNS is required.

Orchestration listens on 8081 inside the compose network and is not published
to the host. After the overlay is up:

```sh
docker compose -f edge/docker-compose.yml -f edge/docker-compose.litellm.yml exec orchestration python -c "import urllib.request; r=urllib.request.Request('http://127.0.0.1:8081/internal/v1/ai/health', headers={'Authorization':'Bearer local-internal-token','x-subject-reference':'health'}); print(urllib.request.urlopen(r).read().decode())"
```

Expect `{"available": true, "mode": "primary", "circuit": "closed"}` when the
live interpreter is constructed. `available` is true even on regex fallback
(NFR-003); `mode` is what tells you the primary path is wired. Host uvicorn
(not Compose) uses `http://localhost:8081` with `Authorization: Bearer` plus
`x-subject-reference`, and `AEA_AI_ENDPOINT=http://localhost:4000/v1/chat/completions`
only if LiteLLM's 4000 is published on the host.

## Local inventory seeder

Postgres starts empty. `InventoryAvailabilityService` treats missing snapshots
and snapshots older than one minute as unknown, and `POST /api/v1/selection`
fails closed with 409 `product_unavailable` (FR-011 / NFR-009). Without a local
feed, T-03 cards show `availability_status: unknown` and Select stays disabled.

Edge compose therefore starts an `inventory-seeder` sidecar when
`AEA_SEED_INVENTORY=1` (the compose default). It writes monotonic, versioned
snapshots for the reference catalog product IDs (`classic-rose-dozen`,
`lilac-bouquet`, `budget-mixed-bunch`, `pink-flower-vase`, `premium-orchid`)
with `available_quantity > 0`, then refreshes `observed_at` about every 30
seconds. Production must omit this sidecar; it does not replace inventory
authority.

To confirm Select on a running stack: send a Discovery message such as
"birthday roses", open T-03, and choose an Available card — or rely on
`python edge/scripts/diagnose.py`, which now posts `POST /api/v1/selection`
against a seeded product.

Open sources such as [Our World in Data](https://ourworldindata.org/) are **not**
a florist SKU catalog. They may later inform optional supply-signal research;
they must not be used as a drop-in seed. See
`research/design-notes/local-inventory-seed.md`.

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
`research/design-notes/edge-workspace-projection-contract.md`):

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
- `POST /api/v1/support` answers a customer question (FR-009/FR-005 and thin
  FR-010). It accepts only `{question}` and returns `{answer,
  approved_source_references, matched, kind, fact_references}`. Situational
  questions about this session's order, delivery, or availability are answered
  from authoritative facts (`kind=situation`). Other questions use approved
  product/policy information; an unmatched question returns a safe
  no-approved-information answer (never fabricated).
- `POST /api/v1/support/escalation` records a T-09 / FR-006 Contact Florist
  request. It accepts only `{reason}` from an allowlist and returns an
  acknowledgement plus `escalation_reason`. Extra fields (email, address, card
  data) are rejected. Chat with Lily / Help remain the FR-009 FAQ overlay.
- Local florist operator console (#170): `GET /florist` serves a labeled staff
  sample, separate from the customer workspace. `GET /api/v1/operator/escalations`
  and `GET /api/v1/operator/sessions/{id}` are least-data reads of Contact Florist
  requests and a session summary (conversation, prior ASO answers, order status,
  availability).
  `GET /api/v1/operator/forecasts` returns thin FR-012 inventory trend
  recommendations from validated snapshot history. They return 404 unless
  `AEA_FLORIST_OPERATOR=1` and `AEA_ENVIRONMENT` is not `production`. See
  `research/design-notes/florist-operator-ui.md`. Not FR-016 / FR-017 CRM.
- `POST /api/v1/checkout` performs FR-019 payment and checkout. It accepts only a
  `payment_reference` (an opaque vault token) and the `observed_total`; raw card
  fields (`card_number`, `cvv`, ...) are rejected at the edge (NFR-013). Checkout
  returns `202 accepted` with `pending: true`; authorization runs in the payment
  consumer (#148). Observe `order.confirmed` (or a decline) via workspace/stream.
  A stale `observed_total` or an already-confirmed order returns 409. The Adaptive
  Workspace T-07 UI follows ADR-013: it confirms session delivery, order total,
  and a session payment reference (`session_pay_ref`) rather than blank re-entry;
  a different vault token is optional when the customer chooses to change it.
- `GET /api/v1/stream` is the reconnectable SSE contract. A cold connection
  receives one `snapshot` event carrying the workspace; a reconnection with
  `Last-Event-ID` (or `?after=`) receives only the `invalidation` deltas it
  missed, each naming the projections that must regenerate (derived from the
  `projection_dependency` registry, plus order-status invalidations for
  NFR-011). Event IDs are the monotonic context version. The Adaptive Workspace
  polls the stream about every 20 seconds while the customer is on T-08 tracking
  so status updates appear within the one-minute NFR without a manual refresh.

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
