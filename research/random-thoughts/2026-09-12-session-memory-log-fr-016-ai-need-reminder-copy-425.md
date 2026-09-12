# Session Memory Log: FR-016 AI-authored Path B Need reminder copy (#425)

> **Tags**: #aea #session-memory #fr-016 #path-b #need #adr-016 #adr-019 #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-12
> **Author**: `@aea-knowledge-guardian` with `@aea-ai-engineer` and `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-016-ai-need-reminder-copy]] · [[fr-016-path-b-need-reminder]] · [[ADR-016]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · #35 · #420 · #425

---

## 1. Why this note exists

Parent [#35](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/35) (US-016 / FR-016) stayed open after #420 / !499 shipped the in-session `#need-reminder` pull card with deterministic template copy. This session ships child [#425](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/425): AI-authored card copy on the existing LiteLLM path. It does **not** close #35. Do not reopen #420. Do not start #36.

---

## 2. Slice that shipped

- `complete_chat_json` is the shared OpenAI-compatible helper used by intent and reminder copy.
- `OpenAICompatibleReminderCopyAuthor` + `AvailableReminderCopyAuthor` take only `occasion_type`, `recipient_relation`, `days_until_event`.
- `EngagementCrmService.get_reminders` authors the soonest item when a `copy_author` is wired; fail-closes to `format_reminder_text`.
- `internal_runtime.py` constructs the reminder author from the same `AEA_AI_*` triple as intent. Load-test mock stays template-only.
- Presence gates, least-data facet, and **Shop this occasion →** are unchanged. Still pull-only.

---

## 3. Honest leftover on #35

| Still open | Why |
|---|---|
| Unsolicited outbound send | No email/SMS; FCM/APNs must not be implemented from ADR-019 |
| Workbook FR-016 Future | Do not promote IDs from this MR |

AI-generated **in-session** card copy is no longer leftover (that was #425).

---

## 4. Wikilinks

[[fr-016-ai-need-reminder-copy]] · [[fr-016-path-b-need-reminder]] · [[ADR-016]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · [[2026-09-11-session-memory-log-fr-016-path-b-need-reminder-420]]
