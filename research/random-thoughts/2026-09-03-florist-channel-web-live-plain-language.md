# Florist can see “web” on a live order — channel badge works (2026-09-03)

> **Tags**: #aea #florist #384 #plain-language #knowledge-first #channel
> **Captured**: 2026-09-03 ~07:22 Europe/Berlin (UTC+2)
> **Audience**: sponsor / florist / non-implementers
> **Technical twin**: [[2026-09-03-path-b-florist-384-migration-023-channel-live]]
> **Related**: [[2026-09-02-native-web-florist-story-plain-language]] · [[2026-09-03-path-b-florist-384-redeploy-prove]]

## In one sentence

After a database fix this morning, the florist staff list shows **which surface** a shopper used — a fresh website checkout showed **`web`**, and the broken orders list is working again.

## What changed in plain words

Yesterday the florist screen could list orders, but the **channel** badge (web vs phone) was stuck, and the orders API was erroring (HTTP 500) because a required database column was missing on the live shop.

This morning we applied **migration 023** on the Path B database (via a one-off ECS task, not the usual deploy pipeline). Then we checked:

1. The orders API returned **OK** again (no more 500).
2. A **new website checkout** landed on the florist list with **channel = web**.
3. Older orders from before the fix still show an empty channel — that is expected.

Evidence was posted on GitLab issue **#384**, and **#384 is being closed**.

## What this does *not* claim

- It does not claim a fresh phone-app channel badge in this same pass — only the **web** path was re-proven here.
- It does not claim the usual shop deploy pipeline now runs migrations by itself (it still does not).

## Honesty (short)

Write-through still works; channel is now visible for new web orders. Close #384 on this live evidence, not on sample UI.
