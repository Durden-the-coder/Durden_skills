# Screening contract

## Decisions

- `include`: original biomedical research with an explicitly evidenced AI core method, evaluated intervention, or material support role.
- `context`: AI-relevant Review, Perspective, Preview, Editorial, News, Highlight, Comment, Commentary, Viewpoint, or non-primary Letter.
- `exclude`: non-biomedical scope, no material AI role, correction/erratum/retraction, or unrelated content.
- `needs_evidence`: apparently relevant material lacks enough text or article-type evidence for a safe decision.

Review and commentary types never enter `include`. A Letter may enter `include` only when abstract/lead evidence demonstrates original methods or results. An empty-abstract Letter with an AI-related title is `needs_evidence`, not automatically included.

Require evidence of a learned model or AI system performing training, inference, representation/generative modelling, evaluation, or intervention. Do not treat “transformer” in a biotechnology product name, predictive/statistical analysis, automated processing, Bayesian modelling, “intelligent” hardware, or prospective usefulness for AI as sufficient evidence.

## Required JSONL fields

Every record requires `work_id`, `journal`, `title`, `url`, `date`, `article_type`, `tracks`, `status`, `ai_role`, `priority`, `evidence_state`, and `evidence_urls`.

- `include`: require `summary_cn`, `importance_cn`, date, evidence URL, and abstract/lead evidence unless the exact title unambiguously states both domains.
- `context`: require `context_reason`, date, article type, and evidence URL; render no full narrative.
- `exclude`: require a normalized `exclusion_reason`.
- `needs_evidence`: record the missing evidence in `exclusion_reason`.

Use priority 5 for time-sensitive high-impact work, 4 for clearly material work, 3 for useful support resources, 2 for lower-impact included/context work, and 1 for unresolved/excluded work. Priority never changes semantic status.

Persist decisions as JSONL records derived from evidence. Do not encode record decisions in executable DOI/title collections or summary override maps.

