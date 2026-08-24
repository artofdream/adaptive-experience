# AEA Pilot Deployment HLD and LLD

Status: architecture evidence view; not a deployment attestation

Related decisions: [ADR-007 Initial Deployment Topology](../06-adr/ADR-007-initial-deployment-topology.md),
[ADR-011 Experience-State Datastore](../06-adr/ADR-011-experience-state-datastore.md),
[ADR-012 MVP External Message Broker](../06-adr/ADR-012-external-message-broker.md),
[ADR-016 Agentic AI Boundary](../06-adr/ADR-016-agentic-ai-boundary.md)

This document details the AWS pilot and shows the local path only where a
side-by-side boundary comparison prevents ambiguity. The two
repository-supported execution paths are:

- **Path A — local reference:** Docker Compose on a developer machine.
- **Path B — `aea-pilot`:** the AWS topology declared in `infra/aws/`, built
  and deployed from GitLab CI.

It does not assert that Terraform has been applied or that a live endpoint is
healthy. Applied-resource, bootstrap, DNS, certificate, secret, alarm, and
end-to-end evidence must be recorded separately by the operator.

## Evidence-status legend

| Marker | Meaning |
|---|---|
| **Implemented** | Executable application, Compose, script, test, or CI behavior exists in the repository. |
| **IaC-defined** | Terraform declares the resource or control, but this document has no independent proof that the resource exists in AWS. |
| **Operationally pending** | Requires operator action or evidence from a reachable deployment target. |

## High-level design

Both paths preserve the ADR-007 boundary: the browser enters through the
gateway, the separately deployed BFF owns browser transport, and the modular
monolith owns orchestration and authoritative domain behavior. The browser
never connects directly to PostgreSQL or Kafka. Kafka is the external broker
selected by ADR-012; PostgreSQL remains authoritative state rather than Kafka.

```mermaid
flowchart LR
  user["Customer or florist browser"]

  subgraph local["Path A — separate local profiles (Implemented)"]
    subgraph localEdge["Edge Compose browser profile"]
      lg["Gateway / static UI<br/>self-signed HTTPS :8443"]
      lb["BFF<br/>HTTP :8080, container-only"]
      lo["Modular monolith<br/>HTTP :8081, container-only"]
      lp[("PostgreSQL 16 + pgvector<br/>ephemeral Edge data")]
      seed["Local inventory seeder"]
      lg -->|"HTTP, private Compose network"| lb
      lb -->|"Bearer-authenticated HTTP"| lo
      lo --> lp
      seed --> lp
    end
    subgraph localPlatform["Platform integration profile"]
      runner["Host integration runner<br/>migrations, relay, consumers"]
      lpp[("PostgreSQL 16 + pgvector<br/>named test volume")]
      lk[("Kafka 3.9.1 KRaft<br/>PLAINTEXT, single node")]
      runner --> lpp
      runner -->|"governed outbox/topic tests"| lk
    end
  end

  subgraph aws["Path B — AWS VPC (IaC-defined)"]
    alb["Public ALB + ACM<br/>HTTPS :443"]
    pgw["Gateway ECS Fargate<br/>HTTP :8080"]
    pb["BFF ECS Fargate<br/>HTTP :8080"]
    po["Orchestration + workers<br/>ECS Fargate"]
    pr[("RDS PostgreSQL 16<br/>encrypted, private")]
    pm[("MSK Kafka 3.9.x<br/>TLS + SASL/SCRAM, private")]
    ai["LiteLLM ECS + Cloud Map<br/>private :4000"]
    sm["Secrets Manager"]
    cw["CloudWatch logs"]
    alb --> pgw --> pb --> po
    po --> pr
    po -. "SASL_SSL" .-> pm
    po --> ai
    sm -. "task secret injection" .-> pb
    sm -. "task secret injection" .-> po
    sm -. "task secret injection" .-> ai
    po -. "runtime logs" .-> cw
  end

  user -->|"https://localhost:8443"| lg
  user -->|"https://aea.artof.link<br/>(pending live evidence)"| alb
```

## Path A — local low-level design

### Components and boundaries

```mermaid
flowchart TB
  browser["Browser"]
  host["Developer host"]

  subgraph compose["edge/docker-compose.yml — private Compose network"]
    gateway["gateway<br/>published 8443:8443<br/>ephemeral self-signed TLS"]
    bff["bff<br/>expose 8080 only<br/>session, CSRF, origin, projections"]
    orch["orchestration<br/>8081 only<br/>modular monolith"]
    seed["inventory-seeder<br/>AEA_ENVIRONMENT=local"]
    db[("postgres<br/>pgvector/pgvector:pg16")]
    gateway -->|"HTTP :8080"| bff
    bff -->|"HTTP :8081<br/>internal bearer"| orch
    orch -->|"PostgreSQL :5432"| db
    seed -->|"PostgreSQL :5432"| db
  end

  subgraph platform["platform/docker-compose.yml — broker integration fixture"]
    pdb[("PostgreSQL :5432<br/>host-published")]
    kafka[("Kafka :9092<br/>host-published, PLAINTEXT")]
  end

  browser -->|"HTTPS :8443"| gateway
  host -. "integration runners" .-> pdb
  host -. "topic provisioning / tests" .-> kafka
```

The edge Compose stack exercises the customer-facing path and starts migrations
before orchestration. It enables the local-only inventory seeder and the local
florist operator. The platform Compose stack supplies PostgreSQL and Kafka for
platform integration testing. They are related test fixtures, not one combined
production topology.

Local trust and protocol properties:

- Only gateway `:8443` is published by the edge stack; BFF and orchestration
  remain on the Compose network.
- Gateway terminates ephemeral self-signed TLS. Gateway-to-BFF and
  BFF-to-orchestration traffic is HTTP within the local container network.
- BFF requires the configured origin, browser bearer/session controls, CSRF
  controls on mutations, and an internal orchestration bearer.
- Local PostgreSQL credentials, the browser bearer, and the internal bearer are
  fixtures. They must not be copied to the pilot.
- Local Kafka is one KRaft broker using `PLAINTEXT`, RF=1 and MinISR=1. It tests
  contracts and delivery behavior, not production encryption or availability.
- The local PostgreSQL volume is not evidence for NFR-007 at-rest encryption.

### Local startup and request sequence

```mermaid
sequenceDiagram
  participant Op as Developer / test runner
  participant DB as PostgreSQL
  participant O as Orchestration
  participant S as Inventory seeder
  participant B as BFF
  participant G as Gateway
  participant U as Browser

  Op->>DB: docker compose starts database
  DB-->>O: health check passes
  O->>DB: apply_migrations.py
  O-->>B: orchestration health becomes ready
  S->>DB: seed_local_inventory.py --loop
  S-->>G: seeder health becomes ready
  B-->>G: /healthz becomes ready
  G-->>Op: HTTPS /healthz ready on :8443
  U->>G: HTTPS UI/API request
  G->>B: private HTTP
  B->>O: authenticated internal HTTP
  O->>DB: authoritative transaction + outbox
  O-->>B: synchronous acknowledgement/projection
  B-->>U: least-data browser response
```

## Path B — AWS pilot low-level design

### Network and runtime topology

```mermaid
flowchart TB
  internet["Internet"]
  dns["DNS: aea.artof.link<br/>(operator-managed)"]
  acm["ACM certificate<br/>(operator prerequisite)"]

  subgraph vpc["AEA VPC — two availability zones (IaC-defined)"]
    subgraph pub["Public subnets"]
      alb["Application Load Balancer<br/>HTTPS :443"]
      nat["NAT Gateway"]
    end

    subgraph priv["Private subnets"]
      gateway["gateway ECS service<br/>ALB mode, HTTP :8080"]
      bff["bff ECS service<br/>HTTP :8080"]
      orchestration["orchestration ECS service<br/>HTTP :8081"]
      relay["outbox relay ECS service"]
      consumer["workspace consumer ECS service"]
      livefeed["lily-reference-live-test<br/>30-second loop"]
      litellm["LiteLLM ECS service<br/>Cloud Map :4000"]
      rds[("RDS PostgreSQL 16<br/>encrypted, 7-day backup<br/>single-AZ pilot")]
      msk[("MSK Kafka 3.9.x<br/>2 brokers / RF=2 / MinISR=1<br/>TLS + SASL/SCRAM")]
    end
  end

  secrets["Secrets Manager<br/>app + MSK SCRAM"]
  logs["CloudWatch log groups<br/>ECS and MSK"]
  anthropic["Anthropic API"]

  internet --> dns --> alb
  acm -. "TLS certificate" .-> alb
  alb -->|"SG: ALB → gateway :8080"| gateway
  gateway -->|"SG: gateway → BFF :8080"| bff
  bff -->|"SG: BFF → orchestration :8081"| orchestration
  orchestration -->|"SG: orchestration → RDS :5432"| rds
  relay -->|"SASL_SSL :9096"| msk
  consumer -->|"SASL_SSL :9096"| msk
  relay --> rds
  consumer --> rds
  livefeed --> rds
  orchestration -->|"HTTP :4000, Cloud Map"| litellm
  litellm -->|"HTTPS egress via NAT"| anthropic
  secrets -. "ECS valueFrom" .-> bff
  secrets -. "ECS valueFrom" .-> orchestration
  secrets -. "ECS valueFrom" .-> relay
  secrets -. "ECS valueFrom" .-> consumer
  secrets -. "ECS valueFrom" .-> litellm
  msk -. "broker logs" .-> logs
  gateway -. "container logs" .-> logs
  bff -. "container logs" .-> logs
  orchestration -. "container logs" .-> logs
```

The security-group chain permits only ALB → gateway → BFF → orchestration
ingress at the application edge. RDS accepts `:5432` from the orchestration
security group. MSK accepts its configured SASL/TLS ports from that same group;
workers share it. LiteLLM accepts `:4000` only from orchestration. The current
Terraform security groups permit broad outbound traffic, routed from private
subnets through the NAT gateway.

The pilot declares two public and two private subnets across two availability
zones because the two-broker MSK cluster requires them. The RDS pilot is
encrypted but explicitly `multi_az = false`, has seven-day backup retention,
and has deletion protection disabled with final snapshot skipped. Those are
pilot trade-offs, not a production resilience baseline.

### Production-mode controls and the named pilot exception

All application task definitions use `AEA_ENVIRONMENT=production`. Therefore:

- the local inventory seeder must fail closed and `AEA_SEED_INVENTORY` must not
  be set;
- generic production keeps florist operator routes at 404;
- only prefix `aea-pilot` sets both `AEA_FLORIST_OPERATOR=1` and
  `AEA_FLORIST_OPERATOR_EXCEPTION=aea-pilot` on the BFF;
- the exception exposes the read-only T-09 inbox only. It neither writes
  inventory nor unblocks T-03 Select;
- the named `lily-reference-live-test` service, not the local seeder, refreshes
  the five reference SKUs through the inventory service every 30 seconds.

The browser fixture bearer must match the UI value, but the live secret is
operator-merged into the existing Secrets Manager JSON object. Replacing the
whole secret risks dropping database, Kafka, or AI keys. AI credentials remain
behind private LiteLLM; orchestration receives only the proxy endpoint, proxy
bearer, and model together.

### Terraform, secret and bootstrap sequence

```mermaid
sequenceDiagram
  participant Sponsor as Sponsor
  participant D as DevSecOps operator
  participant TF as Terraform
  participant AWS as AWS control plane
  participant SM as Secrets Manager
  participant ECS as ECS RunTask / services
  participant RDS as RDS PostgreSQL
  participant MSK as MSK Kafka

  Sponsor->>D: provide ACM/DNS inputs, GitLab variables and secret values
  D->>TF: init, plan, review, apply
  TF->>AWS: create VPC, ALB, ECR, ECS, RDS, MSK, IAM/OIDC
  AWS-->>D: outputs (role, repos, cluster, URL, endpoints)
  Sponsor->>SM: merge browser and AI keys without replacing secret blob
  D->>ECS: run apply_migrations.py
  ECS->>RDS: apply migrations twice to prove idempotence
  D->>ECS: run provision_kafka.py with pilot replication profile
  ECS->>MSK: create governed topics (RF=2, MinISR=1)
  D->>ECS: render and apply least-privilege ACL plan
  ECS->>MSK: apply ACLs to SCRAM principals/groups
  D->>ECS: verify relay, consumer and live-feed services RUNNING
  D->>ECS: diagnose pending outbox and AI health
```

Terraform apply and bootstrap are operator activities. DNS changes, certificate
input, GitLab variable entry, and live secret values require sponsor handoff.
Neither the Scrum Master nor the GitLab deploy pipeline applies Terraform.

### GitLab build and deployment sequence

```mermaid
sequenceDiagram
  participant G as GitLab pipeline on main
  participant OIDC as GitLab OIDC
  participant IAM as AWS IAM deploy role
  participant ECR as ECR repositories
  participant ECS as ECS services
  participant ALB as Public ALB

  G->>OIDC: request ID token (audience https://gitlab.com)
  OIDC->>IAM: AssumeRoleWithWebIdentity<br/>main-project trust condition
  IAM-->>G: short-lived AWS credentials
  G->>ECR: build and push orchestration, BFF, gateway<br/>git SHA + latest
  G->>ECS: force new deployment<br/>orchestration, BFF, gateway, relay, consumer
  G->>ECS: wait for gateway and BFF stable
  G->>ALB: GET /healthz with retries
  ALB-->>G: HTTP 200 required
```

The CI path uses short-lived OIDC credentials and the Terraform-defined IAM
role; static AWS access keys are not part of the design. `resource_group:
path-b-ecs` serializes build/deploy activity. CI builds the pilot images and
pushes ECR tags; laptop-to-pilot image promotion is disallowed except for a
documented break-glass case.

The current `deploy-ecs` job refreshes orchestration, BFF, gateway, relay and
consumer-workspace. Terraform also declares LiteLLM and the reference live-test
service, but those two are not in this CI force-deploy loop; their rollout is
an operator step when their image or secret inputs change.

## Repository evidence and remaining gaps

| Concern | Repository status | Evidence still required |
|---|---|---|
| Local gateway/BFF/orchestration path | **Implemented** in `edge/docker-compose.yml` and edge integration tests | A successful run on the target workstation for the current commit. |
| Local PostgreSQL/Kafka integration | **Implemented** in `platform/docker-compose.yml` and platform integration runner | Local Compose proves behavior only; it does not prove cloud TLS, encryption, or HA. |
| AWS network, ALB, ECR, ECS, RDS, MSK, Secrets, OIDC | **IaC-defined** under `infra/aws/` | A reviewed Terraform plan and applied-state/resource inventory. |
| Public TLS and DNS | ALB HTTPS listener and ACM input are **IaC-defined** | Valid ACM certificate, DNS record, external TLS/hostname check. |
| RDS encryption and backups | `storage_encrypted=true`, seven-day retention are **IaC-defined** | AWS configuration evidence plus restore exercise. RDS is single-AZ in the pilot. |
| MSK transport and authentication | TLS + SASL/SCRAM, KMS-backed SCRAM secret, two brokers are **IaC-defined** | Live connection, topic configuration, ACL-denial, broker degradation and recovery evidence. Pilot RF=2/MinISR=1 is below ADR-012's preferred RF=3/MinISR=2 production baseline because the pilot has two brokers. |
| Migrations, topics and ACLs | Scripts and bootstrap procedure are **Implemented** | Successful in-VPC execution; second migration pass; ACLs applied to the real cluster. |
| GitLab cloud deploy | OIDC `build-ecr` and `deploy-ecs` jobs are **Implemented** | Successful main pipeline against configured AWS variables and an immutable SHA rollout record. |
| Secrets | Secrets Manager resources and ECS injection are **IaC-defined** | Operator confirmation that required keys exist, were merged safely, and no Compose fixture or raw secret entered git/CI logs. |
| Production flags | Task-definition settings and fail-closed code are **Implemented/IaC-defined** | Live negative tests for seeder and generic florist routes, plus positive read-only test for the named `aea-pilot` exception. |
| Observability | ECS/MSK CloudWatch log groups are **IaC-defined** | Retention review, dashboards, actionable alarms, trace correlation, and incident evidence. The deployment plan records 5xx/unhealthy-host alarms as post-pilot. |
| Availability and performance | Health checks and `/healthz` smoke are **Implemented** | Representative load, redundancy/failure exercises, SLO measurements, RDS restore, MSK recovery, and rollback evidence. |
| AI primary path | Private LiteLLM service and secret injection are **IaC-defined** | Live `/internal/v1/ai/health` showing `mode: primary`; no raw Anthropic key outside LiteLLM. |

## Acceptance evidence checklist

Before describing Path B as an operational pilot, retain evidence for:

1. reviewed Terraform plan and apply, with no secrets committed;
2. DNS and ACM validation for the canonical origin;
3. GitLab OIDC identity and least-privilege role assumption from `main`;
4. ECR images tagged with the deployed commit SHA;
5. idempotent migrations, governed topics, and applied Kafka ACLs;
6. running ECS services, drained outbox, healthy consumers, and CloudWatch logs;
7. external `/healthz`, authenticated browser journey, and exact-origin checks;
8. fail-closed production seeder and generic florist behavior, with the narrow
   `aea-pilot` operator exception verified separately;
9. RDS backup/restore, MSK degradation/recovery, deployment rollback, and the
   NFR-003/NFR-004 representative-load checks; and
10. CloudWatch alarms and operational ownership for 5xx, unhealthy targets,
    Kafka replication/lag, retry age, dead letters, and storage pressure.

Until those artifacts exist, Path B is accurately described as an
**IaC-defined pilot with operational evidence pending**, not a validated
production deployment.
