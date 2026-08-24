# Recommendation: CF-051 — FR-016 / FR-017 narrative alignment

> **Finding:** CF-051 (Medium)  
> **Workstream:** `grok` (markdown only — manual GitLab promotion)  
> **Suggested owner:** `@aea-coherence-guardian` + `@aea-product-owner` (wording)  
> **Suggested branch:** `fix/cf-051-fr016-017-narrative`  
> **Do not merge from this sandbox.**

## Problem

Canonical table (`docs/02-business-analysis/requirements.md` + workbook/CSV):

| ID | Meaning | Scope |
|----|---------|--------|
| FR-016 | AI-generated occasion **reminders** | Future |
| FR-017 | Customer **engagement analytics** | Future |

Conflicting prose:

- Same requirements doc: “Staff CRM and live chat remain out of scope **(FR-016 / FR-017)**” — wrong IDs for staff chat.
- Roadmap **M12** marked **Completed** against FR-016/FR-017 (thin zero-PII CRM service exists).
- Roadmap **M16** staff live chat also lists FR-016/FR-017.
- Notes elsewhere correctly say staff chat is Future and thin CRM is a slice.

## Desired outcome

- Prose never maps **staff live chat / staff CRM ticketing** to FR-016/FR-017.
- FR-016/FR-017 remain **reminders / engagement analytics** per table.
- M12 completion language describes the **thin zero-PII occasion/reminder slice** without implying full Future CRM or staff chat.
- M16 cites appropriate IDs (e.g. FR-006 escalation / explicit Future staff-chat scope)—not FR-016/017 as staff chat.

**Do not invent new requirement IDs.** Do not change workbook counts unless sponsor explicitly approves an archive change (out of band).

## Proposed change (focused)

### A. `docs/02-business-analysis/requirements.md`

- Fix the sentence that attributes staff CRM/live chat to FR-016/FR-017.
- Example direction: staff live chat and operator ticketing remain Future; FR-016/FR-017 remain occasion reminders and engagement analytics (Future in workbook); thin client-side/zero-PII reminder helpers may exist without promoting workbook scope.

### B. `docs/07-roadmap/roadmap.md`

- **M12:** Keep “Completed” only if describing delivered thin `crm.py` occasion memory; state clearly workbook scope stays Future; staff live chat stays out.
- **M16:** Drop FR-016/FR-017 as primary coverage for staff chat; use FR-006 / Future staff-chat wording consistent with notes.
- Align bullet notes that currently say “remain Future (FR-016 / FR-017)” when the subject is staff chat—split staff chat vs FR-016/017.

### C. Light cross-check

- `platform/aea_platform/crm.py` header comments may say FR-016/FR-017; ensure they mean reminders/analytics slice, not staff chat.
- No code behavior change required for this MR.

## Out of scope

- Workbook ID rewrites
- Implementing staff WebSocket chat
- Unparking Future → MVP without PO decision

## Acceptance checks

- [ ] No prose maps staff live chat to FR-016/FR-017
- [ ] Table definitions unchanged unless archive change is explicit
- [ ] M12/M16 wording consistent with thin CRM vs staff chat
- [ ] Coherence guard still passes

## Manual GitLab steps

1. Issue CF-051 → `fix/cf-051-fr016-017-narrative`
2. Doc-only MR
3. Hand to MR coordinator when green

## Evidence paths

- `docs/02-business-analysis/requirements.md`
- `docs/07-roadmap/roadmap.md`
- `archive/canonical-requirements.csv`
- `platform/aea_platform/crm.py`
