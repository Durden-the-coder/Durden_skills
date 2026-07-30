---
name: ai-biomedical-journal-watch
description: Collect, screen, rank, audit, and summarize recent AI-related biomedical research and journal trend content from 18 configured journals. Supports customizable rolling windows, evidence-based decisions, prestige-aware ranking, bounded Chinese reports, and pre-render validation.
---

# Biomedical Journal Watch v0.2.1

Read `references/version.json` and use the declared 18-journal scope. Clinical coverage is limited to NEJM and The Lancet.

## Workflow

1. Read `references/time-windows.md`, `references/source-strategies.md`, `references/journal-priority.json`, and `references/screening-contract.md`.
2. Freeze `as_of`; discover from preferred sources and fallbacks; merge by DOI, PMID, then normalized title.
3. Store every candidate before screening. For windows longer than seven days, collect in seven-day slices and screen in batches of 40.
4. Preserve publication date, article type, abstract/lead evidence, and evidence URLs.
5. Assign `include`, `context`, `exclude`, or `needs_evidence` per record. Never implement decisions as DOI/title sets, dictionaries, tuples, whitelists, blacklists, index tables, or summary override tables in executable code.
6. Run the mandatory audit before rendering:

   ```powershell
   python <skill-root>\scripts\audit_reviewed_jsonl.py --input <reviewed.jsonl> --output <audit.json>
   ```

   Do not render a final report when the audit exits nonzero. Review warnings in large runs, especially zero `needs_evidence`.
7. Render with the window-aware stable entry point:

   ```powershell
   python <skill-root>\scripts\render_report_v321.py --window 30d --input <reviewed.jsonl> --output <report.md>
   ```

## Screening guardrails

- Route Review, Perspective, Preview, Editorial, News, Highlight, Comment, Commentary, and Viewpoint to `context` when AI-relevant; never count them as original research.
- Treat a Letter as research only when abstract/lead evidence supports original methods or results. Otherwise use `needs_evidence` or `context`.
- Do not infer AI from lexical collisions. Names such as `transformer base editor`, “intelligent” materials, predictive biomarkers, automated assays, Bayesian/statistical models, or ordinary computational pipelines are not AI evidence by themselves.
- Require an explicit evidenced AI/ML function: training, learned inference, model evaluation, representation/generative learning, or an evaluated AI intervention.
- Prestige affects ranking only, never eligibility.
- Included/context items require dates and evidence URLs. Included items require supported summaries.

## Output policy

- Detailed research: 20 for every window; per-journal tier cap never above 5.
- Additional research index: 30 for `72h`/`96h`, 50 for `7d`, 80 for `30d` or longer.
- Context list: 20 by default; title, journal, date, type, and link only.
- Exclusion summary: top 10 normalized categories by default; keep full reasons in JSONL.
- Markdown is written with a UTF-8 BOM for Windows compatibility. JSONL remains UTF-8.

## Source exceptions

- Nature Communications: enumerate and paginate the official article list; RSS alone is insufficient.
- Nature Methods: follow official pages for abstract/date/type.
- Cell Metabolism: inspect PubMed/Europe PMC publication types and correction links before enrichment.
- Cell Press, AAAS, and The Lancet: when publisher pages block access, use the Crossref/PubMed/Europe PMC union.
- NEJM: use RSS and PubMed, then OpenAlex for missing abstracts.

