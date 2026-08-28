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

Path B journey×viewport clips are UI probes ([[CF-054]]), not marketing. They sit below computational sensors because they are slow and human-scored. They still matter: a dual-viewport shop that only works in one recording is not dual. [[J1]] (Urgent Sam), [[J2]] (Planner Sarah), [[J3]] (Loyal Alex), and [[J4]] (Tracker Chris) are the journey set. One session, desktop Adaptive Workspace, phone linear concierge. Honest leftovers from the 2026-08-27 clips: [[J3]] recall without a reorder badge; [[J4]] ASO fail-closed, not T-08; Track gated until checkout. Live shop re-record of [[J1]] phone+desktop after !300 (`63aaa4ce`) is Unknown. [[CF-054]] is **regressed**, not clip-verified. The queue row on main said `verified` with #272 / !298, !299, !300 until !304 merged (28 Aug 22:14 Berlin). That was a false verified. Main is now `regressed`. Live [[J1]] re-record after !300 is still Unknown. The finding note on main after !304 is `regressed` / #273. Closing #272 from spec !299 is not a probe. Path B `verified` requires a clip dated after the CSS/product merge.

### C. Sensor Economics

`check_coherence.py` costs nothing per run compared with a token-heavy judge. graph-guard catches ID drift before a hat invents US-008. CI is the sensor that survives a closed laptop. Add inferential sensors only for checks no deterministic rule can capture, such as concierge tone. Treat those as advisory, not gates.

### D. The Sensor Coverage Test

- Can a session check inventory honesty without a human staring at Grafana?
- Does every critical Path B claim have at least one computational sensor?
- Are sensor results logged so CF status is not a vibe?
- Could a silent DATE_RE lie reach the next session without tripping a wire?
- If any answer is no, add the sensor before claiming unattended operation.

## V. LAYER 3: THE AGENTIC LOOP

*One finding, one issue, one branch, one MR; loop ticks must not merge*

The AEA agentic loop is not Plan-Execute-Retry inside one context window. It is a typed GitLab loop. The CF-NNN queue lives in `research/coherence-findings-loop.md`. The unit of work is one finding. One layer per finding: a knowledge MR must not restyle Path B CSS. Hourly ticks must not restyle Adaptive Workspace or Path B CSS/JS unless `@aea-ux-designer` was invoked. Hourly ticks must reconcile Issue/MR from `glab`, not from the queue text. Fan-out is how honest queues die. Do not copy template `$5`, 3 retries, or 80% completion as loop bounds.

```python
def cf_loop(finding, vault):
    issue = gitlab.open_issue(finding)     # one CF -> one issue
    branch = spawn_branch(issue)           # one issue -> one branch
    mr = open_mr(branch)                   # one branch -> one MR
    if loop_tick(mr):
        return reject("loop ticks must not merge")
    if not gates_pass(mr):
        return escalate(issue, packet)     # PO / PM / sponsor
    return mrc.merge(mr)                   # only @aea-mr-coordinator
```

**TABLE IV — REQUIRED LOOP BOUNDS (AEA)**

| Bound | Purpose | Default |
|---|---|---|
| One CF per issue | Prevent queue fan-out | Hard rule |
| Loop ticks merge? | Protect main | Never |
| Who merges | Independent verifier | @aea-mr-coordinator only |
| Auto-merge | When gates pass | MRC policy, not the producing hat |
| Escalation | Human decision packet | PO / PM / sponsor |
| Stopping condition | Honest partial state | Always defined |

### A. Escalation Is Not Failure

Escalation to MRC or PO is a **successful stop**, not a failure. A hat that escalates with a packet is more valuable than one that merges a fluent wrong shop. The packet should contain: the decision required, the recommended option, alternatives already tested, cost of waiting, and the safest default if nobody replies. Secrets and budget escalate to the sponsor. Archive and workbook edits need human confirmation. Path B CSS changes escalate to @aea-ux-designer, not to whoever has the editor open.

### B. The Background Agent Rule, Restated

Hashimoto wants an agent working while the human reviews [1]. AEA allows background work inside a finding. It does not allow background merges. Humans steer hats. MRC steers main. That split is the loop.

## VI. LAYER 4: MEMORY AND STATE

*The model forgets every session. DATE_RE is the only live handoff filename*

Every model call starts empty. The harness reconstructs state. DATE_RE is **one file**: `research/daily-briefs/YYYY-MM-DD.md` — the only live handoff. Archaeology lives in `research/random-thoughts/`. Cadence writes `research/random-thoughts/YYYY-MM-DD-daily-activity.md` (SOP after #263). Do not paste papers into DATE_RE. This playbook is a working note in `research/random-thoughts/`, not `docs/`, until `@aea-product-owner` promotes it. Obsidian wikilinks and `#aea` tags stitch the vault. Uncommitted files are not shared memory. If it is not committed on GitLab `main`, the next session does not have it.

**TABLE V — STATE PERSISTENCE LAYERS (AEA)**

| Layer | Persists | Implementation |
|---|---|---|
| Context window | Current turn | Conversation buffer |
| random-thoughts/ | Session traces | research/random-thoughts/ |
| DATE_RE brief | Only live handoff | research/daily-briefs/YYYY-MM-DD.md |
| Cadence activity | Not DATE_RE | research/random-thoughts/YYYY-MM-DD-daily-activity.md |
| CF queue | Finding lifecycle | research/coherence-findings-loop.md |
| Vault graph | Permanent links | Obsidian wikilinks + #aea |
| Git working copy | Nothing uncommitted | Not shared memory |

### A. DATE_RE versus random-thoughts

`random-thoughts/` is allowed to be messy. DATE_RE is not. Cadence jobs must not write DATE_RE; they write `YYYY-MM-DD-daily-activity.md` after #263. A generator that pollutes the handoff filename recreates [[CF-048]]. The brief is a state file. Treat it like a checkpoint, not a blog.

```
BRIEF = f"research/daily-briefs/{today}.md"   # DATE_RE only
# recovery test: new session reads the committed brief
# uncommitted files are not shared memory
# cadence must not write DATE_RE
```

### B. The Recovery Test

Close the session in the middle of a finding. Open a new one. It must read the committed DATE_RE brief, identify the open CF, and resume without asking a human to re-explain Path B. If it cannot, memory is insufficient. Do not compensate by pasting yesterday's chat. That is not a harness.

### C. Memory versus Guides

Memory records what happened. Guides define what should happen. Promote a stable policy into a skill or a rule. Leave the day's debris in random-thoughts/. Typed handoffs are GitLab issue/MR plus vault, not chat. Do not rely on an agent remembering the ID freeze from a prior conversation.

## VII. LAYER 5: PERMISSIONS AND BUDGETS

*Fourteen hats. No fifteenth implementer. The harness is the security boundary*

The model cannot restrict itself. Permissions are a harness property [3]. AEA encodes them as roles, ID freeze, merge policy, and human confirmation gates.

**Template 2 — AEA capability budget**

```
ALLOW: role-scoped skill under .cursor/skills/aea-*/
ALLOW: one CF -> one issue -> one branch -> one MR
DENY: invent BG / US / FR / NFR IDs
DENY: invent a 15th implementer hat
DENY: knowledge MR closing a UI finding
ASK: archive/ or workbook changes (human confirmation)
HUMAN: secrets, budget (sponsor)
CSS Path B: @aea-ux-designer (hourly ticks must not restyle)
MERGE: @aea-mr-coordinator only; no casual merge
```

**TABLE VI — DEFAULT ACTION POLICY (14 HATS)**

| Action | Default | Reason |
|---|---|---|
| Read vault + skills | Allow | Reversible observation |
| Open CF + issue | Allow | Typed intake |
| Edit Path B CSS | @aea-ux-designer | Dual-viewport ownership |
| Change workbook IDs | Human confirm | ID freeze |
| Merge to main | MRC only | Independent verifier |
| Secrets / spend | Sponsor | Irreversible |
| Invent a hat or ID | Deny | Blast radius |

The fourteen hats are: aea-project-manager, aea-product-owner, aea-ux-designer, aea-customer-journey, aea-support-coordinator, aea-ai-engineer, aea-appsec-auditor, aea-devsecops-platform, aea-senior-software-engineer, aea-mr-coordinator, aea-coherence-guardian, aea-knowledge-guardian, aea-cost-guardian, aea-performance-guardian. Keep 14 hats. Typed handoffs travel through GitLab issues/MRs and the vault, not chat. MRC is the independent verifier. Producer bias is why the producing hat does not merge.

### A. Untrusted Surfaces

Path B reads customer speech. That is untrusted content. A crafted utterance must not expand permissions, mint an FR ID, or trigger a merge. Trusted instructions are guide files and skills. Untrusted data is customer input, retrieved docs, and clip narration. Keep them split [2]. Trusted guides vs shop speech: `docs/` and the dual-viewport spec are not live-shop evidence. A specification merge is not a clip.

### B. Four Budget Dimensions

Scope: which hat, which files, which GitLab actions. Rate: findings per session, not an unbounded rewrite of the shop. Reversibility: workbook edits and live CSS are harder to reverse than a draft MR. Visibility: CF status, Grafana, and the brief must show who did what. Encode all four before unattended runs. NFR-003 (≤ 2.5s) is a latency budget on the model call, not permission to skip sensors.

## VIII. LAYER 6: OBSERVABILITY

*Status words need a probe. Grafana is not a vibe check*

A production harness needs telemetry. Required on Path B: CF queue Last seen / status, guard verdicts, LiteLLM latency via CloudWatch, and Grafana at https://aea.artof.link/grafana/. The honesty rule is the distinctive AEA sensor: status words need a probe. Without it, a faster concierge looks successful while omitting the claim that mattered.

**TABLE VII — AEA TRIP WIRE TRIGGERS**

| Trip wire | Indicates | Response |
|---|---|---|
| DATE_RE honesty (CF-048) | Unprobed status words | Reject the brief |
| graph-guard fail | ID or link drift | Block the MR |
| Cadence writes DATE_RE | Handoff pollution | Stop the job |
| Stale observed_at | Inventory demo-mode | unknown + Select disabled |
| CF row vs merged CSS | False verified ([[CF-054]] class) | Reconcile from `glab`; require post-CSS clip |
| NFR-003 breach | LiteLLM SLA miss | Inspect CloudWatch |

**TABLE VIII — HARNESS HEALTH (NO FAKE TARGETS)**

| Signal | Definition | Direction |
|---|---|---|
| Verified CFs | Rows with an actual probe | Up, honestly |
| Unprobed status words | Claims without evidence | Down to zero |
| Queue lag / false verified | Merged CSS still `in-mr`, or `verified` without a post-CSS clip | Down |
| Fail-closed trips | unknown shown when stale | Must fire |
| MRC merges | Non-MRC merges | Down to zero |
| DATE_RE pollution | Non-handoff writers | Down to zero |

### A. The Real Metric

Do not count tokens, messages, or hats invoked. The cost metric is **cost per verified CF** (and per clip-backed UX claim), not tokens. This paper states no completion-rate percentage and does not copy template `$5` / 3 retries / 80% completion. Those numbers were not probed here. Unknown is the correct word when the probe is missing.

### B. Observability as Debugging Infrastructure

When Path B is wrong, the first question is where. Grafana, CloudWatch, the CF row, and the MR pipeline should answer without replaying the whole conversation. Observability is not overhead. It is how CF-048 was catchable.

### C. Cost Attribution

Cost-guardian exists as a hat. This compilation does not publish a dollars-per-journey figure. Unknown. Track cost per verified CF, and per clip-backed UX claim, when the probe exists — not per chatty session and not per token. LiteLLM spend without an honest shop is not efficiency.

**Operational Review Questions**

- Can you name the CF that last changed status, and the probe that justified it?
- Can you see LiteLLM latency against NFR-003 in CloudWatch?
- Can you tell DATE_RE from a random-thoughts log in one glance?
- Would you know if cadence wrote the handoff file?
- Would you know if the queue said `verified` while the finding note still said `in-mr` after CSS merged?

## IX. THE IMPROVEMENT LOOP

*The ratchet is CF intake. Clip re-record is a sensor, not a launch party*

**TABLE IX — FAILURE CLASSIFICATION (AEA)**

| Failure class | Weak fix (avoid) | Strong fix (prefer) |
|---|---|---|
| Unprobed status (CF-048) | Rewrite the sentence | Honesty rule + DATE_RE trip |
| Invented FR/NFR ID | Correct in chat | graph-guard + ID freeze |
| Knowledge MR closes UI CF | Comment on the MR | Permission + MRC policy |
| Stale availability | Softer copy | Fail-closed Select disable |
| Dual-viewport drift | "Looks fine on my laptop" | Spec + UX-owned CSS + clip probe |
| False verified Path B ([[CF-054]]) | Close issue from spec/CSS MR | Post-CSS clip + `glab` reconcile sensor |
| Loop tick merge | Revert later | MRC-only merge |
| Lost session context | Re-explain Path B | Committed DATE_RE brief |

> "Prompts guide behavior. Environments prevent entire classes of failure."
>
> — Lauren Tan, Cursor [10], applied to Path B environments

CF intake is the ratchet, and the ratchet belongs at the **strongest** layer (sensor/CI), not another paragraph. Each failure that lands as a numbered finding, with one issue and one MR, reduces the chance the next session repeats it. The same error three times becomes a sensor. Early in a vault, guide growth is fast. A mature harness adds fewer rules and more guards. Lean by subtraction. This paper does not claim a rules-per-week rate. Unknown.

### A. The Six-Step Engineering Loop

When Path B fails: (1) Reproduce with the same journey and viewport. (2) Classify: missing guide, absent sensor, permission gap, state loss, or observability blind spot. (3) Pick the strongest layer (sensor/CI before a new sentence). (4) Encode the fix. (5) Verify on the original case. (6) Run guards so you did not break [[FR-011]] while fixing copy. Skip no step. Skipping (1) fixes a phantom. Skipping (5) is how [[CF-054]] became a false verified: CSS merged, issue closed, queue said `verified`, no post-CSS clip.

### B. Clip Re-record as Ratchet

Re-record [[J1]]–[[J4]] when the dual-viewport spec or CSS changes. A clip that predates !300 is not evidence that !300 works on the live shop. Encode the class: Path B `verified` requires a clip dated after the CSS/product merge; hourly ticks must reconcile Issue/MR from `glab` (not from the queue text). The 2026-08-28 trail, probed again that evening Berlin: knowledge !298 merged; spec !299 merged and closed #272; feat(ux) CSS !300 merged as `63aaa4ce`; queue row on main is `regressed` after !304 (was `verified` with #272 / !298, !299, !300 — a **false verified**). Finding note on main after !304: `regressed` / #273. Live [[J1]] phone+desktop re-record after !300: Unknown. [[CF-054]] is **regressed**. Do not invent CF-055.

**TABLE X — CONTROL RELIABILITY LADDER**

| Layer | AEA example | Reliability |
|---|---|---|
| Memory | Correction in chat | Low |
| Prompt | "Be honest in the brief" | Low-Medium |
| Guide | AGENTS.md + skill rule | Medium |
| Sensor | check_coherence.py / fail-closed | High |
| Environment | MRC merge + CI + ID freeze | Highest |

## X. BUILD PATH: HOW AEA ALREADY INSTANTIATED THE LAYERS

*Not a fake seven-day greenfield. The vault is the path*

Do not pretend AEA was stood up in a week on an empty repo. The six layers are already instantiated, unevenly. The build path is to notice which layer is thin and strengthen it from real CFs. Roadmap group milestones are M0-M7 MVP, M8-M12 post-MVP, then Future Backlog. DATE_RE 2026-08-28 listed Active Focus Unknown. Milestone lines are roadmap labels, not ship-counts. Do not claim M14-M18 production-ready.

**TABLE XI — AEA LAYER INSTANTIATION (AUGUST 2026)**

| Layer | Already in vault | Honest gap |
|---|---|---|
| Guides | AGENTS.md, 4 rules, 14 skills, ADRs, Path B spec | Lean by subtraction (#275 queued) |
| Sensors | coherence / graph / guards / CI / fail-closed | DATE_RE 14/14 unprobed here |
| Loop | CF queue, one-finding rule, MRC merge | [[CF-054]] false verified; clip Unknown |
| Memory | DATE_RE one file; random-thoughts archaeology | Uncommitted-as-memory temptation |
| Permissions | 14 hats, ID freeze, UX CSS ownership | 15th-hat gravity |
| Observability | Grafana, CF Last seen, CloudWatch, honesty | Live [[J1]] re-record after !300 Unknown |

### A. What MVP Actually Includes

Requirements count is 23 FR + 17 NFR = 40. Source of truth: `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`. Cite existing IDs only. MVP includes conversational discovery, editable Shared Understanding ([[FR-001]]/021), validated recommendations ([[FR-007]]), T-03 Available badge ([[FR-011]]/[[NFR-009]]), thin T-04 [[FR-003]] (size, card message, flower_type/colour/ribbon per ADR-006), delivery, itemized summary FR-018, payment FR-019 (mockup / not live Stripe), tracking FR-023, FAQ [[FR-009]].

### B. What Is Not Shipped

Future / not shipped: live Stripe, browser LCP / Edge SSR, staff live chat, WebRTC, full CRM analytics FR-017, inventory forecasting FR-012. Thin CRM occasion reminders landed as #254/!297 and remain FR-016 Future in the workbook. Naming a merge is not the same as moving the workbook ID.

### C. Expansion Pattern

After the layers exist, expansion follows the ratchet. Run Path B. Every failure names a layer. Same error twice: guide hole. Same error three times: become a sensor. Subtly wrong shop: sensor hole. Scope creep: permission too broad. Cannot diagnose: observability hole. Change one layer at a time. Do not scale hats because the model is impressive. Do not restyle Path B CSS from a knowledge MR.

**Scale Gate — Expand Only When These Are True**

- MRC, not the producer, is the only merger on main.
- Fail-closed inventory has tripped on a stale observation, not only on happy path.
- DATE_RE recovery test passed on a new session.
- Honesty rule has caught at least one unprobed status word.
- A clip probe exists for the journey you claim, dated after the CSS that claimed it.
- No fifteenth hat has been introduced as "just this once."

### D. Draft status (28 August 2026, evening Berlin)

Backlog opened ~22:02 Berlin. Steps are **in progress**, not done.

- #273 `cf-054: Path B verified requires clip dated after CSS (queue reconcile)` — SOP merged as !304; clip after CSS Unknown. Do not treat that merge as clip-verify.
- #274 `harness: DATE_RE stays one file; date and prune guide rules` — in progress (vault placement)
- #275 `harness: prune guide/skill lines that CI sensors already enforce` — queued
- Live [[J1]] re-record after !300: Unknown

Do not mark [[CF-054]] `verified` in this note until those clips exist. The queue word `verified` on main was a false verified until !304. Status on main (probed after merge): **regressed**, pending a clip dated after the CSS merge. !304 is the SOP+queue correction and **merged** 28 Aug 22:14 Berlin. Clip after CSS still Unknown.

## XI. DECISION FRAMEWORK

*Start at the simplest layer that matches the observed failure*

**TABLE XII — ARCHITECTURE DECISION FRAMEWORK (AEA)**

| Problem | Start with | Do not add yet |
|---|---|---|
| Known errors repeat | Strongest layer (sensor/CI); prune duplicate guide | Another hat |
| Availability lies | Fail-closed sensor | Softer copy |
| Hat exceeds scope | Permission + ID freeze | Full committee every edit |
| State lost next session | Committed DATE_RE | Vector memory |
| Status words drift | Honesty trip wire | LLM-as-judge on the brief |
| Viewport divergence | Spec + UX-owned CSS | A second product |
| Loop never stops | One-CF + MRC | Multi-agent debate |

Run the experience. Observe failures. Let the harness grow from CFs. Do not build a heavier harness than the shop. Do not skip sensors because the concierge sounded sure.

## XII. PRODUCTION CHECKLIST FOR PATH B + ENGINEERING HARNESS

*A shop is not production because the demo clip is pretty*

**TABLE XIII — PATH B PRODUCTION READINESS CHECKLIST**

| # | Requirement | Failure if missing |
|---|---|---|
| 1 | AGENTS.md SOP + DATE_RE handoff | Every session starts from zero |
| 2 | 14 hats, no 15th | Shadow implementer |
| 3 | FR/NFR ID freeze + graph-guard | Workbook drift |
| 4 | Computational guards in CI | Errors reach the shop |
| 5 | Fail-closed FR-011 / NFR-009 | Available on stale data |
| 6 | One CF / issue / branch / MR | Queue fan-out |
| 7 | MRC-only merge | Producer bias on main |
| 8 | Honesty rule ([[CF-048]] / [[CF-054]] class) | Unprobed or false-verified status |
| 9 | Grafana + CloudWatch NFR-003 | Blind latency and drift |
| 10 | Trusted/untrusted split | Speech as instruction |
| 11 | UX ownership of Path B CSS | Viewport fork |
| 12 | Clip probe dated after the CSS | Claim without evidence |

## XVI. WHEN NOT TO GROW THE HARNESS

*Not every utterance justifies another skill*

A harness earns its cost when the experience repeats, failures have customer consequences, sessions must preserve Shared Understanding, or more than one hat touches main. One-off copy brainstorms, exploratory product talks, and throwaway prototypes do not need DATE_RE, MRC, and fourteen skills. Path B is not that. It is external-facing and must stay honest about stock, payment mockups, and tracking.

**TABLE XVI — HARNESS DECISION FILTER**

| Scenario | Harness? | Why |
|---|---|---|
| One-off copy riff | No | No recurrence |
| Exploratory UX sketch | Maybe | If it will hit Path B CSS, yes |
| Live availability claim | Yes | FR-011 customer consequence |
| Daily DATE_RE handoff | Yes | Next session depends on it |
| CF intake / MRC merge | Yes | Main is shared |
| Personal note in random-thoughts | No | Not shared memory |
| Payment FR-019 mockup | Yes | Must not imply live Stripe |
| 3DX Lab work | Separate | Out of scope for this paper |

The test: would a customer notice a silent wrong Available badge? Then you need a sensor. Would the next session need yesterday's intent? Then you need DATE_RE. Would a mistaken merge change the shop? Then you need MRC. If none apply, the conversation itself is enough.

## XVII. HARNESS ENGINEERING FOR THE FOURTEEN HATS

*Multi-agent here means typed hats, not a swarm*

The six-layer harness applies to each hat. The system additionally needs typed handoffs, a shared vault, a routing policy (the CF queue), and an independent verifier no producer can override. That verifier is @aea-mr-coordinator.

### A. Typed Handoffs

When @aea-ux-designer passes work to @aea-senior-software-engineer, the handoff is a GitLab artifact plus vault, not chat: issue, MR, evidence, unresolved remainder. "Done, looks good" must not advance Path B. The receiver should open the spec or the CSS and check. Packet fields still apply: identity, pointer, evidence, assumptions, deadline [11].

### B. Shared Memory versus Shared Context

Fourteen hats in one conversation pollute context. AEA's better pattern is already in the vault: hats read DATE_RE, the CF row, and the skill that matches the hat. They do not inherit another hat's discarded plan. Uncommitted files remain private.

### C. The Verifier Must Be Independent

The hat that produced the CSS is not the judge of whether [[CF-054]] is verified. Producer bias is real. A closed issue is not a clip. Deterministic guards first. MRC reports gate failures without silently rewriting the shop. Auto-merge when gates pass is still an MRC act, not a courtesy from the producer. Escalation to MRC or PO is a successful stop.

**TABLE XVII — FOURTEEN-HAT HARNESS EXTENSIONS**

| Multi-hat layer | Single-hat equivalent | What it adds |
|---|---|---|
| GitLab issue / MR packet | Self-check | Contract between hats |
| Vault + DATE_RE | Session log | Cross-hat memory |
| CF queue routing | Agentic loop | One-finding assignment |
| @aea-mr-coordinator | Computational sensor | Producer-consumer split |
| PO / PM / sponsor packet | Human approval | System-level escalation |

## XVIII. CONCLUSION

The model provides interpretation. Domain services provide validation. The outer harness determines whether Lily's Florist is a product or a demo. Related work shows that harness-only changes can move coding-agent benches [2], [6], [7]. Those benches are not this shop. AEA's claim is smaller and stricter: Adaptive Experience = Shared Understanding + Domain Services + Outer Harness. The six layers are the minimum infrastructure for an experience that must work across sessions and viewports without improvising IDs or availability.

Guides prevent known failures. Sensors catch new ones. The agentic loop bounds work to one CF. Memory persists in DATE_RE, not in chat. Permissions freeze fourteen hats. Observability makes honesty checkable. The practical recommendation remains the ratchet: when Path B lies, fix the harness at the strongest layer (sensor/CI), not the sentence. Start from the vault that already exists. Add one guard. Keep one merge owner. Log one probe. Lean by subtraction. The harness accumulates. The experience becomes inspectable.

A reliable AEA system should make this statement true: every important shop claim traces to a guide that shaped it, a sensor that verified it, a hat that was allowed to touch it, a brief that preserved it, and a log that recorded it. When that statement is false, more model calls usually increase opacity. When it is true, the harness is an engineering mechanism rather than a personality.

> "The engineers who thrive in 2026 are not the ones who write the most code. They are the ones who build the best environments for agents to write code in." On Path B the line restates: the team that thrives is the one that builds the best environment for an experience to stay honest.

## XIV. HARNESS VS. PROMPT AND CONTEXT FOR EXPERIENCE SYSTEMS

*Why a dual-viewport florist cannot be prompt-engineered into honesty*

**TABLE XIV-B — THREE DISCIPLINES, EXPERIENCE-SHAPED**

| Challenge | Prompt Eng. | Context Eng. | Harness Eng. |
|---|---|---|---|
| False Available | "Don't overclaim" | Retrieve stock text | Fail-closed sensor |
| Lost intent | Summarize in prompt | Memory / SU object | DATE_RE + FR-001 |
| Wrong hat edits CSS | Instruct in chat | Limit file list | UX ownership + MRC |
| Quality varies | Add examples | Few-shot journeys | Guards + clip probe |
| Runs on forever | "Be concise" | Limit context | One-CF + merge policy |
| Errors repeat | Re-add correction | Store in notes | Guide + CF ratchet |
| Unprobed status | Add warning | Retrieve last brief | Honesty trip wire |

A prompt cannot disable Select. A retrieval pipeline cannot stop a knowledge MR from closing a UI finding. A memory system cannot fire a DATE_RE trip wire. Those are harness responsibilities. Prompt, context, and harness all exist on Path B. If forced to spend the next engineering hour, spend it on the layer that makes a lie unrepresentable.

### A. Compounding

Guide rules, guards, and merge policy compound across sessions. Prompt corrections do not. Context corpora degrade as they grow. Harness improvements are structural. That is the lesson borrowed from related work, not a reprint of its bench deltas.

### B. When All Three Are Needed

The concierge voice is a prompt problem. Shared Understanding is a context problem. Fail-closed inventory, MRC, and honesty are harness problems. Removing any layer weakens Path B. The next hour still belongs to the harness when the shop is already fluent and still untrustworthy.

## XIV. LIMITATIONS AND COMMON MISTAKES

*What goes wrong even with fourteen hats*

### A. The Over-Engineered Fifteenth Hat

A harness with a shadow implementer, twelve inferential judges, and a forty-step approval chain is not safety. It is latency. The harness should be the minimum that keeps Path B honest. If hats spend more time coordinating than shipping probed findings, the harness is too heavy. Do not invent a 15th implementer to "just finish the CSS."

### B. DATE_RE Pollution

Cadence jobs writing DATE_RE, or sessions dumping random-thoughts into the handoff filename, recreate [[CF-048]]. Cadence writes `YYYY-MM-DD-daily-activity.md` after #263. Prune. Expire. Keep one live brief name (`research/daily-briefs/YYYY-MM-DD.md`). Do not paste papers into DATE_RE. A stale brief that claims Active Focus as fact when DATE_RE 2026-08-28 said Unknown is a sensor miss. Date and prune guide rules (#274, in progress).

### C. Claiming Verified Without a Probe

[[CF-054]] is the object lesson — and the live regression. Knowledge !298 merged. Spec !299 merged and closed #272. CSS !300 merged as `63aaa4ce` on 2026-08-28. The queue row on main is `regressed` after !304 (was `verified` with #272 / !298, !299, !300 — a **false verified**). The finding note on main after !304 is `regressed` / #273. Live [[J1]] re-record after !300 is Unknown. Treat [[CF-054]] as **regressed**, pending a clip dated after the CSS merge. Closing a GitLab issue from a spec/CSS MR is not verification. Do not invent CF-055. Sensors that only confirm formatting will pass a shop that still fails [[J3]] reorder and [[J4]] tracking.

### D. Memory Without Cleanup

`random-thoughts/` accumulates. Old notes reference MRs that were superseded. A new session that treats them as DATE_RE will relitigate closed work. Keep the handoff thin. Leave archaeology in labeled logs.

### E. The Harness Does Not Fix Bad Objectives

If the workbook said FR-019 is live Stripe, sensors would faithfully implement a false shop. The harness amplifies the objective. Review the FR/NFR source of truth before ratcheting. Do not invent IDs to make the objective prettier.

**TABLE XV — COMMON AEA HARNESS MISTAKES**

| Mistake | Symptom | Fix |
|---|---|---|
| 15th hat | Shadow implementer | Stay at 14 |
| DATE_RE pollution | Handoff lies | Filename freeze + trip wire |
| False verified ([[CF-054]]) | Queue `verified`, finding note `in-mr`, no post-CSS clip | Clip-after-CSS sensor + `glab` reconcile |
| No computational sensors | Expensive judges | Guards first; same error 3× → sensor |
| Casual merge | Producer bias | MRC only; escalation is a successful stop |
| Wrong FR status | Workbook drift | Human confirm + ID freeze |
| Clip as trophy | Stale evidence | Re-record after CSS; spec is not shop evidence |

## XV. AEA CASE EVIDENCE (HONEST)

*Lily's Florist Path B; no borrowed benches*

### A. Lily's Florist, Path B

The product is an AI-native florist. Customers speak naturally. The interface evolves as understanding grows. Dual presentation: one session, desktop Adaptive Workspace, phone linear concierge. Live shop: https://aea.artof.link. Canonical remote: https://gitlab.com/artof-group/adaptive-experience-architecture. This is the case, not a coding-agent leaderboard.

### B. CF-048, Daily-Brief Honesty

CF-048 is the AEA exhibit for demos that never ship. Status language outran probes. Verification: GitLab #259 / !280. The harness fix is the honesty rule plus the DATE_RE trip wire. That is a real ratchet step. It is not a 44-point bench swing, and this paper does not dress it up as one.

### C. Dual-Viewport Trail (CF-054)

On GitLab main (probed 28 August 2026, evening Berlin): knowledge !298 merged; spec !299 merged and closed #272; feat(ux) CSS !300 merged as `63aaa4ce`; queue row said `verified` until !304 merged (28 Aug 22:14 Berlin) — a **false verified**; main is now `regressed`; finding note after !304 is `regressed` / #273. Live shop re-record of [[J1]] phone+desktop after !300 is Unknown. [[CF-054]] is **regressed**, not clip-verified. Closing a GitLab issue from a spec/CSS MR is not verification. Path B `verified` requires a clip dated after the CSS/product merge. Do not invent CF-055. Report the trail. Do not round it up to verified. The SOP+queue fix is !304 (**merged** 28 Aug 22:14 Berlin, Related #273). Clip after CSS still Unknown.

The Path B / UI evidence section already on main states: after the product MR merges, re-record the same script on both viewports; mark `verified` only if the new clip shows the fix; otherwise leave it open or set `regressed`; Unknown until those clips exist. Hourly ticks must not restyle Path B CSS/JS unless `@aea-ux-designer` was invoked. A knowledge or intake MR may land first; that does not close a UI finding.

### D. Journeys and Leftovers

[[J1]] Urgent Sam, [[J2]] Planner Sarah, [[J3]] Loyal Alex, [[J4]] Tracker Chris. Honest leftovers from 2026-08-27 clips remain: [[J3]] recall without reorder badge; [[J4]] ASO fail-closed not T-08; Track gated until checkout. Those leftovers are evidence of the sensor layer doing its job when humans look. They are also evidence the shop is not a finished trophy. They are not evidence that !300 works.

### E. What This Case Does Not Show

It does not show GAIA deltas, Terminal Bench ranks, or a million generated lines. It does not show live Stripe, Edge SSR LCP, staff live chat, WebRTC, FR-017, or FR-012. It does not show 14/14 skills independently probed. It does not show [[CF-054]] clip-verified. Related work remains related work [1]-[15].

## APPENDIX: GLOSSARY

**TABLE XIV — KEY TERMS**

| Term | Operational definition |
|---|---|---|
| Adaptive Experience | Shared Understanding + Domain Services + Outer Harness |
| Outer harness | 14 hats, vault, CF loop, CI guards, DATE_RE, honesty |
| Inner runtime | Edge BFF + domain services + PostgreSQL + broker (ADRs) |
| Guide | Feedforward: AGENTS.md, rules, skills, ADRs, Path B spec |
| Sensor | Feedback: python guards, CI, fail-closed, clip probes |
| CF loop | One finding -> one issue -> one branch -> one MR |
| DATE_RE | One file: research/daily-briefs/YYYY-MM-DD.md; only live handoff. Cadence writes YYYY-MM-DD-daily-activity.md. Do not paste papers here. |
| Honesty rule | Status words need a probe ([[CF-048]] / [[CF-054]] class) |
| Fail-closed | Missing/stale observed_at -> unknown -> Select disabled |
| MRC | @aea-mr-coordinator; independent merge verifier |
| Path B | Dual viewport: desktop Adaptive Workspace + phone concierge |
| Path B verified | Clip dated after the CSS/product merge; issue-close is not a probe |
| False verified | Queue says `verified` without the required probe ([[CF-054]] on 28 Aug) |
| Unknown | Required label when a probe was not run |

## REFERENCES

[1] M. Hashimoto, "My AI Adoption Journey," mitchellh.com, Feb. 5, 2026. Related work.

[2] R. Lopopolo, "Harness Engineering: Leveraging Codex in an Agent-First World," OpenAI, Feb. 11, 2026. Related work; 1M-line figure is not an AEA result.

[3] B. Böckeler, "Harness Engineering for Coding Agent Users," martinfowler.com, Apr. 2026.

[4] E. Mollick, "A Guide to Which AI to Use in the Agentic Era," 2026.

[5] V. Trivedy, "The Anatomy of an Agent Harness," LangChain Blog, Mar. 10, 2026.

[6] A. Masood, "Agentic Harness Engineering," Google Cloud / Medium, Jun. 2026. GAIA deltas are not AEA results.

[7] LangChain Eng., "Improving Deep Agents with Harness Engineering," Feb. 17, 2026. Terminal Bench ranks are not AEA results.

[8] Faros AI, "AI Engineering Report 2026: Acceleration Whiplash," Aug. 2026.

[9] Can.ac, "I Improved 15 LLMs at Coding in One Afternoon. Only the Harness Changed," 2026.

[10] L. Tan, "How Cursor Turned AI Agents Into Better Engineers," Aug. 12, 2026.

[11] Google Cloud, "Harness Eng. for Multi-Agent Systems Using Google ADK 2.0," Jul. 2026. Not an official Google research paper; cited as related public material.

[12] Anthropic, "Building Effective AI Agents," anthropic.com, Dec. 2024.

[13] A. Osmani, "Agent Harness Engineering," addyosmani.com, Apr. 2026.

[14] OpenAI, "Codex Agent Best Practices," 2026.

[15] Independent compilation, "Production Agent Engineering Practice 2026 / Harness Engineering / Agent = Model + Harness: The 6-Layer Production Playbook" (harness_final.pdf). Independently compiled, not affiliated with Google, OpenAI, or Anthropic. Used as document-design template only.

[16] Art of Group, Adaptive Experience Architecture, GitLab: https://gitlab.com/artof-group/adaptive-experience-architecture (AGENTS.md; .cursor/rules; .cursor/skills/aea-*/; research/coherence-findings-loop.md; research/daily-briefs/; docs/01-product-vision/product-vision.md; docs/05-ux-design-guide/path-b-dual-viewport-specification.md; archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx).

[17] Lily's Florist Path B live shop, https://aea.artof.link, and Grafana, https://aea.artof.link/grafana/.

[18] GitLab issues/MRs cited as already probed: [[CF-048]] #259/!280; dual-viewport !298/!299/!300 (`63aaa4ce`) and #272 (closed by spec !299); [[CF-054]] was a false `verified` until !304; main is now `regressed`; live [[J1]] re-record after !300 Unknown; harness backlog #273 (SOP merged as !304; clip after CSS Unknown) #274 (in progress) #275 (queued); thin CRM #254/!297.

*Source Method.* This document is an independent practical synthesis of AEA vault facts and of the public harness-engineering materials cited above. It is not affiliated with Google, OpenAI, Anthropic, or HashiCorp, and is not endorsed by them. Product behavior may change. This revision (28 August 2026, evening Berlin) read GitLab `main` via MCP `get_repository_file` / `get_work_item` / `get_merge_request` (no clone): `research/coherence-findings-loop.md` (queue row 54 is `regressed` after !304; was a false `verified` with #272 / !298, !299, !300); `research/findings/CF-054-path-b-dual-viewport.md` (`status: regressed`, `merge_request: !304`); issues #272 closed, #273 closed with !304 (close is SOP/queue honesty, not clip-verify), #274 #275 open; MRs !298, !299 (closed #272), !300 merged as `63aaa4ce`; !304 **merged** 28 Aug 22:14 Berlin (Related #273) and is the SOP+queue fix — do not treat !304 as clip-verify. Live [[J1]] after CSS remains Unknown. Recommendations, templates, pseudocode, and decision rules are the author's adaptation for AEA Path B and are not official specifications of any organization mentioned in related work. All diagrams are original. Unknowns are labeled. Comparison or field feedback that would change a claim, a sensor, or a limitation revises this note.






