# Durden_skills

Peer-review skills and review workflows for NSFC grant applications.

本仓库用于存放面向科研评审和项目书预审的 reusable skills / workflow。当前重点是国自然面上（包括青C）项目评审 workflow，后续可能继续追加其他类型的科研评审或写作辅助 skill。

## 项目介绍

国家自然科学基金评审 skill 和工作流，通过多个专业 skill 的调用和协作，辅助完成项目书的结构化审阅。目前已开发 **面上项目评审（包括青C） skill**，后续可能追加其他类型项目的评审 workflow。

当前 skill 经过人工核查，验证了输出结果具备较高质量，可以作为快速审阅本子的“搭子”：帮助节约时间、搭建评审底稿，并尽量减少关键细节遗漏。

它也适合项目申请人在提交申请书之前，用来核对和检查内容质量，提前暴露创新性、研究逻辑、可行性、文献边界和结构性缺陷等问题。

这个仓库本质上也是一次练习：尝试把一个真实科研工作流，从临时 prompt 逐步整理成可复用的 skill / workflow / lightweight AI harness。欢迎交流、fork、提 issue 或提交改进。

## 声明

本项目是一个非官方、实验性的 AI workflow skill，用于学习交流、内部预审和工作流探索。

- 本项目不隶属于国家自然科学基金委员会，也不代表任何官方评审意见。
- 输出内容不能替代专家判断，使用者应自行进行人工复核。
- 请勿把真实、敏感、涉密或未经授权的项目书材料提交到公开 issue、PR 或不可信环境中。
- 本项目以 MIT License 开源，欢迎学习、交流、fork 和改进。

## Skills

### `skills/fund-screenshot-digitization`

基金交易截图数字化 skill：将无法导出的基金交易截图逐页转录为高精度 Excel，并合并为一个可供统计项目使用的单标签页输入文件。

主要能力：

- 按文件名排序建立页码与原图映射；
- 逐页、逐行保留日期、时间、产品、基金代码、交易类型、申请/确认数值与单位、账户和状态；
- 支持 4–8 个 agent 并行处理，每页独立输出，避免并发写同一个工作簿；
- 自动合并、页码覆盖、页内序号唯一性、基金代码、公式和短页校验；
- 明确区分 `--`、空白字段和数值零，不擅自补全截图中未显示的信息。

主要文件：

- `skills/fund-screenshot-digitization/SKILL.md`
- `skills/fund-screenshot-digitization/README.md`
- `skills/fund-screenshot-digitization/scripts/merge_workbooks.py`
- `skills/fund-screenshot-digitization/scripts/validate_workbooks.py`

使用示例：

```text
使用 $fund-screenshot-digitization，逐页识别这些基金交易截图，生成单页复核表，并合并成一个单标签页统计输入文件。
```

### `skills/nsfc-mianshang-review`

国家自然科学基金面上项目评审 skill 和工作流，通过一个入口 skill 调度多个专业 skill 协作完成结构化评审。目前已开发面上项目评审 workflow，适合用于项目申请人提交申请书之前的自查，也适合内部预审时快速搭建审阅底稿。

主要能力：

- PDF-to-TXT extraction
- cache-first staged review
- kill-mode internal triage
- polished Chinese final review output
- manual-review boundaries for figures and non-text evidence

Main files:

- `skills/nsfc-mianshang-review/SKILL.md`
- `skills/nsfc-mianshang-review/README.md`
- `skills/nsfc-mianshang-review/scripts/extract_nsfc_text.py`

### `skills/nsfc-review-ranking`

`nsfc-review-ranking` 用于对多个 `nsfc-mianshang-review` 已生成的评审结果进行横向排序、量化分档和对比总结。它不重新阅读原始 PDF，优先读取 `review/05_final_review.txt`、`review/06_submitted_review_comment.txt` 和 01-04 阶段文件，并根据 provenance header 区分 explicit skill call、fallback、protocol violation 和未完成 skeleton。

主要能力：

- 批量收集 `nsfc-review-*` 目录中的评审 TXT 产物
- 输入质量与 provenance 审计
- 提取单项目 source score 并给出横向校准分
- 输出中文排序报告和会话摘要

Main files:

- `skills/nsfc-review-ranking/SKILL.md`
- `skills/nsfc-review-ranking/scripts/collect_review_results.py`
- `skills/nsfc-review-ranking/references/scoring-rubric.txt`

## 质量与边界

当前 skill 经过人工核查，验证了输出结果具备较高质量，可以作为快速审阅本子的底稿，节约时间并帮助减少关键细节遗漏。不过它仍然不是正式评审系统，也不保证判断完全准确。

本人没有系统学习过编程，主要依靠 AI 辅助制作工具，肯定存在疏漏和不足，工具也会不定期迭代。欢迎交流、提建议和提交改进。

## 配套文件

- `LICENSE`: MIT 开源许可证
- `DISCLAIMER.md`: 免责声明
- `SECURITY.md`: 安全与敏感材料处理说明

This repository is intended to hold reusable skill bundles rather than full applications.


---

## AI 生物医学期刊追踪

`ai-biomedical-journal-watch` 用于持续追踪顶级综合期刊、医学与方法学期刊以及重要专业期刊中的生物医学 AI 内容。它会完成候选发现、证据补全、语义筛选、期刊优先级排序、结果审计和中文报告生成，并保留可追溯的 JSONL 决策记录。

当前公开版本：`v0.2.1`。

## 适用场景

- 每隔数天追踪顶级期刊中的生物医学 AI 新研究；
- 按最近72小时、96小时、7天或30天生成期刊速览；
- 重点关注临床 AI、医学影像、病理、组学、药物发现、蛋白设计、基础模型和科研智能体；
- 单独整理期刊中的 AI 新闻、社论、观点、评论和综述；
- 对抓取覆盖、文章类型、证据充分性和筛选结果进行审计；
- 在长时间窗口中限制正文长度，同时保留完整机器可读记录。

本工具定位为高频期刊监测，而不是严格意义上的系统综述。7天左右的窗口通常能在覆盖率、判断质量和阅读负担之间取得较好平衡；30天窗口候选量更大，适合回顾性扫描，但可能需要更多人工抽查。

## 监测的18本期刊

期刊层级只用于结果排序，不会把不相关内容变成符合项。

### 第一层：顶级综合期刊

1. Nature
2. Science
3. Cell

### 第二层：顶级医学与方法学期刊

4. Nature Medicine
5. Nature Biotechnology
6. Nature Methods
7. Nature Genetics
8. NEJM（The New England Journal of Medicine）
9. The Lancet

临床期刊只监测 NEJM 和 The Lancet 正刊，不包含 NEJM AI、The Lancet Digital Health 或其他临床子刊。

### 第三层：高影响专业期刊

10. Nature Cell Biology
11. Nature Machine Intelligence
12. Cell Stem Cell
13. Cell Metabolism
14. Cancer Cell
15. Science Translational Medicine

### 第四层：重要综合与专业期刊

16. Nature Communications
17. Developmental Cell
18. Science Advances

## 时间窗口

支持以下形式：

- `72h`：最近72小时；
- `96h`：最近96小时，也是默认窗口；
- `7d`：最近7天；
- `30d`：最近30天；
- 自定义时长，例如 `48h`、`14d`；
- 明确日期区间，例如 `2026-07-01..2026-07-15`。

滚动窗口采用半开区间 `[start, as_of)`。超过7天的任务按7天切片采集，最终合并去重并统一排序，避免一次性输入过大。

## 内容筛选规则

一篇研究进入主要结果，必须同时满足：

1. 内容属于人类健康、疾病、临床医学、生物医学研究、药物研发或相关生命科学范围；
2. AI/机器学习承担实质角色，例如模型训练、学习式推断、生成或表征学习、模型评估，或者作为被评价的临床干预；
3. 标题、摘要、正文导语或其他来源证据足以支持判断。

以下情况不会仅凭关键词自动纳入：

- 名称中含有 `transformer`，但实际指基因编辑器或其他生物技术产品；
- 普通贝叶斯或统计模型；
- 只使用“predictive”“automated”“intelligent”等宽泛词语；
- 常规生物信息学流程、数据集或图谱可能在未来用于AI，但当前研究没有明确AI功能；
- AI仅作为背景、比较对象或附带工具。

证据不足但疑似相关的原创研究进入 `needs_evidence`，不会被静默排除。

## 研究与趋势内容分流

报告把内容分为四类：

- `include`：符合标准的原创生物医学 AI 研究；
- `context`：与生物医学 AI 相关的 Review、Perspective、Preview、Editorial、News、Highlight、Comment、Commentary、Viewpoint 或非原创 Letter；
- `needs_evidence`：疑似相关但缺少摘要、正文或文章类型证据；
- `exclude`：非生物医学、没有实质AI作用、校正/撤稿或其他明确不符合内容。

趋势与观点不占用研究论文的20篇详写名额，默认只显示期刊、发布日期、类型、标题和链接。

## 排序与输出上限

主要排序顺序为：

1. 期刊层级；
2. 内容重要性；
3. 发布时间；
4. 期刊名称和标题，用于保持排序稳定。

默认输出限制：

- 详细研究：20篇；
- 单一期刊详写：按层级限制，最多5篇；
- 额外研究索引：72/96小时最多30篇，7天最多50篇，30天及以上最多80篇；
- 趋势与观点：20条；
- 逐条展示的待补证据：10条；
- 排除汇总：最多展示10个标准类别。

展示限制不会减少发现和筛选范围。未展示记录仍保存在 JSONL 中。

## 数据来源与特殊处理

工具综合使用期刊官网、RSS、Crossref、PubMed、Europe PMC 和其他可审计来源。部分期刊具有专门策略：

- Nature Communications：必须分页枚举官网文章列表，不能只依赖少量RSS条目；
- Nature Methods：优先从官网文章页取得在线日期、文章类型、摘要或导语；
- Cell Metabolism：先检查 PubMed/Europe PMC 的文章类型及勘误、校正和撤稿关系；
- Cell Press、AAAS、The Lancet：官网受限时使用 Crossref、PubMed 和 Europe PMC 的并集；
- NEJM：使用官方RSS发现，再由 PubMed 和 OpenAlex 补充摘要证据。

单个来源失败只影响相应期刊或记录，不会让整个任务简单地变成“全部失败”。

## 安装

将整个文件夹复制到 Codex skills 目录：

```text
%USERPROFILE%\.codex\skills\ai-biomedical-journal-watch
```

重新打开一个 Codex 任务后，使用：

```text
$ai-biomedical-journal-watch
```

## 使用示例

```text
使用 $ai-biomedical-journal-watch 检索最近7天的生物医学AI期刊内容，优先展示20篇研究。
```

```text
使用 $ai-biomedical-journal-watch 检索最近30天内容，保留AI相关评论和新闻，但限制趋势列表为20条。
```

## 审计与渲染

最终报告生成前必须审计 reviewed JSONL：

```powershell
python scripts\audit_reviewed_jsonl.py --input reviewed.jsonl --output audit.json
```

审计返回非零状态时，不应生成正式报告。

生成7天报告：

```powershell
python scripts\render_report_v321.py --window 7d --input reviewed.jsonl --output report.md
```

## 已知限制

- 出版商访问限制可能导致部分记录只有单一来源；
- 数据库收录和在线发表日期可能存在延迟；
- Letter、新闻导读和数据库文章类型偶尔需要人工复核；
- 30天窗口更容易出现边界误差和较大的阅读负担；
- 本工具不能替代系统综述、Meta分析或专家最终判断。

建议将7天监测作为常规使用模式，并对30天回顾中的边界条目进行抽查。

