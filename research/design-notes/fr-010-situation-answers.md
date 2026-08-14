# Design note — FR-010 situational support answers (#29)

status: implemented (thin path)
for_issues: "#29 (FR-010 Support Automation)"
affects: "ASO / Support Service; does not replace FR-009 FAQ or T-08 tracking"
date: 2026-08-15

## Decision

Answer order status, session delivery, and product availability from
authoritative session/inventory facts on the existing `POST /support` ASO
form. Publish `support.situation.answered`. Generic policy questions still
use FR-009 / `support.faq.answered`.

FR-010 stays Future in the requirements source of truth.

## Not in this slice

Live LLM generation, CRM memory, staff writes, or replacing T-08.
