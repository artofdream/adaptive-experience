# Sponsor vs Scrum Master vs Product Owner — remaining autonomy gaps

tags: #aea #inbox
status: inbox
captured: 2026-08-18
updated: 2026-08-18

## Note

Cursor `aea-*` skills treat the human as **project sponsor**,
`@aea-project-manager` as Scrum Master, and `@aea-product-owner` as
product mission/vision and product go/no-go. Path B is unparked (DSO
applies). These gaps remain; they are intentional, not missing SM or PO
duties.

- **PO gap closed.** `@aea-product-owner` owns backlog priority among
  existing IDs, product accept/defer/park, M12 unpark recommendation,
  and Path A vs Path B **product** acceptance. Sponsor still required if
  unpark needs budget or secrets. Do not invent FR/NFR IDs.
- **Journey is QA-of-record, not an extra unused-heads head.** Unused-heads
  tally is `/ 9` (PO + PM + 7 specialists). `@aea-customer-journey` still
  walks and reports; product accept of the walk is PO.
- **Dedicated application security reviewer established.** `@aea-appsec-auditor`
  owns application-layer threat audits, prompt injection defenses, API perimeter security,
  and OWASP reviews, pairing with `@aea-devsecops-platform` (infrastructure/AWS/Terraform).
- **GitLab CI var paste is still human.** DSO writes handoff notes; the
  sponsor pastes values `glab` cannot set. Same for `.env` /
  `terraform.tfvars` secrets and production API keys.

## Links

- Related docs: `.cursor/skills/aea-product-owner/SKILL.md`,
  `.cursor/skills/aea-project-manager/SKILL.md`
- Related notes:

## Open questions

- None for the PO gap. Remaining: secrets paste and no separate security
  reviewer beyond DSO.
