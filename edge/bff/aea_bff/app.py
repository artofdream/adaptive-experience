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

        if path == "/api/v1/workspace" and method == "GET":
            raw = self.orchestration.workspace_projection(session_id=session.session_id, subject=subject)
            return await self._json(send, 200, self._least_data_projection(raw), correlation_id)

        if path == "/api/v1/stream" and method == "GET":
            query = parse_qs(scope.get("query_string", b"").decode())
            after = headers.get("last-event-id") or (query.get("after") or [None])[0]
            events = self.orchestration.stream_events(
                session_id=session.session_id, subject=subject, after_event_id=after,
            )
            chunks = []
            for event in events:
                safe = self._least_data_projection(event["projection"])
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
    def _least_data_projection(raw: dict) -> dict:
        tiles = []
        for tile in raw.get("tiles", []):
            tiles.append({key: tile[key] for key in ("id", "status", "summary", "ai_generated") if key in tile})
        return {"context_version": int(raw.get("context_version", 0)), "tiles": tiles}

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
                "structured_intent": safe_intent, "suggestions": suggestions}

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
