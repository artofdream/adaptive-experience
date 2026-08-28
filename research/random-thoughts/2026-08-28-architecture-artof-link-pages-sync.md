# architecture.artof.link — GitLab Pages sync from docs/framework allowlist

> **Tags**: #aea #second-brain #framework #gitlab-pages #path-b #knowledge-first
> **Captured**: 2026-08-28
> **GitLab**: Related #276 (do not `Closes #276` while domain verify remains)
> **Owners to inherit**: @aea-knowledge-guardian, @aea-product-owner, @aea-mr-coordinator, @aea-devsecops-platform
> **This node is knowledge, not DATE_RE, not a shop restyle, and not the #274 playbook.**

Later agents: the public site is allowlisted markdown under `docs/framework/`
on GitLab `main`. Merge publishes. MRC merges, not loop ticks. Shared memory
is committed GitLab `main` only. A status word is a claim.

Disjoint from !305 / !306 / #274: this node does not promote the 715-line
playbook and does not touch DATE_RE.

Existing IDs only: [[CF-052]] (aea.artof.link stays on the shop ALB),
[[CF-054-path-b-dual-viewport]] (regressed; mention on the case-study page
only, not as a trophy).

---

## 1. How sync works

A `pages` job on `main` runs `python scripts/build_framework_site.py`, which
reads the allowlist in that script (`index.md`, `path-b.md`) and writes
`public/index.html` and `public/path-b.html`. GitLab Pages publishes the
`public/` artifact. Adding a page means changing the allowlist, not globbing
the vault.

`scripts/check_knowledge_graph.py` scans `research/random-thoughts/` only,
not `docs/`. Public landing files omit `#aea` and `[[wikilinks]]`.

## 2. What is in / out

In: thin framework landing (formula + six layers + honesty), Path B as
`/path-b` case study linking out to https://aea.artof.link, this vault note,
the build script, the `pages` job, this operator how-to.

Out: shop CSS, ECS ALB hostname, Route53 in `infra/` (none), DATE_RE,
random-thoughts papers on the public site, VC TAM/raise, 3DX Lab, #274, #275.
Do not complete GitLab's "Get started with GitLab Pages" wizard (it would
generate a second CI file).

The `pages` job does not `needs` ECS jobs and does not use
`resource_group: path-b-ecs`. Terraform `domain_name` stays `aea.artof.link`
only ([[CF-052]]).

## 3. Operator how-to (GitLab Pages custom domain)

Click path is GitLab's current docs, probed 28 Aug 2026 (Europe/Berlin) on
this project: **Deploy → Pages**, not Settings → Pages for New domain.
Access control lives under **Settings → General → Visibility, project
features, permissions → Pages**.

Source: https://docs.gitlab.com/user/project/pages/custom_domains_ssl_tls_certification/
and https://docs.gitlab.com/user/project/pages/pages_access_control/

### Do this after MRC merges !308 and the `pages` job has run on `main`

1. Open the project → **Deploy → Pages**.
2. Skip any **Get started with GitLab Pages** wizard (see §4).
3. **New domain**. Domain: `architecture.artof.link`. Leave **Automatic
   certificate management using Let's Encrypt** on. Create New Domain.
4. Copy the verification TXT GitLab shows. Do **not** invent the code.
   - Name/Host: `_gitlab-pages-verification-code.architecture.artof.link`
   - Type: TXT
   - Value: `gitlab-pages-verification-code=<code from GitLab>`
   - If Route53 auto-appends `artof.link`, the record name is only
     `_gitlab-pages-verification-code.architecture`.
5. Paste that TXT in Route53, AWS account `737290977112`, hosted zone
   `artof.link`. Sponsor leftover. There is no `aws_route53` in `infra/`.
   Do not invent a zone ID.
6. Deploy → Pages → Edit domain → **Retry verification**.
7. Set Pages visibility to **Everyone** (project is private; gitlab.io
   otherwise 302s to GitLab login). Then optional **Force HTTPS**.

CNAME is already live (probed 28 Aug 2026): `architecture.artof.link` →
`artof-group.gitlab.io` (A `35.185.44.232`, AAAA `2600:1901:0:7b8a::`).
Do **not** point this hostname at the Path B ALB or Terraform
`domain_name` ([[CF-052]]).

TLS until verify: GitLab still serves the `*.gitlab.io` wildcard, so
HTTPS to `architecture.artof.link` is a hostname mismatch. Let's Encrypt
for the custom domain starts after TXT verify.

Resolving to GitLab IPs is **not** "the site is up". Site HTML is Unknown
until `pages` runs on `main` and Pages is Everyone.

## 4. Wizard trap (probed 28 Aug 2026)

Until a `pages` job has published on `main`, GitLab shows
**Get started with GitLab Pages** (step 1 of 4) on Deploy → Pages.
Sponsor screenshot that evening: breadcrumb
`artof-group / adaptive-experience-architecture` → Pages. Step 1 fields:

- Select your build image: default `node:lts`
- Choose a directory to publish: default `public`
- Next

That wizard generates a `.gitlab-ci.yml` (or a Pages CI snippet). **Do not
hit Next. Do not commit it.** AEA's job is already in !308:
`python:3.12-alpine`, `python scripts/build_framework_site.py`, artifact
`public/`. `node:lts` would fight that. If the wizard already committed a
branch, drop it; do not merge it.

After MRC merges !308 and the job runs, this wizard should go away and
**New domain** plus Access Control remain.

## 5. First-merge CI note

Existing ECS jobs (`build-ecr`, `deploy-ecs`, agent-runner) already watch
`.gitlab-ci.yml`. Adding the `pages` job changes that file, so those jobs
may queue on the first `main` pipeline. They remain independent of `pages`.
MRC / sponsor may cancel an unwanted shop redeploy. Do not attach `pages`
to `path-b-ecs`.

## 6. Next

MRC merges the Pages/code MR with `Related #276`. Keep #276 open until
custom-domain TXT verify + Pages Everyone + Let's Encrypt. CNAME is not
the leftover anymore.
