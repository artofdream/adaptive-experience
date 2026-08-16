from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from .generative_ai import disclosure_for_mode
from .conversation import ConversationService, ConversationSessionNotFound, ConversationValidationError
from .delivery import DeliveryValidationError, normalize_delivery_details
from .intent import (IntentAnalysisService, IntentSessionNotFound, IntentValidationError,
                     ReferenceIntentInterpreter, SharedUnderstandingService,
                     is_stale_context_error)
from .inventory import (InventoryAvailabilityService, InventoryForecastService,
                        InventoryUnavailableError, InventoryValidationError)
from .order import (ORDER_STATUS_SEQUENCE, CheckoutService, CheckoutStateError,
                    CheckoutTotalMismatch, OrderIncompleteError, OrderNotFound, OrderService,
                    OrderStatusError)
from .payment import PaymentValidationError, ReferencePaymentAuthority
from .payment_checkout import PaymentCheckoutHandler
from .pricing import PricingService
from .support import SupportService, SupportValidationError
from .recommendation import RecommendationService
from .selection import SelectionValidationError, normalize_selection_options
from .state import StatePatch


class _InProcessOffsets:
    def commit(self, record) -> None:
        return None


class _InProcessFailures:
    def route(self, consumer_group, record, error):
        raise error


class InternalOrchestrationApp:
    """Authenticated internal HTTP surface; authority remains in platform services."""

    def __init__(self, connection, token: str, interpreter=None):
        if not token:
            raise ValueError("internal token is required")
        from .adapters import (PsycopgExperienceStateStore, PsycopgInventoryAvailabilityStore,
                               PsycopgOrderStore, PsycopgRecommendationStore, PsycopgSupportStore)
        store = PsycopgExperienceStateStore(connection)
        self.store = store
        self.connection = connection
        self.token = token
        self.conversation = ConversationService(store)
        self.shared = SharedUnderstandingService(store)
        self.interpreter = interpreter or ReferenceIntentInterpreter()
        self.intent = IntentAnalysisService(store, self.interpreter)
        inventory_store = PsycopgInventoryAvailabilityStore(connection)
        self.inventory = InventoryAvailabilityService(inventory_store)
        self.forecast = InventoryForecastService(inventory_store)
        order_store = PsycopgOrderStore(connection)
        self.order_store = order_store
        self.order = OrderService(order_store)
        self.recommendation = RecommendationService(
            PsycopgRecommendationStore(connection), self.inventory,
            prior_product_lookup=self.order.session_prior_product_id)
        self.pricing = PricingService()
        self.checkout = CheckoutService(order_store, self.pricing)
        self.payment_handler = PaymentCheckoutHandler(order_store, ReferencePaymentAuthority())
        self.support = SupportService(PsycopgSupportStore(connection))

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
        if scope["path"] == "/internal/v1/operator/escalations" and scope["method"] == "GET":
            return await self._send(send, 200, {"items": self._operator_escalations()})
        if scope["path"] == "/internal/v1/operator/forecasts" and scope["method"] == "GET":
            query = parse_qs(scope.get("query_string", b"").decode())
            session_id = (query.get("session_id") or [""])[0]
            try:
                session_id = str(uuid.UUID(session_id))
            except ValueError:
                return await self._send(send, 422, {"code": "invalid_session_reference"})
            try:
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                return await self._send(send, 200, self._operator_forecasts(
                    session_id, loaded, subject))
            except InventoryValidationError:
                return await self._send(send, 422, {"code": "validation_failed"})
            except (ConversationSessionNotFound, IntentSessionNotFound):
                return await self._send(send, 404, {"code": "session_not_found"})
        if (len(parts) == 5 and parts[:4] == ["internal", "v1", "operator", "sessions"]
                and scope["method"] == "GET"):
            try:
                session_id = str(uuid.UUID(parts[4]))
            except ValueError:
                return await self._send(send, 422, {"code": "invalid_session_reference"})
            try:
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                return await self._send(send, 200, self._operator_summary(session_id, loaded))
            except (ConversationSessionNotFound, IntentSessionNotFound):
                return await self._send(send, 404, {"code": "session_not_found"})
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
            if (len(parts) == 6 and parts[4] == "order" and parts[5] in ("status", "delay")
                    and method == "POST"):
                if self.store.load(session_id) is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                if parts[5] == "status":
                    return await self._advance_order_status(send, session_id, subject, body)
                return await self._set_order_delay(send, session_id, subject, body)
            if (len(parts) == 6 and parts[4] == "support" and parts[5] == "escalation"
                    and method == "POST"):
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._escalate_support(send, session_id, subject, loaded, body)
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
                try:
                    analysis = self.intent.analyze(
                        session_id=session_id, message_text=body.get("message_text"),
                        observed_context_version=result.context_version,
                        correlation_id=body.get("correlation_id"), subject_reference=subject)
                    context_version = analysis.context_version
                except Exception as error:
                    if not is_stale_context_error(error):
                        raise
                    # ADR-005: the message is already accepted; a newer T-02
                    # correction wins and the in-flight interpretation is dropped.
                    loaded = self.store.load(session_id)
                    context_version = (int(loaded["context_version"])
                                       if loaded else result.context_version)
                return await self._send(send, 202, {"code": "accepted",
                    "context_version": context_version, "message_id": result.message_id,
                    **self._assistant_fields()})
            if resource == "shared-understanding" and method == "GET":
                value = self.shared.projection(session_id=session_id)
                return await self._send(send, 200, {"context_version": value.context_version,
                    "structured_intent": value.structured_intent,
                    "suggestions": list(value.suggestions), **self._assistant_fields()})
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
            if resource == "delivery" and method == "POST":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._update_delivery(send, session_id, subject, loaded, body)
            if resource == "order" and method == "POST":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._create_order(send, session_id, loaded, body)
            if resource == "checkout" and method == "POST":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._checkout(send, session_id, subject, loaded, body)
            if resource == "support" and method == "POST":
                loaded = self.store.load(session_id)
                if loaded is None:
                    return await self._send(send, 404, {"code": "session_not_found"})
                body = await self._body(receive)
                return await self._answer_support(send, session_id, subject, loaded, body)
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
            "recommendations": {"items": self.recommendation.preview(
                intent=shared.structured_intent, session_id=session_id)},
        }
        decisions = state.get("decisions") or {}
        selection = decisions.get("product")
        if isinstance(selection, dict):
            facets["selection"] = selection
        delivery = decisions.get("delivery")
        if isinstance(delivery, dict):
            facets["delivery"] = delivery
        order_summary = self.pricing.summarize(decisions)
        if order_summary is not None:
            facets["order_summary"] = order_summary
        order = self.order.projection(session_id=session_id)
        if order is not None:
            delayed = bool(order.get("delayed"))
            facets["order"] = {"order_id": order["order_id"], "status": order["status"],
                               "delayed": delayed,
                               "authoritative_status": "delayed" if delayed else order["status"]}
        return {
            "context_version": int(loaded["context_version"]),
            "facets": facets,
            **self._assistant_fields(),
        }

    def _assistant_fields(self) -> dict:
        """NFR-005 honesty: disclosure matches last interpreter mode."""
        return disclosure_for_mode(getattr(self.interpreter, "last_mode", "reference"))

    def _operator_escalations(self, *, limit: int = 50) -> list[dict]:
        """Least-data Contact Florist inbox (FR-006 / T-09). Not a CRM ticket."""
        return self.support.store.list_escalations(limit=limit)

    def _operator_forecasts(self, session_id: str, loaded: dict, subject: str) -> dict:
        """Manager inventory trends from validated snapshot history (FR-012)."""
        result = self.forecast.recommend(
            session_id=session_id,
            context_version=int(loaded["context_version"]),
            correlation_id=str(uuid.uuid4()),
            subject_reference=subject,
        )
        return {
            "items": [{
                "product_id": item.product_id,
                "trend": item.trend,
                "recommendation": item.recommendation,
                "fact_references": list(item.fact_references),
            } for item in result.items],
            "message_id": result.message_id,
        }

    def _operator_summary(self, session_id: str, loaded: dict) -> dict:
        """Read-only florist view of one opaque session. No payment or raw PII."""
        workspace = self._workspace(session_id, loaded)
        facets = workspace.get("facets") or {}
        conversation = facets.get("conversation") or {}
        shared = facets.get("shared_understanding") or {}
        recommendations = facets.get("recommendations") or {}
        availability = []
        for item in recommendations.get("items") or []:
            if not isinstance(item, dict):
                continue
            availability.append({key: item[key] for key in
                                 ("product_id", "available", "availability_status")
                                 if key in item})
        answers = []
        list_fn = getattr(self.support.store, "list_session_answers", None)
        if callable(list_fn):
            answers = list_fn(session_id=session_id)
        return {
            "session_id": session_id,
            "context_version": workspace["context_version"],
            "conversation": {"messages": list(conversation.get("messages") or [])},
            "shared_understanding": {
                "structured_intent": dict(shared.get("structured_intent") or {})},
            "order": facets.get("order"),
            "selection": facets.get("selection"),
            "delivery": facets.get("delivery"),
            "availability": availability,
            "support_answers": answers,
        }

    async def _select_product(self, send, session_id: str, subject: str,
                              loaded: dict, body: dict):
        product_id = body.get("product_id")
        observed = body.get("observed_context_version")
        correlation_id = body.get("correlation_id")
        if (not isinstance(product_id, str) or not product_id.strip()
                or not isinstance(correlation_id, str) or not correlation_id.strip()):
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            # T-04 options (ADR-006 amended): size, card message, and thin FR-003
            # keys (flower_type, colour, ribbon). Unknown keys still rejected.
            options = normalize_selection_options(
                body.get("options"), product_id=product_id.strip())
        except SelectionValidationError:
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

    async def _advance_order_status(self, send, session_id: str, subject: str, body: dict):
        target_status = body.get("target_status")
        correlation_id = body.get("correlation_id")
        if (not isinstance(target_status, str) or target_status.strip() not in ORDER_STATUS_SEQUENCE
                or not isinstance(correlation_id, str) or not correlation_id.strip()):
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            # Authoritative fulfillment status advance (FR-015); order/operations
            # authority, not a customer action.
            result = self.order.advance_status(
                session_id=session_id, target_status=target_status.strip(),
                correlation_id=correlation_id.strip(), subject_reference=subject)
        except OrderNotFound:
            return await self._send(send, 404, {"code": "order_not_found"})
        except OrderStatusError:
            return await self._send(send, 409, {"code": "invalid_status_transition"})
        return await self._send(send, 202, {"code": "accepted",
            "order_id": result["order_id"], "status": result["status"]})

    async def _set_order_delay(self, send, session_id: str, subject: str, body: dict):
        delayed = body.get("delayed")
        correlation_id = body.get("correlation_id")
        if (not isinstance(delayed, bool)
                or not isinstance(correlation_id, str) or not correlation_id.strip()):
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            result = self.order.set_delay(
                session_id=session_id, delayed=delayed, correlation_id=correlation_id.strip(),
                subject_reference=subject)
        except OrderNotFound:
            return await self._send(send, 404, {"code": "order_not_found"})
        return await self._send(send, 202, {"code": "accepted", "order_id": result["order_id"],
            "order_status": result["status"], "delayed": result["delayed"],
            "authoritative_status": result["authoritative_status"]})

    async def _answer_support(self, send, session_id: str, subject: str,
                              loaded: dict, body: dict):
        correlation_id = body.get("correlation_id")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            result = self.support.answer(
                session_id=session_id, question=body.get("question"),
                correlation_id=correlation_id.strip(), subject_reference=subject,
                context_version=int(loaded["context_version"]),
                situation=self._support_situation(session_id, loaded))
        except SupportValidationError:
            return await self._send(send, 422, {"code": "validation_failed"})
        return await self._send(send, 200, {"code": "answered", "answer": result["answer"],
            "approved_source_references": result.get("approved_source_references", []),
            "matched": result["matched"], "kind": result.get("kind", "faq"),
            "fact_references": result.get("fact_references", [])})

    def _support_situation(self, session_id: str, loaded: dict) -> dict:
        """Least-data session facts for FR-010 situational answers."""
        state = loaded.get("state") or {}
        decisions = state.get("decisions") or {}
        selection = decisions.get("product") if isinstance(decisions.get("product"), dict) else None
        delivery = decisions.get("delivery") if isinstance(decisions.get("delivery"), dict) else None
        order = self.order.projection(session_id=session_id)
        order_facet = None
        if order is not None:
            delayed = bool(order.get("delayed"))
            order_facet = {
                "order_id": order["order_id"], "status": order["status"],
                "delayed": delayed,
                "authoritative_status": "delayed" if delayed else order["status"],
            }
        availability = {}
        product_ids = []
        if isinstance(selection, dict) and selection.get("product_id"):
            product_ids.append(selection["product_id"])
        from .recommendation import REFERENCE_CATALOG
        product_ids.extend(product.product_id for product in REFERENCE_CATALOG)
        try:
            availability = self.inventory.availability(product_ids=product_ids)
        except InventoryValidationError:
            availability = {}
        return {"order": order_facet, "delivery": delivery, "selection": selection,
                "availability": availability}

    async def _escalate_support(self, send, session_id: str, subject: str,
                                loaded: dict, body: dict):
        if not isinstance(body, dict) or set(body) - {"reason", "correlation_id"}:
            return await self._send(send, 422, {"code": "validation_failed"})
        correlation_id = body.get("correlation_id")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            result = self.support.escalate(
                session_id=session_id, reason=body.get("reason"),
                correlation_id=correlation_id.strip(), subject_reference=subject,
                context_version=int(loaded["context_version"]))
        except SupportValidationError:
            return await self._send(send, 422, {"code": "validation_failed"})
        return await self._send(send, 202, {
            "code": result["code"], "accepted": True,
            "message_id": result["message_id"],
            "acknowledgement": result["acknowledgement"],
            "escalation_reason": result["escalation_reason"],
        })

    def _ensure_precheckout_order(self, session_id: str, loaded: dict) -> None:
        """Create the FR-013 order from assembled decisions when checkout runs first."""
        if self.order.projection(session_id=session_id) is not None:
            return
        decisions = (loaded.get("state") or {}).get("decisions") or {}
        self.order.create(
            session_id=session_id, decisions=decisions,
            context_version=int(loaded["context_version"]))

    async def _checkout(self, send, session_id: str, subject: str, loaded: dict, body: dict):
        correlation_id = body.get("correlation_id")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            self._ensure_precheckout_order(session_id, loaded)
        except OrderIncompleteError as error:
            return await self._send(send, 422, {"code": "order_incomplete",
                                               "missing": error.missing})
        try:
            submitted = self.checkout.submit(
                session_id=session_id, payment_reference=body.get("payment_reference"),
                observed_total=body.get("observed_total"), correlation_id=correlation_id.strip(),
                subject_reference=subject)
        except OrderNotFound:
            return await self._send(send, 404, {"code": "order_not_found"})
        except CheckoutTotalMismatch:
            return await self._send(send, 409, {"code": "total_mismatch"})
        except CheckoutStateError:
            return await self._send(send, 409, {"code": "checkout_conflict"})
        except PaymentValidationError:
            return await self._send(send, 422, {"code": "validation_failed"})
        envelope = {
            "message_id": submitted["message_id"], "topic": "order.checkout.requested",
            "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": submitted["correlation_id"], "source": "orchestration",
            "context_version": submitted["context_version"],
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential",
                                 "subject_reference": submitted["subject_reference"]},
            "payload": {"draft_order_id": submitted["order_id"], "total": submitted["total"]},
            "outcome": {},
        }
        # Reference path: dispatch the payment consumer in-process after submit so
        # authorization never runs inside CheckoutService (#148). Kafka workers use
        # the same PaymentCheckoutHandler via GovernedConsumer.
        try:
            self._dispatch_payment_checkout(envelope)
        except Exception:
            # Submission already committed; leave pending for a payment consumer retry.
            pass
        order = self.order.projection(session_id=session_id) or {}
        intent = self.order_store.load_checkout_intent(submitted["order_id"])
        decline_code = intent.get("decline_code") if intent else None
        return await self._send(send, 202, {
            "code": "accepted", "pending": True,
            "order_id": submitted["order_id"],
            "order_status": order.get("status", "submitted"),
            "decline_code": decline_code,
        })

    def _dispatch_payment_checkout(self, envelope: dict) -> None:
        from pathlib import Path

        from .adapters import PsycopgConsumerTransaction
        from .consumer import ConsumedRecord, GovernedConsumer
        from .policy import KafkaPolicy
        from .privacy import PayloadPrivacyGuard

        root = Path(__file__).resolve().parents[1]
        policy = KafkaPolicy.load(root / "config" / "kafka-policy.json")
        schemas = root.parent / "docs" / "04-technical-architecture" / "schemas"
        governed = GovernedConsumer(
            "payment", PsycopgConsumerTransaction(self.connection), _InProcessOffsets(),
            _InProcessFailures(), PayloadPrivacyGuard(policy, schemas))
        governed.process(
            ConsumedRecord("order.checkout.requested", 0, 0, envelope),
            self.payment_handler.handle_checkout_requested)

    async def _create_order(self, send, session_id: str, loaded: dict, body: dict):
        correlation_id = body.get("correlation_id")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            return await self._send(send, 422, {"code": "validation_failed"})
        decisions = (loaded.get("state") or {}).get("decisions") or {}
        try:
            # An order requires the assembled product (#142/#122) and delivery (#33)
            # decisions; it is a separate authoritative aggregate (pre-checkout).
            result = self.order.create(session_id=session_id, decisions=decisions,
                                       context_version=int(loaded["context_version"]))
        except OrderIncompleteError as error:
            return await self._send(send, 422, {"code": "order_incomplete", "missing": error.missing})
        return await self._send(send, 202, {"code": "accepted",
            "order_id": result["order_id"], "order_status": result["status"]})

    async def _update_delivery(self, send, session_id: str, subject: str,
                               loaded: dict, body: dict):
        observed = body.get("observed_context_version")
        correlation_id = body.get("correlation_id")
        if (not isinstance(correlation_id, str) or not correlation_id.strip()
                or not isinstance(observed, int) or isinstance(observed, bool) or observed < 0):
            return await self._send(send, 422, {"code": "validation_failed"})
        try:
            # Reference-only recipient data (FR-014); raw PII is rejected.
            details = normalize_delivery_details(body.get("delivery"))
        except DeliveryValidationError:
            return await self._send(send, 422, {"code": "validation_failed"})
        message_id = str(uuid.uuid4())
        envelope = {
            "message_id": message_id, "topic": "delivery.details.updated",
            "message_type": "event", "schema_version": "1.0.0", "session_id": session_id,
            "correlation_id": correlation_id.strip(), "source": "orchestration",
            "context_version": observed,
            "publication_time": datetime.now(timezone.utc).isoformat(),
            "security_context": {"classification": "confidential", "subject_reference": subject},
            "payload": details, "outcome": {},
        }
        patch = StatePatch.create({"decisions": {"delivery": details}}, ["decisions.delivery"])
        try:
            new_version = self.store.apply_patch(
                session_id, observed, int(loaded["state_schema_version"]), patch,
                [{"message_id": message_id, "topic": "delivery.details.updated",
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
