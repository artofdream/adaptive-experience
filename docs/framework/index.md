# Adaptive Experience Architecture

**Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.**

> **In Plain English:** When shopping with AI, a chatbot shouldn't guess prices or invent inventory. Adaptive Experience Architecture pairs conversational AI with real-world databases (inventory, pricing, logistics) and an outer harness of automated quality checks to keep transactions reliable, private, and honest.

This site is the public documentation surface for the architecture. It is not a shop, not a content management system, and not a pitch deck.

- **Shared Understanding** is the session's current, reviewable model of customer intent (like a live digital notepad shared between customer and store).
- **Domain Services** are authoritative: they validate inventory, prices, delivery slots, and payments (the real-world warehouse and cash register).
- **The Outer Harness** keeps both honest in production — through guides, sensors, an execution loop, persistent memory, strict permissions, and telemetry.

AI may interpret. Domain services decide. Status words are claims; they need a probe.

![Adaptive Experience formula: Shared Understanding + Domain Services + Outer Harness](assets/formula.svg)

---

## The Six Outer Harness Layers

The outer harness wraps around domain services and shared understanding across six layers:

| Layer | Plain-English Job | What It Prevents |
|---|---|---|
| **1. Guides** | Clear instructions, role boundaries, and playbooks | Prevents out-of-scope actions before work begins |
| **2. Sensors** | Automated test checks and fail-closed availability | Catches errors before customers see them |
| **3. Loop** | Interpret → Act → Verify → Remember | Stops sprawling tasks: 1 finding → 1 issue → 1 review |
| **4. Memory** | Persistent session context across page reloads | Solves AI amnesia without stuffing raw chat history |
| **5. Permissions** | Strict controls over who can touch data, funds, or code | Prevents unauthorized merges and self-approval |
| **6. Observability** | Real-time telemetry and proof for every status claim | Eliminates guesswork; unprobed claims stay Unknown |

![The six layers of the outer harness](assets/six-layers.svg)

---

## Explore the Framework & Case Studies

The live flower shop at [aea.artof.link](https://aea.artof.link) is our reference case study, proving these principles on real infrastructure:

- Read the [Comparison & Visual Guide](comparison.html) for the 5-floor building model, 3 eras of AI development, and the honest status ledger.
- Explore the [Schema](schema.html) for the architectural blueprint, execution loop, and team roles.
- See the [Stack](stack.html) for high-level system architecture, cloud deployment, and the "two hostnames, two jobs" separation.
- Review the [Path B Case Study](path-b.html) for customer journey video recordings and dual-viewport presentation.
- See the [Mobile Companion App](companion.html) for the lightweight Android client, Google Play release, and live florist order feeds.
- Learn about [Privacy-Preserving CRM](crm.html) for zero-PII customer intelligence, edge wallets, and 14-day address shredding.
- Read the [Journal](journal.html) for curated stories of real-world challenges, solutions, and hard-learned lessons.
- Check the [Glossary](glossary.html) for plain-English definitions of terms used across this site.
