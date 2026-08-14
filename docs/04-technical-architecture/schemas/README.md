# Topic JSON Schemas

Machine-readable payload schemas for MVP topics (NFR-015, ADR-008).

Naming: `{topic}.v{semver}.json` (for example,
`support.faq.answered.v1.0.0.json`). Schema versions must match the
**Schema version** column in [`../topic-contracts.md`](../topic-contracts.md).

All **22 governed** topics have payload schemas in this directory (the original
21 MVP topics plus `support.escalation.requested` for FR-006 / T-09). Owners refine
field inventories before a publisher ships. The shared bus envelope defined by
ADR-008 is machine-readable in `message-envelope.v1.0.0.json`; envelope fields
remain separate from the topic-specific payload files.

Verify locally or in CI:

```bash
python scripts/check_topic_schemas.py
python scripts/test_topic_schema_guard.py
```

The semantic guard reconciles `topic-contracts.md`, the generator's reviewed
payload manifest, the exact active schema inventory, the shared envelope, and
same-major compatibility rules. It rejects unknown topics, identity drift,
minimum-payload drift, and breaking compatible-version changes.

Regenerate stubs (overwrites) only when intentionally refreshing the set:

```bash
python scripts/write_mvp_topic_schemas.py
```
