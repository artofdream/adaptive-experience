# Mother-birthday smoke on d1debab — 16 Aug 2026

tags: #aea #customer-journey
status: assessment-only
walked_url: https://localhost:8443/
payment_included: yes
walked_at: 2026-08-16T06:57 Europe/Paris
assessed_by: aea-customer-journey
stack: origin/main `d1debab` (!191 + !192). healthz 200.

## Outcome

**Pass.** After `I need flowers...`, first chip is **for Mom**; chips include **under $75**. Composer placeholder is `under $75`. T-07 Create order → **202** order `bb5a6a92-ff29-4e64-b4c4-c8e1202b39e6` (`submitted`). No `order_not_found`. No `csrf_rejected`.

cursor-ide-browser hit the self-signed cert interstitial; Playwright against the live shop (same fallback as the 01:40 pay walk).

No new issues. #27 stays Future.
