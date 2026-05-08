#!/usr/bin/env python
"""Collect NSFC review result artifacts for ranking.

This script scans TXT/MD review artifacts only. It never opens proposal PDFs.
It is aligned with nsfc-mianshang-review v0.5.7 output:
01-04 stage files, 05_final_review.txt, and 06_submitted_review_comment.txt.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    ("final_review", "review/05_final_review.txt", "primary"),
    ("submitted_comment", "review/06_submitted_review_comment.txt", "primary_form"),
    ("peer_review_draft", "review/04_peer_review_draft.txt", "stage"),
    ("reviewer2_stress_test", "review/03_reviewer2_stress_test.txt", "stage"),
    ("literature_checks", "review/02_literature_checks.txt", "stage"),
    ("scientific_critique", "review/01_scientific_critique.txt", "stage"),
    ("review_cache", "review/nsfc_review_cache.txt", "cache"),
    # Legacy fallback names from earlier prototypes.
    ("legacy_final_review", "review/04_final_review.txt", "legacy_primary"),
    ("legacy_final_review", "04_final_review.txt", "legacy_primary"),
    ("final_review", "05_final_review.txt", "primary"),
    ("submitted_comment", "06_submitted_review_comment.txt", "primary_form"),
    ("peer_review_draft", "04_peer_review_draft.txt", "stage"),
    ("reviewer2_stress_test", "03_reviewer2_stress_test.txt", "stage"),
    ("literature_checks", "02_literature_checks.txt", "stage"),
    ("scientific_critique", "01_scientific_critique.txt", "stage"),
    ("review_cache", "nsfc_review_cache.txt", "cache"),
)

REQUIRED_STAGE_NAMES = {
    "scientific_critique",
    "literature_checks",
    "reviewer2_stress_test",
    "peer_review_draft",
    "final_review",
    "submitted_comment",
}

PLACEHOLDER_MARKERS = (
    "To be completed",
    "status: pending",
    "status: partial",
    "placeholder",
    "TODO",
    "待补全",
    "待完成",
    "待填写",
)

PROTOCOL_VIOLATION_MARKERS = (
    "completed_with_protocol_violation",
    "protocol violation",
    "skill was installed but not called",
)

SCORE_PATTERNS = (
    re.compile(r"Total weighted score\s*[:=]\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100", re.I),
    re.compile(r"总加权分\s*[:：=]\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100"),
    re.compile(r"综合加权评分\s*[:：=]?\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100"),
    re.compile(r"加权总分\s*[:：=]?\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100"),
    re.compile(r"加权评分\s*[:：=]?\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100"),
    re.compile(r"总分\s*[:：=]\s*.*?([0-9]+(?:\.[0-9]+)?)\s*/\s*100"),
)

RECOMMENDATION_LINE_PATTERNS = (
    re.compile(r"(?:选择|资助建议|资助意见|最终建议|评审建议|funding recommendation|recommendation)\s*[:：]\s*(.+)", re.I),
    re.compile(r"【(?:选择|资助建议|资助意见|最终建议|评审建议)】\s*(.+)"),
    re.compile(r"KILL-MODE DECISION\s*[:：]\s*(.+)", re.I),
)

RECOMMENDATION_VALUE_PATTERNS = (
    re.compile(r"(不予资助|不建议资助|建议不资助|暂缓资助|可资助|可以资助|优先资助|可考虑支持)"),
    re.compile(r"(not recommended|recommended|priority support|fundable)", re.I),
)


@dataclass
class ArtifactInfo:
    role: str
    rel_path: str
    importance: str
    path: Path
    chars: int
    classification: str
    note: str
    header: dict[str, str]
    score: str
    recommendation: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def compact_chars(text: str) -> int:
    return len("".join(text.split()))


def parse_provenance_header(text: str) -> dict[str, str]:
    lines = text.splitlines()
    header: dict[str, str] = {}
    if not lines or lines[0].strip() != "NSFC_REVIEW_STAGE_PROVENANCE":
        return header
    for line in lines[1:80]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("To be completed", "## ", "# ")):
            break
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            header[key.strip()] = value.strip()
    return header


def extract_score(text: str) -> str:
    for pattern in SCORE_PATTERNS:
        match = pattern.search(text)
        if match:
            return f"{float(match.group(1)):.1f}/100"
    return "not_found"


def extract_recommendation(text: str) -> str:
    # Avoid matching form option lists such as "A. 优先资助 B. 可以资助 C. 不予资助".
    # Only trust explicit decision/recommendation lines.
    lines = [line.strip().strip("*") for line in text.splitlines()]
    for stripped in lines:
        if not stripped:
            continue
        for line_pattern in RECOMMENDATION_LINE_PATTERNS:
            line_match = line_pattern.search(stripped)
            if not line_match:
                continue
            value = line_match.group(1)
            for value_pattern in RECOMMENDATION_VALUE_PATTERNS:
                value_match = value_pattern.search(value)
                if value_match:
                    return value_match.group(1)
    for stripped in lines:
        if not stripped:
            continue
        if "choose one" in stripped.lower():
            continue
        if ("A." in stripped and "B." in stripped) or ("A、" in stripped and "B、" in stripped):
            continue
        if ("priority funding" in stripped.lower() and "fundable" in stripped.lower()) or (
            "优先资助" in stripped and ("可以资助" in stripped or "不予资助" in stripped)
        ):
            continue
        if "综合评价" in stripped and len(stripped) < 30:
            continue
        for value_pattern in RECOMMENDATION_VALUE_PATTERNS:
            value_match = value_pattern.search(stripped)
            if value_match:
                return value_match.group(1)
    return "not_found"


def classify_artifact(text: str, header: dict[str, str]) -> tuple[str, str]:
    chars = compact_chars(text)
    if chars == 0:
        return "placeholder_or_incomplete", "empty"

    lower = text.lower()
    if any(marker.lower() in lower for marker in PROTOCOL_VIOLATION_MARKERS):
        return "protocol_violation", f"chars={chars}"

    status = header.get("status", "").lower()
    execution_mode = header.get("execution_mode", "").lower()
    skill_result = header.get("skill_call_result", "").lower()
    attempted = header.get("attempted_skill_call", "").lower()

    if status in {"pending", "partial", "blocked"}:
        return "placeholder_or_incomplete", f"status={status}; chars={chars}"

    placeholder_hits = sum(1 for marker in PLACEHOLDER_MARKERS if marker.lower() in lower)
    if placeholder_hits and chars < 1800:
        return "placeholder_or_incomplete", f"placeholder_markers={placeholder_hits}; chars={chars}"

    if execution_mode == "explicit_skill_call" and skill_result == "success" and status == "completed":
        return "explicit_skill_call", f"chars={chars}"

    if execution_mode == "fallback_agent_role" and status == "completed":
        return "fallback_agent_role", f"chars={chars}"

    if attempted == "yes" and skill_result in {"permission_blocked", "call_failed", "not_installed", "runtime_not_supported"}:
        return "fallback_agent_role", f"skill_call_result={skill_result}; chars={chars}"

    if header and status == "completed":
        return "documented_nonstandard", f"execution_mode={execution_mode or 'missing'}; chars={chars}"

    if chars >= 1800:
        return "unknown_or_unverified", f"chars={chars}"

    return "placeholder_or_incomplete", f"thin_file; chars={chars}"


def scan_artifact(candidate: Path, role: str, rel_path: str, importance: str) -> ArtifactInfo | None:
    path = candidate / rel_path
    if not path.exists() or not path.is_file():
        return None
    text = read_text(path)
    header = parse_provenance_header(text)
    classification, note = classify_artifact(text, header)
    return ArtifactInfo(
        role=role,
        rel_path=rel_path,
        importance=importance,
        path=path,
        chars=compact_chars(text),
        classification=classification,
        note=note,
        header=header,
        score=extract_score(text),
        recommendation=extract_recommendation(text),
    )


def find_candidate_dirs(root: Path, recursive: bool = False) -> list[Path]:
    candidates: set[Path] = set()
    patterns = ("nsfc-review-*", "nsfc_review_*")
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_dir():
                candidates.add(path)
    if recursive:
        for pattern in patterns:
            for path in root.rglob(pattern):
                if path.is_dir():
                    candidates.add(path)
        for filename in ("05_final_review.txt", "06_submitted_review_comment.txt", "04_final_review.txt"):
            for path in root.rglob(filename):
                parent = path.parent.parent if path.parent.name == "review" else path.parent
                if parent.name.startswith(("nsfc-review-", "nsfc_review_")):
                    candidates.add(parent)
    return sorted(candidates, key=lambda p: str(p).lower())


def find_artifacts(candidate: Path) -> list[ArtifactInfo]:
    found: list[ArtifactInfo] = []
    seen: set[Path] = set()
    for role, rel_path, importance in ARTIFACTS:
        info = scan_artifact(candidate, role, rel_path, importance)
        if info and info.path not in seen:
            found.append(info)
            seen.add(info.path)
    if found:
        return found

    for path in sorted(candidate.rglob("*.txt"), key=lambda p: str(p).lower()):
        if "extracted" in {part.lower() for part in path.parts}:
            continue
        text = read_text(path)
        header = parse_provenance_header(text)
        classification, note = classify_artifact(text, header)
        found.append(
            ArtifactInfo(
                role="unmapped_txt",
                rel_path=str(path.relative_to(candidate)),
                importance="fallback_scan",
                path=path,
                chars=compact_chars(text),
                classification=classification,
                note=note,
                header=header,
                score=extract_score(text),
                recommendation=extract_recommendation(text),
            )
        )
    return found


def proposal_quality(artifacts: list[ArtifactInfo]) -> tuple[str, str]:
    if not artifacts:
        return "D", "no review TXT artifacts found"

    by_role = {artifact.role: artifact for artifact in artifacts}
    missing = sorted(role for role in REQUIRED_STAGE_NAMES if role not in by_role)
    classifications = [artifact.classification for artifact in artifacts]

    if any(cls == "placeholder_or_incomplete" for cls in classifications):
        return "D", "one or more artifacts are placeholders, blocked, partial, or too thin"

    final = by_role.get("final_review") or by_role.get("legacy_final_review")
    if not final:
        return "C", "missing 05_final_review.txt; scoring depends on stage files"

    if final.classification == "protocol_violation":
        return "C", "final review reports protocol violation"

    if final.role == "legacy_final_review":
        return "B", "legacy final review filename; usable but not v0.5.7-complete"

    if missing:
        return "B", "missing stages: " + ",".join(missing)

    major = [a for a in artifacts if a.role in REQUIRED_STAGE_NAMES]
    if all(a.classification == "explicit_skill_call" for a in major):
        return "A", "complete workflow with explicit supporting-skill provenance"

    if all(a.classification in {"explicit_skill_call", "fallback_agent_role", "documented_nonstandard"} for a in major):
        return "A-", "complete workflow with documented fallback/nonstandard provenance"

    if any(a.classification == "unknown_or_unverified" for a in major):
        return "B", "complete-looking workflow but some provenance is unknown"

    return "C", "review artifacts exist but quality requires manual inspection"


def workflow_status(artifacts: list[ArtifactInfo]) -> str:
    roles = {artifact.role for artifact in artifacts}
    if REQUIRED_STAGE_NAMES.issubset(roles):
        return "v0.5.7_complete"
    if "final_review" in roles and "submitted_comment" in roles:
        return "final_and_submitted_comment_present"
    if "legacy_final_review" in roles:
        return "legacy_final_review"
    if artifacts:
        return "partial_review_artifacts"
    return "missing_review_artifacts"


def make_inventory(root: Path, recursive: bool = False) -> str:
    lines = [
        "NSFC REVIEW RANKING INVENTORY",
        f"root: {root}",
        "scanner_version: 0.2.0",
        "aligned_with: nsfc-mianshang-review v0.5.7",
        "",
        "Use these TXT artifacts for ranking. Do not read proposal PDFs.",
        "Prefer review/05_final_review.txt and review/06_submitted_review_comment.txt.",
        f"recursive: {recursive}",
        "",
    ]
    candidates = find_candidate_dirs(root, recursive=recursive)
    if not candidates:
        lines.append("No review directories found.")
        return "\n".join(lines) + "\n"

    for idx, candidate in enumerate(candidates, start=1):
        artifacts = find_artifacts(candidate)
        quality, quality_note = proposal_quality(artifacts)
        lines.append(f"[{idx}] {candidate.name}")
        lines.append(f"dir: {candidate}")
        lines.append(f"workflow_status: {workflow_status(artifacts)}")
        lines.append(f"input_quality: {quality}")
        lines.append(f"input_quality_note: {quality_note}")
        if artifacts:
            final_like = next((a for a in artifacts if a.role in {"final_review", "legacy_final_review"}), None)
            submitted = next((a for a in artifacts if a.role == "submitted_comment"), None)
            if final_like:
                lines.append(f"source_score_from_final_review: {final_like.score}")
                lines.append(f"recommendation_from_final_review: {final_like.recommendation}")
            if submitted:
                lines.append(f"recommendation_from_submitted_comment: {submitted.recommendation}")
            lines.append("artifacts:")
            for artifact in artifacts:
                header_bits = []
                for key in ("workflow_version", "stage", "supporting_skill", "attempted_skill_call", "skill_call_result", "execution_mode", "status"):
                    if key in artifact.header:
                        header_bits.append(f"{key}={artifact.header[key]}")
                header_note = "; ".join(header_bits) if header_bits else "no_structured_header"
                lines.append(f"- role: {artifact.role}")
                lines.append(f"  importance: {artifact.importance}")
                lines.append(f"  path: {artifact.path}")
                lines.append(f"  provenance: {artifact.classification}; {artifact.note}")
                lines.append(f"  header: {header_note}")
                lines.append(f"  score: {artifact.score}")
                lines.append(f"  recommendation: {artifact.recommendation}")
        else:
            lines.append("artifacts: none")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect NSFC review TXT artifacts for ranking.")
    parser.add_argument("--root", required=True, help="Root folder containing review result folders.")
    parser.add_argument("--out", default=None, help="Output inventory TXT path.")
    parser.add_argument("--recursive", action="store_true", help="Also include nested nsfc-review-* folders.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Root folder not found or not a directory: {root}")
        return 2
    out = Path(args.out).expanduser().resolve() if args.out else root / "nsfc_review_ranking_inventory.txt"
    text = make_inventory(root, recursive=args.recursive)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
