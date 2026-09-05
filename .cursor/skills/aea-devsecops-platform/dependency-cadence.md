# Joint DSO + SSE dependency pin cadence

> **Captured**: 2026-08-29
> **Owner**: `@aea-devsecops-platform` with `@aea-senior-software-engineer`
> **Traceability**: Issue #318
> **Not** a fifth daily PM status slot (08:00 / 12:00 / 16:00 / 20:00).

Image pins and app toolchains are different surfaces. Review them **together**
once a month so a Java 21 app is not tested on an OpenJDK 17 CI image
(!341 / `cimg/android:2024.01`).

Ledger: `research/random-thoughts/dependency-pin-ledger.csv`
Digest resolutions (#331): `research/random-thoughts/image-digest-pins.csv`

## Who owns what

| Surface | Owner | Examples |
|---|---|---|
| Environment / image pins | `@aea-devsecops-platform` | `.gitlab-ci.yml` `image:`, Compose vs cloud, `cimg/*`, `docker:*` |
| App toolchain / libraries | `@aea-senior-software-engineer` | Gradle, AGP, Kotlin, `jvmTarget`, `platform/requirements.txt` + `platform/requirements.lock`, edge Python + `edge/requirements.lock` |
| Vulnerable pin (CVE) | `@aea-appsec-auditor` files; SSE/DSO patch | Not this cadence’s default |

Do not pick one owner for “all dependencies.” A collision needs **both**.

## When

- Calendar month (first invoked DSO or SSE session in that month), **or**
- When the sponsor / PM asks for the pin cadence, **or**
- After a class-version / image-vs-toolchain CI miss.

Skip if a ledger row already exists for that `month`. Do not invent a
daily meeting.

## What to record (honesty)

One CSV row per month. Columns are fixed (see the ledger header).

1. **DSO** lists current CI/compose image pins that run builds or tests.
2. **SSE** lists current app JVM / language / AGP / Gradle pins in-repo.
3. **Collision** is `yes` when a required job’s runtime cannot load what
   the app emits (e.g. `jvmTarget` 21 vs image JDK 17). Otherwise `no`.
4. If `yes`: one GitLab issue → one branch from `origin/main` → one MR.
   Do not `allow_failure` the required job to hide it.
5. If the review did not run: do **not** write `collision=no`. Leave the
   month without a row (stale), or write `skipped` in `notes`.

Local Android SDK remains skip-honest (no SDK → attest skipped).

## Check

```text
python scripts/check_dependency_pin_cadence.py --check
```

Validates the ledger header and that the latest `reviewed` date parses.
Does not invent a 15th blocking guard.
