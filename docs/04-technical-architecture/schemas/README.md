# Topic JSON Schemas

Machine-readable payload schemas for MVP topics (NFR-015, ADR-008).

Naming: `{topic}.v{semver}.json` (for example,
`support.faq.answered.v1.0.0.json`). Schema versions must match the
**Schema version** column in [`../topic-contracts.md`](../topic-contracts.md).

All **21 MVP** topics have stub schemas in this directory. Owners refine field
inventories before a publisher ships. Envelope fields remain in the bus
envelope defined by `technical-architecture.md`, not in these payload files.

Verify locally or in CI:

```bash
python scripts/check_topic_schemas.py
```

Regenerate stubs (overwrites) only when intentionally refreshing the set:

```bash
python scripts/write_mvp_topic_schemas.py
```
