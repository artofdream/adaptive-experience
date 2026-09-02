# What we proved tonight — phone app and website orders both reach the florist

> **Tags**: #aea #florist #companion #sponsor #plain-language #knowledge-first
> **Captured**: 2026-09-02 evening Europe/Berlin (UTC+2)
> **Audience**: sponsor / florist / non-implementers
> **Public story**: [architecture.artof.link/companion](https://architecture.artof.link/companion)
> **Technical twin**: [[2026-09-02-native-web-gap-closing-technical-handoff]]
> **Related capture**: [[2026-09-02-florist-operator-native-web-completeness-gaps]] · [[2026-09-02-asus-play-v3-smoke-native-gaps]] · [[2026-09-02-companion-native-web-gap-closing-loop]]

## In one sentence

Orders placed from the **phone app** and from the **website** both showed up for the florist on `/florist` tonight — live list, not a fake sample inbox.

## What we proved

We ran a careful dual check on the live shop:

1. Someone checks out on the **website**.
2. Someone checks out on the **phone companion** (ASUS test phone).
3. The florist screen at `https://aea.artof.link/florist` shows **both** orders in the staff list.

So the big “does the phone path actually write through to the atelier?” question is answered for tonight: **yes, both channels land**.

Public background on the thin phone client: [architecture.artof.link/companion](https://architecture.artof.link/companion).

## What the florist still couldn’t see well

Getting the order *onto* the list is not the same as having every useful field on screen. Tonight the florist still struggled with:

| Need | Why it mattered | Issue | Status (as of this note) |
|------|-----------------|-------|--------------------------|
| Card text in the list | Florist needs the enclosure message at a glance | #383 | Fixed in code via !418 (merged) — needs florist UI redeploy + re-check |
| Web vs phone channel | Can’t tell which surface the shopper used | #384 | Still open — Unknown until live re-check after deploy |
| Product name + price/total | Slug alone is hard to fulfill against | #385 | Fixed in code via !418 (merged) — needs florist UI redeploy + re-check |

Plain takeaway: **write-through works**; **readability on the florist screen** was the remaining gap. Card and money/title fixes are merged in !418; channel (#384) is not closed yet — treat live channel badges as **Unknown** until someone looks again after deploy.

## Phone app nits on the ASUS test phone

While walking Need → Pick → Pay on the dedicated ASUS, we also found small companion UX issues:

| Finding | Issue |
|---------|-------|
| Budget filter still showed a cheaper arrangement than the selected band | #387 |
| Budget label collapsed to a bare number after picking a product | #388 |
| Anniversary journey prefills a Birthday Mom card message | #389 |
| Install looked **debug** (`DEBUGGABLE`, installer empty) — do **not** claim “from Play Store” for that session | #390 |

Fix MRs for #387–#389 are in flight. #390 is an honesty caution, not a florist-screen bug.

## What’s next (plain words)

1. Land the remaining phone UX fixes (#387–#389).
2. Redeploy the florist UI so !418 (and related staff-list work) is what operators actually see.
3. Re-check on the **phone** and on the **florist screen**: card text, title/total, and especially **channel** (#384).
4. Keep the Play honesty gate honest (#390): only say “Play” when the install is clearly store-signed and not debuggable.

No CRM expansion. No claiming sample inbox rows as live orders. The florist gets fulfillment facts; shopper privacy stays least-data.

## Honesty (short)

- Sample florist inbox ≠ live atelier orders.
- Merged code ≠ live until redeploy + look-again.
- Debug / App Distribution install ≠ “installed from Play”.
