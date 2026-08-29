# Native Mobile UX Specification (Android, M19 Phase 0/1)

> **Date**: 2026-08-29
> **Stakeholder**: `@aea-ux-designer`
> **Traceability**: [ADR-017 Native Client Architecture](../06-adr/ADR-017-native-client-architecture.md),
> [ADR-018 Mobile Session & Auth Model](../06-adr/ADR-018-mobile-session-auth.md),
> M19 (roadmap.md), CF-054, FR-001, FR-003, FR-007, FR-008, FR-009,
> NFR-005, NFR-009, NFR-017, ADR-013
> **Prototype**: [Lily's Florist — Native Mobile (J1–J4)](https://www.figma.com/design/BcoNF0vHDV8Pb3efDT5eBf)
> — 10 frames, wired click-through prototype. This document formalizes that
> concept exploration into a canonical screen map; the Figma file itself
> remains a concept prototype, not a production component library.
> **Tags**: #aea

---

## 1. Core principle — carried over, not reinvented

This spec does **not** invent a new mobile flow. It applies the same
target architecture [path-b-dual-viewport-specification.md](path-b-dual-viewport-specification.md)
already defined for mobile *web* — **3-Stage Linear Concierge (Need → Pick
→ Pay)** — translated into native Android idioms, on the **same unified
session** ADR-017 requires. It deliberately does **not** copy the
as-shipped 7-step desktop-workspace-on-a-phone pattern CF-054 found broken
(J1–J4 clips, 2026-08-27) — that was the mistake this spec exists to avoid
repeating on native.

```
Unified Session State (PostgreSQL, via Gateway -> BFF -> platform)
            |
   +--------+--------+--------------------+
   |                 |                    |
Desktop Web      Mobile Web          Android Native
8-Tile            3-Stage             3-Stage Need->Pick->Pay,
Workspace         Need->Pick->Pay     Compose UI, native idioms
(shipped)         (spec'd, CF-054:    (this spec — Figma
                   not yet matching    concept only, no code)
                   on live phone)
```

## 2. Native-idiom translation table

Same content, same rules, different platform components:

| Web mobile pattern | Native Android equivalent | Why |
|---|---|---|
| CSS 3-segment progress bar (Need/Pick/Pay) | Native segmented control (pill group) | Matches platform look; same 3 labels, same order |
| CSS modal drawer (ASO, Contact Florist) | Native bottom sheet | Standard Android pattern for non-blocking overlays; preserves cart/selection context on dismiss (same rule as the web spec) |
| HTML date/time picker | Native date/time chips or platform picker | Faster tap-through than a web date input |
| Web zero-PII checkout form | Native confirmation screen + platform payment sheet reference | Same zero-PII rule (NFR-017) — no PAN fields either way |
| Sticky bottom CTA bar (CSS) | Native bottom app bar with one primary button | Identical rule: exactly one prominent primary CTA per stage (unchanged from the web spec) |

## 3. Screen map (Android, Phase 0 = J1 only; full map for Phase 1)

| # | Screen | Maps to tiles | Stage | Journey evidence |
|---|---|---|---|---|
| 1 | Need · Conversation | T-01, T-02 | Need | J1 Urgent Sam — same-day roses, "I need flowers for Mom's birthday, same day" |
| 2 | Pick · Recommendations | T-03 | Pick | J1 (Available/Unavailable badge, NFR-009); J3 Loyal Alex (same-session reorder badge, not faked) |
| 3 | Pick · Customize | T-04 | Pick | J2 Planner Sarah — card message + satin ribbon; resolves the "Update vs Continue" dual-CTA finding with one CTA, autosave |
| 4 | Pick · Delivery | T-05 | Pick | Destination **reference** only, no street address field (ADR-013) |
| 5 | Pay · Order Summary | T-06 | Pay | Itemized charges |
| 6 | Pay · Checkout | T-07 | Pay | Zero-PII session payment reference, single confirmation control (NFR-017) |
| 7 | Pay · Tracking (unlocked) | T-08 | Pay | Post-checkout only |
| 8 | Track & Contact Florist (gated) | T-08, T-09 | Pay (pre-checkout) | J4 Tracker Chris — honest locked state, **not** a bug: "unlocks after you finish earlier stages" |
| 9 | ASO bottom sheet (cross-cutting overlay) | — | Any | J4 — "Is this safe for cats?", disclaimer "this is not a person" (FR-009 fail-closed), dismiss preserves cart |

**Phase 0 scope** (M19 Phase 0 scaffold issue): screens 1–2 only, J1 happy
path. **Phase 1** (closed testing, blocked on Play account): full 9-screen
map, J1–J4 parity.

## 4. Rules carried over unchanged from the web mobile spec

- Exactly **one** prominent primary CTA per screen — no competing actions.
- Budget/filter chips must be **labeled honestly** as guides or filters —
  never silently ambiguous (the CF-054 finding's "chips vs. filters" issue
  applies equally to native chip components).
- Fail-closed inventory: `Unavailable` badge disables Select; no soft
  fallback that implies availability.
- ASO carries the "this is not a person" disclaimer on **every** screen it
  appears on, not just first use.
- Track/Contact Florist stay gated pre-checkout — this spec does not
  unlock them early. If that changes, it needs its own product decision
  from `@aea-product-owner`, not a UX-spec side effect.
- Destination is a **reference**, never a raw address field (ADR-013).

## 5. Accessibility (Android-specific, replaces WCAG/CSS references)

- Minimum touch target: 48x48dp (Android's own guideline, slightly larger
  than the web spec's 44x44px — use the stricter native number).
- `contentDescription` on every icon-only control (parity with the web
  spec's `aria-live` / `role="alert"` requirements, expressed via Android's
  accessibility APIs — TalkBack, not VoiceOver, for this Android-first
  phase).
- Respect system-level "Remove animations" setting (Android's equivalent of
  `prefers-reduced-motion`).
- Dynamic Type / font-scale support — Compose's default text scaling honors
  system settings; do not hardcode `sp` values that ignore user font-size
  preference.

## 6. What this spec does NOT cover

- iOS (sequenced after Android Phase 0/1 validates — will need its own
  idiom-translation pass when that phase starts, likely largely reusing
  this document's content/rules table with SwiftUI-specific component
  substitutions).
- Push notification UI (governed separately by ADR-019, decision-record
  only — no push screens exist in this spec).
- Any screen beyond the 9 mapped above — this spec is J1–J4 parity, not a
  general native design system.

## 7. Second Brain cross-references

- [[2026-08-29-native-mobile-companion-system-docs-and-toolkit]] — full
  team response (vision, implementation options, challenges, cost estimate,
  HLD/LLD) this spec was scoped from.
- [[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] — source J1–J4 clip
  evidence and the CF-054 finding this spec deliberately does not repeat.
