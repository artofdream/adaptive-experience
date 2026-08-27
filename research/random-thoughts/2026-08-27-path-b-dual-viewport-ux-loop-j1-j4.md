# Path B dual-viewport UX loop (J1–J4 clips, 2026-08-27)

> **Tags**: #aea #second-brain #ux #path-b #j1 #j2 #j3 #j4 #knowledge-first
> **Captured**: 2026-08-27
> **GitLab**: #272
> **Related**: sponsor T-04 notice (parked), not #254 / #231 / !297
> **Owners to inherit**: @aea-ux-designer, @aea-customer-journey, @aea-knowledge-guardian, @aea-mr-coordinator
> **This node is knowledge, not a UI restyle.**
> **Probed**: live `https://aea.artof.link`, phone iPhone SE 375x667 device mode, desktop 1280x800, session-based (no password). Clips cut on 2026-08-27 evening Europe/Berlin.

Later agents: do not rediscover this from chat. Shared memory is committed GitLab `main` only. A status word is a claim. Probe with the same journey script or write Unknown.

Inherits [[2026-08-27-honesty-crisis-lessons-and-path-b-chain]]. Journeys [[J1]] [[J2]] [[J3]] [[J4]]. Requirements in play: [[FR-001]] [[FR-007]] [[FR-011]] [[NFR-009]] [[FR-003]] [[FR-009]] [[FR-008]].

---

## 1. Continuous UX loop (do this, not a new product)

Do **not** add a 15th hat. Do **not** stand up a separate analytics app for this. Mirror the coherence-findings loop:

1. **Record** one journey on one viewport (phone 9:16 or desktop 16:9), captions naming the tile.
2. **Review** against a short bar (below), with the clip as evidence.
3. **One finding → one GitLab issue → one MR.** Owner `@aea-ux-designer`. MRC merges.
4. **Vault wikilink** from this note (or a dated child) to the issue. Clips are evidence, not DATE_RE.
5. **Re-record the same script** after merge. Close only if the new clip shows the fix. If not, the finding is still open.

Graph (nodes already in the repo): Journey × Viewport → Clip → Finding → Issue → Note → MR → Clip′.

`@aea-customer-journey` owns the script (what to tap). `@aea-ux-designer` owns the change. `@aea-knowledge-guardian` keeps the graph honest. Cadence must not write DATE_RE.

---

## 2. What the 2026-08-27 clips actually showed

Origin shop. Session cookie / local-browser-token path; no login form appeared.

| Journey | Phone | Desktop | Honest leftover |
|---|---|---|---|
| [[J1]] Urgent Sam (same-day roses) | E2E 9:16 T-01→T-04 (~2:40) | E2E 16:9 T-01→T-04 + ASO (~4:40) | No pay / Track |
| [[J2]] Planner Sarah | 30s T-04 card + satin ribbon | In the desktop tape (workspace + T-04) | Dual CTA Update vs Continue |
| [[J3]] Loyal Alex | 30s reload; conversation persisted | Same-browser recall on desktop too | **No reorder badge** (not faked) |
| [[J4]] Tracker Chris | 30s ASO “safe for cats?” | Help overlay on desktop | Track locked; Contact Florist gated on tracking |

T-08 / T-09 were **not** reached. Step 7: “Step 7 unlocks after you finish earlier stages.” No money spent.

Desktop step names: Discover / Understand / Choose / Customize / Deliver / Review & pay / Track. Phone: Start / Intent / Pick / Edit / Ship / Pay / Track. Same flow, two vocabularies.

---

## 3. Review vs UX practice (from the clips, not a generic audit)

**Keep (honest product):**
- Large Select; [[NFR-009]] Available badge is visible.
- Photo likeness disclaimer (not stock-in-cooler).
- ASO labeled “This is not a person.” Fail-closed on unapproved pet-safety ([[FR-009]]).
- Shared Understanding is editable ([[FR-001]] / T-02).
- Session, not password.

**Fix (not phone-native; desktop workspace is overloaded when copied down):**
- Seven labeled stages on 375px. People shop in 3–4 moves (need, pick, pay), not Start/Intent/Pick/Edit/Ship/Pay/Track.
- Step names differ by viewport.
- T-04: Update and Continue to delivery compete. Sponsor already noticed T-04 Edit.
- Track and Contact Florist stay locked until checkout, so [[J4]] dead-ends in ASO.
- Suggestion chips (Mom, birthday, under $75) sit next to a $125 Pink Flower Vase. If chips are filters, the grid lies; if they are only prompts, they look applied.
- Desktop Adaptive Workspace showing T-01..T-04 at once is the PC differentiator; shrinking it onto a phone is the bug.
- J3 recall works; there is no reorder control ([[FR-008]] is a ranking hint, not a button).

---

## 4. Dual presentation (how PC and phone stay engaging)

One session, **two presentations**. Do not scale the desktop workspace to 375px.

- **Desktop (wide):** keep Adaptive Workspace. Earlier tiles stay visible. That is the engaging PC trick (spatial, persistent [[FR-001]]).
- **Phone (narrow):** linear concierge. One primary pane (talk → pick a card → pay). Earlier choices live in a collapse / summary sheet, not four tiles. Progress is a short bar (“3 of 4 · Pick”), not seven named steps.
- **Shared across both:** same step names, one primary CTA per screen, same session, fail-closed inventory, ASO not a person.

Engagement is the conversation hook on both; the layout is what changes.

---

## 5. First issue in the loop

#272 is the tracker for this finding. Implementer: `@aea-ux-designer`. This MR only commits this note. No CSS/JS restyle here. Do not batch CRM #254, HLD #231, or !297.

Re-probe after a UX MR: same J1 script on phone and desktop. Unknown until those clips exist.
