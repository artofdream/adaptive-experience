from html.parser import HTMLParser
import pathlib
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
        self.assertIn("include /etc/nginx/mime.types;", nginx)
        self.assertIn("location = / {", nginx)
        self.assertIn("location /api/ {", nginx)
        self.assertIn('proxy_set_header X-Internal-Identity "";', nginx)

    def test_layout_has_explicit_desktop_tablet_and_mobile_contracts(self):
        self.assertIn("grid-template-columns: minmax(0, 1.7fr)", self.css)
        self.assertIn("@media (max-width: 60rem)", self.css)
        self.assertIn("@media (max-width: 40rem)", self.css)
        self.assertIn("grid-template-columns: 1fr", self.css)

    def test_mobile_controls_and_content_resist_clipping(self):
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("width: 100%", self.css)
        self.assertIn('name="viewport"', self.html)

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
        self.assertNotIn('return String(productId || "").replace(/-/g, " ");', self.script)
        self.assertNotIn("gift card", self.html.lower())
        self.assertNotIn("gift_card", self.script.lower())

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
        self.assertIn("data-short", self.html)
        self.assertIn("data-requires-unlock", self.html)
        self.assertIn("Complete earlier steps to unlock", self.script)
        # Product selection suggests Customize (4), not Delivery (5).
        self.assertIn("if (f.selection && f.selection.product_id) return 4;", self.script)

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
        self.assertIn('code === "csrf_rejected" || code === "session_required"', florist)

    def test_florist_operator_console_is_separate_labeled_sample(self):
        html = (ROOT / "ui" / "florist.html").read_text(encoding="utf-8")
        script = (ROOT / "ui" / "assets" / "florist.js").read_text(encoding="utf-8")
        nginx = (ROOT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("Local florist operator sample", html)
        self.assertIn("Not live chat", html)
        self.assertIn("FR-016", html)
        self.assertIn('id="inbox"', html)
        self.assertIn("/api/v1/operator/escalations", script)
        self.assertIn("/api/v1/operator/sessions/", script)
        self.assertIn("/api/v1/operator/forecasts", script)
        self.assertIn('id="support-answers"', html)
        self.assertIn("What Lily already answered", html)
        self.assertIn("support_answers", script)
        self.assertIn('id="forecast"', html)
        self.assertIn("FR-012", html)
        self.assertNotIn("card_number", script)
        self.assertNotIn("postgres", script.lower())
        self.assertIn("location = /florist {", nginx)
        self.assertIn("try_files /florist.html =404;", nginx)
        self.assertIn("location /api/ {", nginx)
        self.assertIn('proxy_set_header X-Internal-Identity "";', nginx)

    def test_t01_thought_completion_chips_come_from_api(self):
        self.assertIn('id="suggestions"', self.html)
        self.assertIn('aria-label="Optional thought-completion suggestions"', self.html)
        self.assertNotIn('class="chip"', self.html)
        self.assertNotIn("Birthday flowers for Mum, under €75", self.html)
        self.assertNotIn(">Birthday</button>", self.html)
        self.assertNotIn(">Wedding</button>", self.html)
        self.assertNotIn(">Sympathy</button>", self.html)
        self.assertIn("function renderSuggestions", self.script)
        self.assertIn("renderSuggestions(shared.suggestions)", self.script)
        self.assertIn("chip.dataset.suggest = text", self.script)
        self.assertIn("chip.textContent = text", self.script)
        self.assertIn('#suggestions").addEventListener("click"', self.script)
        self.assertNotIn('querySelectorAll("[data-suggest]")', self.script)
        self.assertIn('placeholder="For example: Birthday roses for Mum, under €75"', self.html)


if __name__ == "__main__":
    unittest.main()
