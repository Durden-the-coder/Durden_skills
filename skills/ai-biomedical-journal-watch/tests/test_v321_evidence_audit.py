from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_evidence_v321", ROOT / "scripts" / "audit_reviewed_jsonl.py")
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)


def included(abstract: str, article_type: str = "Journal Article") -> dict:
    return {"work_id": "x", "doi": "10.1/x", "date": "2026-07-01", "article_type": article_type, "status": "include", "evidence_urls": ["https://example.org"], "summary_cn": "摘要", "importance_cn": "意义", "_abstract": abstract}


class EvidenceAuditTests(unittest.TestCase):
    def test_database_journal_article_cannot_hide_review(self):
        row = included("In this Review, we examine AI models in genomics. " + "evidence " * 40)
        result = AUDIT.audit([row])
        self.assertTrue(any("identifies review" in item for item in result["errors"]))

    def test_short_commentary_abstract_is_not_original_research(self):
        row = included("Generative artificial intelligence can scale psychotherapy.")
        result = AUDIT.audit([row])
        self.assertTrue(any("sufficient abstract" in item for item in result["errors"]))

    def test_substantive_original_research_passes(self):
        row = included("We trained and externally evaluated a neural network on clinical images. " + "Methods and results support model evaluation. " * 10)
        self.assertEqual(AUDIT.audit([row])["errors"], [])


if __name__ == "__main__":
    unittest.main()

