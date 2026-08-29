# ADR-017 — Native Client Architecture

Status: Accepted

Date: 2026-08-29

Related requirements: FR-001, FR-003, FR-007, FR-008, FR-009; NFR-005,
NFR-009, NFR-017 (existing coverage — this ADR adds a client surface, not
new requirements)

Related decisions: [ADR-007 Initial Deployment Topology](ADR-007-initial-deployment-topology.md),
[ADR-008 Contract-First Messaging](ADR-008-contract-first-messaging.md),
[ADR-013 Confirmation-Driven Experience](ADR-013-confirmation-driven-experience.md)

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md),
[path-b-dual-viewport-specification.md](../05-ux-design-guide/path-b-dual-viewport-specification.md)

Related roadmap: M19 — Native Mobile Companion, Android (Reference
Extension), [roadmap.md](../07-roadmap/roadmap.md)

## Context

`docs/01-product-vision/product-vision.md` names a native Android/iOS
companion as a Future-extension vision ("Android Kotlin/Jetpack Compose
leading to iOS SwiftUI, consuming identical BFF endpoints without backend
rewrites") but that single line was never turned into an architecture
decision. The sponsor directed on 2026-08-29 that this pathway proceeds,
Android first, gradual. Without this ADR, an implementer has no recorded
boundary to fit — the risk is a native client re-implementing business
logic, calling a different entry point than the Gateway, or drifting from
the contract the web client already honors.

## Alternatives

1. **New native-only backend** — a dedicated API surface for mobile,
   optimized for native payload shapes. Fastest to iterate in isolation;
   duplicates business logic and inventory/fail-closed checks the web
   client already implements correctly; breaks the "single session state"
   principle the dual-viewport spec already established for desktop vs.
   mobile web.
2. **Native client bypasses the Gateway, talks to BFF or platform
   directly** — lower latency; violates ADR-007 (Gateway is the sole
   public entry) and would require opening a second public port.
3. **Native client as a third presentation of one session, consuming the
   existing Gateway → BFF → platform chain unchanged** — no new backend, no
   new public entry point, generates its API client from the same
   contract-first schema (ADR-008) the web client's BFF already publishes.
4. **WebView/Trusted Web Activity wrapper around the existing responsive
   mobile client** — fastest possible ship, zero new client code; explicitly
   an interim bridge, not the vision's stated target architecture, and
   risks becoming permanent by default if adopted without a sunset plan.

## Decision

Adopt **Option 3**: the native Android (later iOS) client is a **third
presentation of the same unified session**, alongside the existing desktop
and mobile-web presentations. It authenticates and communicates through the
**same Gateway (ADR-007 sole public entry) → BFF → platform orchestration**
chain the web client already uses. Its API client is **generated from the
BFF's existing OpenAPI contract** (ADR-008) — no hand-maintained native
models, no parallel schema.

The native client **shall not** implement its own business logic,
inventory/fail-closed checks, pricing, or authoritative state. All of that
stays in platform orchestration and domain services, per the existing
system boundary (also consistent with ADR-016's agent/service boundary
principle: the client presents and collects intent, it does not decide).

**Option 4 (WebView/TWA)** is not rejected outright — it remains available
as a documented fallback if Android account/store activation timelines
force an interim step — but it is **not** the default path this ADR
commits to, and any use of it needs its own explicit decision note with a
sunset plan, not a silent substitution for Option 3.

## Rationale

Option 3 is the only alternative that matches the vision statement's own
words ("consuming identical BFF endpoints without backend rewrites") and
fits every existing boundary ADR without modification: ADR-007 (Gateway
sole entry) is unchanged, ADR-008 (contract-first) extends naturally to a
second generated client, and ADR-013 (confirmation-driven, destination
reference not raw address) carries over because the *same* BFF enforces it
regardless of which client called it. Option 1 and Option 2 both require
either duplicating enforced business rules or opening a new public surface,
either of which would need its own extraction ADR under this repo's
modular-monolith constraint — not something this ADR authorizes.

## Consequences

- No new AWS service, ECS task, or public port is introduced by the native
  client itself — it is a new *caller* of infrastructure that already
  exists and is already deployed (`aea-pilot`).
- The native client's build depends on the BFF's OpenAPI contract staying
  current and versioned; a contract change is a breaking change for both
  web and native clients simultaneously, not a native-only concern.
- Session/auth storage (Keystore-backed reference, not credentials) is
  specified separately in ADR-018, not duplicated here.
- Push notifications and any native-only proactive engagement are
  explicitly out of scope for this ADR — see ADR-019 (decision record
  only, no implementation authorized yet).
- iOS is sequenced after Android's first phase validates this
  architecture in production-adjacent use; this ADR applies to both
  platforms equally once iOS work starts — no separate iOS architecture
  ADR is anticipated unless evidence surfaces a real divergence.
- This ADR does not authorize any specific implementation — see the M19
  milestone issues for phased delivery (Phase 0 scaffold, CI, UX spec).
