import asyncio
import json
import pathlib
import unittest

from edge.bff.aea_bff.app import BffApp
from edge.bff.aea_bff.ports import (CheckoutResult, CommandResult, ConversationResult,
                                    CorrectionResult, DeliveryResult, EscalationResult,
                                    OrderResult, SelectionResult, SupportResult)
from edge.bff.aea_bff.security import FixedWindowRateLimiter, StaticTokenAuthenticator


class FakeOrchestration:
    def __init__(self):
        self.messages = []
        self.intent = {"occasion": "birthday", "secret": "omit"}
        self.known_sessions = {}

    def ensure_session(self, **kwargs):
        self.session = kwargs
        self.known_sessions[kwargs["session_id"]] = kwargs

    def load_session(self, **kwargs):
        found = self.known_sessions.get(kwargs["session_id"])
        if found is None:
            return {"status": 404, "code": "session_not_found"}
        payload = {"status": 200, "session_id": kwargs["session_id"]}
        if found.get("recall_id"):
            payload["recall_id"] = found["recall_id"]
        return payload

    def accept_command(self, **kwargs):
        return CommandResult(True, "accepted")

    def select_product(self, **kwargs):
        self.selected = {"product_id": kwargs["product_id"], "options": kwargs["options"]}
        return SelectionResult(True, "accepted", kwargs["observed_context_version"] + 1, "selection-1")

    def update_delivery(self, **kwargs):
        self.delivery = kwargs["delivery"]
        return DeliveryResult(True, "accepted", kwargs["observed_context_version"] + 1, "delivery-1")

    def create_order(self, **kwargs):
        self.created_order = kwargs
        return OrderResult(True, "accepted", "order-9", "created")

    def checkout(self, **kwargs):
        if kwargs["payment_reference"].startswith("decline"):
            return CheckoutResult(True, "accepted", "order-9", "submitted", "declined")
        return CheckoutResult(True, "accepted", "order-9", "confirmed")

    def ask_support(self, **kwargs):
        return SupportResult(True, "answered", "We deliver same day before 2 PM.",
                             ("policy:delivery",), True)

    def request_escalation(self, **kwargs):
        self.escalation = kwargs
        return EscalationResult(True, "escalation_recorded", "esc-1",
                                "A florist has received your request.",
                                kwargs["reason"])

    def list_operator_forecasts(self, **kwargs):
        return {"status": 200, "items": [{
            "product_id": "classic-rose-dozen",
            "trend": "declining",
            "recommendation": "Plan a replenishment.",
            "fact_references": ["inventory:classic-rose-dozen:v1"],
            "secret": "omit",
            "email": "private@example.invalid",
        }]}

    def list_operator_escalations(self, **kwargs):
        return {"status": 200, "items": [{
            "message_id": "esc-1",
            "session_id": "11111111-1111-4111-8111-111111111111",
            "escalation_reason": "unresolved_request",
            "context_reference": "11111111-1111-4111-8111-111111111111",
            "requested_at": "2026-08-15T00:00:00+00:00",
            "secret": "omit",
            "email": "private@example.invalid",
        }]}

    def list_operator_orders(self, **kwargs):
        return {"status": 200, "items": [{
            "order_id": "order-9",
            "session_id": "11111111-1111-4111-8111-111111111111",
            "status": "confirmed",
            "delayed": False,
            "authoritative_status": "confirmed",
            "product_id": "classic-rose-dozen",
            "destination_reference": "dest-1",
            "timing": {"date": "2026-08-16", "window": "morning"},
            "card_message": "Happy birthday Mum",
            "catalog_title": "Classic Rose Dozen",
            "channel": "web",
            "payment_state": "paid",
            "updated_at": "2026-09-02T12:00:00+00:00",
            "secret": "omit",
            "email": "private@example.invalid",
            "decline_code": "omit",
        }]}

    def operator_session_summary(self, **kwargs):
        if kwargs["session_id"] == "00000000-0000-0000-0000-000000000000":
            return {"status": 404, "code": "session_not_found"}
        return {
            "status": 200,
            "session_id": kwargs["session_id"],
            "context_version": 3,
            "conversation": {"messages": [{
                "message_id": "m1", "role": "customer", "text": "roses for mum",
                "status": "submitted", "submitted_at": "2026-08-15T00:00:00+00:00",
                "private": "omit"}]},
            "shared_understanding": {
                "structured_intent": {"occasion": "birthday", "secret": "omit"}},
            "order": {"order_id": "order-9", "status": "preparing",
                      "delayed": False, "authoritative_status": "preparing"},
            "selection": {"product_id": "classic-rose-dozen",
                          "options": {"card_message": "Happy birthday Mum"}},
            "delivery": {"destination_reference": "dest-1",
                         "timing": {"date": "2026-08-16", "window": "morning"}},
            "availability": [{"product_id": "classic-rose-dozen",
                              "availability_status": "available", "available": True,
                              "secret": "omit"}],
            "support_answers": [{
                "message_id": "faq-1",
                "kind": "faq",
                "answer": "Standard orders placed before 2 PM are delivered the same day.",
                "approved_source_references": ["policy:delivery"],
                "answered_at": "2026-08-15T00:01:00+00:00",
                "secret": "omit",
                "email": "private@example.invalid",
            }],
            "email": "omit@example.invalid",
        }

    def workspace_projection(self, **kwargs):
        return {"context_version": 7, "secret": "omit",
                "facets": {
                    "conversation": {"messages": [{
                        "message_id": "m1", "role": "customer", "text": "hi",
                        "status": "submitted", "submitted_at": "2026-08-12T00:00:00+00:00",
                        "private": "omit"}]},
                    "shared_understanding": {
                        "structured_intent": {"occasion": "birthday", "secret": "omit"},
                        "suggestions": ["What budget?"]},
                    "recommendations": {"items": [{
                        "product_id": "classic-rose-dozen", "price": 70.0, "score": 4.0,
                        "rank": 1, "available": True, "availability_status": "available",
                        "secret": "omit"}]},
                    "selection": {"product_id": "classic-rose-dozen",
                                  "options": {"card_message": "hi"}, "secret": "omit"}},
                "ai_generated": True, "assistant_mode": "primary",
                "disclosure": "AI-generated; review it."}

    def stream_events(self, **kwargs):
        after = kwargs.get("after_event_id")
        if after == "2":
            return []
        return [{"event_id": "2", "context_version": 2, "kind": "invalidation",
                 "invalidated_projections": [{
                     "projection_key": "recommendations", "reason": "intent_changed",
                     "secret": "omit"}]}]

    def submit_conversation_message(self, **kwargs):
        self.messages.append({
            "message_id": "message-1", "role": "customer",
            "text": kwargs["message_text"].strip(), "status": "submitted",
            "submitted_at": "2026-08-12T00:00:00+00:00", "private": "omit",
        })
        return ConversationResult(True, "accepted", kwargs["observed_context_version"] + 1,
                                  "message-1", True, "primary", "AI-generated; review it.")

    def conversation_projection(self, **kwargs):
        return {"context_version": len(self.messages), "messages": self.messages, "secret": "omit"}

    def shared_understanding_projection(self, **kwargs):
        return {"context_version": 1, "structured_intent": self.intent,
                "suggestions": ["What budget?"], "secret": "omit",
                "ai_generated": True, "assistant_mode": "primary",
                "disclosure": "AI-generated; review it."}

    def correct_shared_understanding(self, **kwargs):
        self.intent.update(kwargs["corrections"])
        return CorrectionResult(True, "accepted", kwargs["observed_context_version"] + 1,
                                "correction-1")


async def invoke(app, method, path, headers=None, body=b"", query=b""):
    sent = []
    messages = [{"type": "http.request", "body": body, "more_body": False}]
    async def receive(): return messages.pop(0)
    async def send(message): sent.append(message)
    raw_headers = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    await app({"type": "http", "method": method, "path": path, "query_string": query, "headers": raw_headers}, receive, send)
    start, response = sent
    header_map = {}
    cookies = []
    for key, value in start["headers"]:
        name, text = key.decode(), value.decode()
        if name == "set-cookie":
            cookies.append(text)
        header_map[name] = text
    if cookies:
        session_cookie = next((item for item in cookies if item.startswith("__Host-aea_session=")),
                              cookies[-1])
        header_map["set-cookie"] = session_cookie
        header_map["set-cookie-all"] = "\n".join(cookies)
    return start["status"], header_map, response["body"]


class PerimeterTests(unittest.TestCase):
    def setUp(self):
        self.app = BffApp(FakeOrchestration(), StaticTokenAuthenticator("good"), allowed_origin="https://localhost:8443")
        self.auth = {"authorization": "Bearer good", "origin": "https://localhost:8443"}

    def call(self, *args, **kwargs): return asyncio.run(invoke(self.app, *args, **kwargs))

    def session(self):
        status, headers, body = self.call("POST", "/api/v1/session", self.auth)
        self.assertEqual(201, status)
        return headers["set-cookie"].split(";", 1)[0], json.loads(body)["csrf_token"]

    def test_auth_cookie_csrf_and_headers(self):
        self.assertEqual(401, self.call("POST", "/api/v1/session")[0])
        cookie, csrf = self.session()
        self.assertIn("Secure; HttpOnly; SameSite=Lax", self.call("POST", "/api/v1/session", self.auth)[1]["set-cookie"])
        status, headers, _ = self.call("POST", "/api/v1/commands", {**self.auth, "cookie": cookie}, b"{}")
        self.assertEqual(403, status)
        self.assertEqual("DENY", headers["x-frame-options"])

    def test_session_post_reuses_valid_cookie_and_csrf(self):
        cookie, csrf = self.session()
        status, headers, body = self.call("POST", "/api/v1/session", {**self.auth, "cookie": cookie})
        self.assertEqual(201, status)
        self.assertEqual(csrf, json.loads(body)["csrf_token"])
        self.assertEqual(cookie, headers["set-cookie"].split(";", 1)[0])
        # A second boot (/florist or another tab) must not invalidate the first tab.
        mutating = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                    "content-type": "application/json"}
        self.assertEqual(202, self.call(
            "POST", "/api/v1/conversation/messages", mutating,
            json.dumps({"message_text": "hi", "observed_context_version": 0}).encode())[0])
        self.assertEqual(202, self.call(
            "POST", "/api/v1/delivery", mutating,
            json.dumps({"delivery": {"destination_reference": "addr-ref",
                                     "timing": {"date": "2026-09-01", "window": "morning"}},
                        "observed_context_version": 0}).encode())[0])

    def test_session_mints_and_reuses_durable_recall_cookie(self):
        status, headers, _ = self.call("POST", "/api/v1/session", self.auth)
        self.assertEqual(201, status)
        cookies = headers["set-cookie-all"].split("\n")
        recall = next(item for item in cookies if item.startswith("__Host-aea_recall="))
        session = next(item for item in cookies if item.startswith("__Host-aea_session="))
        self.assertIn("Max-Age=2592000", recall)
        self.assertIn("Secure; HttpOnly; SameSite=Lax", recall)
        self.assertNotIn("Max-Age", session)
        recall_pair = recall.split(";", 1)[0]
        session_pair = session.split(";", 1)[0]
        recall_id = recall_pair.split("=", 1)[1]
        self.assertEqual(recall_id, self.app.orchestration.session["recall_id"])
        self.assertEqual(session_pair.split("=", 1)[1],
                         self.app.orchestration.session["session_id"])

        reused = self.call("POST", "/api/v1/session", {
            **self.auth, "cookie": f"{session_pair}; {recall_pair}"})[1]
        reused_recall = next(item for item in reused["set-cookie-all"].split("\n")
                             if item.startswith("__Host-aea_recall="))
        self.assertEqual(recall_id, reused_recall.split(";", 1)[0].split("=", 1)[1])
        self.assertEqual(session_pair.split("=", 1)[1],
                         self.app.orchestration.session["session_id"])

        minted = self.call("POST", "/api/v1/session", {
            **self.auth, "cookie": "__Host-aea_recall=not-a-uuid"})[1]
        minted_recall = next(item for item in minted["set-cookie-all"].split("\n")
                             if item.startswith("__Host-aea_recall="))
        minted_id = minted_recall.split(";", 1)[0].split("=", 1)[1]
        self.assertNotEqual("not-a-uuid", minted_id)
        self.assertEqual(minted_id, self.app.orchestration.session["recall_id"])

    def test_correction_rebinds_cookie_to_orchestration_after_bff_memory_loss(self):
        orchestration = FakeOrchestration()
        auth = StaticTokenAuthenticator("good")
        origin = "https://localhost:8443"
        app_a = BffApp(orchestration, auth, allowed_origin=origin)
        status, headers, body = asyncio.run(invoke(app_a, "POST", "/api/v1/session", self.auth))
        self.assertEqual(201, status)
        cookie = headers["set-cookie"].split(";", 1)[0]
        csrf = json.loads(body)["csrf_token"]
        self.assertNotIn("Max-Age", headers["set-cookie"])
        mutating = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                    "content-type": "application/json"}
        self.assertEqual(202, asyncio.run(invoke(
            app_a, "POST", "/api/v1/conversation/messages", mutating,
            json.dumps({"message_text": "hi", "observed_context_version": 0}).encode()))[0])

        app_b = BffApp(orchestration, auth, allowed_origin=origin)
        self.assertIsNone(app_b.sessions.get(cookie.split("=", 1)[1]))
        status, _, body = asyncio.run(invoke(
            app_b, "PATCH", "/api/v1/shared-understanding", mutating,
            json.dumps({"corrections": {"recipient": "Mum"},
                        "observed_context_version": 1}).encode()))
        self.assertEqual(202, status)
        self.assertTrue(json.loads(body)["accepted"])
        reused = asyncio.run(invoke(app_b, "POST", "/api/v1/session",
                                    {**self.auth, "cookie": cookie}))
        self.assertEqual(201, reused[0])
        self.assertEqual(csrf, json.loads(reused[2])["csrf_token"])
        self.assertEqual(cookie, reused[1]["set-cookie"].split(";", 1)[0])

    def test_command_contract_and_least_data_projection(self):
        cookie, csrf = self.session()
        headers = {**self.auth, "cookie": cookie, "x-csrf-token": csrf, "content-type": "application/json"}
        status, _, body = self.call("POST", "/api/v1/commands", headers, json.dumps({"command": {"type": "continue"}, "observed_context_version": 7}).encode())
        payload = json.loads(body)
        self.assertEqual(202, status)
        self.assertEqual(7, payload["observed_context_version"])
        self.assertRegex(payload["correlation_id"], r"^[0-9a-f-]{36}$")
        status, _, body = self.call("GET", "/api/v1/workspace", {**self.auth, "cookie": cookie})
        self.assertEqual({
            "context_version": 7,
            "facets": {
                "conversation": {"messages": [{
                    "message_id": "m1", "role": "customer", "text": "hi",
                    "status": "submitted", "submitted_at": "2026-08-12T00:00:00+00:00"}]},
                "shared_understanding": {
                    "structured_intent": {"occasion": "birthday"},
                    "suggestions": ["What budget?"]},
                "recommendations": {"items": [{
                    "product_id": "classic-rose-dozen", "price": 70.0, "score": 4.0,
                    "rank": 1, "available": True, "availability_status": "available"}]},
                "selection": {"product_id": "classic-rose-dozen",
                              "options": {"card_message": "hi"}}},
            "ai_generated": True, "assistant_mode": "primary",
            "disclosure": "AI-generated; review it.",
        }, json.loads(body))
        self.assertNotIn(b"secret", body)
        self.assertNotIn(b"private", body)

    def test_selection_requires_csrf_and_is_versioned(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"product_id": "classic-rose-dozen",
                              "options": {"card_message": "hi"},
                              "observed_context_version": 7}).encode()
        # CSRF is enforced on the selection write.
        self.assertEqual(403, self.call("POST", "/api/v1/selection", json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/selection", headers, payload)
        self.assertEqual(202, status)
        result = json.loads(body)
        self.assertTrue(result["accepted"])
        self.assertEqual("selection-1", result["message_id"])
        self.assertEqual(8, result["context_version"])
        # Invalid shapes are rejected before reaching Orchestration.
        self.assertEqual(422, self.call("POST", "/api/v1/selection", headers,
            json.dumps({"product_id": "", "observed_context_version": 7}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/selection", headers,
            json.dumps({"product_id": "x", "observed_context_version": -1}).encode())[0])
        # T-04 options (ADR-006 amended): size + card message + thin FR-003 keys + quantity.
        self.assertEqual(202, self.call("POST", "/api/v1/selection", headers,
            json.dumps({"product_id": "classic-rose-dozen",
                        "options": {"size": "large", "card_message": "hi",
                                    "flower_type": "roses", "colour": "red",
                                    "ribbon": "satin", "quantity": 10},
                        "observed_context_version": 7}).encode())[0])
        # Gift-card value and unknown keys remain rejected at the edge.
        for control in ({"gift_card_value": "50"}, {"composition": "free-form"}):
            self.assertEqual(422, self.call("POST", "/api/v1/selection", headers,
                json.dumps({"product_id": "classic-rose-dozen", "options": control,
                            "observed_context_version": 7}).encode())[0])

    def test_delivery_requires_csrf_and_rejects_raw_pii(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"delivery": {"destination_reference": "addr-ref",
                                           "timing": {"date": "2026-09-01", "window": "morning"}},
                              "observed_context_version": 0}).encode()
        self.assertEqual(403, self.call("POST", "/api/v1/delivery", json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/delivery", headers, payload)
        self.assertEqual(202, status)
        self.assertEqual("delivery-1", json.loads(body)["message_id"])
        # Reference-only: raw recipient PII and a missing timing are rejected at the edge.
        for bad in ({"recipient_name": "Jane", "destination_reference": "r",
                     "timing": {"date": "2026-09-01", "window": "morning"}},
                    {"destination_reference": "r"}):
            self.assertEqual(422, self.call("POST", "/api/v1/delivery", headers,
                json.dumps({"delivery": bad, "observed_context_version": 0}).encode())[0])

    def test_workspace_delivery_facet_is_least_data(self):
        shaped = BffApp._least_data_workspace({"context_version": 3, "facets": {"delivery": {
            "destination_reference": "addr-ref", "secret": "omit",
            "timing": {"date": "2026-09-01", "window": "morning", "secret": "omit"}}}})
        self.assertEqual({"destination_reference": "addr-ref",
                          "timing": {"date": "2026-09-01", "window": "morning"}},
                         shaped["facets"]["delivery"])

    def test_order_creation_requires_csrf(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        self.assertEqual(403, self.call("POST", "/api/v1/order", json_headers, b"{}")[0])
        headers = {**json_headers, "x-csrf-token": csrf, "x-aea-client": "web"}
        status, _, body = self.call("POST", "/api/v1/order", headers, b"{}")
        self.assertEqual(202, status)
        payload = json.loads(body)
        self.assertEqual("order-9", payload["order_id"])
        self.assertEqual("created", payload["status"])
        self.assertEqual("web", self.app.orchestration.created_order["aea_client"])

    def test_workspace_order_facet_is_least_data(self):
        shaped = BffApp._least_data_workspace({"context_version": 4, "facets": {"order": {
            "order_id": "o1", "status": "created", "secret": "omit"}}})
        self.assertEqual({"order_id": "o1", "status": "created"}, shaped["facets"]["order"])

    def test_workspace_order_facet_carries_delay_and_authoritative_status(self):
        shaped = BffApp._least_data_workspace({"context_version": 6, "facets": {"order": {
            "order_id": "o1", "status": "dispatched", "delayed": True,
            "authoritative_status": "delayed", "secret": "omit"}}})
        self.assertEqual({"order_id": "o1", "status": "dispatched",
                          "authoritative_status": "delayed", "delayed": True},
                         shaped["facets"]["order"])

    def test_support_requires_csrf_and_returns_grounded_answer(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"question": "When do you deliver?"}).encode()
        self.assertEqual(403, self.call("POST", "/api/v1/support", json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/support", headers, payload)
        self.assertEqual(200, status)
        answer = json.loads(body)
        self.assertTrue(answer["answered"])
        self.assertIn("policy:delivery", answer["approved_source_references"])
        # Empty or extra fields are rejected.
        self.assertEqual(422, self.call("POST", "/api/v1/support", headers,
            json.dumps({"question": "", "extra": 1}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/support", headers,
            json.dumps({"question": "  "}).encode())[0])

    def test_escalation_requires_csrf_and_rejects_pii_fields(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"reason": "unresolved_request"}).encode()
        self.assertEqual(403, self.call("POST", "/api/v1/support/escalation",
                                        json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/support/escalation", headers, payload)
        self.assertEqual(202, status)
        accepted = json.loads(body)
        self.assertTrue(accepted["accepted"])
        self.assertEqual("escalation_recorded", accepted["code"])
        self.assertEqual("unresolved_request", accepted["escalation_reason"])
        self.assertIn("florist", accepted["acknowledgement"].lower())
        self.assertEqual(422, self.call("POST", "/api/v1/support/escalation", headers,
            json.dumps({"reason": "call_me"}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/support/escalation", headers,
            json.dumps({"reason": "unresolved_request",
                        "email": "private@example.invalid"}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/support/escalation", headers,
            json.dumps({"reason": "unresolved_request",
                        "address": "1 Main St"}).encode())[0])

    def test_checkout_requires_csrf_and_rejects_raw_card_fields(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"payment_reference": "tok_1", "observed_total": 82.0}).encode()
        self.assertEqual(403, self.call("POST", "/api/v1/checkout", json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/checkout", headers, payload)
        self.assertEqual(202, status)
        accepted = json.loads(body)
        self.assertTrue(accepted["accepted"])
        self.assertTrue(accepted["pending"])
        self.assertTrue(accepted["confirmed"])
        # Decline still returns 202 accepted-pending; decline_code is observational.
        declined = self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "decline-1", "observed_total": 82.0}).encode())
        self.assertEqual(202, declined[0])
        declined_body = json.loads(declined[2])
        self.assertTrue(declined_body["accepted"])
        self.assertEqual("declined", declined_body["decline_code"])
        self.assertEqual("submitted", declined_body["status"])
        self.assertFalse(declined_body["confirmed"])
        # Raw card fields and a missing total are rejected at the edge.
        self.assertEqual(422, self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "tok", "observed_total": 82.0,
                        "card_number": "4111111111111111"}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "tok"}).encode())[0])

    def test_workspace_order_summary_facet_is_least_data(self):
        # quantity and unit_price are forwarded so the T-06 summary can show the
        # quantity multiplier (e.g. "product (2x)"); unknown fields stay stripped.
        shaped = BffApp._least_data_workspace({"context_version": 5, "facets": {"order_summary": {
            "currency": "USD", "total": 82.0, "secret": "omit",
            "itemized_charges": [
                {"label": "product", "product_id": "budget-mixed-bunch", "quantity": 2,
                 "unit_price": 35.0, "amount": 70.0, "secret": "omit"},
                {"label": "delivery", "amount": 12.0}]}}})
        self.assertEqual({
            "itemized_charges": [
                {"label": "product", "product_id": "budget-mixed-bunch", "quantity": 2,
                 "unit_price": 35.0, "amount": 70.0},
                {"label": "delivery", "amount": 12.0}],
            "total": 82.0, "currency": "USD"}, shaped["facets"]["order_summary"])

    def test_stream_reconnect(self):
        cookie, _ = self.session()
        headers = {**self.auth, "cookie": cookie}
        first = self.call("GET", "/api/v1/stream", headers)[2]
        self.assertIn(b"id: 2", first)
        self.assertIn(b"recommendations", first)
        self.assertNotIn(b"secret", first)
        self.assertEqual(b"", self.call("GET", "/api/v1/stream", {**headers, "last-event-id": "2"})[2])

    def test_conversation_message_acceptance_and_projection(self):
        cookie, csrf = self.session()
        headers = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                   "content-type": "application/json"}
        status, _, body = self.call(
            "POST", "/api/v1/conversation/messages", headers,
            json.dumps({"message_text": "  flowers for Mum  ",
                        "observed_context_version": 0}).encode(),
        )
        result = json.loads(body)
        self.assertEqual(202, status)
        self.assertEqual("message-1", result["message_id"])
        self.assertEqual(1, result["context_version"])
        self.assertTrue(result["ai_generated"])
        self.assertIn("AI-generated", result["disclosure"])
        status, _, body = self.call("GET", "/api/v1/conversation",
                                    {**self.auth, "cookie": cookie})
        self.assertEqual(200, status)
        projection = json.loads(body)
        self.assertEqual("flowers for Mum", projection["messages"][0]["text"])
        self.assertNotIn("private", projection["messages"][0])

    def test_conversation_rejects_empty_oversized_and_extra_fields(self):
        cookie, csrf = self.session()
        headers = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                   "content-type": "application/json"}
        for payload in (
            {"message_text": " ", "observed_context_version": 0},
            {"message_text": "x" * 2001, "observed_context_version": 0},
            {"message_text": "roses", "observed_context_version": 0, "extra": True},
        ):
            self.assertEqual(422, self.call(
                "POST", "/api/v1/conversation/messages", headers,
                json.dumps(payload).encode(),
            )[0])

    def test_origin_size_rate_and_shape_controls(self):
        self.assertEqual(403, self.call("POST", "/api/v1/session", {"authorization": "Bearer good", "origin": "https://evil.invalid"})[0])
        cookie, csrf = self.session()
        missing_type = {**self.auth, "cookie": cookie, "x-csrf-token": csrf}
        self.assertEqual(415, self.call("POST", "/api/v1/commands", missing_type, b"{}")[0])
        headers = {**missing_type, "content-type": "application/json", "content-length": "70000"}
        self.assertEqual(413, self.call("POST", "/api/v1/commands", headers)[0])
        self.app.rate_limiter = FixedWindowRateLimiter(limit=1)
        self.assertEqual(200, self.call("GET", "/healthz")[0])
        self.assertEqual(200, self.call("GET", "/healthz")[0])
        self.assertEqual(200, self.call("GET", "/api/v1/workspace", {**self.auth, "cookie": cookie})[0])
        self.assertEqual(429, self.call("GET", "/api/v1/workspace", {**self.auth, "cookie": cookie})[0])

    def test_workspace_keeps_prior_order_hint_and_drops_secrets(self):
        shaped = BffApp._least_data_workspace({
            "context_version": 2,
            "facets": {"recommendations": {"items": [{
                "product_id": "lilac-bouquet", "price": 95.0, "score": 5.5,
                "rank": 1, "available": True, "availability_status": "available",
                "prior_order_hint": True, "secret": "omit"}]}},
            "ai_generated": False, "assistant_mode": "reference",
            "disclosure": "Automated interpretation; review and correct before ordering."})
        item = shaped["facets"]["recommendations"]["items"][0]
        self.assertTrue(item["prior_order_hint"])
        self.assertEqual("lilac-bouquet", item["product_id"])
        self.assertNotIn("secret", item)

    def test_workspace_passes_through_fallback_disclosure_without_claiming_ai(self):
        shaped = BffApp._least_data_workspace({
            "context_version": 1, "facets": {},
            "ai_generated": False, "assistant_mode": "fallback",
            "disclosure": "Automated interpretation; review and correct before ordering."})
        self.assertFalse(shaped["ai_generated"])
        self.assertEqual("fallback", shaped["assistant_mode"])
        self.assertNotIn("AI-generated", shaped["disclosure"])

    def test_shared_understanding_review_and_correction_are_least_data(self):
        cookie, csrf = self.session()
        status, _, body = self.call("GET", "/api/v1/shared-understanding",
                                    {**self.auth, "cookie": cookie})
        self.assertEqual(200, status)
        self.assertEqual({"occasion": "birthday"},
                         json.loads(body)["structured_intent"])
        self.assertTrue(json.loads(body)["ai_generated"])
        self.assertIn("AI-generated", json.loads(body)["disclosure"])
        headers = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                   "content-type": "application/json", "x-correlation-id":
                   "00000000-0000-0000-0000-000000000034"}
        status, response_headers, body = self.call(
            "PATCH", "/api/v1/shared-understanding", headers,
            json.dumps({"corrections": {"budget": 75},
                        "observed_context_version": 1}).encode())
        self.assertEqual(202, status)
        result = json.loads(body)
        self.assertEqual(2, result["context_version"])
        self.assertEqual(result["correlation_id"], response_headers["x-correlation-id"])

    def test_shared_understanding_correction_retries_stale_context(self):
        class StaleThenCurrent(FakeOrchestration):
            def __init__(self):
                super().__init__()
                self.correct_versions = []
                self.current_version = 4

            def shared_understanding_projection(self, **kwargs):
                data = super().shared_understanding_projection(**kwargs)
                data["context_version"] = self.current_version
                return data

            def correct_shared_understanding(self, **kwargs):
                observed = kwargs["observed_context_version"]
                self.correct_versions.append(observed)
                if observed < self.current_version:
                    return CorrectionResult(False, "stale_context", self.current_version)
                return super().correct_shared_understanding(**kwargs)

        orchestration = StaleThenCurrent()
        app = BffApp(orchestration, StaticTokenAuthenticator("good"),
                     allowed_origin="https://localhost:8443")
        def call(*args, **kwargs):
            return asyncio.run(invoke(app, *args, **kwargs))
        status, headers, body = call("POST", "/api/v1/session", self.auth)
        self.assertEqual(201, status)
        cookie = headers["set-cookie"].split(";", 1)[0]
        csrf = json.loads(body)["csrf_token"]
        headers = {**self.auth, "cookie": cookie, "x-csrf-token": csrf,
                   "content-type": "application/json"}
        status, _, body = call(
            "PATCH", "/api/v1/shared-understanding", headers,
            json.dumps({"corrections": {"recipient": "Mum"},
                        "observed_context_version": 1}).encode())
        self.assertEqual(202, status)
        result = json.loads(body)
        self.assertTrue(result["accepted"])
        self.assertEqual("accepted", result["code"])
        self.assertEqual(5, result["context_version"])
        self.assertEqual([1, 4], orchestration.correct_versions)

    def test_florist_operator_reads_fail_closed_unless_enabled(self):
        cookie, _csrf = self.session()
        headers = {**self.auth, "cookie": cookie}
        self.assertEqual(404, self.call("GET", "/api/v1/operator/escalations", headers)[0])
        self.assertEqual(404, self.call("GET", "/api/v1/operator/orders", headers)[0])
        self.assertEqual(404, self.call("GET", "/api/v1/operator/forecasts", headers)[0])
        self.assertEqual(404, self.call(
            "GET", "/api/v1/operator/sessions/11111111-1111-4111-8111-111111111111",
            headers)[0])
        self.assertTrue(BffApp.florist_operator_enabled_for(environment="local", flag="1"))
        self.assertFalse(BffApp.florist_operator_enabled_for(environment="production", flag="1"))
        self.assertFalse(BffApp.florist_operator_enabled_for(environment="local", flag=None))
        self.assertTrue(BffApp.florist_operator_enabled_for(
            environment="production", flag="1", exception="aea-pilot"))
        self.assertFalse(BffApp.florist_operator_enabled_for(
            environment="production", flag="1", exception="1"))
        self.assertFalse(BffApp.florist_operator_enabled_for(
            environment="production", flag="1", exception="production"))
        self.assertFalse(BffApp.florist_operator_enabled_for(
            environment="production", flag=None, exception="aea-pilot"))

    def test_florist_operator_inbox_and_session_are_least_data_when_enabled(self):
        app = BffApp(FakeOrchestration(), StaticTokenAuthenticator("good"),
                     allowed_origin="https://localhost:8443", florist_operator_enabled=True)
        def call(*args, **kwargs):
            return asyncio.run(invoke(app, *args, **kwargs))
        status, headers, body = call("POST", "/api/v1/session", self.auth)
        self.assertEqual(201, status)
        cookie = headers["set-cookie"].split(";", 1)[0]
        auth = {**self.auth, "cookie": cookie}
        status, _, body = call("GET", "/api/v1/operator/escalations", auth)
        self.assertEqual(200, status)
        inbox = json.loads(body)
        self.assertEqual([{
            "message_id": "esc-1",
            "session_id": "11111111-1111-4111-8111-111111111111",
            "escalation_reason": "unresolved_request",
            "context_reference": "11111111-1111-4111-8111-111111111111",
            "requested_at": "2026-08-15T00:00:00+00:00",
        }], inbox["items"])
        self.assertNotIn(b"secret", body)
        self.assertNotIn(b"email", body)
        status, _, body = call("GET", "/api/v1/operator/orders", auth)
        self.assertEqual(200, status)
        orders = json.loads(body)
        self.assertEqual("order-9", orders["items"][0]["order_id"])
        self.assertEqual("classic-rose-dozen", orders["items"][0]["product_id"])
        self.assertEqual({"date": "2026-08-16", "window": "morning"},
                         orders["items"][0]["timing"])
        self.assertEqual("Happy birthday Mum", orders["items"][0]["card_message"])
        self.assertEqual("Classic Rose Dozen", orders["items"][0]["catalog_title"])
        self.assertEqual("web", orders["items"][0]["channel"])
        self.assertEqual("paid", orders["items"][0]["payment_state"])
        self.assertNotIn("secret", orders["items"][0])
        self.assertNotIn("email", orders["items"][0])
        self.assertNotIn("decline_code", orders["items"][0])
        self.assertNotIn(b"secret", body)
        self.assertNotIn(b"email", body)
        status, _, body = call("GET", "/api/v1/operator/forecasts", auth)
        self.assertEqual(200, status)
        forecasts = json.loads(body)
        self.assertEqual("declining", forecasts["items"][0]["trend"])
        self.assertNotIn("secret", forecasts["items"][0])
        self.assertNotIn(b"email", body)
        status, _, body = call(
            "GET", "/api/v1/operator/sessions/11111111-1111-4111-8111-111111111111", auth)
        self.assertEqual(200, status)
        summary = json.loads(body)
        self.assertEqual("roses for mum", summary["conversation"]["messages"][0]["text"])
        self.assertEqual({"occasion": "birthday"}, summary["shared_understanding"]["structured_intent"])
        self.assertEqual("preparing", summary["order"]["authoritative_status"])
        self.assertEqual("Happy birthday Mum", summary["selection"]["card_message"])
        self.assertEqual({"date": "2026-08-16", "window": "morning"},
                         summary["delivery"]["timing"])
        self.assertEqual("available", summary["availability"][0]["availability_status"])
        self.assertEqual("faq", summary["support_answers"][0]["kind"])
        self.assertIn("2 PM", summary["support_answers"][0]["answer"])
        self.assertNotIn("secret", summary["support_answers"][0])
        self.assertNotIn("email", summary)
        self.assertNotIn(b"private", body)
        self.assertEqual(422, call("GET", "/api/v1/operator/sessions/not-a-uuid", auth)[0])
        self.assertEqual(404, call(
            "GET", "/api/v1/operator/sessions/00000000-0000-0000-0000-000000000000",
            auth)[0])
        stripped = BffApp._least_data_operator_orders({
            "items": [{
                "order_id": "order-x",
                "session_id": "s1",
                "channel": "rog-phone",
                "payment_state": "refunded",
                "catalog_title": "x" * 200,
                "email": "private@example.invalid",
            }]
        })
        self.assertEqual("order-x", stripped["items"][0]["order_id"])
        self.assertNotIn("channel", stripped["items"][0])
        self.assertNotIn("payment_state", stripped["items"][0])
        self.assertNotIn("catalog_title", stripped["items"][0])
        self.assertNotIn("email", stripped["items"][0])

    def test_x_aea_client_is_observability_only_not_auth(self):
        """#368: allowlisted X-AEA-Client is echoed + logged; never gates auth."""
        import io
        from contextlib import redirect_stdout

        # Missing Bearer still 401 even with a valid client label.
        status, headers, _ = self.call(
            "POST", "/api/v1/session",
            {"origin": "https://localhost:8443", "x-aea-client": "companion-android"})
        self.assertEqual(401, status)

        buf = io.StringIO()
        with redirect_stdout(buf):
            status, headers, body = self.call(
                "POST", "/api/v1/session",
                {**self.auth, "x-aea-client": "companion-android"})
        self.assertEqual(201, status)
        self.assertEqual("companion-android", headers.get("x-aea-client"))
        log_line = buf.getvalue()
        self.assertIn('"event": "bff_access"', log_line)
        self.assertIn('"aea_client": "companion-android"', log_line)

        buf = io.StringIO()
        with redirect_stdout(buf):
            status, headers, _ = self.call(
                "POST", "/api/v1/session",
                {**self.auth, "x-aea-client": "web"})
        self.assertEqual(201, status)
        self.assertEqual("web", headers.get("x-aea-client"))
        self.assertIn('"aea_client": "web"', buf.getvalue())

        # Unknown values are not auth-rejected; labeled unknown for metrics.
        buf = io.StringIO()
        with redirect_stdout(buf):
            status, headers, _ = self.call(
                "POST", "/api/v1/session",
                {**self.auth, "x-aea-client": "evil-token-attempt"})
        self.assertEqual(201, status)
        self.assertEqual("unknown", headers.get("x-aea-client"))
        self.assertIn('"aea_client": "unknown"', buf.getvalue())

        gateway = (pathlib.Path(__file__).resolve().parents[1] / "gateway" / "nginx.conf").read_text(
            encoding="utf-8")
        self.assertIn("aea_client=\"$http_x_aea_client\"", gateway)
        self.assertIn("proxy_set_header X-AEA-Client $http_x_aea_client;", gateway)

    def test_boundary_contains_no_domain_or_infrastructure_authority(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        sources = "\n".join(p.read_text(encoding="utf-8") for p in (root / "bff").rglob("*.py"))
        for forbidden in ("psycopg", "confluent_kafka", "context_version +=", "validate_domain"):
            self.assertNotIn(forbidden, sources)
        compose = (root / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn('"8080:8080"', compose)
        self.assertNotIn("AEA_AI_ENDPOINT", compose)
        overlay = (root / "docker-compose.litellm.yml").read_text(encoding="utf-8")
        self.assertIn("http://litellm:4000/v1/chat/completions", overlay)
        self.assertNotIn("localhost:4000", overlay)
        self.assertNotIn('"8080:8080"', overlay)
        gateway = (root / "gateway" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("TLSv1.2 TLSv1.3", gateway)
        self.assertIn("client_max_body_size 64k", gateway)

    def test_gateway_emits_claimed_security_headers(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        gateway = (root / "gateway" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("add_header Content-Security-Policy", gateway)
        self.assertIn("frame-ancestors 'none'", gateway)
        self.assertIn("default-src 'self'", gateway)
        self.assertIn("object-src 'none'", gateway)
        self.assertIn("add_header Strict-Transport-Security", gateway)
        self.assertIn("X-Content-Type-Options nosniff", gateway)
        self.assertIn("X-Frame-Options DENY", gateway)

    def test_gateway_alb_mode_listens_http_for_alb_targets(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        alb = (root / "gateway" / "nginx-alb.conf").read_text(encoding="utf-8")
        dockerfile = (root / "gateway" / "Dockerfile").read_text(encoding="utf-8")
        entrypoint = (root / "gateway" / "entrypoint.sh").read_text(encoding="utf-8")
        self.assertIn("listen 8080;", alb)
        self.assertNotIn("listen 8443", alb)
        self.assertNotIn("ssl_certificate", alb)
        self.assertIn("location = /healthz", alb)
        self.assertIn("__BFF_UPSTREAM__", alb)
        self.assertIn("__AGENT_UPSTREAM__", alb)
        self.assertIn("location /webhooks/", alb)
        self.assertIn("location /cloud/", alb)
        self.assertIn("location /grafana/", alb)
        self.assertIn("__GRAFANA_UPSTREAM__", alb)
        self.assertIn("port_in_redirect off", alb)
        self.assertNotIn("<<<<<<<", alb)
        self.assertNotIn(">>>>>>>", alb)
        self.assertIn("proxy_set_header X-Internal-Identity \"\";", alb)
        self.assertIn("add_header Content-Security-Policy", alb)
        self.assertIn("frame-ancestors 'none'", alb)
        self.assertIn("COPY nginx-alb.conf", dockerfile)
        self.assertIn('AEA_GATEWAY_MODE:-}" = "alb"', entrypoint)
        self.assertIn("AEA_AGENT_UPSTREAM", entrypoint)
        self.assertIn("__AGENT_UPSTREAM__", entrypoint)
        self.assertIn("openssl req", entrypoint)


if __name__ == "__main__":
    unittest.main()
