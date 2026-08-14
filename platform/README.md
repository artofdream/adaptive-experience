# PostgreSQL and Kafka Foundation

This directory contains the executable, product-neutral platform foundation
defined by ADR-008, ADR-011, and ADR-012. It implements the M1 PostgreSQL
outbox/Kafka/governance baseline, the M2 Conversation, Intent, Shared
Understanding, context-version, state-preservation, correction, stale-result,
and provider-neutral AI orchestration services, and the M3 authoritative,
freshness-aware inventory availability boundary. Florist presentation and domain
copy remain outside this boundary.

## Local startup

Prerequisites: Docker Compose and Python 3.12.

```sh
docker compose -f platform/docker-compose.yml up -d --wait
python platform/scripts/apply_migrations.py
python platform/scripts/provision_kafka.py
python platform/scripts/diagnose.py
```

Local Postgres is `pgvector/pgvector:pg16` so migration 013 can `CREATE EXTENSION vector`
(ADR-014). Recreate the Compose volume if it was created from `postgres:16-alpine`.
Experience-state migrations still do not depend on the extension.

Install the optional runtime adapters before running the Python commands:

```sh
python -m pip install -r platform/requirements.txt
```

No production secret is stored here. Local credentials are intentionally
non-production values and are isolated to the Compose network.

Local Compose PostgreSQL volumes are **not** encrypted at rest. Production
deployments must enable storage encryption for preference and delivery data
satisfying NFR-007 / NFR-012; see
`docs/04-technical-architecture/nfr-007-012-encryption.md`. Application code
stores sensitive customer material as opaque references where possible and does
not implement field-level ciphers.

`render_kafka_acls.py` renders the reviewed least-privilege ACL plan for the
deployment automation. Local Compose uses an isolated plaintext listener so it
can test delivery semantics without pretending to reproduce production TLS and
SASL. Production must apply the rendered policy with authenticated principals;
plaintext production listeners are prohibited by ADR-012.

## Event backbone workers

The async event backbone runs end to end (#149). Two reference workers wire the
tested relay/consumer components to Kafka:

- `python platform/scripts/run_relay.py [--loop]` publishes outbox messages to
  Kafka through a `SourceGuardedPublisher`: each message is validated against the
  privacy guard using its declared `source` as the publishing principal, so
  publication is fail-closed (a payload that leaks a raw sensitive field is never
  acknowledged - it is released for retry, not published).
- `python platform/scripts/run_consumer.py <group> [--loop]` subscribes to the
  topics a group consumes (per the Kafka policy) and processes each record through
  the governed path: delivery guard, idempotency, version-checked apply, retry/DLQ
  routing, and manual offset commit. The `workspace` group applies
  `WorkspaceOrderInvalidationHandler` for `order.status.updated` /
  `order.confirmed` so the browser stream can refresh T-08 (NFR-011).

The container integration path exercises emit -> relay -> Kafka -> governed
consume end to end. Reactive push of order status to the browser and the async
payment evolution (#148) build on these workers.

## Guarantees

- `orchestration.experience_session`, invalidation records, and outbox rows are
  written by one PostgreSQL transaction with optimistic context-version checks.
- Application mutations use `PsycopgExperienceStateStore.apply_patch`: deep
  object patches preserve completed decisions and unaffected tile state, while
  the canonical `projection_dependency` registry derives only the projections
  that must regenerate. Unknown dependency facets fail closed.
- `ConversationService` accepts validated T-01 customer messages, preserves the
  bounded visible transcript in authoritative experience state, and writes the
  governed `customer.message.submitted` outbox event in the same optimistic
  transaction. The acknowledgement does not wait for or invent an AI result
  (FR-001 / ADR-010).
- `IntentAnalysisService` applies provider-neutral `IntentInterpreter` output
  only to the six Shared Understanding facets, refreshes up to three optional
  thought-completion prompts, and publishes `experience.intent.updated` in the
  same versioned transaction. `ReferenceIntentInterpreter` supplies a
  deterministic local implementation without coupling orchestration to an AI
  vendor; product eligibility and ranking remain authoritative downstream
  concerns (FR-002 / ADR-003).
- `SharedUnderstandingService` exposes a least-data review projection and accepts
  partial customer corrections to those same six facets. Corrections preserve
  untouched intent and completed decisions, refresh thought-completion prompts,
  derive only affected projection invalidations, reject stale context versions,
  and publish the resulting `experience.intent.updated` event in the same
  transaction (FR-021).
- The authenticated Internal Orchestration HTTP surface exposes session create,
  conversation submit/projection, Shared Understanding review/correction, AI
  health, and the reactive workspace substrate (#144): `GET .../workspace` returns
  the aggregate least-data facet document at the current context version, and
  `GET .../stream` returns a `snapshot` event on cold connect or the per-version
  `invalidation` deltas after `?after=`, sourced from `experience_invalidation`
  (the `projection_dependency`-derived trail written by `apply_experience_patch`).
  The generic browser `commands` envelope stays deferred (see `edge/README.md`).
- Validated Recommendations wiring (#142, FR-007/FR-011): the `workspace`
  `recommendations` facet is a derived read projection - `RecommendationService`
  ranks the catalog against current intent and annotates each candidate with a
  real-time Available badge from a non-authoritative
  `InventoryAvailabilityService.availability` read (no event published, safe on a
  GET). `POST .../selection` runs an authoritative `purpose="selection"` inventory
  revalidation (published and audited; rejects unavailable or stale), writes the
  `decisions.product` facet, and emits `product.selected` in one versioned
  `apply_experience_patch` transaction (exactly once at the new context version).
  Selection `options` are the explicit T-04 fields - eligible `size`, physical
  `card_message`, and thin FR-003 keys `flower_type`, `colour`, and `ribbon`
  (ADR-006 amended /
  `docs/04-technical-architecture/t04-card-message-contract.md`); unknown keys
  and gift-card value fields are rejected.
- Delivery scheduling (#33, FR-014): `POST .../delivery` validates a `timing`
  (date + window) and an opaque `destination_reference`, writes the
  `decisions.delivery` facet, and emits `delivery.details.updated` in one
  versioned transaction. Recipient details are reference-only - raw recipient
  name/address/contact are rejected - so no PII enters experience state or the
  event, consistent with `PayloadPrivacyGuard`.
- Order creation (#32, FR-013): `POST .../order` assembles the completed
  `decisions.product` and `decisions.delivery` into the `orchestration.customer_order`
  aggregate (migration 008), one order per session (idempotent). It is a separate
  authoritative aggregate, pre-checkout; the workspace `order` facet surfaces
  `order_id` + `status`. Checkout, payment, and confirmation remain M5.
- Order summary (#37, FR-018): the workspace `order_summary` facet is a derived
  read projection - `PricingService.summarize` recomputes an itemized breakdown
  with the FR-018 categories (product, customization, delivery when a destination
  exists, tax, discount, and total) from the current `decisions.product` /
  `decisions.delivery`, mirroring the recommendations projection. Thin FR-003 /
  card message customization is shown as a 0.00 customization line (ADR-006 /
  T-04); reference tax and discount are 0.00 until a pricing authority supplies
  rates. It publishes nothing and stores no state; the `order.summary.updated`
  event and authoritative pricing belong to the checkout flow (M5, #38).
- Automated support answers (#28/#24, FR-009/FR-005): `POST .../support` answers a
  customer question only from approved information. `SupportService` matches the
  question against a reference approved-knowledge base (FAQ + product/policy
  entries, each with `approved_source_references`), returns
  `{answer, approved_source_references, matched}`, and publishes the governed
  `support.faq.answered` event. An unmatched question returns a safe
  no-approved-information answer with empty sources - it never fabricates content;
  human escalation is Future (FR-006).
- Thin RAG scaffolding (#166, ADR-014/ADR-015): `RetrievalService` indexes the
  same approved FAQ/policy corpus into `retrieval.knowledge_chunk` (`pgvector` +
  FTS) and returns hybrid candidates. Similarity hits are never business truth.
  `SupportService` may take an optional retriever as a candidate source after the
  deterministic keyword matcher misses, and only accepts hits that have a
  keyword/FTS rank and map to approved knowledge. Live `POST .../support` does
  not wire a retriever — replacing MVP FAQ with RAG remains out of scope.
- Checkout and payment (#38 / #148, FR-019): `POST .../checkout` price-checks the
  assembled order, stores a private checkout intent, and emits
  `order.checkout.requested` only — returning `202 accepted` / `pending`. The
  payment consumer (`PaymentCheckoutHandler`) authorizes via `PaymentAuthority`,
  emits `payment.authorization.succeeded|failed`, and on success confirms the
  order (`order.confirmed`). Raw card data never reaches the platform. A declined
  payment leaves the order `submitted` with an observational decline code.
- Order status and tracking (#34/#42, FR-015/FR-023): `POST .../order/status`
  advances the order forward-only through `created -> submitted -> confirmed ->
  preparing -> dispatched -> delivered -> completed` (migrations 009/010),
  publishing `order.status.updated` (`order_id`, `authoritative_status`).
  `POST .../order/delay` sets/clears an orthogonal `delayed` flag (FR-023): while
  set, the published and displayed authoritative state is `delayed`; a forward
  move resolves it. These are order/fulfillment authority actions, not customer
  actions; customers read the latest authoritative state through the workspace
  `order` facet (`status`, `delayed`, `authoritative_status`). FR-023 displays the
  latest state, not a history. Status / confirm / delay writes also bump the
  experience `context_version` and record an `order` invalidation so
  `GET .../stream` can push T-08 refreshes (NFR-011). The workspace Kafka
  consumer mirrors the same invalidation when it receives `order.status.updated`
  or `order.confirmed` from the bus (#149). The Adaptive Workspace polls the
  stream every 20s while the customer is on the tracking step.
- `OpenAICompatibleIntentInterpreter` supplies a vendor-neutral Generative AI
  boundary using strict JSON output and a timeout capped at 2.5 seconds.
  `AvailableIntentInterpreter` fails over to the deterministic local interpreter
  and opens a bounded circuit after repeated provider failures, so conversation
  and thought completion remain available outside provider or business hours.
  Configure `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` together;
  `/internal/v1/ai/health` reports primary/fallback mode without exposing secrets
  (FR-004). A concrete vendor remains a deployment choice, not an architecture
  dependency.
- `InventoryAvailabilityService` records monotonic, versioned product snapshots
  in the inventory-owned PostgreSQL schema. Validation reads treat missing or
  older-than-one-minute data as unknown, publish the closed
  `inventory.availability.validated` contract through the transactional outbox,
  and fail selection-time checks closed unless the product is currently
  available (FR-011 / NFR-009).
- `RecommendationService` ranks a deterministic reference catalog against Shared
  Understanding facets (occasion, budget, style, flower preference), asks
  Inventory for freshness-aware availability, and publishes
  `product.recommendations.ready` with eligible product IDs and ranking through
  the transactional outbox (FR-007 / NFR-006). Catalog ownership remains outside
  this boundary; the reference catalog is a local ranking fixture.
- Relay claims use `FOR UPDATE SKIP LOCKED`; a row becomes published only after
  the Kafka producer returns an `acks=all` delivery acknowledgement.
- Message IDs remain stable across relay retries.
- Consumers disable auto commit. A source offset advances only after the local
  idempotency transaction succeeds or a durable retry/DLQ transfer succeeds.
- Async results are applied only when their context version exactly equals the
  authoritative session version. The consumer locks that session row for the
  duration of application, so a concurrent intent change cannot race the check;
  mismatched results are recorded as `stale`, never passed to the handler, and
  then acknowledged (FR-022 / ADR-005).
- The reviewed registry is the source for canonical topics, partition keys,
  publishers, consumer groups, retry tiers, DLQs, and policy tests.
- Every registry entry names an accountable owner and active semantic schema
  version. CI reconciles those fields and the publisher/subscriber permissions
  with the reviewed topic catalog and verifies that the schema file exists.
- `PayloadPrivacyGuard` reconciles every broker publication and subscriber
  delivery with that registry and the closed payload schema. Unknown envelope
  or payload fields, raw customer/payment fields, unauthorized subscribers,
  and unregistered schema versions fail closed before application handling.
- Production relays wrap their broker adapter with
  `PrivacyEnforcingPublisher`; raw names, addresses, contact details, or card
  data are prohibited. Governed contracts use opaque references and
  provider-issued payment tokens instead.
- PostgreSQL keeps a payload-free `message_audit` ledger for publication and
  consumption stages. It records message/topic/source identity, correlation
  and context versions, publication time, sanitized outcomes, and the governed
  security context. Operators query a workflow by correlation ID without
  exposing business payloads; diagnostics report aggregate audit/failure
  counts only.

## Recovery

1. Run `platform/scripts/diagnose.py` and inspect pending/expired outbox claims,
   consumer lag, and topic existence. Diagnostics never print payloads.
2. Restore PostgreSQL before restarting relays. Pending outbox rows are part of
   the authoritative restore set.
3. Start Kafka, apply `provision_kafka.py` idempotently, then start the relay.
4. Do not reset offsets automatically. An authorized operator records the
   reason before replay or DLQ recovery.
5. A relay crash after broker acknowledgement can duplicate a message. Keep the
   original message ID and rely on consumer idempotency.

Run fast tests with `python -m unittest discover -s platform/tests -v`.
Container-backed tests run through `platform/scripts/run_integration_tests.py`.
