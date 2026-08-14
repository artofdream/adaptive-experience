from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aea_platform.workspace_handlers import (  # noqa: E402
    ORDER_STREAM_TOPICS,
    WorkspaceOrderInvalidationHandler,
)


class FakeExperienceStore:
    def __init__(self):
        self.calls = []

    def invalidate_projection(self, session_id, *, projection_key, reason):
        self.calls.append({
            "session_id": session_id,
            "projection_key": projection_key,
            "reason": reason,
        })
        return len(self.calls)


class WorkspaceOrderInvalidationHandlerTests(unittest.TestCase):
    def test_status_updated_invalidates_order_facet(self):
        store = FakeExperienceStore()
        handler = WorkspaceOrderInvalidationHandler(store)
        handler({
            "topic": "order.status.updated",
            "session_id": "sess-1",
            "payload": {"order_id": "ord-1", "authoritative_status": "preparing"},
        })
        self.assertEqual([{
            "session_id": "sess-1",
            "projection_key": "order",
            "reason": "order_status_updated",
        }], store.calls)

    def test_confirmed_uses_distinct_reason(self):
        store = FakeExperienceStore()
        WorkspaceOrderInvalidationHandler(store)({
            "topic": "order.confirmed",
            "session_id": "sess-2",
        })
        self.assertEqual("order_confirmed", store.calls[0]["reason"])

    def test_ignores_unrelated_topics_and_blank_sessions(self):
        store = FakeExperienceStore()
        handler = WorkspaceOrderInvalidationHandler(store)
        handler({"topic": "support.faq.answered", "session_id": "sess-3"})
        handler({"topic": "order.status.updated", "session_id": "  "})
        handler({"topic": "order.status.updated"})
        self.assertEqual([], store.calls)

    def test_order_stream_topics_are_explicit(self):
        self.assertEqual({"order.status.updated", "order.confirmed"}, ORDER_STREAM_TOPICS)


if __name__ == "__main__":
    unittest.main()
