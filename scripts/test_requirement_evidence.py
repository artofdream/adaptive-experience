import copy
import unittest

from check_requirement_evidence import validate
from generate_requirement_evidence import adr_related_ids, build


class RequirementEvidenceTests(unittest.TestCase):
    def test_generated_inventory_is_valid(self):
        self.assertEqual([], validate(build()))

    def test_missing_requirement_is_rejected(self):
        data = build()
        data["records"].pop()
        self.assertTrue(any("inventory mismatch" in error for error in validate(data)))

    def test_evidenced_without_path_is_rejected(self):
        data = copy.deepcopy(build())
        data["records"][0]["adr"] = {"disposition": "evidenced", "paths": []}
        self.assertTrue(any("requires" in error for error in validate(data)))

    def test_false_path_is_rejected(self):
        data = copy.deepcopy(build())
        data["records"][0]["implementation"] = {"disposition": "evidenced", "paths": ["platform/does-not-exist.py"]}
        self.assertTrue(any("missing path" in error for error in validate(data)))

    def test_adr_parser_accepts_wrapped_related_requirements(self):
        text = (
            "# ADR-999\n\nStatus: Proposed\n\n"
            "Related requirements: FR-001, NFR-005,\n"
            "NFR-006\n\nRelated architecture: example.md\n"
        )
        self.assertEqual({"FR-001", "NFR-005", "NFR-006"}, adr_related_ids(text))

    def test_adr_parser_rejects_ids_outside_related_requirements(self):
        text = (
            "# ADR-999 for FR-023\n\nStatus: Proposed\n\n"
            "Related requirements: FR-001\n"
            "(Consequential execution ties: FR-019, NFR-017)\n"
        )
        self.assertEqual({"FR-001"}, adr_related_ids(text))


if __name__ == "__main__":
    unittest.main()
