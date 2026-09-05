# Architecture Glossary

Plain-English definitions for terms and concepts used across this documentation site. Each entry explains what the concept means, why it matters, and where it is applied in practice.

---

## Core Architecture Concepts

### Shared Understanding
The session's live digital notepad. It captures the customer's intent (occasion, recipient relationship, budget, card message) in a structured format that both the shopper and store services can read and update in real time.
- **Why it matters:** It gives the AI persistent context without having to stuff raw chat transcripts into every prompt.
- **Where to see it:** Explored on the [Framework Home](index.html) and [Schema](schema.html).

### Domain Services
The authoritative backend software systems that manage real-world business operations: inventory, pricing, delivery scheduling, payment, and order management.
- **Why it matters:** AI language models are probabilistic word predictors; they cannot reliably track warehouse stock. Domain services always decide transactions.
- **Where to see it:** Diagrammed on the [System Stack](stack.html).

### Outer Harness
The software factory and automated safety scaffolding built around conversational AI to ensure honesty, reliability, and security in production. It consists of six layers: Guides, Sensors, Loop, Memory, Permissions, and Observability.
- **Why it matters:** Without an outer harness, AI prototypes hallucinate prices, leak data, or break when edge cases arise.
- **Where to see it:** Detailed on the [Comparison & Visual Guide](comparison.html).

### Fail-Closed Availability
A safety design rule: if a backend service (such as cooler inventory or delivery driver scheduling) is unreachable or times out, the purchase action turns off immediately.
- **Why it matters:** It is far better to display "Checking inventory..." than to accept a customer's money for flowers that cannot be delivered.
- **Where to see it:** Referenced in the [Comparison](comparison.html#1-the-core-formula-in-everyday-terms).

### Thin Client
A lightweight client application (such as our Android app) that handles screen display and user gestures, while delegating all business logic, inventory validation, and pricing calculations to the central backend.
- **Why it matters:** Prevents "split-brain" bugs where prices on a mobile app differ from prices on the website.
- **Where to see it:** Demonstrated on the [Mobile Companion](companion.html).

### BFF (Backend-for-Frontend)
A secure gateway server that translates client requests from web browsers or mobile apps into internal domain commands.
- **Why it matters:** It prevents public browsers from ever connecting directly to databases or internal message queues.
- **Where to see it:** Illustrated on the [System Stack](stack.html).

### Least-Data & Ephemeral Shredding
A privacy-first design principle (ADR-020) where sensitive customer information (such as physical delivery addresses) is isolated in an encrypted table and automatically purged after a 14-day fulfillment window.
- **Why it matters:** Eliminates the risk of massive customer data breaches by refusing to build permanent PII honeypots.
- **Where to see it:** Detailed on [Privacy CRM](crm.html).

### Edge Wallet
An encrypted notebook on the customer’s phone. After a confirmed order, the companion stores a receipt locally (Android Keystore). Names and card wording stay on the device. The store only ever sees an opaque product/order token if a reorder is sent later.
- **Why it matters:** Repeat shopping does not require a central address book of customers.
- **Honesty:** The **save** is live and has been probed. The Need-screen reorder **button** is on `main` (!459 / #404). Write and tap remain two facts.
- **Where to see it:** [Mobile Companion](companion.html) and [Privacy CRM](crm.html).

### Florist Staff Console
The `/florist` page on the live shop. Florists see orders and Contact Florist requests in a browser. It is not a second native app.
- **Why it matters:** Fulfillment stays on the same store hostname as the customer shop, with least-data reads.
- **Where to see it:** [Path B Case Study](path-b.html).

---

## Project & Governance Terms

### Path B
The code name for our live reference flower shop implementation, running at [https://aea.artof.link](https://aea.artof.link). It demonstrates the Adaptive Workspace and customer journeys in action.
- **Where to see it:** [Path B Case Study](path-b.html).

### Probe
A verification action performed on real hardware or live servers to prove that a feature works as claimed, rather than assuming it works because a ticket was closed.
- **Why it matters:** "Verified" is a claim until backed by a probe. If an unverified feature has not been tested, its status remains **Unknown**.
- **Where to see it:** Illustrated in the [Journal](journal.html#claim-vs-probe) as **Claim vs probe** (the same incident the [comparison](comparison.html#what-aea-claims-here) page calls **Daily-brief honesty**).

### CF-NNN (Coherence Finding Codes)
An internal tracking identifier for an architectural discrepancy or falsifiable claim. Each finding follows a strict 1-finding → 1-issue → 1-branch discipline until verified or resolved.
- **Where to see it:** Referenced in the [Comparison](comparison.html).

### ID Freeze
A governance rule: once a requirement (FR/NFR) or business goal ID is assigned in canonical project records, it is never renumbered or reused, preserving traceability across years of commits.

### Fourteen Hats (Roles)
The 14 specialized quality perspectives AEA uses to inspect code and architecture (e.g. UX Designer, AppSec Auditor, Cost Guardian, Performance Guardian). They represent areas of review, not a 14-person bureaucracy.
- **Where to see it:** Listed on the [Schema](schema.html#team-roles-and-responsibilities).

---

## Related Documentation

- [Framework Home](index.html) — Core formula and overview.
- [Architecture Blueprint](schema.html) — The 6 layers and execution loop.
- [Comparison & Visual Guide](comparison.html) — 5-floor building model.
- [System Stack](stack.html) — Cloud infrastructure and request flow.
- [Project Journal](journal.html) — The story behind the architecture.

