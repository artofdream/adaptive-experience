# ADR-007 — Initial Deployment Topology

Status: Accepted

Date: 2026-08-11

Related requirements: NFR-003, NFR-004, NFR-014

Related architecture: [Technical Architecture](../04-technical-architecture/technical-architecture.md)

## Context
The target architecture defines an experience-oriented, asynchronous system
with an Adaptive UI Workspace, AI Floral Concierge, Experience Orchestration
Engine, Central Message Bus, shared experience-state store, and authoritative
domain services for Catalog, Inventory, Recommendation, Pricing, Delivery,
Order, and Payment.

Those elements require clear ownership and interaction boundaries, but the
architecture does not require every logical element to be deployed as an
independent service from the start. Immediate distribution would introduce
network failure modes, cross-service operations, deployment coordination, and
additional observability demands before the MVP has established evidence that
independent scaling or isolation is necessary.

The initial topology must support the MVP availability and response-time goals
(NFR-003, NFR-004) while leaving room for future AI model enhancements without
major redesign (NFR-014).

## Decision Drivers
- Preserve the ownership and authority boundaries defined by the technical
  architecture.
- Minimize avoidable distributed-system and operational complexity for the MVP.
- Support reliable local development, testing, deployment, and diagnosis.
- Avoid coupling that would prevent a logical module from being extracted when
  there is evidence that independent deployment is warranted.
- Permit AI implementations to evolve behind a stable Concierge boundary.

## Considered Options

### Option A — Independently deployed services from the outset
Deploy orchestration, Concierge, and every authoritative domain service as
separate processes with networked communication.

This maximizes deployment independence but adds network, consistency,
observability, and operational complexity before the MVP demonstrates a need
for it.

### Option B — Unstructured monolith
Implement the MVP as one application without enforced internal module and
ownership boundaries.

This is initially simple, but it weakens authority boundaries, encourages
shared mutable state, and makes later extraction costly and risky.

### Option C — Modular monolith with explicit logical boundaries
Deploy one backend application initially while retaining explicit modules,
owned state, governed contracts, and dependency rules for orchestration,
Concierge, and each authoritative domain capability.

This reduces initial operational complexity while preserving a path to
independent deployment.

## Decision
The MVP backend will be deployed initially as a **modular monolith**.

The Experience Orchestration Engine, AI Floral Concierge, Catalog, Inventory,
Recommendation, Pricing, Delivery, Order, and Payment remain distinct logical
modules within the deployable application. Each module owns its domain logic
and authoritative state. Modules interact only through explicit application
interfaces and governed message contracts; they must not reach into another
module's internal implementation or persistence representation.

The Adaptive UI Workspace is deployed separately and communicates through a
separately deployed **Backend-for-Frontend (BFF)**. The BFF owns browser-facing
transport concerns: session and cookie handling, CSRF protection, request and
response shaping, UI-specific aggregation, streaming connections, and
least-data workspace projections.

The BFF does not own experience state, context versions, workflow decisions,
selective regeneration, or domain rules. Those remain owned by the Experience
Orchestration Engine. Catalog, Inventory, Recommendation, Pricing, Delivery,
Order, and Payment remain authoritative for their business facts. The BFF may
aggregate and relay authorized results, but it must not reinterpret or replace
their authority.

The MVP also includes an **external message broker** as the concrete Central
Message Bus, even while backend modules share one application process. The
broker initially needs only the basic capabilities required for asynchronous
publication, subscription, durable delivery, and recoverable retry behavior.
Governed MVP topics cross the broker boundary; purely local implementation
details may use in-process calls when they are not published domain messages.

The broker product and its advanced operational capabilities are selected
separately. Whatever product is chosen must preserve the published contracts
and delivery semantics so that a module can later move across a process
boundary without changing its domain meaning.

An individual module will be considered for extraction only when measured
evidence identifies at least one material need for:
- independent scaling or materially different resource characteristics;
- stronger security, compliance, or fault-isolation boundaries;
- independent ownership or release cadence;
- availability requirements that cannot be met by the shared deployment; or
- technology specialization that cannot reasonably be contained behind the
  module interface.

Extraction remains a separate architectural decision and is not automatic when
one trigger appears.

## Rationale
A modular monolith provides the shortest operational path to validating the
MVP while retaining the authority boundaries at the heart of the architecture.
It avoids treating deployment boundaries as domain boundaries and allows the
team to gather production evidence before accepting distributed-system costs.
Stable module interfaces also allow the Concierge and its underlying AI model
to evolve without redesigning authoritative domain services (NFR-014).

## Consequences

### Positive
- One backend release and runtime simplify MVP deployment, rollback, local
  development, and end-to-end diagnosis.
- In-process calls can reduce avoidable latency for standard interactions,
  supporting NFR-004.
- Explicit module ownership preserves the documented authority boundary and a
  future extraction path.
- The BFF gives the Adaptive UI a stable, browser-appropriate contract and
  centralizes session, streaming, and minimum-data projection concerns.
- The external broker validates message contracts and asynchronous behavior
  against a real process boundary from the beginning.
- Common operational controls can be established once for the initial backend.

### Negative
- A backend failure or deployment can affect multiple logical modules, so the
  shared runtime has a larger failure domain.
- Modules cannot initially scale or release independently.
- The separately deployed BFF adds another availability, deployment,
  observability, and network boundary.
- The broker adds infrastructure, local-development, monitoring, and failure
  handling work even before services are deployed independently.
- Boundary discipline requires automated enforcement because process isolation
  does not enforce it.

### Risks
- Convenience may lead to direct cross-module persistence access or shared
  domain models, creating an unstructured monolith.
- A resource-intensive Concierge or Recommendation workload could impair other
  modules and threaten NFR-003 or NFR-004.
- Premature extraction could reproduce the complexity this decision seeks to
  defer.
- The BFF could become a second orchestration layer if workflow or domain logic
  is allowed to accumulate there.

## Implementation Constraints
- Each logical module has an explicit public interface and keeps its internal
  domain types and persistence details private.
- The Adaptive UI calls the BFF rather than authoritative domain modules or the
  infrastructure broker directly.
- The BFF may authenticate browser sessions, aggregate authorized responses,
  shape workspace projections, and relay streaming updates. It must not own or
  mutate canonical experience state except through Orchestration commands.
- Workflow sequencing, dependency evaluation, context-version increments, and
  selective regeneration remain exclusive responsibilities of Orchestration.
- Authoritative data remains owned by the module identified in the technical
  architecture; shared tables must not create shared authority.
- Cross-module dependencies must be visible and directed. Cyclic module
  dependencies are prohibited.
- Governed message envelopes and payload contracts must not depend on in-process
  object identity or implementation-specific types.
- Published MVP topics must traverse the external broker; modules must not
  replace broker publication with an in-memory-only event mechanism.
- Broker unavailability and redelivery must be treated as recoverable operating
  conditions rather than silently dropping messages.
- The Concierge accesses business facts through authoritative module interfaces
  and is never their system of record.
- Resource use, latency, errors, and availability must be observable per logical
  module even though modules share a runtime.
- Deployment configuration must allow high-cost or failure-prone adapters,
  especially AI providers, to be isolated or replaced behind module interfaces.

## Verification
- Architecture tests fail on unauthorized module imports, cyclic dependencies,
  and direct access to another module's persistence implementation.
- Contract tests exercise every cross-module public interface and governed
  message boundary.
- Integration tests publish and consume representative MVP topics through the
  external broker, including broker restart and redelivery scenarios.
- End-to-end tests demonstrate the documented authority boundary for
  customer-visible facts.
- Boundary tests fail if the BFF implements domain validation, advances a
  workflow independently, increments a context version, or bypasses
  Orchestration to mutate experience state.
- Browser integration tests cover session security, CSRF protection,
  least-data projections, aggregation, and reconnectable streaming through the
  BFF.
- Load and resilience tests report latency, error rate, and resource use by
  logical module and test the NFR-003 and NFR-004 targets.
- An extraction exercise or documented seam review confirms that at least one
  representative module can move behind a process boundary without changing
  its domain contract.
- AI adapter replacement tests demonstrate that model enhancement does not
  require redesign of authoritative domain modules (NFR-014).

## Revisit Conditions
Revisit this decision when production evidence shows that a module needs
independent scaling, isolation, ownership, release cadence, or technology; when
the shared runtime prevents NFR-003 or NFR-004 from being met; or when security
or compliance obligations require a separate process or data boundary.

Any revision must compare the measured benefit of extraction with its added
network, consistency, deployment, observability, and operational costs.
