# System Architecture & Stack

This page is the high-level technical map of the cloud infrastructure, services, and client applications that power the Adaptive Experience.

> **In Plain English:** When a customer orders flowers online, what happens behind the scenes? This page explains how our cloud servers, secure gateways, event message streams, databases, and mobile apps connect together. It shows how we keep customer interactions fast and private, prevent web browsers from ever touching raw databases, and keep our documentation completely separate from the live shop.

[Two hostnames](#two-hostnames-two-jobs) · [Documentation site](#the-documentation-site) · [Florist runtime](#the-florist-shop-runtime) · [System architecture](#system-architecture-high-level-design) · [Request flow](#request-flow-from-browser-to-database) · [Mobile companion](#the-mobile-companion-app) · [Honesty ledger](#honest-status-ledger)

---

## Two Hostnames, Two Jobs

To prevent interference and ensure high reliability, we operate two distinct public domains:

- **[architecture.artof.link](https://architecture.artof.link):** The framework documentation site (the site you are reading now). It hosts static architecture papers, blueprints, case study videos, and honesty ledgers.
- **[aea.artof.link](https://aea.artof.link):** The live flower shop reference application. It runs the full interactive shopping workspace, cart, and order fulfillment simulation.

These two sites do not share a server, database, or load balancer. If the shop receives heavy traffic, the architecture site is completely unaffected, and vice versa.

![Two hostnames: framework site and florist case study](assets/two-hostnames.svg)

---

## The Documentation Site

The framework site at [architecture.artof.link](https://architecture.artof.link) is built entirely from verified markdown files in this repository.

- **Pure Static Delivery:** A standard-library Python script converts the documentation into lightweight, fast-loading HTML pages published via GitLab Pages.
- **Zero Content Management Systems (CMS):** There is no WordPress, no database, and no tracking scripts. Updates are made through peer-reviewed git merge requests.
- **Status:** Probed and operational with HTTPS.

---

## The Florist Shop Runtime

The live flower shop at [aea.artof.link](https://aea.artof.link) is a real-world deployment of the Adaptive Experience formula:

1. **Secure Perimeter (TLS Edge & BFF):** Web browsers and mobile apps communicate exclusively with a Backend-for-Frontend (BFF) over encrypted HTTPS. Browsers are never allowed to query databases directly.
2. **Event-Driven Orchestration:** User actions (such as selecting a bouquet or adding a card message) are published to a contract-first, Kafka-compatible message bus.
3. **Authoritative Domain Services:** Independent services handle catalog lookups, inventory verification, pricing rules, delivery slot allocation, and order creation. They write directly to a secure PostgreSQL database.
4. **Isolated AI Gateway:** Conversational models sit securely behind a model gateway on a private network, interpreting customer intent without possessing write access to customer financial records.
5. **Cloud Infrastructure:** Hosted in AWS (`us-east-1`) via committed Terraform templates, utilizing ECS Fargate container clusters, Application Load Balancers, and managed PostgreSQL. A local Docker Compose environment mirrors this exact architecture for developer testing.

---

## System Architecture (High-Level Design)

The diagram below illustrates how web shoppers and mobile companion apps connect through the TLS Edge and BFF into the orchestration bus and core services:

![Path B high-level design as used so far](assets/path-b-hld-as-is.svg)

---

## Request Flow: From Browser to Database

This diagram shows how a customer request travels from left to right: from the client's screen, through perimeter security checks, into orchestration, across the message bus, and down into authoritative domain databases:

![Path B as-is flow from clients through TLS edge, BFF, orchestration, bus, and domain services](assets/path-b-flow-as-is.svg)

---

## The Mobile Companion App

The Android companion is an alternative mobile client designed for fast on-the-go orders. It connects to the **same** backend and domain services as the website:

- **Single Source of Truth:** The mobile app shares inventory, pricing, and orders with the website. It does not run a separate database or invent prices.
- **Architectural Vision:** Below is the target architecture diagram showing the companion operating alongside the web shop on the shared BFF:

![Path B to-be high-level design with a native Android companion on the same BFF](assets/path-b-hld-to-be-native.svg)

---

## Honest Status Ledger

Every capability mentioned on this site is classified by its verified production status:

> **Two Public Hostnames** — **Live & Probed:** `architecture.artof.link` (documentation) and `aea.artof.link` (shop) operate on independent infrastructure.
>
> **Backend Domain Services** — **Live on AWS ECS:** PostgreSQL, Kafka-compatible event streaming, and Edge BFF are deployed and active on AWS ECS Fargate.
>
> **Google Play Mobile Distribution** — **Probed (4 Sep 2026):** Production release build (version `5`, non-debuggable) verified on physical ASUS ROG and Samsung Galaxy hardware via Google Play Internal Track (#390).
>
> **Mobile Order Write-Through** — **Probed (4 Sep 2026):** Orders placed in the companion app write through to the store's central database and appear in real time on the florist dashboard with `client: companion-android` (Order `34091114-cb91-44de-a5a3-6be78c503912`, #375, #384).
>
> **Payment Processing** — **Deterministic Simulation:** Real credit card charging is not connected. Payment is safely simulated via an in-memory payment engine under ADR-016.
>
> **Dual-Viewport Layout Proof** — **Unknown:** While responsive CSS has merged, a complete side-by-side journey recording showing desktop (16:9) and phone (9:16) working simultaneously has not yet been captured.
>
> **Operator Dashboard vs. Commercial Billing** — **Operational Distinction:** The sample florist order screen provides order fulfillment visibility, but is not a replacement for an external enterprise billing ERP.

---

## Related Documentation

- [Mobile Companion](companion.html) — Details on the Android app, Google Play release, and honesty gates.
- [Privacy-Preserving CRM](crm.html) — How customer relationships and reminders work without storing personal data.
- [Path B Case Study](path-b.html) — Journey tapes and customer shopping flows.
- [Architecture Blueprint](schema.html) — Core formula, 6 layers, and execution loop.
- [Framework Home](index.html) — Return to the overview.
