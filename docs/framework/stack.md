# Stack

This page is the high-level design **used so far**. The formula and layers stay on the [schema](schema.html). Dual-viewport after CSS remains **Unknown**. Payment is still a mockup.

[Two hostnames](#two-hostnames) · [This site](#this-site) · [Florist runtime](#florist-runtime) · [Honesty](#honesty)

## Two hostnames

Two public hostnames, two jobs:

- [architecture.artof.link](https://architecture.artof.link) is this framework site.
- [aea.artof.link](https://aea.artof.link) is the live florist case study.

They do not share a load balancer. This site is not the shop.

![Two hostnames: framework site and florist case study](assets/two-hostnames.svg)

## This site

Allowlisted markdown in the framework folder is built to static HTML and published as GitLab Pages. The hostname is a DNS alias to that Pages site, with HTTPS. There is no CMS.

Probed 29 August 2026: `GET https://architecture.artof.link/` returned 200.

## Florist runtime

The live shop at [aea.artof.link](https://aea.artof.link) is the Path B instantiation of the formula.

The browser workspace (experience tiles) goes through a TLS edge, then a backend-for-frontend, then orchestration and a contract-first message bus. Authoritative domain services (catalog, inventory, recommendations, pricing, delivery, order, payment) write to PostgreSQL. The assistant may interpret intent. Domain services still decide.

The reference cloud path is AWS (region `us-east-1` in the committed Terraform): public HTTPS load balancer, containers for gateway, BFF, and orchestration, managed PostgreSQL, and a Kafka-compatible bus. A model gateway sits on the private side of that path so the browser never talks to the database or the bus.

A laptop path exists too: Docker Compose with the same edge / BFF / platform split. That is for developers. It is not this website.

Probed 29 August 2026: `GET https://aea.artof.link/` returned 200. That is not a dual-viewport probe and not a payment probe.

## Honesty

- Payment is still a mockup.
- Dual-viewport after CSS remains **Unknown**.
- Native mobile is a later client for the same backend, not this stack.
- This page does not dump internal runbooks, and it does not include 3DX Lab.

See the [schema](schema.html) for the formula, the [Path B case study](path-b.html) for the florist journeys, or the [journal](journal.html) for how this was learned.
