# Session Memory Log: AEA Grok shared-library skill matrix

> **Tags**: #aea #skills #honesty #grok-bot #second-brain
> **Captured**: 2026-09-12
> **GitLab**: [#433](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/433)
> **Author**: `@aea-knowledge-guardian`
> **Related**: [[2026-08-22-missing-skill-gap-assessment-framework]] · [[2026-08-25-trust-but-verify-job-and-single-role-list]] · [[2026-09-12-session-handover-afk-cloud-runners]]

---

## Honesty

This note inventories **Grok shared library skills** (sand-workflow / Grok library recipes). It is **not** an inventory of `.cursor/skills/aea-*` role SOPs.

Every row in the matrix is **Documented** — the recipe exists in the Grok library and/or this vault note. **None** of these rows are Live-probed as an agent-behavior metric. This session has **no probe** of skill invocation, so status is not Live.

Do not promote a row to Live without a dated probe.

Pointer: [work item #433](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/433).

---

## Matrix

Columns are **Skill | Scope | Why? | What**. Shared rows 1–4 already existed on 2026-09-12 and are referenced, not re-authored. Rows 5–9 were created 2026-09-12 by the AEA lane (Grok library ids in backticks). Status for every row: **Documented**.

| Skill | Scope | Why? | What |
|---|---|---|---|
| PR train rebase | Parallel cloud MRs | Future `!503`–`!509`; `!511` then rebase `!510` | Order merges; rebase survivors; no invented conflict scope |
| Honesty ledger gate | FR/NFR status | Play honesty `#390`; `#427` 500 before migrate | Evidence-only promotion; Unknown over guessing |
| Companion plain docs | knowledge.*/architecture.* | Dual-track vault + mobile bar | Plain English + diagrams; formal spec wins |
| Persona journey validation | Live UX audits | Reactive Need→Pick→Pay / ROG / florist; would have caught `#399`/`#400`/`#410` earlier | Standing personas → issues → fix |
| One finding one MR (`one-finding-one-mr`) | Issue/MR hygiene | Parents `#27`/`#35`/`#36` auto-closed by child Closes | One finding→issue→MR; reopen parents |
| Coordinator merge hats (`coordinator-merge-hats`) | Merge authority | MRC vs implementer | Implementer does not self-merge; coordinator merges green non-draft |
| Deploy schema honesty (`deploy-schema-honesty`) | Path B/ECS | `!506` live without RDS tables until RunTask migrate | Deploy≠migrate; dual-probe; vault evidence |
| Committed vault memory (`committed-vault-memory`) | Multi-agent | Only committed `research/` inherits | Search vault first; commit notes with fixes |
| Process-coherence MR body (`process-coherence-mr-body`) | GitLab MR CI | Strict Closes/Validation/Integration evidence | Shape body; `glab` not `gh` |

---

## Deferred / out of scope

Café freeze-first, fail-closed DB/Pages, SES fail-soft, and image allowlist belong to other lanes. Not claimed here.

## OOTB Cursor skills used historically

- `code-changes`, `routines`, `skill-authoring`: yes
- `box-desktop`: partial

## Do not

- Claim Live without a probe.
- Duplicate these recipes as `.cursor/skills/aea-*` role SOPs.
- Hand-edit the generator-owned DATE_RE brief.
- Merge from the author session. MRC owns merge after gates.
