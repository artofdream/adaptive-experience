const TOKEN = "local-browser-token";
const INTENT_LABELS = {
  occasion: "Occasion",
  recipient: "Recipient",
  budget: "Budget",
  style: "Style",
  flower_preference: "Flower preference",
  timing: "Timing",
};
const TRACK_ORDER = ["created", "submitted", "confirmed", "preparing", "dispatched", "delivered", "completed"];
/** Session-scoped reference vault token for ADR-013 confirmation-driven checkout. */
const SESSION_PAYMENT_REFERENCE = "session_pay_ref";
const STEP_CAPTIONS = {
  1: "Step 1 · Enter / Discovery",
  2: "Step 2 · Describe need / Shared Understanding",
  3: "Step 3 · Review recommendations",
  4: "Step 4 · Customize",
  5: "Step 5 · Confirm delivery",
  6: "Step 6 · Review, pay, and order",
  7: "Step 7 · Track delivery",
};
// Mirrored from platform REFERENCE_CATALOG flower tags for thin FR-003 selects.
const PRODUCT_FLOWERS = {
  "pink-flower-vase": ["roses", "mixed"],
  "lilac-bouquet": ["lilac", "mixed"],
  "classic-rose-dozen": ["roses"],
  "budget-mixed-bunch": ["mixed", "carnations"],
  "premium-orchid": ["orchid"],
};
const COLOURS = ["red", "pink", "white", "yellow", "purple", "mixed"];
const RIBBONS = ["none", "satin", "organza", "kraft"];

const help = document.querySelector("#help");
const helpButton = document.querySelector(".help-button");
const asoButton = document.querySelector(".aso");
const form = document.querySelector("#message-form");
const message = document.querySelector("#message");
const messages = document.querySelector("#messages");
const notice = document.querySelector("#notice");
const disclosure = document.querySelector("#disclosure");

const state = { csrf: "", contextVersion: 0, workspace: null, lastEventId: "", step: 1, unlockedThrough: 2 };

const EMPTY_COPY = {
  3: {
    title: "Recommendations need a little more context",
    body: "Share the occasion (and budget if you know it) in the conversation, then return here.",
    cta: "Back to conversation",
    goto: 1,
  },
  4: {
    title: "Nothing to customize yet",
    body: "Choose a recommended arrangement first, then set size and a card message.",
    cta: "View recommendations",
    goto: 3,
  },
  5: {
    title: "Delivery needs a selected product",
    body: "Pick and customize flowers before choosing a delivery window.",
    cta: "Back to customize",
    goto: 4,
  },
  6: {
    title: "Checkout needs delivery details",
    body: "Confirm date, window, and destination reference before paying.",
    cta: "Back to delivery",
    goto: 5,
  },
  7: {
    title: "No order to track yet",
    body: "Create and confirm an order at checkout to open tracking.",
    cta: "Back to checkout",
    goto: 6,
  },
};

function showNotice(text) {
  notice.textContent = text;
  notice.hidden = false;
  window.setTimeout(() => { notice.hidden = true; }, 5000);
}

function facets() {
  return (state.workspace && state.workspace.facets) || {};
}

function intentKeys(f) {
  const intent = (f.shared_understanding && f.shared_understanding.structured_intent)
    || f.shared_understanding || {};
  return Object.keys(intent).filter((key) => intent[key] != null && String(intent[key]).trim() !== "");
}

function recommendationItems(f) {
  const block = f.recommendations || {};
  return block.items || block || [];
}

function unlockedThrough(f) {
  let max = 2;
  if (intentKeys(f).length) max = Math.max(max, 3);
  const items = recommendationItems(f);
  if (Array.isArray(items) && items.length) max = Math.max(max, 4);
  if (f.selection && f.selection.product_id) max = Math.max(max, 5);
  if (f.delivery && f.delivery.timing) max = Math.max(max, 6);
  if (f.order && f.order.order_id) max = Math.max(max, 7);
  return max;
}

function stepReady(step, f) {
  if (step <= 2) return true;
  if (step === 3) return intentKeys(f).length > 0 || (Array.isArray(recommendationItems(f)) && recommendationItems(f).length > 0);
  if (step === 4) return Boolean(f.selection && f.selection.product_id);
  if (step === 5) return Boolean(f.selection && f.selection.product_id);
  if (step === 6) return Boolean(f.delivery && f.delivery.timing);
  if (step === 7) return Boolean(f.order && f.order.order_id);
  return false;
}

function updateJourneyChrome() {
  const f = facets();
  state.unlockedThrough = unlockedThrough(f);
  document.querySelectorAll("#journey-steps [data-step]").forEach((button) => {
    const step = Number(button.dataset.step);
    const unlocked = step <= state.unlockedThrough;
    button.disabled = !unlocked;
    button.setAttribute("aria-disabled", unlocked ? "false" : "true");
    button.classList.toggle("is-locked", !unlocked);
    button.title = unlocked ? "" : "Complete earlier steps to unlock";
    if (step === state.step) button.setAttribute("aria-current", "step");
    else button.removeAttribute("aria-current");
  });
  document.querySelectorAll("[data-requires-unlock]").forEach((button) => {
    const need = Number(button.dataset.requiresUnlock);
    const ok = need <= state.unlockedThrough;
    button.disabled = !ok;
    button.setAttribute("aria-disabled", ok ? "false" : "true");
  });
  const current = document.querySelector(`#journey-steps [data-step="${state.step}"]`);
  if (current) current.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" });
}

function renderStepEmpty(step) {
  const empty = document.querySelector("#step-empty");
  const guidance = document.querySelector("#step-guidance");
  const ready = stepReady(step, facets());
  const showEmpty = step >= 3 && !ready;
  empty.hidden = !showEmpty;
  if (guidance && state.step <= 2) {
    /* guidance visibility still driven by data-journey-steps */
  }
  if (showEmpty) {
    const copy = EMPTY_COPY[step];
    document.querySelector("#step-empty-title").textContent = copy.title;
    document.querySelector("#step-empty-body").textContent = copy.body;
    const cta = document.querySelector("#step-empty-cta");
    cta.textContent = copy.cta;
    cta.dataset.gotoStep = String(copy.goto);
    document.querySelectorAll(".tile-grid .tile").forEach((tile) => {
      tile.hidden = true;
    });
  }
}

function setJourneyStep(step, { focus = true, force = false } = {}) {
  let next = Math.min(7, Math.max(1, Number(step) || 1));
  updateJourneyChrome();
  if (!force && next > state.unlockedThrough) {
    showNotice(`Step ${next} unlocks after you finish earlier stages.`);
    next = Math.min(state.step, state.unlockedThrough) || 1;
  }
  state.step = next;
  document.querySelector("#step-caption").textContent = STEP_CAPTIONS[next];
  document.querySelectorAll("[data-journey-steps]").forEach((node) => {
    if (node.id === "step-empty") return;
    const steps = String(node.dataset.journeySteps).split(",").map((value) => Number(value.trim()));
    node.hidden = !steps.includes(next);
  });
  document.querySelectorAll("[data-show-on-step]").forEach((node) => {
    node.hidden = Number(node.dataset.showOnStep) !== next;
  });
  renderStepEmpty(next);
  if (!document.querySelector("#step-empty").hidden) {
    document.querySelectorAll("[data-journey-steps]").forEach((node) => {
      if (node.id === "step-guidance" || node.id === "step-empty") return;
      if (node.classList.contains("tile") || node.classList.contains("step-guidance")) {
        const steps = String(node.dataset.journeySteps || "").split(",").map((value) => Number(value.trim()));
        if (steps.includes(next)) node.hidden = true;
      }
    });
  }
  updateJourneyChrome();
  if (window.location.hash !== `#step-${next}`) {
    history.replaceState(null, "", `#step-${next}`);
  }
  if (focus) {
    const target = document.querySelector(
      "#step-empty:not([hidden]), .tile-grid .tile:not([hidden]), #step-guidance:not([hidden])",
    );
    if (target) target.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
}

function suggestedStep(f) {
  if (!f) return 1;
  if (f.order && f.order.order_id) return 7;
  if (f.delivery && f.delivery.timing) return 6;
  if (f.selection && f.selection.product_id) return 4;
  const items = recommendationItems(f);
  if (Array.isArray(items) && items.length) return 3;
  if (intentKeys(f).length) return 2;
  return 1;
}

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
    throw new Error(code);
  }
  return payload;
}

function productLabel(productId) {
  return String(productId || "").replace(/-/g, " ");
}

function productArt(productId) {
  const key = String(productId || "");
  return key.length % 2 ? "/assets/bouquet-pink.svg" : "/assets/bouquet-mixed.svg";
}

const STATUS_COPY = {
  created: "Order received",
  submitted: "Order submitted",
  confirmed: "Order confirmed",
  preparing: "Preparing flowers...",
  dispatched: "Out for delivery",
  delivered: "Delivered",
  completed: "Completed",
};

function renderMessages(items) {
  messages.replaceChildren();
  if (!items || !items.length) {
    const intro = document.createElement("p");
    intro.className = "assistant-message";
    intro.textContent = "Hello! What occasion are you shopping for today?";
    messages.append(intro);
    return;
  }
  for (const item of items) {
    const bubble = document.createElement("p");
    bubble.className = item.role === "customer" ? "customer-message" : "assistant-message";
    bubble.textContent = item.text || "";
    messages.append(bubble);
  }
}

function renderUnderstanding(intent) {
  const empty = document.querySelector("#understanding-empty");
  const list = document.querySelector("#understanding-list");
  const entries = Object.entries(intent || {});
  if (!entries.length) {
    empty.hidden = false;
    list.hidden = true;
    list.replaceChildren();
    return;
  }
  empty.hidden = true;
  list.hidden = false;
  list.replaceChildren();
  for (const [key, value] of entries) {
    const dt = document.createElement("dt");
    dt.textContent = INTENT_LABELS[key] || key;
    const dd = document.createElement("dd");
    dd.textContent = value;
    list.append(dt, dd);
  }
}

function renderRecommendations(items) {
  const cards = document.querySelector("#recommendation-cards");
  const empty = document.querySelector("#recommendations-empty");
  cards.replaceChildren();
  const list = items || [];
  if (empty) empty.hidden = list.length > 0;
  for (const item of list) {
    const card = document.createElement("article");
    card.className = "card";
    const thumb = document.createElement("img");
    thumb.className = "thumb";
    thumb.alt = "";
    thumb.src = productArt(item.product_id);
    const title = document.createElement("h3");
    title.textContent = productLabel(item.product_id);
    const price = document.createElement("p");
    price.className = "price";
    price.textContent = item.price != null ? `$${Number(item.price).toFixed(2)}` : "";
    const badge = document.createElement("span");
    badge.className = item.available ? "badge" : "badge unavailable";
    badge.textContent = item.available ? "Available" : (item.availability_status || "Unknown");
    const select = document.createElement("button");
    select.className = "primary";
    select.type = "button";
    select.textContent = "Select";
    select.disabled = item.available === false;
    select.addEventListener("click", () => selectProduct(item.product_id));
    card.append(thumb, title, price, badge, select);
    cards.append(card);
  }
}

function fillSelect(select, values, selected) {
  select.replaceChildren();
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = select.id === "flower-type" ? "Any eligible" : "Any";
  select.append(blank);
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value.charAt(0).toUpperCase() + value.slice(1);
    select.append(option);
  }
  select.value = selected && values.includes(selected) ? selected : "";
}

function renderSelection(selection) {
  const empty = document.querySelector("#selection-empty");
  const formEl = document.querySelector("#selection-form");
  if (!selection || !selection.product_id) {
    empty.hidden = false;
    formEl.hidden = true;
    return;
  }
  empty.hidden = true;
  formEl.hidden = false;
  const options = selection.options || {};
  document.querySelector("#arrangement").value = productLabel(selection.product_id);
  document.querySelector("#size").value = options.size || "";
  fillSelect(
    document.querySelector("#flower-type"),
    PRODUCT_FLOWERS[selection.product_id] || [],
    options.flower_type || "",
  );
  fillSelect(document.querySelector("#colour"), COLOURS, options.colour || "");
  fillSelect(document.querySelector("#ribbon"), RIBBONS, options.ribbon || "");
  document.querySelector("#card-message").value = options.card_message || "";
}

function renderSummary(summary) {
  const lines = document.querySelector("#summary-lines");
  const total = document.querySelector("#summary-total");
  lines.replaceChildren();
  for (const charge of (summary && summary.itemized_charges) || []) {
    const row = document.createElement("p");
    row.className = "charge";
    const label = document.createElement("span");
    label.textContent = charge.label || charge.product_id || "Item";
    const amount = document.createElement("span");
    amount.textContent = charge.amount != null ? `$${Number(charge.amount).toFixed(2)}` : "";
    row.append(label, amount);
    lines.append(row);
  }
  total.textContent = summary && summary.total != null ? `Total $${Number(summary.total).toFixed(2)}` : "";
}

function syncPaymentMode() {
  const other = document.querySelector("input[name='payment-mode']:checked")?.value === "other";
  const input = document.querySelector("#payment-reference");
  const label = document.querySelector("#payment-reference-label");
  input.hidden = !other;
  label.hidden = !other;
  input.required = other;
  if (!other) {
    input.value = "";
    document.querySelector("#confirm-payment").textContent =
      `Session vault reference (${SESSION_PAYMENT_REFERENCE})`;
  } else {
    document.querySelector("#confirm-payment").textContent = input.value.trim() || "Enter a different vault reference";
  }
}

function resolvePaymentReference() {
  const mode = document.querySelector("input[name='payment-mode']:checked")?.value || "session";
  if (mode === "session") return SESSION_PAYMENT_REFERENCE;
  return document.querySelector("#payment-reference").value.trim();
}

function renderCheckoutConfirmation(workspace) {
  const facets = (workspace && workspace.facets) || {};
  const delivery = facets.delivery || {};
  const summary = facets.order_summary || {};
  const destination = document.querySelector("#confirm-destination");
  const total = document.querySelector("#confirm-total");
  const paymentRef = document.querySelector("#session-payment-ref");
  destination.textContent = delivery.destination_reference || "Not set yet — complete delivery first";
  total.textContent = summary.total != null
    ? `$${Number(summary.total).toFixed(2)} ${summary.currency || "USD"}`
    : "Not available — select a product and delivery";
  if (paymentRef) paymentRef.textContent = SESSION_PAYMENT_REFERENCE;
  syncPaymentMode();
}

function renderOrder(order) {
  const status = document.querySelector("#order-status");
  const confirmed = document.querySelector("#order-confirmed");
  const latest = document.querySelector("#latest-status-text");
  const updated = document.querySelector("#latest-status-updated");
  const steps = document.querySelectorAll("#tracking-steps li");
  if (!order) {
    status.textContent = "No order yet.";
    confirmed.hidden = true;
    latest.textContent = "Awaiting order";
    updated.textContent = "";
    steps.forEach((step) => step.classList.remove("done"));
    return;
  }
  const current = order.authoritative_status || order.status;
  const reached = TRACK_ORDER.indexOf(order.status);
  status.textContent = order.delayed ? "Delayed" : current.replace(/_/g, " ");
  confirmed.hidden = !(reached >= TRACK_ORDER.indexOf("confirmed"));
  latest.textContent = STATUS_COPY[current] || current.replace(/_/g, " ");
  updated.textContent = "Last updated from the order status stream";
  steps.forEach((step) => {
    const point = TRACK_ORDER.indexOf(step.dataset.status);
    step.classList.toggle("done", point !== -1 && point <= Math.max(reached, 0));
  });
}

function renderWorkspace(workspace) {
  state.workspace = workspace;
  state.contextVersion = workspace.context_version || 0;
  if (workspace.disclosure) disclosure.textContent = workspace.disclosure;
  const f = workspace.facets || {};
  renderMessages((f.conversation || {}).messages);
  renderUnderstanding((f.shared_understanding || {}).structured_intent || f.shared_understanding);
  renderRecommendations((f.recommendations || {}).items || f.recommendations);
  renderSelection(f.selection);
  renderSummary(f.order_summary);
  renderOrder(f.order);
  renderCheckoutConfirmation(workspace);
  const delivery = f.delivery;
  if (delivery && delivery.destination_reference) {
    document.querySelector("#destination-reference").value = delivery.destination_reference;
    if (delivery.timing && delivery.timing.date) {
      document.querySelector("#delivery-date").value = delivery.timing.date;
    }
    if (delivery.timing && delivery.timing.window) {
      const match = document.querySelector(`input[name="window"][value="${delivery.timing.window}"]`);
      if (match) match.checked = true;
    }
  }
  setJourneyStep(state.step, { focus: false, force: true });
}

async function refreshWorkspace() {
  renderWorkspace(await api("/api/v1/workspace"));
}

async function pullStream() {
  const query = state.lastEventId ? `?after=${encodeURIComponent(state.lastEventId)}` : "";
  const response = await fetch(`/api/v1/stream${query}`, {
    headers: headers(state.lastEventId ? { "Last-Event-ID": state.lastEventId } : {}),
    credentials: "same-origin",
  });
  if (!response.ok) return;
  const body = await response.text();
  for (const block of body.split("\n\n")) {
    const idLine = block.split("\n").find((line) => line.startsWith("id: "));
    const dataLine = block.split("\n").find((line) => line.startsWith("data: "));
    if (idLine) state.lastEventId = idLine.slice(4).trim();
    if (!dataLine) continue;
    const event = JSON.parse(dataLine.slice(6));
    if (event.kind === "snapshot" && event.workspace) renderWorkspace(event.workspace);
    else if (event.kind === "invalidation") await refreshWorkspace();
  }
}

async function selectProduct(productId) {
  const result = await api("/api/v1/selection", {
    method: "POST",
    body: { product_id: productId, observed_context_version: state.contextVersion },
  });
  state.contextVersion = result.context_version;
  await refreshWorkspace();
  await pullStream();
  setJourneyStep(4);
  showNotice("Product selected. You can set size, flower type, colour, ribbon, and a card message next.");
}

function openHelp() {
  help.showModal();
  helpButton.setAttribute("aria-expanded", "true");
  asoButton.setAttribute("aria-expanded", "true");
}

function closeHelp() {
  help.close();
  helpButton.setAttribute("aria-expanded", "false");
  asoButton.setAttribute("aria-expanded", "false");
  helpButton.focus();
}

helpButton.addEventListener("click", openHelp);
asoButton.addEventListener("click", openHelp);
document.querySelector("#chat-with-lily").addEventListener("click", openHelp);
document.querySelector("#contact-florist").addEventListener("click", openHelp);
document.querySelector("[data-close-help]").addEventListener("click", closeHelp);
help.addEventListener("close", () => {
  helpButton.setAttribute("aria-expanded", "false");
  asoButton.setAttribute("aria-expanded", "false");
});

document.querySelector("#correct-open").addEventListener("click", () => {
  document.querySelector("#correct-form").hidden = false;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = message.value.trim();
  if (!text) return;
  try {
    const result = await api("/api/v1/conversation/messages", {
      method: "POST",
      body: { message_text: text, observed_context_version: state.contextVersion },
    });
    state.contextVersion = result.context_version;
    message.value = "";
    await refreshWorkspace();
    await pullStream();
    if (state.step < 2) setJourneyStep(2);
    showNotice("Thanks — your message is ready for the assistant. You can change any detail later.");
  } catch (error) {
    showNotice(`Conversation could not be sent (${error.message}).`);
  }
  message.focus();
});

document.querySelector("#correct-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const key = document.querySelector("#correct-facet").value;
  const value = document.querySelector("#correct-value").value.trim();
  if (!value) return;
  try {
    const result = await api("/api/v1/shared-understanding", {
      method: "PATCH",
      body: { corrections: { [key]: value }, observed_context_version: state.contextVersion },
    });
    state.contextVersion = result.context_version;
    document.querySelector("#correct-form").hidden = true;
    await refreshWorkspace();
    await pullStream();
    showNotice("Shared Understanding updated.");
  } catch (error) {
    showNotice(`Correction failed (${error.message}).`);
  }
});

document.querySelector("#selection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const selection = (state.workspace && state.workspace.facets || {}).selection || {};
  if (!selection.product_id) return;
  const options = {};
  const size = document.querySelector("#size").value.trim();
  const flowerType = document.querySelector("#flower-type").value.trim();
  const colour = document.querySelector("#colour").value.trim();
  const ribbon = document.querySelector("#ribbon").value.trim();
  const card = document.querySelector("#card-message").value.trim();
  if (size) options.size = size;
  if (flowerType) options.flower_type = flowerType;
  if (colour) options.colour = colour;
  if (ribbon) options.ribbon = ribbon;
  if (card) options.card_message = card;
  try {
    const result = await api("/api/v1/selection", {
      method: "POST",
      body: { product_id: selection.product_id, options, observed_context_version: state.contextVersion },
    });
    state.contextVersion = result.context_version;
    await refreshWorkspace();
    await pullStream();
    showNotice("Selection updated.");
  } catch (error) {
    showNotice(`Update failed (${error.message}).`);
  }
});

document.querySelector("#delivery-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const windowValue = document.querySelector("input[name='window']:checked");
  try {
    const result = await api("/api/v1/delivery", {
      method: "POST",
      body: {
        delivery: {
          timing: { date: document.querySelector("#delivery-date").value, window: windowValue && windowValue.value },
          destination_reference: document.querySelector("#destination-reference").value.trim(),
        },
        observed_context_version: state.contextVersion,
      },
    });
    state.contextVersion = result.context_version;
    await refreshWorkspace();
    await pullStream();
    setJourneyStep(5);
    showNotice("Delivery details saved.");
  } catch (error) {
    showNotice(`Delivery could not be saved (${error.message}).`);
  }
});

document.querySelector("#create-order").addEventListener("click", async () => {
  try {
    const result = await api("/api/v1/order", { method: "POST", body: {} });
    await refreshWorkspace();
    await pullStream();
    showNotice(result.accepted ? `Order ${result.order_id} created.` : `Order not created (${result.code}).`);
  } catch (error) {
    showNotice(`Order could not be created (${error.message}).`);
  }
});

document.querySelector("#checkout-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const summary = (state.workspace && state.workspace.facets || {}).order_summary || {};
  const paymentReference = resolvePaymentReference();
  if (!paymentReference) {
    showNotice("Confirm the session payment reference or enter a different vault token.");
    return;
  }
  if (!document.querySelector("#checkout-ack").checked) {
    showNotice("Confirm delivery, total, and payment before placing the order.");
    return;
  }
  try {
    const result = await api("/api/v1/checkout", {
      method: "POST",
      body: {
        payment_reference: paymentReference,
        observed_total: Number(summary.total),
      },
    });
    await refreshWorkspace();
    await pullStream();
    const order = (state.workspace && state.workspace.facets || {}).order || {};
    const confirmed = order.status === "confirmed" || result.confirmed;
    if (confirmed) setJourneyStep(7);
    if (result.decline_code) {
      showNotice(`Payment declined (${result.decline_code}). Order stays submitted.`);
    } else if (confirmed) {
      showNotice("Order confirmed.");
    } else {
      showNotice("Checkout accepted. Waiting for payment confirmation…");
    }
  } catch (error) {
    showNotice(`Checkout failed (${error.message}).`);
  }
});

document.querySelectorAll("input[name='payment-mode']").forEach((input) => {
  input.addEventListener("change", syncPaymentMode);
});
document.querySelector("#payment-reference").addEventListener("input", syncPaymentMode);

document.querySelector("#support-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = document.querySelector("#support-question").value.trim();
  if (!question) return;
  const answer = document.querySelector("#support-answer");
  try {
    const result = await api("/api/v1/support", { method: "POST", body: { question } });
    answer.hidden = false;
    answer.textContent = result.answer || "No approved information matched.";
  } catch (error) {
    answer.hidden = false;
    answer.textContent = `Support is unavailable (${error.message}).`;
  }
});

document.querySelectorAll("#journey-steps [data-step]").forEach((button) => {
  button.addEventListener("click", () => {
    if (button.disabled) {
      showNotice("Complete earlier steps to unlock this stage.");
      return;
    }
    setJourneyStep(button.dataset.step);
  });
});
document.querySelectorAll("[data-goto-step]").forEach((button) => {
  button.addEventListener("click", () => setJourneyStep(button.dataset.gotoStep));
});
document.querySelector("#step-empty-cta").addEventListener("click", (event) => {
  setJourneyStep(event.currentTarget.dataset.gotoStep);
});
window.addEventListener("hashchange", () => {
  const match = window.location.hash.match(/^#step-([1-7])$/);
  if (match) setJourneyStep(match[1], { focus: false });
});

async function boot() {
  try {
    const session = await api("/api/v1/session", { method: "POST" });
    state.csrf = session.csrf_token;
    await refreshWorkspace();
    await pullStream();
    const hashStep = Number((window.location.hash.match(/^#step-([1-7])$/) || [])[1]);
    const suggest = suggestedStep(facets());
    setJourneyStep(hashStep || suggest, { focus: false });
  } catch (error) {
    setJourneyStep(1, { focus: false, force: true });
    showNotice(`Workspace could not start (${error.message}).`);
  }
}

boot();
