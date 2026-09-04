# Mobile Companion App

The Android companion is a **lightweight mobile shopping app** for Lily's Florist. It is designed to do one job cleanly on a phone: help customers quickly find, customize, and order flowers on the go.

> **In Plain English:** When ordering flowers from your phone, you don't need a heavy desktop interface or an AI chatbot pretending to be a store. You want an app that understands what you need, shows real bouquets that are actually in stock, and lets you check out securely in seconds. That is the Companion App.

The live flower shop runs at [https://aea.artof.link](https://aea.artof.link). This page explains how the mobile app is built and how we verify its real-world performance.

---

## How It Works: A "Thin" Client

In software architecture, a **thin client** is an app that handles the screen and user interactions, while leaving the heavy business decisions to the store's central engine.

Instead of duplicating inventory, pricing, or checkout rules inside the phone app, the companion connects directly to the exact same backend service that powers the website:

- **The Store Decides, Not the Phone:** The app never guesses prices, discounts, or stock levels. If an arrangement is sold out in the shop, the app immediately respects that.
- **Fast, Focused Journey (Need → Pick → Pay):** The app focuses strictly on 3 core steps:
  1. **Need:** Telling the app what occasion you are shopping for (e.g. *Mom's Birthday, Same-Day*).
  2. **Pick:** Browsing tailored floral arrangements and choosing your favorite.
  3. **Pay:** Selecting a delivery window and checking out securely.
- **Privacy First:** The app never sees, transmits, or stores raw credit card numbers. It sends an opaque, single-use payment reference only.

---

## See It in Action (30-Second Video)

Here is a 30-second recording of the app running on a physical Android phone connected to the live store backend. 

Watch how tapping **Mom's Birthday (Same-Day)** immediately tailors the catalog to show birthday arrangements available for delivery today:

![Companion Need step on Android, 2 September 2026, 30 seconds](assets/companion-need-30s-2026-09-02.mp4)

---

## Keeping Mobile and Web in Sync: The Honesty Loop

When a business runs both a website and a mobile app, they often drift apart—a price on the website might not match the phone, or a delivery fee might be calculated differently.

To prevent this drift, we use a 4-step **Honesty Loop**:

1. **Detect:** Automated testing tools constantly probe both web and mobile paths, checking that order totals, delivery fees, and inventory match to the penny.
2. **Decide:** When a difference is found, it becomes a single tracked issue with an assigned owner—no hidden bug backlogs.
3. **Ship:** We fix the discrepancy with the smallest possible change to the code.
4. **Prove:** Every fix is proven on real physical phones and live store servers before anyone can claim it works.

If a feature hasn't been physically tested and proven, its status remains **Unknown**. We do not take promises on faith.

---

## The Honesty Ledger: Verified Real-World Proof

Here is what has been physically verified in production, and what has not:

> **Installs from the Google Play Store** — **Verified (4 Sep 2026):** The app was installed on physical test phones (ASUS ROG and Samsung Galaxy) directly from Google Play (Internal Track, version `5`). It is a true production release build, not a developer prototype running on a simulator.

> **Florist Staff See Web vs. Mobile Orders** — **Verified (4 Sep 2026):** When a customer buys flowers through the phone app, the order lands instantly in the florist's live dashboard with a clear channel tag: `client: companion-android`. Florists know immediately whether an order came from the web or the mobile app.

> **Choosable Delivery & Contact the Florist** — **Verified (4 Sep 2026):** Customers can choose their delivery window (`morning`, `afternoon`, or `evening`). If a customer needs special assistance, tapping "Contact Florist" sends an instant notification straight to the florist's inbox.

> **Direct Write-Through to Order History** — **Verified (4 Sep 2026):** Placing an order writes directly to the central database, guaranteeing that inventory updates immediately across both phone and web.

> **Demo Operator Inbox is Not the Billing System** — **No:** We keep this honest. The florist order overview is designed for demonstration and fulfillment visibility, not as a replacement for a full commercial billing accounting system.

> **Real-Time Traffic Dashboard** — **Verified in Code:** Web visits and mobile app traffic are tracked separately in telemetry, so operators can monitor app performance and uptime independently.

---

## Technical Audit Details

For developers and technical evaluators who want to inspect the exact device logs and transaction IDs:

### 1. Google Play Release Verification (#390)
During initial testing, sideloaded builds carried debug flags. To ensure true production quality, version `5` was deployed through Google Play Internal Track. Device inspection on the ASUS ROG test phone (`ASUS_I001DC`) confirmed:
```text
versionCode=5 minSdk=26 targetSdk=36
installerPackageName=com.android.vending
pkgFlags=[ HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP ]
```
The app has zero debug flags and is officially signed and distributed by Google Play (`com.android.vending`).

### 2. Live Order Verification (#375, #384)
On 4 September 2026, a live test purchase was completed from the mobile app on the ASUS ROG phone:
- **Order ID:** `34091114-cb91-44de-a5a3-6be78c503912`
- **Item:** Classic Rose Dozen ($82.00 total)
- **Result:** Appeared in real time at `GET https://aea.artof.link/api/v1/operator/orders` with `client: companion-android`.

---

## Related Framework Topics

- [Path B Case Study](path-b.html) — Watch the full florist workspace journey tapes.
- [Privacy-Preserving CRM](crm.html) — How customer history and reminders work without storing personal data.
- [System Architecture & Stack](stack.html) — How the cloud servers and mobile clients connect.
- [Architecture Glossary](glossary.html) — Plain-English definitions of terms and concepts.
- [Framework Home](index.html) — Return to the overview.


