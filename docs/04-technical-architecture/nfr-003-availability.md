# NFR-003 Assistant Availability

Status: Accepted (MVP reference availability)

Requirement NFR-003: The AI assistant shall maintain 99.5% availability.
Traceability: EP-002 -> NFR-US-003 -> NFR-003. Customer intent: the assistant is
available whenever help is needed, including outside business hours.

## Availability design

The assistant maintains availability by always returning a usable result.
`AvailableIntentInterpreter` wraps a provider-neutral primary
(`OpenAICompatibleIntentInterpreter`) and a deterministic local fallback
(`ReferenceIntentInterpreter`):

- On success, the primary result is used (`mode = primary`).
- On any provider failure, timeout, or invalid output, it degrades to the local
  fallback (`mode = fallback`) and still returns a valid interpretation, so
  conversation and thought completion remain available even when the provider is
  down or outside business hours.

Because the fallback is deterministic and in-process, the assistant never fails to
respond: availability is bounded below by the local path, not the provider.

## Circuit breaker (bounded failures + recovery)

- After `failure_threshold` consecutive provider failures the circuit opens for
  `recovery_seconds`, during which the provider is skipped and the fallback serves
  requests - this bounds failure amplification and latency.
- After the recovery window the primary is retried; a success closes the circuit
  and restores `mode = primary`.

## Health and observability

`GET /internal/v1/ai/health` reports `{available, mode, circuit}`; `available` is
always true because the fallback guarantees a response. The mode and circuit make
degradation observable (NFR-016). AI response quality and error counts for the
live intent and FAQ paths are on `GET /internal/v1/ai/quality` (NFR-008 first
slice; see [nfr-008-quality-monitoring.md](nfr-008-quality-monitoring.md)).

## Latency bound (NFR-004 related)

The primary provider call uses a capped timeout (<= 2.5s) so a slow provider
degrades to the fallback rather than blocking. The edge SLO guard
(`edge/scripts/check_assistant_slo.py`) measures standard-query p95 against the
3s budget in the container integration path.

## Verification

- `platform/tests/test_generative_ai.py`:
  - fallback keeps the assistant available and opens the circuit under failure;
  - the circuit recovers and closes when the provider returns;
  - under total provider failure, 200/200 requests succeed via the fallback -
    measured availability 100%, above the 99.5% target.
- `edge/scripts/run_integration_tests.py` reports the "24/7 assistant analysis and
  fallback path is healthy" and the assistant SLO on the deployed reference stack.

## Scope

These are the MVP reference availability controls. Production availability
targets under representative load and deployment redundancy are exercised in the
performance/availability hardening pass (#152) and reference deployment validation
(#150); this note establishes the mechanism and its measured behavior.
