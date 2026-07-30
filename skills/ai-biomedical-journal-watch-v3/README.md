# AI Biomedical Journal Watch

`ai-biomedical-journal-watch-v3` monitors recent biomedical AI research and journal trend content across 18 configured journals. It supports rolling windows such as 72 hours, 96 hours, 7 days, and 30 days, then produces a ranked Chinese report with an auditable JSONL decision trail.

## Highlights

- 18-journal coverage, with Nature, Science, and Cell prioritized.
- Clinical-journal scope restricted to NEJM and The Lancet.
- Separate sections for original research, trend/commentary content, and items needing evidence.
- Default 20 detailed research items with bounded indexes for longer windows.
- Mandatory pre-render audit for article type, evidence, dates, and uncertainty.
- Journal-specific fallback strategies for Nature Methods, Nature Communications, Cell Metabolism, NEJM, Cell Press, AAAS, and The Lancet.

## Installation

Copy the `ai-biomedical-journal-watch-v3` directory into the Codex skills directory:

```text
%USERPROFILE%\.codex\skills\ai-biomedical-journal-watch-v3
```

Restart or open a new Codex task, then invoke:

```text
$ai-biomedical-journal-watch-v3
```

## Example requests

```text
Use $ai-biomedical-journal-watch-v3 to review biomedical AI papers from the last 7 days.
```

```text
Use $ai-biomedical-journal-watch-v3 to review the last 30 days, show 20 priority studies, and retain AI-related journal commentary as a compact list.
```

## Validation and rendering

Audit reviewed JSONL before rendering:

```powershell
python scripts\audit_reviewed_jsonl.py --input reviewed.jsonl --output audit.json
```

Render a window-aware report:

```powershell
python scripts\render_report_v321.py --window 7d --input reviewed.jsonl --output report.md
```

## Scope and limitations

The skill is designed for literature monitoring rather than systematic-review completeness. Publisher access restrictions, delayed indexing, missing abstracts, and ambiguous article types can still require manual review. Longer windows carry a higher boundary-error rate than 7-day monitoring.

## Version

Current release: `v0.2.1`.

