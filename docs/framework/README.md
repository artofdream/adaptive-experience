# Framework public site — allowlist and sync SOP

PO-owned public surface for `architecture.artof.link`. The website **is** the allowlisted markdown in this directory on GitLab `main`. Merge = publish. No CMS.

Graph-guard (`scripts/check_knowledge_graph.py`) scans `research/random-thoughts/` only, not `docs/`. Public pages here omit `#aea` and `[[wikilinks]]`. HTML is generated; wikilinks would not render usefully anyway.

## Allowlist (published HTML)

| Source | Published as |
|--------|----------------|
| `docs/framework/index.md` | `public/index.html` |
| `docs/framework/path-b.md` | `public/path-b.html` |

This README is operator SOP. It is **not** in the allowlist and is not published.

Adding a public page means:

1. Add the markdown under `docs/framework/`.
2. Add a row to `PAGES` in `scripts/build_framework_site.py`.
3. MR. MRC merges. The `pages` job on `main` rebuilds `public/`.

Do not glob the whole repo. Do not paste DATE_RE, vault papers, TAM/raise, or 3DX Lab onto the public site. Do not restyle the shop.

## Sync SOP

1. Edit allowlisted files in this directory (framework-only). Path B stays a case study.
2. Open one MR from `main`. Do not batch #274 / #275 or the playbook paper.
3. MRC merges. Do not self-merge.
4. On `main`, CI job `pages` runs `python scripts/build_framework_site.py` and publishes the `public/` artifact to GitLab Pages.
5. Until DNS exists, the site is at `https://artof-group.gitlab.io/adaptive-experience-architecture/`.
6. Sponsor leftover: GitLab Pages custom domain `architecture.artof.link` → CNAME to `artof-group.gitlab.io` plus verification TXT. Do not add this hostname to the Path B ALB or Terraform `domain_name` (CF-052). There is no Route53 in `infra/`.

The `pages` job does not `needs` ECS jobs and does not use `resource_group: path-b-ecs`.
