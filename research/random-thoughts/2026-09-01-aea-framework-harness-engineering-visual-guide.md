> **Tags**: #aea #second-brain #visual-guide #harness #architecture #knowledge-first
> **Captured**: 2026-09-01
> **Author**: @aea-knowledge-guardian, @aea-product-owner, @aea-ux-designer
> **Audience**: General Public, Product Teams, Non-Researcher Stakeholders
> **Companion Academic Papers**: [[2026-09-01-aea-framework-harness-engineering]], [[2026-08-31-aea-framework-harness-engineering]]

# The Plain-English Guide to Harness Engineering
## How to Build AI Experiences That Actually Ship and Stay Honest

---

## Executive Summary: The AI Dilemma

Most AI demonstrations look astonishing in a scripted 30-second screen recording, yet fail completely when real customers use them. 

The reason is simple: **A fluent conversation is not a finished store.**

When a customer shops at a florist, they don't just want charming conversation. They need to know:
* Is this bouquet actually sitting in the cooler right now?
* Can a delivery driver get it to the hospital before 5:00 PM?
* Will my card be charged the exact right amount without leaking my private payment data?

An AI language model alone cannot answer those questions reliably because language models are probabilistic word predictors—not databases, inventory trackers, or payment gateways.

**Adaptive Experience Architecture (AEA)** solves this by surrounding the AI with a protective operational factory called the **Outer Harness**.

---

## 1. The Core Formula in Everyday Terms

$$\text{Adaptive Experience} = \text{Shared Understanding} + \text{Domain Services} + \text{Outer Harness}$$

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. THE CUSTOMER TALKS                                                  │
│    Shopper: "I need bright birthday flowers for my mom today in Berlin"│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. THE AI INTERPRETER & LIVE NOTEPAD                                   │
│    • AI Concierge: Listens and extracts intent (Occasion, Date, Color) │
│    • Shared Understanding: A digital notepad visible to both parties   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. THE REAL-WORLD SERVICES (The Source of Truth)                       │
│    • Warehouse: Validates real physical inventory (Fail-Closed)        │
│    • Delivery Engine: Calculates realistic driver routing & cutoffs    │
│    • Cash Register: Itemizes pricing, taxes, and zero-PII payment      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. THE OUTER HARNESS (The Factory & Inspectors)                        │
│    • 14 Automated Quality Guards: Verifies facts before showing them   │
│    • Independent Gatekeeper: Ensures no untested changes reach customers│
└────────────────────────────────────────────────────────────────────────┘
```

### The Three Golden Rules:
1. **AI Interprets, Domain Services Decide:** The AI can suggest flowers, but only the database can confirm they are in stock.
2. **Fail-Closed Availability:** If the inventory system is unreachable or outdated, the button automatically disables. It is far better to say "Checking stock..." than to sell flowers you don't have.
3. **No Self-Approval:** The person or agent who writes the code is never the one who approves it for production.

---

## 2. The Three Eras of Building with AI (2023 &rarr; 2026)

The software industry has evolved through three distinct phases:

```
┌────────────────────────────────────────────────────────────────────────┐
│ ERA 1 (2023-2024): PROMPT ENGINEERING                                  │
│ Focus: "Finding the magic words" to coax better responses from the AI. │
│ Flaw:  The AI forgets everything as soon as the chat ends.             │
├────────────────────────────────────────────────────────────────────────┤
│ ERA 2 (2025): CONTEXT & SEARCH (RAG)                                   │
│ Focus: Stuffing large PDF documents and search results into the prompt.│
│ Flaw:  Information overload; the AI knows facts but can't take actions.│
├────────────────────────────────────────────────────────────────────────┤
│ ERA 3 (2026): HARNESS ENGINEERING                                      │
│ Focus: Building the entire software factory and guardrails around AI.  │
│ Result: Deterministic databases, automated tests, and proven outcomes. │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 5 Concentric Floors (Why AI Apps Break)

Think of an AI system like a 5-story building. **Each floor rests on the one below it.** If you skip the lower floors, the top of the building will collapse into thin air.

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🏢 FLOOR 05: THE AGENT TEAM & GOVERNANCE (Graph Engineering)           │
│    Specialized human/agent roles + an Independent Reviewer.            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 🔄 FLOOR 04: THE GOAL RUN & RETRIES (Loop Engineering)           │  │
│  │    Clear objectives, execution budgets, and single-task focus.   │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ ⚙️ FLOOR 03: THE MACHINE & TESTS (Harness Engineering)     │  │  │
│  │  │    Connecting AI to real tools + automated quality guards. │  │  │
│  │  │  ┌──────────────────────────────────────────────────────┐  │  │  │
│  │  │  │ 🧠 FLOOR 02: THE MEMORY CURATOR (Context Engineering)│  │  │  │
│  │  │  │    Filters noise, keeps lessons, manages active window.│  │  │
│  │  │  │  ┌────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │ 💬 FLOOR 01: THE MESSAGE (Prompt Engineering)  │  │  │  │  │
│  │  │  │  │    Clear role, single objective, strict rules. │  │  │  │  │
│  │  │  │  └────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Built On Real Infrastructure
┌────────────────────────────────────────────────────────────────────────┐
│ 🏛️ SOLID FOUNDATION: REAL DATABASES & INVENTORY (PostgreSQL & Kafka)   │
└────────────────────────────────────────────────────────────────────────┘
```

* **The Lower-Floor Invariant:** If your 5th-floor multi-agent team keeps failing, don't blame the agents—check your 2nd-floor memory filter. Bad input on Floor 2 ruins everything above it.
* **The Economic Law:** Swapping the underlying AI model (like switching from Claude to GPT or Gemini) takes **1 afternoon**. Rebuilding your 5-floor operational harness takes **3 months**. The harness is your real intellectual property.

---

## 4. How the "Second Brain" Solves AI Amnesia

Without engineered memory, an AI starts every new conversation with complete amnesia. Dumping hundreds of pages of past chat history into the prompt makes the AI slow, expensive, and confused.

Instead, AEA organizes institutional memory into **4 distinct vaults**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 📖 1. PROCEDURE MEMORY (Skills)                                        │
│    Step-by-step playbooks for repeatable tasks (e.g. how to run tests).│
├────────────────────────────────────────────────────────────────────────┤
│ 🚫 2. CORRECTION MEMORY (Constraints)                                  │
│    Hard rules learned from past mistakes (e.g. "Never invent fake IDs").│
├────────────────────────────────────────────────────────────────────────┤
│ 🕸️ 3. RELATIONSHIP MEMORY (Knowledge Graph)                            │
│    Links showing how features, requirements, and systems connect.      │
├────────────────────────────────────────────────────────────────────────┤
│ 📅 4. DAILY BRIEF (Cross-Session Handoff)                              │
│    A clean 1-page summary of exactly where the team left off today.    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Clear Team Roles: The 14 Hats Mapped to 6 Functions

To prevent agents and developers from stepping on each other, AEA organizes 14 specialized roles into 6 clear functions:

```
1. 🔭 SCOUT & ANALYST (Discovery)
   • UX Designer (@aea-ux)
   • Customer Journey Specialist (@aea-cj)
   • Support Coordinator (@aea-support)

2. 🎯 STRATEGIST (Prioritization)
   • Product Owner (@aea-po)
   • Project Manager (@aea-pm)

3. 🛡️ GUARDIAN (Safety & Quality)
   • AppSec Security Auditor (@aea-appsec)
   • Cost & FinOps Guardian (@aea-cost)
   • Performance & Speed Guardian (@aea-perf)
   • Coherence Guardian (@aea-coherence)

4. ⚡ EXECUTOR (Builders)
   • Senior Software Engineer (@aea-sse)
   • AI & Machine Learning Engineer (@aea-ai)
   • DevSecOps & Cloud Platform Engineer (@aea-dso)

5. ⚖️ INDEPENDENT VERIFIER (The Gatekeeper)
   • Merge Request Coordinator (@aea-mrc)
   * Core Rule: The builder can NEVER approve or merge their own code!

6. 📚 OBSERVER & KNOWLEDGE
   • Knowledge Guardian (@aea-kg)
   * Records every breakthrough and lesson into the Second Brain.
```

---

## 6. The Six Layers of the Outer Harness

```
┌───────────────┬────────────────────────────────────────────────────────┐
│ Layer         │ What It Does in Plain English                          │
├───────────────┼────────────────────────────────────────────────────────┤
│ 1. Guides     │ The Rulebook: Clear instructions and boundaries before │
│               │ starting work.                                         │
│ 2. Sensors    │ The Smoke Alarms: Automated tests that detect errors   │
│               │ before customers see them.                             │
│ 3. Loop       │ The Workflow: One problem &rarr; one branch &rarr; one review.     │
│ 4. Memory     │ The Vault: Preserving lessons so mistakes never repeat.│
│ 5. Permissions│ The Keycard: Strictly controlling who can touch data,  │
│               │ budgets, and production systems.                       │
│ 6. Observation│ The Dashboard: Real-time telemetry proving everything  │
│               │ works with hard evidence, not guesses.                 │
└───────────────┴────────────────────────────────────────────────────────┘
```

---

## 7. Summary: What Makes AEA Different?

1. **Honesty Over Hype:** We never claim a feature is "verified" just because someone wrote code. It must be proven on real devices with real test clips.
2. **Deterministic Backing:** The AI concierge creates the experience, but real PostgreSQL databases and Kafka streams guarantee the transaction.
3. **Continuous Antifragility:** Every time a bug occurs, we don't just fix the code—we install a permanent automated guardrail so that entire class of mistake is mathematically impossible to repeat.
