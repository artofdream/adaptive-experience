# Path B Dual-Viewport UX Architecture Specification

> **Date**: 2026-08-28  
> **Stakeholder**: `@aea-ux-designer`  
> **Traceability**: Issue #272, CF-054, ADR-002, ADR-003, ADR-004, ADR-006, ADR-013, FR-001..FR-021, NFR-005, NFR-017  
> **Tags**: #aea  

---

## 1. Executive Summary & Core Principle

Following the J1–J4 journey reviews across desktop (1280px) and mobile (iPhone SE 375x667) viewports, this specification defines the canonical UX architecture for **Path B Dual-Viewport Presentation**.

### The Core Architectural Principle
> **Single Session State, Dual Adaptive Presentations.**  
> The underlying session engine (`edge/bff/aea_bff`), PostgreSQL event stream, and Shared Understanding model remain 100% unified. The client interface dynamically projects the session into one of two viewport-optimized UX topologies based on screen width and input capabilities.

```
                         ┌─────────────────────────────────────────┐
                         │   Unified Session State (PostgreSQL)    │
                         │ Shared Understanding + Cart + Selection │
                         └────────────────────┬────────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
        Desktop Viewport (≥ 1024px)                       Mobile Viewport (< 768px)
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│ 8-Tile Persistent Adaptive Workspace   │       │ 3-Stage Linear Concierge Flow          │
│ - Tiles T-01..T-08 in-place canvas     │       │ - Stage 1: Need (Intent & Search)      │
│ - Simultaneous multi-tile visibility   │       │ - Stage 2: Pick (Customize & Delivery) │
│ - Extended stepper & multi-column grid │       │ - Stage 3: Pay  (Summary & Checkout)   │
└────────────────────────────────────────┘       └────────────────────────────────────────┘
```

---

## 2. Dual-Viewport Topology Breakdown

### 2.1 Desktop Viewport Presentation (≥ 1024px)
- **Pattern**: Persistent 8-Tile Adaptive Workspace (`ADR-002`, `data-journey-mode="steps"`).
- **Layout**: 2-column or 3-column responsive grid layout with persistent side-by-side tiles (`T-01` Conversation + `T-02` Shared Understanding anchored on the left).
- **Navigation**: Multi-stage progress header displaying tiles `T-01` through `T-08`.
- **Interaction**: Tiles progressively expand and hydrate in place as session state advances. Customers can freely re-inspect previous tiles without destroying working state.

### 2.2 Mobile Viewport Presentation (< 768px / iPhone SE 375x667)
- **Pattern**: Streamlined Linear Concierge (*Need → Pick → Pay*).
- **Layout**: Single-column vertical stack with fixed bottom primary CTA bar.
- **Navigation**: Compact 3-stage progress bar (*Need*, *Pick*, *Pay*) with unified stage labels matching both desktop and mobile headers.
- **CTAs**: Exactly **one prominent primary CTA** per stage (e.g., *"Find My Bouquet"*, *"Proceed to Delivery"*, *"Confirm Order"*). Secondary actions (e.g., *Contact Florist*, *Help*) are rendered as non-blocking modal drawer overlays (`ADR-004`).

---

## 3. Mobile Stage Mapping & Unified CTA Rules

| Mobile Stage | Included Tiles | Stage Purpose | Primary CTA | Secondary Overlay |
| :--- | :--- | :--- | :--- | :--- |
| **1. Need** | `T-01` (Conversation)<br>`T-02` (Shared Understanding) | Express occasion, recipient relation, and budget preference | *"Find My Bouquet"* | `ASO` FAQ / Chat with Lily (`?`) |
| **2. Pick** | `T-03` (Recommendations)<br>`T-04` (Customization)<br>`T-05` (Delivery) | Select SKU, pick size/card message, and confirm delivery date | *"Proceed to Delivery & Checkout"* | `T-09` Contact Florist Drawer |
| **3. Pay** | `T-06` (Order Summary)<br>`T-07` (Checkout)<br>`T-08` (Tracking) | Review total charges, acknowledge terms, and submit order | *"Confirm Order & Track"* | `T-08` Live Tracking Panel |

---

## 4. Specific UX Improvements & Alignments

1. **Unified Budget Chips**:
   - Budget selection chips ($75, $100, $125, $150+) on mobile match the exact catalog price points in `T-03` curated recommendations, eliminating visual price discrepancy.
2. **Simplified Customization Panel (`T-04 / ADR-006`)**:
   - Mobile `T-04` exposes arrangement options, size chips (Standard, Deluxe, Premium), and card message input only. Advanced compositions remain explicitly out of scope per `ADR-006`.
3. **Streamlined Confirmation & Zero-PII Checkout (`T-07 / ADR-013 / NFR-017`)**:
   - Mobile `T-07` presents an instant confirmation checkbox and single-click checkout button using opaque session vault references. Zero credit card or raw address fields are rendered (`NFR-017`).
4. **Non-Blocking Support Overlays (`ADR-004`)**:
   - Automated Help (`ASO`) and `T-09` Contact Florist slide up as lightweight bottom-sheet drawers on mobile, preserving customer cart and selection context upon dismissal.

---

## 5. Accessibility & Responsive Budget Enforcement

- **WCAG 2.1 AA Compliance**:
  - Minimum touch tap target size: **44 x 44 px** on all interactive mobile buttons and budget chips.
  - Visible focus indicators: High-contrast `:focus-visible` outline rings on all form inputs and CTAs.
  - Screen Reader Announcements: `aria-live="polite"` regions for AI prompt status updates (`NFR-005`) and inline error alerts (`role="alert"`).
  - Motion Controls: Respects `prefers-reduced-motion` media query by disabling slide animations.
- **Performance Budget**:
  - Sub-100ms LCP on mobile viewports via progressive hydration of active stage components.

---

## 6. Second Brain Wikilinks & Cross-References

- [[2026-08-27-path-b-dual-viewport-ux-loop-j1-j4]] — J1–J4 Phone & Desktop Recording Review Log.
- [[CF-054-path-b-dual-viewport]] — Coherence Finding for Path B Dual-Viewport Presentation Alignment.
- [[2026-08-27-session-memory-log-crm-reminders-and-cloud-handoff]] — Previous Session Hand-off Log.
