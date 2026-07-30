# Time-window policy

Accept `72h`, `96h`, `7d`, `30d`, any positive integer plus `h`/`d`, and explicit `YYYY-MM-DD..YYYY-MM-DD`. Default to `96h`. Freeze one UTC `as_of`; rolling windows are `[start, as_of)` and explicit intervals are `[start 00:00 UTC, end 00:00 UTC)`.

Keep discovery independent from output limits. Merge the full pool, then screen batches of 40 and persist each batch. For windows longer than seven days, collect non-overlapping seven-day slices and rank once after merging.

Default report limits:

- Detailed included research: 20 for every window.
- Per-journal detailed cap: tier-specific, never above 5.
- Additional included index: 30 for `72h`/`96h`, 50 for `7d`, 80 for `30d` or longer.
- Context title list: 20 by default; user-configurable.
- Individually displayed `needs_evidence`: 10.

Longer windows must not truncate collection. Store undisplayed records and all decisions in JSONL, and disclose how many were omitted from presentation.

