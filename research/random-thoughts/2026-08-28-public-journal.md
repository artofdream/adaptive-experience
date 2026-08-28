# Public journal on architecture.artof.link

#aea

Related #278. Disjoint from !309 / #277. Do not batch. MRC merges.

## What shipped on the branch

- `docs/framework/journal.md` → `public/journal.html`
- Three allowlisted diagrams under `docs/framework/assets/` (JPEG, local only)
- `scripts/build_framework_site.py` renders `![alt](assets/name.jpg)` and copies safe files from `docs/framework/assets/` to `public/assets/`
- Nav + index + Path B links
- README allowlist row

## Honesty

Journal episodes are curated from committed vault facts. Public page omits ticket soup and DATE_RE. Dual-viewport after CSS remains Unknown; the journal says so without presenting Path B as verified.

## Conflict with !309

!309 adds `schema` to `PAGES`. This branch adds `journal` to `PAGES` from `main`. Second merge needs a rebase of the allowlist. Do not invent a combined commit from the implementer.

## Leftover (not this MR)

Pages visibility Everyone, Let's Encrypt for `architecture.artof.link`, TXT if GitLab still shows one. CNAME already live. Do not touch the shop ALB.
