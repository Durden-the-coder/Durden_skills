from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RENDER = load_module("render_v321", ROOT / "scripts" / "render_report_v321.py")
AUDIT = load_module("audit_v321", ROOT / "scripts" / "audit_reviewed_jsonl.py")


class V321RegressionTests(unittest.TestCase):
    def test_window_limits(self):
        self.assertEqual(RENDER.index_limit_for_window("96h"), 30)
        self.assertEqual(RENDER.index_limit_for_window("7d"), 50)
        self.assertEqual(RENDER.index_limit_for_window("30d"), 80)
        self.assertEqual(RENDER.index_limit_for_window("45d"), 80)

    def test_exclusion_reasons_are_bounded(self):
        report = "# x\n\n## 排除汇总\n\n" + "\n".join(f"- reason-{i}: 1" for i in range(15)) + "\n"
        bounded = RENDER.bound_exclusion_reasons(report, 10)
        self.assertIn("另有 5 类", bounded)
        self.assertNotIn("reason-14", bounded)

    def test_audit_blocks_context_types_and_unsupported_letters(self):
        base = {"work_id": "x", "doi": "", "date": "2026-07-01", "evidence_urls": ["https://example.org"], "summary_cn": "摘要", "importance_cn": "意义"}
        review = dict(base, status="include", article_type="Review")
        letter = dict(base, work_id="y", status="include", article_type="Letter")
        errors = AUDIT.audit([review, letter])["errors"]
        self.assertTrue(any("must be context" in item for item in errors))
        self.assertTrue(any("letter lacks" in item for item in errors))

    def test_utf8_bom_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.md"
            path.write_text("中文", encoding="utf-8-sig")
            self.assertEqual(path.read_bytes()[:3], b"\xef\xbb\xbf")


if __name__ == "__main__":
    unittest.main()

