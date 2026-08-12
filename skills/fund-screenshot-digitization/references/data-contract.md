# Data contract

The machine-facing sheet uses one row per visible transaction and these columns:

| Column | Meaning |
|---|---|
| 页码 | Position in the filename-sorted screenshot set. |
| 页内序号 | Row number shown on the source page. |
| 交易日期 | Date only; retain the source date. |
| 交易时刻 | Time only; null when not shown. |
| 产品名称 | Product/fund name exactly as displayed. |
| 基金代码 | Six-character text when shown; null for products with no code displayed. |
| 业务类型 | Exact displayed transaction type. |
| 申请数值 / 申请单位 | Numeric value and its displayed unit. `--` in the visual review sheet maps to null here plus a review note. |
| 确认数值 / 确认单位 | Numeric value and its displayed unit. `--` maps to null here. |
| 关联账户 | Account text exactly as displayed; null when absent. |
| 状态 | Exact displayed status, including failure/cancelled variants. |
| 来源文件 | Original page workbook filename. |

Rules:

- Do not convert a blank field into zero.
- Do not convert a displayed `--` into zero.
- Preserve unusual unit pairs such as 份 requested and 元 confirmed.
- Preserve duplicate-looking rows when both are visibly present.
- Short pages are valid; do not pad them with invented transactions.
