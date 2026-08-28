> **Tags**: #aea #second-brain #harness #path-b #knowledge-first
> **Captured**: 2026-08-28
> **Draft status**: in progress (not canonical `docs/`)
> **Backlog**: #273 clip-verify (!304 merged; clip after CSS Unknown) · #274 vault placement (this MR) · #275 prune (queued)
> **CF-054**: CSS !300 merged; live J1 after CSS Unknown; main queue is `regressed` after !304 (was false `verified`)

# Production Experience Engineering Practice 2026

# Adaptive Experience Architecture

## Adaptive Experience = Shared Understanding + Domain Services + Outer Harness: The 6-Layer Production Playbook

*Instantiated on Lily's Florist Path B (Art of Group). Mapped onto the six-layer harness taxonomy of Hashimoto, Fowler, and Codex field reports. Canonical remote: GitLab https://gitlab.com/artof-group/adaptive-experience-architecture. Live shop: https://aea.artof.link. Tracker is GitLab (glab), not GitHub.*

*Independently compiled, August 2026 — Art of Group / AEA knowledge guardian — not affiliated with Google, OpenAI, Anthropic, or HashiCorp — and not endorsed. Template inspired by harness_final.pdf (Hashimoto / Fowler / Codex field reports). Revised 28 August 2026 evening Berlin after a GitLab main probe of [[CF-054]].*

*Vault: #aea. Existing IDs only: [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]] [[J1]] [[J2]] [[J3]] [[J4]] [[CF-048]] [[CF-054]]. This note lives in `research/random-thoughts/` as a working paper, not in `docs/`, until `@aea-product-owner` promotes it. Do not paste it into DATE_RE.*

```
+------------------+     +------------------+     +------------------+
|     GUIDES       |     |   AGENTIC LOOP   |     |     SENSORS      |
| AGENTS.md SOP    |     |                  |     | coherence.py     |
| .cursor/rules    +---->+ 1 CF > 1 issue +---->+ graph-guard      |
| 14 skills, ADRs  |     | 1 branch > 1 MR  |     | CI + fail-closed |
| Path B dual spec |     | MRC merge only   |     | Path B clip probe|
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+--------+---------+     +--------+---------+     +--------+---------+
|     MEMORY       |     |   PERMISSIONS    |     |  OBSERVABILITY   |
| DATE_RE briefs   |     | 14 hats (no 15th)|     | Grafana          |
| random-thoughts  |     | ID freeze        |     | CF queue status  |
| vault wikilinks  |     | MRC merge gate   |     | honesty / DATE   |
+------------------+     +------------------+     +------------------+
```

**Fig. 1.** The six-layer Adaptive Experience Architecture mapped onto the outer harness. Guides and sensors form the steering loop (feedforward + feedback). Memory, permissions, and observability form the runtime foundation. The agentic loop sits at the center: one finding, one GitLab issue, one branch, one MR.

**Abstract —** Production AI-native experiences fail the same way production agents fail: a fluent demo is not a bounded, honest, merge-gated system. This note presents Adaptive Experience Architecture (AEA) as an outer harness around a florist product, Lily's Florist Path B, where customers speak naturally and the interface evolves as shared understanding grows. The formula is Adaptive Experience = Shared Understanding + Domain Services + Outer Harness. The model is whatever LLM Path B calls through LiteLLM under the NFR-003 timeout SLA (≤ 2.5s). The outer harness is the 14-role stakeholder team, the vault, the coherence loop, and CI guards. The inner product runtime is the edge BFF, platform domain services, PostgreSQL, and a product-neutral broker per the ADRs. We map AEA onto the six harness layers and report only findings that have been probed. Status words need a probe: a queue row that says `verified` without a clip dated after the CSS merge is a false verified. We report [[CF-054]] as **regressed**, not clip-verified. !304 **merged** 28 Aug 22:14 Berlin (Related #273). Queue on main is now `regressed`. Live [[J1]] clip after !300 remains Unknown. Merge is not clip-verify. We do not restate third-party benchmark swings as AEA results. Related work on Agent = Model + Harness is cited, not inherited as evidence.

**Index Terms —** Adaptive Experience Architecture, outer harness, shared understanding, Path B dual viewport, coherence findings, DATE_RE, 14 hats, fail-closed inventory, GitLab MR coordinator, honesty rule, Lily's Florist, guides and sensors.

## I. THE PROBLEM: DEMOS THAT NEVER SHIP

*Why a fluent florist demo is not yet a production experience*

A chatbot produces responses. An AI-native florist must produce outcomes: a validated recommendation, an honest availability badge, an itemized summary, and a session that survives a viewport change. The difference is not which model Path B called this week. The difference is the infrastructure that turns a probabilistic interpreter into a bounded, observable shop. Path B lets customers speak naturally. The interface is supposed to evolve as understanding grows. That promise dies the moment the system performs confidence it did not earn.

AEA already has a name for that failure class. CF-048 is the daily-brief honesty finding. Status words appeared without a probe. The DATE_RE generator can claim coverage it did not measure. A session can narrate a ship that the vault does not show. That is the AEA version of demos that never ship: not a missing model, a missing harness. [[CF-048]] was verified through GitLab issue #259 and MR !280. The lesson is the product. Fluent language around an unprobed status is a regression, not a milestone.

[[CF-054]] is the live exhibit of the same class. On GitLab main (probed 28 August 2026, 22:16 Berlin) the queue row is `regressed` with #273 / #272 · !298 !299 !300 (CSS merged; clip after CSS Unknown). Until !304 merged at 22:14 Berlin that row said `verified` — a **false verified**. Dual-viewport CSS !300 merged as `63aaa4ce`. Spec !299 closed #272. Finding note on main after !304: `regressed` / #273. Live [[J1]] phone+desktop re-record after !300 is Unknown. Closing a GitLab issue from a spec or CSS MR is not verification. Treat this as a [[CF-054]] **regression**, not a new finding. Path B `verified` requires a clip dated after the CSS/product merge. Hourly ticks must reconcile Issue/MR from `glab`, not from the queue text. !304 (`docs/273-cf054-clip-verify-after-css`) **merged** 28 Aug 22:14 Berlin and set the queue on main to `regressed`. Live [[J1]] clip after !300 remains Unknown. Merge is not clip-verify.

### A. The Three Eras, for Experience Systems

The industry spent 2023-2024 optimizing prompts. It spent 2025 stuffing context: RAG, MCP, memory. By 2026, coding-agent practitioners named a third discipline: harness engineering [1], [2], [3]. Experience systems need the same progression, with different artifacts. A prompt does not keep FR-011 honest. A larger context window does not stop a knowledge MR from closing a UI finding. The outer harness does.

**TABLE I — THREE ERAS OF EXPERIENCE ENGINEERING**

| Era | Focus | Optimizes | Limitation |
|---|---|---|---|
| Prompt Eng. (2023-24) | Single turn | Phrasing, tone | One utterance |
| Context Eng. (2025) | What the model sees | RAG, MCP, SU | Information, not action |
| Harness Eng. (2026) | Full environment | Guides, sensors, merge | Entire runtime + shop |

Each era subsumes the previous one. AEA Path B still needs prompts (the concierge voice) and context (Shared Understanding, FR-001/021). The harness is what decides whether those turns become a shop a customer can trust. Prompt engineering shapes what the model says. Context engineering shapes what the model sees. Harness engineering shapes what the experience is allowed to claim, what domain services must validate, and what constitutes a finished journey [3].

### B. Who This Playbook Is For

This note is for the 14 AEA hats, and for small product teams who are building an AI-native experience rather than a coding agent. No new agent framework is required. The architecture is useful wherever an LLM interprets intent and domain services must remain the source of truth. 3DX Lab is a separate project and is out of scope here. GitHub github.com/artofdream/adaptive-experience is a one-way mirror, not the tracker. Work happens on GitLab.

**Revision policy.** Comparison or field feedback that would change a claim, a sensor, or a limitation revises this note. Do not leave the playbook stale while a sibling comparison is more honest. A status word is a claim: probe committed GitLab `main` or write Unknown. Shared memory is committed GitLab `main` only.

