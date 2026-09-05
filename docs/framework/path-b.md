# Path B Florist Case Study

[Path B](glossary.html#path-b) is the reference flower shop implementation of Adaptive Experience Architecture, running live at [https://aea.artof.link](https://aea.artof.link).

> **In Plain English:** When creating an e-commerce experience powered by conversational AI, you need a realistic testbed to prove that the architecture works under real-world conditions. **Path B** is our working reference design: a live flower shop called Lily's Florist. It demonstrates how a single customer session smoothly adapts between wide desktop monitors and handheld mobile phones without losing cart contents or conversation context.

Live reference store: [https://aea.artof.link](https://aea.artof.link)

---

## What Path B Demonstrates

Path B implements the core AEA formula: **Shared Understanding + Domain Services + Outer Harness**.

It provides an **Adaptive Workspace** that changes its presentation depending on the device:

- **Desktop (16:9 Widescreen):** An interactive, spatial workspace. The customer chats with the florist assistant on one side, while visual tiles (arrangement preview, greeting card note, delivery calendar, and cart total) dynamically appear and update on the other side.
- **Mobile (9:16 Handheld):** A streamlined, vertical concierge interface tailored for quick thumb scrolling and tap-to-select choices.

Both interfaces share the exact same underlying session, inventory catalog, and business rules.

---

## The Four Tested Customer Journeys

To verify the store's behavior, we test the shopping flow against four distinct customer personas:

### 1. Urgent Sam — Same-Day Delivery
Sam needs roses delivered today for an unexpected celebration. The assistant quickly filters the catalog for arrangements currently in the cooler, verifies immediate delivery driver slots, and guides Sam through rapid checkout.

![Urgent Sam, 27 August 2026 phone tape, 30 seconds](assets/j1-urgent-sam-30s.mp4)

---

### 2. Planner Sarah — Custom Arrangement & Message
Sarah is planning a milestone anniversary days in advance. She customizes her order with a keepsake glass vase, luxury satin ribbon, and a heartfelt handwritten card message, using interactive card controls to review and confirm every detail.

![Planner Sarah, 27 August 2026 phone tape, 30 seconds](assets/j2-planner-sarah-30s.mp4)

---

### 3. Loyal Alex — Seamless Session Persistence
Alex adds flowers to their cart, steps away, and accidentally reloads the browser window. Instead of forgetting the cart or restarting the conversation, the session memory instantly restores Alex's selections, occasion context, and active cart.

![Loyal Alex, 27 August 2026 phone tape, 30 seconds](assets/j3-loyal-alex-30s.mp4)

---

### 4. Tracker Chris — Order Status & Florist Escalation
Chris placed an order earlier and wants to know when it will arrive. Chris enters their order reference to see real-time fulfillment status, and taps "Contact Florist" to send an instant note directly to the atelier staff.

![Tracker Chris, 27 August 2026 phone tape, 30 seconds](assets/j4-tracker-chris-30s.mp4)

---

## Florist staff console (not a second native app)

Staff fulfill orders on the **same live store**, at `/florist` in a browser (phone, tablet, or laptop). That page is **mobile web**, not a separate Play Store app for florists.

What is on the live staff page as of 4 September 2026, in plain terms:

- **Day windows:** Staff Orders can show Today / next 3 days / next 7 days / Delayed / All, with counts on each pill. Contact Florist has its own day windows (looking backward).
- **Load more:** Long lists page in rather than dumping everything at once.
- **Phone layout:** Tables collapse; a Details sheet opens the arrangement and card; nav pills wrap so Forecast is not clipped off-screen; tap targets are at least 44 pixels.

A **native Android app for florists** is a possible later product. It is not current work. The customer companion stays the only native Path B app until shop-floor proof, a hard web/PWA limit, a second Play track the staff will actually maintain, and an explicit go are all evidenced.

### Atelier Shift Routine: 4 Daily Steps for Shop Staff

For florists working the shop floor, the daily workflow follows 4 focused steps:

1. **Morning Batching (`#prepare`):** Check arrangement tallies (e.g. *5× Classic Rose Dozen*) and delivery window splits (Morning / Afternoon). Tap **`Details ↗`** to open the bottom sheet and transcribe the customer's handwritten card messages.
2. **Order Fulfillment (`#orders`):** Work through the **Today** queue. Note channel badges (`web` vs `companion-android`) and packaging notes.
3. **Inquiry Triage (`#inbox`):** Watch for real-time customer escalations from the Contact Florist button. Tap any inquiry to jump to that customer's shared session context.
4. **End-of-Day Review:** Switch filters to **Delayed** to ensure zero missed orders, then check **3 days** / **7 days** to plan upcoming flower cooler inventory.

*For complete operational procedures, multi-device shortcuts, and least-data guarantees, see the [Florist Operator Guide](../05-ux-design-guide/florist-operator-guide.md).*

---

## Architectural Honesty: Intended vs. Verified

- **Dual-Viewport Layout:** Providing side-by-side desktop and mobile views from a single codebase is the intended architectural design. While responsive CSS has been deployed, a continuous side-by-side video walkthrough recorded simultaneously on both viewports remains **Unknown**. Path B stays transparently labeled as *not fully verified* until that dual probe is recorded.
- **Payment Processing:** Payment is safely handled by a deterministic simulation engine under ADR-016; live credit card processing (Stripe) is deliberately inactive.

---

## Related Documentation

- [System Stack](stack.html) — How the cloud servers, message bus, and mobile clients connect.
- [Mobile Companion](companion.html) — Details on the native Android app and Google Play release.
- [Project Journal](journal.html) — Stories of real-world challenges, solutions, and hard-learned lessons.
- [Architecture Glossary](glossary.html) — Plain-English definitions of terms and concepts.
- [Framework Home](index.html) — Return to the overview.
