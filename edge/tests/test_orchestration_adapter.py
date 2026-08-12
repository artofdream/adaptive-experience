import unittest

from edge.bff.aea_bff.orchestration import HttpOrchestration, OrchestrationUnavailable


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
