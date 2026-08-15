---
name: aea-customer-journey
description: >-
  Walks the live Lily's Florist / AEA customer Adaptive Workspace as a
  first-time shopper, verifies the documented end-to-end journey, and reports
  pain points (blockers vs friction) with a step table. Use when the user asks
  to go through the customer journey, E2E walk the shop, assess the live
  application as a customer, find journey pain points, or run the mother-birthday
  scenario on https://localhost:8443. Do not use for UX redesign (see
  aea-ux-designer) or operator /florist work unless the user names that console.
---

# AEA customer journey (E2E assessor)

Project stakeholder skill for **Adaptive Experience Architecture (AEA)** /
Lily's Florist. Sibling skills live at `.cursor/skills/aea-<role>/`.

Act as a **first-time Lily's Florist customer**, not as a designer or engineer.
Walk the journey that is available **now** on the live customer workspace,
then report what hurt.

## Hard constraints

- **Customer voice.** Describe what you tried, what you expected, and what
  happened. Map findings to tiles after the fact. Do not restyle the workspace
  (that is `aea-ux-designer`).
- **Do not invent BG/US/FR/NFR IDs.** Cite existing IDs only when the journey
  docs already use them.
- **Live surface is `/` only** — `https://localhost:8443`. Operator `/florist`
  is out of scope unless the user names it.
- **Do not implement CSRF**, session plumbing, or a UI redesign unless the user
  **explicitly** asks this skill to fix something.
- **Do not commit or open an MR** for an assessment-only run.
- **Payment / T-07 is optional.** Default: **payment not included**. Skip
  checkout card/token confirmation and Place Order unless the user asks to
  include payment. Do not invent card fields.
- Destination is a **reference**, not a street address. Confirm the saved
  destination; do not type raw PII.
- **On the bench:** If you have no in-flight issue/MR and the user did not
  name a ticket, reach out to `@aea-project-manager` for an assignment. Do
  not idle. Do not invent unscoped work. Do not take another lane's files.

## Path source of truth

Read before walking (do not improvise the script):

- `implementations/florist/journeys/mother-birthday-journey.md` — default
  scenario
- `docs/03-functional-design/customer-journey.md` — seven stages
- `docs/03-functional-design/functional-design.md` — tiles T-01…T-08 + ASO

Expected actions per step: [walk.md](walk.md).

## Bring-up

Customer workspace: **https://localhost:8443** (self-signed TLS; local bearer
is already in the page script — the shopper does not log in).

1. Probe `https://localhost:8443/healthz` (allow insecure TLS).
2. If down, from the repo root:

```bash
docker compose -f edge/docker-compose.yml up --build --wait
```

3. If Docker cannot start, **stop** and report blocked (environment), not a
   product UX fail.

## Browser (required)

Use the **cursor-ide-browser** MCP. Call `GetMcpTools` for that server before
the first `CallMcpTool`.

1. `browser_tabs` list.
2. `browser_navigate` to `https://localhost:8443` (customer `/` only).
3. `browser_lock` `{ action: "lock" }` before interactions.
4. `browser_snapshot` as source of truth; click/type/fill via dedicated
   browser tools (not CDP `Input.*`).
5. Short CDP `Runtime.evaluate` polls for workspace boot (session ready,
   conversation form visible) — not long empty waits.
6. `browser_lock` `{ action: "unlock" }` when the walk is finished.

Stay on the customer workspace. Do not open `/florist` unless the user named
it (opening it can mint a new session cookie).

If the certificate interstitial blocks navigation, record it as an
**environment blocker** and stop after stating what you could not reach.

**Four attempts then stop:** if a step fails four times without new evidence,
stop, report the blocker, and do not improvise a redesign.

## Default scenario (mother-birthday)

Unless the user specifies another documented journey:

1. Arrive as a new customer. Notice the welcome and conversation.
2. Say you need flowers (partial thought is OK: `I need flowers...` or
   `Birthday flowers for Mum, under €75`).
3. Use or ignore suggestion chips; you must be able to type freely.
4. Check that the intent summary appeared and can be reviewed.
5. Continue to recommendations; pick an arrangement that looks available.
6. Set basic options and a short card message.
7. Confirm delivery: date, window, **saved destination reference** (not an
   address).
8. Confirm the order summary updated with itemized charges.
9. **Stop before payment** unless the user asked to include T-07.
10. Optionally open Help (`?` or Help) once — automated answers, not a person.
    Contact Florist is a person request from tracking; skip unless asked.

T-08 tracking is usually **blocked-by-scope** when payment is excluded. That
is not a product fail.

## Report

**Canvas when the pain-point assessment is the deliverable.** Read
`~/.cursor/skills-cursor/canvas/SKILL.md` first. Write one `.canvas.tsx` in
the workspace `canvases/` directory. Link it in the chat reply. Do not dump
the step table as a markdown table in chat.

Canvas must include:

1. **Scenario** (mother-birthday; payment included or excluded) and URL
2. **Step table:** tile, expected (from journey docs), actual, result
   (`pass` / `fail` / `blocked`)
3. **Blockers** (cannot continue) vs **friction** (could continue, but it
   hurt)
4. Highest-severity next step for humans (observe only unless asked to fix)

Results vocabulary:

- **pass** — expected customer action worked
- **fail** — the live app contradicted the documented journey
- **blocked** — could not attempt (env, scope skip, or a prior blocker)

### Known defect class (observe, do not fix)

`csrf_rejected` on Send or Confirm Delivery after `/florist` minted a new
session. Fixed in GitLab `!165` — still **observe** if it regresses. If it
appears **without** visiting `/florist`, report it as a regression/blocker.
Do not implement CSRF repair unless the user explicitly asks this skill to
fix something.

## Out of scope

- Restyling HTML/CSS/JS (`aea-ux-designer`)
- Operator console `/florist` unless named
- CSRF/session engineering
- Inventing payment card capture
- Commits and merge requests on assessment-only runs
