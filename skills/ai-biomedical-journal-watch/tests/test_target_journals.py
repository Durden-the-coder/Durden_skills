from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "target_journal_enrichment.json"


class TargetJournalRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        cls.records = {row["doi"]: row for row in payload["records"]}

    def test_nature_methods_official_pages_supply_bounded_evidence(self):
        for doi in ("10.1038/s41592-026-03186-8", "10.1038/s41592-026-03174-y"):
            row = self.records[doi]
            self.assertEqual(row["recommended_decision"], "screenable")
            self.assertEqual(row["screening_evidence"]["source"], "publisher")
            evidence_length = len(row["screening_evidence"]["abstract"])
            self.assertGreaterEqual(evidence_length, 100)
            self.assertLess(evidence_length, 5000)
            self.assertIn("nature.com/articles/", row["sources"]["publisher"]["final_url"])

    def test_cell_metabolism_missing_abstracts_are_errata(self):
        expected_targets = {
            "10.1016/j.cmet.2026.07.017": "27773696",
            "10.1016/j.cmet.2026.07.013": "39146936",
        }
        for doi, corrected_pmid in expected_targets.items():
            row = self.records[doi]
            self.assertTrue(row["non_research_type"])
            self.assertEqual(row["recommended_decision"], "exclude_non_research_type")
            self.assertIn("Published Erratum", row["sources"]["europe_pmc"]["publication_types"])
            corrections = row["sources"]["europe_pmc"]["corrections"]
            self.assertEqual(corrections[0]["id"], corrected_pmid)


if __name__ == "__main__":
    unittest.main()

