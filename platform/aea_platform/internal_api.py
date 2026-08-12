from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from .conversation import ConversationService, ConversationSessionNotFound, ConversationValidationError
from .intent import IntentSessionNotFound, IntentValidationError, SharedUnderstandingService


class InternalOrchestrationApp:
    """Authenticated internal HTTP surface; authority remains in platform services."""

    def __init__(self, connection, token: str):
        if not token:
            raise ValueError("internal token is required")
        from .adapters import PsycopgExperienceStateStore
        store = PsycopgExperienceStateStore(connection)
        self.connection = connection
        self.token = token
        self.conversation = ConversationService(store)
        self.shared = SharedUnderstandingService(store)

    async def __call__(self, scope, receive, send):
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        if headers.get("authorization") != f"Bearer {self.token}":
            return await self._send(send, 401, {"code": "internal_authentication_required"})
        subject = headers.get("x-subject-reference", "").strip()
        if not subject:
            return await self._send(send, 400, {"code": "subject_required"})
        parts = scope["path"].strip("/").split("/")
        if len(parts) < 4 or parts[:3] != ["internal", "v1", "sessions"]:
            return await self._send(send, 404, {"code": "not_found"})
        session_id = parts[3]
        method = scope["method"]
        try:
            if len(parts) == 4 and method == "PUT":
                self.connection.execute(
                    "INSERT INTO orchestration.experience_session "
                    "(session_id,state_schema_version,expires_at) VALUES (%s,1,%s) "
                    "ON CONFLICT (session_id) DO NOTHING",
                    (session_id, datetime.now(timezone.utc) + timedelta(minutes=30)))
                self.connection.commit()
                return await self._send(send, 204, {})
            resource = parts[4] if len(parts) == 5 else ""
            if resource == "conversation" and method == "GET":
                return await self._send(send, 200, self.conversation.projection(session_id=session_id))
            if resource == "conversation" and method == "POST":
                body = await self._body(receive)
                result = self.conversation.submit(
                    session_id=session_id, subject_reference=subject,
                    message_text=body.get("message_text"),
                    observed_context_version=body.get("observed_context_version"),
                    correlation_id=body.get("correlation_id"))
                return await self._send(send, 202, {"code": "accepted",
                    "context_version": result.context_version, "message_id": result.message_id})
            if resource == "shared-understanding" and method == "GET":
                value = self.shared.projection(session_id=session_id)
                return await self._send(send, 200, {"context_version": value.context_version,
                    "structured_intent": value.structured_intent,
                    "suggestions": list(value.suggestions)})
            if resource == "shared-understanding" and method == "PATCH":
                body = await self._body(receive)
                result = self.shared.correct(
                    session_id=session_id, corrections=body.get("corrections"),
                    observed_context_version=body.get("observed_context_version"),
                    correlation_id=body.get("correlation_id"), subject_reference=subject)
                return await self._send(send, 202, {"code": "accepted",
                    "context_version": result.context_version, "message_id": result.message_id})
        except (ConversationSessionNotFound, IntentSessionNotFound):
            return await self._send(send, 404, {"code": "session_not_found"})
        except (ConversationValidationError, IntentValidationError, TypeError):
            return await self._send(send, 422, {"code": "validation_failed"})
        except Exception as error:
            if getattr(error, "sqlstate", None) == "40001":
                self.connection.rollback()
                return await self._send(send, 409, {"code": "stale_context"})
            raise
        return await self._send(send, 404, {"code": "not_found"})

    @staticmethod
    async def _body(receive):
        data = bytearray()
        while True:
            message = await receive()
            data.extend(message.get("body", b""))
            if not message.get("more_body", False):
                return json.loads(data or b"{}")

    @staticmethod
    async def _send(send, status, payload):
        body = b"" if status == 204 else json.dumps(payload).encode()
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": body})
