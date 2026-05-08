---
name: nsfc-mianshang-review
version: 0.5.7
description: Review NSFC General Program grant proposals with a PDF-to-TXT, cache-first, staged workflow. Use for Chinese NSFC mian-shang proposal review, kill-mode internal triage, novelty checks, scientific critique, reviewer-2 stress testing, and polished Chinese final review. Explicitly routes supporting skills when available and falls back to equivalent in-agent roles when unavailable.
allowed-tools: Read Write Edit Bash WebSearch Skill
license: MIT license
metadata:
    skill-author: Durden
---

# NSFC General Program Review

Use this skill as the workflow entry point for NSFC General Program proposal review. It coordinates PDF/TXT preparation, cache-first analysis, and staged use of the bundled review skills.

## Execution Fast Path

For full-review tasks, follow this exact path before reading detailed references:

1. Convert the proposal PDF/TXT into `extracted/00_full_text.txt`, `extracted/01_section_index.txt`, and `extracted/extraction_report.txt` by running `scripts/extract_nsfc_text.py --init-review-files`.
2. Build or update `review/nsfc_review_cache.txt` from TXT only.
3. Produce one file per supporting skill, in order:
   - `01_scientific_critique.txt` using `scientific-critical-thinking`
   - `02_literature_checks.txt` using `literature-review`
   - `03_reviewer2_stress_test.txt` using `reviewer-2-simulator`
   - `04_peer_review_draft.txt` using `peer-review`
   - `05_final_review.txt` using `scientific-writing`
   - `06_submitted_review_comment.txt` using `scientific-writing` as a form-comment adapter
4. Before writing each stage file, attempt the explicit supporting skill call when the runtime exposes a Skill mechanism.
5. If a supporting skill cannot be called, continue with fallback, but record the exact provenance and use `completed_with_protocol_violation` when a visible/installed skill was not attempted.
6. Identify the proposal's research attribute as `free_exploration`, `goal_oriented`, or `unclear`, and include an attribute-match judgment in `04_peer_review_draft.txt`, `05_final_review.txt`, and `06_submitted_review_comment.txt`.
7. Keep Kill-mode judgment in every full workflow by default; the user does not need to request it separately. `04_peer_review_draft.txt`, `05_final_review.txt`, and `06_submitted_review_comment.txt` must contain the exact heading `KILL-MODE DECISION`.
8. When assigning A/B/C priority or comparing proposals, use `references/scoring-rubric.txt`: exact matching rubric dimensions, 0-5 raw dimension scores, weighted points, total weighted score out of 100, cap rules, and ethics/compliance gate.
9. End with `06_submitted_review_comment.txt`, a concise form-ready comment file matching NSFC review-table fields, preserving a brief `KILL-MODE DECISION`, and ending with a manual-review reminder.

Detailed rules are below. Use `references/output-templates.txt` for templates and `references/scoring-rubric.txt` when consistent ratings, A/B/C grades, attribute mismatch, or ranking support is needed.

## When to Use This Skill

Use this skill when:

- reviewing NSFC General Program / 面上项目 proposals;
- running internal pre-submission triage or kill-mode review;
- extracting PDF proposal text into staged review artifacts;
- evaluating novelty, scientific logic, feasibility, risk, and funding priority;
- producing polished Chinese review comments from staged evidence files.

## When Not to Use This Skill

Do not use this skill to:

- generate a full grant application for an applicant;
- review unrelated journal manuscripts when NSFC proposal structure is irrelevant;
- perform budget-only, attachment-only, or administrative-only checks;
- inspect confidential non-text figures unless the user explicitly provides safe access;
- bypass human expert review for final funding, ethics, biosafety, or confidentiality decisions.

## Non-Interactive Execution Policy

For a single explicitly specified proposal, continue through workflow stages automatically unless extraction fails, a required password is missing, the output directory is unsafe, or a safety/compliance issue appears. Do not stop at normal single-proposal stage boundaries to ask the user to say `go`.

For batch workflows, this non-interactive policy applies only to extraction/preparation QC and review-task-card generation. Do not perform model-based review for multiple proposals in the same agent window/session. Each queued proposal should be reviewed in a fresh agent window/session using its generated task card.

If the runtime asks for tool permission, request the smallest useful action scope, preferably limited to reading proposal-derived TXT files, running `scripts/extract_nsfc_text.py`, and writing artifacts under the review directory.

## Non-Negotiable File Rules

- If the user provides a PDF, local PDF-to-TXT extraction is the default entry behavior of this workflow. Do not require manual step-by-step user preparation unless extraction is blocked.
- If the input is a PDF, read it only during the PDF-to-TXT conversion step.
- After TXT extraction succeeds, never read the PDF again. All later review work must use TXT files, cache files, and short copied evidence snippets.
- If the PDF is encrypted or text extraction is blocked, do not treat this as a normal failure. Ask the user which format they want to provide next: password, decrypted PDF, exported TXT, or OCR text.
- Only require human intervention for PDF preparation when one of the following is true:
  - the PDF is encrypted and no password is available;
  - the PDF is image-based and OCR text is not available;
  - the extracted text is too incomplete or too corrupted to support review;
  - a safe local review directory cannot be created.
- Prefer `.txt` as the primary working copy. Markdown is optional and only for human-facing summaries.
- Run all generated workflow artifacts under the user-specified review directory. Do not write to system, global agent, or package/cache directories.
- All code execution for this workflow must stay inside the user-provided review directory or the inferred proposal-local review directory.
- Do not write workflow artifacts to system folders, user profile cache locations, global skill directories, or agent home directories by default.
- If a safe local review workspace cannot be created without writing to a protected or unrelated directory, stop and ask the user for a review directory.
- The user should only need to provide the proposal path and, when needed, the PDF password. If the user does not provide a review directory, create a clean proposal-specific review folder in the parent directory of the proposal folder. Example: for `D:\AI projects\claude_code\2026国自然评审\项目书\proposal.pdf`, use `D:\AI projects\claude_code\2026国自然评审\nsfc-review-proposal\`.
- Keep the proposal folder clean. Do not write extracted or review files into the proposal folder unless the user explicitly asks.
- Chinese source text is expected. It does not reduce workflow quality. Preserve scientific terms accurately and produce final review text in polished Chinese by default.

## Scope

Review these components:

- Basic project identity: title, field, keywords, research attribute, duration, collaborators.
- Title.
- Chinese abstract.
- Project rationale: scientific value, research gap, significance, domestic/international status, key scientific question.
- Research content: objectives, scientific questions, tasks, technical route, distinctive features, innovation, annual plan.
- Research basis: prior work, preliminary data, feasibility analysis, risks and mitigation, and working conditions directly relevant to feasibility.
- Related ongoing/completed projects only when they affect overlap, continuity, feasibility, or independence.
- Applicant/team background only when it affects ability to complete the proposed work.
- Representative papers only when they support preliminary basis, novelty, or feasibility.
- Non-text visual materials only through explicit human review. This includes mechanism schematics, technical workflow diagrams, and experimental result figures that are not faithfully captured by text extraction.

Exclude low-value administrative review by default: budget details, attachment directory mechanics, unit-consistency declarations, recommendation-letter logistics, routine certificates, and generic form-filling checks.

Also treat figure-heavy, non-text proposal content as a manual-review boundary by default. If key claims depend on images, diagrams, gels, microscopy panels, model schematics, or workflow figures that were not reliably converted into text, the final review must explicitly say those materials still require human inspection.

## Research Attribute And Scoring

For every full review, record the applicant-selected research attribute and judge whether the proposal content matches it:

- `free_exploration`: curiosity/frontier-driven basic research.
- `goal_oriented`: basic research driven by economic/social/national/clinical need.
- `unclear`: attribute is missing or cannot be confidently extracted.

Use two evidence chains:

```text
free_exploration:
academic frontier or unknown phenomenon
-> basic scientific question
-> original hypothesis/mechanism/principle
-> generalizable new knowledge

goal_oriented:
economic/social/national/clinical need
-> key bottleneck
-> underlying unknown basic scientific problem
-> mechanistic research in this proposal
-> generalizable new knowledge
```

Attribute mismatch levels:

- `none`: selected attribute and proposal logic are aligned.
- `mild`: wording is imperfect, but the scientific logic supports the selected attribute.
- `moderate`: label and main logic are visibly misaligned, but a scientific question still exists; maximum grade B.
- `severe`: the selected attribute is central to the proposal logic but the chain fails; treat as a decision-level defect and usually grade C.

Use `references/scoring-rubric.txt` for 0-5 scoring details, weights, cap rules, and A/B/C mapping. Do not treat the weighted score as automatic: cap rules, ethics/compliance gates, and Kill-mode judgment can override the numeric total.

Scoring output is low-freedom and must be reproducible:

- Select exactly one rubric table: `free_exploration` or `goal_oriented`.
- Use the exact dimension names and weights from `references/scoring-rubric.txt`.
- Do not rename, merge, split, replace, or omit rubric dimensions.
- For each dimension, output `raw_score / 5`, `weight`, and `weighted_points = raw_score / 5 * weight`.
- Output `Total weighted score: <x>/100`.
- Output `Grade before cap rules`, `Cap rules triggered`, `Final grade after cap rules`, and `Funding opinion`.
- Do not report the final weighted score only as a 0-5 average such as `2.4/5`; this is not sufficient for ranking or cross-proposal comparison.

## Workflow Artifacts

Use this structure under the user-specified review directory:

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
    04_peer_review_draft.txt
    05_final_review.txt
    06_submitted_review_comment.txt
```

For batch jobs, also use:

```text
work_root/
  _batch/
    manifest.tsv
    extraction_qc_report.txt
    review_queue.tsv
    review_status.tsv
```

Create TXT artifacts first with:

```bash
<python> scripts/extract_nsfc_text.py --proposal <proposal.pdf-or-txt> [--password <pdf-password>] --init-review-files
```

If the user explicitly provides a review directory, add:

```bash
--workdir <review_dir>
```

If `--workdir` is omitted, the script creates `nsfc-review-<proposal-stem>` in the parent directory of the folder containing the proposal. `--init-review-files` pre-creates the review-stage skeleton files under `review/` so the workflow can continue without a separate file-creation prompt.

## Batch Workflow

For multiple proposals, split the job into deterministic preparation and one-proposal-per-session model review. Batch mode prepares files and task cards only; it must not perform model-based review for multiple proposals in the same session.

### Batch Step 1: Extract And QC

Run this first on the proposal folder:

```bash
<python> scripts/batch_extract_and_qc.py --proposal-dir <proposal_dir>
```

Optional arguments:

```bash
--work-root <work_root>
--batch-dir <work_root>/_batch
--password <shared_password>
--password-file <passwords.tsv>
--limit <N>
```

`passwords.tsv` should be UTF-8 tab-separated with columns:

```text
file	password
proposal_a.pdf	password-a
proposal_b.pdf	password-b
```

This step must not perform scientific review. It only creates or updates `nsfc-review-*` folders, initializes review skeletons, and writes:

- `_batch/manifest.tsv`
- `_batch/extraction_qc_report.txt`
- `_batch/review_queue.tsv`
- `_batch/review_status.tsv`
- `_batch/review_task_index.tsv`
- `_batch/review_prompts.txt`
- `_batch/review_tasks/<index>_<proposal>.md`

QC checks include:

- `00_full_text.txt` exists and has sufficient text volume;
- `01_section_index.txt` contains title, Chinese abstract, project rationale, research content, and research basis;
- extraction report does not show encrypted/missing-dependency/unsupported-input errors;
- review skeleton files exist;
- review skeleton files contain required provenance headers.

Only proposals with `status: READY_FOR_REVIEW` should enter model-based review. Each such proposal receives a task card under `_batch/review_tasks/`.

This is extraction/preparation QC only. It does not certify that model-based review has completed.

### Batch Step 2: New Session Review Tasks

After batch preparation, stop the current batch session and tell the user to open a new agent window/session for review.

Use one generated task card per new session:

```text
读取并执行：<work_root>/_batch/review_tasks/001_<proposal>.md
```

The task card contains the review directory, allowed input files, required stage files, scoring constraints, completion QC command, and a stop-after-this-project instruction.

The first task should be treated as the pilot review. After it finishes, the human check should confirm:

- extracted full text is complete enough;
- section index is aligned;
- cache is decision-relevant, not a full-text summary;
- stage files are substantive and have `status: completed`;
- provenance headers correctly report `explicit_skill_call` or `fallback_agent_role`;
- final review is polished Chinese and contains manual-review boundaries.

### Batch Step 3: Repeat One Task Per New Session

For each remaining queued proposal, open another fresh agent window/session and execute the next task card. Do not ask one agent session to review several proposals in sequence.

Update `_batch/review_status.tsv` after every proposal:

```text
NOT_STARTED
IN_PROGRESS
COMPLETED
FAILED
NEEDS_HUMAN_REVIEW
```

Do not let one failed proposal affect another proposal. Record the failure reason and start the next task only in a fresh session.

### Batch Step 4: Review Completion QC

After model-based review, run review-completion QC on existing `nsfc-review-*` folders:

```bash
<python> scripts/review_completion_qc.py --work-root <work_root>
```

This checks whether `01` through `06` review files are completed, whether supporting skill provenance is explicit/fallback/protocol-violating, and whether the final review contains Kill-mode judgment, manual-review reminders, a funding recommendation, and a form-ready submitted review comment. This step is separate from extraction QC so batch preparation remains fast and deterministic.

## Required Provenance Headers

Every generated stage file must start with a provenance header. Keep the header when editing the file, and update it before marking the stage complete.

For `01_scientific_critique.txt`, `02_literature_checks.txt`, and `03_reviewer2_stress_test.txt`, use:

```text
NSFC_REVIEW_STAGE_PROVENANCE
workflow_skill: nsfc-mianshang-review
workflow_version: 0.5.6
stage: <scientific_critique | literature_checks | reviewer2_stress_test>
supporting_skill: <scientific-critical-thinking | literature-review | reviewer-2-simulator>
attempted_skill_call: <yes | no>
skill_call_result: <success | unavailable | failed | permission_blocked | runtime_not_supported | not_attempted>
execution_mode: <explicit_skill_call | fallback_agent_role | unavailable_not_attempted>
status: <completed | completed_with_protocol_violation | partial | blocked | pending>
input_files:
- extracted/00_full_text.txt
- review/nsfc_review_cache.txt
output_file: review/<stage_file_name>.txt
generated_at: <YYYY-MM-DD HH:MM local time, or unknown>
fallback_reason: <none | supporting skill unavailable | skill call failed | runtime does not support skill-to-skill routing | permission blocked | skill was installed but not called | other>
```

Use this closed vocabulary for `skill_call_result`:

```text
success
not_installed
permission_blocked
runtime_not_supported
call_failed
not_attempted
```

Rules for these values:

- Use `success` only after the supporting skill was actually invoked.
- Use `not_installed` only after the runtime indicates the named skill is unavailable.
- Use `permission_blocked` only when the runtime or user denies the call.
- Use `runtime_not_supported` only when the environment has no skill-to-skill call mechanism.
- Use `call_failed` only after a real call attempt fails.
- Use `not_attempted` only when no call attempt was made. `not_attempted` plus substantive output must be treated as a protocol issue unless the runtime truly lacks any Skill mechanism.

For `04_peer_review_draft.txt` and `05_final_review.txt`, use the same single-supporting-skill stage header pattern as above.

`04_peer_review_draft.txt` must use:

```text
stage: peer_review_draft
supporting_skill: peer-review
output_file: review/04_peer_review_draft.txt
input_files:
- review/nsfc_review_cache.txt
- review/01_scientific_critique.txt
- review/02_literature_checks.txt
- review/03_reviewer2_stress_test.txt
```

`05_final_review.txt` must use:

```text
stage: final_scientific_writing
supporting_skill: scientific-writing
output_file: review/05_final_review.txt
input_files:
- review/04_peer_review_draft.txt
```

`06_submitted_review_comment.txt` must use:

```text
stage: submitted_review_comment
supporting_skill: scientific-writing
output_file: review/06_submitted_review_comment.txt
input_files:
- review/05_final_review.txt
```

Rules:

- Do not write `status: completed` until the file contains substantive analysis and no `待补充` placeholders.
- Use `execution_mode: explicit_skill_call` only when the runtime actually exposed and invoked the supporting skill.
- Before writing a stage file, you must attempt an explicit supporting skill call when the runtime exposes a Skill mechanism.
- Use `attempted_skill_call: yes` only after an actual call attempt. Do not use it for mental simulation or role-playing.
- Use `execution_mode: fallback_agent_role` when the current agent completed the role because explicit skill invocation was unavailable or failed.
- If the supporting skill is installed or visible but no explicit call was attempted, do not write `status: completed`; write `status: completed_with_protocol_violation`.
- Do not pair `attempted_skill_call: no` with `skill_call_result: runtime_not_supported`; use `not_attempted` unless the runtime itself explicitly reports no Skill mechanism.
- If provenance is unknown, write `execution_mode: fallback_agent_role` and state the uncertainty in `fallback_reason`; do not imply a skill call occurred.
- Downstream ranking depends on these headers. Missing or vague provenance should be treated as lower input-quality evidence.

## Required Workflow

### 1. Prepare Text Working Copy

If the proposal is a PDF, the workflow should automatically begin by running `scripts/extract_nsfc_text.py` with an available Python runtime to create `extracted/00_full_text.txt` and `extracted/extraction_report.txt`.

If the proposal is already TXT, copy or reference it as `extracted/00_full_text.txt` inside the review directory.

If no workdir is provided, infer one from the proposal path by placing `nsfc-review-<proposal-stem>` in the parent directory of the folder containing the proposal.

If extraction reports `ENCRYPTED_PDF`, stop and ask the user for the next input format. Do not continue reviewing from the PDF. This is an action-required state, not a workflow failure.

Do not redirect extraction outputs into system folders, agent cache locations, or global skill directories. If the inferred path is unsafe, ask for a local review directory before running extraction.

### 2. Route Before Deep Review

Start each review with a short routing note:

- Task type: full review, section review, pre-submission self-check, or revision planning.
- Available artifacts: TXT, section index, cache, final review draft.
- Skills to use and why.
- Excluded low-value administrative materials.

Default skill routing:

- Title and Chinese abstract: `peer-review` for quick proposal positioning and overall framing.
- Project rationale: `scientific-critical-thinking` plus targeted `literature-review`.
- Research content: `scientific-critical-thinking`, `reviewer-2-simulator`, and `peer-review`.
- Research basis: `scientific-critical-thinking` and `peer-review`.
- `scientific-critical-thinking`: scientific question, causal logic, design rigor, statistics, feasibility, risk, overclaims.
- `literature-review`: targeted novelty, gap, and field-context checks.
- `reviewer-2-simulator`: harsh pre-submission stress test and likely reviewer objections.
- `peer-review`: structured grant-style evaluation and final organization.
- `scientific-writing`: polished Chinese or English review comments, revision advice, or response text.

Supporting skill routing policy:

- At each stage, first attempt to explicitly load or call the named supporting skill if the runtime exposes a Skill mechanism.
- Treat explicit skill calls as protocol-required, not optional polish. Do not choose fallback merely because the current agent can complete the role itself.
- Fallback is allowed only after one of these conditions is true: the supporting skill is not installed, the runtime has no Skill mechanism, the call is rejected by permission policy, or the attempted call fails.
- When fallback is used after a real attempt, set `attempted_skill_call: yes`, record `skill_call_result`, and write a concrete `fallback_reason`.
- When no explicit attempt was made even though the skill was visible or likely installed, set `attempted_skill_call: no`, `skill_call_result: not_attempted`, `execution_mode: fallback_agent_role`, and `status: completed_with_protocol_violation`.
- The workflow should still produce substantive files after fallback, but provenance must make the protocol deviation visible.
- Do not skip literature checks merely because `literature-review` is unavailable. Use available web search, PubMed/Entrez tools, or concise manual query synthesis for targeted novelty checks.

### 3. Build Or Update Review Cache

Before final judgment, create `review/nsfc_review_cache.txt`. Do not summarize the entire proposal. Extract only decision-relevant content.

Cache schema:

```text
NSFC GENERAL PROGRAM REVIEW CACHE

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
```

Reuse this cache in later steps. Return to `00_full_text.txt` only for missing details or short evidence quotes.

### 4. Scientific Critique

Explicitly use `scientific-critical-thinking` on the cache plus targeted TXT snippets when available. If unavailable, complete this stage in the current agent using the same role:

- Is the central question a real basic-science question?
- Does the research attribute match the proposal content?
- Do aims answer the scientific question rather than list techniques?
- Are controls, sample sizes, statistical plans, model systems, validation paths, and endpoints adequate?
- Do expected outcomes overreach the evidence?
- Are risk and alternative plans concrete enough?

Save concise findings to `review/01_scientific_critique.txt` when producing files.
The file must begin with `NSFC_REVIEW_STAGE_PROVENANCE`, with `stage: scientific_critique`, `supporting_skill: scientific-critical-thinking`, and the correct `execution_mode`.

### 5. Targeted Literature Checks

Explicitly use `literature-review` only for key claims when available. If unavailable, complete this stage in the current agent with targeted web/literature searches:

- Verify the most important novelty claims.
- Identify obvious missing work or competing explanations.
- Check whether the proposed gap is real and current.
- Avoid broad literature review unless explicitly requested.

Save results to `review/02_literature_checks.txt` when producing files.
The file must begin with `NSFC_REVIEW_STAGE_PROVENANCE`, with `stage: literature_checks`, `supporting_skill: literature-review`, and the correct `execution_mode`.

### 6. Stress Test

Explicitly use `reviewer-2-simulator` after the cache and scientific critique when available. If unavailable, complete this stage in the current agent as a strict reviewer-2 role:

- Produce the strongest score-lowering arguments.
- Focus on top issues that would matter to NSFC reviewers.
- Convert vague concerns into concrete fixable problems.
- Explicitly distinguish between revisable weaknesses and structural flaws that should materially lower fundability.

Save results to `review/03_reviewer2_stress_test.txt` when producing files.
The file must begin with `NSFC_REVIEW_STAGE_PROVENANCE`, with `stage: reviewer2_stress_test`, `supporting_skill: reviewer-2-simulator`, and the correct `execution_mode`.

### 7. Peer Review Draft

Explicitly use `peer-review` to structure the grant-style judgment and save it to `review/04_peer_review_draft.txt`. If unavailable, complete the equivalent role in the current agent and record fallback provenance.

The draft must synthesize `nsfc_review_cache.txt`, `01_scientific_critique.txt`, `02_literature_checks.txt`, and `03_reviewer2_stress_test.txt`. Do not bypass these stage files when producing the judgment.

The draft must include:

- research attribute match judgment;
- weighted scoring summary using the exact matching rubric dimensions and weights;
- ethics/compliance gate;
- cap-rule checks;
- default Kill-mode decision section with the exact heading `KILL-MODE DECISION`.

The user does not need to ask for Kill-mode separately.

### 8. Final Scientific Writing

Explicitly use `scientific-writing` to polish `review/04_peer_review_draft.txt` into `review/05_final_review.txt`. If unavailable, complete the equivalent role in the current agent and record fallback provenance.

The final review must be written in polished Chinese unless the user explicitly requests another language. Keep the tone professional, restrained, concrete, and suitable for NSFC-style review or pre-submission internal review.

`scientific-writing` may improve clarity, structure, tone, concision, and Chinese expression, but it must not change the evidence judgment, reverse the funding recommendation, or soften the Kill-mode decision produced by the peer-review draft.

`scientific-writing` must preserve the scoring table from `04_peer_review_draft.txt` with exact rubric dimensions, weights, raw scores, weighted points, total `/100`, grade before cap rules, cap rules, final grade, and funding opinion. It may polish the wording in the evidence-basis column, but must not collapse the scoring table into a 0-5 average or replace it with generic grant-review dimensions.

`05_final_review.txt` must contain the exact heading `KILL-MODE DECISION`. Under that heading, include:

- decision-level defects;
- number of structural flaws;
- cap-rule effect on the grade;
- strict internal recommendation.

### 9. Submitted Review Comment

Create `review/06_submitted_review_comment.txt` from `review/05_final_review.txt`. This file is for copying into the official review form, so it must be concise, polished Chinese, and organized by the form fields.

Include these fields:

```text
COMPREHENSIVE EVALUATION
- Choose one: A excellent / B good / C medium / D poor

FUNDING OPINION
- Choose one: A priority funding / B fundable / C not funded

KILL-MODE DECISION
- Brief internal triage summary. Preserve the strict recommendation from `05_final_review.txt`.

SCIENTIFIC EVALUATION DESCRIPTION
- Use the official definition for the selected research attribute:
  - free_exploration: originality/frontier basic research from curiosity or academic inspiration, not aimed at current application needs.
  - goal_oriented: basic research driven by economic/social development needs or national needs.

SPECIFIC REVIEW COMMENTS
1. Attribute-specific question 1.
2. Attribute-specific question 2.
3. Attribute-specific question 3.

MANUAL REVIEW REMINDER
```

For `free_exploration`, the three specific comments should answer:

1. The innovation of the research idea and the reasoning.
2. The value of the scientific question and contribution to relevant frontiers.
3. The applicant's innovation potential, feasibility of the research plan, and suggestions for improvement.

For `goal_oriented`, the three specific comments should answer:

1. Whether the project addresses a basic scientific question behind economic/social development needs or national needs, with reasoning.
2. The innovation of the scientific question and the scientific value of expected results.
3. The applicant's innovation potential, feasibility of the research plan, and suggestions for improvement.

End the file with a reminder that text extraction cannot fully assess non-text figures, technical route diagrams, mechanism models, experimental images, representative papers, CV details, ethics/biosafety/compliance materials, and other form attachments; these require human review before submission.

If the workflow did not inspect critical non-text figures directly, explicitly include a manual-review reminder covering:

- mechanism diagrams or model schematics,
- technical workflow diagrams,
- experimental result figures, microscopy panels, gels, blots, plots, or other image-based evidence.

When the user is doing internal triage, pre-screening, kill-mode review, or asks for a stricter funding recommendation, apply a conservative decision rule:

- Do not let general significance, available platforms, or decent preliminary basis outweigh structural flaws.
- Treat the following as potentially fatal unless the proposal itself clearly neutralizes them:
  - the core novelty claim is weak, already substantially occupied by prior work, or mainly rhetorical;
  - the main mechanistic chain is not designed to close with decisive experiments;
  - the proposal is overloaded, diffuse, or tries to do too many partially connected things;
  - a high-risk hypothesis is central to the application but has weak direct preliminary support;
  - translational or exploratory extensions materially dilute the core basic-science question.
- If two or more structural flaws remain after considering the proposal's own evidence, default to `not recommended for support` or an equivalent negative internal decision, even if the topic is important and the team appears capable.
- Use `scientific-critical-thinking` and `reviewer-2-simulator` as the primary drivers of fundability; `peer-review` should organize the decision, not soften it.
- Use `scientific-writing` only to clarify and polish the judgment. It must not reverse a negative decision produced by the evidence review.

Recommended output:

```text
OVERALL ASSESSMENT

RESEARCH ATTRIBUTE MATCH

STRENGTHS

MAJOR CONCERNS

MINOR CONCERNS

FEASIBILITY AND RISK ASSESSMENT

INNOVATION ASSESSMENT

SCORING SUMMARY AND CAP RULES

Use this required format:

```text
Rubric used: free_exploration / goal_oriented

| Dimension exactly from scoring-rubric.txt | Weight | Raw score /5 | Weighted points | Evidence basis |
| ... | ... | ... | ... | ... |

Total weighted score: <x>/100
Grade before cap rules: A / B / C
Cap rules triggered: <none or list>
Final grade after cap rules: A / B / C
Funding opinion: A priority funding / B fundable / C not funded
```

ETHICS AND COMPLIANCE GATE

SUGGESTIONS FOR REVISION

FUNDING RECOMMENDATION OR PRIORITY
```

For each major concern, cite the relevant section or cache item. Use short quotes only when necessary.

For every full workflow run, add one short section before the funding recommendation. Use this exact heading in `04_peer_review_draft.txt`, `05_final_review.txt`, and `06_submitted_review_comment.txt`:

```text
KILL-MODE DECISION
```

Use this section to name the structural reasons the proposal should be rejected or deprioritized. Do not bury decision-level defects inside minor wording suggestions.

## Automation Pattern

Use the workflow as a state machine:

1. `PDF_OR_TXT_INPUT`
2. `TXT_READY`
3. `CACHE_READY`
4. `SCIENTIFIC_CRITIQUE_READY`
5. `LITERATURE_CHECKS_READY`
6. `STRESS_TEST_READY`
7. `PEER_REVIEW_DRAFT_READY`
8. `FINAL_REVIEW_READY`
9. `SUBMITTED_REVIEW_COMMENT_READY`

At the start of every turn, identify the latest completed state from files in the review directory, then continue from the next state. Do not restart from the PDF once TXT exists.

## References

- Use `references/scoring-rubric.txt` only when a consistent rating standard is needed.
- Use `references/output-templates.txt` only when drafting file outputs or final review text.

## Safety And Integrity

- Do not generate a complete grant application for the applicant.
- Do not fabricate policy requirements, citations, project details, or reviewer criteria.
- If generative AI use is discussed, remind the user that NSFC 2026 requires human verification and truthful disclosure/labeling of AI-assisted content.
- Flag ethical, biosafety, sensitive-information, or confidentiality risks only when they affect scientific review or compliance.



