from html.parser import HTMLParser
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1] / "gateway"


class UiParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.labels = set()
        self.aria = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append(tag)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "label" and values.get("for"):
            self.labels.add(values["for"])
        self.aria.extend(key for key in values if key.startswith("aria-"))


class BrowserUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "ui" / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.script = (ROOT / "ui" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.parser = UiParser()
        cls.parser.feed(cls.html)

    def test_interface_has_one_clear_conversation_entry_point(self):
        self.assertEqual(1, self.html.count('id="message-form"'))
        self.assertIn('placeholder="For example:', self.html)
        self.assertIn("You can change every detail later", self.html)
        self.assertIn("Nothing is final until you review", self.html)
        self.assertIn('onsubmit="event.preventDefault()"', self.html)

    def test_app_js_does_not_use_unquoted_template_interpolations(self):
        """A single unquoted ${...} is a SyntaxError and kills T-01/T-02 boot."""
        for i, line in enumerate(self.script.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if "${" in line and "`" not in line:
                self.fail(
                    f"app.js line {i} interpolates without backticks (parse error): {line}"
                )
            if re.search(r"\bfetch\s*\(\s*/", line):
                self.fail(
                    f"app.js line {i} uses an unquoted fetch URL (parse error): {line}"
                )

    def test_semantic_landmarks_labels_and_live_feedback_are_present(self):
        for tag in ("header", "main", "section", "aside", "form", "label", "dialog"):
            self.assertIn(tag, self.parser.tags)
        self.assertIn("message", self.parser.labels)
        self.assertIn("aria-live", self.parser.aria)
        self.assertIn('href="#conversation"', self.html)

    def test_keyboard_focus_and_help_return_are_explicit(self):
        self.assertIn(":focus-visible", self.css)
        self.assertIn("helpButton.focus()", self.script)
        self.assertIn('aria-expanded="false"', self.html)

    def test_gateway_serves_ui_without_weakening_api_perimeter(self):
        nginx = (ROOT / "nginx.conf").read_text(encoding="utf-8")
        alb = (ROOT / "nginx-alb.conf").read_text(encoding="utf-8")
        self.assertIn("include /etc/nginx/mime.types;", nginx)
        self.assertIn("location = / {", nginx)
        self.assertIn("location /api/ {", nginx)
        self.assertIn("location /webhooks/ {", nginx)
        self.assertIn("location /cloud/ {", nginx)
        self.assertIn("set $agent_upstream http://agent-runner:8080;", nginx)
        self.assertNotIn("proxy_pass http://aea-agent-runner", nginx)
        self.assertIn('proxy_set_header X-Internal-Identity "";', nginx)
        self.assertIn("location = / {", alb)
        self.assertIn("location /api/ {", alb)
        self.assertIn("location /webhooks/ {", alb)
        self.assertIn("location /cloud/ {", alb)
        self.assertNotIn("<<<<<<<", alb)
        self.assertNotIn(">>>>>>>", alb)
        self.assertIn("set $agent_upstream __AGENT_UPSTREAM__;", alb)
        self.assertIn('proxy_set_header X-Internal-Identity "";', alb)

    def test_layout_has_explicit_desktop_tablet_and_mobile_contracts(self):
        self.assertIn("grid-template-columns: minmax(0, 1.7fr)", self.css)
        self.assertIn("@media (max-width: 60rem)", self.css)
        self.assertIn("@media (max-width: 40rem)", self.css)
        self.assertIn("grid-template-columns: 1fr", self.css)
        self.assertIn("grid-area: conversation", self.css)
        self.assertIn("grid-area: understanding", self.css)
        tablet = self.css.split("@media (max-width: 60rem)", 1)[1].split("@media", 1)[0]
        self.assertNotIn("order: -1", tablet)
        self.assertIn('"conversation understanding"', tablet)
        self.assertIn('"main main"', tablet)
        conversation = self.html.index('id="conversation"')
        understanding = self.html.index('id="understanding"')
        workspace_main = self.html.index('class="workspace-main"')
        self.assertLess(conversation, understanding)
        self.assertLess(understanding, workspace_main)

    def test_mobile_controls_and_content_resist_clipping(self):
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("width: 100%", self.css)
        self.assertIn('name="viewport"', self.html)
        self.assertIn("viewport-fit=cover", self.html)
        self.assertIn("overflow-x: clip", self.css)
        self.assertIn("env(safe-area-inset-bottom", self.css)
        self.assertIn("width: min(calc(100% - 2rem), 1440px)", self.css)
        self.assertIn('class="help-button"', self.html)
        self.assertIn('class="aso"', self.html)
        # Duplicate ASO FAB is hidden on narrow viewports; header Help remains.
        self.assertIn(".aso { display: none; }", self.css)
        mobile = self.css.split("@media (max-width: 40rem)", 1)[1].split("@media", 1)[0]
        self.assertNotIn("overflow-x: hidden", mobile)
        self.assertNotIn("min-width: 3.25rem", mobile)
        self.assertIn(".journey-nav .steps { display: none; }", mobile)
        self.assertIn(".journey-nav .phases {", mobile)
        self.assertIn('id="journey-phases"', self.html)
        self.assertIn('data-phase="need"', self.html)
        self.assertIn('data-phase="pick"', self.html)
        self.assertIn('data-phase="pay"', self.html)
        self.assertNotIn("data-short", self.html)
        self.assertIn('data-step="7"', self.html)
        self.assertIn('inline: "nearest"', self.script)

    def test_platform_preferences_remain_usable(self):
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn("forced-colors: active", self.css)

    def test_adaptive_workspace_regions_match_discovery_v01(self):
        for region in ("conversation", "recommendations", "selection", "delivery",
                       "order-summary", "order-tracking"):
            self.assertIn(f'id="{region}"', self.html)
        self.assertIn("T-01", self.html)
        self.assertIn("T-02", self.html)
        self.assertIn("T-03", self.html)
        self.assertIn("T-04", self.html)
        self.assertIn("T-05", self.html)
        self.assertIn("T-08", self.html)
        self.assertIn("ASO FAQ overlay", self.html)
        self.assertIn("Lily's Florist", self.html)

    def test_t04_exposes_thin_fr003_fields(self):
        self.assertIn('id="size"', self.html)
        self.assertIn('id="quantity"', self.html)
        self.assertIn('id="card-message"', self.html)
        self.assertIn('id="flower-type"', self.html)
        self.assertIn('id="colour"', self.html)
        self.assertIn('id="ribbon"', self.html)
        self.assertIn("Arrangement", self.html)
        self.assertIn("Flower type", self.html)
        self.assertIn("PRODUCT_FLOWERS", self.script)
        self.assertIn("PRODUCT_NAMES", self.script)
        self.assertIn('"Classic Rose Dozen"', self.script)
        self.assertIn('"Budget Mixed Bunch"', self.script)
        self.assertIn("if (PRODUCT_NAMES[id]) return PRODUCT_NAMES[id];", self.script)
        self.assertIn("items: currentItems", self.script)
        self.assertNotIn('return String(productId || "").replace(/-/g, " ");', self.script)
        self.assertNotIn("gift card", self.html.lower())
        self.assertNotIn("gift_card", self.script.lower())
        self.assertEqual(1, self.html.count(">Continue to delivery<"))
        self.assertNotIn(">Update</button>", self.html)
        self.assertIn('type="submit">Continue to delivery</button>', self.html)
        self.assertIn("setJourneyStep(5);", self.script)

    def test_t03_ranking_skus_use_vendored_attributed_photos(self):
        assets = ROOT / "ui" / "assets"
        skus = (
            "classic-rose-dozen",
            "lilac-bouquet",
            "budget-mixed-bunch",
            "pink-flower-vase",
            "premium-orchid",
        )
        self.assertIn("const PRODUCT_ART", self.script)
        for sku in skus:
            self.assertIn(f'"{sku}": "/assets/sku-{sku}.jpg"', self.script)
            jpeg = assets / f"sku-{sku}.jpg"
            self.assertTrue(jpeg.exists(), sku)
            self.assertGreater(jpeg.stat().st_size, 10000)
            self.assertEqual(b"\xff\xd8\xff", jpeg.read_bytes()[:3])
        notice = (assets / "NOTICE.txt").read_text(encoding="utf-8")
        self.assertIn("classic-rose-dozen", notice)
        self.assertIn("Nancy Wong", notice)
        self.assertIn("George Chernilevsky", notice)
        self.assertIn("BEST Bud's for Life", notice)
        self.assertIn("Soumendra Kumar Sahoo", notice)
        self.assertIn("Guillaume Paumier", notice)
        self.assertIn("CC BY-SA 4.0", notice)
        self.assertIn("not photographs of this shop's cooler", notice)
        self.assertIn("not the rest of this", notice)
        self.assertIn("repository", notice)
        self.assertIn("thumb.alt = productLabel(item.product_id)", self.script)
        self.assertIn('id="selection-thumb"', self.html)
        self.assertIn("thumb.src = productArt(selection.product_id)", self.script)
        self.assertIn("not this shop's cooler", self.html)
        self.assertIn("Photo credits", self.html)
        self.assertIn("/assets/NOTICE.txt", self.html)
        self.assertNotIn("upload.wikimedia.org", self.script)
        self.assertNotIn("unsplash.com", self.script.lower())
        self.assertNotIn("pexels.com", self.script.lower())

    def test_sample_layout_3_color_and_journey_steps(self):
        self.assertIn('data-visual="sample-layout-3"', self.html)
        self.assertIn('data-journey-mode="steps"', self.html)
        self.assertIn('id="journey-steps"', self.html)
        self.assertIn('id="checkout"', self.html)
        for step in range(1, 8):
            self.assertIn(f'data-step="{step}"', self.html)
        self.assertIn('data-journey-steps="5,6"', self.html)
        self.assertIn('data-journey-steps="6"', self.html)
        self.assertIn("setJourneyStep", self.script)
        self.assertIn("STEP_CAPTIONS", self.script)
        self.assertIn("STATUS_POLL_MS", self.script)
        self.assertIn("syncStatusPolling", self.script)
        self.assertIn("state.step === 7", self.script)
        self.assertIn("--purple: #6344a9", self.css)
        self.assertIn("--green: #2f9e6b", self.css)
        self.assertIn("linear-gradient", self.css)
        self.assertIn("bouquet-hero.svg", self.html)
        self.assertIn("bouquet-pink.svg", self.script)
        self.assertIn("PRODUCT_ART", self.script)
        self.assertIn("sku-classic-rose-dozen.jpg", self.script)
        self.assertIn("Chat with Lily", self.html)
        self.assertIn("confirmed-banner", self.html)
        self.assertIn("payment-card", self.html)
        self.assertIn("florist-status.svg", self.html)
        self.assertTrue((ROOT / "ui" / "assets" / "bouquet-hero.svg").exists())

    def test_journey_activates_tiles_in_place_not_all_at_once(self):
        self.assertIn("Journey stages", self.html)
        self.assertIn("Continue to recommendations", self.html)
        self.assertIn('data-journey-steps="3"', self.html)
        self.assertIn('data-journey-steps="4"', self.html)
        self.assertIn('data-journey-steps="5"', self.html)
        self.assertIn('data-journey-steps="7"', self.html)
        self.assertIn("node.hidden = !entered", self.script)
        self.assertIn("is-current", self.script)
        self.assertIn("T-01 · Persistent", self.html)
        self.assertIn("T-02 · Persistent", self.html)
        self.assertIn("ASO FAQ overlay", self.html)
        self.assertIn("Earlier choices stay visible", self.html)

    def test_workspace_errors_are_inline_and_plain_language(self):
        self.assertIn('id="message-form-error"', self.html)
        self.assertIn('id="delivery-form-error"', self.html)
        self.assertIn('id="checkout-form-error"', self.html)
        self.assertIn('role="alert"', self.html)
        self.assertIn(".form-error", self.css)
        self.assertIn("ERROR_COPY", self.script)
        self.assertIn("csrf_rejected", self.script)
        self.assertIn("showFormError", self.script)
        self.assertIn("friendlyError", self.script)
        self.assertIn("Refresh the page, then try again.", self.script)
        self.assertNotIn("Conversation could not be sent (${error.message})", self.script)
        self.assertNotIn("Delivery could not be saved (${error.message})", self.script)

    def test_delivery_date_rejects_days_before_today(self):
        self.assertIn('id="delivery-date"', self.html)
        self.assertIn('type="date"', self.html)
        self.assertIn('id="delivery-date-hint"', self.html)
        self.assertIn("Today or later", self.html)
        self.assertIn("function localIsoDate", self.script)
        self.assertIn("function isDeliveryDateBeforeToday", self.script)
        self.assertIn("function constrainDeliveryDateMin", self.script)
        self.assertIn("function rejectPastDeliveryDate", self.script)
        self.assertIn("function bindDeliveryDateGuard", self.script)
        self.assertIn("input.min = localIsoDate()", self.script)
        self.assertIn("delivery_date_past", self.script)
        self.assertIn("Delivery cannot be scheduled in the past.", self.script)
        self.assertIn("Choose today or a later date.", self.script)
        self.assertIn("const pastCopy = rejectPastDeliveryDate()", self.script)
        self.assertIn("bindDeliveryDateGuard()", self.script)
        # Mirrors isDeliveryDateBeforeToday: YYYY-MM-DD compare; invalid non-empty fails closed.
        today = "2026-08-17"
        self.assertTrue(self._is_delivery_date_before_today("2026-08-16", today))
        self.assertFalse(self._is_delivery_date_before_today("2026-08-17", today))
        self.assertFalse(self._is_delivery_date_before_today("2026-08-18", today))
        self.assertFalse(self._is_delivery_date_before_today("", today))
        self.assertTrue(self._is_delivery_date_before_today("17/08/2026", today))

    @staticmethod
    def _is_delivery_date_before_today(value, today):
        iso = str(value or "").strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
            return bool(iso)
        return iso < today

    def test_delivery_confirms_saved_destination_reference(self):
        self.assertIn("SESSION_DESTINATION_REFERENCE", self.script)
        self.assertIn('id="session-destination-ref"', self.html)
        self.assertIn(">home<", self.html)
        self.assertIn("Confirm saved destination", self.html)
        self.assertIn("Confirm delivery details", self.html)
        self.assertIn("Saved destination reference", self.html)
        self.assertNotIn("Confirm Delivery", self.html)
        self.assertIn("resolveDestinationReference", self.script)

    def test_intent_summary_supports_review_and_correct(self):
        self.assertIn("Review and correct", self.html)
        self.assertIn('id="understanding-status"', self.html)
        self.assertIn("Updating from your last message", self.html)
        self.assertIn("appendPendingCustomer", self.script)
        self.assertIn("setUnderstandingPending", self.script)
        self.assertIn("intent-edit", self.script)
        self.assertIn('id="suggestions"', self.html)
        self.assertNotIn("data-suggest", self.html)
        self.assertIn("function renderSuggestions", self.script)
        self.assertIn("shared.suggestions", self.script)
        self.assertIn("chip.dataset.suggest", self.script)
        self.assertIn("chip.textContent", self.script)
        self.assertIn('id="suggestions-hint"', self.html)
        self.assertIn("They are not filters on the shop.", self.html)
        self.assertIn(".chip::before { content: \"+ \";", self.css)

    def test_checkout_is_confirmation_driven(self):
        self.assertIn('id="checkout-confirm"', self.html)
        self.assertIn('id="checkout-ack"', self.html)
        self.assertIn("SESSION_PAYMENT_REFERENCE", self.script)
        self.assertIn("renderCheckoutConfirmation", self.script)
        self.assertIn("resolvePaymentReference", self.script)
        self.assertIn("Confirm session payment reference", self.html)
        self.assertIn("I confirm delivery, total, and payment", self.html)
        self.assertIn("session_pay_ref", self.html)
        self.assertIn("async function confirmAndPay", self.script)
        self.assertIn('querySelector("#create-order").addEventListener("click", confirmAndPay)',
                      self.script)
        self.assertIn(".confirm-panel", self.css)
        self.assertIn("unlockedThrough", self.script)
        self.assertIn("stepReady", self.script)
        self.assertIn("EMPTY_COPY", self.script)
        self.assertIn('id="step-empty"', self.html)
        self.assertIn('id="step-empty-cta"', self.html)
        self.assertIn("is-locked", self.css)
        self.assertIn("phaseForStep", self.script)
        self.assertIn('id="journey-phases"', self.html)
        self.assertIn("data-requires-unlock", self.html)
        self.assertIn("Complete earlier steps to unlock", self.script)
        # Product selection suggests Customize (4), not Delivery (5).
        self.assertIn("if (f.selection && f.selection.product_id) return 4;", self.script)
        self.assertIn("prior_order_hint", self.script)
        self.assertIn("Ordered earlier in this browser", self.script)
        self.assertIn('item.prior_order_hint ? "Reorder" : "Select"', self.script)  # FR-008
        self.assertIn("state.step = 4;", self.script)
        select_fn = self.script.split("async function selectProduct", 1)[1].split("function openHelp", 1)[0]
        self.assertLess(select_fn.find("state.step = 4;"), select_fn.find("await refreshWorkspace()"))

    def test_shell_uses_edge_apis_without_data_plane_secrets(self):
        for path in ("/api/v1/session", "/api/v1/conversation/messages",
                     "/api/v1/shared-understanding", "/api/v1/workspace",
                     "/api/v1/stream", "/api/v1/selection"):
            self.assertIn(path, self.script)
        self.assertNotIn("postgres", self.script.lower())
        self.assertNotIn("kafka", self.script.lower())
        self.assertNotIn("5432", self.html + self.script)

    def test_contact_florist_is_t09_escalation_not_faq(self):
        self.assertIn('id="escalation"', self.html)
        self.assertIn('id="contact-florist"', self.html)
        self.assertIn('id="escalation-reason"', self.html)
        self.assertIn("T-09 · Support Escalation", self.html)
        self.assertIn("/api/v1/support/escalation", self.script)
        self.assertIn("From this session:", self.script)
        self.assertIn('result.kind === "situation"', self.script)
        self.assertIn("openEscalation", self.script)
        self.assertIn('contactFlorist.addEventListener("click", openEscalation)', self.script)
        self.assertNotIn('querySelector("#contact-florist").addEventListener("click", openHelp)',
                         self.script)
        self.assertNotIn("Escalate (Future)", self.html)
        self.assertIn("unresolved_request", self.html)
        self.assertIn("order_issue", self.html)
        self.assertIn("delivery_issue", self.html)
        self.assertIn("product_question", self.html)

    def test_mutating_fetches_send_csrf_and_use_allowed_windows(self):
        self.assertIn("async function ensureSession()", self.script)
        self.assertIn('"X-AEA-Client": "web"', self.script)
        self.assertIn('init.headers["X-CSRF-Token"] = state.csrf', self.script)
        self.assertIn('["POST", "PUT", "PATCH", "DELETE"]', self.script)
        self.assertIn('code === "csrf_rejected" || code === "session_required"', self.script)
        for path in ("/api/v1/conversation/messages", "/api/v1/delivery",
                     "/api/v1/selection", "/api/v1/checkout", "/api/v1/support",
                     "/api/v1/shared-understanding"):
            self.assertIn(path, self.script)
        self.assertIn('value="morning"', self.html)
        self.assertIn('value="afternoon"', self.html)
        self.assertIn('value="evening"', self.html)
        self.assertNotIn('value="10:00-12:00"', self.html)
        florist = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        self.assertIn("async function ensureSession()", florist)
        self.assertIn('"X-AEA-Client": "web"', florist)
        self.assertIn('code === "csrf_rejected" || code === "session_required"', florist)

    def test_florist_operator_console_is_separate_labeled_sample(self):
        html = (ROOT / "ui" / "florist.html").read_text(encoding="utf-8")
        script = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        nginx = (ROOT / "nginx.conf").read_text(encoding="utf-8")
        alb = (ROOT / "nginx-alb.conf").read_text(encoding="utf-8")
        self.assertIn("Local florist operator sample", html)
        self.assertIn("Not live chat", html)
        self.assertIn("FR-016", html)
        self.assertIn("aea-pilot", html)
        self.assertIn("Do not open this console in the same browser as", html)
        self.assertIn("Shop is a separate browser", html)
        self.assertNotIn(">Customer workspace<", html)
        self.assertNotIn('href="/">', html)
        self.assertIn("T-03 Select", html)
        self.assertIn('id="inbox"', html)
        self.assertIn('id="orders"', html)
        self.assertIn("/api/v1/operator/orders", script)
        self.assertIn("catalog_title", script)
        self.assertIn("payment_state", script)
        self.assertIn("item.channel", script)
        self.assertIn("item.card_message", script)
        self.assertIn('fact("Card message"', script)
        self.assertIn('fact("Channel"', script)
        self.assertIn('fact("Total"', script)
        self.assertIn("catalog_title", script)
        self.assertIn("<th scope=\"col\">Card</th>", html)
        self.assertIn("<th scope=\"col\">Channel</th>", html)
        self.assertIn("<th scope=\"col\">Paid</th>", html)
        self.assertIn('id="order-filter-today"', html)
        self.assertIn('id="order-filter-delayed"', html)
        # Per-section day-window filters (#398): orders gain 3/7-day windows and
        # the Contact Florist inbox gains its own Today/3/7/All filter group.
        self.assertIn('id="order-filter-3d"', html)
        self.assertIn('id="order-filter-7d"', html)
        self.assertIn('id="inbox-filter-today"', html)
        self.assertIn('id="inbox-filter-3d"', html)
        self.assertIn('id="inbox-filter-7d"', html)
        self.assertIn('id="inbox-filter-all"', html)
        self.assertIn("function filterOrders", script)
        self.assertIn("function filterInbox", script)
        self.assertIn("function isWithinDays", script)
        self.assertIn('orderFilter: "today"', script)
        self.assertIn('inboxFilter: "all"', script)
        self.assertIn("Select an order or inbox row", html)
        self.assertIn("Has order", script)
        self.assertIn(">Inbox</span>", script)
        self.assertIn("function sessionIdSet", script)
        self.assertNotIn("claim-btn", script)
        self.assertNotIn("resolve-btn", script)
        self.assertNotIn(">Claim</button>", script)
        self.assertNotIn(">Resolve</button>", script)
        self.assertNotIn('target.status = "In Progress"', script)
        self.assertNotIn('target.status = "Resolved"', script)
        self.assertIn("sessionIdSet(state.orders)", script)
        self.assertIn("sessionIdSet(state.items)", script)
        self.assertIn('sessionRef.textContent = "Select an order or inbox row."', script)
        self.assertNotIn("Select an inbox row when a request arrives.", script)
        self.assertIn("/api/v1/operator/escalations", script)
        self.assertIn("/api/v1/operator/sessions/", script)
        self.assertIn("/api/v1/operator/forecasts", script)
        self.assertIn('id="support-answers"', html)
        self.assertIn("What Lily already answered", html)
        self.assertIn("support_answers", script)
        self.assertIn('id="forecast"', html)
        self.assertIn("FR-012", html)
        self.assertIn("REASON_LABELS", script)
        self.assertIn("customer-message", script)
        self.assertNotIn("user-message", script)
        self.assertNotIn("Sample rows remain for layout", script)
        self.assertIn("No Contact Florist requests yet", script)
        self.assertNotIn("card_number", script)
        self.assertNotIn("postgres", script.lower())
        self.assertIn("location = /florist {", nginx)
        self.assertIn("try_files /florist.html =404;", nginx)
        self.assertIn("location /api/ {", nginx)
        self.assertIn('proxy_set_header X-Internal-Identity "";', nginx)
        self.assertIn("location = /florist {", alb)
        self.assertIn("try_files /florist.html =404;", alb)

    def test_florist_destination_handle_labels_without_street(self):
        script = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        self.assertIn("function destinationHandleLabel", script)
        self.assertIn('home: "Home"', script)
        self.assertIn('work: "Work"', script)
        self.assertIn("Destination handle", script)
        self.assertIn("destinationHandleLabel(item.destination_reference)", script)
        self.assertIn(
            "destinationHandleLabel(summary.delivery.destination_reference)", script)

    def test_florist_today_prepare_list_is_derived_from_staff_orders(self):
        html = (ROOT / "ui" / "florist.html").read_text(encoding="utf-8")
        script = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        self.assertIn('id="prepare"', html)
        self.assertIn('id="prepare-rows"', html)
        self.assertIn('id="prepare-title"', html)
        self.assertIn("Today's arrangements to prepare", html)
        self.assertIn("Grouped from Staff orders due today. Not inventory forecast. Not CRM.", html)
        self.assertIn("<th scope=\"col\">Arrangement</th>", html)
        self.assertIn("<th scope=\"col\">Count</th>", html)
        self.assertIn("<th scope=\"col\">Windows</th>", html)
        self.assertIn("<th scope=\"col\">Cards</th>", html)
        self.assertIn("<th scope=\"col\">Channels</th>", html)
        self.assertIn("const prepareRows = document.querySelector(\"#prepare-rows\")", script)
        self.assertIn("function groupPrepareItems", script)
        self.assertIn("function renderPrepare", script)
        self.assertIn("function uniqueSorted", script)
        self.assertIn("ordersError: false", script)
        self.assertIn('filterOrders(items, "today")', script)
        self.assertIn("item.catalog_title || item.product_id", script)
        self.assertIn("item.card_message).slice(0, 40)", script)
        self.assertIn("uniqueSorted(group.cards).slice(0, 2)", script)
        self.assertIn("uniqueSorted(group.windows)", script)
        self.assertIn("uniqueSorted(group.channels)", script)
        self.assertIn("No arrangements to prepare today.", script)
        self.assertIn("Could not load today's arrangements. This list stays empty.", script)
        self.assertIn("state.ordersError = true", script)
        self.assertIn("renderPrepare(state.orders)", script)
        self.assertIn("/api/v1/operator/orders", script)
        self.assertNotIn("/api/v1/operator/prepare", script)
        self.assertNotIn("street", script.lower())
        self.assertNotIn("email", script.lower())
        self.assertNotIn("card_number", script)
        self.assertNotIn("claim-btn", script)
        self.assertNotIn(">Claim</button>", script)

    def test_t01_thought_completion_chips_come_from_api(self):
        self.assertIn('id="suggestions"', self.html)
        self.assertIn('aria-label="Optional thought-completion suggestions"', self.html)
        self.assertNotIn('class="chip"', self.html)
        self.assertNotIn("Birthday flowers for Mum, under €75", self.html)
        self.assertNotIn("under €75", self.html)
        self.assertNotIn("under €75", self.script)
        self.assertNotIn(">Birthday</button>", self.html)
        self.assertNotIn(">Wedding</button>", self.html)
        self.assertNotIn(">Sympathy</button>", self.html)
        self.assertIn("function renderSuggestions", self.script)
        self.assertIn("renderSuggestions(shared.suggestions)", self.script)
        self.assertIn("function thoughtCompletionCopy", self.script)
        self.assertIn('THOUGHT_COMPLETION_COPY', self.script)
        self.assertIn('"Who are the flowers for?": "for Mom"', self.script)
        self.assertIn('"What is the occasion?": "for a birthday"', self.script)
        self.assertIn('"What budget should I work within?": "under $75"', self.script)
        self.assertIn("chip.dataset.suggest = text", self.script)
        self.assertIn("chip.textContent = text", self.script)
        self.assertIn('#suggestions").addEventListener("click"', self.script)
        self.assertNotIn('querySelectorAll("[data-suggest]")', self.script)
        self.assertIn('placeholder="For example: Birthday roses for Mum, under $75"', self.html)

    def test_florist_operator_mobile_table_and_order_overlay(self):
        html = (ROOT / "ui" / "florist.html").read_text(encoding="utf-8")
        script = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        css = (ROOT / "ui" / "assets" / "styles.css").read_text(encoding="utf-8")

        # HTML table wrap and dialog
        self.assertIn('class="operator-table-wrap"', html)
        self.assertIn('class="operator-table operator-table-orders"', html)
        self.assertIn('class="operator-table operator-table-prepare"', html)
        self.assertIn('class="operator-nav"', html)
        self.assertIn('class="operator-filter-wrap"', html)
        self.assertIn('class="dialog-sheet-handle"', html)
        self.assertIn('id="order-detail-dialog"', html)
        self.assertIn('id="order-dialog-facts"', html)
        self.assertIn('id="order-dialog-title"', html)
        self.assertIn('data-close-order-dialog', html)

        # JS date formatting and overlay
        self.assertIn("function formatRequestedDateHtml", script)
        self.assertIn("function openOrderDetail", script)
        self.assertIn("TABLE_HEADER_ICONS", script)
        self.assertIn("function decorateHeaderIcons", script)
        self.assertIn("order-detail-trigger", script)
        self.assertIn("order-cell-main", script)
        self.assertIn("order-mobile-meta", script)
        self.assertIn("prepare-mobile-meta", script)
        self.assertIn("dialog-card-note", script)

        # CSS mobile responsive 3-column table, nav, and dialog
        self.assertIn(".operator-table-wrap", css)
        self.assertIn(".operator-cell-date", css)
        self.assertIn(".operator-nav", css)
        self.assertIn(".operator-filter-wrap", css)
        self.assertIn(".operator-table-orders th:nth-child(n+4)", css)
        self.assertIn(".operator-table-prepare th:nth-child(n+4)", css)
        self.assertIn("dialog.operator-dialog", css)
        self.assertIn(".dialog-sheet-handle", css)
        self.assertIn(".dialog-card-note", css)


if __name__ == "__main__":
    unittest.main()
