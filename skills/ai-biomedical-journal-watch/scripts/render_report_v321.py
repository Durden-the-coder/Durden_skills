from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

BASE_PATH = Path(__file__).with_name("render_report.py")
SPEC = importlib.util.spec_from_file_location("bmwatch_render_base", BASE_PATH)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)

DEFAULT_EXCLUSION_REASON_LIMIT = 10


def index_limit_for_window(window: str) -> int:
    value = (window or "96h").strip().lower()
    presets = {"72h": 30, "96h": 30, "7d": 50, "30d": 80}
    if value in presets:
        return presets[value]
    match = re.fullmatch(r"(\d+)([hd])", value)
    if match:
        amount, unit = int(match.group(1)), match.group(2)
        days = amount / 24 if unit == "h" else amount
        return 80 if days >= 30 else 50 if days >= 7 else 30
    return 30


def bound_exclusion_reasons(report: str, limit: int) -> str:
    marker = "## 排除汇总\n\n"
    if marker not in report:
        return report
    prefix, section = report.split(marker, 1)
    entries = section.rstrip().splitlines()
    if len(entries) <= limit:
        return report
    hidden = len(entries) - limit
    kept = entries[:limit] + [f"- 另有 {hidden} 类低频排除理由未展示；完整记录见 JSONL。"]
    return prefix + marker + "\n".join(kept) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window", default="96h")
    parser.add_argument("--detail-limit", type=int, default=BASE.DEFAULT_DETAIL_LIMIT)
    parser.add_argument("--per-journal", type=int, default=BASE.DEFAULT_PER_JOURNAL_CEILING)
    parser.add_argument("--index-limit", type=int)
    parser.add_argument("--evidence-limit", type=int, default=BASE.DEFAULT_EVIDENCE_LIMIT)
    parser.add_argument("--context-limit", type=int, default=BASE.DEFAULT_CONTEXT_LIMIT)
    parser.add_argument("--exclusion-reason-limit", type=int, default=DEFAULT_EXCLUSION_REASON_LIMIT)
    args = parser.parse_args()
    index_limit = args.index_limit if args.index_limit is not None else index_limit_for_window(args.window)
    if min(args.detail_limit, args.per_journal, index_limit, args.evidence_limit, args.context_limit, args.exclusion_reason_limit) < 0:
        raise ValueError("limits must be non-negative")
    records = BASE.load_records(args.input)
    report = BASE.render(records, args.detail_limit, args.per_journal, index_limit, args.evidence_limit, args.context_limit)
    report = bound_exclusion_reasons(report, args.exclusion_reason_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8-sig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

