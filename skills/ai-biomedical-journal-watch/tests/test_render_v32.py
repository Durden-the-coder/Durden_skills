from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_report_v32", ROOT / "scripts" / "render_report.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def record(i, status, journal="Nature", article_type="Article"):
    row = {"work_id": str(i), "journal": journal, "title": f"Item {i}", "url": f"https://example.org/{i}", "date": f"2026-07-{20+i:02d}", "article_type": article_type, "tracks": ["A"], "status": status, "priority": 3, "ai_role": "core_method", "evidence_urls": [f"https://example.org/{i}"]}
    if status == "include": row.update(summary_cn="摘要", importance_cn="意义")
    if status == "exclude": row.update(exclusion_reason="no_material_ai_role")
    if status == "needs_evidence": row.update(exclusion_reason="missing_abstract")
    if status == "context": row.update(context_reason="biomedical_ai_trend")
    return row


class RenderV32Tests(unittest.TestCase):
    def test_dates_and_context_are_visible_and_separate(self):
        rows = [record(1, "include", "Science"), record(2, "context", "Nature", "News"), record(3, "needs_evidence", "NEJM"), record(4, "exclude", "Cell")]
        report = MODULE.render(rows, 20, 5, 30, 10)
        self.assertIn("发布日期：** 2026-07-21", report)
        self.assertIn("## 趋势与观点（非研究内容）", report)
        self.assertIn("Nature · 2026-07-22 · News", report)
        self.assertIn("NEJM · 2026-07-23", report)
        self.assertIn("纳入 1；趋势观点 1", report)

    def test_context_limit_bounds_long_windows(self):
        rows = [record(i, "context", "Nature", "Comment") for i in range(1, 8)]
        report = MODULE.render(rows, 20, 5, 30, 10, context_limit=3)
        section = report.split("## 趋势与观点（非研究内容）", 1)[1].split("## 待补证据", 1)[0]
        self.assertEqual(section.count("https://example.org/"), 3)
        self.assertIn("另有 4 条", section)

    def test_context_requires_article_type(self):
        row = record(1, "context")
        row.pop("article_type")
        path = ROOT / "tests" / "_invalid_context.jsonl"
        path.write_text(__import__("json").dumps(row), encoding="utf-8")
        try:
            with self.assertRaisesRegex(ValueError, "lacks article_type"):
                MODULE.load_records(path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__": unittest.main()

