# CF-015 — Gate issues #106–#108 lack matching ADR files

tags: #aea #coherence-finding
status: in-progress
finding_id: CF-015
severity: high
issue: "#106 (ADR-008); then #107; then #108"
branch: docs/adr-008-contract-first-messaging

## Claim

GitLab gate issues #106–#108 have no correctly numbered ADR files for
contract-first messaging, experience-state ownership, and command/event
boundaries. Those number slots were occupied by unrelated tech stubs (CF-014).

## Intended fix

After CF-014 quarantine: three SOP cycles authoring ADR-008, ADR-009, ADR-010
matching each issue (`Closes #106`, then `#107`, then `#108`).

## Progress

- [x] CF-014 verified on main @ a0ab098
- [ ] ADR-008 / #106
- [ ] ADR-009 / #107
- [ ] ADR-010 / #108
