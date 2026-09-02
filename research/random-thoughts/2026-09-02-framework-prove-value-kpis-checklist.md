# Framework: prove value checklist (florist & other verticals)

> **Tags**: #aea #second-brain #framework #kpis #florist #honesty #companion
> **Captured**: 2026-09-02
> **Owners**: `@aea-product-owner` / agents
> **This node is knowledge, not product code.**

**Opening principle:** *A framework is only as good as it matches needs in reality.*

Docs, architecture diagrams, ADRs, and “framework” pages without a **named real need** and a **measurable journey fit** are not framework value. They are inventory. If the framework does not match needs in reality, it must **evolve** to match those needs (with measurable proof) or be **discarded**. Do not keep zombie patterns, docs, or ADRs that fail the need→journey→telemetry test.

**Success criterion:** *Works in production-like reality for a named need* > *agents collaborate more elegantly.* Improvement for agentic workflows is nice; the goal is that the framework stays valid when applied in real life (Lily's Florist and other implementations). Agentic sophistication without field-valid application does not count as success.

---

## Purpose

How to demonstrate Adaptive Experience Architecture value with **measurable proof** — not prettier docs. Lily's Florist is the reference vertical; the checklist is reusable for other verticals.

Related vault: [[2026-09-02-native-client-validation-alternatives]] · [[2026-09-02-companion-native-web-gap-closing-loop]] · [[2026-09-02-play-api-ci-upload-closed-testing]]. Companion README: `clients/mobile/android/README.md`. Public twin: [architecture.artof.link/companion](https://architecture.artof.link/companion).

---

## Prove-value checklist (do in order)

### 0. Reality gate (before anything else)

- [ ] Named real need exists in stakeholder language (not only in our docs)
- [ ] Measurable journey fit exists (path in product + how we will know it worked)
- [ ] Pattern still earns its place **OR** scheduled for removal/supersede
- [ ] Success bar is field-valid application for the named need — not agentic elegance alone

If any of these fail: stop claiming framework value. Evolve with proof, or discard.

### A. Anchor the need

- [ ] Stakeholder names the pain in their words (florist or buyer)
- [ ] Map pain to a journey (Need→Pick→Pay / staff path), not only an essay
- [ ] Pick ONE golden journey for the demo window (e.g. Mom's Birthday → classic dozen + delivery)

### B. Sensors before claims

- [ ] Baseline: time-to-order, completion, corrections/409s (even manual counts OK)
- [ ] Choose honesty channel: App Dist for UX speed; Play internal when claiming store install
- [ ] Confirm operator sink (workspace/tracking) ≠ Contact Florist inbox alone
- [ ] Note native vs web twin URL if comparing (architecture.artof.link/companion)

### C. Run the proof

- [ ] Execute golden journey on the chosen channel
- [ ] Record outcome: accepted order?, staff-visible?, corr ids
- [ ] Run or cite companion-bff-parity-probe if API parity is part of the claim
- [ ] Capture before/after on ONE pain (budget, total+fee, Start Over, etc.)

### D. KPI board (minimum set)

| Layer | KPIs (measure these) | Vanity to skip |
| --- | --- | --- |
| **Customer** | checkout completion; time-to-order; correction/409 rate; empty Pick rate | page views; AI messages sent |
| **Shop** | staff-visible within N min; manual re-key rate; mis-pick rate | roadmap % |
| **Platform** | `aea_client` native vs web volume+errors; parity probe streak; Play vs App Dist honesty | — |
| **Learning** | findings closed/week; pain→testable-build latency | — |

### E. Framework vs reality gates

- [ ] Need exists in stakeholder language
- [ ] Path exists in product
- [ ] Telemetry agrees — if not, fix brief/stack/companion honesty, don't force the claim
- [ ] Pattern still earns its place OR scheduled for removal/supersede

### F. Evolution loop

- [ ] Each change names the KPI it should move
- [ ] Dual-probe / parity / App Dist / Play treated as sensors
- [ ] Vault/daily-brief records what was proven
- [ ] Promote pattern to "framework" only after one vertical shows numbers

### G. AI-augmented bar (honest)

AI adds value only if it beats non-AI baseline on:

- faster intent→SKU
- better constrained choice (budget/occasion/stock)
- recovery (stale/wrong total/sold-out)
- later: operator assist when staff path is real

If completion / time-to-order / corrections don't move, AI is decoration.

---

## Evolve or discard

When need→journey→telemetry fails:

1. **Evolve** — change the pattern/doc/ADR so it matches the named need; ship the smallest proof that the KPI moved.
2. **Discard** — supersede or remove zombie inventory; do not leave failed claims labeled as framework.

Keeping unmatched docs “for later” without a removal/supersede date is how frameworks rot. The §0 and §E gates include: **pattern still earns its place OR scheduled for removal/supersede.**

---

## Pointers

- Vault: [[2026-09-02-native-client-validation-alternatives]], [[2026-09-02-companion-native-web-gap-closing-loop]], [[2026-09-02-play-api-ci-upload-closed-testing]]
- Companion README: `clients/mobile/android/README.md`
- Architecture /companion: https://architecture.artof.link/companion
- Impact measurement sibling: [[2026-08-22-ai-user-impact-measurement-framework]]

---

## Honesty

- App Dist ≠ Play.
- Parity green ≠ UX.
- Probe ≠ dual-probe write-through.
- Don't claim production florist rollout from internal testing alone.
- **A framework is only as good as it matches needs in reality** — docs without need + journey fit are not proof; unmatched patterns evolve with numbers or get discarded.
- Field-valid application for a named need beats elegant agentic workflow. If it does not work in production-like reality, it is not framework success.
