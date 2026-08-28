# Adaptive Experience Architecture

**Adaptive Experience = Shared Understanding + Domain Services + Outer Harness.**

This site is the public surface for that formula and the six layers around it. It is not a shop, not a CMS, and not a pitch deck.

The Path B florist at [aea.artof.link](https://aea.artof.link) is one [case study](path-b.html), not the home. The [schema](schema.html) is the public map (formula, layers, loop, roles, named journeys). A [comparison](comparison.html) names sources and says what the related-work mapping is and is not.

## Formula

Shared Understanding is the session's current, reviewable model of intent. Domain services are authoritative: they validate stock, price, delivery, and payment. The outer harness is everything that keeps those two honest in production — guides, sensors, the loop, memory, permissions, and observability.

AI may interpret. Domain services decide. Status words are claims; they need a probe.

## Six layers

1. **Guides** — constraints and playbooks that steer the experience (what may be said, what must be checked, who owns a surface). Fourteen hats are **roles**, not extra layers.
2. **Sensors** — how the system notices intent, viewport, and state without inventing it.
3. **Loop** — interpret, act, verify, remember. Closing a ticket is not the same as a probe.
4. **Memory** — Shared Understanding that persists for a session. Memory stores what was agreed, not what would look good on a slide.
5. **Permissions** — who may change what. Domain services stay authoritative; the outer harness does not silently restyle or redeploy a live shop.
6. **Observability** — evidence for every status word. If the probe is missing, write **Unknown**.

## Honesty

A status word (`verified`, `shipped`, `complete`) is a claim. Probe it with the same journey, the same viewport, or a mechanical check — or write Unknown. Do not treat a merged spec or a CSS change as verification.

Fourteen hats are lenses. Three executable jobs: implement, verify, merge (MRC only).

## What this site is

- The AEA **framework** (formula + six layers), published from allowlisted markdown on GitLab `main`. See [schema](schema.html) for the communication map and [comparison](comparison.html) for sources.
- Edit `docs/framework/`, open an MR, MRC merges, GitLab Pages publishes. No CMS.
- Intended hostname: `architecture.artof.link` (CNAME to `artof-group.gitlab.io` is live; GitLab Pages domain verification and Let's Encrypt remain). Until Pages publishes, treat the site as not up.

## What this site is not

- Not the Path B shop (`aea.artof.link`, ECS Fargate). That hostname stays on the ALB only (CF-052).
- Not a section bolted onto the pilot.
- Not internal vault papers, fundraising materials, or lab prototypes.
- Not a florist theme and not a screenshot gallery.

Read the [Path B case study](path-b.html) if you want to see one instantiation, including what is still **regressed**.
