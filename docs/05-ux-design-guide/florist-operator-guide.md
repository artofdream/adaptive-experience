# Florist Operator Console User Guide (FR-013)

> **Document**: Florist Operator Console Operational Manual  
> **Audience**: Atelier florists, store managers, fulfillment staff, and support operators  
> **Console URL**: <https://aea.artof.link/florist> (or local <https://localhost:8443/florist>)  
> **Supported Devices**: Desktop (widescreen), Tablet, and Mobile Handheld (iOS / Android browser)  
> **Canonical Path**: docs/05-ux-design-guide/florist-operator-guide.md  
> **Traceability**: FR-013 (Staff Order List & Detail), FR-012 (Contact Florist Escalation), T-09, NFR-017 (Zero-PII / Least-Data)

---

## 1. Overview & Purpose

The **Florist Operator Console** (/florist) is a purpose-built, responsive web application designed for florist atelier staff. It runs directly inside modern web browsers (Chrome, Safari, Firefox, Edge) across laptops, tablets, and phones without requiring installation of a separate native app.

The console provides full operational visibility into live orders, batch bouquet preparation, and customer support inquiries while strictly upholding the **Least-Data Architecture (NFR-017)**:
- **What you see:** Bouquet title, count, delivery window, physical card message, fulfillment handle, and order status.
- **What is never exposed:** Raw customer names, personal phone numbers, full credit card details, or permanent tracking profiles.

---

## 2. Console Layout & Workspace Panels

The console is organized into four interconnected functional panels:

`
┌────────────────────────────────────────────────────────────────────────┐
│ Site Header: Lily's Florist · Operator           [Top Nav: Jump Pills]│
├────────────────────────────────────────────────────────────────────────┤
│ 1. STAFF ORDERS (#orders)                                              │
│    • Day filters: [Today] [3 days] [7 days] [Delayed] [All]            │
│    • 9-col table on desktop; collapses to 3 key cols on mobile phone   │
├────────────────────────────────────────────────────────────────────────┤
│ 2. TODAY'S ARRANGEMENTS TO PREPARE (#prepare)                          │
│    • Aggregated arrangement tallies by bouquet type                    │
│    • Delivery window counts (Morning, Afternoon, Evening)              │
│    • [Details ↗] opens enclosure card messages bottom-sheet dialog     │
├────────────────────────────────────────────────────────────────────────┤
│ 3. CONTACT FLORIST INBOX (#inbox)                                      │
│    • Live customer escalation requests (T-09)                          │
│    • Filter by Today, 3 days, 7 days, All                              │
│    • Click any inquiry row to jump to customer session context         │
├────────────────────────────────────────────────────────────────────────┤
│ 4. ORDER & SESSION INSPECTOR (#session)                                │
│    • Detailed fact list (channel, status, paid total, delivery handle) │
│    • Shared Understanding intent transcript audit                      │
└────────────────────────────────────────────────────────────────────────┘
`

---

## 3. The 4-Step Daily Shift Routine

To run the atelier efficiently, follow this standard 4-step routine throughout your shift:

### Step 1: Morning Batching & Arrangement Prep (#prepare)
1. Open <https://aea.artof.link/florist> at the start of your shift.
2. Tap **Prepare** on the top navigation bar or scroll to **Today's arrangements to prepare**.
3. Review the total counts for each bouquet type (e.g. *"5× Classic Rose Dozen"*, *"3× Budget Mixed Bunch"*).
4. Note the scheduled delivery windows (*"Morning: 3, Afternoon: 2"*).
5. Tap **Details ↗** next to any arrangement to open the **Arrangement Details** bottom-sheet dialog. Here you can:
   - Read the exact, full customer card messages for that batch.
   - Transcribe the messages onto physical handwritten greeting cards.
   - Tap **View related orders** to jump directly to those specific orders.

### Step 2: Order Fulfillment & Assembly (#orders)
1. Go to **Staff orders**.
2. By default, the list filters to **Today** with live order counts displayed on each filter pill.
3. Review the order queue:
   - Check the **Channel** badge: web (website checkout) or companion-android (mobile phone app).
   - Check the **Delivery Window**: prioritize morning orders before fternoon and evening.
   - Check the **Paid Total**: verifies that the checkout completed successfully.
4. As flowers are arranged and packed into delivery boxes, attach the handwritten card matching the order reference (ord-...).

### Step 3: Handling Customer Inquiries (#inbox)
1. Check the **Contact Florist inbox** panel periodically for incoming customer requests.
2. When a customer uses "Contact Florist" in their app, an entry appears with the timestamp, reason, and session reference.
3. Tap the row or the session link to automatically scroll to #session and load that customer's active chat context.
4. Review their message and address their request (e.g., updating delivery instructions or answering bouquet questions).

### Step 4: End-of-Day Review & Forecast
1. Switch the order filter to **Delayed** to ensure no order was missed or unfulfilled.
2. Switch to **3 days** or **7 days** to review upcoming scheduled deliveries and plan flower cooler replenishment with wholesale suppliers.

---

## 4. Multi-Device Ergonomics (Desktop, Tablet & Phone)

The operator console adapts intelligently to your screen size:

| Feature | Desktop / Laptop (>=1024px) | Tablet (768px - 1023px) | Mobile Phone (<768px) |
|---|---|---|---|
| **Staff Orders Layout** | Full 9 columns (Updated, Order, Status, Arrangement, Card, Channel, Paid, When, Destination) | 9 columns with horizontal scroll and responsive paddings | **Collapses to 3 clean columns**: Updated, Order & Arrangement, Status & Details (No horizontal scrolling) |
| **Order Details** | Displayed in table rows and inline in #session | Displayed in table and #session | Native bottom-sheet <dialog> opens on tapping Details ↗ |
| **Arrangement Prep** | 5 columns with card message preview | 5 columns with wrapped card chips | 3 columns: Arrangement, Count, Windows & Details (full cards in bottom sheet) |
| **Navigation** | Sticky top bar | Sticky top bar with quick nav | Wrapped touch-friendly pills (all >=44px) + floating ↑ and ↓ buttons |

### Touch Controls & Shortcuts
- **Jump Pills:** Tap Orders, Prepare, Inbox, or Session at the top of the screen to jump instantly without tedious thumb scrolling.
- **Floating Scroll Buttons:** The circular **↑** and **↓** buttons pinned at the bottom-right corner let you jump to the very top or very bottom of the page in one tap.
- **Escape Key / Close Button:** Any open details dialog can be dismissed by tapping **✕**, clicking the **Close** button, or pressing Esc on a keyboard.

---

## 5. Security, Flags & Privacy Architecture

The console operates under strict production safety boundaries:

1. **Fail-Closed Access Gate:**  
   The operator console only serves live data when AEA_FLORIST_OPERATOR=1 is configured. If disabled, all operator API endpoints return 404 Not Found or 403 Forbidden to protect shop integrity.
2. **CSRF Isolation:**  
   Always open /florist in a dedicated browser tab or window separate from any active customer shopping session to prevent cookie cross-contamination.
3. **Zero-PII / Least-Data Guarantee (NFR-017):**  
   Customer delivery street addresses and telephone numbers are processed through isolated, KMS-encrypted ephemeral storage and automatically shredded 14 days after delivery. Staff see fulfillment destination handles (home, work) and scheduled windows, preserving customer privacy at all times.
