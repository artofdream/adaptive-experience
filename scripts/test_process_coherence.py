import unittest

from check_process_coherence import evaluate


class ProcessCoherenceTests(unittest.TestCase):
    def mr(self, description: str, **overrides):
        value = {
            "iid": 10,
            "source_branch": "codex/10-example",
            "target_branch": "main",
            "description": description,
        }
        value.update(overrides)
        return value

    def test_docs_mr_with_one_issue_and_validation_passes(self):
        mr = self.mr("Closes #10\n\n## Validation:\n- coherence guard")
        self.assertEqual([], evaluate(mr, ["docs/example.md"]))

    def test_code_mr_requires_integration_evidence(self):
        mr = self.mr("Closes #10\n\n## Validation:\n- unit tests")
        findings = evaluate(mr, ["platform/example.py"])
        self.assertTrue(any("integration" in finding for finding in findings))

    def test_code_mr_accepts_named_integration_evidence(self):
        mr = self.mr(
            "Closes #10\n\n## Validation:\n- unit tests\n"
            "Integration evidence: platform integration suite passed"
        )
        self.assertEqual([], evaluate(mr, ["platform/example.py"]))

    def test_multiple_closing_issues_fail(self):
        mr = self.mr("Closes #10\nCloses #11\n\nValidation: docs only")
        self.assertTrue(any("exactly one" in finding for finding in evaluate(mr, [])))

    def test_recurring_report_exception_passes_without_issue(self):
        mr = self.mr(
            "Process-Exception: recurring-report\n\nValidation: deterministic report generation"
        )
        self.assertEqual([], evaluate(mr, ["research/daily-briefs/2026-08-18.md"]))

    def test_unknown_exception_fails(self):
        mr = self.mr("Process-Exception: skip-all\n\nValidation: none")
        self.assertTrue(any("unknown" in finding for finding in evaluate(mr, [])))


if __name__ == "__main__":
    unittest.main()
