from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable

# FR-015 authoritative order status lifecycle: creation through delivery. Status
# only moves forward along this sequence.
ORDER_STATUS_SEQUENCE = ("created", "submitted", "preparing", "dispatched", "delivered")


class OrderIncompleteError(RuntimeError):
    """A required T-04/T-05 decision is missing, so no order can be created."""

    def __init__(self, missing: str):
        super().__init__(missing)
        self.missing = missing


class OrderNotFound(RuntimeError):
    """No order exists for the session."""


class OrderStatusError(ValueError):
    """An order status transition is not a valid forward move (FR-015)."""


class OrderService:
    """Assemble a customer order from completed decisions (FR-013).

    M4 scope is order *creation* from the product selection (#142/#122) and the
    delivery decision (#33). Checkout, payment, and confirmation are M5. Creation
    is idempotent per session: a session has at most one order.
    """

    def __init__(self, store, *, new_id: Callable[[], uuid.UUID] | None = None,
                 now: Callable[[], datetime] | None = None):
        self.store = store
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def create(self, *, session_id: str, decisions: dict, context_version: int) -> dict:
        product = decisions.get("product") if isinstance(decisions, dict) else None
        delivery = decisions.get("delivery") if isinstance(decisions, dict) else None
        if not isinstance(product, dict) or not product.get("product_id"):
            raise OrderIncompleteError("product")
        if not isinstance(delivery, dict) or not delivery.get("destination_reference"):
            raise OrderIncompleteError("delivery")
        return self.store.create_or_get(
            session_id=session_id, order_id=str(self.new_id()),
            context_version=context_version, product=product, delivery=delivery)

    def projection(self, *, session_id: str) -> dict | None:
        return self.store.by_session(session_id)

    def advance_status(self, *, session_id: str, target_status: str,
                       correlation_id: str, subject_reference: str) -> dict:
        """Move the order forward to an authoritative status and publish it (FR-015).

        Forward-only: ``target_status`` must be later in ``ORDER_STATUS_SEQUENCE``
        than the current status. The status update and the governed
        ``order.status.updated`` event commit together.
        """
        if target_status not in ORDER_STATUS_SEQUENCE:
            raise OrderStatusError(f"unknown status: {target_status}")
        allowed_priors = ORDER_STATUS_SEQUENCE[:ORDER_STATUS_SEQUENCE.index(target_status)]
        result = self.store.advance_status(
            session_id=session_id, target_status=target_status,
            allowed_priors=allowed_priors, message_id=str(self.new_id()),
            correlation_id=correlation_id, subject_reference=subject_reference,
            published_at=self.now().astimezone(timezone.utc))
        if result is None:
            raise OrderNotFound(session_id)
        if not result["changed"]:
            raise OrderStatusError(
                f"cannot move from {result['status']} to {target_status}")
        return result
