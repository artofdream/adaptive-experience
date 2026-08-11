# PostgreSQL and Kafka Foundation

This directory is the executable M1 foundation defined by ADR-008, ADR-011,
and ADR-012. It is deliberately product-neutral: M2 application behavior uses
these boundaries but is not implemented here.

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
- Relay claims use `FOR UPDATE SKIP LOCKED`; a row becomes published only after
  the Kafka producer returns an `acks=all` delivery acknowledgement.
- Message IDs remain stable across relay retries.
- Consumers disable auto commit. A source offset advances only after the local
  idempotency transaction succeeds or a durable retry/DLQ transfer succeeds.
- The reviewed registry is the source for canonical topics, partition keys,
  publishers, consumer groups, retry tiers, DLQs, and policy tests.

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
