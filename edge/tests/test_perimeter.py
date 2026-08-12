import asyncio
import json
import pathlib
import unittest

from edge.bff.aea_bff.app import BffApp
from edge.bff.aea_bff.ports import CommandResult, ConversationResult, CorrectionResult
from edge.bff.aea_bff.security import FixedWindowRateLimiter, StaticTokenAuthenticator


class FakeOrchestration:
    def __init__(self):
        self.messages = []
        self.intent = {"occasion": "birthday", "secret": "omit"}

    def ensure_session(self, **kwargs):
        self.session = kwargs

    def accept_command(self, **kwargs):
        return CommandResult(True, "accepted")

    def workspace_projection(self, **kwargs):
        return {"context_version": 7, "secret": "omit", "tiles": [{"id": "a", "status": "ready", "summary": "ok", "private": "omit"}]}

    def stream_events(self, **kwargs):
        after = kwargs.get("after_event_id")
        return [] if after == "2" else [{"event_id": "2", "projection": self.workspace_projection()}]

    def submit_conversation_message(self, **kwargs):
        self.messages.append({
            "message_id": "message-1", "role": "customer",
            "text": kwargs["message_text"].strip(), "status": "submitted",
            "submitted_at": "2026-08-12T00:00:00+00:00", "private": "omit",
        })
        return ConversationResult(True, "accepted", kwargs["observed_context_version"] + 1,
                                  "message-1")

    def conversation_projection(self, **kwargs):
        return {"context_version": len(self.messages), "messages": self.messages, "secret": "omit"}

    def shared_understanding_projection(self, **kwargs):
        return {"context_version": 1, "structured_intent": self.intent,
                "suggestions": ["What budget?"], "secret": "omit"}

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
        self.assertEqual({"context_version": 7, "tiles": [{"id": "a", "status": "ready", "summary": "ok"}]}, json.loads(body))

    def test_stream_reconnect(self):
        cookie, _ = self.session()
        headers = {**self.auth, "cookie": cookie}
        self.assertIn(b"id: 2", self.call("GET", "/api/v1/stream", headers)[2])
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
