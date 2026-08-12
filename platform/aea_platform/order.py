from __future__ import annotations

import uuid
from typing import Callable


class OrderIncompleteError(RuntimeError):
    """A required T-04/T-05 decision is missing, so no order can be created."""

    def __init__(self, missing: str):
        super().__init__(missing)
        self.missing = missing


class OrderService:
    """Assemble a customer order from completed decisions (FR-013).

    M4 scope is order *creation* from the product selection (#142/#122) and the
    delivery decision (#33). Checkout, payment, and confirmation are M5. Creation
    is idempotent per session: a session has at most one order.
    """

    def __init__(self, store, *, new_id: Callable[[], uuid.UUID] | None = None):
        self.store = store
        self.new_id = new_id or uuid.uuid4

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
