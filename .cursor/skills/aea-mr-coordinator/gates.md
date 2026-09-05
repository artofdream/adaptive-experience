# MR coordinator — merge gates

GitLab: `artof-group/adaptive-experience-architecture` (`glab`).

Run these before `glab mr merge` (immediate or auto-merge / MWPS).
**All three groups must pass.** After they pass, **must** run
`glab mr merge <n> --yes --auto-merge`. One miss → reach out; do not
merge and do not set auto-merge.

## 1. Scope

- One finding / one issue / one MR (coherence SOP).
- Title and description state **in** and **out**.
- Diff matches the description (no surprise files).
- No drive-by refactors, renames, or extra docs.
- `Closes #N` (or equivalent) when the work closes an issue.
- Not a pile of unrelated stakeholder skills **plus** UX **plus** Terraform
  in one MR.

Fail examples: mixed UX+cloud; “also fixed lint”; description says docs-only
but `edge/` or `platform/` changed.

## 2. Boundary

- No invented BG/US/FR/NFR IDs; archive xlsx untouched unless the issue is
  explicitly that (rare, **sponsor**-confirmed).
- No secrets, `.env`, vault credentials, `infra/aws/terraform.tfvars`.
- No force-push to `main` / `master`.
- Not merging `main` into itself.
- Docs-only vs code classified correctly.
- Docker-integration-before-MR
  (`.cursor/rules/docker-integration-before-mr.mdc`):
  - Platform/Postgres/Kafka impact →
    `python platform/scripts/run_integration_tests.py`
  - Edge/BFF/gateway/UI impact →
    `python edge/scripts/run_integration_tests.py`
  - Docs-only, Cursor-rule, or research-note → no Docker required
    (must be explicit in the MR).
- If Docker was skipped, that is **CI-only** — merge only if **PM-SM
  accepted CI-only for that named MR**, or the **sponsor** already
  accepted CI-only. Prefer wait. CI-only that changes production risk
  still needs the sponsor.

## 3. Validation path

- MR body has a **test plan**.
- Required GitLab CI on the MR pipeline is **green**, or still
  running (set auto-merge / MWPS; do not merge immediately). Failed
  required jobs are a fail.
- No failed **required** jobs. `markdownlint` is required (#325).
  `linkcheck` is required (#326). `ruff` is required (#327).
  `bandit` is required (#328). `python-lock` is required (#329).
- Local integration recorded when the SOP requires it (command + outcome in
  MR, chat, or CI job that is the same runner).
- CI-only: **not** sponsor by default. PM-SM may accept it for a named MR
  **or** wait when local Docker was unavailable. Prefer wait unless the
  sponsor already accepted CI-only. Production-risk CI-only → sponsor.

## Reach-out (do not merge, do not set auto-merge)

- Scope is mixed or unclear → **PM-SM**
- Validation is missing or skipped → **PM-SM**. “CI only” without
  acceptance for that named MR: PM-SM may accept or wait (prefer wait).
  CI-only **production** risk → **sponsor**
- Conflicts, rebase uncertainty, force-with-lease onto a shared branch you
  did not author. Conflicts → **do not merge** and **do not rebase**.
  Request `@aea-senior-software-engineer` (comment / assign). Do not
  invent a rebase unless SSE owns it.
- Required job failed or the pipeline crashed. **Must** request
  `@aea-senior-software-engineer` (or `@aea-devsecops-platform` for
  runner / image / compose). Comment with job URL and error. Do not sit
  on a red required job.
- Security/privacy/cloud apply (`terraform apply`) — DSO operates; this
  skill does not apply as part of merge
- Secrets, `.env`, vault credentials, or `infra/aws/terraform.tfvars` →
  **sponsor**
- Canonical scope / new FR-NFR IDs / archive workbook → **sponsor**
- Force-push to `main` / `master`
- Disagreement between MR description and diff → **PM-SM**
- This skill was not invoked and there is no create/push handoff
  (loop tick / sibling skill)

## Commands

```bash
glab mr view <n>
glab mr diff <n>
glab ci status
glab mr merge <n> --yes --auto-merge
```

`--auto-merge` is GitLab MWPS (`merge_when_pipeline_succeeds`). After
gates pass, **must** set it. Prefer MWPS while the pipeline is running.
`--yes` skips the interactive prompt only. Do not wait for a second
“please merge this named MR” prompt. An author create/push handoff is
enough to start this checklist (`.cursor/rules/mr-handoff-to-mrc.mdc`).

Never: `git push --force` to `main`, merge unless this skill was invoked,
`--auto-merge=false` to skip a running pipeline, `terraform apply`.
