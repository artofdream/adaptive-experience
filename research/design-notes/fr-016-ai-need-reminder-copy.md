# Design note — FR-016 AI-authored Need reminder copy (#425)

status: implemented (thin path)
for_issues: "#425 (child of #35 / FR-016 Engagement and CRM)"
affects: "T-01 `#need-reminder` card copy; same `reminders` facet and presence gates as #420"
date: 2026-09-12

## Decision

When Path B LiteLLM is configured (`AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`,
`AEA_AI_MODEL` together), the soonest in-session `#need-reminder` line may
be AI-authored from categorical fields only: `occasion_type`,
`recipient_relation`, `days_until_event`.

The author reuses the existing OpenAI-compatible chat-completions helper
(`complete_chat_json`) — the same stack as `OpenAICompatibleIntentInterpreter`.
No second provider, no cron, no email/SMS, no FCM/APNs (ADR-019 stays a
decision record).

Timeout, transport error, invalid JSON, PII-like output, or overlong copy
fail closed to `format_reminder_text` (the #420 template). The card still
renders. Presence gates are unchanged: fresh Need, 30-day lookahead,
least-data facet.

Parent #35 stays open. Outbound **outbox dry-run** is #428. This slice does
**not** close a live outbound channel.

## Not in this slice

Unsolicited outbound send, native push, #36 analytics expansion, or
workbook promotion of FR-016 from Future.

## Prove

1. With a healthy chat-completions stub, `get_reminders` / workspace
   `reminders.items[0].reminder_text` is the model line.
2. With timeout or invalid output, the same item is the deterministic
   template and the card still has copy.
3. No SMTP / FCM / APNs / cron send path is introduced.
4. Parent #35 remains open; MR may `Closes #425` only.
