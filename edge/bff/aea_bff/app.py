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


class BffApp:
    def __init__(self, orchestration: OrchestrationPort, authenticator: StaticTokenAuthenticator,
                 *, allowed_origin: str, max_request_bytes: int = 65536,
                 sessions: SessionStore | None = None,
                 rate_limiter: FixedWindowRateLimiter | None = None):
        self.orchestration = orchestration
        self.authenticator = authenticator
        self.allowed_origin = allowed_origin
        self.max_request_bytes = max_request_bytes
        self.sessions = sessions or SessionStore()
        self.rate_limiter = rate_limiter or FixedWindowRateLimiter()

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
            session = self.sessions.create(subject)
            try:
                self.orchestration.ensure_session(session_id=session.session_id, subject=subject)
            except (OrchestrationUnavailable, RuntimeError):
                return await self._error(send, 503, "orchestration_unavailable", correlation_id)
            cookie = (f"__Host-aea_session={session.session_id}; Path=/; Secure; HttpOnly; "
                      "SameSite=Lax")
            return await self._json(send, 201, {"csrf_token": session.csrf_token}, correlation_id,
                                    {"set-cookie": cookie})

        session = self.sessions.get(self._cookie(headers.get("cookie"), "__Host-aea_session"))
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
                result = self.orchestration.correct_shared_understanding(
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
            # Only MVP T-04 options (ADR-006): an eligible size and a physical card
            # message. Reject FR-003 controls (flower type, colour, ribbon, ...) at
            # the edge; Orchestration re-validates and normalizes authoritatively.
            if (set(options) - {"size", "card_message"}
                    or any(not isinstance(value, str) for value in options.values())
                    or len(options.get("card_message", "")) > 280
                    or len(options.get("size", "")) > 40):
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
                                   "availability_status") if key in item})
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
            if isinstance(facets_in["order"].get("order_id"), str):
                order["order_id"] = facets_in["order"]["order_id"]
            if isinstance(facets_in["order"].get("status"), str):
                order["status"] = facets_in["order"]["status"]
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

    async def _error(self, send, status, code, correlation_id, extra_headers=None):
        await self._json(send, status, {"error": code, "correlation_id": correlation_id},
                         correlation_id, extra_headers)

    async def _json(self, send, status, payload, correlation_id, extra_headers=None):
        await self._send(send, status, json.dumps(payload).encode(), "application/json", correlation_id,
                         extra_headers)

    async def _send(self, send, status, body, content_type, correlation_id, extra_headers=None):
        headers = dict(SECURITY_HEADERS)
        headers.update({"content-type": content_type, "x-correlation-id": correlation_id})
        headers.update(extra_headers or {})
        await send({"type": "http.response.start", "status": status,
                    "headers": [(key.encode(), value.encode()) for key, value in headers.items()]})
        await send({"type": "http.response.body", "body": body})
