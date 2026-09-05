# Session Memory Log: #331 image digest pins (2026-09-05)

> **Tags**: #aea #session-memory #dso #ci #image-digest #second-brain
> **Captured**: 2026-09-05
> **Author**: `@aea-knowledge-guardian` with `@aea-devsecops-platform`
> **Related**: [[2026-09-05]] · [[2026-09-05-session-memory-log-cts-ai-afk-cloud-handover]] · #331 · !481

---

## Decisions

- #330 / !480 is on `main` (`9391e43`). This slice is **#331 only**. Do not stack #332–#334 onto `.gitlab-ci.yml`.
- Digest pins are the **amd64 platform digests GitLab SaaS actually pulled** on pipeline `2823193345` (and related jobs). That matches Path B / GitLab runners. Do not substitute a multi-arch index digest unless a job printed that index.
- `grafana/grafana:10.4.0` was not printed in the edge-docker log used for other pins. The recorded digest `sha256:f9811e4e…` matches the linux/amd64 Image ID in prometheus-community/helm-charts#4382. If GitLab `edge-docker-integration` rejects it, fix the pin from that job log — do not invent a newer tag rebuild.
- `ghcr.io/berriai/litellm:main-latest` stays an **expiring exception** (`image-digest-exceptions.json`, owner `@aea-devsecops-platform`, expires `2026-10-05`). GHCR was not live-resolvable from this cloud VM. Do not invent a `main-latest` digest.
- Required job is `image-digest`. Isolated from `pip-audit` (#330). No Trivy/Syft/Checkov/tfsec in this MR.

## Trade-offs

- This cloud VM cannot reach Docker Hub / GHCR / PyPI. Local proof is the gate + 14/14 guards. Live image **pull/build** proof is GitLab `image-digest`, `edge-docker-integration`, and `platform-foundation-integration`.
- Fixture names `*.Dockerfile` are Dockerfiles. The gate must treat `unpinned.Dockerfile` as a Dockerfile, not YAML.

## Do not

- Merge !481 from the author session. Undraft when required CI is green; MRC owns merge.
- Start #332 image SBOM/scan or #334 IaC scan on this branch.
- Commit dirty Android `mipmap-*` launcher PNGs from this VM snapshot.
