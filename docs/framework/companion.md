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
  1. **Need:** You can tap a suggestion (e.g. *Mom's Birthday, Same-Day*) **or type your own words**. Continue unlocks once the app has something useful to work with — not only a parsed occasion keyword.
  2. **Pick:** Browsing tailored floral arrangements, choosing one, and setting **how many** (1–10), same as the website customize step.
  3. **Pay:** Selecting a delivery window and destination nickname (`home` / `work`), then checking out securely.
- **Privacy First:** The app never sees, transmits, or stores raw credit card numbers. It sends an opaque, single-use payment reference only.

---

## See It in Action (30-Second Video)

Here is a 30-second recording of the app running on a physical Android phone connected to the live store backend.

Watch the full **Need → Pick → Pay** path: **Mom's Birthday (Same-Day)**, budget chip, **Budget Mixed Bunch**, then **Confirm** through to **Order Confirmed** on a physical ASUS ROG phone against live Path B:

![Companion Need→Pick→Pay on Android ROG, 4 September 2026, 30 seconds](assets/companion-need-30s-2026-09-04.mp4)

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

> **Installs from the Google Play Store** — **Verified (A36 and ROG Play Internal v8, 5 Sep 2026):** Samsung A36 (`SM_A366B`, adb `RZCY60W1EZW`) and ASUS ROG (`ASUS_I001DC`, serial `K9AIKN07B088C89`) each installed companion `versionCode` **8** / `versionName` `0.1.0-alpha.8` from Play Internal (`installerPackageName=com.android.vending`, non-`DEBUGGABLE`). Earlier Play-honest proves on ROG/A36 used prior Internal builds (v4–v7). **This page's 30s demo clip** remains the 4 Sep ROG App Dist / packageinstaller take — UX proof of Need→Pick→Pay→Confirmed, not Play-install honesty for that take.
>
> **Florist Staff See Web vs. Mobile Orders** — **Verified (4 Sep 2026):** When a customer buys flowers through the phone app, the order lands instantly in the florist's live dashboard with a clear channel tag: `client: companion-android`. Florists know immediately whether an order came from the web or the mobile app.
>
> **Choosable Delivery & Contact the Florist** — **Verified (4 Sep 2026):** Customers can choose their delivery window (`morning`, `afternoon`, or `evening`). If a customer needs special assistance, tapping "Contact Florist" sends an instant notification straight to the florist's inbox.
>
> **Direct Write-Through to Order History** — **Verified (4 Sep 2026):** Placing an order writes directly to the central database, guaranteeing that inventory updates immediately across both phone and web.
>
> **Phone remembers the last order (Edge Wallet)** — **Write verified; Need reorder *code* on `main` (!459 / #404); Play v8 tap Unknown:** After Confirm, the phone stores an encrypted receipt on the device (no street address, no card number). That **save** is a separate fact from the shortcut. Need shows a returning-customer card **only when a device-held receipt exists** (`latestWalletReceipt != null`). On 5 Sep 2026, Play Internal v8 **fresh / cold-start Need** showed **no** Reorder / wallet one-tap CTA on **both** A36 and ROG (chips only). Do not treat ROG as an open #404 tap prove. The #404 vault note records a sideloaded ROG walk — UX/code proof, not Play-install honesty. Play-honest follow-up is [#407](https://gitlab.com/artof-group/adaptive-experience-architecture/-/work_items/407). **This page's 30s demo clip** remains the !455 Need→Pick→Pay take and does not show the reorder card. Sponsor-machine ROG evidence path (not inspected from this checkout): `C:\Users\claud\Temp\aea-rog-404\`.
>
> **Budget chips after free-text / No limit:** Issues #401 and #402 are closed on `main` (!457, !460). **Device prove (A36 Play v8, 5 Sep 2026 — not ROG):** #401 **PASS** — free-text Need then `$100+` → chat `Budget: $100+`; no BFF 422; View Arrangements shown. #402 **PASS** — **No limit** chip → Need/Pick/Pay honest No limit copy (not Skip budget / Budget not set). Sponsor-machine evidence path (not inspected from this checkout): `C:\Users\claud\Temp\aea-v8\evidence\`.
>
> **Demo Operator Inbox is Not the Billing System** — **No:** We keep this honest. The florist order overview is designed for demonstration and fulfillment visibility, not as a replacement for a full commercial billing accounting system.
>
> **Real-Time Traffic Dashboard** — **Verified in Code:** Web visits and mobile app traffic are tracked separately in telemetry, so operators can monitor app performance and uptime independently.

---

## Technical Audit Details

For developers and technical evaluators who want to inspect the exact device logs and transaction IDs:

### 1. Google Play Release Verification (#390)
During initial testing, sideloaded builds carried debug flags. To ensure true production quality, later Internal builds were deployed through Google Play Internal Track. Play-honest v8 dumpsys on 5 Sep 2026 matches on **both** named handsets (A36 `SM_A366B` / `RZCY60W1EZW`, and ROG `ASUS_I001DC` / `K9AIKN07B088C89`):

```text
versionCode=8 versionName=0.1.0-alpha.8
installerPackageName=com.android.vending
non-DEBUGGABLE
# prior Play-honest proves: ROG/A36 on versionCode 4–5; Play Internal upload also reached versionCode 7
```

Both v8 installs are signed and distributed by Google Play (`com.android.vending`) with no debug flag. This session did not inspect the sponsor evidence directories (`C:\Users\claud\Temp\aea-v8\evidence\`, `C:\Users\claud\Temp\aea-rog-404\`).

### 2. Live Order Verification (#375, #384)
On 4 September 2026, live test purchases completed from the mobile app on the ASUS ROG phone. Latest demo recording:
- **Order ID:** `f3583908-b2ca-4b5e-a4e8-aa0c6c040177`
- **Item:** Budget Mixed Bunch + delivery (**$47,00** total)
- **Status:** SUBMITTED (Preparing in atelier) · ETA afternoon → home
- **Result:** Companion showed **Order Confirmed!**; same write-through path as prior florist probes (`client: companion-android`).

---

## Shopper Privacy & Edge Wallet Guide: How Reordering Works

When you place an order on Lily's Florist Companion, your personal details (recipient name, card message draft, address nickname) never enter a centralized CRM tracking database. Instead, they are stored securely in your phone's **Edge Wallet** (Android Keystore hardware encryption):

1. **Zero-PII Storage:** The florist atelier only receives the bouquet SKU, delivery window, and message text to print on the physical card.
2. **1-Tap Reorder Shortcut (FR-008):** When a **local encrypted receipt** exists and Need is still fresh (no typed message, no occasion chip yet), a private card appears (*"Reorder for {recipient}"*). Tapping **`Reorder →`** revalidates current cooler stock and takes you straight to Pick with your arrangement pre-selected. The card is **not** shown on an empty wallet. Play Internal v8 cold-start Need on A36 and ROG (5 Sep 2026) showed chips only — Play tap remains **Unknown** (#407).
3. **Right to Be Forgotten:** You can wipe your local encrypted history at any time; physical delivery addresses at the shop are automatically shredded after 14 days.

*For full details on on-device encryption and privacy guarantees, see the [Customer Edge Wallet Guide](../05-ux-design-guide/customer-edge-wallet-guide.md).*

---

## Related Framework Topics

- [Path B Case Study](path-b.html) — Customer journey tapes and the florist staff console (browser, not a second app).
- [Privacy-Preserving CRM](crm.html) — How customer history and the on-phone wallet work without storing personal data.
- [Journal](journal.html) — Why a saved receipt is not the same as a reorder button.
- [System Architecture & Stack](stack.html) — How the cloud servers and mobile clients connect.
- [Architecture Glossary](glossary.html) — Plain-English definitions of terms and concepts.
- [Framework Home](index.html) — Return to the overview.
