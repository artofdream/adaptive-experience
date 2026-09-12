# Design note — FR-016 Path B Need-phase occasion reminder (#420)

status: implemented (thin path)
for_issues: "#420 (child of #35 / FR-016 Engagement and CRM)"
affects: "T-01 Need affordance; workspace `reminders` facet unchanged"
date: 2026-09-11

## Decision

When a returning browser already has zero-PII occasion memory
(`crm.customer_occasion_memory` keyed by the session recall source hash)
and `get_reminders` returns an item inside the 30-day lookahead, Path B
Need (T-01) shows a card — the deterministic `reminder_text` plus
**Shop this occasion →** — only when Need is still fresh: no customer
messages and no occasion.

Tap posts the existing conversation command using categorical
`occasion_type` + `recipient_relation` only. Shared Understanding updates
as it would from a typed Need message. The card then hides.

Not AI-generated outbound send. Not email/SMS. Not native push (ADR-019).
Not FR-017 engagement analytics (#36). Parent #35 stays open.

## Follow-up

AI-authored in-session card copy is #425 (`fr-016-ai-need-reminder-copy.md`).
Unsolicited outbound send remains leftover on #35.

## Not in this slice

Unsolicited push (FCM/APNs), staff live chat, operator ticketing, or
workbook promotion of FR-016 from Future.

## Prove

1. Accept an order in this browser with occasion + delivery date
   (session payment reference). Capture writes month/day from that date.
2. Open a new experience session that still presents `__Host-aea_recall`
   (do not wipe the recall cookie).
3. Need shows `#need-reminder` before any chat when the anniversary is
   inside the 30-day lookahead. Empty memory: card hidden.
4. Tap **Shop this occasion →** → conversation carries the categorical
   occasion; Shared Understanding updates.
5. Starting Need (typed message or occasion) hides the card.

Walker: `python scripts/walk_returning_shopper.py --payment`.
