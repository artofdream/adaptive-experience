# Architecture Blueprint (Schema)

This page is the public architectural map of Adaptive Experience Architecture. It defines how the core components connect, how customer interactions are validated, and how responsibilities are divided.

> **In Plain English:** When an AI assistant helps a shopper, it shouldn't be an unconstrained chatbot making up answers. This blueprint shows the scaffolding that wraps around the AI: checking real store databases, executing a strict 4-step loop (Interpret → Act → Verify → Remember), and using specialized quality checks to prevent mistakes.

[Formula](#the-core-formula) · [Six layers](#the-six-layers) · [The loop](#the-execution-loop) · [Team roles](#team-roles-and-responsibilities) · [Journeys](#tested-customer-journeys) · [Stack](stack.html)

---

## The Core Formula

**Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.**

- **Shared Understanding:** The session's live digital notepad. It captures what the customer wants (the recipient, occasion, budget, and card message) in a structured format both the shopper and the store can inspect.
- **Domain Services:** The authoritative backend systems. They validate stock in the cooler, calculate delivery fees, charge cards, and create real orders.
- **The Outer Harness:** The automated safety net. It wraps around both the conversational AI and the databases to ensure transactions are reliable and honest.

**The Golden Rule:** AI may interpret customer intent, but domain services always make the decisions. Status claims require empirical proof.

![Adaptive Experience formula](assets/formula.svg)

---

## The Six Layers

The outer harness wraps around domain services and shared understanding across six functional layers:

1. **Guides (Playbooks & Rules):** Explicit instructions and guardrails loaded before work starts, defining what actions are permitted and who owns which surface.
2. **Sensors (Smoke Alarms):** Automated tests and checks that observe state and detect errors before customers encounter them.
3. **Loop (Execution Cycle):** The repeatable pattern for every transaction: interpret intent, take an action, verify the result, and remember the agreed state.
4. **Memory (Persistent Context):** Structured storage that keeps customer selections, carts, and occasions intact across page reloads without amnesia.
5. **Permissions (Access Control):** Strict security controls ensuring only authorized services can modify inventory, process funds, or touch code.
6. **Observability (Hard Evidence):** Real-time telemetry and telemetry dashboards. If a claim has not been tested, it remains labeled **Unknown**.

![The six layers of the outer harness](assets/six-layers.svg)

---

## The Execution Loop

Every interaction between a customer and the system follows a disciplined 4-step cycle:

| Step | Plain-English Action | What It Guarantees |
|---|---|---|
| **1. Interpret** | Extract customer intent into Shared Understanding | AI structures the conversation without guessing or making decisions |
| **2. Act** | Call deterministic Domain Services | Real inventory, verified pricing, available delivery slots, and payment |
| **3. Verify** | Run automated checks and journey probes | No action is marked complete without proof on real screens and servers |
| **4. Remember** | Persist agreed state to session memory | The customer's cart, occasion, and preferences survive page reloads |

![The four-step execution loop: Interpret, Act, Verify, Remember](assets/the-loop.svg)

---

## Team Roles and Responsibilities

To keep engineering rigorous, AEA divides responsibilities across 14 specialized lenses (hats) grouped into 5 functions:

- **Discovery (3 lenses):** UX Designer, Customer Journey Specialist, Support Coordinator.
- **Strategy & Delivery (2 lenses):** Product Owner, Project Manager.
- **Safety & Quality (4 lenses):** AppSec Auditor, Cost Guardian, Performance Guardian, Coherence Guardian.
- **Builders (3 lenses):** Senior Software Engineer, AI Engineer, DevSecOps Platform.
- **Governance & Memory (2 lenses):** Merge Request Coordinator (MRC), Knowledge Guardian.

Work flows through 3 executable jobs: **implement**, **verify**, and **merge**. To prevent conflicts of interest, the engineer or AI that writes code is never the one who merges it. **Only the independent Merge Request Coordinator merges.**

---

## Honesty, Knowledge, and Antifragility

- **Claims Require Proof:** In software, words like `verified`, `shipped`, and `complete` are easy to say. AEA treats them as claims that must be backed by automated test output or physical device probes. A closed ticket or a merged code change is not proof that a feature works on real screens.
- **Knowledge First:** The project's memory lives in version-controlled repository history and Second Brain notes—not in ephemeral chat windows that disappear when closed.
- **Systemic Antifragility:** If an error happens twice, it signals a missing automated test or architectural gate—not a need for more discipline or pep talks.

---

## Tested Customer Journeys

We test the live reference shop at [aea.artof.link](https://aea.artof.link) against 4 named customer scenarios:

- **J1 Urgent Sam:** Same-day rose delivery with rapid checkout.
- **J2 Planner Sarah:** Advance birthday scheduling with custom card messages, satin ribbon, and vase selection.
- **J3 Loyal Alex:** Returning shopper whose cart and preferences persist across browser reloads.
- **J4 Tracker Chris:** Order lookup, delivery tracking, and direct escalation to the florist team.

---

## Related Documentation

- [System Stack](stack.html) — How the cloud servers, message bus, and mobile clients connect.
- [Path B Case Study](path-b.html) — Watch the 30-second recordings of all 4 customer journeys.
- [Comparison & Visual Guide](comparison.html) — The 5-floor building model and industry comparison.
- [Architecture Glossary](glossary.html) — Plain-English definitions of terms and concepts.
- [Framework Home](index.html) — Return to the overview.

