from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable

# Order status lifecycle: creation, checkout submission, payment confirmation
# (M5), then FR-015/FR-023 fulfillment through completion. Status only moves
# forward along this sequence; `delayed` is an orthogonal flag (FR-023).
ORDER_STATUS_SEQUENCE = ("created", "submitted", "confirmed", "preparing",
                         "dispatched", "delivered", "completed")

# Accepted checkout or later. Draft ``created`` rows do not hint T-03.
PRIOR_ORDER_HINT_STATUSES = frozenset(
    ORDER_STATUS_SEQUENCE[ORDER_STATUS_SEQUENCE.index("submitted"):])


class OrderIncompleteError(RuntimeError):
    """A required T-04/T-05 decision is missing, so no order can be created."""

    def __init__(self, missing: str):
        super().__init__(missing)
        self.missing = missing


class OrderNotFound(RuntimeError):
    """No order exists for the session."""


class OrderStatusError(ValueError):
    """An order status transition is not a valid forward move (FR-015)."""


class CheckoutStateError(RuntimeError):
    """The order is not in a checkoutable state (unpriced or already confirmed)."""


class CheckoutTotalMismatch(ValueError):
    """The observed total does not match the authoritative order total."""


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

    def session_prior_product_id(self, session_id: str) -> str | None:
        """Same-session accepted-order product for the thin FR-008 T-03 hint.

        Returns a catalog product_id only when this session already has an
        order at submitted or later. Draft ``created`` rows, missing views,
        and malformed product payloads return None. Not cross-session CRM.
        """
        if not isinstance(session_id, str) or not session_id.strip():
            return None
        view = self.store.checkout_view(session_id.strip())
        if not isinstance(view, dict):
            return None
        if view.get("status") not in PRIOR_ORDER_HINT_STATUSES:
            return None
        product = view.get("product")
        if not isinstance(product, dict):
            return None
        product_id = product.get("product_id")
        if not isinstance(product_id, str) or not product_id.strip():
            return None
        return product_id.strip()

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

    def set_delay(self, *, session_id: str, delayed: bool, correlation_id: str,
                  subject_reference: str) -> dict:
        """Set or clear the delay flag and publish the authoritative state (FR-023).

        Delay is orthogonal to the linear status: while set, the published and
        displayed authoritative state is ``delayed``; clearing it republishes the
        current linear status.
        """
        result = self.store.set_delay(
            session_id=session_id, delayed=bool(delayed), message_id=str(self.new_id()),
            correlation_id=correlation_id, subject_reference=subject_reference,
            published_at=self.now().astimezone(timezone.utc))
        if result is None:
            raise OrderNotFound(session_id)
        return result


class CheckoutService:
    """Async-ready checkout submission (FR-019 / #148).

    Price-checks the assembled order, stores a private payment intent, and emits
    ``order.checkout.requested``. Authorization runs in the payment consumer
    (``PaymentCheckoutHandler``), not on this request path.
    """

    def __init__(self, store, pricing, *,
                 new_id: Callable[[], uuid.UUID] | None = None, now=None):
        self.store = store
        self.pricing = pricing
        self.new_id = new_id or uuid.uuid4
        self.now = now or (lambda: datetime.now(timezone.utc))

    def submit(self, *, session_id: str, payment_reference: str, observed_total,
               correlation_id: str, subject_reference: str) -> dict:
        from .payment import normalize_payment_reference
        reference = normalize_payment_reference(payment_reference)
        view = self.store.checkout_view(session_id)
        if view is None:
            raise OrderNotFound(session_id)
        if view["status"] not in ("created", "submitted"):
            raise CheckoutStateError(view["status"])
        summary = self.pricing.summarize({"product": view["product"], "delivery": view["delivery"]})
        if summary is None:
            raise CheckoutStateError("unpriced")
        total = summary["total"]
        if (isinstance(observed_total, bool) or not isinstance(observed_total, (int, float))
                or round(float(observed_total), 2) != total):
            raise CheckoutTotalMismatch()
        published_at = self.now().astimezone(timezone.utc)
        message_id = str(self.new_id())
        if not self.store.request_checkout(
                session_id=session_id, order_id=view["order_id"], total=total,
                payment_reference=reference, message_id=message_id,
                correlation_id=correlation_id, subject_reference=subject_reference,
                published_at=published_at, context_version=view["context_version"]):
            raise CheckoutStateError("not_submittable")
        return {
            "accepted": True,
            "pending": True,
            "order_id": view["order_id"],
            "status": "submitted",
            "message_id": message_id,
            "context_version": view["context_version"],
            "total": total,
            "correlation_id": correlation_id,
            "subject_reference": subject_reference,
        }

    # Back-compat alias used by older call sites during the #148 cutover.
    def checkout(self, **kwargs):
        return self.submit(**kwargs)
