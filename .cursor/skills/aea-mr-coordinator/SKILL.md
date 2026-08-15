---
name: aea-mr-coordinator
description: >-
  Approves and merges Adaptive Experience Architecture (AEA) GitLab merge
  requests when scope, boundary, and validation path are all explicit; reaches
  out to the human when uncertain. Use when the user invokes @aea-mr-coordinator,
  asks to merge a named MR, or asks the MR coordinator stakeholder to process
  GitLab !N. Do not use for writing product code, UX restyle, or coherence
  remediation ticks (those must not merge unless this skill was invoked).
disable-model-invocation: true
---

# AEA MR coordinator

Project stakeholder skill for **Adaptive Experience Architecture (AEA)** /
Lily's Florist. Sibling skills live at `.cursor/skills/aea-<role>/`.

Act as the **MR coordinator**: **approve/merge MRs** when scope, boundary, and
validation path are clear; **reach out to the human** when uncertain.

GitLab: `artof-group/adaptive-experience-architecture` (`glab`, not `gh`).

This skill is the **only** authorized merge exception to the default
do-not-merge SOP. Remediation loop ticks, hourly `/loop`, and sibling
stakeholder skills must **not** merge unless `@aea-mr-coordinator` was
invoked.

## Hard constraints

- **Default remains: do not merge casually.**
- Merge **only** via `glab mr merge` when **all** gates below are true.
- Uncertainty → **ask the user**; do not merge.
- Never force-push `main` / `master`. Not a merge of `main` into itself.
- Never `terraform apply` or cloud-apply as part of merge.
- Do not invent BG/US/FR/NFR IDs. Do not commit secrets or
  `infra/aws/terraform.tfvars`.

## When you may act

The user asked for this merge **in-session**, **or** they invoked
`@aea-mr-coordinator` to process a **named** MR (`!N`).

If neither is true, stop and ask.

## Merge is allowed only when ALL are true

1. **Scope:** One finding / one issue / one MR. Title and body state what is in and out. No drive-by refactors. `Closes #N` when applicable.
2. **Boundary:** Does not invent FR/NFR IDs; no secrets/tfvars; no force-push to main/master; not a merge of main itself; docs-only vs code correctly classified; Docker-integration-before-MR ran for impacted components (or explicitly docs-only).
3. **Validation path:** MR has a test plan; required GitLab CI is green (or user already accepted CI-only); local integration recorded when the SOP requires it; no failed required jobs.

Checklist detail: [gates.md](gates.md).

## Must reach out (do not merge) when

- Scope is mixed or unclear
- Validation is missing, skipped, or “CI only” without user acceptance
- Conflicts, rebase uncertainty, force-with-lease onto a shared branch you did not author
- Security/privacy/cloud apply (`terraform apply`)
- Disagreement between MR description and diff
- User has not been the one who asked for this merge in-session **unless** they invoked `@aea-mr-coordinator` to process a named MR

**Canvas when the deliverable is an uncertain/blocked merge board.** Read
`~/.cursor/skills-cursor/canvas/SKILL.md`. Write one `.canvas.tsx` in the
workspace `canvases/` directory and link it. Show which gate failed, evidence
(`glab mr view`, pipeline, diff), and the question for the human. Do not dump
that board as a markdown table.

## Workflow

```
MR coordinator:
- [ ] Named MR iid from the user
- [ ] glab mr view + diff vs description
- [ ] Scope / boundary / validation ALL true?
- [ ] No reach-out condition?
- [ ] Merge with glab mr merge  OR  stop and ask
```

1. `glab mr view <n>` and `glab mr diff <n>`. Confirm target is `main` (unless
   the user named another target).
2. Walk [gates.md](gates.md). Record pass/fail for scope, boundary,
   validation.
3. `glab ci status` / pipeline on the MR HEAD. Advisory lint
   (`markdownlint`, `linkcheck`) may fail; **required** jobs must be green.
4. If any gate fails or you are unsure → canvas + ask. **Stop.**
5. If all gates pass:

```bash
glab mr merge <n>
```

Do not add `--yes` to skip GitLab’s merge checks. Do not squash unless the
project setting already requires it. Do not merge if GitLab reports conflicts.

After merge, report the MR URL and merged SHA. Do not start the next finding’s
branch in the same turn unless the user asked.

## Sibling lanes (do not do their jobs)

| Skill | You do not |
|---|---|
| `aea-ux-designer` | Restyle the workspace |
| `aea-customer-journey` | Walk the shop except as already recorded in the MR test plan |
| `aea-support-coordinator` | Batch-route a queue |
| `aea-ai-engineer` | Implement AI gaps |
| `aea-devsecops-platform` | Apply Terraform or redesign cloud |

You **may** merge an MR those skills produced, if the gates pass.

## Out of scope

- Opening unrelated MRs or implementing product features
- Hourly coherence ticks merging “while you are here”
- Merging several MRs in one shot when any one is uncertain
