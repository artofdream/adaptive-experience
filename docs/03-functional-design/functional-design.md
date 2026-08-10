# Functional Design

> Coherent with the MVP functional tile catalog in
> `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx`.

## Workspace sections
- Header
- Conversation
- Shared Understanding (Intent Summary)
- Adaptive Workspace (tiles)

## MVP tile catalog

| Tile | Title | Role | Scope |
|---|---|---|---|
| T-01 | Conversation and Intent | Captures natural-language goals and clarification; persistent. | MVP |
| T-02 | Intent Summary (Shared Understanding) | Shows the current interpretation and permits correction (FR-021). | MVP |
| T-03 | Curated Recommendations | Presents validated options matching intent, budget, availability, and delivery. | MVP |
| T-04 | Product Selection and Customization | Product selection, basic options (arrangement, size), and card message. Advanced customization (FR-003) is Future. | MVP |
| T-05 | Delivery and Recipient | Recipient details and valid dates/windows. | MVP |
| T-06 | Order Summary | Selections, fees, taxes, discounts, and total; continuously updated (FR-018). | MVP |
| T-07 | Checkout and Confirmation | Initiates secure payment; confirmed order only after payment succeeds (FR-019). | MVP |
| T-08 | Order Tracking | Latest authoritative preparation/dispatch/delay/delivery/completion status (FR-023). | MVP |
| T-09 | Support Escalation | Conditional overlay for unresolved requests (FR-006). | Future |

## Interaction principles
- Progressive thought completion drives intent capture (see ADR-003).
- Selective regeneration: only affected tiles refresh; completed decisions persist (FR-020).
- Latest relevant intent wins: stale responses are rejected (FR-022; ADR-005).
- AI interprets; domain services validate customer-visible facts.

## Functional flow
1. Customer arrives; the adaptive workspace initializes (T-01).
2. Discovery is seeded with contextual prompts.
3. Customer enters partial intent; thought-completion suggestions appear.
4. Shared Understanding updates in the Intent Summary (T-02); customer can correct it.
5. Curated Recommendations emerge, validated by Recommendation/Inventory/Pricing (T-03).
6. Customer selects a product and sets basic options (T-04); advanced customization (FR-003) is Future.
7. Delivery and recipient details are collected and validated (T-05).
8. Order Summary updates continuously with itemized charges (T-06).
9. Checkout initiates secure payment; the order is confirmed only after payment succeeds (T-07).
10. Workspace evolves into Order Tracking (T-08).
11. Support Escalation (T-09) remains a Future overlay outside the MVP.
