# CF-010 — Stub GitLab wiki pages

tags: #aea #coherence-finding
status: verified
finding_id: CF-010
severity: medium
issue: #101
mr: !50
branch: docs/cf-010-populate-gitlab-wiki
published: 2026-08-10 via scripts/publish_wiki.py
verified_on_main: 660db1e

## Claim

GitLab wiki lists 11 pages, but each body is a one-line title stub (~9–48
characters) and is not populated from canonical `docs/` / `implementations/` /
`archive/`.

## Evidence

- `glab api projects/:id/wikis` — 11 slugs present
- Sample lengths: `home` 48, `product-vision` 16, `roadmap` 9
- Accidental wiki stubs were previously removed from git (`d6d0d98`)

## Reproduction

1. `glab api projects/:id/wikis`
2. `glab api projects/:id/wikis/product-vision` → content is `# Product Vision` only

## Intended fix

- Add reviewed navigation-hub markdown under `wiki/`
- Publish via `scripts/publish_wiki.py` (GitLab Wikis API)
- Do not duplicate SoT; link into `docs/` / `archive/` / florist design
