# Claude ↔ Obsidian loop

Working knowledge loop for this docs-only repository: capture in Obsidian,
synthesize with Claude (Cursor or Claude Code), promote into git under clear
boundaries.

## Roles

| Tool | Role |
|------|------|
| **Obsidian** | Capture, link, and refine working notes (inbox, daily notes, exploratory graphs). |
| **Claude** | Synthesize notes, draft or edit `research/` and `docs/`, check coherence, prepare tight git changes. |
| **Git (`docs/`, `implementations/`)** | Canonical, reviewable product architecture — CI-guarded source of truth for published claims. |

This is a **knowledge workflow**, not a paid sync product. Cursor's `/loop`
skill can optionally schedule a recurring promote/review pass; it is not
required for day-to-day use.

## Sync boundaries

```text
Obsidian (local working surface)
    │  capture / link / tag
    ▼
research/          ← shared scratch that may be committed
    │  promote when stable
    ▼
docs/ + implementations/   ← canonical (MR + coherence SOP)
    ▲
archive/ xlsx      ← requirements count source of truth (change rarely)
```

| Layer | Path | In git? | Purpose |
|-------|------|---------|---------|
| Vault config | `.obsidian/`, `.trash/` | **No** (gitignored) | Personal Obsidian workspace. |
| Inbox | `research/inbox/` | Yes (optional) | Fleeting notes ready for Claude to triage. |
| Research | `research/**` (except inbox if you prefer private) | Yes | Exploratory notes not yet canonical. |
| Canonical docs | `docs/`, `implementations/` | Yes | Product architecture; edit via focused MRs. |
| Requirements SoT | `archive/*.xlsx` | Yes | Coherence guard baseline — do not invent IDs here. |

**Do not** treat Obsidian as a second publisher of FR/BG/US IDs. Canonical
counts and mappings stay in `archive/` + `docs/`; the loop only *feeds*
candidates into that model.

## Recommended vault setup

You already have Obsidian vaults under `C:\data\vaults\` (e.g. `cts`). Either:

1. **Repo as vault (preferred for this project)** — In Obsidian: Open folder as
   vault → `C:\projects\code\adaptive-experience`. Keep `.obsidian/` local
   (gitignored). Use `research/inbox/` for capture.
2. **Sibling vault** — Create `C:\data\vaults\aea` for private notes only, and
   keep a short index note that points at the git repo paths you are promoting
   into. Do not duplicate whole `docs/` trees into the private vault.

Avoid Obsidian Sync / paid bridges unless you already use them; plain markdown
on disk is enough.

## Day-to-day loop

### 1. Capture (Obsidian)

- New idea → note in `research/inbox/` using
  [`templates/inbox-note.md`](templates/inbox-note.md).
- Prefer wikilinks (`[[note]]`) and tags (`#aea`, `#promote`, `#risk`) over
  long unstructured dumps.
- Keep FR/US/BG IDs only when citing existing docs; mark unverified IDs clearly.

### 2. Triage (Claude)

In Cursor or Claude Code, point at inbox notes and ask to:

1. Cluster related notes.
2. Separate **fact** (already in docs) vs **proposal** vs **open question**.
3. Write a promotion candidate under `research/` (or update an existing note)
   using [`templates/promotion-candidate.md`](templates/promotion-candidate.md).
4. List exact target paths under `docs/` / `implementations/` if promotion is
   warranted — do not edit canonical docs yet unless asked.

### 3. Promote (Claude + git)

When a candidate is ready:

1. Confirm it does not contradict `archive/` counts or existing IDs.
2. Apply a **tight** edit to the owning canonical file(s).
3. If the change is a coherence inconsistency/gap, follow
   `.cursor/rules/coherence-findings-sop.mdc` (one issue → one branch → one MR).
4. Run `python scripts/check_coherence.py` (or CI) when requirements/IDs move.
5. Leave inbox notes marked `#promoted` or move them to
   `research/archive/` (optional local convention).

### 4. Reflect (Obsidian)

- Link the vault note to the git path that absorbed it (plain relative path is
  enough, e.g. `docs/06-adr/ADR-004-customer-support-overlay.md`).
- Close or retag open questions.

## Coherence finding loop

Use [`coherence-findings-loop.md`](coherence-findings-loop.md) when an
assessment produces multiple findings. It adds a durable, ordered queue to this
knowledge loop while preserving the one-finding-per-MR boundary.

New assessments first run as a separate intake pass: save the assessment,
deduplicate findings by stable `CF-NNN` ID, reopen regressions, and reprioritize
unstarted work. A remediation iteration then processes only the first queued or
regressed finding: reproduce it against updated `main`, record evidence, hand
confirmed work to the coherence findings SOP, verify the merged result on
`main`, then stop. This prevents later MRs from silently undoing earlier
remediation.

## Post-merge documentation verification

After an MR that touches requirements, mappings, topics, or CI lands on
`main`, run this short path (not a separate tooling system):

1. `git checkout main && git pull`
2. `python scripts/check_coherence.py` (or `sh scripts/check-coherence.sh`)
3. Confirm the **main** pipeline `coherence-guard` job is green
4. Spot-check linked paths changed in the MR (README area links, topic
   contracts, or the finding's evidence paths)

### MR checklist (docs / coherence)

- [ ] `Closes #N` links the finding issue
- [ ] Scope is one finding only
- [ ] Local coherence guard run when IDs, chains, scope, or CSV/workbook move
- [ ] After merge: verification steps 1–3 above on updated `main`

## Optional Cursor `/loop`

For a recurring triage reminder in an Agents session (not a cloud cron):

```text
/loop 1d Triage research/inbox/: cluster notes, draft or update promotion
candidates under research/, and list any canonical docs/ edits that need a
dedicated branch. Do not open GitLab issues/MRs unless following the coherence
findings SOP for a confirmed inconsistency/gap. Do not invent requirement IDs.
```

Stop the loop when asked. Prefer human-triggered triage if inbox volume is low.

For coherence remediation, use the narrower prompt in
[`coherence-findings-loop.md`](coherence-findings-loop.md); do not combine it
with inbox triage in the same iteration.

## Claude project hints

- Repo root [`CLAUDE.md`](../CLAUDE.md) summarizes boundaries for Claude Code.
- Cursor rule: `.cursor/rules/claude-obsidian-loop.mdc`.
- Prefer editing markdown in place; match existing tone (short sections, tables
  for inventories, no drive-by refactors).

## Out of scope

- Automatic two-way sync daemons or paid Obsidian↔Git bridges.
- Committing `.obsidian/` workspace state.
- Batching unrelated coherence fixes (see coherence SOP).
- Inventing BG/US/FR/NFR IDs outside the archive-backed model.
