# 更新记录

## v0.2.1 — 2026-07-30

### 期刊范围

- 固定监测18本目标期刊；
- Nature、Science、Cell 正刊优先；
- 临床期刊仅保留 NEJM 和 The Lancet 正刊；
- 移除 NEJM AI 与 The Lancet Digital Health。

### 时间窗口与输出

- 支持72小时、96小时、7天、30天、自定义时长及明确日期区间；
- 默认优先详写20篇研究；
- 7天窗口最多展示50篇额外研究索引；
- 30天及以上窗口最多展示80篇额外研究索引；
- 每条展示内容增加发布日期；
- Markdown 使用带 BOM 的 UTF-8，提高 Windows 中文兼容性。

### 筛选与排序

- 按期刊层级、内容重要性和发布时间排序；
- 增加 `include`、`context`、`needs_evidence`、`exclude` 四状态；
- Review、Perspective、News、Editorial 等非原创内容进入趋势与观点栏目；
- 无摘要或证据不足的 Letter 不再自动纳入原创研究；
- 增加 `transformer`、`predictive`、普通统计模型等词义碰撞防护；
- 数据集、图谱、队列和常规计算流程必须有明确AI功能才能纳入。

### 抓取与证据

- 为 Nature Methods 增加官网文章页证据策略；
- 为 Nature Communications 增加官网分页枚举要求；
- 为 Cell Metabolism 增加勘误、校正和撤稿识别；
- Cell Press、AAAS、The Lancet 受限时使用 Crossref、PubMed、Europe PMC 并集；
- NEJM 使用官方RSS发现，并通过 PubMed、OpenAlex 补充摘要。

### 审计与质量控制

- 最终报告前强制运行 JSONL 审计；
- 纳入和趋势内容必须具有日期及证据链接；
- 大型任务出现零 `needs_evidence` 时发出警告；
- 排除汇总默认限制为10类，完整记录保留在JSONL；
- 增加 Nature Methods、Cell Metabolism、时间窗口、趋势分流、证据长度和编码回归测试。

`v0.2.1` 对应此前内部测试的 V3.2.1 稳定线；从本版本开始，对外统一使用语义化版本号。

