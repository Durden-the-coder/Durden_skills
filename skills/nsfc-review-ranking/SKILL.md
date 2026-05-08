---
name: nsfc-review-ranking
version: 0.2.0
description: Rank multiple NSFC General Program review results with calibrated quantitative scores, A/B/C grades, provenance audit, and comparative Chinese rationale. Use when the user provides directories containing nsfc-mianshang-review outputs or final review TXT files and asks to compare, sort, grade, score, stratify, select top/bottom proposals, or produce a ranked summary report.
---

# NSFC Review Ranking

Use this skill to compare already-generated NSFC review results. Do not re-review proposal PDFs. Do not read original PDFs.

This skill is aligned with `nsfc-mianshang-review` `0.5.7+`. Prefer:

- `review/05_final_review.txt`
- `review/06_submitted_review_comment.txt`
- `review/01_scientific_critique.txt` through `review/04_peer_review_draft.txt`
- `review/nsfc_review_cache.txt`

Older `review/04_final_review.txt` outputs are supported as legacy inputs, but mark them as legacy and lower confidence.

## Inputs

Accept any of these:

- A root folder containing multiple `nsfc-review-*` review directories.
- A list of review directories.
- A list of final review TXT files.
- A mixed folder containing `05_final_review.txt`, `06_submitted_review_comment.txt`, stage files, or `nsfc_review_cache.txt`.

If a root folder is provided, discover candidates with:

```bash
<python> scripts/collect_review_results.py --root <root_dir> --out <root_dir>/nsfc_review_ranking_inventory.txt
```

By default, the script only scans first-level `nsfc-review-*` / `nsfc_review_*` directories under the root. Use `--recursive` only when the user explicitly wants nested review folders included.

Read the generated inventory, then read only the needed TXT review artifacts. Never read proposal PDFs.

## Provenance And Input Quality

Before scoring, audit whether each input artifact is complete and where it appears to come from. Do not treat a complete explicit-skill workflow, a documented fallback, a protocol violation, and an unfilled skeleton as equivalent evidence.

The inventory classifies artifacts as:

- `explicit_skill_call`: structured provenance says the supporting skill was called successfully.
- `fallback_agent_role`: structured provenance says the supporting skill was unavailable, blocked, or failed and the current agent completed the role directly.
- `documented_nonstandard`: a structured header exists and status is completed, but execution mode is not one of the expected values.
- `unknown_or_unverified`: substantive content exists but provenance is unclear.
- `protocol_violation`: the artifact reports protocol violation or supporting-skill bypass.
- `placeholder_or_incomplete`: empty, pending, partial, blocked, or still contains skeleton text.
- `unreadable`: the artifact cannot be read.

Assign each proposal an input quality grade:

- `A`: `01-06` files are complete and major stage provenance is explicit.
- `A-`: `01-06` files are complete and fallback/nonstandard provenance is documented consistently.
- `B`: final review is substantive, but some stage files are missing, legacy, or have unknown provenance.
- `C`: final review is missing/thin, protocol-violating, or scoring depends heavily on partial stage files.
- `D`: one or more required files are placeholders, unreadable, missing, or clearly incomplete.

Use input quality as a confidence label, not as an automatic scientific score. When evidence quality is `C` or `D`, include a confidence limitation and avoid overstating fine score differences.

## Ranking Goal

Produce relative ranking even when all proposals receive negative recommendations. The output should answer:

- Which proposals are least bad / most fundable within this batch?
- Which are clearly weaker?
- Are score differences meaningful or essentially tied?
- Which defects drive the separation?
- Are the differences derived from scientific merit or from input quality uncertainty?

## Scoring Policy

Use two score fields when possible:

1. `source_score`: the score already present in `05_final_review.txt`, usually `Total weighted score: x/100`.
2. `calibrated_ranking_score`: your cross-batch score after comparing all projects.

Do not blindly copy the source score. Use it as the starting anchor, then calibrate across the batch:

- Preserve clear within-project judgments from `05_final_review.txt`.
- Adjust only when two reports use the same score band but the comparative defects are clearly different.
- Explain any adjustment of 5 points or more.
- Keep the calibrated score on a 100-point internal triage scale.

Scores are not official NSFC scores. Report grades with an `A/B/C` system plus `+/-`; do not output `D/E/F` grades.

- `A+ / 90-100`: outstanding or clear priority for support.
- `A / 85-89`: recommended for support.
- `A- / 80-84`: fundable; can be considered for support.
- `B+ / 75-79`: borderline but relatively strong within the borderline group.
- `B / 70-74`: borderline.
- `B- / 65-69`: borderline but relatively weak.
- `C+ / 55-64`: not recommended, but has local strengths or salvageable elements.
- `C / 45-54`: not recommended.
- `C- / 0-44`: clearly not recommended; structural defects dominate.

For kill-mode or internal screening, weak applications may cluster in `C+/C/C-`, but still separate them precisely with numeric scores and relative rank.

## Ranking Rubric

Use `references/scoring-rubric.txt`. This ranking rubric is for cross-project calibration. It does not replace the per-project free-exploration or goal-oriented rubric inside `nsfc-mianshang-review`.

When `05_final_review.txt` already contains per-project dimensions and `Total weighted score: x/100`, extract them first. Then use the ranking rubric to compare projects across a batch.

Do not let good writing, topic importance, platform resources, or generic preliminary work erase fatal scientific defects.

## Workflow

1. Discover review artifacts with `scripts/collect_review_results.py`.
2. Read `nsfc_review_ranking_inventory.txt`.
3. Audit provenance and input completeness for each candidate.
4. Read `05_final_review.txt` and `06_submitted_review_comment.txt` first.
5. Read `01-04` stage files only when final reviews are thin, inconsistent, or when tie-breaking needs more detail.
6. Build a comparison table with project id/name, source file, source score, calibrated score, recommendation, fatal flaws, major strengths, major concerns, input quality, and provenance status.
7. Calibrate scores across the batch:
   - compare adjacent proposals;
   - avoid identical scores unless genuinely indistinguishable;
   - use 1-3 point gaps for near ties;
   - use 5-10 point gaps for clear qualitative differences;
   - use 10+ point gaps for different fundability classes.
8. Assign final A/B/C grade and rank.
9. Write a polished Chinese TXT report.
10. Also return a concise Chinese session summary to the user.

## Required Output

Write a TXT report named `nsfc_review_ranking_report.txt` in the root folder provided by the user, unless they specify another path.

Also print a concise result summary in the chat/session after writing the file. This session summary is mandatory because users often need to inspect the result without opening the TXT file first.

The session summary must include:

- output file path;
- number of discovered review folders;
- number of ranked proposals and number excluded for input-quality reasons;
- top 3 ranked proposals with calibrated score, grade, input quality, and recommendation;
- bottom 3 ranked proposals among rankable proposals;
- any excluded `D` quality proposals;
- 2-4 key caveats, especially missing source scores, fallback provenance, protocol violations, or human-review boundaries.

Keep the session summary compact. Do not paste the full TXT report into the chat unless the user explicitly asks for it.

Use this structure for the TXT report:

```text
国自然面上项目评审结果排序报告

一、排序原则与评分说明

二、总排名表
Rank | 项目 | 原始分 | 横向校准分 | 等级 | 输入质量 | workflow 状态 | 建议 | 主要排序依据

三、分项评分与校准说明
项目 | 科学问题 | 创新性/文献位置 | 机制逻辑 | 设计可行性 | 前期基础 | 写作可评审性 | 原始分 | 校准分

四、输入质量与来源审计
逐项说明 provenance、supporting skill 调用情况、fallback/protocol violation、缺失文件和人工审核边界。

五、逐项简评

六、相邻项目比较

七、人工复核提醒
```
The final report and session summary must both be in polished Chinese.

## Tie-Breaking Rules

When total scores are close:

1. Prefer stronger novelty over better polish.
2. Prefer closed mechanistic logic over broad ambition.
3. Prefer feasible decisive experiments over many exploratory tasks.
4. Prefer direct preliminary evidence over platform claims.
5. In kill-mode, rank fewer fatal flaws above more general strengths.
6. If scientific merit is tied, prefer higher input quality only as a confidence factor, not as the primary score driver.

## Integrity Rules

- Do not fabricate details absent from review artifacts.
- Do not assume a file was produced by a supporting skill unless structured provenance documents it.
- If the review artifacts are too thin, state uncertainty and read available stage TXT files before scoring.
- If only final reviews exist, score from final reviews and mark the evidence base as limited.
- If a final review is an unfilled skeleton, do not score from it. Read stage files if available and assign input quality `C` or `D`.
- If a report says figures, work conditions, CV, representative papers, attachments, or ethics documents require human review, include this as a confidence limitation, not as automatic rejection.
- Preserve confidentiality: do not copy large proposal text into the ranking report.
