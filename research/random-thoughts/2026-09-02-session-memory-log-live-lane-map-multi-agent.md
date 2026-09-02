# Session memory — live multi-agent lane map

> **Captured**: 2026-09-02
> **Owner**: `@aea-project-manager` with `@aea-knowledge-guardian`
> **Tags**: #aea #second-brain #handoff #lanes #mrc
> **Companion**: [[2026-09-02-session-memory-log-florist-queue-rog-handoff]] · [[2026-09-02-session-handover-cloud-agents-local-cts-ai]]

Inspected live at ~21:25Z; tree refreshed to `5878529` before this commit (`!410` / `#387` and a Docker WSL vault note now on `main`). Primary tree `C:\projects\code\adaptive-experience` was **dirty and behind `origin/main`**. Do not checkout or rebase there. New docs work uses a sibling worktree from `origin/main`. Never stage mipmap PNGs (LFS pointer collisions).

`/florist` and customer `/` stay in **separate browsers**. Samsung A36 is sponsor daily phone only.

## Who owns which lane

| Actor | Owns | Do not |
|---|---|---|
| Florist operator ([Florist operator efficiency](8edc7ad8-8513-4904-95e9-dcfe28c465f9)) | `#395` florist.js/html **Today's arrangements to prepare**; note stacked florist MRs | companion Kotlin, ADB, `#381`, `#382` |
| Grok-bot / grob-ai | `#381` companion T-09 + real T-05; ROG `ASUS_I001DC` serial `K9AIKN07B088C89` | florist.js / BFF list; A36; share ADB |
| Companion split authors | `#387` !410 **merged**; remaining `#388` !414, `#389` !408, `#390` !419 | bundled !416 unless SSE closes the red job **and** remaining splits are closed |
| Cloud SSE / DSO | CI, compose, `deploy-ecs` on `main`, Path B `https://aea.artof.link/` | ADB; florist operator slices already in `#395` |
| MRC (`@aea-mr-coordinator`) | `glab mr merge --yes --auto-merge` after gates | rebase; invent product; merge without create/push handoff |
| This PM / knowledge lane | `#396` vault + DATE_RE brief; blocked reach-out; status notes | florist.js; companion code; merge; `#381` ADB |

## In flight (GitLab, not chat)

**Florist stacked slices — already on `main` (do not reopen):** !409 `#376`, !412 `#378`, !415 `#379`, !417 `#380` remove Claim/Resolve. Docs !421 merged. Live `/florist` still needed Path B `deploy-ecs` after !417.

**Florist next:** `#395` issue open, **no MR yet** — florist operator owns it. `#393` / `#392` / `#391` look like duplicates of facts already shipped in !409; do not start parallel florist.js MRs.

**Companion (open):**

| MR | Issue | Pipeline at inspect | Note |
|---|---|---|---|
| !410 | `#387` | **merged** `ec265d3` | under-floor band filter on `main` |
| !414 | `#388` | required **success** `2814585693` at inspect; authors must retarget after !410 | prefer this split |
| !408 | `#389` | required **success** `2814585797` | prefer this split |
| !419 | `#390` | required **success** `2814585994` | docs Play honesty; auto-merge was canceled 21:21Z |
| !416 | `#387`+`#388`+`#389` bundle | required **failed** `2814545442` | `android-build-debug` https://gitlab.com/artof-group/adaptive-experience-architecture/-/jobs/16267776138 — SSE reach-out posted |

**Parked / do not start:** `#382` destination handle (PO). Persist Claim (removed in !417, not a write path). `#381` stays grok-bot. M12 CRM `#35`/`#36`. Shop CSS restyle.

**Main CI:** pipeline `2814723176` on `bd473b8` was **running** (verify green; integration + `deploy-ecs` created). Cloud runners own it.

## Do not touch

- Primary working tree (untracked Android build artifacts, activity-report drafts, LFS mipmaps).
- Grok-bot ADB / ROG / `#381`.
- Florist operator `#395` / `edge/gateway/ui/assets/florist.js`.
- Shop customer CSS / Adaptive Workspace restyle.
- CRM, street/PII, persist Claim.

## How to hand off

1. **Author create/push:** non-resolvable note `@aea-mr-coordinator` with create vs push + HEAD SHA (`.cursor/rules/mr-handoff-to-mrc.mdc`). Reply on the existing thread for later SHAs.
2. **MRC:** gates then `glab mr merge <n> --yes --auto-merge`. Authors and PM do not merge.
3. **Red required job:** comment the owner with job URL (`.cursor/rules/blocked-reach-out.mdc`). Compile/Gradle/tests → `@aea-senior-software-engineer`. Runner/image/compose → `@aea-devsecops-platform`. Do not rebase. Do not invent a product fix.
4. **Worktree:** `git worktree add -b <branch> <sibling-path> origin/main`. Do not steal a dirty primary checkout.

## Local worktrees (do not reuse blindly)

Many sibling trees are **stale feature leftovers** (`feat/360-*`, `ci/320-*`, `docs/florist-rog-handoff`, …). Treat them as occupied or abandoned — start a **new** tree from updated `origin/main`. This note was written in `C:\projects\code\adaptive-experience-coord-lanes` on `docs/396-live-lane-map`.

Older cloud-offline playbook: [[2026-09-02-session-handover-cloud-agents-local-cts-ai]]. cts-ai is back; that note’s “workstation offline” section is historical. ROG + florist split: [[2026-09-02-session-memory-log-florist-queue-rog-handoff]].
