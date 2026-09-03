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

function filterOrders(items, filter = state.orderFilter) {
  const list = Array.isArray(items) ? items : [];
  if (filter === "delayed") return list.filter(isDelayedOrder);
  if (filter === "today") return list.filter((item) => isTodayOrder(item));
  return list;
}

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
    row.innerHTML = `<td>${group.title}</td>
      <td>${group.count}</td>
      <td>${uniqueSorted(group.windows).join(" · ") || "—"}</td>
      <td>${cards}</td>
      <td><code>${uniqueSorted(group.channels).join(" · ") || "—"}</code></td>`;
    prepareRows.append(row);
  }
}

function syncOrderFilterButtons() {
  for (const [id, value] of [
    ["#order-filter-today", "today"],
    ["#order-filter-delayed", "delayed"],
    ["#order-filter-all", "all"],
  ]) {
    const button = document.querySelector(id);
    if (button) button.setAttribute("aria-pressed", String(state.orderFilter === value));
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
    return;
  }
  if (!visible.length) {
    const copy = state.orderFilter === "delayed"
      ? "No delayed orders."
      : "No orders for today.";
    orderRows.append(emptyRow(9, copy));
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
    row.innerHTML = `<td>${formatRequested(item.updated_at)}</td>
      <td><button type="button" class="text-link" data-session="${item.session_id}">${shortRef(item.order_id)}</button>${sample}${inboxLink}</td>
      <td><span class="badge">${statusText}</span></td>
      <td>${arrangement}</td>
      <td>${card}</td>
      <td><code>${channel}</code></td>
      <td><span class="badge">${paid}</span></td>
      <td>${formatWhen(item.timing)}</td>
      <td><code>${shortRef(item.destination_reference)}</code></td>`;
    orderRows.append(row);
  }
}

document.querySelectorAll("#order-filter-today, #order-filter-delayed, #order-filter-all").forEach((button) => {
  button.addEventListener("click", () => {
    if (button.id === "order-filter-delayed") state.orderFilter = "delayed";
    else if (button.id === "order-filter-all") state.orderFilter = "all";
    else state.orderFilter = "today";
    renderOrders(state.orders);
  });
});

function renderInbox(items) {
  inboxRows.replaceChildren();
  state.items = items;
  if (!items.length) {
    inboxRows.append(emptyRow(3, "No Contact Florist requests yet. This inbox stays empty until a customer uses T-09."));
    return;
  }
  for (const item of items) {
    const row = document.createElement("tr");
    if (item.session_id === state.selectedId) row.className = "is-selected";
    const sample = item.sample ? ' <span class="status">Sample</span>' : "";
    const orderLink = sessionIdSet(state.orders).has(item.session_id)
      ? ' <span class="badge">Has order</span>' : "";
    row.innerHTML = `<td>${formatRequested(item.requested_at)}</td>
      <td><button type="button" class="text-link" data-session="${item.session_id}">${reasonLabel(item.escalation_reason)}</button>${sample}${orderLink}</td>
      <td><code>${shortRef(item.context_reference || item.session_id)}</code></td>`;
    inboxRows.append(row);
  }
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
    fact("Saved destination", shortRef(summary.delivery.destination_reference));
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
    openSession(button.getAttribute("data-session"));
  }
});

if (orderRows) {
  orderRows.addEventListener("click", (event) => {
    const target = event.target.closest("[data-session]");
    if (target) {
      openSession(target.getAttribute("data-session"));
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
