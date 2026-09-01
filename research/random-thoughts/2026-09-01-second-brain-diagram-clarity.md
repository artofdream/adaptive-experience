# Second Brain: add diagrams where text-only hides the path

> **Tags**: #aea #second-brain #knowledge
> **Captured**: 2026-09-01
> **Owner**: `@aea-knowledge-guardian`
> **Status**: operating principle + queued review; not a mass rewrite this session

Sponsor side note 2026-09-01 after the #351 visual runbook: Second Brain notes
that are **only prose** should be reviewed and given diagrams where that
clarifies the path. Canvas is session UI. Durable diagrams live in git as
mermaid (or equivalent) under `research/random-thoughts/`.

Worked example: [[2026-09-01-android-upload-keystore-gitlab-file-var]]
(broken File-textarea path vs base64 decode). Session log:
[[2026-09-01-session-memory-log-android-upload-keystore-file-var]].

## Principle

When a note tells a human or agent to **do a sequence** (GitLab Variables,
Firebase, Play Console, CI job play) or has a **failure vs fix fork**, include
a mermaid flowchart (or two: broken vs correct). Names only for secrets.
Do not paste keys, JSON, SHA-1, or keystore bytes into diagrams or prose.

Architecture essays, ADR pointers, and one-line status logs can stay
text-first. Do not decorate every paragraph.

## Queued review (later, not this MR)

- Prefer **operator / sponsor / CI** notes before long strategy papers.
- One note (or one tight cluster) per MR. Do not batch-rewrite the vault.
- Cursor canvases are not shared memory. After a visual explanation in chat,
  extract mermaid + steps into `research/random-thoughts/` the same day.
- Do not invent BG/US/FR/NFR IDs. Do not promote this principle into `docs/`
  unless asked.

## Do not claim

- That every existing vault file has been reviewed.
- That mermaid is required on session-memory logs with no procedure.
