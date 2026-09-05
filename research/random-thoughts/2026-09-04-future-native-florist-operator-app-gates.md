# Future native florist *operator* app — development gates (sponsor 2026-09-04)

> **Tags**: #aea #vault #sponsor #florist-operator #native #mobile-web #pwa #path-b #companion #gates
> **Date**: 2026-09-04
> **Canonical path**: `research/random-thoughts/2026-09-04-future-native-florist-operator-app-gates.md`
> **Audience**: sponsor / planners / implementers (two tracks below)
> **Related**: [[2026-09-04-florist-operator-multi-device-responsive-architecture]] · [[2026-09-04-session-memory-log-florist-operator-mobile-ux]] · [[2026-09-02-native-web-florist-story-plain-language]] · !450

---

## Plain

**Decision (2026-09-04):** A **native Android app for the florist operator** is a **potential future**, not current work.

- The **customer companion** stays the native Path B product (Play / App Distribution track for shoppers).
- The **operator** stays **mobile-web** at `/florist` (plus optional **PWA / Add-to-Home-Screen** later if useful).
- Do **not** start a second native product surface for staff until the gates below are all evidenced — not vibes, preference, or “apps feel nicer.”

**Near-term path:** florist **responsive honesty** landed in !450; day filters !453 and boot/pagination !434 also on `main`. Next is PWA / Add-to-Home-Screen **before** any native operator app — still gated below. Public wording: [[2026-09-04-session-memory-log-evening-mrc-rog-wallet-honesty]] and `docs/framework/path-b.md`.

**Gates before developing a native operator app** (all must be true and evidenced):

1. **Shop-floor proof** that responsive florist web still **fails a real operator job** (not just preference) **after** current mobile polish lands.
2. **At least one hard constraint** web/PWA cannot meet well — e.g. offline must-not-lose orders, Bluetooth printer / cash drawer / barcode, reliable background push for new orders, or all-day camera/scan workflow.
3. **Staff willingness** to maintain a **second Play track** (versionCode discipline; Internal vs App Distribution honesty) **separate from** the companion.
4. **Explicit sponsor go** for a second native product surface (scope, auth/staff model) — **not** a companion fork without an ADR.

Until those clear: operator = mobile-web `/florist`; companion = the only native Path B client.

---

## Vault

### Sponsor decision (2026-09-04)

| Surface | Status | Notes |
|---------|--------|-------|
| Customer **companion** (native Android) | **Current Path B product** | Play Internal / App Dist; keep honesty on versionCode / installer / debuggable |
| Florist **operator** (`/florist`) | **Mobile-web now** | Responsive polish !450, day filters !453, boot/pagination !434 on `main`; optional PWA later |
| Native Android **operator** app | **Potential future only** | Not scheduled; blocked on gates below |

### Development gates (must all be evidenced)

1. **Shop-floor failure proof (post-polish)**  
   - Evidence that responsive `/florist` still blocks a **real** operator job after current mobile polish (!450 etc.) lands and is live-proved.  
   - Preference / “native feels better” alone is **insufficient**.

2. **Hard web/PWA constraint (≥1)**  
   Document and prove at least one constraint that mobile-web / PWA cannot meet well, such as:  
   - Offline **must-not-lose** order workflows  
   - Bluetooth printer / cash drawer / barcode hardware  
   - Reliable **background push** for new orders  
   - All-day **camera / scan** workflow  

3. **Second Play track willingness**  
   Explicit staff/ops willingness to maintain a **separate** Play package/track from companion: versionCode scheme, Internal vs App Distribution honesty, release discipline.

4. **Explicit sponsor go + ADR**  
   Written sponsor approval for a **second native product surface**, including scope and auth/staff model.  
   **Forbidden without ADR:** forking companion into an operator app.

### Near-term path (do this instead)

1. Finish florist **responsive honesty** — !450 (`fix(florist): operator console responsive polish + ≥44px targets`) and related polish; live-prove on phone/tablet/laptop.  
2. Consider **PWA / Add-to-Home-Screen** for `/florist` before any native operator investment.  
3. Revisit native operator **only** when gates 1–4 are all evidenced.

### Out of scope for this note / this MR

- Do **not** merge companion !422 work or change companion lanes here.  
- Do **not** touch operator efficiency draft !434.  
- This MR is **vault knowledge capture only** — no product code.

### Honesty

- Native operator app = **future option**, not committed roadmap.  
- Companion remains the sole native Path B surface until gates + sponsor go + ADR.  
- !450 polish must land and be shop-floor proved before any “web failed” claim.