# Functional view extract (29 Aug 2026)

Related: #295. Public ancestor slice is #296 (Path B only). Journal origin is #293 / !322 (merged). Copyright rule is #294. Quantic assignment packet is not in this repo.

This note is what later agents should read instead of rediscovering the workbook.

## Sources in the vault

- `archive/Lilys_Florist_final.pdf` — group delivery (Meghna Desai, Hiren Vadalia, Claude Tsarafidy). Already on `main`.
- `archive/Lilys_Florist_MVP_Functional_Architecture.pdf` — original 9-page functional view. Team-authored. Added with this note.
- `archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx` and `archive/canonical-requirements.csv` — already on `main`. Do not treat them as live shop evidence.
- Quantic *Managing AI Engineering Project* brief: cited, not stored. A sponsor attachment is not a publish license.

## What survived into AEA

These are the team's own design lines, not a Quantic rubric.

- Intent before navigation. The experience starts from a goal, not a catalog tree.
- One persistent workspace. Conversation, recommendations, delivery, and the order stay in one place.
- Selective regeneration. Only the tiles that a change touches refresh.
- Loose coupling on a topic bus. Tiles do not call each other directly.
- AI interprets; domain services validate. Price, inventory, delivery, payment, and the order stay authoritative.
- Implementation-neutral on purpose, so wireframes and services could move together.

Live schema already says the same split in public words. The functional view is the ancestor, not the live shop.

## Tile roles (IDs as written in that view)

Do not invent new IDs. These eight already appear in the functional view:

- T-01 Conversation and intent
- T-02 Intent summary
- T-03 Curated recommendations
- T-04 Product selection and customization
- T-05 Delivery and recipient
- T-06 Order summary
- T-07 Checkout and confirmation
- T-08 Support escalation

Domain services named there: catalog, inventory, recommendation, pricing, delivery, order, payment, support.

## What drifted

- Four named journeys (Urgent Sam, Planner Sarah, Loyal Alex, Tracker Chris) are later Path B names. They are not in the 9-page view.
- The outer harness (two hostnames, claim-vs-probe, fourteen hats) is later.
- Live payment is still a mockup.
- Dual-viewport after CSS remains Unknown.
- The view deferred multi-agent orchestration, predictive inventory, and arbitrary AI-generated UI. Those are still not AEA claims.

## Not on Pages

- The Quantic packet, its rubric, its sample questions, its failure statistic.
- The full FR / NFR / epic tables from the group delivery.
- Interview share links and the Jira board.
- This extract. Vault stays vault.
- A screenshot or reprint of either PDF.

## Check before reuse

Is the sentence ours? If it is a course teaching paragraph, stop. If a public page needs a fact, paraphrase and keep it thin. Path B may name the ancestor. Schema does not get a tile ID table.
