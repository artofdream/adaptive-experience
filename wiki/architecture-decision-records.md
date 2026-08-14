# Architecture Decision Records

Accepted ADRs (see `docs/06-adr/`):

| ADR | Title |
|---|---|
| ADR-001 | Shared Understanding |
| ADR-002 | Experiences instead of pages |
| ADR-003 | Progressive thought completion |
| ADR-004 | Customer support overlay (ASO MVP; T-09 Future) |
| ADR-005 | Latest relevant intent wins |
| ADR-006 | MVP customization boundary |
| ADR-007 | Initial deployment topology (modular monolith + BFF) |
| ADR-008 | Contract-first messaging and transactional outbox |
| ADR-009 | Experience-state ownership and persistence |
| ADR-010 | Synchronous command and asynchronous event boundaries |
| ADR-011 | PostgreSQL experience-state datastore |
| ADR-012 | Apache Kafka external message broker |
| ADR-013 | Confirmation-driven experience |
| ADR-014 | PostgreSQL pgvector for semantic retrieval |
| ADR-015 | RAG and hybrid retrieval |
| ADR-016 | Agentic AI boundary |

ADR-011 through ADR-016 are Accepted when their promotion MRs have merged.
PostgreSQL is the experience-state datastore; Kafka is the MVP broker;
`pgvector` is the semantic retrieval store; hybrid RAG requires post-retrieval
validation; the agent prepares plans while domain services mutate state.
ADR-013 extends Thought Before Form into transaction execution.

## Canonical docs

- [docs/06-adr/](https://gitlab.com/artof-group/adaptive-experience-architecture/-/tree/main/docs/06-adr)
