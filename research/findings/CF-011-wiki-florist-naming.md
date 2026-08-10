# CF-011 — Wiki florist naming (implementation vs design)

tags: #aea #coherence-finding
status: verified
finding_id: CF-011
severity: low
issue: #102
mr: !51
branch: docs/cf-011-wiki-florist-naming
published: 2026-08-10 florist-reference-design wiki republished
verified_on_main: 8537084

## Claim

`wiki/florist-reference-design.md` calls Lily's Florist the AEA “reference
implementation”, while root README (and page title) use “reference design”.

## Evidence

- `wiki/florist-reference-design.md` L3
- `README.md` naming section: “reference design”

## Intended fix

Align wiki wording to “reference design” and republish via
`python scripts/publish_wiki.py`.
