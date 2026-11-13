# Claim ledger schema

Use one record for each material claim. TSV is convenient for review; JSONL is preferable when claims have multiple sources or decisions.

## Required fields

| Field | Meaning |
|---|---|
| `claim_id` | Stable identifier, for example `R6-C03` or `LEGEND-S6-B02`. |
| `section` | Results, Discussion, Limitations, Abstract, legend, or response letter. |
| `claim_text` | Current wording of the claim. |
| `claim_type` | `OBSERVATION`, `COMPARISON`, `ASSOCIATION`, `MECHANISM`, `CAUSATION`, or `TRANSLATION`. |
| `evidence_location` | Figure/panel, table, method, dataset, or source-card ID. |
| `evidence_status` | `DIRECT`, `INDIRECT`, `MIXED`, `CONTRADICTORY`, or `MISSING`. |
| `model_context` | Cell line, species, tissue, treatment, dose, duration, endpoint, or cohort. |
| `supported_wording` | Strongest wording justified by the evidence. |
| `risk_note` | Main caveat, confounder, alternative explanation, or statistical concern. |
| `decision` | `KEEP`, `CALIBRATE`, `SPLIT`, `MOVE`, `REMOVE`, `AUTHOR_DECISION`, or `PENDING`. |
| `owner` | Main agent, author, or named specialist responsible for the next decision. |

## Optional fields

`source_ids`, `figure_numbers`, `exact_p_value`, `effect_size`, `sample_size`, `statistical_test`, `citation_decision`, `reviewer_ids`, `discussion_limitation_issue_id`, `candidate_text`, `last_updated`.

## Source card schema

Each source card should contain:

```text
source_id:
full_citation:
stable_url_or_doi:
source_type: PRIMARY | DATASET | GUIDELINE | METHODS | REVIEW | OTHER
claim_supported:
exact_passage_or_result:
model_or_population:
assay_or_endpoint:
direction_of_effect:
directness: DIRECT | INDIRECT | MIXED | CONTRADICTORY
limitations:
recommended_use: ACCEPT | ACCEPT_WITH_CALIBRATION | REPLACE | REJECT | AUTHOR_DECISION
```

Do not write a source card from a search-result snippet alone. Read the source or an authoritative full-text record sufficiently to verify the claimed result.

## Challenge record

```text
challenge_id:
claim_id:
concern:
risk_type: CAUSALITY | CONFOUNDING | MODEL | STATISTICS | BIAS | GENERALIZATION | REPRESENTATION | OTHER
severity: FATAL | MAJOR | IMPORTANT | MINOR
evidence_for_concern:
minimum_fix:
destination: RESULTS | DISCUSSION | LIMITATIONS | QUEUE
status: OPEN | RESOLVED | DECLINED | QUEUED
```

## Peer-review record

```text
review_id:
perspective: DESIGN_STATISTICS | BIOLOGY_MECHANISM | TRANSLATIONAL_RELEVANCE | OTHER
scope:
summary:
strengths:
major_concerns:
minor_concerns:
representation_or_evidence_check:
recommendations:
overall_assessment:
decision_class: QUICK_FIX | MINOR_REVISION | MAJOR_REVISION | ACKNOWLEDGE_BUT_DECLINE
source_basis:
```

Use `source_basis` to record the figures, methods, source cards, or full texts used by the reviewer. Do not imply that a reviewer is grounded in a named expert or journal perspective unless that basis is actually available.

## Discussion/Limitations queue record

```text
issue_id:
question:
affected_claim_ids:
why_it_matters:
evidence_for:
evidence_against:
severity:
confidence:
destination: DISCUSSION | LIMITATIONS | BOTH | AUTHOR_DECISION
candidate_text:
resolving_evidence:
status: PENDING_AUTHOR_DECISION | INCLUDED | DEFERRED | RESOLVED
```

