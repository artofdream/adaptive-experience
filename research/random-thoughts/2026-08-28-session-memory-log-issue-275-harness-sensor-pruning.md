# Session Memory Log: Issue #275 — Harness Lean Pruning & Sensor-Backed Rules

> **Date**: 2026-08-28  
> **Stakeholders**: `@aea-knowledge-guardian`, `@aea-coherence-guardian`, `@aea-senior-software-engineer`  
> **Traceability**: Issue #275, CF-048  
> **Tags**: #aea  

---

## 1. Executive Summary

This session executed **Issue #275** (`harness: prune guide/skill lines that CI sensors already enforce`), applying the "lean by subtraction" principle across guide rules and stakeholder instructions.

---

## 2. Key Accomplishments & Changes

1. **Sensor-Backed Rule Pruning**:
   - Audited overlapping prose rules in `AGENTS.md` and `.cursor/rules/` against active computational sensors (`run_verify_job.py`, `run_all_guards.py`, `check_secrets_posture.py`, `check_coherence.py`, `check_stakeholder_skills_sync.py`).
   - Collapsed redundant manual checklists into concise pointers to automated test runners.

2. **Maintained Canonical 14-Role Boundary**:
   - Reaffirmed the 14-role stakeholder matrix without adding redundant hats or external playbook metrics ($5/task, 3 retries, 80% completion).
   - Enforced that automated CI sensors serve as the source of verification truth, keeping guide files lightweight and maintainable.

---

## 3. Second Brain References

- [[2026-08-28-session-memory-log-issue-274-harness-date-re-rules]]
- [[2026-08-27-honesty-crisis-lessons-and-path-b-chain]]
- [[2026-08-25-trust-but-verify-job-and-single-role-list]]
