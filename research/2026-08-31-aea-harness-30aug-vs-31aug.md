> **Tags**: #aea #second-brain #harness #knowledge-first #kocer
> **Captured**: 2026-08-31
> **Draft status**: vault note (not canonical `docs/`)
> **Left**: 30 Aug PDFs / [[2026-08-30-aea-framework-harness-engineering]] + `research/2026-08-30-aea-harness-vs-wast3-memory-engineering.md`
> **Right**: [[2026-08-31-aea-framework-harness-engineering]] (Kocer five-floor rewrite on `docs/337-kocer-five-layers-harness-revision-clean`)
> **Also**: [[2026-08-31-aea-vs-kocer-five-layers-agent-engineering]]
> **GitLab**: #341 (this honesty pass) · #337 (PO comments 31 Aug; !358 paper close ≠ implement)

# 30 Aug harness (wast3 flags) vs 31 Aug harness (Kocer floors)

#aea

This note compares the versions in the 30 Aug PDFs to the **latest** playbook on this branch. It does not promote either into `docs/`. It does not start implementation.

## Sources

| Artifact | Path | What it is |
|---|---|---|
| 30 Aug playbook | `research/random-thoughts/2026-08-30-aea-framework-harness-engineering.md` | Proposed next version after a second read of [19]. Flag set I1–I15. Successor of 29 Aug. |
| 30 Aug comparison | `research/2026-08-30-aea-harness-vs-wast3-memory-engineering.md` | Same source as the open PDF. Honest adopt/adapt/defer/reject. |
| 31 Aug playbook | `research/random-thoughts/2026-08-31-aea-framework-harness-engineering.md` | Kocer [21] five concentric floors. Successor-of field still points at **29 Aug**, not 30 Aug. |
| 31 Aug vs Kocer | `research/random-thoughts/2026-08-31-aea-vs-kocer-five-layers-agent-engineering.md` | Related-work extract. Does not cite the 30 Aug flag paper. |

PDF exports of the 30 Aug pair live at `research/pdf-export/*-2026-08-30.pdf` (local only).

## What each revision is for

**30 Aug** is a **discipline pass**. Same formula, same six outer-harness layers. New work is the flag set and the honesty check that #289–#292 closed ≠ shipped.

**31 Aug** is a **taxonomy pass**. New work is Kocer’s wrapping floors (prompt → context → harness → loop → graph) plus three proposed runtime pieces (context curator, orthogonal reviewer, stack diagnostic sensor). Formula kept. Domain services still sit under the stack.

They are not the same kind of revision. 31 Aug does not replace 30 Aug’s flag table. 30 Aug does not contain Kocer’s nesting law.

## Side-by-side

| Dimension | 30 Aug (PDFs) | 31 Aug (latest playbook) |
|---|---|---|
| Related work | [19] 0xWast3 memory engineering | [21] Kocer five layers; [19] cited in the header only |
| Declared successor of | 29 Aug playbook | 29 Aug playbook (**skips 30 Aug**) |
| Outer shape | Six layers: guides, sensors, loop, memory, permissions, observability | Five floors wrapping the model; six layers listed as “kept” but not remapped row-by-row |
| Memory claim | Context ≠ memory; DATE_RE vs vault weight split (I1–I3 **adopt**, language only) | Floor 02 “Context Engineering” + “Negative Constraints Memory” + read-before/write-after |
| Corrections | I5 **adapt**: probe-gated line in the **owning** guide. I11 **reject**: new `CONSTRAINTS.md` | Floor 02 names negative constraints as part of the curator. No I11 refuse |
| Typed edges | I7 **adapt**, vault-only, not shipped | Drawn inside floor 05 as if `derived_from` / `constrains` / `verifies` are inventory |
| Reviewer | MRC hat merges; I8 **reject** LLM judge; I12 **reject** 300-agent swarm | Law 2: orthogonal **model instance** + fresh window. MRC / Duo / CI listed together |
| Path B honesty | [[CF-048]] verified; [[CF-054]] **regressed**; live [[J1]] after !300 Unknown | No Path B evidence section. Status words not restated |
| CF-055 | “Do not invent CF-055” = do not mint a contradiction finding | Listed as an existing vault ID next to CF-048 / CF-054 |
| PO gate | I4–I8 need accept on #337 before implement | Three runtime proposals “identified”; no adopt/adapt/defer/reject table |
| Length / role | Short successor; 28 Aug remains the long form | Short successor; 28 Aug still the long form |

## What 31 Aug adds that 30 Aug did not have

These are **advantages of the 31 Aug draft as ideas**. They are not Path B evidence.

1. **Harness vs loop vs graph is nesting, not a bake-off.** 30 Aug already refused a swarm (I12) and kept one-CF loop + MRC. It did not say the three names are floors of one stack. That sentence is worth keeping.
2. **Diagnose downward.** If floor 05 looks broken, inspect floor 02 first. Matches AEA “status word needs a probe,” aimed at layer skip rather than tracker honesty.
3. **Economic asymmetry.** Model swap via LiteLLM / [[ADR-016]] vs quarter-scale stack. 30 Aug implied this (I2, I15 reject weight training). 31 Aug names it.
4. **Domain services drawn under the floors.** Keeps the AEA differentiator that [19] and [21] both lack.

## What 31 Aug drops or overclaims vs 30 Aug

1. **Lineage skip.** Successor-of is still 29 Aug. I1–I15 are not imported. A reader of only 31 Aug can treat typed edges and constraints as already true.
2. **I11-shaped language.** “Negative Constraints Memory” in floor 02 is the file 30 Aug rejected unless it is a probe-gated line in an existing guide.
3. **I7-shaped inventory.** Floor 05 diagram lists typed edges as present. 30 Aug: convention proposed; graph-guard is still an ID sensor.
4. **Law 2 vs I8.** Independent review with a **fresh window** and a **different hat** is already MRC + required CI. An **orthogonal model family** as the merge verifier is the LLM-judge class 30 Aug rejected. Duo on the diagram is not a probe that Duo is the MRC hat.
5. **Path B silence.** [[CF-054]] **regressed** and live [[J1]] Unknown disappear. That is a [[CF-048]]-class omission if 31 Aug is treated as the current playbook.
6. **CF-055 collision.** CF-055 already exists as the public-framework glossary finding (`research/findings/CF-055-framework-glossary-undefined-terms.md`, queue `in-progress`, #300 / !331). It is **not** a contradiction-sensor CF. 28–30 Aug “do not invent CF-055” meant do not mint that second class. 31 Aug listing `[[CF-055]]` beside CF-048 / CF-054 without that distinction is sloppy, not a new ID.

## Honest flags on the 31 Aug deltas

| ID | 31 Aug claim | Flag | Why | Must not |
|---|---|---|---|---|
| K1 | Keep five-floor wrapping as a **map** of the outer harness | **adapt** | Clarifies names. Does not retire the six product layers or the 14 hats. | Do not replace MRC, DATE_RE, or domain services with a graph runtime. |
| K2 | Diagnose higher-floor failure by probing the floor below | **adopt** | Same honesty rule, aimed at layer skip. Language-only. | Do not add a sensor that skips `glab` / clip probes. |
| K3 | Model is commodity; stack is IP | **adopt** | Restates [[ADR-016]] + I2 / I15. | No Path B weight training. No dollar claim. |
| K4 | Runtime `context_curator.py` | **defer** | New platform component. Needs PO + AI engineer. Easy to become silent CONSTRAINTS injection (I11). | Do not ship from this paper. Do not feed shop speech as trusted context. |
| K5 | Fresh-context **human/CI** review (MRC + required jobs) | **adopt** | Already true. Say it. | Do not rename MRC to a model node. |
| K6 | Orthogonal **LLM** reviewer as auto-merge gate | **reject** | Conflicts with I8 (no judge model) and MRC-only merge. | No second merger. No Duo-as-MRC. |
| K7 | `check_agent_stack_layers.py` | **adapt** | Computational sensor is in-scope **if** it checks real invariants (DATE_RE committed, guards, no invented status). | Must not weaken the 14-guard ratchet. |
| K8 | Typed edges already in floor 05 | **reject** as current-state | Still I7 proposed. | Do not document costume as inventory. |
| K9 | Negative constraints as a memory product | **reject** as current-state | Still I11. Fold into I5 if PO accepts. | No new `CONSTRAINTS.md`. |
| K10 | Skip 30 Aug flags because 31 Aug is newer | **reject** | Newer date ≠ absorbed predecessor. | Do not close I4–I8 by rewriting the playbook. |

## Recommended next playbook shape (not adopted)

If 31 Aug is to be the successor, it must **import** 30 Aug, not skip it:

1. Successor-of: 30 Aug (and 29 Aug, 28 Aug long form).
2. Keep I1–I3 / K2 / K3 / K5 as explicit already-true sentences.
3. Keep I4–I8 and K4 / K7 labeled **proposed** until PO comments adopt on a **second** implement issue.
4. Keep I11–I15 and K6 / K8 / K9 in a “when not to grow memory / when not to add a judge” section.
5. Restore Path B honesty: [[CF-054]] **regressed**; live [[J1]] after !300 Unknown unless a later session probes a clip.
6. Mention CF-055 only as the glossary finding, not as a contradiction CF.

Do not implement K4 or K6 from the 31 Aug paper. Do not treat the 31 Aug vs-Kocer note’s “concrete gaps” as PO accept.

## Explicit non-goals

- Do not restyle the shop.
- Do not invent BG / US / FR / NFR IDs.
- Do not invent a second CF-055.
- Do not weaken guards.
- Do not paste this onto Pages or into DATE_RE.
