#!/usr/bin/env python
"""Prepare TXT working files for NSFC grant review.

Design goals:
- PDF input is read only for text extraction.
- Later review steps should use generated TXT files.
- Encrypted PDFs produce an action-required report instead of a hard crash.
- All outputs are written under the user-specified workdir.
- Optional review-stage skeleton files help agents continue the workflow.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

BLOCKED_WRITE_PARTS = {
    "windows",
    "program files",
    "program files (x86)",
    "appdata",
    ".codex",
    ".claude",
    ".agents",
}

PAGE_RE = re.compile(r"^===== PAGE (\d+) =====$")


def is_blocked_workdir(path: Path) -> bool:
    parts = {p.lower() for p in path.resolve().parts}
    return bool(parts & BLOCKED_WRITE_PARTS)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def try_import_pdf_reader():
    try:
        from pypdf import PdfReader  # type: ignore
        return PdfReader, "pypdf"
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore
        return PdfReader, "PyPDF2"
    except Exception:
        return None, None


def extract_pdf_text(pdf_path: Path, password: str | None):
    PdfReader, backend = try_import_pdf_reader()
    if PdfReader is None:
        return "", {"status": "DEPENDENCY_MISSING", "message": "Install pypdf/PyPDF2 or provide exported TXT file."}

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        return "", {"status": "PDF_OPEN_ERROR", "message": str(exc), "backend": backend}

    encrypted = bool(getattr(reader, "is_encrypted", False))
    if encrypted:
        if not password:
            return "", {
                "status": "ENCRYPTED_PDF",
                "message": "PDF is encrypted. Ask the user for password, decrypted PDF, exported TXT, or OCR text.",
                "backend": backend,
            }
        try:
            result = reader.decrypt(password)
            if result == 0:
                return "", {
                    "status": "ENCRYPTED_PDF_PASSWORD_FAILED",
                    "message": "Password did not decrypt the PDF.",
                    "backend": backend,
                }
        except Exception as exc:
            return "", {
                "status": "ENCRYPTED_PDF_PASSWORD_ERROR",
                "message": str(exc),
                "backend": backend,
            }

    pages = []
    page_count = len(reader.pages)
    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            page_text = f"\n[PAGE {idx} EXTRACTION ERROR: {exc}]\n"
        pages.append(f"\n\n===== PAGE {idx} =====\n{page_text.strip()}\n")

    full_text = "".join(pages).strip() + "\n"
    non_ws = sum(1 for ch in full_text if not ch.isspace())
    status = "OK" if non_ws >= max(500, page_count * 50) else "LOW_TEXT_POSSIBLE_OCR_NEEDED"
    return full_text, {
        "status": status,
        "backend": backend,
        "pages": page_count,
        "non_whitespace_chars": non_ws,
        "encrypted": encrypted,
    }


def normalize_line(line: str) -> str:
    line = line.replace("\u00a0", " ").replace("\u3000", " ")
    line = re.sub(r"\s+", "", line)
    return line.strip()


def split_pages(full_text: str):
    pages = []
    current_page = 0
    current_lines = []
    for raw_line in full_text.splitlines():
        match = PAGE_RE.match(raw_line)
        if match:
            if current_page:
                pages.append((current_page, current_lines))
            current_page = int(match.group(1))
            current_lines = []
            continue
        if current_page:
            current_lines.append(raw_line.rstrip())
    if current_page:
        pages.append((current_page, current_lines))
    return pages


def page_char_offset(full_text: str, page_no: int, line_text: str) -> int:
    page_marker = f"===== PAGE {page_no} ====="
    page_pos = full_text.find(page_marker)
    if page_pos < 0:
        return -1
    return full_text.find(line_text, page_pos)


def find_line_with_candidates(pages, full_text: str, candidates, page_start: int = 1):
    for page_no, lines in pages:
        if page_no < page_start:
            continue
        for line in lines:
            compact = normalize_line(line)
            if compact and any(candidate in compact for candidate in candidates):
                pos = page_char_offset(full_text, page_no, line)
                return page_no, pos, " ".join(line.split())
    return None


def find_first_nonempty_line(pages, full_text: str, page_start: int = 1, skip_candidates=()):
    for page_no, lines in pages:
        if page_no < page_start:
            continue
        for line in lines:
            compact = normalize_line(line)
            if not compact:
                continue
            if any(candidate in compact for candidate in skip_candidates):
                continue
            pos = page_char_offset(full_text, page_no, line)
            return page_no, pos, " ".join(line.split())
    return None


def find_title(pages, full_text: str):
    title = find_line_with_candidates(pages, full_text, ("项目名称",), page_start=1)
    if title is not None:
        return title
    return find_first_nonempty_line(
        pages,
        full_text,
        page_start=1,
        skip_candidates=("申请代码", "接收部门", "国家自然科学基金", "项目申请号"),
    )


def format_section(name: str, found) -> str:
    if found is None:
        return f"{name}: not found"
    page_no, pos, snippet = found
    return f"{name}: page {page_no}, char {pos}\n  {snippet}"


def make_section_index(full_text: str) -> str:
    pages = split_pages(full_text)
    title = find_title(pages, full_text)
    abstract = find_first_nonempty_line(
        pages,
        full_text,
        page_start=3,
        skip_candidates=("英文摘要", "abstract", "主要参与者", "预算", "报告正文"),
    )
    project_rationale = find_line_with_candidates(pages, full_text, ("（一）立项依据", "(一)立项依据"), page_start=5)
    research_content = find_line_with_candidates(pages, full_text, ("（二）研究内容", "(二)研究内容"), page_start=8)
    research_basis = find_line_with_candidates(pages, full_text, ("（三）研究基础", "(三)研究基础"), page_start=12)
    lines = [
        format_section("title", title),
        format_section("chinese_abstract", abstract),
        format_section("project_rationale", project_rationale),
        format_section("research_content", research_content),
        format_section("research_basis", research_basis),
        "",
        "notes:",
        "- 'research_content' includes distinctive features and innovation points.",
        "- 'research_basis' includes feasibility analysis.",
        "- low-value administrative sections are intentionally excluded.",
    ]
    return "\n".join(lines).strip() + "\n"


def initial_cache_template(source_name: str) -> str:
    return f"""NSFC GENERAL PROGRAM REVIEW CACHE

SOURCE
{source_name}

BASIC INFORMATION
Title:
Field:
Research attribute: free exploration / goal-oriented / unclear
Duration:
Collaborators:

CORE SCIENTIFIC QUESTION

CENTRAL HYPOTHESIS OR MAIN LOGIC

SIGNIFICANCE CLAIMS
- Claim:
  Evidence in application:
  Concern:

RESEARCH OBJECTIVES AND CONTENT
- Objective/Aim:
  Methods:
  Expected result:
  Risk:

CLAIMED INNOVATION
- Innovation claim:
  Basis:
  Concern:

TECHNICAL ROUTE

PRELIMINARY BASIS AND FEASIBILITY
- Evidence:
  Supports:
  Limitation:

RISKS AND ALTERNATIVES

APPLICANT/TEAM FIT

RELATED PROJECT OVERLAP OR CONTINUITY

KEY LITERATURE CLAIMS TO VERIFY

CANDIDATE MAJOR CONCERNS

CANDIDATE MINOR CONCERNS
"""


def review_stage_skeletons():
    return {
        "01_scientific_critique.txt": "科学性批判分析\n\n待补充：\n1. 核心科学问题是否成立\n2. 中心假说或逻辑链是否闭环\n3. 研究设计、统计、验证路径是否充分\n4. 主要科学风险与替代方案\n",
        "02_literature_checks.txt": "定向文献核查\n\n待补充：\n1. novelty 的真实边界\n2. 关键文献是否已覆盖该方向\n3. 关键 claim 是否存在公开证据冲突或缺口\n",
        "03_reviewer2_stress_test.txt": "Reviewer 2 压力测试\n\n待补充：\n1. 最可能导致扣分或否决的结构性缺陷\n2. 哪些问题属于可修改弱点，哪些属于决策级缺陷\n3. kill-mode 下的致命问题清单\n",
        "04_final_review.txt": "总体评价\n\n待补充。\n\n优势\n\n待补充。\n\n创新性评估\n\n待补充。\n\n致命缺陷或决策级问题\n\n待补充。\n\n次要问题\n\n待补充。\n\n可行性与风险评估\n\n待补充。\n\n修改建议\n\n待补充。\n\n人工审核提醒\n\n待补充：工作条件、简历/代表作、图示和图像证据等人工审核边界。\n\n资助判断\n\n待补充。\n",
    }


def report_text(proposal: Path, workdir: Path, metadata: dict, outputs) -> str:
    lines = [
        "NSFC PDF/TXT EXTRACTION REPORT",
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"Proposal: {proposal}",
        f"Workdir: {workdir}",
        "",
        "STATUS",
        str(metadata.get("status", "UNKNOWN")),
        "",
        "DETAILS",
    ]
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    lines.extend(["", "OUTPUTS"])
    lines.extend(str(p) for p in outputs)
    return "\n".join(lines) + "\n"


def safe_stem(name: str) -> str:
    stem = Path(name).stem.strip()
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", stem)
    stem = re.sub(r"\s+", "_", stem)
    return stem[:80] or "proposal"


def default_workdir_for(proposal: Path) -> Path:
    return proposal.parent.parent / f"nsfc_review_{safe_stem(proposal.name)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract NSFC proposal PDF/TXT into review workflow TXT files.")
    parser.add_argument("--proposal", required=True, help="Path to proposal PDF or TXT.")
    parser.add_argument("--workdir", default=None, help="Review workflow directory.")
    parser.add_argument("--password", default=None, help="Optional PDF password.")
    parser.add_argument("--copy-input", action="store_true", help="Copy the input file into workdir/input.")
    parser.add_argument("--init-review-files", action="store_true", help="Pre-create review stage skeleton files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    proposal = Path(args.proposal).expanduser().resolve()
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else default_workdir_for(proposal).resolve()

    if not proposal.exists():
        print(f"Proposal not found: {proposal}", file=sys.stderr)
        return 2
    if is_blocked_workdir(workdir):
        print(f"Refusing to write to blocked/system-like workdir: {workdir}", file=sys.stderr)
        return 3

    extracted = workdir / "extracted"
    review = workdir / "review"
    extracted.mkdir(parents=True, exist_ok=True)
    review.mkdir(parents=True, exist_ok=True)

    outputs = []
    suffix = proposal.suffix.lower()

    if suffix == ".pdf":
        full_text, metadata = extract_pdf_text(proposal, args.password)
        if str(metadata.get("status", "")).startswith("ENCRYPTED_PDF"):
            action_path = extracted / "ACTION_REQUIRED_encrypted_pdf.txt"
            write_text(action_path, "The proposal PDF is encrypted or extraction is blocked.\n\nAsk the user for password, decrypted PDF, exported TXT, or OCR text.\n")
            outputs.append(action_path)
        elif metadata.get("status") == "DEPENDENCY_MISSING":
            action_path = extracted / "ACTION_REQUIRED_pdf_dependency_or_txt.txt"
            write_text(action_path, "PDF extraction dependency is missing. Ask the user to install pypdf/PyPDF2, provide TXT, or provide OCR text.\n")
            outputs.append(action_path)
        else:
            full_path = extracted / "00_full_text.txt"
            index_path = extracted / "01_section_index.txt"
            write_text(full_path, full_text)
            write_text(index_path, make_section_index(full_text))
            outputs.extend([full_path, index_path])
    elif suffix in {".txt", ".text"}:
        full_text = proposal.read_text(encoding="utf-8", errors="replace")
        metadata = {"status": "OK_TXT_INPUT", "chars": len(full_text)}
        full_path = extracted / "00_full_text.txt"
        index_path = extracted / "01_section_index.txt"
        write_text(full_path, full_text)
        write_text(index_path, make_section_index(full_text))
        outputs.extend([full_path, index_path])
    else:
        metadata = {"status": "UNSUPPORTED_INPUT_FORMAT", "message": "Provide PDF or TXT for this workflow.", "suffix": suffix}

    if args.copy_input and metadata.get("status") != "UNSUPPORTED_INPUT_FORMAT":
        input_dir = workdir / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        copied = input_dir / proposal.name
        shutil.copy2(proposal, copied)
        outputs.append(copied)

    cache_path = review / "nsfc_review_cache.txt"
    if not cache_path.exists() and str(metadata.get("status", "")).startswith(("OK", "LOW_TEXT")):
        write_text(cache_path, initial_cache_template(proposal.name))
        outputs.append(cache_path)

    if args.init_review_files and str(metadata.get("status", "")).startswith(("OK", "LOW_TEXT")):
        for name, content in review_stage_skeletons().items():
            path = review / name
            if not path.exists():
                write_text(path, content)
                outputs.append(path)

    report_path = extracted / "extraction_report.txt"
    write_text(report_path, report_text(proposal, workdir, metadata, outputs))
    outputs.append(report_path)

    print(report_text(proposal, workdir, metadata, outputs))
    status = str(metadata.get("status", ""))
    if status.startswith("OK") or status == "LOW_TEXT_POSSIBLE_OCR_NEEDED" or status.startswith("ENCRYPTED_PDF") or status == "DEPENDENCY_MISSING":
        return 0
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
