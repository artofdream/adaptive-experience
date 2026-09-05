# Customer Guide: The Edge Wallet & Privacy-Preserving Reordering

> **Document**: Customer & Shopper Privacy Guide  
> **Audience**: Shoppers using Lily's Florist Android Companion or Web Adaptive Workspace  
> **Canonical Path**: `docs/05-ux-design-guide/customer-edge-wallet-guide.md`  
> **Related Standards**: ADR-020 (Privacy-Preserving CRM & Edge Wallet), FR-008 (Reorder Shortcut), NFR-017 (Zero-PII Perimeter)

---

## 1. Why Lily's Florist Protects Your Privacy

When you buy flowers online from most companies, your personal information is fed into a massive central customer relationship database (CRM). These databases store:
- Your full legal name, private phone number, and physical home address.
- The names of your loved ones (partner, mother, children, colleagues).
- The sensitive, heartfelt greeting card messages you write.
- A permanent log of every occasion you celebrate.

When these corporate databases get hacked or sold to advertisers, your intimate personal life is exposed.

**Lily's Florist does not believe in collecting honeypots of customer data.** We built our entire store on an architecture called **Zero-PII / Least-Data**. Instead of tracking you in the cloud, we give your phone an encrypted digital safe called the **Edge Wallet**.

---

## 2. What is the Edge Wallet?

The **Edge Wallet** is a private, hardware-encrypted storage vault built directly into the Lily's Florist Companion app on your Android phone.

- **Hardware-Level Encryption:** Your receipts and notes are encrypted using Android Keystore cryptographic keys (`AesGcmKey` / `AesSivKey`). Only your specific device can unlock them.
- **Never Uploaded to the Cloud:** The contents of your Edge Wallet remain strictly on your physical phone. They are **never** synced to a central server, backed up to our cloud, or shared with third parties.

---

## 3. What Stays on Your Phone vs. What the Florist Sees

To deliver beautiful flowers, our atelier needs to know what bouquet you ordered and when to bring it. But they do not need to keep a permanent dossier on you.

Here is the exact boundary:

| Information | Stays on Your Phone (Edge Wallet) | Seen by Florist Atelier | Stored in Cloud Database Forever |
|---|---|---|---|
| **Your Name & Email** | Stays on phone | Never asked or collected | **NEVER** |
| **Recipient Name** (*e.g., "Mom"*) | Encrypted on phone | Never sent over network | **NEVER** |
| **Card Message Drafts** | Encrypted on phone | Stays on phone until order | **NEVER** |
| **Bouquet Arrangement Ordered** | Saved in local receipt | Visible to florist for packing | Only anonymous SKU token |
| **Delivery Window** (*Morning / Afternoon*) | Saved in local receipt | Visible to delivery driver | Purged after fulfillment |
| **Handwritten Card Text** | Saved in local receipt | Printed on physical card | Purged after fulfillment |
| **Delivery Street Address** | Nickname (*"Home"*) on phone | Used during delivery trip only | **Shredded automatically after 14 days** |

---

## 4. How 1-Tap Reordering Works (FR-008)

Buying flowers for recurring celebrations (like Mother's Day, birthdays, or anniversaries) shouldn't require answering the same chatbot questions every single year.

The Edge Wallet makes reordering effortless while keeping you 100% anonymous. The returning-customer card appears only when a **local encrypted receipt** already exists — not on a first / empty Play install. Play Internal v8 cold-start Need on A36 and ROG (5 Sep 2026) showed suggestion chips only; Play tap remains Unknown (#407).

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. YOU OPEN THE APP OR START A NEW ARRANGEMENT                         │
│    Your phone reads your local encrypted receipt.                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. PRIVATE RETURNING-CUSTOMER CARD APPEARS                             │
│    Card: "Reorder for Mom"                                             │
│    "1-tap repeat order from this phone's encrypted wallet" [Reorder →] │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. 1-TAP INVENTORY REVALIDATION                                        │
│    Tapping [Reorder →] checks live stock in the florist cooler.        │
│    (Transmits only the bouquet SKU — ZERO personal data sent).         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. DIRECT TO PICK STAGE                                                │
│    The arrangement is pre-selected and ready to checkout instantly.    │
└────────────────────────────────────────────────────────────────────────┘
```

### Why this is safer than traditional "1-Click Checkout":
1. **No Account Required:** You don't need to create a username, choose a password, or verify your email.
2. **Fresh Stock Guaranteed:** The reorder doesn't blindly charge your card. It validates that the florist has fresh roses in the cooler today before presenting the order for your confirmation.
3. **Zero Tracking:** The florist backend sees an anonymous shopping session checking inventory availability; they have no idea *who* you are reordering for.

---

## 5. Customer Sovereignty & The Right to Be Forgotten

Your data belongs exclusively to you. You have absolute control over your shopping history:

- **Automatic Shredding:** Even for physical deliveries, our delivery database automatically shreds all temporary street addresses and phone numbers 14 days after the flowers arrive.
- **Instant Local Wipe:** If you want to wipe your past purchase history, tapping **Clear History** inside the app immediately destroys the cryptographic keys and deletes all encrypted receipts from your phone. No traces remain—on your device or on our servers.
