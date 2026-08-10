# Adaptive Experience Architecture — Wiki

This directory is the **reviewed source** for the GitLab project wiki.
Canonical architecture and requirements still live under `docs/`,
`implementations/`, and `archive/`. Wiki pages are a **navigation hub**: short
summaries plus links into the repo — not a second source of truth.

## Pages

| Wiki slug | Source file | Canonical docs |
|---|---|---|
| home | `home.md` | `README.md` |
| product-vision | `product-vision.md` | `docs/01-product-vision/` |
| business-analysis | `business-analysis.md` | `docs/02-business-analysis/` |
| functional-design | `functional-design.md` | `docs/03-functional-design/` |
| technical-architecture | `technical-architecture.md` | `docs/04-technical-architecture/` |
| ux-design-guide | `ux-design-guide.md` | `docs/05-ux-design-guide/` |
| architecture-decision-records | `architecture-decision-records.md` | `docs/06-adr/` |
| roadmap | `roadmap.md` | `docs/07-roadmap/` |
| florist-reference-design | `florist-reference-design.md` | `implementations/florist/` |
| coherence-workflow | `coherence-workflow.md` | `research/coherence-findings-loop.md` |
| source-of-truth | `source-of-truth.md` | `archive/` |

## Publish

```sh
python scripts/publish_wiki.py
```

Requires authenticated `glab` for this project. The script upserts each page
via the GitLab Wikis API.
