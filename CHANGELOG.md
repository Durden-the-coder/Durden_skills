# 更新记录

## 2026-08-12 — 新增数据下载与基金数据 Skill

### `index-value-download`

- 新增从理杏仁（lixinger.com）批量下载指数估值历史 CSV 的 Skill；
- 支持 PE-TTM、PB、股息率等指标；
- 支持“上市以来”、10 年、5 年和 3 年时间范围；
- 支持断点续传、跳过已完成组合和缺口检查；
- 使用 Playwright + Edge 完成真实浏览器登录与下载；
- 强制通过 `LIXINGER_USER` 和 `LIXINGER_PASS` 环境变量传入凭据。

### `fund-nav-fetch`

- 新增从天天基金／东方财富公开接口抓取公募基金历史净值的 Skill；
- 支持基金名称自动查询代码、6 位基金代码和 JSON 映射输入；
- 获取单位净值、累计净值和日增长率；
- 按页抓取完整历史记录，自动去重、排序并生成 UTF-8-SIG CSV；
- 使用 Playwright、Referer 和路由拦截处理分页与 CORS 限制；
- 支持 Edge，失败时回退到 Playwright Chromium。

提交：[81339b1](https://github.com/Durden-the-coder/Durden_skills/commit/81339b11ef344f103ff46c95b7a28ab821c3b4f3)

## 2026-08-12 — 完善个人 Skill 仓库文档

- 根目录 README 增加 `ai-news-72h` 的完整介绍；
- 根目录 README 增加 `fund-screenshot-digitization` 的完整介绍；
- 统一 Skill 区块的标题层级、导航和可读性；
- 保留原有 NSFC 与生物医学期刊追踪内容；
- 将新增加的 `index-value-download` 和 `fund-nav-fetch` 加入根目录导航。

提交：[8c082c1](https://github.com/Durden-the-coder/Durden_skills/commit/8c082c1de5b050ef4b37ada0e0cbd1888e599ffe)、[b5f1f7b](https://github.com/Durden-the-coder/Durden_skills/commit/b5f1f7b01e5795512007444e5a9eb9ae88b93930)

## 2026-08-12 — 新增 `fund-screenshot-digitization`

- 新增基金交易截图逐页数字化 Skill；
- 支持按文件名排序建立页码映射；
- 支持逐页、逐行转录和短页保留；
- 支持 4–8 个 Agent 并行处理，每页独立产物；
- 新增确定性 Excel 合并脚本；
- 新增工作簿结构、页码、基金代码、公式和重复行校验脚本；
- 新增交易数据契约，明确区分 `--`、空白字段和数值零；
- 保留 Codex 宿主适配配置，同时兼容其他 Agent。

提交：[184577a](https://github.com/Durden-the-coder/Durden_skills/commit/184577a90b95b5993211b65297b19eb7508369e1)

## 2026-07-30 — `ai-biomedical-journal-watch` v0.2.1

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

