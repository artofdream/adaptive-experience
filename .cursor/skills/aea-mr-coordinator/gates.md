# MR coordinator — merge gates

GitLab: `artof-group/adaptive-experience-architecture` (`glab`).

Run these before `glab mr merge` (immediate or auto-merge / MWPS).
**All three groups must pass.** One miss → reach out; do not merge and
do not set auto-merge.

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
  explicitly that (rare, human-confirmed).
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
- If Docker was skipped, that is **CI-only** — merge only if the **user
  already accepted** CI-only in this session.

## 3. Validation path

- MR body has a **test plan**.
- Required GitLab CI on the MR pipeline is **green**, or still
  running (set auto-merge / MWPS; do not merge immediately). Failed
  required jobs are a fail.
- No failed **required** jobs. Advisory `markdownlint` / `linkcheck`
  `allow_failure: true` are not blockers unless the user treats them as such.
- Local integration recorded when the SOP requires it (command + outcome in
  MR, chat, or CI job that is the same runner).
- User already accepted CI-only **only** when local Docker was unavailable
  and they said so.

## Reach-out (do not merge, do not set auto-merge)

- Scope is mixed or unclear
- Validation is missing, skipped, or “CI only” without user acceptance
- Conflicts, rebase uncertainty, force-with-lease onto a shared branch you
  did not author
- Security/privacy/cloud apply (`terraform apply`)
- Secrets, `.env`, vault credentials, or `infra/aws/terraform.tfvars`
- Force-push to `main` / `master`
- Disagreement between MR description and diff
- User has not been the one who asked for this merge in-session **unless**
  they invoked `@aea-mr-coordinator` to process a named MR

## Commands

```bash
glab mr view <n>
glab mr diff <n>
glab ci status
glab mr merge <n> --yes --auto-merge
```

`--auto-merge` is GitLab MWPS (`merge_when_pipeline_succeeds`). Prefer it
over merging immediately while the pipeline is running. `--yes` skips the
interactive prompt only.

Never: `git push --force` to `main`, `glab mr merge` on an unnamed MR,
`--auto-merge=false` to skip a running pipeline, `terraform apply`.
