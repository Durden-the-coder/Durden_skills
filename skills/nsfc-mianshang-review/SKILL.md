---
name: nsfc-mianshang-review
version: 0.4.5
description: Review NSFC General Program grant proposals with a PDF-to-TXT, cache-first, staged workflow. Use for Chinese NSFC mian-shang proposal review, kill-mode internal triage, novelty checks, scientific critique, reviewer-2 stress testing, and polished Chinese final review. Explicitly routes supporting skills when available and falls back to equivalent in-agent roles when unavailable.
allowed-tools: Read Write Edit Bash WebSearch
license: MIT license
metadata:
    skill-author: Durden
---

# NSFC General Program Review

Use this skill as the workflow entry point for NSFC General Program proposal review. It coordinates PDF/TXT preparation, cache-first analysis, explicit supporting-skill routing when available, and role-equivalent fallback when supporting skills cannot be invoked.

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

Continue through workflow stages automatically unless extraction fails, a required password is missing, the output directory is unsafe, or a safety/compliance issue appears. Do not stop at normal stage boundaries to ask the user to say `go`.

If the runtime asks for tool permission, request the smallest useful action scope, preferably limited to reading proposal-derived TXT files, running `scripts/extract_nsfc_text.py`, and writing artifacts under the review directory.

## Non-Negotiable File Rules

- If the user provides a PDF, local PDF-to-TXT extraction is the default entry behavior. Do not require manual step-by-step preparation unless extraction is blocked.
- If the input is a PDF, read it only during the PDF-to-TXT conversion step.
- After TXT extraction succeeds, never read the PDF again. Later work must use TXT files, cache files, stage files, and short copied evidence snippets.
- If the PDF is encrypted or text extraction is blocked, do not treat this as a normal failure. Ask for password, decrypted PDF, exported TXT, or OCR text.
- Prefer `.txt` as the primary working copy. Markdown is optional and only for human-facing summaries.
- Run all workflow artifacts under the user-specified review directory or the inferred proposal-local review directory.
- Do not write workflow artifacts to system folders, user profile cache locations, global skill directories, or agent home directories by default.
- The user should only need to provide the proposal path and, when needed, the PDF password. If no review directory is provided, create a clean proposal-specific review folder in the parent directory of the proposal folder. Example: for `D:\AI projects\claude_code\2026国自然评审\项目书\proposal.pdf`, use `D:\AI projects\claude_code\2026国自然评审\nsfc-review-proposal\`.
- Keep the proposal folder clean. Do not write extracted or review files into the proposal folder unless explicitly asked.
- Chinese source text is expected. Preserve scientific terms accurately and produce final review text in polished Chinese by default.

## Scope

Review these components by default:

- title and Chinese abstract;
- project rationale: scientific value, research gap, significance, field status, key scientific question;
- research content: objectives, scientific questions, tasks, technical route, distinctive features, innovation, annual plan;
- research basis: prior work, preliminary data, feasibility analysis, risks and mitigation;
- team background, representative papers, and related projects only when they affect feasibility, novelty, overlap, or independence;
- non-text visual materials only through explicit human review.

Exclude low-value administrative review by default: budget details, attachment directory mechanics, unit-consistency declarations, recommendation-letter logistics, routine certificates, and generic form-filling checks.

If key claims depend on images, diagrams, gels, microscopy panels, model schematics, workflow figures, or result plots that were not reliably converted into text, the final review must explicitly say those materials still require human inspection.

## Workflow Artifacts

Use this structure under the review directory:

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

Create TXT artifacts first with:

```bash
<python> scripts/extract_nsfc_text.py --proposal <proposal.pdf-or-txt> [--password <pdf-password>] --init-review-files
```

If the user explicitly provides a review directory, add:

```bash
--workdir <review_dir>
```

If `--workdir` is omitted, the script creates `nsfc-review-<proposal-stem>` in the parent directory of the folder containing the proposal.

## Required Workflow

### 1. Prepare Text Working Copy

If the proposal is a PDF, automatically begin by running `scripts/extract_nsfc_text.py` with an available Python runtime to create `extracted/00_full_text.txt`, `extracted/01_section_index.txt`, and `extracted/extraction_report.txt`.

If extraction reports `ENCRYPTED_PDF`, stop and ask the user for the next input format. Do not continue reviewing from the PDF. This is an action-required state, not a workflow failure.

### 2. Route Before Deep Review

Start each review with a short routing note:

- task type: full review, section review, pre-submission self-check, or revision planning;
- available artifacts: TXT, section index, cache, stage files, final review draft;
- skills to use and why;
- excluded low-value administrative materials.

Default routing:

- Title and Chinese abstract: `peer-review` for quick proposal positioning and overall framing.
- Project rationale: `scientific-critical-thinking` plus targeted `literature-review`.
- Research content: `scientific-critical-thinking`, `reviewer-2-simulator`, and `peer-review`.
- Research basis: `scientific-critical-thinking` and `peer-review`.
- Final organization and language: `peer-review` plus `scientific-writing`.

Supporting skill routing policy:

- At each stage, first try to explicitly load or call the named supporting skill if the runtime exposes a skill mechanism.
- If a supporting skill is not installed, cannot be loaded, or the runtime does not support skill-to-skill routing, do not stop the workflow. Instead, perform the equivalent role in the current agent and write the stage artifact.
- The workflow succeeds when all required stage files contain role-appropriate analysis. It does not require the UI to show separate supporting-skill calls.
- When fallback is used, briefly note it inside the relevant stage file, for example: `Routing note: scientific-critical-thinking was unavailable; current agent completed this role directly.`
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

Explicitly use `scientific-critical-thinking` on the cache plus targeted TXT snippets when available. If unavailable, complete this stage in the current agent using the same role.

Check whether the central question is a real basic-science question, whether the research attribute matches the content, whether aims answer the question rather than list techniques, whether controls/sample sizes/statistics/model systems/validation paths/endpoints are adequate, whether expected outcomes overreach the evidence, and whether risk alternatives are concrete.

Save concise findings to `review/01_scientific_critique.txt`.

### 5. Targeted Literature Checks

Explicitly use `literature-review` only for key claims when available. If unavailable, complete this stage in the current agent with targeted web/literature searches.

Verify the most important novelty claims, identify missing work or competing explanations, and check whether the proposed gap is real and current. Avoid broad literature review unless explicitly requested.

Save results to `review/02_literature_checks.txt`.

### 6. Stress Test

Explicitly use `reviewer-2-simulator` after the cache and scientific critique when available. If unavailable, complete this stage in the current agent as a strict reviewer-2 role.

Produce the strongest score-lowering arguments, focus on top issues that would matter to NSFC reviewers, and distinguish revisable weaknesses from structural flaws that should materially lower fundability.

Save results to `review/03_reviewer2_stress_test.txt`.

### 7. Final Review

Explicitly use `peer-review` to structure the final judgment and `scientific-writing` to polish it when available. If either is unavailable, complete the equivalent role in the current agent.

The final review must synthesize `nsfc_review_cache.txt`, `01_scientific_critique.txt`, `02_literature_checks.txt`, and `03_reviewer2_stress_test.txt`. Do not bypass these stage files when producing the final judgment.

The final review must be written in polished Chinese unless the user explicitly requests another language.

If the workflow did not inspect critical non-text figures directly, explicitly include a manual-review reminder covering mechanism diagrams, technical workflow diagrams, experimental result figures, microscopy panels, gels, blots, plots, and other image-based evidence.

For internal kill-mode review, include:

```text
FATAL FLAWS OR DECISION-LEVEL DEFECTS
```

Use this section to name the structural reasons the proposal should be rejected or deprioritized. Do not bury decision-level defects inside minor wording suggestions.

## Kill-Mode Decision Rule

When the user asks for internal triage, pre-screening, kill-mode review, or a stricter funding recommendation:

- do not let general significance, available platforms, or decent preliminary basis outweigh structural flaws;
- treat weak novelty, unclosed mechanism chains, overloaded aims, central high-risk hypotheses with weak support, and translational extensions that dilute the basic-science question as potentially fatal unless the proposal clearly neutralizes them;
- if two or more structural flaws remain after considering the proposal's own evidence, default to `not recommended for support` or an equivalent negative internal decision;
- let `scientific-critical-thinking` and `reviewer-2-simulator` drive fundability; `peer-review` should organize the decision, not soften it;
- use `scientific-writing` only to clarify and polish the judgment.

## Automation Pattern

Use the workflow as a state machine:

1. `PDF_OR_TXT_INPUT`
2. `TXT_READY`
3. `CACHE_READY`
4. `SCIENTIFIC_CRITIQUE_READY`
5. `LITERATURE_CHECKS_READY`
6. `STRESS_TEST_READY`
7. `FINAL_REVIEW_READY`

At the start of every turn, identify the latest completed state from files in the review directory, then continue from the next state. Do not restart from the PDF once TXT exists.

## References

- Use `references/scoring-rubric.txt` only when a consistent rating standard is needed.
- Use `references/output-templates.txt` only when drafting file outputs or final review text.

## Safety And Integrity

- Do not generate a complete grant application for the applicant.
- Do not fabricate policy requirements, citations, project details, or reviewer criteria.
- If generative AI use is discussed, remind the user that NSFC 2026 requires human verification and truthful disclosure/labeling of AI-assisted content.
- Flag ethical, biosafety, sensitive-information, confidentiality, or non-text-evidence risks only when they affect scientific review or compliance.
