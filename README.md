# Adaptive Experience Architecture (AEA)

Designing AI-native experiences that evolve with shared understanding.

## Reference design
Lily's Florist Shop.

## Naming
- **AEA** — Adaptive Experience Architecture (this repository / product architecture).
- **Lily's Florist Shop** — the reference design (also shortened to **Florist** under
  `implementations/florist/`).
- **Quantic** — legacy label retained only in some `archive/` filenames (for example
  the canonical workbook). Do not rename those archive files; treat Quantic as
  historical packaging, not a current product name.

## Repository areas
- [Product vision](docs/01-product-vision/product-vision.md)
- [Business analysis](docs/02-business-analysis/business-goals-epics-stories.md)
- [Functional design](docs/03-functional-design/functional-design.md)
- [Technical architecture](docs/04-technical-architecture/technical-architecture.md)
- [UX design guide](docs/05-ux-design-guide/ux-design-guide.md)
- [Architecture Decision Records](docs/06-adr/ADR-001-shared-understanding.md)
- [Roadmap](docs/07-roadmap/roadmap.md)
- [Requirement evidence convention](docs/08-traceability/requirement-evidence.md)
- [Florist reference design](implementations/florist/README.md)
- [Platform foundation](platform/README.md) — product-neutral PostgreSQL,
  outbox, Kafka, governance, and orchestration services.
- [Edge browser perimeter](edge/README.md) — TLS gateway, BFF, browser UI, and
  least-data Edge-to-Orchestration contracts.
- Research / Claude ↔ Obsidian loop ([`research/claude-obsidian-loop.md`](research/claude-obsidian-loop.md))
- GitLab wiki source ([`wiki/`](wiki/) — publish with `python scripts/publish_wiki.py`)
- Stakeholder skills: canonical role definitions under [`.cursor/skills/`](.cursor/skills/),
  with generated discovery adapters for Codex ([`.agents/skills/`](.agents/skills/)),
  Claude ([`.claude/skills/`](.claude/skills/)), Copilot
  ([`.github/instructions/`](.github/instructions/)), and Gemini
  ([`.gemini/skills/`](.gemini/skills/)),
  regenerated with `python scripts/generate_codex_stakeholder_skills.py`.

## Source of truth
The canonical requirements model lives in [`archive/`](archive/):

- [`Quantic_Project_Consolidated_Coherence_Validated.xlsx`](archive/Quantic_Project_Consolidated_Coherence_Validated.xlsx) — canonical mapping (7 business goals · 7 epics · 23 user stories · 17 non-functional stories · 40 requirements). Docs under `docs/` derive from this file. The CI coherence guard (`scripts/check-coherence.sh` → `scripts/check_coherence.py`) parses the workbook's Consolidated Mapping sheet and fails if markdown BG/US/NFR-US/FR/NFR counts diverge from it.
- [`Lilys_Florist_final.pdf`](archive/Lilys_Florist_final.pdf) — full requirements-engineering report.
- [`sample-layout-3.png`](archive/sample-layout-3.png) — unannotated sample workspace layout.
- [`sample-layout-3-with-notes.png`](archive/sample-layout-3-with-notes.png) — annotated sample workspace layout.
- [`canonical-requirements.csv`](archive/canonical-requirements.csv) — reviewable
  text export of requirement, story, and scope rows. Update it in the same
  change as the workbook; the workbook remains authoritative.

Large binaries (`*.pdf`, `*.png`) are stored via **Git LFS** (see
`.gitattributes`). The `.xlsx` mapping is kept as a plain file; use the CSV
export for meaningful Git review because XLSX is a packaged binary format.

## North star
Adaptive Experience Architecture enables AI-native applications where shared understanding continuously reshapes the workspace without disrupting the user's flow.
