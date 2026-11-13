---
name: evidence-grounded-scientific-writing
description: Orchestrate evidence-grounded biomedical manuscript writing with claim-level auditing, adversarial review, citation adjudication, academic humanization, and a visible Discussion/Limitations decision queue.
---

# Evidence-Grounded Scientific Writing

## Purpose

Use this skill when drafting or revising biomedical manuscripts, Results sections, Discussion sections, abstracts, figure legends, or reviewer responses that must remain faithful to experimental data and published evidence. The skill coordinates bounded specialist passes, maintains a claim-level evidence ledger, and preserves important unresolved issues for an author decision instead of silently smoothing them away.

This is an orchestration skill, not a permission to invent experiments, citations, statistics, sample sizes, or mechanistic conclusions.

## Operating principle

The main agent owns the canonical draft and the final decision. Specialist agents produce auditable inputs; they do not overwrite one another's conclusions or establish truth by majority vote. Every retained claim must be traceable to a figure, table, method, dataset, or external source, and the wording must not exceed the strength of that support.

The default workflow has three rounds, but it is adaptive: stop early when the claim ledger is clean, or reopen a round when a major contradiction, unsupported inference, or missing source is discovered.

## Preflight audit

Before dispatching writers or reviewers, create a short `preflight_audit` that records:

- the requested section, target journal or house style, intended audience, and desired length;
- the available figures, tables, methods, statistical details, source files, and known data gaps;
- the claims that must be made, claims that are optional, and claims that must not be made;
- the required terminology, spelling, tense, citation style, and author preferences;
- the unresolved questions that could change the interpretation or the conclusion.

The audit is the first output of the workflow. It prevents a fluent draft from hiding missing evidence and gives the critical reviewer a defined scope.

## Roles

### Main agent

The main agent must:

1. define the task and create the preflight audit;
2. build and maintain the canonical draft, claim ledger, source cards, challenge log, citation decisions, and unresolved queue;
3. dispatch bounded tasks with explicit inputs and output schemas;
4. reconcile disagreements by evidence quality, directness, and scope rather than by vote;
5. preserve convergent and divergent reviewer concerns separately;
6. apply calibrated wording and the author's requested style only after factual integration;
7. run the final audit for figure mapping, numerical fidelity, citations, terminology, and unresolved issues.

The author controls substantive decisions. If a reviewer perspective, interpretation, or unresolved issue could materially change the manuscript's conclusion, pause for author input when it cannot be inferred safely. Do not create a mandatory pause for routine copy-editing.

### Scientific writer

Draft only from the supplied evidence packet and claim ledger. Map statements to panels, methods, or source cards. Distinguish observation, interpretation, and speculation. Do not fill missing details from general knowledge.

### Critical challenger

Stress-test the proposed claims for alternative explanations, causal overreach, confounding, selection or reporting bias, model limitations, statistical weakness, and mismatch between assay and conclusion. For each concern, state:

- the exact claim;
- the risk type and severity: `FATAL`, `MAJOR`, `IMPORTANT`, or `MINOR`;
- the evidence supporting the concern;
- the smallest revision or additional evidence that would address it;
- whether the issue belongs in the Results, Discussion, Limitations, or the unresolved queue.

Use directness and proportionality: a descriptive claim supported by a figure does not require mechanistic proof, whereas a causal or translational claim does.

### Literature researcher

Search for primary and authoritative sources that support, qualify, or challenge specific claims. Return source cards with the exact claim supported, relevant passage or result, model/population, study type, date, stable URL or DOI, and limitations. Separate direct support from analogy, background, and contradiction. External literature can contextualize an experiment; it cannot repair a missing experiment.

### Citation adjudicator

For each proposed citation, decide `ACCEPT`, `ACCEPT_WITH_CALIBRATION`, `REPLACE`, `REJECT`, or `AUTHOR_DECISION`. Check that the source supports the nearby claim, in the same direction and at the same level of specificity. Record whether support is direct, indirect, mixed, or conflicting, and flag citation dumping, outdated sources, non-primary claims, and population or model mismatch.

### Peer reviewer

Run a focused final review rather than a generic imitation of a journal review. For biomedical work, choose at most three perspective-based reviewers as needed:

- experimental design and statistics;
- cell, molecular, or disease biology;
- translational, clinical, or model relevance.

Use perspective labels, not invented named experts. A named or theory-specific persona is allowed only when the user explicitly requests it and the required full texts or source corpus are available. Each review must contain: summary, strengths, major concerns, minor concerns, representation or evidence check, concrete recommendations, and overall assessment. Classify each issue as `QUICK_FIX`, `MINOR_REVISION`, `MAJOR_REVISION`, or `ACKNOWLEDGE_BUT_DECLINE`, with a reason.

### Academic humanizer

Perform two distinct passes. First, audit for overclaiming, hype, filler, citation dumping, vague magnitude words, repetitive transitions, and AI-like boilerplate. Second, rewrite for clarity and human academic voice while preserving all numbers, figure references, citations, uncertainty, and scientific meaning. It must report any sentence whose verb was downgraded and confirm that no quantitative or evidentiary content was changed.

## Three-round protocol

### Round 1: independent evidence work

- The writer produces a conservative draft from the evidence packet.
- The challenger evaluates claims and alternative explanations independently.
- The literature researcher retrieves targeted source cards.
- The humanizer performs a claim-and-style audit without becoming the final arbiter of evidence.

The main agent then creates a first claim ledger and identifies disagreements. No prose is treated as final merely because multiple agents used similar wording.

### Round 2: adjudication and controlled revision

- The citation adjudicator evaluates every external source against the exact nearby claim.
- The main agent reconciles the writer, challenger, and literature outputs.
- Numerical, statistical, model, and figure-panel details are checked against the source material.
- The draft is revised, with claims downgraded, split, removed, or moved to Discussion/Limitations when appropriate.

Open issues that could alter the conclusion are sent to the author. Issues that are important but cannot be resolved in the current task are entered into the unresolved queue with candidate wording and a clear status.

### Round 3: focused peer review and final integration

- The peer reviewer examines the integrated draft using only the selected perspectives.
- The challenger is reused only for a distinct residual risk; do not duplicate the same review under a new label.
- The main agent resolves actionable issues, records declined changes, and reruns the humanizer as the final style pass.
- The final audit verifies claim support, figure order, numerical fidelity, citation placement, terminology, and queue status.

Do not force a third round when no unresolved major or important issue remains. Do not mark the task complete while a required factual or author decision is pending.

## Claim and evidence discipline

For each material claim, record:

- claim text and claim type: observation, comparison, association, mechanism, causation, or translation;
- evidence location: figure/panel, table, method, dataset, or source card;
- evidence status: `DIRECT`, `INDIRECT`, `MIXED`, `CONTRADICTORY`, or `MISSING`;
- model, species, cell line, treatment, dose, duration, and endpoint when relevant;
- supported wording, unsupported wording, and calibrated replacement;
- reviewer concerns, decision, and owner.

Use the weakest verb that accurately describes the evidence. Prefer `was associated with`, `was consistent with`, `supported`, or `suggested` when causality is not established. Do not turn a significant P value into a large effect, a correlation into a mechanism, or a pathway enrichment into a demonstrated molecular target.

For figures, verify panel lettering and order, treatment names, concentrations, durations, sample sizes, error bars, statistical tests, and exact P values. If a detail is not visible or supplied, mark it `MISSING` rather than infer it.

## Discussion and Limitations queue

Important unresolved issues must be recorded in `discussion_limitation_queue` rather than silently omitted. Each entry should include:

- `issue_id`, unresolved question, affected claim, and why it matters;
- evidence for and against the interpretation;
- severity and confidence;
- destination: `DISCUSSION`, `LIMITATIONS`, `BOTH`, or `AUTHOR_DECISION`;
- candidate calibrated text;
- evidence or experiment that would resolve it;
- status: `PENDING_AUTHOR_DECISION`, `INCLUDED`, `DEFERRED`, or `RESOLVED`.

Candidate text is not an accepted manuscript claim until the author or main agent explicitly adopts it. When the user requests a complete draft before deciding, keep the queue visible in the deliverables and avoid presenting queued interpretations as established facts.

## Source and citation rules

- Prefer primary studies, authoritative datasets, guidelines, and methods papers for specific claims.
- Use a source only when its model, population, assay, and direction of effect fit the sentence.
- Keep citation placement close to the supported claim; split sentences when one citation cannot support all clauses.
- Never invent or silently repair DOI, PMID, sample size, P value, effect size, date, or experimental detail.
- If sources disagree, report the disagreement and explain why one source is more applicable; do not hide it through citation stacking.
- Literature review is not a substitute for validating the user's own figures or raw data.

## Artifact contract

Maintain these files or structured objects for any substantial run:

- `preflight_audit.md`
- `task_spec.md`
- `claim_ledger.tsv` or `.jsonl`
- `source_cards.md` or `.jsonl`
- `challenge_log.md`
- `citation_decisions.md`
- `discussion_limitation_queue.md`
- `round-1/`, `round-2/`, and `round-3/` outputs when those rounds run
- `peer_review_summary.md`
- `decision_log.md`
- `final_draft.md` and, when requested, `final_figure_legends.md`

For small tasks, these may be compact sections in one report, but the fields must remain recoverable. Persist outputs in files rather than leaving the audit trail only in chat.

## Final acceptance checklist

Before reporting completion, confirm:

- every retained empirical claim has direct support or clearly calibrated indirect support;
- observations, interpretations, mechanisms, and hypotheses are distinguishable;
- all figures, panels, numbers, P values, models, and sample sizes match the supplied material;
- every accepted citation has a recorded relevance decision;
- major and important reviewer concerns are resolved, explicitly declined, or queued;
- unresolved issues are visible in Discussion/Limitations or the author-decision queue;
- the humanizer changed style without changing evidence;
- no required work remains hidden behind a polished paragraph.

## References

Use the bundled references for the ledger fields and round protocol:

- `references/ledger-schema.md`
- `references/round-protocol.md`

