# CF-016 — Kafka Accepted stub vs broker TBD

tags: #aea #coherence-finding
status: queued
finding_id: CF-016
severity: medium

## Claim

Quarantined Kafka draft previously claimed Accepted while Proposed ADR-007 and
technical architecture leave the message bus product-neutral.

## Intended fix

After ADR-007 lands: either Accept Kafka under a free ADR number consistent with
topology, or keep the bus abstract and leave Kafka as research-only.
