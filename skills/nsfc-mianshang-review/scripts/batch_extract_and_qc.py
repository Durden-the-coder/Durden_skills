#!/usr/bin/env python
"""Batch prepare NSFC proposal TXT artifacts and QC reports.

This script only performs deterministic preparation:
- discover proposal PDFs/TXTs;
- run extract_nsfc_text.py for each input;
- QC generated text, section index, and review skeleton provenance headers;
- write batch manifest, QC report, review queue, and one review task card per ready proposal.

It does not perform scientific review and does not read PDFs after extraction.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REQUIRED_SECTIONS = (
    "title",
    "chinese_abstract",
    "project_rationale",
    "research_content",
    "research_basis",
)

REVIEW_STAGE_FILES = (
    "01_scientific_critique.txt",
    "02_literature_checks.txt",
    "03_reviewer2_stress_test.txt",
    "04_peer_review_draft.txt",
    "05_final_review.txt",
    "06_submitted_review_comment.txt",
)

SECTION_LOCATION_RE = re.compile(r"^([a-z_]+): page\s+(\d+), char\s+(\d+)", re.MULTILINE)


def safe_stem(name: str) -> str:
    import re

    stem = Path(name).stem.strip()
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", stem)
    stem = re.sub(r"\s+", "_", stem)
    return stem[:80] or "proposal"


def load_passwords(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    passwords: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            key = (row.get("file") or row.get("filename") or row.get("proposal") or "").strip()
            password = (row.get("password") or "").strip()
            if key:
                passwords[key] = password
    return passwords


def discover_inputs(proposal_dir: Path) -> list[Path]:
    files: list[Path] = []
    for suffix in ("*.pdf", "*.PDF", "*.txt", "*.TXT"):
        files.extend(proposal_dir.glob(suffix))
    return sorted({p.resolve() for p in files}, key=lambda p: p.name.lower())


def run_extract(
    extract_script: Path,
    proposal: Path,
    workdir: Path,
    password: str | None,
) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(extract_script),
        "--proposal",
        str(proposal),
        "--workdir",
        str(workdir),
        "--init-review-files",
    ]
    if password:
        cmd.extend(["--password", password])
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_section_locations(index: str) -> dict[str, tuple[int, int]]:
    locations: dict[str, tuple[int, int]] = {}
    for match in SECTION_LOCATION_RE.finditer(index):
        locations[match.group(1)] = (int(match.group(2)), int(match.group(3)))
    return locations


def qc_workdir(workdir: Path) -> tuple[str, list[str], dict[str, str]]:
    details: dict[str, str] = {}
    issues: list[str] = []

    full_text = workdir / "extracted" / "00_full_text.txt"
    section_index = workdir / "extracted" / "01_section_index.txt"
    report = workdir / "extracted" / "extraction_report.txt"
    review_dir = workdir / "review"

    if not full_text.exists():
        issues.append("missing 00_full_text.txt")
    else:
        text = read_text(full_text)
        non_ws = sum(1 for ch in text if not ch.isspace())
        details["non_whitespace_chars"] = str(non_ws)
        if non_ws < 1500:
            issues.append(f"low text volume: {non_ws} non-whitespace chars")

    if not section_index.exists():
        issues.append("missing 01_section_index.txt")
    else:
        index = read_text(section_index)
        missing = []
        for section in REQUIRED_SECTIONS:
            if f"{section}: not found" in index or f"{section}:" not in index:
                missing.append(section)
        details["missing_sections"] = ",".join(missing) if missing else "none"
        if missing:
            issues.append("missing section index entries: " + ",".join(missing))
        positions = parse_section_locations(index)
        expected_order = [section for section in REQUIRED_SECTIONS if section in positions]
        if expected_order != sorted(expected_order, key=lambda section: positions[section]):
            issues.append("section index locations are inconsistent")
        if {"chinese_abstract", "project_rationale"} <= set(positions) and positions["chinese_abstract"] > positions["project_rationale"]:
            issues.append("chinese abstract appears after project rationale in section index")

    if not report.exists():
        issues.append("missing extraction_report.txt")
    else:
        report_text = read_text(report)
        for marker in ("ENCRYPTED_PDF", "DEPENDENCY_MISSING", "UNSUPPORTED_INPUT_FORMAT", "PDF_OPEN_ERROR"):
            if marker in report_text:
                issues.append(f"extraction report contains {marker}")

    if not review_dir.exists():
        issues.append("missing review directory")
    else:
        for name in REVIEW_STAGE_FILES:
            stage_path = review_dir / name
            if not stage_path.exists():
                issues.append(f"missing review skeleton: {name}")
                continue
            head = read_text(stage_path)[:800]
            if "NSFC_REVIEW_STAGE_PROVENANCE" not in head:
                issues.append(f"missing stage provenance header: {name}")
            else:
                if "attempted_skill_call:" not in head:
                    issues.append(f"missing attempted skill call record: {name}")
                if "skill_call_result:" not in head:
                    issues.append(f"missing skill call result record: {name}")
                if "status: completed_with_protocol_violation" in head:
                    issues.append(f"protocol violation recorded: {name}")
                if "status: completed" in head and "attempted_skill_call: no" in head:
                    issues.append(f"completed stage has unattempted supporting skill call: {name}")

    status = "READY_FOR_REVIEW" if not issues else "NEEDS_ATTENTION"
    return status, issues, details


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_review_task_card(
    task_path: Path,
    index: str,
    proposal: Path,
    workdir: Path,
    qc_script: Path,
) -> None:
    task_path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# NSFC Review Task {index}

IMPORTANT: Open a new agent window/session for this task. Review only this one proposal. Do not process any other proposal in the same session.

## Suggested Prompt

使用 `nsfc-mianshang-review`，只审阅下面这一个项目。不要处理其他项目。

读取并执行本任务卡中的路径和要求：

`{task_path}`

## Proposal

`{proposal}`

## Review Directory

`{workdir}`

## Inputs To Use

Use TXT/review artifacts only:

- `{workdir / "extracted" / "00_full_text.txt"}`
- `{workdir / "extracted" / "01_section_index.txt"}`
- `{workdir / "extracted" / "extraction_report.txt"}`
- `{workdir / "review" / "nsfc_review_cache.txt"}`

Do not read the PDF during review. The PDF was only for extraction.

## Required Work

1. Identify the latest workflow state from files in the review directory.
2. Complete or update `review/nsfc_review_cache.txt` if needed.
3. Generate or complete these files in order:
   - `review/01_scientific_critique.txt`
   - `review/02_literature_checks.txt`
   - `review/03_reviewer2_stress_test.txt`
   - `review/04_peer_review_draft.txt`
   - `review/05_final_review.txt`
   - `review/06_submitted_review_comment.txt`
4. Before writing each stage file, explicitly call the corresponding supporting skill when available.
5. If a supporting skill cannot be explicitly called, record accurate provenance in that stage file.
6. Scoring must use exact dimensions and weights from `scoring-rubric.txt`, including `Total weighted score: x/100`.
7. `05_final_review.txt` and `06_submitted_review_comment.txt` must include `KILL-MODE DECISION`.
8. After finishing, run review completion QC:

```powershell
python "{qc_script}" --workdir "{workdir}"
```

9. Stop after this project. Do not continue to the next task.

## Completion Standard

- Stage files `01` through `06` are substantive and marked completed.
- Final review is polished Chinese.
- Submitted review comment is suitable for the NSFC review form.
- QC passes, or QC issues are clearly reported.
"""
    suggested_prompt = (
        "## Suggested Prompt\n\n"
        "使用 `nsfc-mianshang-review`，只审阅下面这一个项目。不要处理其他项目。\n"
        "读取并执行本任务卡中的路径和要求：\n\n"
        f"`{task_path}`\n\n"
    )
    text = text[: text.index("## Suggested Prompt")] + suggested_prompt + text[text.index("## Proposal") :]
    task_path.write_text(text, encoding="utf-8")


def review_prompt_text(position: int, total: int, task_file: str) -> str:
    return (
        f"【NSFC审阅任务 {position}/{total}】\n"
        "请新建一个 agent 窗口/session，然后复制粘贴以下内容执行：\n\n"
        "使用 `nsfc-mianshang-review`，只审阅这一个项目，不要处理其他项目。\n"
        f"读取并执行：{task_file}\n"
        "完成后停止，不要继续下一个任务。"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch extract NSFC proposal PDFs/TXTs and run deterministic QC.")
    parser.add_argument("--proposal-dir", required=True, help="Folder containing proposal PDFs/TXTs.")
    parser.add_argument("--work-root", default=None, help="Root folder for nsfc-review-* outputs. Defaults to proposal-dir parent.")
    parser.add_argument("--batch-dir", default=None, help="Batch metadata directory. Defaults to work-root/_batch.")
    parser.add_argument("--password", default=None, help="Optional shared PDF password for all encrypted PDFs.")
    parser.add_argument("--password-file", default=None, help="Optional UTF-8 TSV with columns file,password.")
    parser.add_argument("--limit", type=int, default=None, help="Optional max number of files to process.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    proposal_dir = Path(args.proposal_dir).expanduser().resolve()
    if not proposal_dir.exists() or not proposal_dir.is_dir():
        print(f"Proposal directory not found: {proposal_dir}", file=sys.stderr)
        return 2

    work_root = Path(args.work_root).expanduser().resolve() if args.work_root else proposal_dir.parent.resolve()
    batch_dir = Path(args.batch_dir).expanduser().resolve() if args.batch_dir else work_root / "_batch"
    task_dir = batch_dir / "review_tasks"
    extract_script = Path(__file__).with_name("extract_nsfc_text.py").resolve()
    qc_script = Path(__file__).with_name("review_completion_qc.py").resolve()
    passwords = load_passwords(Path(args.password_file).expanduser().resolve() if args.password_file else None)

    proposals = discover_inputs(proposal_dir)
    if args.limit is not None:
        proposals = proposals[: args.limit]

    manifest_rows: list[dict[str, str]] = []
    queue_rows: list[dict[str, str]] = []
    report_lines = [
        "NSFC BATCH EXTRACTION QC REPORT",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"proposal_dir: {proposal_dir}",
        f"work_root: {work_root}",
        f"batch_dir: {batch_dir}",
        f"proposal_count: {len(proposals)}",
        "",
    ]

    for idx, proposal in enumerate(proposals, start=1):
        password = passwords.get(proposal.name) or passwords.get(str(proposal)) or args.password
        workdir = work_root / f"nsfc-review-{safe_stem(proposal.name)}"
        returncode, output = run_extract(extract_script, proposal, workdir, password)
        status, issues, details = qc_workdir(workdir)
        if returncode != 0:
            status = "NEEDS_ATTENTION"
            issues.append(f"extract_script_returncode={returncode}")

        issue_text = "; ".join(issues) if issues else "none"
        manifest_rows.append(
            {
                "index": str(idx),
                "proposal": str(proposal),
                "workdir": str(workdir),
                "status": status,
                "issues": issue_text,
                "non_whitespace_chars": details.get("non_whitespace_chars", ""),
                "missing_sections": details.get("missing_sections", ""),
            }
        )
        if status == "READY_FOR_REVIEW":
            task_file = task_dir / f"{idx:03d}_{safe_stem(proposal.name)}.md"
            write_review_task_card(task_file, f"{idx:03d}", proposal, workdir, qc_script)
            queue_rows.append(
                {
                    "index": str(idx),
                    "proposal": str(proposal),
                    "workdir": str(workdir),
                    "task_file": str(task_file),
                    "next_step": "open_new_session_and_run_task_card",
                    "status": "QUEUED",
                }
            )

        report_lines.extend(
            [
                f"[{idx}] {proposal.name}",
                f"workdir: {workdir}",
                f"status: {status}",
                f"issues: {issue_text}",
                f"non_whitespace_chars: {details.get('non_whitespace_chars', '')}",
                f"missing_sections: {details.get('missing_sections', '')}",
                "",
            ]
        )
        if returncode != 0:
            report_lines.extend(["extract_output:", output[-2000:], ""])

    write_tsv(
        batch_dir / "manifest.tsv",
        manifest_rows,
        ["index", "proposal", "workdir", "status", "issues", "non_whitespace_chars", "missing_sections"],
    )
    write_tsv(batch_dir / "review_queue.tsv", queue_rows, ["index", "proposal", "workdir", "task_file", "next_step", "status"])
    write_tsv(
        batch_dir / "review_status.tsv",
        [
            {
                "index": row["index"],
                "proposal": row["proposal"],
                "workdir": row["workdir"],
                "task_file": row["task_file"],
                "review_status": "NOT_STARTED",
                "notes": "",
            }
            for row in queue_rows
        ],
        ["index", "proposal", "workdir", "task_file", "review_status", "notes"],
    )
    write_tsv(
        batch_dir / "review_task_index.tsv",
        queue_rows,
        ["index", "proposal", "workdir", "task_file", "next_step", "status"],
    )
    prompt_blocks = [
        "NSFC REVIEW PROMPTS",
        "Copy one block into a new agent window/session. Use one session per task.",
        "",
    ]
    for position, row in enumerate(queue_rows, start=1):
        prompt_blocks.append(review_prompt_text(position, len(queue_rows), row["task_file"]))
        prompt_blocks.append("")
    (batch_dir / "review_prompts.txt").write_text("\n".join(prompt_blocks).rstrip() + "\n", encoding="utf-8")
    (batch_dir / "extraction_qc_report.txt").write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")

    print("\n".join(report_lines))
    print(f"manifest: {batch_dir / 'manifest.tsv'}")
    print(f"review_queue: {batch_dir / 'review_queue.tsv'}")
    print(f"review_status: {batch_dir / 'review_status.tsv'}")
    print(f"review_task_index: {batch_dir / 'review_task_index.tsv'}")
    print(f"review_prompts: {batch_dir / 'review_prompts.txt'}")
    print(f"review_tasks: {task_dir}")
    print(f"qc_report: {batch_dir / 'extraction_qc_report.txt'}")
    print("")
    print("=" * 72)
    print("NEXT STEP: OPEN A NEW AGENT WINDOW/SESSION FOR EACH REVIEW TASK")
    print("=" * 72)
    print("Batch preparation is complete. Do not review multiple proposals in this session.")
    print(f"Ready review tasks: {len(queue_rows)}")
    if queue_rows:
        print("")
        print("Copy/paste prompts:")
        print("")
        for position, row in enumerate(queue_rows, start=1):
            print(review_prompt_text(position, len(queue_rows), row["task_file"]))
            print("")
        print(f"一共需要执行 {len(queue_rows)} 次；每次新建一个窗口/session，只执行一个 task card。")
    else:
        print("No READY_FOR_REVIEW tasks were generated. Check extraction_qc_report.txt first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
