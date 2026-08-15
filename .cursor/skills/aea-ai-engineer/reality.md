# AEA AI reality (do not oversell)

Re-read these files if the claim might be stale. Do not describe scaffolds as
live customer behavior.

## Intent (the only optional LLM path)

- `platform/aea_platform/generative_ai.py` —
  `OpenAICompatibleIntentInterpreter` (JSON facet extract, timeout ≤ 2.5s)
  wrapped by `AvailableIntentInterpreter` (threshold 3, recovery 30s).
- `platform/aea_platform/internal_runtime.py` — primary is constructed only
  when `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` are **all**
  set. Partial env fails closed at process start. Otherwise
  `InternalOrchestrationApp` uses `ReferenceIntentInterpreter` (regex in
  `intent.py`).
- Fallback / reference still returns facets + suggestions so conversation
  continues (NFR-003).
- Projections always include `ai_generated`, `assistant_mode`
  (`primary` / `fallback` / `reference`), and disclosure
  `"AI-generated interpretation; review and correct before ordering."`
  even when the regex path ran. Honesty work is making disclosure match
  mode (NFR-005), not removing disclosure from primary LLM output.

Health: `GET /internal/v1/ai/health`. Edge SLO:
`edge/scripts/check_assistant_slo.py`.

## Not AI (live)

| Surface | What it actually is |
|---|---|
| T-03 recommendations | `RecommendationService` ranks `REFERENCE_CATALOG` (5 SKUs) by intent overlap + price; inventory must be `available`. FR-007. FR-008 not implemented. |
| T-01 conversation log | `ConversationService` stores **customer** messages. Static “Hello! …” is HTML chrome. No generative assistant replies in-stream. |
| ASO `POST /support` | `SupportService` keyword match on `REFERENCE_KNOWLEDGE`. Unmatched → safe no-approved-information string. Never fabricate. |
| FR-010 | Token/session-fact answers (`kind=situation`). Not an LLM. |
| FR-012 `/florist` forecasts | `InventoryForecastService` trends from validated snapshot history. Operator-facing. Not a demand model. |
| T-04…T-08, payment | Domain services + confirmation (ADR-013). Agents must not silent-submit. |

## Scaffolds (exist, not on the live request path)

| Piece | Where | Live wiring |
|---|---|---|
| `AgentRuntime` | `platform/aea_platform/agent.py` | Fail-closed allowlist; reference tool `lookup_approved_knowledge`. **Not** constructed in `InternalOrchestrationApp`. Does not serve `POST /support` or T-03. Must not persist/publish FAQ events. |
| `RetrievalService` | `platform/aea_platform/retrieval.py` + migration `013_retrieval_pgvector.sql` | Hybrid candidates. `SupportService` *may* take a retriever after keyword miss, and only if the hit has keyword/FTS rank **and** maps to approved knowledge. Live app **does not pass a retriever**. |

ADR-015: similarity is never business truth. ADR-016: agent prepares; services
execute; tool results `authoritative=False`.

## Customer-pain mapping (prioritize these over scaffolds)

| Pain | Likely owner | Not an LLM catalog job |
|---|---|---|
| Send fails / csrf_rejected | security/edge (`!165` / `#171`) | unless asked to own session+AI boot |
| Intent summary never updates | intent interpreter / T-02 projection | |
| Disclosure says AI while mode is fallback/reference | NFR-005 honesty (this skill + UX copy if wording) | |
| Empty T-03 | inventory seeder / FR-007 ranking / availability fail-closed | do not invent LLM products |
| Help answers nonsense | keyword FAQ / approved knowledge | do not free-generate policy |

## Docs to cite (existing IDs only)

- FR-004, FR-005, FR-007, FR-008 (Future), FR-009, FR-010 (thin), NFR-003,
  NFR-004, NFR-005, NFR-006
- ADR-001, ADR-003, ADR-015, ADR-016
- `docs/04-technical-architecture/nfr-003-availability.md`
- `research/design-notes/adr-016-agentic-runtime.md`
- `research/design-notes/pgvector-rag-scaffold.md`
- `platform/README.md` (thin RAG / thin agent paragraphs)

## Tests that pin honesty

- `platform/tests/test_generative_ai.py` — fallback + circuit
- `platform/tests/test_agent.py` — fail-closed tools
- `platform/tests/test_support.py` — keyword first; retriever optional
- `platform/tests/test_retrieval.py` — hybrid candidates
- `edge/tests/test_browser_ui.py` — `#disclosure` copy if you change it
