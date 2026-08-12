import unittest

from edge.bff.aea_bff.orchestration import HttpOrchestration, OrchestrationUnavailable
from edge.bff.aea_bff.ports import CommandResult


class HttpOrchestrationTests(unittest.TestCase):
    def test_propagates_identity_correlation_and_context(self):
        calls = []
        def transport(method, url, headers, payload, timeout):
            calls.append((method, url, headers, payload))
            return 202, '{"code":"accepted","context_version":4,"message_id":"m1"}'
        adapter = HttpOrchestration("http://orchestration:8081", "internal", transport=transport)
        result = adapter.submit_conversation_message(
            session_id="s1", subject="user1", message_text="roses",
            observed_context_version=3, correlation_id="c1")
        self.assertTrue(result.accepted)
        self.assertEqual(4, result.context_version)
        self.assertEqual("user1", calls[0][2]["x-subject-reference"])
        self.assertEqual("c1", calls[0][3]["correlation_id"])

    def test_dependency_failure_is_fail_closed(self):
        def transport(*_): raise TimeoutError()
        adapter = HttpOrchestration("http://orchestration:8081", "internal", transport=transport)
        with self.assertRaises(OrchestrationUnavailable):
            adapter.conversation_projection(session_id="s1", subject="user1")

    def test_command_stays_deferred_without_calling_internal(self):
        calls = []
        def transport(*args):
            calls.append(args)
            return 500, "{}"
        adapter = HttpOrchestration("http://orchestration:8081", "internal", transport=transport)
        command = adapter.accept_command(
            session_id="s1", subject="user1", command={"type": "continue"},
            observed_context_version=1, correlation_id="c1")
        self.assertEqual(CommandResult(False, "orchestration_unavailable"), command)
        self.assertEqual([], calls)

    def test_select_product_posts_to_internal_selection(self):
        calls = []
        def transport(method, url, headers, payload, timeout):
            calls.append((method, url, payload, headers))
            return 202, '{"code":"accepted","context_version":9,"message_id":"sel-1"}'
        adapter = HttpOrchestration("http://orchestration:8081", "internal", transport=transport)
        result = adapter.select_product(
            session_id="s1", subject="user1", product_id="rose",
            options={"card_message": "hi"}, observed_context_version=8, correlation_id="c1")
        self.assertTrue(result.accepted)
        self.assertEqual(9, result.context_version)
        self.assertEqual("sel-1", result.message_id)
        self.assertEqual("POST", calls[0][0])
        self.assertTrue(calls[0][1].endswith("/sessions/s1/selection"))
        self.assertEqual("rose", calls[0][2]["product_id"])
        self.assertEqual("c1", calls[0][2]["correlation_id"])
        self.assertEqual("user1", calls[0][3]["x-subject-reference"])

    def test_workspace_and_stream_reach_internal_with_identity(self):
        calls = []
        def transport(method, url, headers, payload, timeout):
            calls.append((method, url, headers))
            if url.endswith("/workspace"):
                return 200, '{"context_version":5,"facets":{},"ai_generated":true}'
            return 200, ('{"events":[{"event_id":"5","context_version":5,"kind":"invalidation",'
                         '"invalidated_projections":[{"projection_key":"recommendations","reason":"intent_changed"}]}]}')
        adapter = HttpOrchestration("http://orchestration:8081", "internal", transport=transport)
        workspace = adapter.workspace_projection(session_id="s1", subject="user1")
        events = list(adapter.stream_events(session_id="s1", subject="user1", after_event_id="3"))
        self.assertEqual(5, workspace["context_version"])
        self.assertEqual("5", events[0]["event_id"])
        self.assertEqual("recommendations", events[0]["invalidated_projections"][0]["projection_key"])
        self.assertTrue(any(url.endswith("/sessions/s1/workspace") for _, url, _ in calls))
        self.assertTrue(any(url.endswith("/sessions/s1/stream?after=3") for _, url, _ in calls))
        self.assertTrue(all(headers["x-subject-reference"] == "user1" for _, _, headers in calls))
