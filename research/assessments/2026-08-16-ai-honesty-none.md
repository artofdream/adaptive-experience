# AI honesty — no remaining MVP code gap — 16 Aug 2026

tags: #aea #ai-engineer
status: none — stop
assessed_ref: `4521f6d` on `origin/main`
assessed_by: aea-ai-engineer
assessed_at: 2026-08-16T02:05 Europe/Paris

## Verdict

**None.** No true MVP honest-AI *code* gap remains that is not NFR-014
pluggability, not UX currency (#181), and not FR-008. Did not open an issue
or MR. Did not start scaffold wiring.

## Live probe (did not rebuild Compose)

`https://localhost:8443/healthz` → `200 {"status": "ok"}`.

Orchestration `/internal/v1/ai/health` is not published on the host; did not
`docker compose exec` (DevSecOps is rebuilding). Inferred from Edge payloads
on a fresh session:

| Surface | `assistant_mode` | `ai_generated` | Disclosure | Honest? |
|---|---|---|---|---|
| `GET` shared-understanding (empty) | `fallback` | false | Automated interpretation… | yes |
| `GET` workspace (empty) | `fallback` | false | same | yes |
| `POST` conversation (202) | `fallback` | false | same | yes |
| After “birthday roses for Mum under 75” | `fallback` | false | same | yes |

Intent facets came from the deterministic interpreter (occasion / recipient /
flower_preference). T-03 returned five ranked SKUs with availability only —
no AI-ranking field. `POST /api/v1/support` returned a keyword FAQ hit
(`policy:delivery`); payload does not mention AI.

`mode: fallback` (not `reference`) means `AvailableIntentInterpreter` is
constructed — `AEA_AI_*` are set — and the last primary call degraded. That
is NFR-003, not a false AI claim. `available: true` on health remains
“fallback always answers,” not proof a provider is live.

## Code vs docs (re-checked)

- **Intent env + circuit** — `internal_runtime.py` still requires
  `AEA_AI_ENDPOINT`, `AEA_AI_API_KEY`, and `AEA_AI_MODEL` together; else
  `ReferenceIntentInterpreter`. `AvailableIntentInterpreter` still wraps
  primary with threshold 3 / 30s recovery. Did not edit
  `platform/aea_platform/generative_ai.py` (#56 / NFR-014).
- **T-02 disclosure vs `assistant_mode`** — `disclosure_for_mode` claims
  “AI-generated” only for `primary`. BFF passes the triple through. Live
  fallback payloads match. Tests:
  `platform/tests/test_generative_ai.py`,
  `edge/tests/test_perimeter.py`
  (`test_workspace_passes_through_fallback_disclosure_without_claiming_ai`).
- **No AI claim on fallback / reference** — live disclosure is
  `Automated interpretation; review and correct before ordering.`
- **No ranking-as-AI** — `RecommendationService` remains FR-007 overlap +
  price. T-03 chrome is “Curated Recommendations.”
- **T-01** — customer messages only; static hello is UI chrome.
- **ASO** — keyword FAQ + FR-010 session facts. Help copy: “Automated
  answers from approved shop information. This is not a person.”
- **AgentRuntime / RetrievalService** — still scaffolds, not on the live
  `POST /support` or T-03 path. Not honesty bugs.

## Not this gap (left parked)

- Static `#disclosure` HTML default and “AI assistant” chrome in
  `edge/gateway/ui/` — UX-owned; #181 currency this cycle.
- #56 / NFR-014 adapter pluggability — senior software engineer.
- #27 / FR-008 history recs — not next; did not start.
- CRM #35/#36. AWS stays parked. Did not merge.

## Why none

The honesty contract is the payload triple matching the interpreter that
actually ran. That contract holds on the live shop and in the tests that pin
it. Remaining “AI” wording is either UX chrome, a Future FR, or an unused
scaffold. Restoring `primary` is an ops/provider question, not a disclosure
bug.
