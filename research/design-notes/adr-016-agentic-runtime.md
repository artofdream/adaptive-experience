# Design note — Thin ADR-016 agentic runtime (#168)

status: accepted (2026-08-15)
for_issues: "#168 (ADR-016 agentic runtime scaffolding)"
affects: "platform agent tool-calling boundary; optional SupportService.lookup"
author: claude
date: 2026-08-15

> **Decisions (2026-08-15):**
> 1. First executable slice for [ADR-016](../../docs/06-adr/ADR-016-agentic-ai-boundary.md).
>    The Accepted docs ADR stays as-is.
> 2. `AgentRuntime` is fail-closed: only an explicit tool allowlist may run; unknown
>    tools, unknown arguments, filesystem/network/SQL names, and write side-effects
>    are rejected at construction or invoke.
> 3. Reference path is one Support/Concierge **read** tool,
>    `lookup_approved_knowledge`, which calls `SupportService.lookup` (approved
>    knowledge, optional `RetrievalService` after a keyword miss). It does **not**
>    call `answer()`, so it neither persists nor publishes `support.faq.answered`.
> 4. Live `POST .../support` remains the deterministic FAQ path. The agent runtime
>    is not wired into `InternalOrchestrationApp`.

## Model

- **`ToolSpec`**: name, description, handler, allowlisted argument keys, `side_effect="read"`.
- **`AgentRuntime.invoke(tool, arguments)`**: validates the name against the
  allowlist, bounds argument keys/values, runs the handler, and returns a
  non-authoritative `ToolResult`.
- **`reference_concierge_runtime()`**: registers only `lookup_approved_knowledge`.
  Retrieval hits stay candidates (ADR-015); approved answer text is used, never
  the snippet. Similarity rank is never business truth.
- The runtime does not receive DB credentials for orders, payments, inventory,
  or experience-state tables. No new Kafka topics.

## Local / CI

Unit tests in `platform/tests/test_agent.py` do not need Docker. Platform
integration is unchanged (no schema or topic).

## Deferred

- Production model vendors and live LLM tool-calling loops
- Multi-agent orchestration
- Plan-preparation / consequential-write tools (ADR-013 confirmation)
- FR-006 human escalation (separate branch)
- Recommendation history FR-008, broader automated status answers FR-010
- Wiring the runtime into `InternalOrchestrationApp` or the browser BFF
- Live PSP or CRM
