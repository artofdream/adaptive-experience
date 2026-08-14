from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable

from .payment import PaymentAuthority, PaymentOutcome, PaymentValidationError, normalize_payment_reference


class PaymentCheckoutHandler:
    """Authorize checkout in the payment consumer path (#148).

    Consumes ``order.checkout.requested``, loads the private checkout intent
    (payment_reference never rides the bus), authorizes via ``PaymentAuthority``,
    then either confirms the order or records a decline. Retry/DLQ wrap this
    handler through ``GovernedConsumer``.
    """

    def __init__(self, store, payment: PaymentAuthority, *,
                 new_id: Callable[[], uuid.UUID] | None = None,
                 now: Callable[[], datetime] | None = None):
        self.store = store
        self.payment = payment
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def handle_checkout_requested(self, envelope: dict) -> PaymentOutcome:
        payload = envelope.get("payload") or {}
        draft_order_id = payload.get("draft_order_id")
        total = payload.get("total")
        if not isinstance(draft_order_id, str) or not draft_order_id.strip():
            raise PaymentValidationError("draft_order_id is required")
        intent = self.store.load_checkout_intent(draft_order_id.strip())
        if intent is None:
            raise PaymentValidationError("checkout intent is missing")
        if (isinstance(total, bool) or not isinstance(total, (int, float))
                or round(float(total), 2) != round(float(intent["total"]), 2)):
            raise PaymentValidationError("checkout total mismatch")
        published_at = self.now().astimezone(timezone.utc)
        outcome = self.payment.authorize(
            payment_reference=intent["payment_reference"], total=float(intent["total"]))
        if outcome.authorized:
            self.store.record_authorization_succeeded(
                session_id=intent["session_id"], order_id=intent["order_id"],
                message_id=str(self.new_id()), correlation_id=intent["correlation_id"],
                subject_reference=intent["subject_reference"], published_at=published_at,
                context_version=intent["context_version"])
            if not self.store.confirm(
                    session_id=intent["session_id"], order_id=intent["order_id"],
                    message_id=str(self.new_id()), correlation_id=intent["correlation_id"],
                    subject_reference=intent["subject_reference"], published_at=published_at,
                    context_version=intent["context_version"]):
                raise RuntimeError("order not confirmable after authorization")
            self.store.clear_checkout_intent(intent["order_id"])
        else:
            self.store.record_authorization_failed(
                session_id=intent["session_id"], order_id=intent["order_id"],
                decline_code=outcome.decline_code or "declined",
                message_id=str(self.new_id()), correlation_id=intent["correlation_id"],
                subject_reference=intent["subject_reference"], published_at=published_at,
                context_version=intent["context_version"])
        return outcome
