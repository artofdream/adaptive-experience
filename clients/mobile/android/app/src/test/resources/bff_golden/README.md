# BFF golden fixtures (native↔web contract)

Shapes mirror web `confirmAndPay` in `edge/gateway/ui/assets/app.js`:

- `observed_total: Number(order_summary.total)` after delivery (product + REFERENCE_DELIVERY_FEE $12)
- `payment_reference: "session_pay_ref"` (opaque vault ref; no raw card fields)

Used by `BffWebContractTests` (#367). Do not claim operator/website dual-write from these unit fixtures (#360).
