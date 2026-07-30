from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

CONTEXT_ONLY_TYPES = {"comment", "commentary", "editorial", "highlight", "news", "perspective", "preview", "review", "viewpoint"}
REVIEW_SIGNALS = re.compile(r"\b(in this review|this review|we review|we provide a review|this perspective)\b", re.I)
MIN_PRIMARY_EVIDENCE_CHARS = 200


def evidence_text(row: dict) -> str:
    return " ".join(str(row.get(key) or "") for key in ("abstract", "_abstract", "lead_text")).strip()


def audit(records: list[dict]) -> dict:
    errors, warnings = [], []
    statuses = Counter(row.get("status") for row in records)
    for index, row in enumerate(records, 1):
        label = row.get("doi") or row.get("work_id") or f"line-{index}"
        status = row.get("status")
        article_type = str(row.get("article_type") or "").strip().lower()
        text = evidence_text(row)
        if status in {"include", "context"} and not row.get("date"):
            errors.append(f"{label}: {status} lacks date")
        if status in {"include", "context"} and not row.get("evidence_urls"):
            errors.append(f"{label}: {status} lacks evidence_urls")
        if status == "include":
            if article_type in CONTEXT_ONLY_TYPES:
                errors.append(f"{label}: {article_type} must be context, not include")
            elif REVIEW_SIGNALS.search(text):
                errors.append(f"{label}: abstract identifies review/perspective content; use context")
            if article_type == "letter" and len(text) < MIN_PRIMARY_EVIDENCE_CHARS:
                errors.append(f"{label}: letter lacks sufficient original-research evidence")
            elif article_type != "letter" and len(text) < MIN_PRIMARY_EVIDENCE_CHARS:
                errors.append(f"{label}: include lacks sufficient abstract/lead evidence for original research")
            if not row.get("summary_cn") or not row.get("importance_cn"):
                errors.append(f"{label}: include lacks supported summary fields")
        if status == "context":
            if not article_type:
                errors.append(f"{label}: context lacks article_type")
            if not row.get("context_reason"):
                errors.append(f"{label}: context lacks context_reason")
        if status == "needs_evidence" and not row.get("exclusion_reason"):
            warnings.append(f"{label}: needs_evidence lacks missing-evidence reason")
    if len(records) >= 200 and not statuses.get("needs_evidence"):
        warnings.append("large run has zero needs_evidence records; verify that uncertainty was not forced into include/exclude")
    return {"records": len(records), "statuses": dict(statuses), "errors": errors, "warnings": warnings}


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(load(args.input))
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8-sig")
    print(payload)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

