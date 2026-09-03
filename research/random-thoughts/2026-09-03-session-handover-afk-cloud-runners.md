# Session Handover: AFK Status & Cloud Runner Autonomous Tasks (2026-09-03)

#aea #aea/handover #aea/session #aea/crm #aea/florist

**Date:** 2026-09-03 08:06 UTC  
**Author:** `@aea-mr-coordinator` & `@aea-devsecops-platform`  
**Repository:** `artof-group/adaptive-experience-architecture`  
**Related Documents:** [[2026-09-03-path-b-florist-384-migration-023-channel-live]] · [[2026-09-02-session-memory-log-devops-companion-budget-florist-operator]] · [[2026-09-02-least-data-crm-privacy-preserving-order-insights]]

---

## 1. Active Cloud Runner Pipelines

1. **MR !431 (`feat/least-data-operator-crm`)**:
   - Scope: Migration `024_operator_crm_subject_profile.sql`, `CrmService` in `platform/aea_platform/crm.py`, unit tests, and public framework page `docs/framework/crm.md` (`architecture.artof.link/crm.html`).
   - Status: Pipeline running with `✓ Will auto-merge` enabled.
2. **GitLab Pages (`pages` job)**:
   - Will automatically deploy `public/` upon merge of !431 to `main`.

---

## 2. Handover Tasks for Cloud Agents (Cursor / Grok-Bot / MRC)

### Task A: Cloud DB Migration 024 RunTask on AWS ECS
- Once MR !431 merges to `main`, execute `python platform/scripts/apply_migrations.py` on AWS ECS cluster `aea-pilot` (task definition `aea-pilot-orchestration`) to apply `024_operator_crm_subject_profile.sql` in production RDS PostgreSQL.

### Task B: Issue Triage & Cleanup for Merged Operator Facts (#375, #377, #383, #384, #385, #391, #392, #393)
- MR !409, !418, and migration 023 already resolved channel attribution (`aea_client`), catalog product title, itemized total, and card message visibility on both the `/florist` staff list and session facts drawer.
- Cloud agents can verify live `/api/v1/operator/orders` and close resolved/duplicate issues.

### Task C: Play Store Honesty on ASUS Hardware (#390)
- Ensure tests distinguish between local debug sideloads (`installer=null`, `DEBUGGABLE`) vs release Google Play Store installs (`installer=com.android.vending`, non-debuggable).

---

## 3. Local Machine (cts-ai) Posture
- Working tree clean, all 14 quality guards green.
- ADB connected (`K9AIKN07B088C89` ASUS ROG).
- Host is ready for automated resumption.
