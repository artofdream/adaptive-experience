# Performance and Availability Hardening

Status: Accepted (M7 verification)

Scope: the M7 performance and availability hardening pass (#152) - reconfirm the
standard-query budget, characterize read-projection and relay throughput, and
reconfirm availability under failure. Related: NFR-004 (performance), NFR-003
(availability, #45). Production load profiles and redundancy are exercised in
reference deployment validation (#150).

## Standard-query response budget (NFR-004)

The assistant standard-query path must respond within 3 seconds.
`edge/scripts/check_assistant_slo.py` measures the p95/max over ten
representative queries through the deployed reference stack (TLS gateway, BFF,
Orchestration, PostgreSQL, AI fallback) in the container integration path and
fails if the max exceeds the 3s budget. Measured p95 is consistently well under
the budget (tens of milliseconds).

## Read-projection latency

Customer-facing reads are synchronous projections. The workspace aggregate is the
heaviest read: it composes the conversation, shared-understanding, recommendations
(ranking plus a live availability read), order-summary (pricing), order, delivery,
and selection facets. Under 50 repeated aggregations it stays well within budget
(p95 < 1s locally, far below the 3s NFR-004 limit), verified by
`test_workspace_projection_latency_under_repeated_load`.

## Relay throughput and backpressure

The outbox relay claims up to `limit` pending messages per pass with
`FOR UPDATE SKIP LOCKED` and publishes each with an acks=all acknowledgement
before marking it published. `limit` is the backpressure control. A 50-message
batch is claimed and acknowledged in a single pass with nothing left pending,
verified by `test_relay_publishes_a_batch_in_one_pass`.

## Durability under failure

- **Relay retry:** a publication that is not acknowledged is released for retry
  with a stable message id and a bounded backoff; it is never lost or duplicated
  (`test_relay_keeps_identity_and_retries_unacknowledged_publication`). A poisoned
  message is never published (fail-closed at the guard).
- **Consumer retry/DLQ:** `KafkaFailureRouter` durably transfers a failed delivery
  to a per-consumer retry tier, or to the consumer DLQ for non-recoverable errors,
  before the source offset advances - so no message is dropped or double-applied
  (`test_nonrecoverable_failure_routes_to_consumer_dlq`,
  `test_offset_does_not_commit_when_retry_transfer_fails`).

## Availability under failure (NFR-003)

The assistant stays available by degrading to the deterministic local interpreter,
with a bounded-failure circuit breaker and recovery (see
`nfr-003-availability.md`). Measured 100% availability under total provider
failure. The edge runner reports the 24/7 assistant fallback path healthy.

## Verification evidence

| Property | Evidence |
|----------|----------|
| Standard-query p95 < 3s on the deployed stack | check_assistant_slo.py (edge integration) |
| Workspace read-projection p95 under load | test_workspace_projection_latency_under_repeated_load |
| Relay batch throughput, nothing pending | test_relay_publishes_a_batch_in_one_pass |
| Relay retry keeps identity, no loss | test_relay_keeps_identity_and_retries_unacknowledged_publication |
| Consumer DLQ / offset safety | test_nonrecoverable_failure_routes_to_consumer_dlq |
| Availability under provider failure | test_generative_ai.py, nfr-003-availability.md |

## Scope

These are reference measurements that establish the performance and availability
characteristics. Production load testing, capacity, and redundancy are part of
reference deployment validation (#150).
