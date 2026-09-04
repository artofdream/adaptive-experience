const TOKEN = "local-browser-token";
const SAMPLE_ORDERS = [
  {
    order_id: "ord-sample-1",
    session_id: "11111111-1111-4111-8111-111111111111",
    status: "preparing",
    delayed: false,
    authoritative_status: "preparing",
    product_id: "classic-rose-dozen",
    catalog_title: "Classic Rose Dozen",
    destination_reference: "dest-ref-1",
    timing: { date: "2026-08-16", window: "morning" },
    card_message: "Happy birthday Mum",
    channel: "web",
    payment_state: "paid",
    updated_at: "2026-08-15T08:20:00+00:00",
    sample: true,
  },
  {
    order_id: "ord-sample-2",
    session_id: "22222222-2222-4222-8222-222222222222",
    status: "dispatched",
    delayed: true,
    authoritative_status: "delayed",
    product_id: "lilac-bouquet",
    catalog_title: "Lilac Bouquet",
    destination_reference: "dest-ref-2",
    timing: { date: "2026-08-15", window: "afternoon" },
    card_message: "Thinking of you",
    channel: "companion-android",
    payment_state: "declined",
    updated_at: "2026-08-15T07:50:00+00:00",
    sample: true,
  },
];
const SAMPLE_INBOX = [
  {
    message_id: "sample-esc-1",
    session_id: "11111111-1111-4111-8111-111111111111",
    escalation_reason: "unresolved_request",
    context_reference: "11111111-1111-4111-8111-111111111111",
    requested_at: "2026-08-15T08:12:00+00:00",
    sample: true,
  },
  {
    message_id: "sample-esc-2",
    session_id: "22222222-2222-4222-8222-222222222222",
    escalation_reason: "delivery_issue",
    context_reference: "22222222-2222-4222-8222-222222222222",
    requested_at: "2026-08-15T07:41:00+00:00",
    sample: true,
  },
  {
    message_id: "sample-esc-3",
    session_id: "33333333-3333-4333-8333-333333333333",
    escalation_reason: "product_question",
    context_reference: "33333333-3333-4333-8333-333333333333",
    requested_at: "2026-08-14T16:05:00+00:00",
    sample: true,
  },
];
const SAMPLE_SESSIONS = {
  "11111111-1111-4111-8111-111111111111": {
    session_id: "11111111-1111-4111-8111-111111111111",
    context_version: 6,
    conversation: { messages: [
      { message_id: "m1", role: "customer", text: "Birthday roses for Mum, under 75", status: "submitted", submitted_at: "2026-08-15T08:00:00+00:00" },
      { message_id: "m2", role: "assistant", text: "I can help with a classic rose dozen. Review the interpretation before ordering.", status: "visible", submitted_at: "2026-08-15T08:00:04+00:00" },
    ] },
    shared_understanding: { structured_intent: { occasion: "birthday", recipient: "Mum", budget: "75" } },
    order: { order_id: "ord-sample-1", status: "preparing", delayed: false, authoritative_status: "preparing", channel: "web", total: 82, currency: "EUR", payment_state: "unpaid" },
    selection: { product_id: "classic-rose-dozen", catalog_title: "Classic Rose Dozen", card_message: "Happy birthday Mum" },
    delivery: { destination_reference: "dest-ref-1", timing: { date: "2026-08-16", window: "morning" } },
    availability: [
      { product_id: "classic-rose-dozen", available: true, availability_status: "available" },
      { product_id: "premium-orchid", available: false, availability_status: "unknown" },
    ],
    support_answers: [
      {
        kind: "faq",
        answer: "Standard orders placed before 2 PM are delivered the same day; later orders arrive the next day.",
        approved_source_references: ["policy:delivery"],
        answered_at: "2026-08-15T08:05:00+00:00",
        sample: true,
      },
    ],
  },
  "22222222-2222-4222-8222-222222222222": {
    session_id: "22222222-2222-4222-8222-222222222222",
    context_version: 9,
    conversation: { messages: [
      { message_id: "d1", role: "customer", text: "The window changed and nobody told me.", status: "submitted", submitted_at: "2026-08-15T07:30:00+00:00" },
    ] },
    shared_understanding: { structured_intent: { occasion: "anniversary", timing: "this weekend" } },
    order: { order_id: "ord-sample-2", status: "dispatched", delayed: true, authoritative_status: "delayed", channel: "companion-android", total: 107, currency: "EUR", payment_state: "paid" },
    selection: { product_id: "lilac-bouquet", catalog_title: "Lilac Bouquet", card_message: "Thinking of you" },
    delivery: { destination_reference: "dest-ref-2", timing: { date: "2026-08-15", window: "afternoon" } },
    availability: [
      { product_id: "lilac-bouquet", available: true, availability_status: "available" },
    ],
    support_answers: [
      {
        kind: "situation",
        situation_kind: "order_status",
        answer: "Your order is currently delayed.",
        fact_references: ["session:order"],
        answered_at: "2026-08-15T07:35:00+00:00",
        sample: true,
      },
    ],
  },
  "33333333-3333-4333-8333-333333333333": {
    session_id: "33333333-3333-4333-8333-333333333333",
    context_version: 2,
    conversation: { messages: [
      { message_id: "p1", role: "customer", text: "Can you substitute peonies if roses are unknown?", status: "submitted", submitted_at: "2026-08-14T16:00:00+00:00" },
    ] },
    shared_understanding: { structured_intent: { flower_preference: "peonies", style: "garden" } },
    order: null,
    selection: null,
    delivery: null,
    availability: [
      { product_id: "classic-rose-dozen", available: false, availability_status: "unknown" },
      { product_id: "budget-mixed-bunch", available: false, availability_status: "unknown" },
    ],
    support_answers: [
      {
        kind: "faq",
        answer: "If a stem is unavailable we substitute a similar flower of equal or greater value, preserving the style.",
        approved_source_references: ["policy:substitution"],
        answered_at: "2026-08-14T16:02:00+00:00",
        sample: true,
      },
    ],
  },
};

const SAMPLE_FORECASTS = [
  {
    product_id: "classic-rose-dozen",
    trend: "declining",
    recommendation: "Quantity declined from 10 to 4; about 2 days to stockout at this rate. Plan a replenishment.",
    sample: true,
  },
  {
    product_id: "lilac-bouquet",
    trend: "stable",
    recommendation: "Quantity is stable at 8; no replenishment recommended.",
    sample: true,
  },
  {
    product_id: "budget-mixed-bunch",
    trend: "insufficient",
    recommendation: "This product has only one validated snapshot; no trend yet.",
    sample: true,
  },
];

const REASON_LABELS = {
  unresolved_request: "Unresolved request",
  delivery_issue: "Delivery issue",
  product_question: "Product question",
};
const FACET_LABELS = {
  occasion: "Occasion",
  recipient: "Recipient",
  budget: "Budget",
  style: "Style",
  flower_preference: "Flower preference",
  timing: "Timing",
};
const TREND_LABELS = {
  declining: "Declining",
  stable: "Stable",
  insufficient: "Not enough history",
};

const mode = document.querySelector("#operator-mode");
const orderRows = document.querySelector("#order-rows");
const prepareRows = document.querySelector("#prepare-rows");
const inboxRows = document.querySelector("#inbox-rows");
const forecastRows = document.querySelector("#forecast-rows");
const transcript = document.querySelector("#transcript");
const supportAnswers = document.querySelector("#support-answers");
const orderFacts = document.querySelector("#order-facts");
const availability = document.querySelector("#availability");
const sessionRef = document.querySelector("#session-ref");

const state = {
  csrf: "",
  live: false,
  items: SAMPLE_INBOX,
  orders: SAMPLE_ORDERS,
  orderFilter: "today",
  inboxFilter: "all",
  ordersError: false,
  selectedId: "",
};

function headers(extra) {
  return {
    Authorization: `Bearer ${TOKEN}`,
    "X-AEA-Client": "web",
    Origin: window.location.origin,
    ...extra,
  };
}

async function ensureSession() {
  const session = await api("/api/v1/session", { method: "POST", _retried: true });
  state.csrf = session.csrf_token;
  return session;
}

async function api(path, options = {}) {
  const method = options.method || "GET";
  const init = {
    method,
    headers: headers(options.headers || {}),
    credentials: "same-origin",
  };
  if (state.csrf && path !== "/api/v1/session"
      && ["POST", "PUT", "PATCH", "DELETE"].includes(method.toUpperCase())) {
    init.headers["X-CSRF-Token"] = state.csrf;
  }
  if (options.body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(options.body);
  }
  const response = await fetch(path, init);
  const payload = response.headers.get("content-type")?.includes("application/json")
    ? await response.json() : await response.text();
  if (!response.ok) {
    const code = payload && payload.error || payload && payload.code || `http_${response.status}`;
    if (!options._retried && path !== "/api/v1/session"
        && (code === "csrf_rejected" || code === "session_required")) {
      await ensureSession();
      return api(path, { ...options, _retried: true });
    }
    const error = new Error(code);
    error.status = response.status;
    throw error;
  }
  return payload;
}

function shortRef(value) {
  const text = String(value || "");
  return text.length > 12 ? `${text.slice(0, 8)}…${text.slice(-4)}` : text;
}

/** Least-data fulfillment handle for florist (#382). Kinds only — no address fields. */
const DESTINATION_KIND_LABELS = {
  home: "Home",
  work: "Work",
  other: "Other saved place",
};
function destinationHandleLabel(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const key = raw.toLowerCase();
  if (DESTINATION_KIND_LABELS[key]) return DESTINATION_KIND_LABELS[key];
  return shortRef(raw);
}

function reasonLabel(value) {
  const key = String(value || "");
  return REASON_LABELS[key] || key.replaceAll("_", " ");
}

function facetLabel(key) {
  return FACET_LABELS[key] || key.replaceAll("_", " ");
}

function formatRequested(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatRequestedDateHtml(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  const dayStr = new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
  const timeStr = new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
  return `<div class="operator-cell-date"><span class="date-day">${dayStr}</span><span class="date-time">${timeStr}</span></div>`;
}

const TABLE_HEADER_ICONS = {
  Updated: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  Requested: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  Order: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
  Status: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>`,
  Arrangement: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a5 5 0 0 1 5 5c0 2.3-1.5 4.3-3.6 4.9.4.7.6 1.4.6 2.1 0 2.8-2.2 5-5 5s-5-2.2-5-5c0-.7.2-1.4.6-2.1C2.5 11.3 1 9.3 1 7a5 5 0 0 1 5-5c1.4 0 2.6.6 3.5 1.5A4.98 4.98 0 0 1 12 2z"/><line x1="12" y1="14" x2="12" y2="22"/></svg>`,
  Card: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`,
  Cards: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>`,
  Channel: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>`,
  Channels: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>`,
  Paid: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>`,
  When: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  Windows: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  Destination: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  Reason: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  Session: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`,
  Count: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>`,
  Product: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>`,
  Trend: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>`,
  Recommendation: `<svg class="th-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg>`,
};

function decorateHeaderIcons() {
  document.querySelectorAll(".operator-table th").forEach((th) => {
    const text = th.textContent.trim();
    if (TABLE_HEADER_ICONS[text] && !th.querySelector(".th-icon")) {
      th.innerHTML = `${TABLE_HEADER_ICONS[text]} <span class="th-label">${text}</span>`;
    }
  });
}

function emptyRow(columns, copy) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = columns;
  cell.className = "operator-empty";
  cell.textContent = copy;
  row.append(cell);
  return row;
}

function renderForecasts(items) {
  forecastRows.replaceChildren();
  if (!items.length) {
    forecastRows.append(emptyRow(3, "No validated inventory snapshots yet. Forecast stays empty until history exists."));
    return;
  }
  for (const item of items) {
    const row = document.createElement("tr");
    const trend = TREND_LABELS[item.trend] || item.trend;
    row.innerHTML = `<td><code>${item.product_id}</code></td>
      <td><span class="badge">${trend}</span></td>
      <td>${item.recommendation}</td>`;
    forecastRows.append(row);
  }
}

function formatWhen(timing) {
  if (!timing || typeof timing !== "object") return "—";
  const parts = [timing.date, timing.window].filter(Boolean);
  return parts.length ? parts.join(" · ") : "—";
}

function todayIso(now = new Date()) {
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function isTodayOrder(item, today = todayIso()) {
  const date = item?.timing?.date;
  if (date === today) return true;
  if (!item?.updated_at) return false;
  const updated = new Date(item.updated_at);
  if (Number.isNaN(updated.getTime())) return false;
  return todayIso(updated) === today;
}

function isDelayedOrder(item) {
  return Boolean(item?.delayed) || item?.authoritative_status === "delayed";
}

function sessionIdSet(items) {
  return new Set((items || []).map((item) => item.session_id).filter(Boolean));
}

// Day-window filtering (#398): parse a YYYY-MM-DD date or an ISO datetime to a
// local calendar date so the window comparison is timezone-stable and matches
// isTodayOrder's string semantics for timing.date.
function toLocalDate(value) {
  if (!value) return null;
  const s = String(value);
  const ymd = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (ymd) return new Date(Number(ymd[1]), Number(ymd[2]) - 1, Number(ymd[3]));
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? null : new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

function dayDiffFromToday(value, now = new Date()) {
  const d = toLocalDate(value);
  if (!d) return null;
  const base = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((d.getTime() - base.getTime()) / 86400000);
}

/** True when value's calendar date is within +/- n days of today. n=0 => today. */
function isWithinDays(value, n) {
  const diff = dayDiffFromToday(value);
  return diff !== null && Math.abs(diff) <= n;
}

/** An order counts for a day window by its delivery date (timing.date) or last update. */
function orderWithinDays(item, n) {
  return isWithinDays(item?.timing?.date, n) || isWithinDays(item?.updated_at, n);
}

function filterOrders(items, filter = state.orderFilter) {
  const list = Array.isArray(items) ? items : [];
  if (filter === "delayed") return list.filter(isDelayedOrder);
  if (filter === "today") return list.filter((item) => isTodayOrder(item));
  if (filter === "3d") return list.filter((item) => orderWithinDays(item, 3));
  if (filter === "7d") return list.filter((item) => orderWithinDays(item, 7));
  return list;
}

// Per-section day filter for the Contact Florist inbox, by requested_at (#398).
function filterInbox(items, filter = state.inboxFilter) {
  const list = Array.isArray(items) ? items : [];
  if (filter === "today") return list.filter((item) => isWithinDays(item?.requested_at, 0));
  if (filter === "3d") return list.filter((item) => isWithinDays(item?.requested_at, 3));
  if (filter === "7d") return list.filter((item) => isWithinDays(item?.requested_at, 7));
  return list;
}

const ORDER_FILTER_IDS = {
  "order-filter-today": "today",
  "order-filter-3d": "3d",
  "order-filter-7d": "7d",
  "order-filter-delayed": "delayed",
  "order-filter-all": "all",
};
const INBOX_FILTER_IDS = {
  "inbox-filter-today": "today",
  "inbox-filter-3d": "3d",
  "inbox-filter-7d": "7d",
  "inbox-filter-all": "all",
};

function uniqueSorted(values) {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

function groupPrepareItems(items) {
  // Live: today by timing.date or updated_at. Labeled sample keeps all rows so grouping is visible.
  const source = state.live ? filterOrders(items, "today") : (Array.isArray(items) ? items : []);
  const groups = new Map();
  for (const item of source) {
    if (!item || typeof item !== "object") continue;
    const key = item.catalog_title || item.product_id || "unknown";
    if (!groups.has(key)) {
      groups.set(key, {
        title: item.catalog_title || item.product_id || "—",
        count: 0,
        windows: [],
        cards: [],
        channels: [],
      });
    }
    const group = groups.get(key);
    group.count += 1;
    const when = formatWhen(item.timing);
    if (when !== "—") group.windows.push(when);
    if (item.card_message) group.cards.push(String(item.card_message).slice(0, 40));
    if (item.channel) group.channels.push(item.channel);
  }
  return Array.from(groups.values()).sort((a, b) => String(a.title).localeCompare(String(b.title)));
}

function renderPrepare(items) {
  if (!prepareRows) return;
  prepareRows.replaceChildren();
  if (state.live && state.ordersError) {
    prepareRows.append(emptyRow(5, "Could not load today's arrangements. This list stays empty."));
    return;
  }
  const groups = groupPrepareItems(items);
  if (!groups.length) {
    const copy = state.live
      ? "No arrangements to prepare today."
      : "Labeled sample has no rows in this layout.";
    prepareRows.append(emptyRow(5, copy));
    return;
  }
  for (const group of groups) {
    const row = document.createElement("tr");
    const cards = uniqueSorted(group.cards).slice(0, 2).join("; ") || "—";
    const channels = uniqueSorted(group.channels).join(" · ") || "—";
    const cardMeta = cards !== "—" ? `<span class="prepare-mobile-cards">“${cards}”</span>` : "";
    const channelMeta = channels !== "—" ? `<span><code>${channels}</code></span>` : "";
    const mobileMeta = (cardMeta || channelMeta)
      ? `<div class="prepare-mobile-meta">${cardMeta}${channelMeta}</div>`
      : "";
    row.innerHTML = `<td>
        <span class="prepare-title-main">${group.title}</span>
        ${mobileMeta}
      </td>
      <td>${group.count}</td>
      <td>${uniqueSorted(group.windows).join(" · ") || "—"}</td>
      <td>${cards}</td>
      <td><code>${channels}</code></td>`;
    prepareRows.append(row);
  }
}

function syncOrderFilterButtons() {
  for (const [id, value] of Object.entries(ORDER_FILTER_IDS)) {
    const button = document.querySelector(`#${id}`);
    if (button) button.setAttribute("aria-pressed", String(state.orderFilter === value));
  }
}

function syncInboxFilterButtons() {
  for (const [id, value] of Object.entries(INBOX_FILTER_IDS)) {
    const button = document.querySelector(`#${id}`);
    if (button) button.setAttribute("aria-pressed", String(state.inboxFilter === value));
  }
}

function renderOrders(items) {
  if (!orderRows) return;
  orderRows.replaceChildren();
  if (Array.isArray(items)) state.orders = items;
  renderPrepare(state.orders);
  const visible = filterOrders(state.orders, state.orderFilter);
  syncOrderFilterButtons();
  if (!state.orders.length) {
    orderRows.append(emptyRow(9, "No companion or website orders yet. This list stays empty until a checkout writes through."));
    decorateHeaderIcons();
    return;
  }
  if (!visible.length) {
    const ORDER_EMPTY_COPY = {
      delayed: "No delayed orders.",
      today: "No orders for today.",
      "3d": "No orders in the next 3 days.",
      "7d": "No orders in the next 7 days.",
    };
    const copy = ORDER_EMPTY_COPY[state.orderFilter] || "No orders in this range.";
    orderRows.append(emptyRow(9, copy));
    decorateHeaderIcons();
    return;
  }
  for (const item of visible) {
    const row = document.createElement("tr");
    if (item.session_id === state.selectedId) row.className = "is-selected";
    row.setAttribute("data-session", item.session_id);
    const sample = item.sample ? ' <span class="status">Sample</span>' : "";
    const inboxLink = sessionIdSet(state.items).has(item.session_id)
      ? ' <span class="badge">Inbox</span>' : "";
    const statusText = item.authoritative_status || item.status || "—";
    const arrangement = item.catalog_title || item.product_id || "—";
    const card = item.card_message ? String(item.card_message).slice(0, 40) : "—";
    const channel = item.channel || "—";
    const paid = item.payment_state || "—";
    row.innerHTML = `<td>${formatRequestedDateHtml(item.updated_at)}</td>
      <td>
        <div class="order-cell-main">
          <div><button type="button" class="text-link" data-session="${item.session_id}" data-order-id="${item.order_id}">${shortRef(item.order_id)}</button>${sample}${inboxLink}</div>
          <div class="order-mobile-meta">
            <span class="order-arrangement-mobile">${arrangement}</span>
            <span class="order-channel-mobile"><code>${channel}</code></span>
          </div>
        </div>
      </td>
      <td>
        <div class="status-cell-main">
          <span class="badge">${statusText}</span>
          <button type="button" class="text-link order-detail-trigger" data-order-id="${item.order_id}" aria-label="View details for order ${item.order_id}">Details ↗</button>
        </div>
      </td>
      <td>${arrangement}</td>
      <td>${card}</td>
      <td><code>${channel}</code></td>
      <td><span class="badge">${paid}</span></td>
      <td>${formatWhen(item.timing)}</td>
      <td>${destinationHandleLabel(item.destination_reference)}</td>`;
    orderRows.append(row);
  }
  decorateHeaderIcons();
}

document.querySelectorAll(Object.keys(ORDER_FILTER_IDS).map((id) => `#${id}`).join(",")).forEach((button) => {
  button.addEventListener("click", () => {
    state.orderFilter = ORDER_FILTER_IDS[button.id] || "today";
    renderOrders(state.orders);
  });
});

document.querySelectorAll(Object.keys(INBOX_FILTER_IDS).map((id) => `#${id}`).join(",")).forEach((button) => {
  button.addEventListener("click", () => {
    state.inboxFilter = INBOX_FILTER_IDS[button.id] || "all";
    renderInbox(state.items);
  });
});

function renderInbox(items) {
  if (Array.isArray(items)) state.items = items;
  const full = Array.isArray(state.items) ? state.items : [];
  inboxRows.replaceChildren();
  syncInboxFilterButtons();
  if (!full.length) {
    inboxRows.append(emptyRow(3, "No Contact Florist requests yet. This inbox stays empty until a customer uses T-09."));
    decorateHeaderIcons();
    return;
  }
  const visible = filterInbox(full, state.inboxFilter);
  if (!visible.length) {
    inboxRows.append(emptyRow(3, "No Contact Florist requests in this day range."));
    decorateHeaderIcons();
    return;
  }
  for (const item of visible) {
    const row = document.createElement("tr");
    if (item.session_id === state.selectedId) row.className = "is-selected";
    const sample = item.sample ? ' <span class="status">Sample</span>' : "";
    const orderLink = sessionIdSet(state.orders).has(item.session_id)
      ? ' <span class="badge">Has order</span>' : "";
    row.innerHTML = `<td>${formatRequestedDateHtml(item.requested_at)}</td>
      <td><button type="button" class="text-link" data-session="${item.session_id}">${reasonLabel(item.escalation_reason)}</button>${sample}${orderLink}</td>
      <td><code>${shortRef(item.context_reference || item.session_id)}</code></td>`;
    inboxRows.append(row);
  }
  decorateHeaderIcons();
}

function fact(term, value) {
  const dt = document.createElement("dt");
  dt.textContent = term;
  const dd = document.createElement("dd");
  dd.textContent = value;
  orderFacts.append(dt, dd);
}

function renderSession(summary, label) {
  sessionRef.textContent = label;
  transcript.replaceChildren();
  const messages = summary.conversation?.messages || [];
  if (!messages.length) {
    const empty = document.createElement("p");
    empty.className = "operator-empty";
    empty.textContent = "No messages in this session yet.";
    transcript.append(empty);
  }
  for (const message of messages) {
    const p = document.createElement("p");
    p.className = message.role === "customer" ? "customer-message" : "assistant-message";
    p.textContent = message.text;
    transcript.append(p);
  }
  orderFacts.replaceChildren();
  const order = summary.order;
  if (order) {
    fact("Order", order.order_id || "—");
    fact("Status", order.status || "—");
    fact("Authoritative status", order.authoritative_status || "—");
    fact("Delayed", order.delayed ? "yes" : "no");
    if (order.channel) {
      fact("Channel", order.channel);
    }
    if (order.payment_state) {
      fact("Payment", order.payment_state);
    }
    if (typeof order.total === "number") {
      const currency = order.currency || "";
      fact("Total", `${currency ? currency + " " : ""}${order.total.toFixed(2)}`.trim());
    }
  } else {
    fact("Order", "none yet");
  }
  const selectionLabel = summary.selection?.catalog_title || summary.selection?.product_id;
  if (selectionLabel) {
    fact("Selection", selectionLabel);
  }
  // #383: card may arrive flattened on selection or only on order product options (API shapes it).
  const cardMessage = summary.selection?.card_message
    || summary.selection?.options?.card_message
    || null;
  if (cardMessage) {
    fact("Card message", cardMessage);
  }
  if (summary.delivery?.destination_reference) {
    fact("Destination handle", destinationHandleLabel(summary.delivery.destination_reference));
  }
  const timing = summary.delivery?.timing;
  if (timing && (timing.date || timing.window)) {
    fact("When", formatWhen(timing));
  }
  const intent = summary.shared_understanding?.structured_intent || {};
  for (const [key, value] of Object.entries(intent)) {
    fact(facetLabel(key), String(value));
  }
  availability.replaceChildren();
  const stock = summary.availability || [];
  if (!stock.length) {
    const empty = document.createElement("li");
    empty.textContent = "No availability on this session yet.";
    availability.append(empty);
  }
  for (const item of stock) {
    const li = document.createElement("li");
    const status = item.availability_status || "unknown";
    const badge = document.createElement("span");
    badge.className = status === "available" ? "badge" : "badge unavailable";
    badge.textContent = status === "available" ? "Available" : "Unknown";
    li.append(`${item.product_id} `, badge);
    availability.append(li);
  }
  if (supportAnswers) {
    supportAnswers.replaceChildren();
    const answers = summary.support_answers || [];
    if (!answers.length) {
      const empty = document.createElement("li");
      empty.textContent = "No ASO answers recorded for this session yet.";
      supportAnswers.append(empty);
    }
    for (const item of answers) {
      const li = document.createElement("li");
      const kind = item.kind === "situation" ? (item.situation_kind || "situation") : "FAQ";
      li.textContent = `${kind}: ${item.answer}`;
      supportAnswers.append(li);
    }
  }
}

async function openSession(sessionId) {
  state.selectedId = sessionId;
  renderInbox(state.items);
  renderOrders(state.orders);
  if (!state.live) {
    const sample = SAMPLE_SESSIONS[sessionId];
    if (sample) {
      renderSession(sample, `Sample session ${shortRef(sessionId)}`);
    }
    return;
  }
  try {
    const summary = await api(`/api/v1/operator/sessions/${sessionId}`);
    renderSession(summary, `Session ${shortRef(sessionId)}`);
  } catch (error) {
    sessionRef.textContent = `Could not load session (${error.message}).`;
  }
}

inboxRows.addEventListener("click", (event) => {
  const button = event.target.closest("[data-session]");
  if (button) {
    const sessionId = button.getAttribute("data-session");
    openSession(sessionId);
    if (window.innerWidth <= 768) {
      const sessionSection = document.querySelector("#session");
      if (sessionSection) {
        sessionSection.scrollIntoView({ behavior: "smooth" });
      }
    }
  }
});

function openOrderDetail(orderId) {
  const item = (state.orders || []).find((o) => o.order_id === orderId);
  if (!item) return;
  const dialog = document.querySelector("#order-detail-dialog");
  const facts = document.querySelector("#order-dialog-facts");
  const title = document.querySelector("#order-dialog-title");
  if (!dialog || !facts) return;

  title.textContent = `Order ${item.order_id}`;
  facts.replaceChildren();

  function addFact(term, value, isBadge = false) {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    if (isBadge) {
      const span = document.createElement("span");
      span.className = "badge";
      span.textContent = value;
      dd.appendChild(span);
    } else {
      dd.textContent = value;
    }
    facts.append(dt, dd);
  }

  const statusText = item.authoritative_status || item.status || "—";
  addFact("Order ID", item.order_id);
  addFact("Status", statusText, true);
  if (item.delayed) {
    addFact("Delayed", "yes", true);
  }
  addFact("Arrangement", item.catalog_title || item.product_id || "—");
  addFact("When", formatWhen(item.timing));
  if (item.card_message) {
    const dt = document.createElement("dt");
    dt.textContent = "Card message";
    const dd = document.createElement("dd");
    const cardBox = document.createElement("div");
    cardBox.className = "dialog-card-note";
    cardBox.textContent = `“${item.card_message}”`;
    dd.appendChild(cardBox);
    facts.append(dt, dd);
  } else {
    addFact("Card message", "—");
  }
  addFact("Channel", item.channel || "—");
  addFact("Payment", item.payment_state || "—", true);
  addFact("Destination handle", destinationHandleLabel(item.destination_reference));
  addFact("Updated", formatRequested(item.updated_at));

  const jumpBtn = document.querySelector("#order-dialog-jump-session");
  if (jumpBtn) {
    jumpBtn.onclick = () => {
      if (typeof dialog.close === "function") {
        dialog.close();
      } else {
        dialog.removeAttribute("open");
      }
      if (item.session_id) {
        openSession(item.session_id);
        const sessionSection = document.querySelector("#session");
        if (sessionSection) {
          sessionSection.scrollIntoView({ behavior: "smooth" });
        }
      }
    };
  }

  if (item.session_id) {
    openSession(item.session_id);
  }

  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
}

if (orderRows) {
  orderRows.addEventListener("click", (event) => {
    const detailTrigger = event.target.closest(".order-detail-trigger");
    if (detailTrigger) {
      openOrderDetail(detailTrigger.getAttribute("data-order-id"));
      return;
    }
    const target = event.target.closest("[data-session]");
    if (target) {
      const orderId = target.getAttribute("data-order-id") || target.closest("tr")?.querySelector("[data-order-id]")?.getAttribute("data-order-id");
      if (window.innerWidth <= 768 && orderId) {
        openOrderDetail(orderId);
      } else {
        openSession(target.getAttribute("data-session"));
      }
    }
  });
}

document.querySelectorAll("[data-close-order-dialog]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const dialog = document.querySelector("#order-detail-dialog");
    if (dialog && typeof dialog.close === "function") {
      dialog.close();
    } else if (dialog) {
      dialog.removeAttribute("open");
    }
  });
});

const orderDetailDialog = document.querySelector("#order-detail-dialog");
if (orderDetailDialog) {
  orderDetailDialog.addEventListener("click", (e) => {
    if (e.target === orderDetailDialog && typeof orderDetailDialog.close === "function") {
      orderDetailDialog.close();
    }
  });
}

function showSampleLayout(modeCopy) {
  state.live = false;
  state.ordersError = false;
  state.orderFilter = "all";
  state.selectedId = SAMPLE_INBOX[0].session_id;
  renderOrders(SAMPLE_ORDERS);
  renderInbox(SAMPLE_INBOX);
  renderForecasts(SAMPLE_FORECASTS);
  renderSession(SAMPLE_SESSIONS[SAMPLE_INBOX[0].session_id], "Sample session (labeled)");
  mode.textContent = modeCopy;
}

function showEmptySession() {
  sessionRef.textContent = "Select an order or inbox row.";
  transcript.replaceChildren();
  const empty = document.createElement("p");
  empty.className = "operator-empty";
  empty.textContent = "No session selected.";
  transcript.append(empty);
  orderFacts.replaceChildren();
  fact("Order", "none yet");
  availability.replaceChildren();
  const stockEmpty = document.createElement("li");
  stockEmpty.textContent = "No availability on this session yet.";
  availability.append(stockEmpty);
  if (supportAnswers) {
    supportAnswers.replaceChildren();
    const answerEmpty = document.createElement("li");
    answerEmpty.textContent = "No ASO answers recorded for this session yet.";
    supportAnswers.append(answerEmpty);
  }
}

function renderLiveChatConsole(sessionId) {
  const container = document.querySelector("#operator-actions") || document.querySelector("#operator-panel");
  if (!container) return;
  
  let chatBox = document.querySelector("#operator-live-chat-box");
  if (!chatBox) {
    chatBox = document.createElement("div");
    chatBox.id = "operator-live-chat-box";
    chatBox.style.cssText = "margin-top:15px; padding:12px; background:#f4f6f9; border:1px solid #dcdfe6; border-radius:6px;";
    chatBox.innerHTML = `
      <h4 style="margin:0 0 8px 0; color:#2c3e50;">Operator Live Chat Console</h4>
      <div id="operator-chat-log" style="height:120px; overflow-y:auto; background:#fff; border:1px solid #dcdfe6; padding:6px; font-size:13px; margin-bottom:8px;">
        <p style="margin:2px 0; color:#888;"><i>No active chat messages yet.</i></p>
      </div>
      <div style="display:flex; gap:6px;">
        <input type="text" id="operator-chat-msg" placeholder="Type operator response..." style="flex:1; padding:6px; font-size:13px;" />
        <button type="button" id="operator-chat-send" style="padding:6px 14px; font-size:13px; background:#27ae60; color:#fff; border:none; border-radius:4px; cursor:pointer;">Send Reply</button>
      </div>
    `;
    container.appendChild(chatBox);
    
    const sendBtn = chatBox.querySelector("#operator-chat-send");
    const msgInput = chatBox.querySelector("#operator-chat-msg");
    const logBox = chatBox.querySelector("#operator-chat-log");
    
    sendBtn.addEventListener("click", () => {
      const text = msgInput.value.trim();
      if (text) {
        const p = document.createElement("p");
        p.style.margin = "3px 0";
        p.innerHTML = `<strong style="color:#27ae60;">Florist:</strong> ${text}`;
        logBox.appendChild(p);
        msgInput.value = "";
        logBox.scrollTop = logBox.scrollHeight;
      }
    });
  }
}

async function boot() {
  showSampleLayout("Showing labeled sample data until operator APIs are confirmed.");
  try {
    await ensureSession();
    const inbox = await api("/api/v1/operator/escalations");
    state.live = true;
    let forecasts = [];
    try {
      const payload = await api("/api/v1/operator/forecasts");
      forecasts = payload.items || [];
    } catch (_error) {
      forecasts = [];
    }
    renderForecasts(forecasts);
    let orders = [];
    state.ordersError = false;
    try {
      const payload = await api("/api/v1/operator/orders");
      orders = Array.isArray(payload.items) ? payload.items : [];
    } catch (_error) {
      orders = [];
      state.ordersError = true;
    }
    renderOrders(orders);
    const items = inbox.items || [];
    if (items.length) {
      state.selectedId = items[0].session_id;
      renderInbox(items);
      await openSession(items[0].session_id);
      mode.textContent = "Live operator reads (least-data).";
    } else if (orders.length) {
      state.selectedId = orders[0].session_id;
      renderInbox([]);
      await openSession(orders[0].session_id);
      mode.textContent = "Live operator reads (least-data). Staff orders only.";
    } else {
      state.selectedId = "";
      renderInbox([]);
      showEmptySession();
      mode.textContent = "Live operator reads enabled. No Contact Florist requests yet.";
    }
  } catch (error) {
    if (error.status === 404) {
      showSampleLayout("Operator APIs disabled (fail closed). Labeled sample layout is shown.");
    } else {
      showSampleLayout(`Operator APIs unavailable (${error.message}). Labeled sample layout is shown.`);
    }
  }
}

boot();
