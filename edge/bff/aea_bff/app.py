from __future__ import annotations

import json
import uuid
from http.cookies import SimpleCookie
from urllib.parse import parse_qs

from .ports import OrchestrationPort
from .orchestration import OrchestrationUnavailable
from .security import FixedWindowRateLimiter, SessionStore, StaticTokenAuthenticator


SECURITY_HEADERS = {
    "content-security-policy": "default-src 'self'; frame-ancestors 'none'; object-src 'none'",
    "referrer-policy": "no-referrer",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "cache-control": "no-store",
}

SESSION_COOKIE = "__Host-aea_session"
RECALL_COOKIE = "__Host-aea_recall"
RECALL_MAX_AGE_SECONDS = 2592000


class BffApp:
    def __init__(self, orchestration: OrchestrationPort, authenticator: StaticTokenAuthenticator,
                 *, allowed_origin: str, max_request_bytes: int = 65536,
                 sessions: SessionStore | None = None,
                 rate_limiter: FixedWindowRateLimiter | None = None,
                 florist_operator_enabled: bool = False):
        self.orchestration = orchestration
        self.authenticator = authenticator
        self.allowed_origin = allowed_origin
        self.max_request_bytes = max_request_bytes
        self.sessions = sessions or SessionStore()
        self.rate_limiter = rate_limiter or FixedWindowRateLimiter()
        self.florist_operator_enabled = florist_operator_enabled

    @staticmethod
    def florist_operator_enabled_for(*, environment: str, flag: str | None) -> bool:
        """Local-only staff reads. Production always fails closed."""
        return flag == "1" and environment != "production"

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        correlation_id = self._correlation_id(headers.get("x-correlation-id"))
        path, method = scope["path"], scope["method"]
        if path == "/healthz" and method == "GET":
            return await self._json(send, 200, {"status": "ok"}, correlation_id)
        if headers.get("origin") not in {None, self.allowed_origin}:
            return await self._error(send, 403, "origin_rejected", correlation_id)

        subject = self.authenticator.authenticate(headers.get("authorization"))
        if subject is None:
            return await self._error(send, 401, "authentication_required", correlation_id)
        if not self.rate_limiter.allow(subject):
            return await self._error(send, 429, "rate_limit_exceeded", correlation_id,
                                     extra_headers={"retry-after": "60"})

        if path == "/api/v1/session" and method == "POST":
            # Reuse a valid same-subject cookie. A second tab or /florist boot
            # must not mint a new session and invalidate the first tab's CSRF.
            existing = self.sessions.get(self._cookie(headers.get("cookie"), SESSION_COOKIE))
            presented_recall = self._recall_id(
                self._cookie(headers.get("cookie"), RECALL_COOKIE))
            if existing is not None and existing.subject == subject:
                session = existing
                if session.recall_id is None:
                    session.recall_id = presented_recall or str(uuid.uuid4())
            else:
                session = self.sessions.create(
                    subject, recall_id=presented_recall or str(uuid.uuid4()))
            try:
                self.orchestration.ensure_session(
                    session_id=session.session_id, subject=subject,
                    recall_id=session.recall_id)
            except (OrchestrationUnavailable, RuntimeError):
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 201, {"csrf_token": session.csrf_token}, correlation_id, (
                ("set-cookie", self._cookie_header(SESSION_COOKIE, session.session_id)),
                ("set-cookie", self._cookie_header(
                    RECALL_COOKIE, session.recall_id, max_age=RECALL_MAX_AGE_SECONDS)),
            ))

        session = self.sessions.get(self._cookie(headers.get("cookie"), SESSION_COOKIE))
        if session is None or session.subject != subject:
            return await self._error(send, 401, "session_required", correlation_id)
        if method in {"POST", "PUT", "PATCH", "DELETE"}:
            if headers.get("x-csrf-token") != session.csrf_token:
                return await self._error(send, 403, "csrf_rejected", correlation_id)

        if path == "/api/v1/commands" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                command = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if set(command) != {"command", "observed_context_version"} or not isinstance(command["command"], dict):
                return await self._error(send, 422, "invalid_command_shape", correlation_id)
            observed = command["observed_context_version"]
            if not isinstance(observed, int) or observed < 0:
                return await self._error(send, 422, "invalid_context_version", correlation_id)
            result = self.orchestration.accept_command(
                session_id=session.session_id, subject=subject, command=command["command"],
                observed_context_version=observed, correlation_id=correlation_id,
            )
            status = 202 if result.accepted else 422
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "correlation_id": correlation_id, "observed_context_version": observed,
            }, correlation_id)

        if path == "/api/v1/conversation/messages" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                submission = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if set(submission) != {"message_text", "observed_context_version"}:
                return await self._error(send, 422, "invalid_conversation_shape", correlation_id)
            message_text = submission["message_text"]
            observed = submission["observed_context_version"]
            if (not isinstance(message_text, str) or not message_text.strip()
                    or len(message_text.strip()) > 2000
                    or any(ord(character) < 32 and character not in "\n\t"
                           for character in message_text.strip())):
                return await self._error(send, 422, "invalid_message_text", correlation_id)
            if not isinstance(observed, int) or isinstance(observed, bool) or observed < 0:
                return await self._error(send, 422, "invalid_context_version", correlation_id)
            try:
                result = self.orchestration.submit_conversation_message(
                    session_id=session.session_id, subject=subject, message_text=message_text,
                    observed_context_version=observed, correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else (409 if result.code == "stale_context" else 422)
            return await self._json(send, status, {
                "accepted": result.accepted,
                "code": result.code,
                "message_id": result.message_id,
                "correlation_id": correlation_id,
                "context_version": result.context_version,
                "ai_generated": result.ai_generated,
                "assistant_mode": result.assistant_mode,
                "disclosure": result.disclosure,
            }, correlation_id)

        if path == "/api/v1/conversation" and method == "GET":
            try:
                raw = self.orchestration.conversation_projection(
                    session_id=session.session_id, subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_conversation(raw), correlation_id)

        if path == "/api/v1/shared-understanding" and method == "GET":
            try:
                raw = self.orchestration.shared_understanding_projection(
                    session_id=session.session_id, subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_shared_understanding(raw),
                                    correlation_id)

        if path == "/api/v1/shared-understanding" and method == "PATCH":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                correction = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if set(correction) != {"corrections", "observed_context_version"}:
                return await self._error(send, 422, "invalid_correction_shape", correlation_id)
            observed = correction["observed_context_version"]
            if (not isinstance(correction["corrections"], dict) or not correction["corrections"]
                    or not isinstance(observed, int) or isinstance(observed, bool) or observed < 0):
                return await self._error(send, 422, "invalid_correction_shape", correlation_id)
            try:
                result = self._correct_shared_understanding(
                    session_id=session.session_id, subject=subject,
                    corrections=correction["corrections"], observed_context_version=observed,
                    correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else (409 if result.code == "stale_context" else 422)
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "message_id": result.message_id, "correlation_id": correlation_id,
                "context_version": result.context_version,
            }, correlation_id)

        if path == "/api/v1/selection" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                selection = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if (not isinstance(selection, dict)
                    or set(selection) - {"product_id", "options", "observed_context_version"}
                    or "product_id" not in selection
                    or "observed_context_version" not in selection):
                return await self._error(send, 422, "invalid_selection_shape", correlation_id)
            product_id = selection["product_id"]
            options = selection.get("options", {})
            observed = selection["observed_context_version"]
            if (not isinstance(product_id, str) or not product_id.strip()
                    or len(product_id.strip()) > 120 or not isinstance(options, dict)
                    or not isinstance(observed, int) or isinstance(observed, bool) or observed < 0):
                return await self._error(send, 422, "invalid_selection_shape", correlation_id)
            # T-04 options (ADR-006 amended): size, card message, and thin FR-003
            # keys. Orchestration re-validates tokens and flower_type eligibility.
            allowed = {"size", "card_message", "flower_type", "colour", "ribbon"}
            if (set(options) - allowed
                    or any(not isinstance(value, str) for value in options.values())
                    or len(options.get("card_message", "")) > 280
                    or len(options.get("size", "")) > 40
                    or len(options.get("flower_type", "")) > 40
                    or len(options.get("colour", "")) > 40
                    or len(options.get("ribbon", "")) > 40):
                return await self._error(send, 422, "invalid_selection_shape", correlation_id)
            try:
                result = self.orchestration.select_product(
                    session_id=session.session_id, subject=subject, product_id=product_id.strip(),
                    options=options, observed_context_version=observed, correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else (
                409 if result.code in {"stale_context", "product_unavailable"} else 422)
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "message_id": result.message_id, "correlation_id": correlation_id,
                "context_version": result.context_version,
            }, correlation_id)

        if path == "/api/v1/delivery" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                request = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if (not isinstance(request, dict)
                    or set(request) - {"delivery", "observed_context_version"}
                    or "delivery" not in request or "observed_context_version" not in request):
                return await self._error(send, 422, "invalid_delivery_shape", correlation_id)
            delivery = request["delivery"]
            observed = request["observed_context_version"]
            # Reference-only recipient data (FR-014): reject raw PII keys at the edge
            # by allowing only timing and destination_reference; Orchestration
            # re-validates authoritatively.
            if (not isinstance(delivery, dict)
                    or set(delivery) - {"timing", "destination_reference"}
                    or not isinstance(delivery.get("destination_reference"), str)
                    or not isinstance(delivery.get("timing"), dict)
                    or not isinstance(observed, int) or isinstance(observed, bool) or observed < 0):
                return await self._error(send, 422, "invalid_delivery_shape", correlation_id)
            try:
                result = self.orchestration.update_delivery(
                    session_id=session.session_id, subject=subject, delivery=delivery,
                    observed_context_version=observed, correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else (409 if result.code == "stale_context" else 422)
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "message_id": result.message_id, "correlation_id": correlation_id,
                "context_version": result.context_version,
            }, correlation_id)

        if path == "/api/v1/order" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                request = json.loads(body or b"{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if not isinstance(request, dict):
                return await self._error(send, 422, "invalid_order_shape", correlation_id)
            try:
                result = self.orchestration.create_order(
                    session_id=session.session_id, subject=subject, correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else 422
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "order_id": result.order_id, "status": result.status,
                "correlation_id": correlation_id,
            }, correlation_id)

        if path == "/api/v1/checkout" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                request = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            # Only a payment reference and the observed total are accepted; raw card
            # fields (card_number, cvv, ...) are rejected at the edge (NFR-013).
            if (not isinstance(request, dict)
                    or set(request) - {"payment_reference", "observed_total"}
                    or "payment_reference" not in request or "observed_total" not in request):
                return await self._error(send, 422, "invalid_checkout_shape", correlation_id)
            payment_reference = request["payment_reference"]
            observed_total = request["observed_total"]
            if (not isinstance(payment_reference, str) or not payment_reference.strip()
                    or len(payment_reference.strip()) > 200 or isinstance(observed_total, bool)
                    or not isinstance(observed_total, (int, float)) or observed_total <= 0):
                return await self._error(send, 422, "invalid_checkout_shape", correlation_id)
            try:
                result = self.orchestration.checkout(
                    session_id=session.session_id, subject=subject,
                    payment_reference=payment_reference.strip(), observed_total=observed_total,
                    correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            if result.accepted:
                status = 202
            elif result.code in {"total_mismatch", "checkout_conflict"}:
                status = 409
            elif result.code == "order_not_found":
                status = 404
            else:
                status = 422
            return await self._json(send, status, {
                "accepted": result.accepted,
                "pending": bool(result.accepted),
                "confirmed": result.confirmed,
                "code": result.code,
                "order_id": result.order_id,
                "status": result.status,
                "decline_code": result.decline_code,
                "correlation_id": correlation_id,
            }, correlation_id)

        if path == "/api/v1/support" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                request = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            if (not isinstance(request, dict) or set(request) - {"question"}
                    or "question" not in request):
                return await self._error(send, 422, "invalid_support_shape", correlation_id)
            question = request["question"]
            if (not isinstance(question, str) or not question.strip()
                    or len(question.strip()) > 500):
                return await self._error(send, 422, "invalid_support_shape", correlation_id)
            try:
                result = self.orchestration.ask_support(
                    session_id=session.session_id, subject=subject, question=question.strip(),
                    correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 200 if result.answered else 422
            return await self._json(send, status, {
                "answered": result.answered, "code": result.code, "answer": result.answer,
                "approved_source_references": list(result.approved_source_references),
                "matched": result.matched, "kind": result.kind,
                "fact_references": list(result.fact_references),
                "correlation_id": correlation_id,
            }, correlation_id)

        if path == "/api/v1/support/escalation" and method == "POST":
            if headers.get("content-type", "").split(";", 1)[0].strip() != "application/json":
                return await self._error(send, 415, "unsupported_media_type", correlation_id)
            body = await self._body(receive, headers)
            if isinstance(body, tuple):
                return await self._error(send, body[0], body[1], correlation_id)
            try:
                request = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return await self._error(send, 400, "invalid_json", correlation_id)
            allowed_reasons = {
                "unresolved_request", "order_issue", "delivery_issue", "product_question",
            }
            if (not isinstance(request, dict) or set(request) - {"reason"}
                    or "reason" not in request):
                return await self._error(send, 422, "invalid_escalation_shape", correlation_id)
            reason = request["reason"]
            if not isinstance(reason, str) or reason.strip() not in allowed_reasons:
                return await self._error(send, 422, "invalid_escalation_shape", correlation_id)
            try:
                result = self.orchestration.request_escalation(
                    session_id=session.session_id, subject=subject,
                    reason=reason.strip(), correlation_id=correlation_id)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = 202 if result.accepted else 422
            return await self._json(send, status, {
                "accepted": result.accepted, "code": result.code,
                "message_id": result.message_id,
                "acknowledgement": result.acknowledgement,
                "escalation_reason": result.escalation_reason,
                "correlation_id": correlation_id,
            }, correlation_id)

        if path == "/api/v1/operator/escalations" and method == "GET":
            if not self.florist_operator_enabled:
                return await self._error(send, 404, "not_found", correlation_id)
            try:
                raw = self.orchestration.list_operator_escalations(subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            if int(raw.get("status") or 200) >= 500:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_operator_escalations(raw),
                                    correlation_id)

        if path == "/api/v1/operator/forecasts" and method == "GET":
            if not self.florist_operator_enabled:
                return await self._error(send, 404, "not_found", correlation_id)
            try:
                raw = self.orchestration.list_operator_forecasts(
                    session_id=session.session_id, subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = int(raw.get("status") or 200)
            if status == 404 or raw.get("code") == "session_not_found":
                return await self._error(send, 404, "session_not_found", correlation_id)
            if status >= 500:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_operator_forecasts(raw),
                                    correlation_id)

        operator_prefix = "/api/v1/operator/sessions/"
        if path.startswith(operator_prefix) and method == "GET":
            if not self.florist_operator_enabled:
                return await self._error(send, 404, "not_found", correlation_id)
            session_id = path[len(operator_prefix):]
            try:
                session_id = str(uuid.UUID(session_id))
            except ValueError:
                return await self._error(send, 422, "invalid_session_reference", correlation_id)
            try:
                raw = self.orchestration.operator_session_summary(
                    session_id=session_id, subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            status = int(raw.get("status") or 200)
            if status == 404 or raw.get("code") == "session_not_found":
                return await self._error(send, 404, "session_not_found", correlation_id)
            if status >= 500:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_operator_summary(raw),
                                    correlation_id)

        if path == "/api/v1/workspace" and method == "GET":
            try:
                raw = self.orchestration.workspace_projection(
                    session_id=session.session_id, subject=subject)
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            return await self._json(send, 200, self._least_data_workspace(raw), correlation_id)

        if path == "/api/v1/stream" and method == "GET":
            query = parse_qs(scope.get("query_string", b"").decode())
            after = headers.get("last-event-id") or (query.get("after") or [None])[0]
            try:
                events = self.orchestration.stream_events(
                    session_id=session.session_id, subject=subject, after_event_id=after,
                )
            except OrchestrationUnavailable:
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            chunks = []
            for event in events:
                safe = self._least_data_stream_event(event)
                chunks.append(f"id: {event['event_id']}\nevent: workspace\ndata: {json.dumps(safe)}\n\n")
            await self._send(send, 200, "".join(chunks).encode(), "text/event-stream", correlation_id,
                             {"x-accel-buffering": "no"})
            return

        await self._error(send, 404, "not_found", correlation_id)

    async def _body(self, receive, headers):
        try:
            declared = int(headers.get("content-length", "0"))
        except ValueError:
            return 400, "invalid_content_length"
        if declared > self.max_request_bytes:
            return 413, "request_too_large"
        data = bytearray()
        while True:
            message = await receive()
            data.extend(message.get("body", b""))
            if len(data) > self.max_request_bytes:
                return 413, "request_too_large"
            if not message.get("more_body", False):
                return bytes(data)

    @staticmethod
    def _cookie(raw: str | None, name: str) -> str | None:
        cookie = SimpleCookie(raw or "")
        return cookie[name].value if name in cookie else None

    @staticmethod
    def _recall_id(candidate: str | None) -> str | None:
        if not isinstance(candidate, str) or not candidate.strip():
            return None
        try:
            return str(uuid.UUID(candidate.strip()))
        except ValueError:
            return None

    @staticmethod
    def _cookie_header(name: str, value: str, *, max_age: int | None = None) -> str:
        header = f"{name}={value}; Path=/; Secure; HttpOnly; SameSite=Lax"
        if max_age is not None:
            header += f"; Max-Age={max_age}"
        return header

    @staticmethod
    def _correlation_id(candidate: str | None) -> str:
        try:
            return str(uuid.UUID(candidate)) if candidate else str(uuid.uuid4())
        except ValueError:
            return str(uuid.uuid4())

    @staticmethod
    def _least_data_workspace(raw: dict) -> dict:
        facets_in = raw.get("facets") or {}
        facets = {}
        if isinstance(facets_in.get("conversation"), dict):
            facets["conversation"] = {
                "messages": BffApp._least_data_conversation(facets_in["conversation"])["messages"]}
        if isinstance(facets_in.get("shared_understanding"), dict):
            shaped = BffApp._least_data_shared_understanding(facets_in["shared_understanding"])
            facets["shared_understanding"] = {
                "structured_intent": shaped["structured_intent"],
                "suggestions": shaped["suggestions"]}
        if isinstance(facets_in.get("recommendations"), dict):
            items = []
            for item in facets_in["recommendations"].get("items") or []:
                if isinstance(item, dict):
                    items.append({key: item[key] for key in
                                  ("product_id", "price", "score", "rank", "available",
                                   "availability_status", "prior_order_hint") if key in item})
            facets["recommendations"] = {"items": items}
        if isinstance(facets_in.get("selection"), dict):
            selection = {}
            if isinstance(facets_in["selection"].get("product_id"), str):
                selection["product_id"] = facets_in["selection"]["product_id"]
            if isinstance(facets_in["selection"].get("options"), dict):
                selection["options"] = facets_in["selection"]["options"]
            facets["selection"] = selection
        if isinstance(facets_in.get("delivery"), dict):
            delivery = {}
            if isinstance(facets_in["delivery"].get("destination_reference"), str):
                delivery["destination_reference"] = facets_in["delivery"]["destination_reference"]
            if isinstance(facets_in["delivery"].get("timing"), dict):
                timing = facets_in["delivery"]["timing"]
                delivery["timing"] = {key: timing[key] for key in ("date", "window")
                                      if key in timing}
            facets["delivery"] = delivery
        if isinstance(facets_in.get("order"), dict):
            order = {}
            for key in ("order_id", "status", "authoritative_status"):
                if isinstance(facets_in["order"].get(key), str):
                    order[key] = facets_in["order"][key]
            if isinstance(facets_in["order"].get("delayed"), bool):
                order["delayed"] = facets_in["order"]["delayed"]
            facets["order"] = order
        if isinstance(facets_in.get("order_summary"), dict):
            summary_in = facets_in["order_summary"]
            charges = []
            for charge in summary_in.get("itemized_charges") or []:
                if isinstance(charge, dict):
                    charges.append({key: charge[key] for key in ("label", "product_id", "amount")
                                    if key in charge})
            order_summary = {"itemized_charges": charges}
            if isinstance(summary_in.get("total"), (int, float)):
                order_summary["total"] = summary_in["total"]
            if isinstance(summary_in.get("currency"), str):
                order_summary["currency"] = summary_in["currency"]
            facets["order_summary"] = order_summary
        return {"context_version": int(raw.get("context_version", 0)),
                "facets": facets,
                "ai_generated": bool(raw.get("ai_generated", False)),
                "assistant_mode": raw.get("assistant_mode"),
                "disclosure": raw.get("disclosure")}

    @staticmethod
    def _least_data_stream_event(event: dict) -> dict:
        shaped = {"event_id": str(event.get("event_id", "")),
                  "context_version": int(event.get("context_version", 0)),
                  "kind": event.get("kind")}
        if event.get("kind") == "snapshot":
            shaped["workspace"] = BffApp._least_data_workspace(event.get("workspace") or {})
        else:
            projections = []
            for item in event.get("invalidated_projections") or []:
                if isinstance(item, dict) and "projection_key" in item:
                    projections.append({key: item[key] for key in ("projection_key", "reason")
                                        if key in item})
            shaped["invalidated_projections"] = projections
        return shaped

    @staticmethod
    def _least_data_conversation(raw: dict) -> dict:
        messages = []
        for item in raw.get("messages", [])[-50:]:
            if not isinstance(item, dict):
                continue
            messages.append({key: item[key] for key in
                             ("message_id", "role", "text", "status", "submitted_at")
                             if key in item})
        return {"context_version": int(raw.get("context_version", 0)), "messages": messages}

    @staticmethod
    def _least_data_shared_understanding(raw: dict) -> dict:
        allowed = {"occasion", "budget", "recipient", "style",
                   "flower_preference", "timing"}
        intent = raw.get("structured_intent") or {}
        safe_intent = {key: intent[key] for key in allowed if key in intent}
        suggestions = [item for item in (raw.get("suggestions") or [])[:3]
                       if isinstance(item, str)]
        return {"context_version": int(raw.get("context_version", 0)),
                "structured_intent": safe_intent, "suggestions": suggestions,
                "ai_generated": bool(raw.get("ai_generated", False)),
                "assistant_mode": raw.get("assistant_mode"),
                "disclosure": raw.get("disclosure")}

    @staticmethod
    def _least_data_operator_escalations(raw: dict) -> dict:
        items = []
        for item in (raw.get("items") or [])[:50]:
            if not isinstance(item, dict):
                continue
            shaped = {key: item[key] for key in
                      ("message_id", "session_id", "escalation_reason",
                       "context_reference", "requested_at") if key in item}
            if shaped:
                items.append(shaped)
        return {"items": items}

    @staticmethod
    def _least_data_operator_forecasts(raw: dict) -> dict:
        items = []
        for item in (raw.get("items") or [])[:100]:
            if not isinstance(item, dict):
                continue
            shaped = {key: item[key] for key in
                      ("product_id", "trend", "recommendation", "fact_references")
                      if key in item}
            if shaped.get("product_id") and shaped.get("trend") and shaped.get("recommendation"):
                refs = shaped.get("fact_references")
                if isinstance(refs, list):
                    shaped["fact_references"] = [str(ref) for ref in refs if isinstance(ref, str)][:8]
                items.append(shaped)
        return {"items": items}

    @staticmethod
    def _least_data_operator_summary(raw: dict) -> dict:
        conversation = raw.get("conversation") if isinstance(raw.get("conversation"), dict) else {}
        shared = raw.get("shared_understanding") if isinstance(raw.get("shared_understanding"), dict) else {}
        availability = []
        for item in raw.get("availability") or []:
            if isinstance(item, dict):
                availability.append({key: item[key] for key in
                                     ("product_id", "available", "availability_status")
                                     if key in item})
        order = None
        if isinstance(raw.get("order"), dict):
            order = {key: raw["order"][key] for key in
                     ("order_id", "status", "authoritative_status", "delayed")
                     if key in raw["order"]}
        selection = None
        if isinstance(raw.get("selection"), dict) and isinstance(raw["selection"].get("product_id"), str):
            selection = {"product_id": raw["selection"]["product_id"]}
        delivery = None
        if isinstance(raw.get("delivery"), dict):
            delivery = {}
            if isinstance(raw["delivery"].get("destination_reference"), str):
                delivery["destination_reference"] = raw["delivery"]["destination_reference"]
            if isinstance(raw["delivery"].get("timing"), dict):
                timing = raw["delivery"]["timing"]
                delivery["timing"] = {key: timing[key] for key in ("date", "window")
                                      if key in timing}
        answers = []
        for item in raw.get("support_answers") or []:
            if not isinstance(item, dict):
                continue
            shaped = {key: item[key] for key in
                      ("message_id", "kind", "answer", "approved_source_references",
                       "situation_kind", "fact_references", "answered_at")
                      if key in item}
            if shaped.get("kind") not in ("faq", "situation"):
                continue
            if not isinstance(shaped.get("answer"), str) or not shaped["answer"]:
                continue
            for list_key in ("approved_source_references", "fact_references"):
                refs = shaped.get(list_key)
                if isinstance(refs, list):
                    shaped[list_key] = [str(ref) for ref in refs if isinstance(ref, str)][:8]
            answers.append(shaped)
        return {
            "session_id": raw.get("session_id"),
            "context_version": int(raw.get("context_version", 0)),
            "conversation": BffApp._least_data_conversation(conversation),
            "shared_understanding": {
                "structured_intent": BffApp._least_data_shared_understanding(shared)["structured_intent"]},
            "order": order,
            "selection": selection,
            "delivery": delivery or None,
            "availability": availability,
            "support_answers": answers,
        }

    def _correct_shared_understanding(self, *, session_id: str, subject: str,
                                      corrections: dict, observed_context_version: int,
                                      correlation_id: str):
        """Retry a T-02 save against the current version if the client raced an update.

        Orchestration still owns compare-and-set (ADR-009). The BFF only reloads
        the authoritative version and retries once so `stale_context` is not
        leaked to the customer during “Updating…”.
        """
        result = self.orchestration.correct_shared_understanding(
            session_id=session_id, subject=subject, corrections=corrections,
            observed_context_version=observed_context_version,
            correlation_id=correlation_id)
        if result.accepted or result.code != "stale_context":
            return result
        projection = self.orchestration.shared_understanding_projection(
            session_id=session_id, subject=subject)
        current = projection.get("context_version")
        if (not isinstance(current, int) or isinstance(current, bool) or current < 0
                or current == observed_context_version):
            return result
        return self.orchestration.correct_shared_understanding(
            session_id=session_id, subject=subject, corrections=corrections,
            observed_context_version=current, correlation_id=correlation_id)

    async def _error(self, send, status, code, correlation_id, extra_headers=None):
        await self._json(send, status, {"error": code, "correlation_id": correlation_id},
                         correlation_id, extra_headers)

    async def _json(self, send, status, payload, correlation_id, extra_headers=None):
        await self._send(send, status, json.dumps(payload).encode(), "application/json", correlation_id,
                         extra_headers)

    async def _send(self, send, status, body, content_type, correlation_id, extra_headers=None):
        headers = list(SECURITY_HEADERS.items())
        headers.extend((("content-type", content_type), ("x-correlation-id", correlation_id)))
        if isinstance(extra_headers, dict):
            headers.extend(extra_headers.items())
        elif extra_headers:
            headers.extend(extra_headers)
        await send({"type": "http.response.start", "status": status,
                    "headers": [(key.encode(), value.encode()) for key, value in headers]})
        await send({"type": "http.response.body", "body": body})
