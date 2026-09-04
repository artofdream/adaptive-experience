# Strategic Architecture Study: Florist Operator Multi-Device Responsive Architecture & Ergonomic Console Design

#aea #operator #mobile-ux #responsive #least-data #ergonomics #accessibility #fr-013 #second-brain

**Date:** 2026-09-04  
**Authors:** `@aea-knowledge-guardian`, `@aea-ux-designer` & `@aea-senior-software-engineer`  
**Repository:** `artof-group/adaptive-experience-architecture`  
**Target Scope:** Florist Operator Console (`/florist`), Multi-Device UI/UX (Mobile, Tablet, Desktop), FR-013 Staff Orders & Prepare Lists, Least-Data Privacy (ADR-020 / NFR-017)  
**Related Documents:** [[2026-09-04-session-memory-log-florist-operator-mobile-ux]] · [[2026-09-03-florist-today-prepare-list-395]] · [[2026-09-02-least-data-crm-privacy-preserving-order-insights]] · [[2026-09-02-native-web-florist-story-plain-language]]

---

## 1. Executive Summary & Operational Context

In modern retail and boutique florist operations, operators rarely sit stationary in front of a laptop. Florists move constantly between the arranging workbench, refrigerated storage, delivery dispatch staging, and the customer counter. Handheld mobile phones and counter-mounted tablets are the primary computing form factors in the field.

Prior to this work, the Lily's Florist Operator Console (`https://aea.artof.link/florist`) was optimized primarily for wide desktop viewports. When accessed from a mobile phone (e.g., viewport width 360px–412px), the interface suffered critical usability breakdowns:
1. **Column Crush & Single-Character Word Wrapping**: The 9-column **Staff Orders** table and 5-column **Today's Arrangements to Prepare** table were compressed horizontally. Coupled with `overflow-wrap: anywhere`, text broke character-by-character into single-letter vertical cascades (`U \n p \n d \n a \n t \n e \n d`, `s \n u \n b \n m \n i \n t \n t \n e \n d`, and delivery dates split across 12 lines).
2. **Icon & Text Collision**: Table headers injected with inline SVG icons suffered severe visual collisions (e.g., `Arrangement# Count` where a 4-line grid icon collided with adjacent header labels).
3. **Below-the-Fold Disconnect**: Tapping an order row updated `#session` facts far below the fold with zero immediate visual confirmation on small screens.
4. **Scroll Fatigue**: Navigating between Staff Orders, Today's Prepare, Contact Florist Inbox, Session Facts, and Demand Forecast required hundreds of pixels of repetitive swiping.

This study codifies the complete set of architectural patterns, design decisions, touch ergonomics, and code implementations established to transform the Florist Operator Console into a responsive, accessible, multi-device operational tool while preserving laptop data density and Least-Data privacy invariants.

---

## 2. Multi-Device Viewport Breakpoints & Ergonomic Matrix

The operator interface adheres to a 3-tier viewport matrix balancing high information density on desktop with touch targets and legibility on mobile:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MULTI-DEVICE ADAPTATION MATRIX                         │
├──────────────────────┬─────────────────────────┬───────────────────────────────────────┤
│ Form Factor          │ Viewport Range          │ UX & Layout Paradigm                  │
├──────────────────────┼─────────────────────────┼───────────────────────────────────────┤
│ **Mobile Phone**     │ `< 48rem` (< 768px)     │ • 3-column collapsed tables (Col 1-3) │
│                      │                         │ • Columns 4+ surfaced via Overlays    │
│                      │                         │ • Bottom-sheet drawer modals          │
│                      │                         │ • Horizontal quick-nav pill bar       │
│                      │                         │ • Floating Top/Bottom scroll buttons  │
├──────────────────────┼─────────────────────────┼───────────────────────────────────────┤
│ **Tablet**           │ `48rem` – `60rem`       │ • 2-column paired fact grid           │
│ (iPad / Slate)       │ (768px – 1024px)        │ • Contained horizontal table panning  │
│                      │                         │ • Centered modal dialogs              │
│                      │                         │ • 44px touch targets enforced         │
├──────────────────────┼─────────────────────────┼───────────────────────────────────────┤
│ **Laptop / Desktop** │ `>= 64rem` (>= 1024px)  │ • Full 9-column Staff Orders table    │
│                      │                         │ • Full 5-column Prepare table         │
│                      │                         │ • Side-by-side workspace split layout │
│                      │                         │ • High data density for desk work     │
└──────────────────────┴─────────────────────────┴───────────────────────────────────────┘
```

---

## 3. Responsive Table Architecture & 3-Column Collapsing

The core breakthrough was adopting the proven 3-column layout of the **Contact Florist Inbox** (`Requested`, `Reason`, `Session`) as the universal mobile standard across all operator tables.

### A. Staff Orders Table (`#orders`)
- **Desktop (9 columns)**: `Updated`, `Order`, `Status`, `Arrangement`, `Card`, `Channel`, `Paid`, `When`, `Destination`.
- **Mobile Collapsed (3 columns)**:
  - **Column 1 (`Updated`)**: Dedicated `.operator-cell-date` with non-breaking 2-line layout (`date-day` on top, `date-time` underneath) using tabular numerals (`font-variant-numeric: tabular-nums`).
  - **Column 2 (`Order & Arrangement`)**: Order reference button (`ord-...`) with arrangement title and channel badge stacked underneath (`.order-cell-main`).
  - **Column 3 (`Status & Details`)**: Status badge (`submitted`, `delayed`, `preparing`) stacked above an explicit `Details ↗` button (`.order-detail-trigger`).
- **Hiding Strategy**: CSS rule `.operator-table-orders th:nth-child(n+4), .operator-table-orders td:nth-child(n+4) { display: none; }` cleanly eliminates horizontal crushing.

### B. Today's Arrangements to Prepare (`#prepare`)
- **Desktop (5 columns)**: `Arrangement`, `Count`, `Windows`, `Cards`, `Channels`.
- **Mobile Collapsed (3 columns)**:
  - **Column 1 (`Arrangement & Metadata`)**: Prominent arrangement title (`.prepare-title-main`) with inline metadata (`.prepare-mobile-meta`) displaying card message snippets and channel badges.
  - **Column 2 (`Count`)**: Centered badge (`.order-status-badge`) displaying total units to prepare.
  - **Column 3 (`Windows & Details`)**: Scheduled delivery window tags (`.prepare-windows-text`) plus a `Details ↗` trigger button (`.prepare-detail-trigger`).
- **Hiding Strategy**: CSS rules `.operator-table-prepare th:nth-child(n+4), #prepare .operator-table th:nth-child(n+4)` hide columns 4 and 5 on mobile viewports.

---

## 4. Native Bottom-Sheet Overlay Architecture

To prevent small screens from becoming cluttered while ensuring no operational data is lost, secondary and detailed attributes are surfaced via HTML5 `<dialog>` elements styled as native mobile bottom-sheet drawers.

```
┌────────────────────────────────────────────────────────┐
│                  NATIVE BOTTOM-SHEET DRAWER            │
├────────────────────────────────────────────────────────┤
│                    [── Sheet Handle ──]                │
│                                                        │
│  FR-013 · Today's prepare grouping              [✕]    │
│  Arrangement details                                   │
│                                                        │
│  Arrangement:   Pastel Pitcher Trio                    │
│  Quantity:      3 to prepare                           │
│  Delivery:      morning, evening                       │
│  Channels:      web, companion-android                 │
│  Related:       ord-e01, ord-e04, ord-e05              │
│                                                        │
│  Customer Card Messages                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ "Happy 70th Birthday Mum! With all our love..."  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  [ View related orders ]             [ Close ]         │
└────────────────────────────────────────────────────────┘
```

### Overlay Specifications
1. **Order Detail Dialog (`<dialog id="order-detail-dialog">`)**:
   - Triggered by tapping `Details ↗` or any order row on screens `<= 768px`.
   - Surfaces all 9 facts: Order ID, Status, Delayed Flag, Arrangement, When, Card Message, Channel, Payment State, and Destination Handle.
   - Quotes customer card messages in dedicated styled blocks (`.dialog-card-note`).
   - Provides a *"Jump to session transcript ↓"* action that dismisses the dialog, activates the session, and scrolls directly to `#session`.
2. **Arrangement Prepare Dialog (`<dialog id="prepare-detail-dialog">`)**:
   - Triggered by tapping `Details ↗` or any prepare row on screens `<= 768px`.
   - Displays full uncapped card messages (bypassing the 40-character table truncation).
   - Surfaces delivery windows, channels, and associated order IDs.
   - Provides a *"View related orders"* action that automatically switches the order filter and scrolls smoothly to `#orders`.
3. **Modal Semantics & Keyboard Accessibility**:
   - Opened via native `dialog.showModal()` with backdrop dimming (`rgba(27, 18, 48, 0.45)`).
   - Closes via `Escape` key, backdrop click, or explicit `Close` / `✕` buttons.

---

## 5. Touch Ergonomics, Iconography & Navigation Controls

### A. Floating Bidirectional Scroll Controls (`.operator-scroll-controls`)
- Pinned to bottom-right (`position: fixed; bottom: 1.25rem; right: 1.25rem; z-index: 90;`).
- Circular action buttons (`#scroll-to-top` `↑` and `#scroll-to-bottom` `↓`) with 44×44px tap targets.
- Soft lavender drop shadow (`box-shadow: 0 4px 14px rgba(76, 47, 138, 0.22)`) with hover/focus translation (`translateY(-2px)`).
- Executes programmatic smooth scrolling:
  - Top: `window.scrollTo({ top: 0, behavior: 'smooth' });`
  - Bottom: `window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });`

### B. Segmented Filter Controls (`.operator-filter-wrap`)
- Replaced plain text hyperlinks with an accessible segmented pill control (`Today`, `Delayed`, `All`).
- Active pill highlighted with solid lavender background (`var(--lavender)`), high-contrast purple text (`var(--purple-deep)`), and subtle box-shadow.
- Min-height 44px tap target ensures operators with gloved or wet hands can toggle filters reliably.

### C. Quick Anchor Bar (`.operator-nav`)
- Sticky horizontal navigation bar with smooth-scrolling chip buttons (`#orders`, `#prepare`, `#inbox`, `#session`, `#forecast`).
- Styled with `overflow-x: auto` and `white-space: nowrap` for horizontal swiping on mobile.

### D. Table Header Iconography & Typography
- **Header Alignment**: Wrapped SVG icons and labels in `.th-wrap` (`display: inline-flex; align-items: center; gap: 0.35rem; white-space: nowrap;`).
- **Symbol Clarity**: Replaced the ambiguous 4-line intersecting grid icon with a clean 4-square tally symbol for `Count`.
- **Word Wrapping Normalization**: Replaced disruptive `overflow-wrap: anywhere` with `overflow-wrap: break-word; word-break: normal;` to ensure words break naturally at word boundaries.

---

## 6. Least-Data Privacy & Security Boundaries (ADR-020 / NFR-017)

All operator enhancements strictly respect the zero-PII and least-data perimeter:
1. **Opaque Destination Handles**: The console surfaces destination handles (`home`, `work`, `dest-ref-1`) via `destinationHandleLabel()`. At no point are raw physical street addresses, unit numbers, or customer names transmitted or rendered.
2. **Payment State Isolation**: Payment information is limited to abstract state tokens (`paid`, `authorized`, `pending`). No credit card PANs, tokens, or billing addresses exist in the operator data path.
3. **Same-Origin CSRF Isolation**: As documented in the console header note, the florist console is run in an operator session separate from the customer shopping workspace to eliminate CSRF cross-contamination.

---

## 7. Automated Test Suite & Quality Guard Evidence

Every UI enhancement is permanently verified by automated test harnesses:

1. **Browser UI Unit Tests (`edge/tests/test_browser_ui.py`)**:
   - `test_florist_operator_console_is_separate_labeled_sample`: Asserts labeled sample status, isolation from customer workspace, and API routing.
   - `test_florist_today_prepare_list_is_derived_from_staff_orders`: Asserts that prepare items are derived directly from staff orders without separate PII APIs.
   - `test_florist_operator_mobile_table_and_order_overlay`: Asserts all markup, dialogs, scroll buttons, CSS classes, and JavaScript event bindings.
   - **Result**: 26/26 tests passed in `0.025s`.
2. **Edge Integration Suite (`edge/tests`)**:
   - All 77 tests in `edge/tests` passed in `0.572s`.
3. **Local Docker Integration Tests (`edge/scripts/run_integration_tests.py`)**:
   - Verified end-to-end container operation: Nginx reverse proxy, BFF gateway, PostgreSQL inventory, and assistant SLO guard (p95 latency 2.40s <= 3.00s; availability 99.9%).
4. **AEA Unified Pre-Flight Quality Guards (`scripts/run_all_guards.py`)**:
   - Verified 14/14 pre-flight guards clean (Coherence, Secrets, Traceability DAG, Governance Loop, SLO, Property Graph, Knowledge Graph, Reorder Service, Payment Simulation, Stakeholder Skills Sync, Second Brain Knowledge Graph).

---

## 8. Lessons Learned & Reusable Principles for Future AEA Consoles

1. **The 3-Column Maximum for Mobile Tables**: Data tables on mobile devices (`<= 48rem`) should never exceed 3 primary columns. All additional attributes must be routed to progressive disclosure overlays.
2. **Pairing Text and Icons in Flex Wrappers**: Never rely on raw inline text adjacent to SVG elements in table headers. Always enclose them in an `inline-flex` container with `white-space: nowrap` and defined `gap`.
3. **Two-Tier Modals**: Bottom-sheet drawers with drag handles represent the standard UX pattern for mobile operations, while centered modals remain the standard for desktop. Using CSS media queries on `<dialog>` allows one semantic HTML element to seamlessly serve both form factors.
4. **Persistent Scroll Anchors**: Long operational consoles benefit substantially from floating Top/Bottom scroll controls, reducing cognitive overhead and ergonomic strain during high-volume shifts.
