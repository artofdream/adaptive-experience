# Source of truth

Canonical requirements live in [`archive/`](https://gitlab.com/artof-group/adaptive-experience-architecture/-/tree/main/archive):

| Artifact | Role |
|---|---|
| `Quantic_Project_Consolidated_Coherence_Validated.xlsx` | Authoritative mapping (7/23/17/40) |
| `canonical-requirements.csv` | Reviewable text export (must match workbook) |
| `Lilys_Florist_final.pdf` | Requirements-engineering report |
| `sample-layout-3-with-notes.png` | Annotated sample workspace layout |

Published docs under `docs/` and `implementations/` derive from the workbook.
CI `coherence-guard` fails if inventories, chains, scope, or CSV triples drift.

Wiki pages in this project are **navigation only** — edit `wiki/` in git and run
`python scripts/publish_wiki.py` rather than treating the wiki as authoritative.
