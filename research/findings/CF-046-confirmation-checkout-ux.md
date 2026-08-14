# CF-046 — ADR-013 confirmation UX missing on T-07

finding_id: CF-046
status: in-mr
issue: "#161"

## Claim

ADR-013 requires confirmation over blank re-entry for T-05…T-07. T-07 presented
a blank `payment_reference` text field instead of confirming session delivery,
order total, and a session payment reference.

## Fix

Checkout (T-07) now:

- Surfaces delivery destination, order total, and session payment reference for
  validation (`#checkout-confirm`)
- Defaults to confirming `session_pay_ref` (session-scoped vault token)
- Asks for a different payment reference only when the customer chooses that
  delta
- Requires an explicit acknowledgement checkbox before Place Order

## Verification

- `cd edge; python -m unittest tests.test_browser_ui -v`
