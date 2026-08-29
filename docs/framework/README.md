# Framework public site — allowlist and sync SOP

PO-owned public surface for `architecture.artof.link`. The website **is** the allowlisted markdown in this directory on GitLab `main`. Merge = publish. No CMS.

Graph-guard (`scripts/check_knowledge_graph.py`) scans `research/random-thoughts/` only, not `docs/`. Public pages here omit `#aea` and `[[wikilinks]]`. HTML is generated; wikilinks would not render usefully anyway.

## Allowlist (published HTML)

| Source | Published as |
|--------|----------------|
| `docs/framework/index.md` | `public/index.html` |
| `docs/framework/schema.md` | `public/schema.html` |
| `docs/framework/comparison.md` | `public/comparison.html` |
| `docs/framework/path-b.md` | `public/path-b.html` |
| `docs/framework/journal.md` | `public/journal.html` |
| `docs/framework/assets/` (safe filenames only) | `public/assets/` |

This README is operator SOP. It is **not** in the allowlist and is not published.

Adding a public page means:

1. Add the markdown under `docs/framework/`.
2. Add a row to `PAGES` in `scripts/build_framework_site.py`.
3. MR. MRC merges. The `pages` job on `main` rebuilds `public/`.

Images and short videos are optional. Use `![alt](assets/name.jpg)` or `![alt](assets/name.mp4)` on its own line. The builder copies only files whose path matches `assets/[A-Za-z0-9._-]+\.(png|jpg|jpeg|webp|svg|mp4|webm)`. An `mp4`/`webm` line becomes a `<video controls>` player; a matching `.jpg` is used as the poster. No remote URLs. No `..`. No mermaid (the builder does not render it).

Do not glob the whole repo. Do not paste DATE_RE, vault papers, TAM/raise, or 3DX Lab onto the public site. A lean [comparison](comparison.md) page is allowlisted; the 715-line vault working paper is not. Do not restyle the shop.

## Sync SOP

1. Edit allowlisted files in this directory (framework-only). Path B stays a case study.
2. Open one MR from `main`. Do not batch #274 / #275 or the playbook paper.
3. MRC merges. Do not self-merge.
4. On `main`, CI job `pages` runs `python scripts/build_framework_site.py` and publishes the `public/` artifact to GitLab Pages.
5. After MRC merge, the `pages` job on `main` publishes `public/`.
6. **Do not** use GitLab's **Get started with GitLab Pages** wizard (step 1
   defaults to `node:lts` + `public/`). That would generate a second CI file
   and fight `scripts/build_framework_site.py` (`python:3.12-alpine`). Leave
   the wizard until the job has run; then **Deploy → Pages → New domain**.
7. Custom domain leftover (sponsor, Route53 account `737290977112`):
   CNAME `architecture.artof.link` → `artof-group.gitlab.io` is **already
   live**. Add the GitLab Pages **TXT** GitLab shows after New domain. Then
   Retry verification, set Pages visibility to **Everyone**, leave Let's
   Encrypt on. Click path: **Deploy → Pages** (not Settings → Pages).
   Access control: **Settings → General → Visibility → Pages → Everyone**.
   Do not add this hostname to the Path B ALB or Terraform `domain_name`
   (CF-052). There is no Route53 in `infra/`.

The `pages` job does not `needs` ECS jobs and does not use `resource_group: path-b-ecs`.
