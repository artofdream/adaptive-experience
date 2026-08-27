# Session Memory Log: Issue #270 Anthropic / LiteLLM 2.0s Timeout Remediation & CF-049 Verification

> **Tags**: #aea #issue-270 #cf-049 #litellm #anthropic #timeout #nfr-003 #adr-016 #second-brain
> **Captured**: 2026-08-27
> **Issue**: #270
> **Coherence Finding**: CF-049 (Verified)
> **Owners to inherit**: @aea-ai-engineer, @aea-devsecops-platform, @aea-performance-guardian, @aea-coherence-guardian, @aea-knowledge-guardian

---

## 1. Issue Background & Remediation (#270)

Issue **#270** flagged that Path B live intent interpretation degraded to local reference fallback whenever Anthropic API responses returned at ~2.048s.

Investigation revealed that while `OpenAICompatibleIntentInterpreter` enforces an NFR-003 SLA upper boundary of **&le; 2.5s**, `request_timeout` in `edge/litellm.yaml` and default `AEA_AI_TIMEOUT` in `platform/aea_platform/internal_runtime.py` were hardcoded to **2.0s**. Requests taking between 2.0s and 2.5s were prematurely aborted at the 2.0s threshold.

### Technical Remediation & Trade-Offs

- **Single Source of Truth Alignment**: Updated `litellm_settings.request_timeout` from `2` to `2.5` seconds in `edge/litellm.yaml` (which Terraform embeds directly into the Path B ECS task definition).
- **Runtime Default**: Updated default `AEA_AI_TIMEOUT` in `internal_runtime.py` and `OpenAICompatibleIntentInterpreter` constructor in `generative_ai.py` from `2.0` to `2.5` seconds.
- **SLA Boundary Guarantee**: The strict NFR-003 SLA upper bound (`if timeout_seconds > 2.5: raise ValueError`) remains intact and uncompromised.

---

## 2. Coherence Finding CF-049 Verification

- Updated `research/coherence-findings-loop.md` row 49 (CF-049) status from `queued` to **`verified`**.
- Confirmed performance metric output honesty in `scripts/audit_lcp_performance.py` accurately reporting `[NETWORK TTFB FLOOR]` and noting that full Web Vitals LCP requires headless Chrome paint timing traces.

---

## 3. Verification Results

- Platform Unit Tests: 247 Passed
- Edge Unit Tests: 69 Passed
- Coherence Check: Passed
- Pre-Flight Quality Guards: 14/14 Passed
