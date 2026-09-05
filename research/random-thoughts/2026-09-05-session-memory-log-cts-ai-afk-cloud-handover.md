# Session Memory Log: cts-ai AFK cloud handover (2026-09-05 afternoon)

> **Tags**: #aea #session-memory #handover #cts-ai #cloud-agents #second-brain
> **Captured**: 2026-09-05
> **Author**: `@aea-knowledge-guardian` with `@aea-project-manager`
> **Related**: [[2026-09-05-session-handover-cts-ai-afk-cloud-agents]] · [[2026-09-05-session-memory-log-a36-play-v8-honesty-401-402]] · [[2026-09-04-future-native-florist-operator-app-gates]]

---

## Decisions

- Sponsor: **no native florist/operator app** unless specifically requested (not this window). Operator stays `/florist` mobile-web.
- Consumer companion **v8** is already on Play Internal. Do not bump `versionCode` just to re-upload.
- MRC merged !464 (Figma node IDs) and !465 (A36 Play v8 honesty). **No open MRs** at handoff.
- `cts-ai` leaves AEA for hours. Cloud may take **#323** first, then the serialized DSO chain. **CF-056** queue row may be marked `verified` if !361 evidence still holds. Everything else in §4 of the handover stays reserved.

## Trade-offs

- Two vaults (research + private Obsidian) stay as they are: research is the shared bus; a second vault is inbox only. Do not split DATE_RE or CF queue across vaults.
- Local leftover `quality/327-blocking-ruff-baseline` had **no commits** and a dirty Ruff `--fix` tree. Restored. Cloud must not treat that checkout as WIP.

## Do not

- Sideload the A36. Claim CF-054 verified without new clips. Start #324+ in the same MR as #323. Play App Dist as if it were Play honesty.
