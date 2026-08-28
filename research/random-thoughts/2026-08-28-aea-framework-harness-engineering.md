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

## II. THE FORMULA: ADAPTIVE EXPERIENCE = SU + SERVICES + HARNESS

*How Path B restates Agent = Model + Harness*

Related work crystallized a coding-agent formula: Agent = Model + Harness [1], [2], [3]. Hashimoto's ratchet is the method: when the agent makes a mistake, engineer a solution so the mistake does not recur [1]. AEA keeps that ratchet and changes the product. The thing being shipped is not a million-line coding agent. It is a florist experience in which Shared Understanding is editable, recommendations are validated, and availability is fail-closed.

> "Anytime you find an agent makes a mistake, you take the time to engineer a solution such that the agent never makes that mistake again."
>
> — Mitchell Hashimoto [1], applied here to experience failures, not code diffs

The AEA restatement is operational. Shared Understanding is the customer-visible state ([[FR-001]], FR-021). Domain services validate what the model is not allowed to invent ([[FR-007]], inventory, delivery, payment). The outer harness is everything that keeps fourteen hats from improvising a fifteenth, keeps IDs frozen, and keeps merges behind @aea-mr-coordinator. Keep 14 hats. Do not copy playbook `$5` / 3 retries / 80% completion as AEA policy.

### A. Related Work, Not Inherited Evidence

The template playbook compiles third-party harness-only gains: a GAIA swing, a Terminal Bench rank change, a million-line Codex codebase [2], [6], [7]. Those numbers are not AEA results. This paper does not reprint them as if Lily's Florist had run those benches. Cite them as related work. AEA evidence in this note is narrower: [[CF-048]] verified (#259 / !280); the dual-viewport trail on !298 / !299 / !300 with [[CF-054]] **regressed** (queue `verified` is a false verified; live [[J1]] re-record after !300 Unknown); fail-closed inventory as specified ([[FR-011]] / [[NFR-009]]); and an honest leftover list from the 2026-08-27 clips.

**TABLE II — INNER RUNTIME VERSUS OUTER HARNESS (AEA)**

| Layer | What it is | What it is not |
|---|---|---|
| Model | LLM Path B calls via LiteLLM; NFR-003 ≤ 2.5s | The product |
| Inner runtime | Edge BFF, domain services, PostgreSQL, broker per ADRs | The 14-hat team |
| Outer harness | 14 roles, vault, CF loop, CI guards, DATE_RE | A prompt file |
| Shared Understanding | Editable customer state ([[FR-001]]/021) | A hidden chain-of-thought |

### B. Inner Harness vs. Outer Harness

Frontier labs ship an inner harness: safety layers, native tool calling, context windows. AEA does not pretend to replace that. The engineering moat for Path B is the outer harness: session-start SOP, 14 canonical skills, coherence scripts, GitLab gates, fail-closed inventory, and the honesty rule. This playbook is about that outer harness [5]. The inner product runtime still matters. Domain services validate. The broker stays product-neutral per the ADRs. Payment FR-019 is mockup, not live Stripe. That is an honesty constraint, not a roadmap slogan.

## III. LAYER 1: GUIDES

*Feedforward controls that prevent known failures before a session starts*

Guides are what an AEA session reads before it acts. They are feedforward. Fowler and Böckeler's guides-and-sensors taxonomy remains the vocabulary [3]. On Path B the guide surface is specific, not generic AGENTS.md folklore.

### A. What Guides Contain

The session-start SOP lives in AGENTS.md. Cursor loads `.cursor/rules` with session-start-briefing, coherence-findings-sop, docker-integration-before-mr, and stakeholder-skills-sync. Fourteen canonical skills sit under `.cursor/skills/aea-*/`. ADRs freeze architecture moves. FR and NFR IDs come from the workbook, not from a helpful agent inventing a new number. The dual-viewport contract is `docs/05-ux-design-guide/path-b-dual-viewport-specification.md`. Path B CSS is owned by @aea-ux-designer. Guides should name files, roles, and stop conditions. Motivational language is not a guide.

**Template 1 — Minimum AEA session-start guide**

```
PROJECT: Lily's Florist / Path B
TRACKER: GitLab (glab). GitHub is a one-way mirror.
HANDOFF: research/daily-briefs/YYYY-MM-DD.md   # DATE_RE only
RULES:
- Do not invent BG / US / FR / NFR IDs
- Do not invent a 15th implementer hat
- One CF -> one issue -> one branch -> one MR
- Only @aea-mr-coordinator merges
ANTI-PATTERNS:
- Status words without a probe ([[CF-048]] / [[CF-054]] false verified)
- Loop ticks that merge or restyle Path B CSS
- Knowledge MR closing a UI finding
- Queue `verified` without a clip dated after the CSS merge
```

Vision principles from `docs/01-product-vision/product-vision.md` belong in the guide layer because they constrain design: Thought before form; Knowledge before navigation; Shared understanding before recommendation; Experiences earn attention; Continuity before immediacy; Latest relevant intent wins; AI interprets, domain services validate. BG-001 through BG-007 exist in that vision. This paper does not invent their wording.

### B. The Ratchet, AEA-shaped

Hashimoto's ratchet still holds [1]. The six steps on Path B: (1) a session or a clip surfaces a failure. (2) Classify the class, not the anecdote. (3) Pick the **strongest** layer — a sensor or CI guard, not another paragraph. (4) Encode it in the vault. (5) Open one CF and one GitLab issue. (6) Do not call it verified until a probe says so. A prompt patch fixes one conversation. A skill rule fixes every future hat that loads it. A CI guard makes the error structurally harder. The same error three times becomes a sensor. A DATE_RE line is not a probe. Docs and spec are trusted guides; they are not live-shop evidence.

### C. Guide Hygiene

Fourteen skills and four always-on rules already accumulate. Lean by **subtraction**, not a fifteenth skill. Version them. Date the reason a rule exists. Delete guide and skill lines that CI sensors already enforce (GitLab #275, queued). Date and prune guide rules (GitLab #274, in progress). Do not grow a fifteenth skill that is secretly "just implement it." A guide file with undated aspirations is not a harness. It is vault drift.

- Can the hat verify the rule without subjective taste?
- Does the rule trace to an observed CF, ADR, FR, or NFR?
- Are two skills telling the same hat opposite merge policies?
- Could a python guard replace this sentence?
- When was the rule last read against current Path B behavior?

### D. Guides as Organizational Memory

AGENTS.md is not a suggestion to the model. It is the system of record for how a session must begin. When the conversation and the guide conflict, the guide wins. That inversion is what makes the outer harness durable [2]. New hats inherit the ID freeze and the MRC merge rule in seconds. When a human leaves, the corrections remain in skills, ADRs, and the CF queue.

### E. The Cost of Not Having Guides

Without the SOP, every new session infers Path B from the live shop alone. It will invent FR IDs. It will treat GitHub as the tracker. It will mark [[CF-054]] `verified` because CSS merged — that already happened on main until !304, and it was a false verified. It will write a DATE_RE file that is not the DATE_RE filename. Every correction made only in chat dies with the session. The guide file is what makes the correction permanent.

## IV. LAYER 2: SENSORS

*Feedback controls; computational first; clips are probes, not trophies*

Sensors verify after execution. They catch what guides did not prevent. Computational sensors first [3]. Inferential judgment is expensive and non-deterministic. Path B already has python guards. Use them before asking a model whether the shop "feels" done.

**TABLE III — AEA SENSOR TYPES AND RELIABILITY**

| Type | Example | Speed | Determinism |
|---|---|---|---|
| Computational | scripts/check_coherence.py | Fast | Deterministic |
| Computational | check_knowledge_graph.py | Fast | Deterministic |
| Computational | run_all_guards.py + GitLab CI | Fast | Deterministic |
| Computational | Fail-closed inventory [[FR-011]] / [[NFR-009]] | Fast | Deterministic |
| Probe (UI) | Path B journey×viewport clips ([[CF-054]]) | Slow | Human-scored |
| Inferential | LLM-as-judge on copy tone | Slow | Non-deterministic |

Fail-closed inventory is a product sensor, not a linter. Missing or stale `observed_at` becomes unknown. Select is disabled. That is [[FR-011]] / [[NFR-009]]. A green Available badge without a fresh observation is a demo. DATE_RE claiming 14/14 skill coverage is a generator claim. This paper does not restate 14/14 as independently probed. Nobody ran the script for this compilation.

### A. Self-Verification Pattern

The strongest pattern gives the session its own sensors. After a change, run the guard. Loop the error text back. This is not the model grading itself. It is the model executing an external check.

```python
def fail_closed_inventory(row):
    if missing(row.observed_at) or stale(row.observed_at):
        return "unknown"   # Select disabled (FR-011 / NFR-009)
    return row.availability

def verified_step(hat, task, sensors):
    result = hat.execute(task)
    for sensor in sensors:
        verdict = sensor.check(result)
        if not verdict.passed:
            result = hat.fix(result, verdict)
            if not sensor.check(result).passed:
                return escalate(task, verdict)
    return result
```

### B. Clip Probes


