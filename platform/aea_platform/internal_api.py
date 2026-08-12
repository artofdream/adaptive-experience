from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from .conversation import ConversationService, ConversationSessionNotFound, ConversationValidationError
from .intent import (IntentAnalysisService, IntentSessionNotFound, IntentValidationError,
                     ReferenceIntentInterpreter, SharedUnderstandingService)
from .inventory import (InventoryAvailabilityService, InventoryUnavailableError,
                        InventoryValidationError)
from .recommendation import RecommendationService
from .state import StatePatch


class InternalOrchestrationApp:
    """Authenticated internal HTTP surface; authority remains in platform services."""

    def __init__(self, connection, token: str, interpreter=None):
        if not token:
            raise ValueError("internal token is required")
        from .adapters import (PsycopgExperienceStateStore, PsycopgInventoryAvailabilityStore,
                               PsycopgRecommendationStore)
        store = PsycopgExperienceStateStore(connection)
        self.store = store
        self.connection = connection
        self.token = token
        self.conversation = ConversationService(store)
        self.shared = SharedUnderstandingService(store)
        self.interpreter = interpreter or ReferenceIntentInterpreter()
        self.intent = IntentAnalysisService(store, self.interpreter)
        self.inventory = InventoryAvailabilityService(PsycopgInventoryAvailabilityStore(connection))
        self.recommendation = RecommendationService(
            PsycopgRecommendationStore(connection), self.inventory)

    async def __call__(self, scope, receive, send):
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        if headers.get("authorization") != f"Bearer {self.token}":
            return await self._send(send, 401, {"code": "internal_authentication_required"})
        subject = headers.get("x-subject-reference", "").strip()
        if not subject:
            return await self._send(send, 400, {"code": "subject_required"})
        parts = scope["path"].strip("/").split("/")
        if scope["path"] == "/internal/v1/ai/health" and scope["method"] == "GET":
            health = getattr(self.interpreter, "health", lambda: {
                "available": True, "mode": "reference", "circuit": "closed"})()
            return await self._send(send, 200, health)
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
                analysis = self.intent.analyze(
                    session_id=session_id, message_text=body.get("message_text"),
                    observed_context_version=result.context_version,
                    correlation_id=body.get("correlation_id"), subject_reference=subject)
                return await self._send(send, 202, {"code": "accepted",
                    "context_version": analysis.context_version, "message_id": result.message_id,
                    "ai_generated": True,
                    "assistant_mode": getattr(self.interpreter, "last_mode", "reference"),
                    "disclosure": "AI-generated interpretation; review and correct before ordering."})
            if resource == "shared-understanding" and method == "GET":
                value = self.shared.projection(session_id=session_id)
                return await self._send(send, 200, {"context_version": value.context_version,
                    "structured_intent": value.structured_intent,
                    "suggestions": list(value.suggestions), "ai_generated": True,
                    "assistant_mode": getattr(self.interpreter, "last_mode", "reference"),
                    "disclosure": "AI-generated interpretation; review and correct before ordering."})
            if resource == "shared-understanding" and method == "PATCH":
                body = await self._body(receive)
                result = self.shared.correct(
                    session_id=session_id, corrections=body.get("corrections"),
                    observed_context_version=body.get("observed_context_version"),
                    correlation_id=body.get("correlation_id"), subject_reference=subject)
                return await self._send(send, 202, {"code": "accepted",
                    "context_version": result.context_version, "message_id": result.message_id})
            if resource == "workspace" and method == "GET":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                return await self._send(send, 200, self._workspace(session_id, loaded))
            if resource == "selection" and method == "POST":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._select_product(send, session_id, subject, loaded, body)
            if resource == "stream" and method == "GET":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                current = int(loaded["context_version"])
                after = self._query_after(scope)
                if after is None:
                    events = [{"event_id": str(current), "context_version": current,
                               "kind": "snapshot", "workspace": self._workspace(session_id, loaded)}]
                else:
                    events = [{"event_id": str(item["context_version"]),
                               "context_version": item["context_version"], "kind": "invalidation",
                               "invalidated_projections": item["invalidated_projections"]}
                              for item in self.store.invalidations_after(session_id, after)]
                return await self._send(send, 200, {"events": events})
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

    def _workspace(self, session_id: str, loaded: dict) -> dict:
        """Aggregate least-data facet document at the current context version.

        Tiles are namespaced facets (Option A, #144). Recommendations/selection
        facets slot in as their services begin writing state (#142).
        """
        conversation = self.conversation.projection(session_id=session_id)
        shared = self.shared.projection(session_id=session_id)
        state = loaded.get("state") or {}
        facets = {
            "conversation": {"messages": conversation.get("messages", [])},
            "shared_understanding": {
                "structured_intent": shared.structured_intent,
                "suggestions": list(shared.suggestions),
            },
            "recommendations": {"items": self.recommendation.preview(intent=shared.structured_intent)},
        }
        selection = (state.get("decisions") or {}).get("product")
        if isinstance(selection, dict):
            facets["selection"] = selection
        return {
            "context_version": int(loaded["context_version"]),
            "facets": facets,
            "ai_generated": True,
            "assistant_mode": getattr(self.interpreter, "last_mode", "reference"),
            "disclosure": "AI-generated interpretation; review and correct before ordering.",
        }

    async def _select_product(self, send, session_id: str, subject: str,
                              loaded: dict, body: dict):
        product_id = body.get("product_id")
        options = body.get("options") if body.get("options") is not None else {}
        observed = body.get("observed_context_version")
        correlation_id = body.get("correlation_id")
        if (not isinstance(product_id, str) or not product_id.strip()
                or not isinstance(options, dict)
                or not isinstance(correlation_id, str) or not correlation_id.strip()):
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            # Authoritative selection-time revalidation (publishes + audits); rejects
            # unavailable or stale inventory (FR-011).
            self.inventory.validate(
                session_id=session_id, product_ids=[product_id.strip()],
                observed_context_version=observed, correlation_id=correlation_id.strip(),
                subject_reference=subject, purpose="selection")
        except InventoryUnavailableError:
            return await self._send(send, 409, {"code": "product_unavailable"})
        except InventoryValidationError:
            return await self._send(send, 422, {"code": "validation_failed"})
        except RuntimeError:
            self.connection.rollback()
            return await self._send(send, 409, {"code": "stale_context"})
        # Write the product decision and emit product.selected in one versioned
        # transaction, so the event fires exactly once at the new context version.
        message_id = str(uuid.uuid4())
        envelope = {
            "message_id": message_id, "topic": "product.selected", "message_type": "event",
            "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id.strip(), "source": "orchestration",
            "context_version": observed,
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential", "subject_reference": subject},
            "payload": {"product_id": product_id.strip(), "options": options}, "outcome": {},
        }
        patch = StatePatch.create(
            {"decisions": {"product": {"product_id": product_id.strip(), "options": options}}},
            ["decisions.product"])
        try:
            new_version = self.store.apply_patch(
                session_id, observed, int(loaded["state_schema_version"]), patch,
                [{"message_id": message_id, "topic": "product.selected",
                  "aggregate_key": session_id, "envelope": envelope}])
        except Exception as error:
            if getattr(error, "sqlstate", None) == "40001":
                self.connection.rollback()
                return await self._send(send, 409, {"code": "stale_context"})
            raise
        return await self._send(send, 202, {"code": "accepted",
            "context_version": new_version, "message_id": message_id})

    @staticmethod
    def _query_after(scope) -> int | None:
        raw = parse_qs(scope.get("query_string", b"").decode())
        value = (raw.get("after") or [None])[0]
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

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
