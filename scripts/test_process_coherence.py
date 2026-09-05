import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from check_process_coherence import (
    changed_paths,
    ci_git_changed_paths,
    evaluate,
    evaluate_live,
    parse_git_name_status,
)

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_process_coherence.py"
FIXTURES = ROOT / "scripts" / "fixtures" / "process_coherence"


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

    def test_closing_issue_accepts_trailing_period(self):
        mr = self.mr("Closes #10.\n\n## Validation:\n- coherence guard")
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

    def test_deleted_code_path_still_requires_integration_evidence(self):
        mr = self.mr("Closes #10\n\nValidation: unit tests")
        mr["changes"] = [{"old_path": "platform/removed.py", "new_path": "platform/removed.py"}]
        findings = evaluate(mr, changed_paths(mr))
        self.assertTrue(any("integration" in finding for finding in findings))

    def test_rename_out_of_code_path_still_requires_integration_evidence(self):
        mr = self.mr("Closes #10\n\nValidation: docs")
        mr["changes"] = [{"old_path": "edge/legacy.py", "new_path": "docs/legacy.md"}]
        self.assertIn("edge/legacy.py", changed_paths(mr))
        findings = evaluate(mr, changed_paths(mr))
        self.assertTrue(any("integration" in finding for finding in findings))

    def test_live_diffs_preserve_old_and_new_paths(self):
        mr = self.mr("Closes #10\n\nValidation: unit tests")
        diffs = [{"old_path": "edge/legacy.py", "new_path": "docs/legacy.md"}]
        with patch("check_process_coherence.ci_git_changed_paths", return_value=None):
            with patch("check_process_coherence.gitlab_api", return_value=diffs) as api:
                paths = changed_paths(mr)
        self.assertEqual(["docs/legacy.md", "edge/legacy.py"], paths)
        api.assert_called_once_with(
            "merge_requests/10/diffs", {"per_page": 100, "page": 1}
        )

    def test_live_diffs_404_does_not_block_when_description_is_valid(self):
        mr = self.mr("Closes #10\n\nValidation: unit tests")
        error = HTTPError(
            "https://gitlab.example/api/v4/projects/1/merge_requests/10/diffs",
            404,
            "Not Found",
            None,
            None,
        )
        with patch("check_process_coherence.gitlab_api", side_effect=error):
            with patch("check_process_coherence.ci_git_changed_paths", return_value=None):
                findings = evaluate_live(mr)
        self.assertEqual([], findings)

    def test_git_name_status_keeps_rename_old_and_new_paths(self):
        output = "R100\tedge/legacy.py\tdocs/legacy.md\nM\tdocs/example.md\n"
        self.assertEqual(
            ["docs/example.md", "docs/legacy.md", "edge/legacy.py"],
            parse_git_name_status(output),
        )

    def test_ci_git_changed_paths_reads_mr_base_and_head(self):
        env = {
            "CI_MERGE_REQUEST_DIFF_BASE_SHA": "abc",
            "CI_COMMIT_SHA": "def",
        }
        with patch.dict("os.environ", env, clear=False):
            with patch("check_process_coherence.subprocess.check_output", return_value="A\tplatform/x.py\n") as git:
                paths = ci_git_changed_paths()
        self.assertEqual(["platform/x.py"], paths)
        git.assert_called_once()

    def test_evaluate_live_uses_git_paths_for_integration_rule(self):
        mr = self.mr("Closes #10\n\nValidation: unit tests")
        with patch("check_process_coherence.ci_git_changed_paths", return_value=["platform/x.py"]):
            findings = evaluate_live(mr)
        self.assertTrue(any("integration" in finding for finding in findings))

    def test_live_non_404_diffs_error_is_not_hidden(self):
        mr = self.mr("Closes #10\n\nValidation: unit tests")
        error = HTTPError(
            "https://gitlab.example/api/v4/projects/1/merge_requests/10/diffs",
            403,
            "Forbidden",
            None,
            None,
        )
        with patch("check_process_coherence.ci_git_changed_paths", return_value=None):
            with patch("check_process_coherence.gitlab_api", side_effect=error):
                with self.assertRaises(HTTPError):
                    evaluate_live(mr)

    def _run_fixture(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--fixture", str(FIXTURES / name)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_known_bad_fixture_fails(self):
        result = self._run_fixture("known_bad.json")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PROCESS COHERENCE FINDINGS", result.stdout)
        self.assertIn("exactly one closing issue", result.stdout)
        self.assertIn("unknown Process-Exception", result.stdout)
        self.assertIn("lacks a Validation section", result.stdout)
        self.assertIn("named Process-Exception", result.stdout)

    def test_clean_baseline_fixture_passes(self):
        result = self._run_fixture("clean_baseline.json")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("ok: falsifiable MR process-coherence evidence is present", result.stdout)

    def test_named_exception_fixture_passes(self):
        result = self._run_fixture("named_exception.json")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("ok: falsifiable MR process-coherence evidence is present", result.stdout)


if __name__ == "__main__":
    unittest.main()
