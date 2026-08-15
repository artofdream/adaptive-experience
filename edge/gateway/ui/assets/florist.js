const TOKEN = "local-browser-token";
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
    order: { order_id: "ord-sample-1", status: "preparing", delayed: false, authoritative_status: "preparing" },
    selection: { product_id: "classic-rose-dozen" },
    delivery: { destination_reference: "dest-ref-1", timing: { date: "2026-08-16", window: "morning" } },
    availability: [
      { product_id: "classic-rose-dozen", available: true, availability_status: "available" },
      { product_id: "premium-orchid", available: false, availability_status: "unknown" },
    ],
  },
  "22222222-2222-4222-8222-222222222222": {
    session_id: "22222222-2222-4222-8222-222222222222",
    context_version: 9,
    conversation: { messages: [
      { message_id: "d1", role: "customer", text: "The window changed and nobody told me.", status: "submitted", submitted_at: "2026-08-15T07:30:00+00:00" },
    ] },
    shared_understanding: { structured_intent: { occasion: "anniversary", timing: "this weekend" } },
    order: { order_id: "ord-sample-2", status: "dispatched", delayed: true, authoritative_status: "delayed" },
    selection: { product_id: "lilac-bouquet" },
    delivery: { destination_reference: "dest-ref-2", timing: { date: "2026-08-15", window: "afternoon" } },
    availability: [
      { product_id: "lilac-bouquet", available: true, availability_status: "available" },
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

const mode = document.querySelector("#operator-mode");
const inboxRows = document.querySelector("#inbox-rows");
const forecastRows = document.querySelector("#forecast-rows");
const transcript = document.querySelector("#transcript");
const orderFacts = document.querySelector("#order-facts");
const availability = document.querySelector("#availability");
const sessionRef = document.querySelector("#session-ref");

const state = { csrf: "", live: false, items: SAMPLE_INBOX };

function headers(extra) {
  return {
    Authorization: `Bearer ${TOKEN}`,
    Origin: window.location.origin,
    ...extra,
  };
}

async function api(path, options = {}) {
  const init = {
    method: options.method || "GET",
    headers: headers(options.headers || {}),
    credentials: "same-origin",
  };
  if (options.body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.headers["X-CSRF-Token"] = state.csrf;
    init.body = JSON.stringify(options.body);
  }
  const response = await fetch(path, init);
  const payload = response.headers.get("content-type")?.includes("application/json")
    ? await response.json() : await response.text();
  if (!response.ok) {
    const code = payload && payload.error || payload && payload.code || `http_${response.status}`;
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

function renderForecasts(items) {
  forecastRows.replaceChildren();
  for (const item of items) {
    const row = document.createElement("tr");
    row.innerHTML = `<td><code>${item.product_id}</code></td>
      <td>${item.trend}</td>
      <td>${item.recommendation}</td>`;
    forecastRows.append(row);
  }
}

function renderInbox(items) {
  inboxRows.replaceChildren();
  for (const item of items) {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${item.requested_at || "—"}</td>
      <td><button type="button" class="text-link" data-session="${item.session_id}">${item.escalation_reason}</button></td>
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
  for (const message of summary.conversation?.messages || []) {
    const p = document.createElement("p");
    p.className = message.role === "customer" ? "user-message" : "assistant-message";
    p.textContent = `${message.role}: ${message.text}`;
    transcript.append(p);
  }
  orderFacts.replaceChildren();
  const order = summary.order;
  if (order) {
    fact("Order", order.order_id || "—");
    fact("Status", order.status || "—");
    fact("Authoritative", order.authoritative_status || "—");
    fact("Delayed", order.delayed ? "yes" : "no");
  } else {
    fact("Order", "none yet");
  }
  if (summary.selection?.product_id) {
    fact("Selection", summary.selection.product_id);
  }
  if (summary.delivery?.destination_reference) {
    fact("Destination", summary.delivery.destination_reference);
  }
  const intent = summary.shared_understanding?.structured_intent || {};
  for (const [key, value] of Object.entries(intent)) {
    fact(key, String(value));
  }
  availability.replaceChildren();
  for (const item of summary.availability || []) {
    const li = document.createElement("li");
    li.textContent = `${item.product_id}: ${item.availability_status || "unknown"}`;
    availability.append(li);
  }
}

async function openSession(sessionId) {
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

async function boot() {
  renderInbox(SAMPLE_INBOX);
  renderForecasts(SAMPLE_FORECASTS);
  renderSession(SAMPLE_SESSIONS[SAMPLE_INBOX[0].session_id], "Sample session (labeled)");
  mode.textContent = "Showing labeled sample data until operator APIs are confirmed.";
  try {
    const session = await api("/api/v1/session", { method: "POST" });
    state.csrf = session.csrf_token;
    const inbox = await api("/api/v1/operator/escalations");
    state.live = true;
    state.items = inbox.items || [];
    try {
      const forecasts = await api("/api/v1/operator/forecasts");
      if ((forecasts.items || []).length) {
        renderForecasts(forecasts.items);
      }
    } catch (_error) {
      renderForecasts(SAMPLE_FORECASTS);
    }
    if (state.items.length) {
      renderInbox(state.items);
      await openSession(state.items[0].session_id);
      mode.textContent = "Live local operator reads are enabled (least-data).";
    } else {
      mode.textContent = "Operator APIs enabled; no Contact Florist requests yet. Sample rows remain for layout.";
    }
  } catch (error) {
    state.live = false;
    if (error.status === 404) {
      mode.textContent = "Operator APIs disabled (fail closed). Labeled sample layout is shown.";
    } else {
      mode.textContent = `Operator APIs unavailable (${error.message}). Labeled sample layout is shown.`;
    }
  }
}

boot();
