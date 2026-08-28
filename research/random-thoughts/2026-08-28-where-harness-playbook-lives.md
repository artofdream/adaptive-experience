# Where the harness playbook and comparison live (2026-08-28)

> **Tags**: #aea #second-brain #harness #knowledge-first #path-b
> **Captured**: 2026-08-28
> **GitLab**: Related #274 (this note). Related #273 via !304 (**merged**). #275 queued.
> **Related**: [[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] [[2026-08-27-session-memory-log-cf054-path-b-ux-in-coherence-loop]] [[2026-08-26-date-re-bus-and-agent-runner-image-roll]] [[2026-08-28-aea-framework-harness-engineering]] [[2026-08-28-aea-vs-harness-playbook-comparison]]
> **This node is knowledge, not DATE_RE, not a UI restyle.**

Later agents: shared memory is committed GitLab `main` only. A status word is a claim. Probe or write Unknown.

## 1. Decision

The 2026-08-28 AEA 6-layer playbook and the comparison vs `harness_final.pdf` are **Second Brain working notes**, not published architecture.

| Artifact | Lives in | Does not live in |
|---|---|---|
| Framework playbook (md) | `research/random-thoughts/2026-08-28-aea-framework-harness-engineering.md` | DATE_RE, `docs/`, GitHub mirror |
| Comparison (md) | `research/random-thoughts/2026-08-28-aea-vs-harness-playbook-comparison.md` | DATE_RE, `docs/` |
| This placement note | `research/random-thoughts/2026-08-28-where-harness-playbook-lives.md` | DATE_RE, `docs/` |
| PDFs | optional local / chat attachments | git (binaries are not the vault) |
| Clips | evidence paths, not vault bodies | DATE_RE |
| Implementation | GitLab issues #273 #274 #275, one finding one MR | a 15th hat |

`docs/` is for canonical product/architecture after `@aea-product-owner` promotes a note. Until then, `research/` is the working area. DATE_RE may list recent Second Brain filenames after a knowledge merge. Do not paste the paper into DATE_RE.

Wikilinks and `#aea` keep the graph-guard happy. Cite existing [[FR-001]] [[J1]] [[CF-048]] [[CF-054]] IDs. Do not invent BG/US/FR/NFR.

## 2. DATE_RE one-file binding

Read on GitLab `main` (no clone): `scripts/check_daily_brief_freshness.py` defines `DATE_RE = re.compile(r"^(\\d{4}-\\d{2}-\\d{2})\\.md$")`. That is the only live handoff filename.

- DATE_RE = only `research/daily-briefs/YYYY-MM-DD.md`.
- Archaeology belongs in `research/random-thoughts/`.
- Cadence writes `research/random-thoughts/YYYY-MM-DD-daily-activity.md` after #263 / !285. Cadence must not create, edit, append, restore, or commit DATE_RE.
- Do not paste papers into DATE_RE.
- DATE_RE may list recent Second Brain filenames after merge, not the paper body.
- Typed handoffs stay GitLab issue/MR + vault, not shared chat.
- Owner of DATE_RE remains `scripts/generate_daily_brief.py` plus honest hand-review (see [[2026-08-26-date-re-bus-and-agent-runner-image-roll]]).
- This MR does **not** rewrite AGENTS.md or session-start SOP. Guide prune is #275 (queued). Monthly prune of rules sensors already cover remains undone — hence **Related #274**, not Closes.

## 3. How a later session should use them

1. Session start: DATE_RE, then this node if the work is harness/lean/CF-054.
2. Treat the playbook as a map of the outer harness, not as ship evidence. Template benches are related work, not AEA results.
3. Lean/antifragility/maintainability work is the backlog, not more paper:
   - #273 CF-054 clip dated after CSS + queue reconcile. SOP+queue fix is !304 (**merged** 28 Aug 22:14 Berlin). On `main` the CF-054 queue row is `regressed`. GitLab closed #273 with that merge; the close is SOP/queue honesty, not clip-verify. Live [[J1]] clip after CSS !300: Unknown.
   - #274 DATE_RE one file + this placement (this MR). Disjoint files from !304.
   - #275 prune guide lines sensors already enforce (queued). Do not start #275 here.
4. MRC merges. Knowledge guardian writes notes. UX owns the clip. Coherence owns the CF row.

## 4. Next draft of the playbook

Mark steps **in progress**, not done:

- Clip-verify close sensor (CF-054 / #273): SOP merged as !304; clip after CSS Unknown
- Queue reconcile from `glab`: on `main` after !304 (CF-054 is `regressed`)
- Guide/skill prune (#275): queued
- DATE_RE thin (#274): in progress via this note
- Live J1 re-record after !300: Unknown

Do not mark CF-054 `verified` in the paper until those clips exist. Paper language: **regressed** on main after !304; clip after CSS Unknown.

## 5. Disjoint from !304

!304 touches `.cursor/rules/coherence-findings-sop.mdc`, `research/coherence-findings-loop.md`, `research/findings/CF-054-path-b-dual-viewport.md`, and `research/random-thoughts/2026-08-28-session-memory-log-cf054-regressed-clip-verify.md`. This MR does not touch those files. No shop CSS. Branch is from `main`, not from the #273 branch.
