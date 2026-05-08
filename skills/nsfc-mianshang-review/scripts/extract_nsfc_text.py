#!/usr/bin/env python
"""Prepare TXT working files for NSFC grant review.

This script is intentionally conservative:
- PDF input is read only for text extraction.
- Later review steps should use generated TXT files.
- Encrypted PDFs produce an action-required report instead of a hard crash.
- All outputs are written under the user-specified workdir, or by default
  under a sibling review directory named nsfc-review-<proposal-stem>.
- Review-stage skeleton files can be pre-created to help agents continue the
  workflow in environments where first-write file creation is unreliable.
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

HEADING_PATTERNS = {
    "chinese_abstract": (
        r"\u4e2d\s*\u6587\s*\u6458\s*\u8981",
    ),
    "project_rationale": (
        r"[\uff08(]\s*\u4e00\s*[\uff09)]\s*\u7acb\s*\u9879\s*\u4f9d\s*\u636e",
        r"\u4e00\s*[\u3001.\uff0e]\s*\u7acb\s*\u9879\s*\u4f9d\s*\u636e",
    ),
    "research_content": (
        r"[\uff08(]\s*\u4e8c\s*[\uff09)]\s*\u7814\s*\u7a76\s*\u5185\s*\u5bb9",
        r"\u4e8c\s*[\u3001.\uff0e]\s*\u7814\s*\u7a76\s*\u5185\s*\u5bb9",
    ),
    "research_basis": (
        r"[\uff08(]\s*\u4e09\s*[\uff09)]\s*\u7814\s*\u7a76\s*\u57fa\s*\u7840",
        r"\u4e09\s*[\u3001.\uff0e]\s*\u7814\s*\u7a76\s*\u57fa\s*\u7840",
    ),
}


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


def extract_pdf_text(pdf_path: Path, password: str | None) -> tuple[str, dict]:
    PdfReader, backend = try_import_pdf_reader()
    if PdfReader is None:
        return "", {
            "status": "DEPENDENCY_MISSING",
            "message": "Install pypdf/PyPDF2 or provide an exported TXT file.",
        }

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
                    "message": "Password did not decrypt the PDF. Ask the user for another format.",
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


def split_pages(full_text: str) -> list[tuple[int, list[str]]]:
    pages: list[tuple[int, list[str]]] = []
    current_page = 0
    current_lines: list[str] = []
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
    if not pages:
        pages.append((1, [line.rstrip() for line in full_text.splitlines()]))
    return pages


def page_char_offset(full_text: str, page_no: int, line_text: str) -> int:
    page_marker = f"===== PAGE {page_no} ====="
    page_pos = full_text.find(page_marker)
    if page_pos < 0:
        return full_text.find(line_text)
    return full_text.find(line_text, page_pos)


def find_line_with_candidates(
    pages: list[tuple[int, list[str]]],
    full_text: str,
    candidates: tuple[str, ...],
    page_start: int = 1,
) -> tuple[int, int, str] | None:
    normalized_candidates = tuple(normalize_line(candidate) for candidate in candidates)
    for page_no, lines in pages:
        if page_no < page_start:
            continue
        for line in lines:
            compact = normalize_line(line)
            if compact and any(candidate in compact for candidate in normalized_candidates):
                pos = page_char_offset(full_text, page_no, line)
                return page_no, pos, " ".join(line.split())
    return None


def find_first_nonempty_line(
    pages: list[tuple[int, list[str]]],
    full_text: str,
    page_start: int = 1,
    skip_candidates: tuple[str, ...] = (),
) -> tuple[int, int, str] | None:
    normalized_skips = tuple(normalize_line(candidate) for candidate in skip_candidates)
    for page_no, lines in pages:
        if page_no < page_start:
            continue
        for line in lines:
            compact = normalize_line(line)
            if not compact:
                continue
            if any(candidate in compact for candidate in normalized_skips):
                continue
            pos = page_char_offset(full_text, page_no, line)
            return page_no, pos, " ".join(line.split())
    return None


def first_nonempty_after(
    pages: list[tuple[int, list[str]]],
    full_text: str,
    heading: tuple[int, int, str] | None,
) -> tuple[int, int, str] | None:
    if heading is None:
        return None
    target_page, _, heading_line = heading
    for page_no, lines in pages:
        if page_no != target_page:
            continue
        seen_heading = False
        for line in lines:
            normalized = " ".join(line.split())
            if not seen_heading and normalized == heading_line:
                seen_heading = True
                continue
            if seen_heading and normalize_line(line):
                pos = page_char_offset(full_text, page_no, line)
                return page_no, pos, " ".join(line.split())
    return None


def format_section(name: str, found: tuple[int, int, str] | None) -> str:
    if found is None:
        return f"{name}: not found"
    page_no, pos, snippet = found
    return f"{name}: page {page_no}, char {pos}\n  {snippet}"


def page_for_pos(full_text: str, pos: int) -> int:
    page_no = 0
    for match in re.finditer(r"^===== PAGE (\d+) =====$", full_text, flags=re.MULTILINE):
        if match.start() > pos:
            break
        page_no = int(match.group(1))
    return page_no or 1


def line_around_pos(full_text: str, pos: int) -> str:
    line_start = full_text.rfind("\n", 0, pos) + 1
    line_end = full_text.find("\n", pos)
    if line_end < 0:
        line_end = len(full_text)
    line = " ".join(full_text[line_start:line_end].split())
    if line:
        return line
    snippet = " ".join(full_text[pos : pos + 80].split())
    return snippet


def find_heading_by_regex(
    full_text: str,
    patterns: tuple[str, ...],
    start_pos: int = 0,
) -> tuple[int, int, str] | None:
    matches: list[re.Match[str]] = []
    for pattern in patterns:
        match = re.search(pattern, full_text[start_pos:], flags=re.IGNORECASE | re.MULTILINE)
        if match:
            matches.append(match)
    if not matches:
        return None
    match = min(matches, key=lambda m: m.start())
    pos = start_pos + match.start()
    return page_for_pos(full_text, pos), pos, line_around_pos(full_text, pos)


def find_title(pages: list[tuple[int, list[str]]], full_text: str) -> tuple[int, int, str] | None:
    title = find_line_with_candidates(
        pages,
        full_text,
        ("\u9879\u76ee\u540d\u79f0", "\u9879\u76ee\u540d\u79f0\uff1a", "\u9879\u76ee\u540d\u79f0:"),
        page_start=1,
    )
    if title is not None:
        return title
    return find_first_nonempty_line(
        pages,
        full_text,
        page_start=1,
        skip_candidates=(
            "\u7533\u8bf7\u4ee3\u7801",
            "\u53d7\u7406\u90e8\u95e8",
            "\u56fd\u5bb6\u81ea\u7136\u79d1\u5b66\u57fa\u91d1",
            "\u9879\u76ee\u7533\u8bf7\u4e66",
            "\u57fa\u672c\u4fe1\u606f",
        ),
    )


def make_section_index(full_text: str) -> str:
    pages = split_pages(full_text)
    title = find_title(pages, full_text)
    abstract = find_heading_by_regex(full_text, HEADING_PATTERNS["chinese_abstract"])
    if abstract is not None:
        abstract = (abstract[0], abstract[1], "\u4e2d\u6587\u6458\u8981")
    else:
        abstract = find_line_with_candidates(
            pages,
            full_text,
            ("\u4e2d\u6587\u6458\u8981", "\u6458\u8981"),
            page_start=1,
        )
    if abstract is not None and abstract[2] != "\u4e2d\u6587\u6458\u8981":
        abstract_first = first_nonempty_after(pages, full_text, abstract)
        if abstract_first is not None:
            abstract = abstract_first
    project_rationale = find_heading_by_regex(full_text, HEADING_PATTERNS["project_rationale"])
    research_content = find_heading_by_regex(
        full_text,
        HEADING_PATTERNS["research_content"],
        start_pos=(project_rationale[1] + 1) if project_rationale else 0,
    )
    research_basis = find_heading_by_regex(
        full_text,
        HEADING_PATTERNS["research_basis"],
        start_pos=(research_content[1] + 1) if research_content else 0,
    )
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
        "- non-text figures and diagrams require human inspection.",
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


def review_stage_skeletons() -> dict[str, str]:
    return {
        "01_scientific_critique.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: scientific_critique
supporting_skill: scientific-critical-thinking
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- extracted/00_full_text.txt
- review/nsfc_review_cache.txt
output_file: review/01_scientific_critique.txt
generated_at: unknown
fallback_reason: not yet run

Scientific Critique

Role routing: first attempt an explicit scientific-critical-thinking skill call. If unavailable, complete this stage in the current agent and record fallback provenance.

To be completed: core scientific question, hypothesis coherence, design rigor, statistics, feasibility, risks, alternatives, and decision-level methodological concerns.
"""
        ),
        "02_literature_checks.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: literature_checks
supporting_skill: literature-review
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- extracted/00_full_text.txt
- review/nsfc_review_cache.txt
output_file: review/02_literature_checks.txt
generated_at: unknown
fallback_reason: not yet run

Targeted Literature Checks

Role routing: first attempt an explicit literature-review skill call. If unavailable, use available web/PubMed/Crossref searches or concise manual query synthesis and record fallback provenance.

To be completed: key novelty claims, closest prior work, claim conflicts, field saturation, and evidence-backed novelty boundary.
"""
        ),
        "03_reviewer2_stress_test.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: reviewer2_stress_test
supporting_skill: reviewer-2-simulator
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- extracted/00_full_text.txt
- review/nsfc_review_cache.txt
output_file: review/03_reviewer2_stress_test.txt
generated_at: unknown
fallback_reason: not yet run

Reviewer 2 Stress Test

Role routing: first attempt an explicit reviewer-2-simulator skill call. If unavailable, complete this stage in the current agent as a strict reviewer-2 role and record fallback provenance.

To be completed: strongest score-lowering objections, fatal or structural flaws, fixable weaknesses, and Kill-mode implications.
"""
        ),
        "04_peer_review_draft.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: peer_review_draft
supporting_skill: peer-review
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- review/nsfc_review_cache.txt
- review/01_scientific_critique.txt
- review/02_literature_checks.txt
- review/03_reviewer2_stress_test.txt
output_file: review/04_peer_review_draft.txt
generated_at: unknown
fallback_reason: not yet run

Peer Review Draft

Role routing: first attempt an explicit peer-review skill call to organize the grant-style judgment. If unavailable, complete this stage in the current agent and record fallback provenance.

To be completed: overall judgment, strengths, novelty, major concerns, minor concerns, feasibility, manual-review boundary, funding judgment, and an exact KILL-MODE DECISION section.
"""
        ),
        "05_final_review.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: final_scientific_writing
supporting_skill: scientific-writing
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- review/04_peer_review_draft.txt
output_file: review/05_final_review.txt
generated_at: unknown
fallback_reason: not yet run

Final Chinese Review

Role routing: first attempt an explicit scientific-writing skill call to polish 04_peer_review_draft.txt into a professional Chinese final review. scientific-writing must not change the evidence judgment or soften the Kill-mode decision.

To be completed: polished Chinese final review with an exact KILL-MODE DECISION section and manual-review reminders.
"""
        ),
        "06_submitted_review_comment.txt": (
            """NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: submitted_review_comment
supporting_skill: scientific-writing
attempted_skill_call: no
skill_call_result: not_attempted
execution_mode: unavailable_not_attempted
status: pending
input_files:
- review/05_final_review.txt
output_file: review/06_submitted_review_comment.txt
generated_at: unknown
fallback_reason: not yet run

Submitted Review Comment

Role routing: first attempt an explicit scientific-writing skill call to convert 05_final_review.txt into concise NSFC form-style review comments. Preserve the evidence judgment, A/B/C grade, funding opinion, cap-rule effects, and Kill-mode conclusion.

To be completed: form-ready comments with comprehensive evaluation, funding opinion, an exact KILL-MODE DECISION section, scientific evaluation description, specific review comments for the selected research attribute, and a manual-review reminder.
"""
        ),
    }


def report_text(proposal: Path, workdir: Path, metadata: dict, outputs: list[Path]) -> str:
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
    proposal_folder = proposal.parent
    parent_of_proposal_folder = proposal_folder.parent
    return parent_of_proposal_folder / f"nsfc-review-{safe_stem(proposal.name)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract NSFC proposal PDF/TXT into review workflow TXT files.")
    parser.add_argument("--proposal", required=True, help="Path to proposal PDF or TXT.")
    parser.add_argument(
        "--workdir",
        default=None,
        help="Review workflow directory. If omitted, creates nsfc-review-<proposal-stem> in the parent directory of the proposal folder.",
    )
    parser.add_argument("--password", default=None, help="Optional PDF password. Avoid shell history when possible.")
    parser.add_argument(
        "--copy-input",
        action="store_true",
        help="Copy the input file into workdir/input. Off by default to keep folders clean.",
    )
    parser.add_argument(
        "--init-review-files",
        action="store_true",
        help="Pre-create review stage skeleton files to help downstream agents continue the workflow.",
    )
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

    outputs: list[Path] = []
    suffix = proposal.suffix.lower()
    metadata: dict

    if suffix == ".pdf":
        full_text, metadata = extract_pdf_text(proposal, args.password)
        if metadata.get("status", "").startswith("ENCRYPTED_PDF"):
            action_path = extracted / "ACTION_REQUIRED_encrypted_pdf.txt"
            write_text(
                action_path,
                "The proposal PDF is encrypted or extraction is blocked.\n\n"
                "Ask the user which input format to use next:\n"
                "1. password for extraction,\n"
                "2. decrypted PDF,\n"
                "3. exported TXT,\n"
                "4. OCR text.\n\n"
                "Do not continue reviewing from the PDF until TXT is available.\n",
            )
            outputs.append(action_path)
        elif metadata.get("status") == "DEPENDENCY_MISSING":
            action_path = extracted / "ACTION_REQUIRED_pdf_dependency_or_txt.txt"
            write_text(
                action_path,
                "PDF extraction dependency is missing.\n\n"
                "Ask the user whether to install pypdf/PyPDF2, provide exported TXT, or provide OCR text.\n",
            )
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
        metadata = {
            "status": "UNSUPPORTED_INPUT_FORMAT",
            "message": "Provide PDF or TXT for this workflow.",
            "suffix": suffix,
        }

    if args.copy_input and metadata.get("status") not in {"UNSUPPORTED_INPUT_FORMAT"}:
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
    if (
        status.startswith("OK")
        or status == "LOW_TEXT_POSSIBLE_OCR_NEEDED"
        or status.startswith("ENCRYPTED_PDF")
        or status == "DEPENDENCY_MISSING"
    ):
        return 0
    return 4


if __name__ == "__main__":
    raise SystemExit(main())


