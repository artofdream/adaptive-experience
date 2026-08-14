from __future__ import annotations

"""Workspace projection handlers for governed Kafka consumption (NFR-011).

Order status remains authoritative on ``customer_order``. These handlers bump
experience ``context_version`` and record an ``order`` invalidation so the
browser SSE stream can refresh T-08 without a user-triggered workspace pull.
"""


ORDER_STREAM_TOPICS = frozenset({"order.status.updated", "order.confirmed"})


class WorkspaceOrderInvalidationHandler:
    """Invalidate the workspace ``order`` facet from order lifecycle events."""

    def __init__(self, store):
        self.store = store

    def __call__(self, envelope: dict) -> None:
        self.handle(envelope)

    def handle(self, envelope: dict) -> None:
        topic = envelope.get("topic")
        if topic not in ORDER_STREAM_TOPICS:
            return
        session_id = envelope.get("session_id")
        if not isinstance(session_id, str) or not session_id.strip():
            return
        reason = "order_confirmed" if topic == "order.confirmed" else "order_status_updated"
        self.store.invalidate_projection(
            session_id.strip(), projection_key="order", reason=reason)
