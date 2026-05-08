#!/usr/bin/env python
"""QC completed NSFC review outputs.

This script checks model-generated review artifacts after the review workflow.
It does not read PDFs and does not perform scientific review.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


REVIEW_STAGE_FILES = (
    "01_scientific_critique.txt",
    "02_literature_checks.txt",
    "03_reviewer2_stress_test.txt",
    "04_peer_review_draft.txt",
    "05_final_review.txt",
    "06_submitted_review_comment.txt",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def discover_workdirs(work_root: Path) -> list[Path]:
    return sorted(
        [p for p in work_root.glob("nsfc-review-*") if p.is_dir()],
        key=lambda p: p.name.lower(),
    )


def header(text: str) -> str:
    return text[:2000]


def has_completed_status(head: str) -> bool:
    return "\nstatus: completed\n" in f"\n{head}\n"


def has_protocol_violation(head: str) -> bool:
    return "status: completed_with_protocol_violation" in head


def qc_review_workdir(workdir: Path) -> tuple[str, list[str], dict[str, str]]:
    issues: list[str] = []
    details: dict[str, str] = {}
    review_dir = workdir / "review"

    if not review_dir.exists():
        return "NEEDS_ATTENTION", ["missing review directory"], details

    explicit_count = 0
    fallback_count = 0
    completed_count = 0

    for name in REVIEW_STAGE_FILES:
        path = review_dir / name
        if not path.exists():
            issues.append(f"missing review file: {name}")
            continue
        text = read_text(path)
        head = header(text)
        if "NSFC_REVIEW_STAGE_PROVENANCE" not in head:
            issues.append(f"missing provenance header: {name}")
        if "attempted_skill_call:" not in head:
            issues.append(f"missing attempted_skill_call: {name}")
        if "skill_call_result:" not in head:
            issues.append(f"missing skill_call_result: {name}")
        if has_protocol_violation(head):
            issues.append(f"protocol violation recorded: {name}")
        if has_completed_status(head):
            completed_count += 1
            if "attempted_skill_call: no" in head:
                issues.append(f"completed file has unattempted supporting skill call: {name}")
        else:
            issues.append(f"not completed: {name}")
        if "execution_mode: explicit_skill_call" in head:
            explicit_count += 1
        if "execution_mode: fallback_agent_role" in head:
            fallback_count += 1
        if "To be completed" in text:
            issues.append(f"placeholder remains: {name}")

    final_text = read_text(review_dir / "05_final_review.txt")
    if final_text:
        if "KILL-MODE DECISION" not in final_text:
            issues.append("final review missing exact KILL-MODE DECISION section")
        if not any(marker in final_text for marker in ("manual-review", "human inspection")):
            issues.append("final review missing manual-review reminder")
        if not any(marker in final_text for marker in ("funding", "recommendation")):
            issues.append("final review missing funding recommendation")
        if not any(marker in final_text for marker in ("attribute", "free_exploration", "goal_oriented")):
            issues.append("final review missing research attribute match judgment")
        if not any(marker in final_text for marker in ("A/B/C", "weighted score", "cap rule")):
            issues.append("final review missing scoring summary or cap-rule check")
        scoring_markers = (
            "Total weighted score",
            "/100",
            "Raw score /5",
            "Weighted points",
            "Grade before cap rules",
            "Final grade after cap rules",
        )
        for marker in scoring_markers:
            if marker not in final_text:
                issues.append(f"final review missing required scoring marker: {marker}")
        forbidden_score_patterns = ("综合加权评分：约", "加权总分：约")
        if any(pattern in final_text and "/5" in final_text for pattern in forbidden_score_patterns):
            issues.append("final review appears to use 0-5 average instead of /100 weighted score")

    submitted_text = read_text(review_dir / "06_submitted_review_comment.txt")
    if submitted_text:
        required_markers = (
            "COMPREHENSIVE EVALUATION",
            "FUNDING OPINION",
            "KILL-MODE DECISION",
            "SCIENTIFIC EVALUATION DESCRIPTION",
            "SPECIFIC REVIEW COMMENTS",
            "MANUAL REVIEW REMINDER",
        )
        for marker in required_markers:
            if marker not in submitted_text:
                issues.append(f"submitted review comment missing section: {marker}")

    details["completed_stage_files"] = str(completed_count)
    details["explicit_skill_calls"] = str(explicit_count)
    details["fallback_agent_roles"] = str(fallback_count)
    status = "REVIEW_QC_PASS" if not issues else "NEEDS_ATTENTION"
    return status, issues, details


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QC completed NSFC review workflow outputs.")
    parser.add_argument("--work-root", default=None, help="Folder containing nsfc-review-* directories.")
    parser.add_argument("--workdir", action="append", default=None, help="Specific nsfc-review-* directory to check. Can be repeated.")
    parser.add_argument("--output", default=None, help="Output TSV path. Defaults to <work-root>/_batch/review_completion_qc_report.txt.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workdir:
        workdirs = [Path(p).expanduser().resolve() for p in args.workdir]
        work_root = workdirs[0].parent if workdirs else Path.cwd()
    else:
        work_root = Path(args.work_root).expanduser().resolve() if args.work_root else Path.cwd().resolve()
        workdirs = discover_workdirs(work_root)

    rows: list[dict[str, str]] = []
    for idx, workdir in enumerate(workdirs, start=1):
        status, issues, details = qc_review_workdir(workdir)
        rows.append(
            {
                "index": str(idx),
                "workdir": str(workdir),
                "status": status,
                "issues": "; ".join(issues) if issues else "none",
                "completed_stage_files": details.get("completed_stage_files", ""),
                "explicit_skill_calls": details.get("explicit_skill_calls", ""),
                "fallback_agent_roles": details.get("fallback_agent_roles", ""),
            }
        )

    output = Path(args.output).expanduser().resolve() if args.output else work_root / "_batch" / "review_completion_qc_report.txt"
    write_tsv(
        output,
        rows,
        [
            "index",
            "workdir",
            "status",
            "issues",
            "completed_stage_files",
            "explicit_skill_calls",
            "fallback_agent_roles",
        ],
    )
    print(f"review_completion_qc_report: {output}")
    print(f"checked_workdirs: {len(rows)}")
    print(f"generated_at: {datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
