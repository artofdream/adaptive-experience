# ADR-012 — MVP External Message Broker

Status: Accepted

Date: 2026-08-11

Related requirements: NFR-015, NFR-016, NFR-017, FR-022

Related decisions: [ADR-007 Initial Deployment Topology](ADR-007-initial-deployment-topology.md),
[ADR-008 Contract-First Messaging](ADR-008-contract-first-messaging.md),
[ADR-010 Command and Event Boundaries](ADR-010-command-event-boundaries.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md),
[MVP Topic Contracts](../04-technical-architecture/topic-contracts.md)

Related issue: [#120 — Select MVP external message broker](https://gitlab.com/artof-group/adaptive-experience-architecture/-/issues/120)

## Context

ADR-007 requires governed MVP topics to cross a real external broker boundary
even while the backend begins as a modular monolith. ADR-008 establishes
contract-first JSON Schema messages, transactional outbox publication,
at-least-once delivery, idempotent consumers, and explicit publisher and
subscriber authorization. ADR-010 keeps browser interactions synchronous at
the application edge while authoritative domain progression uses the broker.

The product choice was deliberately deferred. The MVP now needs a concrete
broker and operating baseline for durable publication, retry, redelivery,
access control, observability, local development, and recovery.

The broker transports and retains governed messages for a bounded operational
period. It does not own workflow, experience state, business facts, schema
meaning, or the authoritative audit record.

## Decision Drivers

- Satisfy the accepted at-least-once model without silently losing messages.
- Confirm that an outbox message reached the required broker replicas before
  marking it published.
- Support independent consumer progress and controlled replay.
- Preserve ordering for messages sharing an authoritative aggregate key.
- Route the 21 product-neutral MVP topic names to authorized consumer groups.
- Enforce separate publisher and subscriber credentials with least privilege.
- Expose producer, partition, replication, consumer-lag, retry, and dead-letter
  signals.
- Run in a single local or CI container while supporting a replicated
  production topology.
- Establish conventions that prevent Kafka retention from becoming accidental
  domain authority.

## Considered Options

### Option A — Apache Kafka

Use Kafka topics, keyed partitions, and consumer groups. Retain messages for a
bounded operational window so consumers can recover and authorized operators
can replay them. Use producer acknowledgements and idempotence, replicated
topics, manual offset management, retry topics, and dead-letter topics.

Kafka provides durable retention, ordering within a partition, independent
consumer progress, replay, and a path to higher-volume event processing. Its
retry, dead-letter, partitioning, retention, and offset conventions must be
defined explicitly.

### Option B — RabbitMQ

Use a durable topic exchange, per-consumer queues, publisher confirms, manual
acknowledgements, quorum queues, retry queues, and dead-letter exchanges.

RabbitMQ maps directly to work-queue delivery and has first-class queue routing
and dead-letter mechanisms. Each consumer requires a separately operated queue
and stored delivery copy, while retained history and independent replay are not
its primary model.

### Option C — NATS with JetStream

Use JetStream streams, subjects, and durable consumers with explicit
acknowledgement and redelivery.

JetStream is lightweight and supports persisted at-least-once delivery. Its
advisory-driven dead-letter pattern and stream, retention, consumer, and
subject-permission conventions require additional design for this repository's
acceptance criteria.

### Option D — Cloud-provider queue and notification services

Select a provider-specific combination of topics, queues, retries, and
dead-letter queues.

Managed operations can reduce infrastructure work, but choosing a deployment
provider now would couple routing, security, local emulation, and recovery to a
provider. A managed Kafka service may implement Option A when it preserves this
decision's semantics and configuration controls.

## Decision

Use **Apache Kafka as the MVP external message broker**.

Kafka is an infrastructure adapter behind the product-neutral message
contracts. Canonical topic names, envelopes, schemas, owners, and authorized
subscribers remain defined by the repository rather than Kafka client types or
deployment resources.

The MVP retains **at-least-once end-to-end semantics**. Kafka producer
idempotence reduces duplicates within a producer session, but it does not make
a PostgreSQL state transaction, outbox relay, Kafka publication, and consumer
database transaction globally exactly once. Stable message identity and
consumer idempotency remain mandatory.

### Topic and partition model

- Each governed MVP topic maps to a Kafka topic with the same canonical name.
- Environment isolation uses separate clusters or an approved topic-name and
  authorization boundary; environment prefixes are deployment metadata and do
  not change the canonical topic recorded in the envelope.
- Every topic has an explicit owner, authorized producers, authorized consumer
  groups, partition count, replication factor, retention policy, maximum
  message size, and compatibility expectation in version-controlled
  configuration.
- Message keys preserve order for an authoritative aggregate: experience flows
  use session ID; order flows use draft-order or order ID; other domains use
  their documented aggregate identifier.
- Events sharing a key are ordered only within a partition. There is no global
  ordering across topics, keys, or partitions.
- Partition counts are not increased casually because repartitioning changes
  key-to-partition assignment. A change requires an ordering and consumer
  impact review.

### Production durability baseline

- Production topics use a replication factor of at least three when the
  hosting environment permits and require at least two in-sync replicas for
  acknowledged writes.
- Producers use `acks=all` and idempotence. Unsafe acknowledgement or retry
  configurations are prohibited for authoritative publications.
- Unclean leader election is disabled for governed topics.
- Topic creation and alteration are controlled by reviewed automation;
  applications do not rely on automatic topic creation.
- Kafka runs in KRaft mode. Production controller and broker placement avoids a
  single failure domain; the exact managed or self-hosted topology is a
  deployment decision constrained by these durability rules.

### Publication

- The transactional-outbox relay is the only normal producer of authoritative
  messages to Kafka.
- Messages carry the complete ADR-008 envelope and use a stable message ID
  across relay retries.
- The relay marks an outbox row published only after Kafka acknowledges the
  required replicas.
- Connection failure, acknowledgement timeout, unavailable partitions, or an
  insufficient in-sync replica set leaves the outbox row unpublished for
  bounded-backoff retry.
- A lost acknowledgement can cause a later process to republish the same outbox
  message. Kafka producer idempotence is not used as a substitute for stable
  message IDs or consumer idempotency.
- Broker-specific headers may carry transport metadata but must not replace or
  alter the governed envelope and payload.

### Consumption and offset handling

- Each logical subscriber uses a stable, explicitly authorized consumer group.
  Instances of that subscriber share partitions within the group.
- Consumers disable automatic offset commitment for authoritative processing.
- A consumer commits its offset only after its local transaction, idempotency
  record, and resulting outbox rows commit successfully.
- Processing checks the stable message ID before applying effects. Duplicate
  deliveries return the recorded outcome and may then advance the offset.
- Consumers reject stale context versions under FR-022 regardless of Kafka
  arrival order.
- Consumer rebalances, crashes, and offset-commit ambiguity are expected
  redelivery conditions and must not corrupt authoritative state.
- Offset reset or replay is an authorized, audited operator action. It is never
  performed automatically to hide consumer failure.

### Retry and dead-letter handling

- Kafka has no broker-native delayed delivery queue. Recoverable failures use
  version-controlled retry topics associated with the consumer boundary and
  explicit delay tiers.
- A retry processor republishes a due message to the original governed topic or
  next retry tier while preserving message ID, canonical topic, schema version,
  correlation ID, aggregate key, original publication time, attempt count, and
  failure classification.
- Delivery attempts and total retry age are bounded. Exhausted or
  non-recoverable messages move to a consumer-specific dead-letter topic.
- Retry and dead-letter publication is durable and must complete before the
  failed source offset is committed.
- Dead-letter payloads contain the original governed message plus sanitized
  diagnostic metadata; they must not expose unnecessary personal or payment
  data.
- Dead-letter replay is an authorized operator action with a recorded reason
  and outcome. Payloads are not edited in place to force success.
- Retry topics and dead-letter topics have explicit retention, ACLs, ownership,
  monitoring, and capacity limits.

### Retention and replay

- Governed topics use a bounded time- and size-based retention window sufficient
  for recovery and approved replay. Exact values are configuration backed by an
  operational recovery objective, not hard-coded in domain code.
- Delete retention is the default. Log compaction is enabled only for a topic
  whose key, tombstone, and state-reconstruction semantics are documented in a
  separate review.
- Kafka retention is not the authoritative data-retention policy for sessions,
  orders, payments, or audits. PostgreSQL and domain stores retain authoritative
  state according to their lifecycle policies.
- Replay consumers must use normal schema validation, authorization,
  idempotency, stale-context, audit, and outbox rules.

### Security and governance

- Production clients authenticate using an approved SASL mechanism or mutual
  TLS, and all broker traffic uses TLS.
- Producers and consumer groups receive separate principals and least-privilege
  ACLs for only their registered topics and group IDs.
- The browser and Adaptive UI receive no Kafka credentials or network access.
- Cluster administration, topic administration, application production, and
  application consumption are separate privileges.
- Broker ACLs complement contract-policy tests: authorization to write a topic
  does not permit an invalid schema or excessive payload under NFR-015 and
  NFR-017.
- Secrets are supplied by the deployment environment and are never committed to
  the repository.

### Operations and recovery

- Topic definitions, broker policies, principals, ACLs, quotas, and consumer
  group conventions are version-controlled and applied idempotently.
- Local development and CI run Kafka in an official single-node KRaft container
  with persisted storage when restart behavior is tested. This provides
  semantic parity but not production high availability.
- Metrics and alerts cover producer errors and latency, unavailable or
  under-replicated partitions, in-sync replica shrinkage, offline partitions,
  controller health, disk use, request throttling, consumer lag, rebalance
  frequency, retry age, and dead-letter growth.
- During broker unavailability, authoritative transactions continue only when
  their local outbox commit succeeds. The relay drains the backlog after Kafka
  recovery; no code path substitutes an in-memory-only event bus.
- Recovery procedures preserve topic configuration, committed records, group
  offsets, ACLs, and retry/dead-letter topics according to the hosting model.

## Rationale

Kafka is selected for its durable retained log, keyed partition ordering,
independent consumer groups, replay, and ability to support future event-driven
growth without changing the 21 governed message contracts. These benefits are
accepted despite higher operational and application-convention cost.

The choice deliberately does not introduce event sourcing or make Kafka the
system of record. PostgreSQL remains authoritative for experience state and
each domain module remains authoritative for its business facts. The outbox and
idempotent-consumer rules remain the consistency boundary.

RabbitMQ would provide simpler queue-native retry and dead-letter behavior, but
Kafka's retention and independent replay are preferred for the intended
evolution of the platform. The added retry-topic, partition, retention, and
offset disciplines are mandatory consequences rather than optional future
work.

## Consequences

### Positive

- Consumers recover independently from retained topic history.
- New authorized consumer groups can process retained events without adding
  another copy at publication time.
- Aggregate-key ordering and partitioned scale are available from the start.
- Consumer lag is an explicit measure of asynchronous system health.
- The platform has a direct path to higher-throughput processing and controlled
  replay without changing domain schemas.

### Negative

- Kafka adds partition, replication, retention, ACL, quota, offset, rebalance,
  controller, upgrade, and capacity-management responsibilities.
- Delayed retry and dead-letter handling require application-managed topics and
  processors.
- Partition-key and partition-count mistakes can be expensive to correct.
- Local single-node operation does not reproduce production quorum failure
  behavior.
- Retained messages increase privacy, deletion, disk-capacity, and operational
  governance obligations.

### Risks

- A consumer may commit an offset before its local transaction, losing work.
- A retry processor may reorder messages for the same aggregate or create an
  unbounded retry loop.
- Teams may mistake retention or replay for domain authority and build state
  directly from undocumented topic history.
- Overly broad ACLs may expose topics or consumer progress to unauthorized
  modules.
- Consumer lag or disk growth may go unnoticed without actionable alerts.
- Exactly-once marketing may lead implementers to remove required outbox or
  idempotency controls.

## Implementation Constraints

- Published MVP topics traverse Kafka; an in-memory-only substitute is not
  permitted for integration or production behavior.
- Topic and consumer-group names map deterministically to the canonical topic
  registry and logical subscriber identity.
- Authoritative producers use the transactional outbox, stable message IDs,
  `acks=all`, and producer idempotence.
- Authoritative consumers use manual offset commitment, local idempotency, and
  stale-context rejection.
- Offsets advance only after successful local commit or durable transfer to the
  appropriate retry or dead-letter topic.
- Retry never changes the governed payload or domain meaning.
- Partition keys are documented per topic and use authoritative aggregate
  identifiers rather than infrastructure-generated values.
- Broker-specific metadata must not leak into domain schemas.
- Retention, replay, diagnostics, and dead-letter records obey least-data and
  sensitive-data controls.
- Broker and client upgrades require compatibility tests for producers,
  consumers, rebalances, retry processors, ACLs, and recovery.

## Verification

- Contract tests provision all 21 governed topics and prove that only documented
  producers and consumer groups can access each representative topic.
- Publication tests prove an outbox row is marked published only after an
  `acks=all` acknowledgement and that relay restart preserves stable identity.
- Durability tests stop a broker or remove an in-sync replica and verify
  acknowledged-write behavior against the configured replication and
  `min.insync.replicas` policy.
- Consumer tests cover failure before local commit, failure after local commit
  but before offset commit, rebalance during processing, duplicate delivery,
  stale context version, and idempotent outcome recovery.
- Ordering tests publish concurrent messages for the same aggregate key and
  prove partition-local order, then prove stale protection when retry causes a
  later arrival.
- Retry tests demonstrate explicit delay tiers, bounded attempts and age, and
  durable transfer before source-offset commitment.
- Dead-letter tests prove exhausted messages reach the correct authorized topic
  with sanitized diagnostics and can be replayed through an audited procedure.
- Retention tests verify expiry and capacity policies without treating Kafka as
  the domain or audit store.
- Local and CI tests start an official Kafka KRaft container, apply reviewed
  topic and ACL configuration, publish representative schemas, restart with
  persisted storage, and verify consumer recovery.
- Observability tests assert producer failures, replication degradation,
  consumer lag, retry age, rebalances, and dead-letter growth emit the required
  metrics and correlated logs.

## Revisit Conditions

Revisit the decision when measured operating cost exceeds the benefit of
retention and replay; when required ordering cannot be expressed safely through
partition keys; when a managed provider cannot preserve the selected
durability and authorization semantics; or when workload evidence favors a
simpler queue broker or a different streaming platform.

Any replacement must preserve the product-neutral envelopes, schemas,
publisher/subscriber registry, outbox atomicity, at-least-once assumption,
idempotency, stale-context rejection, and auditable outcomes.
