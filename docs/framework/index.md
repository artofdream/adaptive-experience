# Adaptive Experience Architecture

**Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.**

> **In Plain English:** When shopping with AI, a chatbot shouldn't guess prices or invent inventory. Adaptive Experience Architecture pairs conversational AI with real-world databases (inventory, pricing, logistics) and an outer harness of automated quality checks to keep transactions reliable and honest.

This site is the public surface for that architecture. It is not a shop, not a content management system, and not a pitch deck.

- **Shared Understanding** is the session's current, reviewable model of customer intent (a live digital notepad).
- **Domain Services** are authoritative: they validate inventory, price, delivery slots, and payment (the warehouse and cash register).
- **The Outer Harness** keeps both honest in production — through guides, sensors, the loop, memory, permissions, and observability.

AI may interpret. Domain services decide. Status words are claims; they need a probe.

![Adaptive Experience formula: Shared Understanding + Domain Services + Outer Harness](assets/formula.svg)

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

## Case Study & Explore the Framework

The live florist at [aea.artof.link](https://aea.artof.link) is one case study, not the framework home. Dual-viewport is the intended presentation, not yet fully verified.

- Read the [comparison & visual guide](comparison.html) for the visual 5-floor building model, 3 eras table, and honest status ledger.
- Explore the [schema](schema.html) for the complete architectural map, layers, loop, and named journeys.
- See the [stack](stack.html) for the high-level design used so far (two hostnames, this site, the florist runtime).
- Review the [Path B case study](path-b.html) for customer journey video recordings and implementation details.
- Read the [journal](journal.html) for curated stories of challenge, solve, ship, and lesson learned.
- See the [glossary](glossary.html) for terms used across this site (Path B, CF-NNN, ID freeze, and more).
