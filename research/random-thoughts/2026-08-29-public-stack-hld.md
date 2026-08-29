# Public stack HLD on architecture.artof.link

> **Tags**: #aea #promote #second-brain #public-site
> **Captured**: 2026-08-29
> **Related**: #310

Sponsor asked for a public section of the actual stack / architecture / HLD used so far.

## Probe (29 Aug 2026, Europe/Berlin)

- `GET https://architecture.artof.link/` 200. Schema page is formula/layers/hats/journeys only.
- `GET https://aea.artof.link/` 200.
- `GET https://architecture.artof.link/assets/two-hostnames.svg` 200 `image/svg+xml`.
- No `/stack` page before this note.

## Sources (committed, not pasted onto Pages)

- `docs/04-technical-architecture/aea-pilot-deployment-hld-lld.md` — Path A Compose vs Path B AWS topology; the HLD itself is not a deployment attestation.
- `docs/aea-system-documentation.md` §3 HLD (edge, BFF, modular monolith, bus, domain services, PostgreSQL).
- `infra/aws/variables.tf` defaults `aws_region = us-east-1`, `domain_name = aea.artof.link`.
- `docs/framework/README.md` — this public site is GitLab Pages from allowlisted markdown; CNAME to `artof-group.gitlab.io`; not the florist ALB.

## What shipped in the Related MR

Public `/stack` from probed 200s plus the committed HLD, in public voice. Payment mockup. Dual-viewport after CSS **Unknown**. Not ARM64. Not 3DX Lab.
