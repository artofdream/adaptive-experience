# Technical architecture

Style: asynchronous, event-driven, experience-oriented.

**Authority boundary:** AI Floral Concierge interprets; domain services validate
customer-visible facts (catalog, inventory, recommendations, pricing, delivery,
orders, payments, status).

MVP topics and ownership live in topic contracts (NFR-015 schema versions,
publishers, subscribers). Automated FAQ answers publish on
`support.faq.answered` (AI Concierge). Human escalation remains Future.

## Canonical docs

- [technical-architecture.md](https://gitlab.com/artof-group/adaptive-experience-architecture/-/blob/main/docs/04-technical-architecture/technical-architecture.md)
- [topic-contracts.md](https://gitlab.com/artof-group/adaptive-experience-architecture/-/blob/main/docs/04-technical-architecture/topic-contracts.md)
- [schemas/](https://gitlab.com/artof-group/adaptive-experience-architecture/-/tree/main/docs/04-technical-architecture/schemas)
