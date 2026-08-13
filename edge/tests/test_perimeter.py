import asyncio
import json
import pathlib
import unittest

from edge.bff.aea_bff.app import BffApp
from edge.bff.aea_bff.ports import (CheckoutResult, CommandResult, ConversationResult,
                                    CorrectionResult, DeliveryResult, OrderResult, SelectionResult)
from edge.bff.aea_bff.security import FixedWindowRateLimiter, StaticTokenAuthenticator


class FakeOrchestration:
    def __init__(self):
        self.messages = []
        self.intent = {"occasion": "birthday", "secret": "omit"}

    def ensure_session(self, **kwargs):
        self.session = kwargs

    def accept_command(self, **kwargs):
        return CommandResult(True, "accepted")

    def select_product(self, **kwargs):
        self.selected = {"product_id": kwargs["product_id"], "options": kwargs["options"]}
        return SelectionResult(True, "accepted", kwargs["observed_context_version"] + 1, "selection-1")

    def update_delivery(self, **kwargs):
        self.delivery = kwargs["delivery"]
        return DeliveryResult(True, "accepted", kwargs["observed_context_version"] + 1, "delivery-1")

    def create_order(self, **kwargs):
        return OrderResult(True, "accepted", "order-9", "created")

    def checkout(self, **kwargs):
        if kwargs["payment_reference"].startswith("decline"):
            return CheckoutResult(False, "payment_declined", "order-9", "submitted", "declined")
        return CheckoutResult(True, "confirmed", "order-9", "confirmed")

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
    return start["status"], {k.decode(): v.decode() for k, v in start["headers"]}, response["body"]


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
        # MVP options only (ADR-006): size + card message accepted; FR-003 controls rejected.
        self.assertEqual(202, self.call("POST", "/api/v1/selection", headers,
            json.dumps({"product_id": "classic-rose-dozen",
                        "options": {"size": "large", "card_message": "hi"},
                        "observed_context_version": 7}).encode())[0])
        for control in ({"colour": "red"}, {"ribbon": "gold"}, {"flower_type": "rose"}):
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
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/order", headers, b"{}")
        self.assertEqual(202, status)
        payload = json.loads(body)
        self.assertEqual("order-9", payload["order_id"])
        self.assertEqual("created", payload["status"])

    def test_workspace_order_facet_is_least_data(self):
        shaped = BffApp._least_data_workspace({"context_version": 4, "facets": {"order": {
            "order_id": "o1", "status": "created", "secret": "omit"}}})
        self.assertEqual({"order_id": "o1", "status": "created"}, shaped["facets"]["order"])

    def test_checkout_requires_csrf_and_rejects_raw_card_fields(self):
        cookie, csrf = self.session()
        json_headers = {**self.auth, "cookie": cookie, "content-type": "application/json"}
        payload = json.dumps({"payment_reference": "tok_1", "observed_total": 82.0}).encode()
        self.assertEqual(403, self.call("POST", "/api/v1/checkout", json_headers, payload)[0])
        headers = {**json_headers, "x-csrf-token": csrf}
        status, _, body = self.call("POST", "/api/v1/checkout", headers, payload)
        self.assertEqual(202, status)
        self.assertTrue(json.loads(body)["confirmed"])
        # Decline maps to 402 with a decline code (no card data).
        declined = self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "decline-1", "observed_total": 82.0}).encode())
        self.assertEqual(402, declined[0])
        self.assertEqual("declined", json.loads(declined[2])["decline_code"])
        # Raw card fields and a missing total are rejected at the edge.
        self.assertEqual(422, self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "tok", "observed_total": 82.0,
                        "card_number": "4111111111111111"}).encode())[0])
        self.assertEqual(422, self.call("POST", "/api/v1/checkout", headers,
            json.dumps({"payment_reference": "tok"}).encode())[0])

    def test_workspace_order_summary_facet_is_least_data(self):
        shaped = BffApp._least_data_workspace({"context_version": 5, "facets": {"order_summary": {
            "currency": "USD", "total": 82.0, "secret": "omit",
            "itemized_charges": [
                {"label": "product", "product_id": "classic-rose-dozen", "amount": 70.0, "secret": "omit"},
                {"label": "delivery", "amount": 12.0}]}}})
        self.assertEqual({
            "itemized_charges": [
                {"label": "product", "product_id": "classic-rose-dozen", "amount": 70.0},
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

    def test_boundary_contains_no_domain_or_infrastructure_authority(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        sources = "\n".join(p.read_text(encoding="utf-8") for p in (root / "bff").rglob("*.py"))
        for forbidden in ("psycopg", "confluent_kafka", "context_version +=", "validate_domain"):
            self.assertNotIn(forbidden, sources)
        compose = (root / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn('"8080:8080"', compose)
        gateway = (root / "gateway" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("TLSv1.2 TLSv1.3", gateway)
        self.assertIn("client_max_body_size 64k", gateway)


if __name__ == "__main__":
    unittest.main()
