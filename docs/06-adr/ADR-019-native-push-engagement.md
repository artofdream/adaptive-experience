# ADR-019 — Native Push & Proactive Engagement (Decision Record Only)

Status: Accepted (decision record only — no implementation authorized)

Date: 2026-08-29

Related requirements: FR-016, FR-017 (`EngagementCrmService`, delivered in
`platform/aea_platform/crm.py` for occasion reminders / zero-PII engagement
memory — this ADR governs a new *delivery channel* for that existing
capability, not new engagement logic)

Related decisions: [ADR-017 Native Client Architecture](ADR-017-native-client-architecture.md),
[ADR-018 Mobile Session & Auth Model](ADR-018-mobile-session-auth.md)

Related roadmap: M19 — Native Mobile Companion, Android (Reference
Extension) names this ADR as groundwork; push implementation is **explicitly
not part of M19's J1–J4 parity scope**. [roadmap.md](../07-roadmap/roadmap.md)

## Context

`product-vision.md` already flags "proactive annual occasion engagement"
(FCM/APNs relays tied to `EngagementCrmService`, FR-016) as an unshipped
Future-extension vision. A native client makes push technically available
for the first time — the web client has no equivalent unsolicited-contact
channel today. Push is a **new class of risk** this repo has not governed:
unlike a web session (customer-initiated, in-tab), a push notification can
reach a customer's lock screen without them opening the app, which raises
consent and rate-limiting questions the existing FR-016/FR-017
implementation never had to answer because it only ever populated
in-session UI.

This ADR is a **decision record only**. It authorizes no FCM/APNs code. It
exists so that when push implementation is scheduled (a later milestone,
not M19), the implementer has a governed boundary to build against instead
of inventing consent rules ad hoc.

## Alternatives

1. **No governance — implement push when the milestone arrives** — defers
   the hard questions (opt-in default, quiet hours, rate limits) to
   whoever happens to implement it first, risking an ungoverned unsolicited-
   contact channel shipping by default.
2. **Push disabled entirely, permanently** — safest, but contradicts the
   already-published product-vision.md intent and would need an explicit
   vision change, not a native-mobile ADR, to walk back.
3. **Record the consent/governance model now, implementation later** — push
   stays FR-016/FR-017's existing engagement logic, relayed through
   FCM (Android) / APNs (iOS, later) as a **transport only**; the ADR fixes
   opt-in-by-default-off, quiet hours, and rate limits as non-negotiable
   before any implementation issue can be scoped.

## Decision

Adopt **Option 3**. When native push implementation is scheduled (a later
milestone, explicitly not M19), it must satisfy all of the following before
any customer receives a push notification:

- **Opt-in, default off.** No push notification is sent to a customer who
  has not explicitly enabled it in the native app. Installing the app or
  completing an order does not imply consent.
- **Transport only, no new engagement logic.** FCM/APNs relay the *same*
  occasion-reminder content `EngagementCrmService` (FR-016) already
  produces. This ADR does not authorize new engagement content or
  targeting logic beyond what FR-016/FR-017 already define.
- **Zero-PII payload.** Push payloads carry no raw customer data — same
  reference-based pattern as ADR-013 and ADR-018. The notification body may
  be human-readable ("Time to send birthday flowers?") but carries no
  session reference, address, or payment detail in the payload itself.
- **Rate limits and quiet hours.** A customer cannot receive more than a
  small, explicit cap of engagement pushes in a rolling window, and no push
  is sent during locally-configured quiet hours. Exact limits are an
  implementation-time decision, not fixed by this ADR — but the *category*
  of constraint is fixed here.
- **Revocable at any time**, without needing to contact support or delete
  the app — an in-app toggle is required, not just OS-level notification
  permission.

## Rationale

Option 3 is the only alternative that lets the already-published
product-vision.md line proceed without either silently shipping an
ungoverned contact channel (Option 1) or contradicting published vision
without an explicit vision-level decision (Option 2). Fixing consent/rate-
limit *categories* now, while no code exists yet, costs nothing and removes
a governance gap before it becomes technical debt.

## Consequences

- No FCM/APNs code is authorized by this ADR. The M19 CI/Firebase issue may
  wire Firebase project *infrastructure* generally (Crashlytics, App
  Distribution) but must not enable push sending under this ADR's cover.
- A future push-implementation issue must cite this ADR and demonstrate
  opt-in default-off, zero-PII payload, rate limits, and an in-app revoke
  control before it can be considered complete — this is a review
  checklist this ADR creates, not new tooling.
- `EngagementCrmService` (FR-016/FR-017) itself is unchanged — this ADR
  governs a new delivery channel for its existing output, not its logic.
- If push is never implemented, this ADR still stands as the governance
  record for *if* it ever is — it does not expire or require re-decision
  absent a change to the constraints themselves.
