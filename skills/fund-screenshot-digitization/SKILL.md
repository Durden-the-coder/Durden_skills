---
name: fund-screenshot-digitization
description: Digitize fund transaction screenshots into accurate, page-level Excel records and a validated single-sheet statistics input. Use when a fund website cannot export transactions, screenshots are the source of truth, or an existing batch needs careful reprocessing, merging, or QA.
---

# Fund Screenshot Digitization

Use this skill for high-fidelity transcription of Chinese fund transaction screenshots. Treat the image—not OCR guesses, fund knowledge, or neighboring pages—as authoritative.

## Workflow

1. **Inventory and order sources**
   - List image files with `rg --files` or the equivalent and sort by filename using the host's locale-independent ordering.
   - Assign page numbers from that sorted list. Record the source filename in every page result.
   - Never assume every page has 20 rows; count visible rows and preserve short pages.

2. **Transcribe one page at a time**
   - Use one agent per page (or a small disjoint page range). Agents may read images and write only their own page artifact; they must not write a shared workbook.
   - Read every visible row from the original image. Preserve product names, transaction types, status text, punctuation, decimals, and units exactly.
   - Keep `--`, an explicitly blank field, and numeric zero distinct. Do not infer hidden time, fund code, account, or amounts.
   - Treat fund codes as six-character text, including leading zeroes. Keep request and confirmation values numeric with separate unit columns.
   - Mark an unclear field as null and record the reason in the agent's review note; do not silently repair it from another page.

3. **Write the page artifact**
   - Prefer the supplied page-13 template when the user requests matching formatting. Keep the two standard sheets: `交易记录` for human review and `数字字段` for machine use.
   - Populate all visible rows, preserve the source filename, and leave unused template rows empty on short pages.
   - Run a formula/error scan and render or otherwise inspect the populated sheet before accepting the page. A rendering API failure is not a data pass: report it and perform a structural check.

4. **Merge only after page QA**
   - Run `scripts/merge_workbooks.py` after page artifacts are complete. It selects the best artifact for each page, reads the numeric schema, and writes one sheet named `交易明细`.
   - The merged columns are: `页码`, `页内序号`, `交易日期`, `交易时刻`, `产品名称`, `基金代码`, `业务类型`, `申请数值`, `申请单位`, `确认数值`, `确认单位`, `关联账户`, `状态`, `来源文件`.
   - Run `scripts/validate_workbooks.py` on both the page directory and merged output. Sort by page then row, and reject missing pages, duplicate `(页码, 页内序号)`, unexpected row counts, malformed codes, or formulas/errors.

## Parallelism and handoff

- Use 4–8 agents for throughput; one page per agent is safest.
- Give every agent a disjoint output filename such as `交易记录_第014页_数字化_精细复核版.xlsx`.
- The parent agent owns inventory, exception review, merging, final validation, and delivery.
- For low-quality pages or high-value numeric fields, start a second independent transcription only for the flagged page and compare row-by-row.
- Do not delete source screenshots or accepted page artifacts during processing. Clean only named temporary crops, renders, OCR dumps, and scripts after delivery.

## Bundled scripts

- `scripts/merge_workbooks.py`: deterministic page selection, schema normalization, one-sheet merge, and numeric formatting.
- `scripts/validate_workbooks.py`: page coverage, row uniqueness, schema, fund-code, formula, and merged-file checks.
- `references/data-contract.md`: field meanings and rules for null, `--`, units, and short pages.

Run scripts with the workspace's maintained Python environment when one is specified. Example:

```powershell
python scripts\merge_workbooks.py --input-dir D:\Download\天天基金交易记录 --output D:\Download\天天基金交易记录\天天基金交易记录_合并统计输入.xlsx --expected-pages 190
python scripts\validate_workbooks.py --input-dir D:\Download\天天基金交易记录 --expected-pages 190
python scripts\validate_workbooks.py --merged D:\Download\天天基金交易记录\天天基金交易记录_合并统计输入.xlsx --expected-pages 190
```
