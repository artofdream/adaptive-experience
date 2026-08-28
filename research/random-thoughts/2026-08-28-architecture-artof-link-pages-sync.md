# architecture.artof.link — GitLab Pages sync from docs/framework allowlist

> **Tags**: #aea #second-brain #framework #gitlab-pages #path-b #knowledge-first
> **Captured**: 2026-08-28
> **GitLab**: Related #276 (do not `Closes #276` while DNS remains)
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
the build script, the `pages` job.

Out: shop CSS, ECS ALB hostname, Route53 (none in `infra/`), DATE_RE,
random-thoughts papers on the public site, VC TAM/raise, 3DX Lab, #274, #275.

The `pages` job does not `needs` ECS jobs and does not use
`resource_group: path-b-ecs`. Terraform `domain_name` stays `aea.artof.link`
only ([[CF-052]]).

## 3. DNS leftover (sponsor, one-time)

There is no `aws_route53` in `infra/`. Do not invent a zone ID.

Until DNS exists, after MRC merge the site is at
`https://artof-group.gitlab.io/adaptive-experience-architecture/`.

Sponsor leftover:

1. GitLab: Settings → Pages → New domain `architecture.artof.link`.
2. DNS CNAME: `architecture.artof.link` → `artof-group.gitlab.io`.
3. DNS TXT: GitLab Pages verification record (value shown in the Pages UI).
4. Do **not** add this hostname to the Path B ALB or Terraform `domain_name`.

## 4. First-merge CI note

Existing ECS jobs (`build-ecr`, `deploy-ecs`, agent-runner) already watch
`.gitlab-ci.yml`. Adding the `pages` job changes that file, so those jobs
may queue on the first `main` pipeline. They remain independent of `pages`.
MRC / sponsor may cancel an unwanted shop redeploy. Do not attach `pages`
to `path-b-ecs`.

## 5. Next

MRC merges the Pages/code MR with `Related #276`. Keep #276 open until DNS
is done, or close only the Pages/code part and leave DNS listed as remaining.
