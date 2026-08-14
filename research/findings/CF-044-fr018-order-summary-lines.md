# CF-044 — FR-018 order summary missing tax/discount/customization lines

finding_id: CF-044
status: in-progress
issue: "#159"

## Claim

FR-018 requires an itemized order summary containing selected products,
customization charges, delivery fees, taxes, discounts, and total.
`PricingService` previously emitted product (+ optional card_message) and
delivery only.

## Reproduction

1. `PricingService.summarize({"product": {"product_id": "classic-rose-dozen"}})`
   returned only a `product` line.
2. Requirements FR-018 and functional design T-06 name taxes, discounts, and
   customization charges as part of the MVP summary.

## Fix

Emit FR-018 categories once a known product is selected:

- `customization` at 0.00 (ADR-006 / T-04: no thin-option or card surcharge)
- `tax` and `discount` always present (reference amounts 0.00)
- `delivery` when a destination reference exists

## Verification

- `python -m unittest platform.tests.test_pricing`
- Postgres integration `test_order_summary_facet_reflects_and_recomputes_from_decisions`
