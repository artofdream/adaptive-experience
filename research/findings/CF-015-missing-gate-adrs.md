# CF-015 — Gate issues #106–#108 lack matching ADR files

tags: #aea #coherence-finding
status: queued
finding_id: CF-015
severity: high
issue: "#106 #107 #108"

## Claim

GitLab gate issues #106–#108 have no correctly numbered ADR files for
contract-first messaging, experience-state ownership, and command/event
boundaries. Those number slots were occupied by unrelated tech stubs (CF-014).

## Intended fix

After CF-014 quarantine: three SOP cycles authoring ADR-008, ADR-009, ADR-010
matching each issue (`Closes #106`, then `#107`, then `#108`).
