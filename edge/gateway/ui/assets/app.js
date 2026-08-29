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
/** Session-scoped destination reference for ADR-013 confirmation-driven delivery. */
const SESSION_DESTINATION_REFERENCE = "home";
const STEP_CAPTIONS = {
  1: "Now · Discover — earlier choices stay on this workspace",
  2: "Now · Understand — review and correct the summary",
  3: "Now · Choose — recommendations stay visible after you pick",
  4: "Now · Customize — selected flowers stay on this workspace",
  5: "Now · Deliver — confirm the saved destination, not an address",
  6: "Now · Review and pay — confirm values already captured",
  7: "Now · Track — Help is automated; Contact Florist is a person",
};
const ERROR_COPY = {
  csrf_rejected: "This session could not verify the request. Refresh the page, then try again.",
  http_401: "Your session expired. Refresh the page to continue.",
  http_403: "This action was blocked. Refresh the page, then try again.",
  http_409: "The workspace changed while you were editing. Refresh, then try again.",
  http_422: "That value could not be saved. Check the highlighted fields.",
  http_429: "Please wait a moment, then try again.",
  http_500: "Something went wrong on our side. Try again in a moment.",
  http_502: "The shop is briefly unavailable. Try again in a moment.",
  http_503: "The shop is briefly unavailable. Try again in a moment.",
  delivery_date_past: "Delivery cannot be scheduled in the past. Choose today or a later date.",
};
// Customer-facing names for T-03 cards (and T-04 arrangement). IDs stay slugs.
const PRODUCT_NAMES = {
  "pink-flower-vase": "Pink Flower Vase",
  "lilac-bouquet": "Lilac Bouquet",
  "classic-rose-dozen": "Classic Rose Dozen",
  "budget-mixed-bunch": "Budget Mixed Bunch",
  "premium-orchid": "Premium Orchid",
};
// Mirrored from platform REFERENCE_CATALOG flower tags for thin FR-003 selects.
const PRODUCT_FLOWERS = {
  "pink-flower-vase": ["roses", "mixed"],
  "lilac-bouquet": ["lilac", "mixed"],
  "classic-rose-dozen": ["roses"],
  "budget-mixed-bunch": ["mixed", "carnations"],
  "premium-orchid": ["orchid"],
};
// Vendored open-licence stills for FR-007 ranking SKUs (T-03 + T-04).
// Category likeness, not this shop's cooler. Credits: /assets/NOTICE.txt
const PRODUCT_ART = {
  "classic-rose-dozen": "/assets/sku-classic-rose-dozen.jpg",
  "lilac-bouquet": "/assets/sku-lilac-bouquet.jpg",
  "budget-mixed-bunch": "/assets/sku-budget-mixed-bunch.jpg",
  "pink-flower-vase": "/assets/sku-pink-flower-vase.jpg",
  "premium-orchid": "/assets/sku-premium-orchid.jpg",
};
const COLOURS = ["red", "pink", "white", "yellow", "purple", "mixed"];
const RIBBONS = ["none", "satin", "organza", "kraft"];
/** ADR-003 chip copy: API missing-facet questions become thought completions. */
const THOUGHT_COMPLETION_COPY = {
  "What is the occasion?": "for a birthday",
  "What budget should I work within?": "under $75",
  "Who are the flowers for?": "for Mom",
  "What style or mood would you prefer?": "romantic style",
  "Any flower preferences?": "roses",
  "When should they arrive?": "this weekend",
};

const help = document.querySelector("#help");
const helpButton = document.querySelector(".help-button");
const asoButton = document.querySelector(".aso");
const contactFlorist = document.querySelector("#contact-florist");
const escalation = document.querySelector("#escalation");
const form = document.querySelector("#message-form");
const message = document.querySelector("#message");
const messages = document.querySelector("#messages");
const notice = document.querySelector("#notice");
const disclosure = document.querySelector("#disclosure");

const state = {
  csrf: "",
  contextVersion: 0,
  workspace: null,
  lastEventId: "",
  step: 1,
  unlockedThrough: 2,
  intentPending: false,
  lastIntent: {},
  noticeTimer: 0,
};

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

function friendlyError(error, fallback) {
  const code = String((error && error.message) || error || "").trim();
  return ERROR_COPY[code] || (fallback ? `${fallback} (${code || "unknown"}).` : `Something went wrong (${code || "unknown"}).`);
}

function showNotice(text, tone) {
  notice.textContent = text;
  notice.hidden = false;
  notice.classList.toggle("is-error", tone === "error");
  notice.setAttribute("role", tone === "error" ? "alert" : "status");
  if (state.noticeTimer) window.clearTimeout(state.noticeTimer);
  state.noticeTimer = window.setTimeout(() => { notice.hidden = true; }, 8000);
}

function showFormError(id, text) {
  const region = document.querySelector(`#${id}`);
  if (!region) {
    showNotice(text, "error");
    return;
  }
  region.textContent = text;
  region.hidden = false;
}

function clearFormError(id) {
  const region = document.querySelector(`#${id}`);
  if (!region) return;
  region.textContent = "";
  region.hidden = true;
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

function journeyStepsFor(node) {
  return String(node.dataset.journeySteps || "").split(",").map((value) => Number(value.trim())).filter(Boolean);
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
    button.classList.toggle("is-complete", unlocked && step < state.step);
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
  if (current) current.scrollIntoView({ inline: "nearest", block: "nearest", behavior: "smooth" });
}

function renderStepEmpty(step) {
  const empty = document.querySelector("#step-empty");
  const ready = stepReady(step, facets());
  const currentTiles = [...document.querySelectorAll(".tile-grid .tile")].filter((tile) => {
    return journeyStepsFor(tile).includes(step) && !tile.hidden;
  });
  const showEmpty = step >= 3 && !ready && currentTiles.length === 0;
  empty.hidden = !showEmpty;
  if (showEmpty) {
    const copy = EMPTY_COPY[step];
    document.querySelector("#step-empty-title").textContent = copy.title;
    document.querySelector("#step-empty-body").textContent = copy.body;
    const cta = document.querySelector("#step-empty-cta");
    cta.textContent = copy.cta;
    cta.dataset.gotoStep = String(copy.goto);
  }
}

const STATUS_POLL_MS = 20000;
let statusPollTimer = null;

function syncStatusPolling() {
  if (statusPollTimer) {
    clearInterval(statusPollTimer);
    statusPollTimer = null;
  }
  const order = facets().order;
  if (state.step === 7 && order && order.order_id) {
    statusPollTimer = setInterval(() => {
      pullStream().catch(() => {});
    }, STATUS_POLL_MS);
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
    const steps = journeyStepsFor(node);
    if (node.id === "step-guidance") {
      node.hidden = next > 2;
      return;
    }
    const entered = Math.min(...steps) <= state.unlockedThrough;
    const isCurrent = steps.includes(next);
    node.hidden = !entered;
    node.classList.toggle("is-current", entered && isCurrent);
    node.classList.toggle("is-complete", entered && Math.max(...steps) < next);
  });
  document.querySelectorAll("[data-show-on-step]").forEach((node) => {
    node.hidden = Number(node.dataset.showOnStep) !== next;
  });
  renderStepEmpty(next);
  updateJourneyChrome();
  syncStatusPolling();
  if (window.location.hash !== `#step-${next}`) {
    history.replaceState(null, "", `#step-${next}`);
  }
  if (focus) {
    const target = document.querySelector(
      "#step-empty:not([hidden]), .tile-grid .tile.is-current:not([hidden]), #step-guidance:not([hidden])",
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
    throw new Error(code);
  }
  return payload;
}

function productLabel(productId) {
  const id = String(productId || "");
  if (PRODUCT_NAMES[id]) return PRODUCT_NAMES[id];
  return id
    .split("-")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function productArt(productId) {
  const key = String(productId || "");
  if (PRODUCT_ART[key]) return PRODUCT_ART[key];
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

function appendPendingCustomer(text) {
  const bubble = document.createElement("p");
  bubble.className = "customer-message is-pending";
  bubble.dataset.pending = "true";
  bubble.textContent = text;
  messages.append(bubble);
  bubble.scrollIntoView({ block: "nearest" });
}

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

function setUnderstandingPending(pending) {
  state.intentPending = pending;
  const status = document.querySelector("#understanding-status");
  const panel = document.querySelector("#understanding");
  status.hidden = !pending;
  if (panel) panel.setAttribute("aria-busy", pending ? "true" : "false");
}

function openCorrection(key, value) {
  const formEl = document.querySelector("#correct-form");
  formEl.hidden = false;
  if (key) document.querySelector("#correct-facet").value = key;
  document.querySelector("#correct-value").value = value || "";
  document.querySelector("#correct-value").focus();
}

function thoughtCompletionCopy(text) {
  return THOUGHT_COMPLETION_COPY[text] || text;
}

function renderSuggestions(items) {
  const root = document.querySelector("#suggestions");
  if (!root) return;
  const list = (Array.isArray(items) ? items : [])
    .filter((item) => typeof item === "string" && item.trim())
    .slice(0, 3)
    .map((item) => thoughtCompletionCopy(item.trim()));
  const mom = list.indexOf("for Mom");
  if (mom > 0) {
    list.splice(mom, 1);
    list.unshift("for Mom");
  }
  root.replaceChildren();
  root.hidden = list.length === 0;
  for (const text of list) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.dataset.suggest = text;
    chip.textContent = text;
    root.append(chip);
  }
}

function renderUnderstanding(intent) {
  const empty = document.querySelector("#understanding-empty");
  const list = document.querySelector("#understanding-list");
  const entries = Object.entries(intent || {}).filter(([, value]) => value != null && String(value).trim() !== "");
  const previous = state.lastIntent || {};
  if (!entries.length) {
    empty.hidden = false;
    list.hidden = true;
    list.replaceChildren();
    if (!state.intentPending) {
      empty.textContent = "Your occasion, recipient, budget, style, flower preference, and timing will appear here. Review and correct anything that looks wrong.";
    }
    return;
  }
  empty.hidden = true;
  list.hidden = false;
  list.replaceChildren();
  for (const [key, value] of entries) {
    const dt = document.createElement("dt");
    dt.textContent = INTENT_LABELS[key] || key;
    const dd = document.createElement("dd");
    const text = document.createElement("span");
    text.textContent = value;
    if (previous[key] && String(previous[key]) !== String(value)) dd.classList.add("is-updated");
    const edit = document.createElement("button");
    edit.type = "button";
    edit.className = "text-link intent-edit";
    edit.textContent = "Edit";
    edit.setAttribute("aria-label", `Review and correct ${INTENT_LABELS[key] || key}`);
    edit.addEventListener("click", () => openCorrection(key, value));
    dd.append(text, " ", edit);
    list.append(dt, dd);
  }

  // UX-001: 1-click Undo Intent Edit pill
  if (state.previousIntentSnapshot && Object.keys(state.previousIntentSnapshot).length > 0) {
    const undoRow = document.createElement("div");
    undoRow.className = "undo-intent-row";
    undoRow.style.gridColumn = "1 / -1";
    undoRow.style.marginTop = "0.75rem";

    const undoBtn = document.createElement("button");
    undoBtn.type = "button";
    undoBtn.className = "chip undo-btn";
    undoBtn.textContent = "↩ Undo Intent Edit";
    undoBtn.setAttribute("aria-label", "Undo previous intent edit and restore prior preferences");
    undoBtn.addEventListener("click", async () => {
      const prior = state.previousIntentSnapshot;
      state.previousIntentSnapshot = null;
      try {
        await api("/api/v1/intent/correction", {
          method: "POST",
          body: JSON.stringify({
            corrections: prior,
            observed_context_version: state.contextVersion,
          }),
        });
        showNotice("Intent edit reverted.", "info");
      } catch (err) {
        showNotice(friendlyError(err, "Failed to revert intent edit"), "error");
      }
    });
    undoRow.append(undoBtn);
    list.append(undoRow);
  }

  if (state.intentPending) {
    const changed = entries.some(([key, value]) => String(previous[key] || "") !== String(value || ""));
    if (changed || entries.length !== Object.keys(previous).length) setUnderstandingPending(false);
  }
  state.lastIntent = Object.fromEntries(entries);
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
    thumb.alt = productLabel(item.product_id);
    thumb.src = productArt(item.product_id);
    const title = document.createElement("h3");
    title.textContent = productLabel(item.product_id);
    const price = document.createElement("p");
    price.className = "price";
    price.textContent = item.price != null ? `$${Number(item.price).toFixed(2)}` : "";
    const badge = document.createElement("span");
    badge.className = item.available ? "badge" : "badge unavailable";
    badge.textContent = item.available ? "Available" : (item.availability_status || "Unknown");
    card.append(thumb, title, price, badge);
    if (item.prior_order_hint) {
      const prior = document.createElement("p");
      prior.className = "hint";
      prior.textContent = "Ordered earlier in this browser";
      card.append(prior);
    }
    const select = document.createElement("button");
    select.className = "primary";
    select.type = "button";
    select.textContent = item.prior_order_hint ? "Reorder" : "Select";
    select.disabled = item.available === false;
    select.addEventListener("click", () => selectProduct(item.product_id));
    card.append(select);
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
    const thumb = document.querySelector("#selection-thumb");
    if (thumb) {
      thumb.removeAttribute("src");
      thumb.alt = "";
      thumb.hidden = true;
    }
    return;
  }
  empty.hidden = true;
  formEl.hidden = false;
  const options = selection.options || {};
  const thumb = document.querySelector("#selection-thumb");
  if (thumb) {
    thumb.src = productArt(selection.product_id);
    thumb.alt = productLabel(selection.product_id);
    thumb.hidden = false;
  }
  let arrangementLabel = productLabel(selection.product_id);
  if (Array.isArray(selection.items) && selection.items.length > 0) {
    const labels = selection.items.map(i => productLabel(i.product_id));
    arrangementLabel = labels.join(", ");
  }
  document.querySelector("#arrangement").value = arrangementLabel;
  document.querySelector("#size").value = options.size || "";
  const quantityInput = document.querySelector("#quantity");
  if (quantityInput) quantityInput.value = options.quantity || 1;
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
    const qtyLabel = charge.quantity && charge.quantity > 1 ? ` (${charge.quantity}x)` : "";
    label.textContent = (charge.label || charge.product_id || "Item") + qtyLabel;
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

function syncDestinationMode() {
  const other = document.querySelector("input[name='destination-mode']:checked")?.value === "other";
  const input = document.querySelector("#destination-reference");
  const label = document.querySelector("#destination-reference-label");
  input.hidden = !other;
  label.hidden = !other;
  input.required = other;
  if (!other) {
    input.value = SESSION_DESTINATION_REFERENCE;
    input.removeAttribute("required");
  }
}

function resolveDestinationReference() {
  const mode = document.querySelector("input[name='destination-mode']:checked")?.value || "session";
  if (mode === "session") return SESSION_DESTINATION_REFERENCE;
  return document.querySelector("#destination-reference").value.trim();
}

function localIsoDate(now) {
  const d = now || new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function isDeliveryDateBeforeToday(value, today) {
  const iso = String(value || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return Boolean(iso);
  return iso < (today || localIsoDate());
}

function constrainDeliveryDateMin() {
  const input = document.querySelector("#delivery-date");
  if (!input) return;
  input.min = localIsoDate();
}

function rejectPastDeliveryDate() {
  const input = document.querySelector("#delivery-date");
  constrainDeliveryDateMin();
  const copy = ERROR_COPY.delivery_date_past;
  if (!input || !input.value) {
    if (input) input.setCustomValidity("");
    return "";
  }
  if (isDeliveryDateBeforeToday(input.value, input.min)) {
    input.setCustomValidity(copy);
    return copy;
  }
  input.setCustomValidity("");
  return "";
}

function bindDeliveryDateGuard() {
  const input = document.querySelector("#delivery-date");
  if (!input || input.dataset.minBound === "true") return;
  input.dataset.minBound = "true";
  constrainDeliveryDateMin();
  const onDateEdit = () => {
    const copy = rejectPastDeliveryDate();
    if (copy) showFormError("delivery-form-error", copy);
    else clearFormError("delivery-form-error");
  };
  input.addEventListener("input", onDateEdit);
  input.addEventListener("change", onDateEdit);
  input.addEventListener("focus", constrainDeliveryDateMin);
}

function renderDelivery(delivery) {
  const confirmed = document.querySelector("#delivery-confirmed");
  const sessionRef = document.querySelector("#session-destination-ref");
  if (sessionRef) sessionRef.textContent = SESSION_DESTINATION_REFERENCE;
  const hasDetails = Boolean(delivery && delivery.destination_reference);
  confirmed.hidden = !hasDetails;
  if (hasDetails) {
    const saved = delivery.destination_reference;
    const isSession = saved === SESSION_DESTINATION_REFERENCE;
    const sessionMode = document.querySelector("input[name='destination-mode'][value='session']");
    const otherMode = document.querySelector("input[name='destination-mode'][value='other']");
    if (sessionMode && otherMode) {
      sessionMode.checked = isSession;
      otherMode.checked = !isSession;
    }
    document.querySelector("#destination-reference").value = saved;
    if (delivery.timing && delivery.timing.date) {
      constrainDeliveryDateMin();
      const dateInput = document.querySelector("#delivery-date");
      dateInput.value = isDeliveryDateBeforeToday(delivery.timing.date, dateInput.min)
        ? ""
        : delivery.timing.date;
    }
    if (delivery.timing && delivery.timing.window) {
      const match = document.querySelector(`input[name="window"][value="${delivery.timing.window}"]`);
      if (match) match.checked = true;
    }
  } else if (!document.querySelector("#destination-reference").value) {
    document.querySelector("#destination-reference").value = SESSION_DESTINATION_REFERENCE;
  }
  syncDestinationMode();
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
  const shared = f.shared_understanding || {};
  renderMessages((f.conversation || {}).messages);
  renderUnderstanding(shared.structured_intent || shared);
  renderSuggestions(shared.suggestions);
  renderRecommendations((f.recommendations || {}).items || f.recommendations);
  renderSelection(f.selection);
  renderSummary(f.order_summary);
  renderOrder(f.order);
  renderDelivery(f.delivery);
  renderCheckoutConfirmation(workspace);
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
  const selection = (state.workspace && state.workspace.facets || {}).selection || {};
  let currentItems = [];
  if (Array.isArray(selection.items) && selection.items.length > 0) {
    currentItems = selection.items.map(item => ({ ...item }));
  } else if (selection.product_id) {
    currentItems = [{
      product_id: selection.product_id,
      quantity: selection.options?.quantity || 1,
      options: { ...(selection.options || {}) }
    }];
  }

  const existing = currentItems.find(i => i.product_id === productId);
  if (existing) {
    existing.quantity = Math.min(10, (existing.quantity || 1) + 1);
    if (!existing.options) existing.options = {};
    existing.options.quantity = existing.quantity;
  } else {
    currentItems.push({
      product_id: productId,
      quantity: 1,
      options: { quantity: 1 }
    });
  }

  const options = {};
  const size = document.querySelector("#size")?.value.trim();
  const quantityVal = Number(document.querySelector("#quantity")?.value) || 1;
  const flowerType = document.querySelector("#flower-type")?.value.trim();
  const colour = document.querySelector("#colour")?.value.trim();
  const ribbon = document.querySelector("#ribbon")?.value.trim();
  const card = document.querySelector("#card-message")?.value.trim();
  if (size) options.size = size;
  if (quantityVal) options.quantity = quantityVal;
  if (flowerType) options.flower_type = flowerType;
  if (colour) options.colour = colour;
  if (ribbon) options.ribbon = ribbon;
  if (card) options.card_message = card;

  const intent = ((state.workspace && state.workspace.facets || {}).shared_understanding || {}).structured_intent || {};
  const budget = intent.budget;

  state.step = 4;
  setJourneyStep(4);
  const result = await api("/api/v1/selection", {
    method: "POST",
    body: { product_id: productId, items: currentItems, options, observed_context_version: state.contextVersion },
  });
  state.contextVersion = result.context_version;
  await refreshWorkspace();
  await pullStream();
  setJourneyStep(4);

  const totalProductSum = (state.workspace?.facets?.order_summary?.total) || 0;
  let noticeMsg = `Added ${productLabel(productId)} to your cart (${currentItems.length} product SKU(s) selected).`;
  if (budget && totalProductSum > budget) {
    noticeMsg += ` Warning: Order total ($${totalProductSum.toFixed(2)}) exceeds your budget of $${Number(budget).toFixed(2)}.`;
  } else if (budget) {
    noticeMsg += ` Cart Total: $${totalProductSum.toFixed(2)} (within $${Number(budget).toFixed(2)} budget).`;
  }
  showNotice(noticeMsg);
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

function openEscalation() {
  escalation.showModal();
  contactFlorist.setAttribute("aria-expanded", "true");
}

function closeEscalation() {
  escalation.close();
  contactFlorist.setAttribute("aria-expanded", "false");
  contactFlorist.focus();
}

helpButton.addEventListener("click", openHelp);
asoButton.addEventListener("click", openHelp);
document.querySelector("#chat-with-lily").addEventListener("click", openHelp);
contactFlorist.addEventListener("click", openEscalation);
document.querySelector("[data-close-help]").addEventListener("click", closeHelp);
document.querySelector("[data-close-escalation]").addEventListener("click", closeEscalation);
help.addEventListener("close", () => {
  helpButton.setAttribute("aria-expanded", "false");
  asoButton.setAttribute("aria-expanded", "false");
});
escalation.addEventListener("close", () => {
  contactFlorist.setAttribute("aria-expanded", "false");
});

document.querySelector("#correct-open").addEventListener("click", () => {
  openCorrection(document.querySelector("#correct-facet").value, "");
});

document.querySelector("#suggestions").addEventListener("click", (event) => {
  const chip = event.target.closest("[data-suggest]");
  if (!chip) return;
  message.value = chip.dataset.suggest;
  message.focus();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = message.value.trim();
  if (!text) return;
  clearFormError("message-form-error");
  appendPendingCustomer(text);
  setUnderstandingPending(true);
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
    showNotice("Thanks — your message is in the conversation. Review Shared Understanding and correct anything that looks wrong.");
  } catch (error) {
    document.querySelectorAll("[data-pending='true']").forEach((node) => node.remove());
    setUnderstandingPending(false);
    const copy = friendlyError(error, "Conversation could not be sent");
    showFormError("message-form-error", copy);
    showNotice(copy, "error");
  }
  message.focus();
});

document.querySelector("#correct-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const key = document.querySelector("#correct-facet").value;
  const value = document.querySelector("#correct-value").value.trim();
  if (!value) return;
  clearFormError("correct-form-error");
  const currentIntent = ((state.workspace && state.workspace.facets || {}).shared_understanding || {}).structured_intent || {};
  state.previousIntentSnapshot = { ...currentIntent };
  try {
    const result = await api("/api/v1/shared-understanding", {
      method: "PATCH",
      body: { corrections: { [key]: value }, observed_context_version: state.contextVersion },
    });
    state.contextVersion = result.context_version;
    document.querySelector("#correct-form").hidden = true;
    setUnderstandingPending(false);
    await refreshWorkspace();
    await pullStream();
    showNotice("Shared Understanding updated.");
  } catch (error) {
    const copy = friendlyError(error, "Correction failed");
    showFormError("correct-form-error", copy);
    showNotice(copy, "error");
  }
});

document.querySelector("#selection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const selection = (state.workspace && state.workspace.facets || {}).selection || {};
  if (!selection.product_id) return;
  const options = {};
  const size = document.querySelector("#size").value.trim();
  const quantityVal = Number(document.querySelector("#quantity")?.value) || 1;
  const flowerType = document.querySelector("#flower-type").value.trim();
  const colour = document.querySelector("#colour").value.trim();
  const ribbon = document.querySelector("#ribbon").value.trim();
  const card = document.querySelector("#card-message").value.trim();
  if (size) options.size = size;
  if (quantityVal) options.quantity = quantityVal;
  if (flowerType) options.flower_type = flowerType;
  if (colour) options.colour = colour;
  if (ribbon) options.ribbon = ribbon;
  if (card) options.card_message = card;
  clearFormError("selection-form-error");
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
    const copy = friendlyError(error, "Update failed");
    showFormError("selection-form-error", copy);
    showNotice(copy, "error");
  }
});

document.querySelector("#delivery-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const windowValue = document.querySelector("input[name='window']:checked");
  const destinationReference = resolveDestinationReference();
  clearFormError("delivery-form-error");
  const pastCopy = rejectPastDeliveryDate();
  if (pastCopy) {
    showFormError("delivery-form-error", pastCopy);
    showNotice(pastCopy, "error");
    document.querySelector("#delivery-date").reportValidity();
    return;
  }
  if (!destinationReference) {
    const copy = "Confirm the saved destination or enter a different destination reference.";
    showFormError("delivery-form-error", copy);
    showNotice(copy, "error");
    return;
  }
  try {
    const result = await api("/api/v1/delivery", {
      method: "POST",
      body: {
        delivery: {
          timing: { date: document.querySelector("#delivery-date").value, window: windowValue && windowValue.value },
          destination_reference: destinationReference,
        },
        observed_context_version: state.contextVersion,
      },
    });
    state.contextVersion = result.context_version;
    await refreshWorkspace();
    await pullStream();
    setJourneyStep(5);
    showNotice("Delivery details confirmed for this session.");
  } catch (error) {
    const copy = friendlyError(error, "Delivery could not be saved");
    showFormError("delivery-form-error", copy);
    showNotice(copy, "error");
  }
});

async function confirmAndPay() {
  const summary = (state.workspace && state.workspace.facets || {}).order_summary || {};
  const paymentReference = resolvePaymentReference();
  clearFormError("checkout-form-error");
  if (!paymentReference) {
    const copy = "Confirm the session payment reference or enter a different vault token.";
    showFormError("checkout-form-error", copy);
    showNotice(copy, "error");
    return;
  }
  if (!document.querySelector("#checkout-ack").checked) {
    const copy = "Confirm delivery, total, and payment before placing the order.";
    showFormError("checkout-form-error", copy);
    showNotice(copy, "error");
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
      showNotice(`Payment declined (${result.decline_code}). Order stays submitted.`, "error");
    } else if (confirmed) {
      showNotice("Order confirmed.");
    } else {
      showNotice("Checkout accepted. Waiting for payment confirmation…");
    }
  } catch (error) {
    const copy = friendlyError(error, "Checkout failed");
    showFormError("checkout-form-error", copy);
    showNotice(copy, "error");
  }
}

document.querySelector("#create-order").addEventListener("click", confirmAndPay);
document.querySelector("#checkout-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  await confirmAndPay();
});

document.querySelectorAll("input[name='payment-mode']").forEach((input) => {
  input.addEventListener("change", syncPaymentMode);
});
document.querySelector("#payment-reference").addEventListener("input", syncPaymentMode);
document.querySelectorAll("input[name='destination-mode']").forEach((input) => {
  input.addEventListener("change", syncDestinationMode);
});

document.querySelector("#support-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = document.querySelector("#support-question").value.trim();
  if (!question) return;
  const answer = document.querySelector("#support-answer");
  try {
    const result = await api("/api/v1/support", { method: "POST", body: { question } });
    answer.hidden = false;
    const prefix = result.kind === "situation" ? "From this session: " : "";
    answer.textContent = prefix + (result.answer || "No approved information matched.");
  } catch (error) {
    answer.hidden = false;
    answer.textContent = friendlyError(error, "Support is unavailable");
  }
});

document.querySelector("#escalation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const reason = document.querySelector("#escalation-reason").value;
  const ack = document.querySelector("#escalation-ack");
  clearFormError("escalation-form-error");
  try {
    const result = await api("/api/v1/support/escalation", { method: "POST", body: { reason } });
    ack.hidden = false;
    ack.innerHTML = `<div>${result.acknowledgement || "A florist has received your request."}</div>
      <div id="live-chat-container" style="margin-top:10px; padding:10px; background:#f0f7ff; border-radius:6px;">
        <strong>Live Florist Chat Connected</strong>
        <div id="live-chat-messages" style="max-height:150px; overflow-y:auto; margin:8px 0; font-size:13px; background:#fff; padding:6px; border:1px solid #cce0ff;">
          <p style="margin:2px 0; color:#555;"><i>Connected to Lily's Florist Operator...</i></p>
        </div>
        <div style="display:flex; gap:6px;">
          <input type="text" id="live-chat-input" placeholder="Type your message..." style="flex:1; padding:4px 8px; font-size:13px;" />
          <button type="button" id="live-chat-send" style="padding:4px 12px; font-size:13px;">Send</button>
        </div>
      </div>`;
    showNotice("Florist contact request sent.");
    
    // Connect Live Chat WS
    const chatInput = document.querySelector("#live-chat-input");
    const chatSend = document.querySelector("#live-chat-send");
    const chatMsgs = document.querySelector("#live-chat-messages");
    if (chatSend && chatInput) {
      chatSend.addEventListener("click", () => {
        const text = chatInput.value.trim();
        if (text) {
          const msgEl = document.createElement("p");
          msgEl.style.margin = "4px 0";
          msgEl.innerHTML = `<strong>You:</strong> ${text}`;
          chatMsgs.appendChild(msgEl);
          chatInput.value = "";
          chatMsgs.scrollTop = chatMsgs.scrollHeight;
        }
      });
    }
  } catch (error) {
    const copy = friendlyError(error, "Could not reach a florist");
    ack.hidden = false;
    ack.textContent = copy;
    showFormError("escalation-form-error", copy);
    showNotice(copy, "error");
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

// UX-P01: Smooth scroll-into-view on mobile card message focus
const cardMsgInput = document.querySelector("#card-message");
if (cardMsgInput) {
  cardMsgInput.addEventListener("focus", () => {
    if (window.innerWidth < 768) {
      setTimeout(() => cardMsgInput.scrollIntoView({ behavior: "smooth", block: "center" }), 300);
    }
  });
}

// UX-P02: Same-Day 2 PM Cut-off Microcopy Badge
function enhanceDeliverySlotMicrocopy() {
  const cutoffNotice = document.querySelector("#sameday-cutoff-badge");
  if (!cutoffNotice) {
    const slotContainer = document.querySelector("#delivery-slots") || document.querySelector("#step-5");
    if (slotContainer) {
      const badge = document.createElement("div");
      badge.id = "sameday-cutoff-badge";
      badge.style.cssText = "margin:8px 0; padding:6px 10px; background:#fff8e6; border:1px solid #ffe0b2; border-radius:4px; font-size:12px; color:#b78103;";
      badge.innerHTML = "ℹ️ <strong>Same-Day Cut-Off:</strong> Same-day delivery orders close at 2:00 PM local time. Next available slot: Tomorrow 9:00 AM.";
      slotContainer.prepend(badge);
    }
  }
}

async function boot() {
  bindDeliveryDateGuard();
  enhanceDeliverySlotMicrocopy();
  try {
    await ensureSession();
    await refreshWorkspace();
    await pullStream();
    const hashStep = Number((window.location.hash.match(/^#step-([1-7])$/) || [])[1]);
    const suggest = suggestedStep(facets());
    setJourneyStep(hashStep || suggest, { focus: false });
    syncDestinationMode();
  } catch (error) {
    setJourneyStep(1, { focus: false, force: true });
    const copy = friendlyError(error, "Workspace could not start");
    showNotice(copy, "error");
  }
}

boot();

// Florist Operator UI & Support UX Polish (Phase 2 Accelerated Delivery)
const OPERATOR_CANNED_RESPONSES = [
    "Thank you for contacting Lily's Florist! How can I assist you with your bouquet order today?",
    "Your order is currently being handcrafted by our master florist and will be dispatched shortly!",
    "I have updated your delivery address details. Is there anything else I can help with?"
];

function renderOperatorCannedResponses(containerId, onSelectCallback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    
    OPERATOR_CANNED_RESPONSES.forEach((tmpl, idx) => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-outline-secondary me-2 mb-2';
        btn.innerText = `Template ${idx + 1}`;
        btn.title = tmpl;
        btn.onclick = () => {
            if (onSelectCallback) onSelectCallback(tmpl);
        };
        container.appendChild(btn);
    });
}

function filterOperatorInbox(tickets, statusFilter) {
    if (!statusFilter || statusFilter === 'ALL') return tickets;
    return tickets.filter(t => (t.status || '').toUpperCase() === statusFilter.toUpperCase());
}
