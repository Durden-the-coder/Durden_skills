# Three-round protocol

This protocol is the default for a substantial scientific-writing task. The main agent may stop early when the acceptance checklist is satisfied, but must record why a round was skipped.

## Phase 0: intake and preflight

1. Define the section, target journal/style, audience, length, and output format.
2. Inventory figures, tables, methods, statistics, datasets, source files, and known gaps.
3. Extract the required claims and prohibited or unsupported claims.
4. Create the initial claim ledger and `discussion_limitation_queue`.
5. Select reviewer perspectives only after the scope is known.

Ask the author a question only when the answer cannot be inferred safely and could change the conclusion, reviewer strategy, or interpretation. Routine wording choices should not block the workflow.

## Round 1: independent work

Dispatch disjoint prompts so the outputs are genuinely independent:

- writer: conservative draft mapped to the supplied data;
- critical challenger: alternative explanations, validity, bias, statistics, and claim strength;
- literature researcher: targeted primary and authoritative source cards;
- academic humanizer: pre-edit audit of claim strength, AI-like phrasing, and readability.

Each output must include its evidence basis and unknowns. The writer must not use a source that the literature researcher has not verified; the literature researcher must not decide how strongly the manuscript should state an unverified experiment.

The main agent merges evidence into the ledger before merging prose.

## Round 2: adjudication

1. Compare every retained claim with its figure/panel or method record.
2. Run the citation adjudicator on every external citation.
3. Label support as direct, indirect, mixed, contradictory, or missing.
4. Downgrade, split, move, remove, or retain claims according to the ledger.
5. Record unresolved issues with candidate Discussion/Limitations language.
6. Ask the author to decide only on material open questions.

The main agent must preserve dissent in the challenge log. Agreement between agents is not evidence if all agents relied on the same unsupported premise.

## Round 3: focused peer review

Choose at most three perspectives. Use only those needed for the task:

| Perspective | Main checks |
|---|---|
| Design/statistics | Controls, randomisation or pairing, measurement, sample size, test choice, multiplicity, effect size, missing data, and causal wording. |
| Biology/mechanism | Model fit, pathway interpretation, alternative mechanisms, assay-to-conclusion mapping, and extrapolation beyond the tested system. |
| Translation/relevance | Human or animal model relevance, external validity, clinical framing, therapeutic language, and limitations of bulk or surrogate measurements. |

Each reviewer returns a structured memo with summary, strengths, major concerns, minor concerns, evidence/representation check, recommendations, and overall assessment. Classify concerns as quick fix, minor revision, major revision, or acknowledge-but-decline.

Use perspective labels by default. Use named or theory-specific personas only if the author requests them and a suitable source corpus or full texts are available. A simulated review is a stress test, not a prediction of editorial outcome.

## Humanizer and final audit

The final humanizer pass occurs after substantive integration. It may improve sentence flow, transitions, density, and academic voice, but may not change numbers, P values, figure references, citations, uncertainty, or claim type. It must report any change that affects a verb, qualifier, or magnitude word.

The main agent then checks:

- claim-to-evidence links and citation decisions;
- figures, panel order, treatment names, dose, duration, model, sample size, test, error bars, units, and P values;
- distinction between observation, interpretation, mechanism, and hypothesis;
- major and important reviewer concerns;
- unresolved queue status and author decisions;
- style requirements and terminology.

## Stop and escalation rules

- Stop after Round 1 when the task is a narrow copy edit and no scientific claim changes.
- Stop after Round 2 when no major or important risk remains and the requested output is not a peer-review simulation.
- Escalate to the author when a missing datum, conflicting result, or alternative explanation could change the central conclusion.
- Never use a polished final paragraph to conceal a pending decision.

