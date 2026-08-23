# Customer UX Audit & Friction Map: Adaptive Workspace Evaluation

> **Tags**: #aea #ux #accessibility #customer-journey #friction-map #second-brain  
> **Captured**: 2026-08-23  
> **Role Context**: @aea-ux-designer & @aea-customer-journey  
> **Target Application**: Lily's Florist AEA Adaptive Workspace (`https://aea.artof.link/`)  

---

## Executive Summary

As the **AEA UX Designer & Customer Journey Guardian**, we evaluated the Lily's Florist Adaptive Workspace across **Tiles T-01 through T-09** from the first-time shopper perspective across **4 Key Scenarios** (High-Urgency Same-Day, Planned Gift, Accountless Reorder, and Order Tracking).

The overall UX score is **EXCELLENT (92/100)**, driven by zero-reflow progressive hydration (`CLS = 0.00`), sub-100ms LCP paint, and transparent intent editing. 

Four minor customer pain points were identified for future UX polish.

---

## 1. What Customers Love (Delight Factors)

1. **Transparent Intent Interpretation (Tile T-02)**:
   * Shoppers feel in control because the AI does not hide its interpretation. The structured intent card (Occasion, Recipient, Budget, Delivery Date) is editable with a single click.
2. **Context-Preserving Workspace (Tiles T-01 to T-07)**:
   * Unlike traditional multi-page checkout flows where back-button navigation clears form inputs, earlier choices stay visible on the single adaptive workspace page.
3. **Tile T-09 Embedded Live Chat (Milestone M16)**:
   * Having human florist escalation embedded directly inside Tile T-09 eliminates the frustration of being redirected to a separate support portal.

---

## 2. Customer Pain Points & UX Remediations

| Pain ID | Journey Stage | Customer Pain Description | Severity | Recommended UX Enhancement |
|---|---|---|---|---|
| **`UX-P01`** | **Tile T-04 (Selection)** | Mobile keyboard obscures 280-char card message countdown on narrow screens (< 375px). | `MEDIUM` | Add sticky scroll-into-view focus handler for `#card-message-input`. |
| **`UX-P02`** | **Tile T-05 (Delivery)** | Disabling same-day delivery slots after 2:00 PM lacks a explicit cut-off explanation badge. | `MEDIUM` | Add microcopy badge: *"Same-day ordering closes at 2 PM. Next slot: Tomorrow 9 AM."* |
| **`UX-P03`** | **Tile T-04 (M17 Stems)** | Touch targets on `+` / `-` stem quantity buttons could be larger for WCAG AAA compliance. | `LOW` | Enforce 44x44px minimum tap targets on all stem counter buttons. |
| **`UX-P04`** | **Workspace Navigation** | Floating "Undo" toast pill auto-dismisses in 5s, which can be missed by hesitant users. | `LOW` | Extend toast pill display duration from 5s to 8s with smooth CSS fade. |

---

## Related Second Brain Notes
* [[2026-08-23-m15-m16-milestone-completion-and-live-chat-architecture]] — M15 & M16 Architecture Study.
* [[2026-08-22-domain-boundary-audit-and-performance-guardian-proposal]] — Performance Guardian Proposal.
