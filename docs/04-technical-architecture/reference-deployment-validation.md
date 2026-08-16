# Reference Deployment Validation

Status: Accepted (M7 verification)

Scope: the M7 reference deployment validation (#150) - the deployment artifacts,
automation, and topology controls for the modular-monolith reference deployment
(ADR-007), and what remains a real-deployment-target activity. Related: #149
(event backbone), #152 (performance/availability).

## Topology (ADR-007)

The reference deployment is a modular monolith: PostgreSQL, Kafka, the
Orchestration app, the BFF, and the Nginx TLS gateway, provisioned per area by
Docker Compose.

## Broker security (ADR-012)

- Production requires **TLS + SASL** listeners with authenticated principals.
  **Plaintext production listeners are prohibited.** The local Compose uses an
  isolated plaintext listener to test delivery semantics only; it does not
  reproduce production TLS/SASL.
- The **least-privilege ACL plan** is rendered by `render_kafka_acls.py`: each
  publisher may Write only its own topics; each subscriber may Read only the
  topics it consumes, bound to its own group, and Write only its own retry/DLQ
  topics. No other grant is produced. Verified by
  `platform/tests/test_deployment.py` (complete coverage + least-privilege +
  group-bound reads). Production applies the rendered plan against authenticated
  principals.

## Deployment automation (reproducible)

- `apply_migrations.py` is idempotent: it skips already-applied versions, so a
  re-run is a no-op (verified in the integration path by applying twice).
- `provision_kafka.py` is idempotent: it creates missing topics and aligns
  `min.insync.replicas` to RF-1 (floor 1) so RF is never equal to MinISR when
  RF >= 2. Path B pilot uses `AEA_KAFKA_REPLICATION_PROFILE=pilot` (RF=2).
- `render_kafka_acls.py` emits the ACL plan for the deployment automation.
- Local credentials are non-production values isolated to the Compose network;
  production secrets come from the deployment environment, not the repository.

## Container orchestration controls

- Health checks are defined for PostgreSQL, Orchestration, the BFF, and the
  gateway.
- The **BFF has no published host port** (Compose `expose` only); the **Nginx
  gateway (8443) is the sole public entry point** and strips internal identity
  headers before proxying.
- A boundary test asserts the BFF source imports neither `psycopg` nor
  `confluent_kafka` and never mutates a context version directly.

## Deployed end-to-end smoke

`edge/scripts/run_integration_tests.py` builds the containers, waits for every
health check, and verifies the guided browser interface, the authenticated
Edge-to-Orchestration Shared Understanding path, the 24/7 assistant fallback path,
and the standard-query SLO through the real TLS gateway, BFF, Orchestration, and
PostgreSQL. The async backbone (relay -> Kafka -> governed consume) is validated
end to end by the backbone integration tests (#149).

## Requires a real deployment target

The following are deployment-environment activities, not exercisable in local
Compose; the artifacts they consume are validated here:

- Production TLS certificates and SASL principals on the broker, and applying the
  rendered ACL plan to a real cluster.
- A managed secret store supplying production credentials.
- Multi-node redundancy and capacity/load testing (see #152 scope).

## Verification evidence

| Item | Evidence |
|------|----------|
| Least-privilege ACL plan, complete + group-bound | test_deployment.py; render_kafka_acls.py |
| Migrations idempotent | apply_migrations.py (twice); test migrations at latest |
| BFF no host port; gateway-only; header stripping | edge/docker-compose.yml; edge runner; boundary test |
| Deployed stack healthy + journey path + SLO | edge/scripts/run_integration_tests.py |
| Backbone runs end to end | test_kafka_integration BackboneIntegrationTests (#149) |
