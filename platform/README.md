# PostgreSQL and Kafka Foundation

This directory contains the executable, product-neutral platform foundation
defined by ADR-008, ADR-011, and ADR-012. It implements the M1 PostgreSQL
outbox/Kafka/governance baseline and the M2 Conversation, Intent, Shared
Understanding, context-version, state-preservation, correction, stale-result,
and provider-neutral AI orchestration services. Florist presentation and domain
copy remain outside this boundary.

## Local startup

Prerequisites: Docker Compose and Python 3.12.

```sh
docker compose -f platform/docker-compose.yml up -d --wait
python platform/scripts/apply_migrations.py
python platform/scripts/provision_kafka.py
python platform/scripts/diagnose.py
```

Install the optional runtime adapters before running the Python commands:

```sh
python -m pip install -r platform/requirements.txt
```

No production secret is stored here. Local credentials are intentionally
non-production values and are isolated to the Compose network.

`render_kafka_acls.py` renders the reviewed least-privilege ACL plan for the
deployment automation. Local Compose uses an isolated plaintext listener so it
can test delivery semantics without pretending to reproduce production TLS and
SASL. Production must apply the rendered policy with authenticated principals;
plaintext production listeners are prohibited by ADR-012.

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
- `OpenAICompatibleIntentInterpreter` supplies a vendor-neutral Generative AI
  boundary using strict JSON output and a timeout capped at 2.5 seconds.
  `AvailableIntentInterpreter` fails over to the deterministic local interpreter
  and opens a bounded circuit after repeated provider failures, so conversation
  and thought completion remain available outside provider or business hours.
  Configure `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` together;
  `/internal/v1/ai/health` reports primary/fallback mode without exposing secrets
  (FR-004). A concrete vendor remains a deployment choice, not an architecture
  dependency.
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
