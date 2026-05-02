---
name: nsfc-mianshang-review
version: 0.4.2
description: Review National Natural Science Foundation of China General Program applications with a cache-first, PDF-to-TXT, staged workflow. Use for NSFC mian-shang proposal review, scientific value, innovation, feasibility, and structured Chinese review comments. Coordinates literature-review, scientific-critical-thinking, peer-review, reviewer-2-simulator, and scientific-writing while minimizing token use.
---

# NSFC Mianshang Review

Use this skill as the workflow entry point for NSFC General Program proposal review.

## Non-Negotiable File Rules

- If the user provides a PDF, local PDF-to-TXT extraction is the default entry behavior.
- Read the PDF only during the PDF-to-TXT conversion step.
- After TXT extraction succeeds, never read the PDF again.
- Later review work must use TXT files, cache files, and short copied evidence snippets.
- If the PDF is encrypted or extraction is blocked, do not treat this as a normal failure. Ask for password, decrypted PDF, exported TXT, or OCR text.
- Prefer `.txt` as the primary working copy. Markdown is optional and only for human-facing summaries.
- Run all workflow artifacts under the user-specified review directory.
- Do not write workflow artifacts to system folders, user profile cache locations, global skill directories, or agent home directories by default.
- If the user does not provide a review directory, create `nsfc_review_<proposal-stem>` in the parent directory of the proposal folder.
- Keep the proposal folder clean. Do not write extracted or review files into the proposal folder unless explicitly asked.
- Chinese source text is expected. Produce final review text in polished Chinese by default.

## Default File Layout

```text
review_dir/
  extracted/
    00_full_text.txt
    01_section_index.txt
    extraction_report.txt
  review/
    nsfc_review_cache.txt
    01_scientific_critique.txt
    02_literature_checks.txt
    03_reviewer2_stress_test.txt
    04_final_review.txt
```

## Primary Review Scope

Default focus:

1. 标题
2. 中文摘要
3. 立项依据
4. 研究内容（含特色与创新点、年度计划）
5. 研究基础（含可行性分析）

Default low-priority exclusions:

- budget details
- attachment directory mechanics
- routine form-filling checks
- recommendation-letter logistics
- generic declarations

## Required Workflow

### 1. Prepare Text Working Copy

If the input is a PDF, run:

```bash
<python> scripts/extract_nsfc_text.py --proposal <proposal.pdf-or-txt> --workdir <review_dir>
```

If the environment is unreliable at creating new files outside its current workspace, add:

```bash
--init-review-files
```

If extraction reports encrypted PDF status, stop and ask the user for the next input format. Do not continue reviewing from the PDF.

### 2. Route Before Deep Review

Start each review with a short routing note:

- task type: full review / section review / internal pre-screen / revision planning
- available artifacts: TXT, section index, cache, final review draft
- skills to use and why
- excluded low-value administrative materials

Default routing:

- title / abstract -> `peer-review`
- project rationale -> `scientific-critical-thinking` + targeted `literature-review`
- research content -> `scientific-critical-thinking` + `reviewer-2-simulator` + `peer-review`
- research basis -> `scientific-critical-thinking` + `peer-review`
- final polishing -> `scientific-writing`

### 3. Build Or Update Review Cache

Before final judgment, create `review/nsfc_review_cache.txt`. Do not summarize the entire proposal. Extract only decision-relevant content.

Required cache fields:

- BASIC INFORMATION
- CORE SCIENTIFIC QUESTION
- CENTRAL HYPOTHESIS OR MAIN LOGIC
- SIGNIFICANCE CLAIMS
- RESEARCH OBJECTIVES AND CONTENT
- CLAIMED INNOVATION
- TECHNICAL ROUTE
- PRELIMINARY BASIS AND FEASIBILITY
- RISKS AND ALTERNATIVES
- APPLICANT/TEAM FIT
- RELATED PROJECT OVERLAP OR CONTINUITY
- KEY LITERATURE CLAIMS TO VERIFY
- CANDIDATE MAJOR CONCERNS
- CANDIDATE MINOR CONCERNS

### 4. Scientific Critique

Use `scientific-critical-thinking` to check:

- whether the central question is a real basic-science question
- whether the research attribute matches the proposal content
- whether aims answer the scientific question rather than list techniques
- whether controls, sample sizes, validation paths, and endpoints are adequate
- whether risk and alternatives are concrete enough

### 5. Targeted Literature Checks

Use `literature-review` only for key claims:

- verify the most important novelty claims
- identify obvious missing work or competing explanations
- check whether the proposed gap is real and current

### 6. Stress Test

Use `reviewer-2-simulator` after the cache and critique:

- produce the strongest score-lowering arguments
- focus on top issues that would matter to NSFC reviewers
- distinguish revisable weaknesses from structural flaws

### 7. Final Review

Use `peer-review` to structure the final judgment and `scientific-writing` to polish it.

Recommended sections:

```text
OVERALL ASSESSMENT
STRENGTHS
MAJOR CONCERNS
MINOR CONCERNS
FEASIBILITY AND RISK ASSESSMENT
INNOVATION ASSESSMENT
SUGGESTIONS FOR REVISION
FUNDING RECOMMENDATION OR PRIORITY
```

For internal kill-mode review, add:

```text
FATAL FLAWS OR DECISION-LEVEL DEFECTS
```

## Kill-Mode Decision Rule

When the user asks for internal pre-screening, triage, or kill-mode review:

- do not let general significance, available platforms, or decent preliminary basis outweigh structural flaws
- treat the following as potentially fatal unless clearly neutralized by the proposal itself:
  - the core novelty claim is weak or already occupied by prior work
  - the main mechanistic chain is not designed to close with decisive experiments
  - the proposal is overloaded, diffuse, or tries to do too many partially connected things
  - a high-risk hypothesis is central but has weak direct preliminary support
  - translational extensions materially dilute the core basic-science question
- if two or more structural flaws remain after considering the proposal's own evidence, default to `not recommended for support`
- let `scientific-critical-thinking` and `reviewer-2-simulator` drive fundability; `peer-review` organizes but should not soften the decision

## State Machine

Use the workflow as a state machine:

1. `PDF_OR_TXT_INPUT`
2. `TXT_READY`
3. `CACHE_READY`
4. `SCIENTIFIC_CRITIQUE_READY`
5. `LITERATURE_CHECKS_READY`
6. `STRESS_TEST_READY`
7. `FINAL_REVIEW_READY`

At the start of every turn, identify the latest completed state from files in the review directory, then continue from the next state.

## Manual Review Boundary

If key claims depend on non-text materials that were not reliably converted into text, the final review must explicitly remind the user to inspect:

- mechanism diagrams / model schematics
- technical workflow diagrams
- experimental result figures
- microscopy panels, gels, blots, plots, and other image-based evidence

## References

- `references/scoring-rubric.txt`
- `references/output-templates.txt`

## Integrity

- Do not generate a complete grant application for the applicant.
- Do not fabricate policy requirements, citations, project details, or reviewer criteria.
- If generative AI use is discussed, remind the user that NSFC 2026 requires human verification and truthful disclosure of AI-assisted content.
