# Session Memory Log: FR-016 Path B Need-phase occasion reminder (#420)

> **Tags**: #aea #session-memory #fr-016 #path-b #need #adr-019 #adr-020 #nfr-017 #second-brain
> **Captured**: 2026-09-11
> **Author**: `@aea-knowledge-guardian` with `@aea-senior-software-engineer`
> **Repository**: `artof-group/adaptive-experience-architecture`
> **Related**: [[fr-016-path-b-need-reminder]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · #35 · #254 · #420

---

## 1. Why this note exists

Parent [#35](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/35) (US-016 / FR-016) stayed open after #254 / !297 shipped thin zero-PII `EngagementCrmService` and the workspace `reminders` facet. Path B Need did not render that facet. Full FR-016 is AI-generated **outbound** reminders. Native push stays ADR-019 decision-record only.

This session ships child [#420](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/420): a Need-phase pull card on `/`. It does **not** close #35. Do not start #36.

---

## 2. Slice that shipped

- Existing facet `reminders.items` (least-data: `occasion_type`, `days_until_event`, `reminder_text`, `recipient_relation`).
- T-01 `#need-reminder` shows the soonest `reminder_text` only when Need is fresh (no customer messages, no occasion).
- Tap **Shop this occasion →** posts existing `POST /api/v1/conversation/messages` from categorical occasion + relation.
- Walker `walk_returning_shopper.py --payment` classifies `#need-reminder` after `__Host-aea_recall` replay.

---

## 3. Honest leftover on #35

| Still open | Why |
|---|---|
| AI-generated reminder copy | Current text is a deterministic template in `get_reminders` |
| Unsolicited outbound send | No email/SMS; FCM/APNs must not be implemented from ADR-019 |
| Workbook FR-016 Future | Do not promote IDs from this MR |

Empty occasion memory or dates outside the 30-day lookahead hide the card. That is current product.

---

## 4. Wikilinks

[[fr-016-path-b-need-reminder]] · [[ADR-019]] · [[ADR-020]] · [[FR-016]] · [[2026-08-27-session-memory-log-crm-reminders-and-cloud-handoff]]
