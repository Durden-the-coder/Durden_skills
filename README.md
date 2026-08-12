# Durden_skills

个人 Agent Skill 仓库。

这里收录我在实际工作中整理、验证和持续迭代的可复用 Skill。每个 Skill 都以自身目录中的 `SKILL.md` 为核心执行规范，并根据需要附带脚本、参考资料、测试样例和宿主适配配置。

本 README 保留各个 Skill 的详细介绍、能力边界和使用说明。Skill 的排列依据是其首次进入本仓库的 GitHub 提交时间，后续更新不会改变其首次发布日期。

## Skills

### 1. `skills/nsfc-mianshang-review`

首次进入仓库：2026-05-02

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

### 2. `skills/nsfc-review-ranking`

首次进入仓库：2026-05-08

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

### 3. `skills/ai-news-72h`

首次进入仓库：2026-06-15

用于检索、核验并撰写最近 72 小时全球 AI 新闻和 AI for Science 研究动态的 Skill。除基础模型、Agent、硬件、软件和应用新闻外，重点捕捉刚发布的科研消息，包括早期预印本、生命医学重点期刊论文，以及主要实验室首次公开的新研究或科研资源。

## 主要能力

- 按用户时区计算精确的最近 72 小时时间窗；
- 区分事件发生时间、首次公开时间和媒体发布时间；
- 检索模型、Agent、硬件、软件、应用和产业新闻；
- 监测 arXiv、bioRxiv 和 medRxiv 的首次发布预印本；
- 核对 arXiv `v1` 时间，排除 `v2`、`v3` 等后续更新；
- 监测指定生命与医学重点期刊的新在线原创研究；
- 监测主要实验室首次公开的新研究、模型、数据集和科研工具；
- 提供摘要、验证情况、重要性评价、局限和原始来源；
- 执行时间、事实、来源、研究类型和链接检查。

## AI for Science 信源

包括 arXiv、bioRxiv、medRxiv，以及 Nature、Science、Cell、Nature Medicine、Nature Biotechnology、Nature Methods、Nature Genetics、Nature Communications、Science Advances、PNAS、Cell Systems、Patterns、Cancer Cell、NEJM、NEJM AI、The Lancet、The Lancet Digital Health、Nature Machine Intelligence 和 Science Translational Medicine 等期刊。

实验室官方渠道重点包括 OpenAI、Anthropic、Google Research、Google DeepMind、Microsoft Research、Meta FAIR、NVIDIA Research、Broad Institute、EMBL-EBI、Allen Institute、Arc Institute 和 Chan Zuckerberg Initiative。

## AI for Science 纳入范围

AI 或机器学习必须是核心方法、主要技术贡献、主要研究对象，或对科学发现和实验流程具有实质作用。重点包括：

- 生物学基础模型和生物医学多模态模型；
- 蛋白质结构预测、功能建模和生成式设计；
- AI 药物发现与分子生成；
- 基因组学、单细胞和空间组学机器学习；
- AI 医学影像与数字病理；
- 虚拟细胞和数据驱动的生物系统模拟；
- AI 辅助实验设计与自动化实验室；
- 生物医学科学 Agent；
- 临床 AI 模型和医疗多模态模型。

排除仅使用常规统计分析、传统生物信息学流程、仅在摘要或讨论中提及 AI，或 AI 不是主要方法和贡献的内容。

## 输出与验证

默认输出包括精确统计窗口、检索截止时间、模型与产业新闻、AI for Science 研究、生命医学期刊论文、实验室科研动态、科学问题、AI 方法、关键结果、验证情况、开放情况、综合重要性评价、局限和原始来源链接。

预印本必须标注“尚未同行评议”，核对首次版本和发布时间，不把作者报告的结果写成独立验证结论。

### 4. `skills/ai-biomedical-journal-watch`

首次进入仓库：2026-07-30

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

### 5. `skills/fund-screenshot-digitization`

首次进入仓库：2026-08-12

一个以 `SKILL.md` 为核心规范、可在 Codex 中完整调用，也可迁移到其他支持 skill/instruction 文件的 Agent 的基金交易截图数字化 skill。它将无法导出的交易截图逐页转录为高精度 Excel，并合并为一个可供统计项目使用的单标签页输入文件。

主要能力：

- 按文件名排序建立页码与原图映射；
- 逐页、逐行保留日期、时间、产品、基金代码、交易类型、申请/确认数值与单位、账户和状态；
- 支持 4–8 个 Agent 并行处理，每页独立输出，避免并发写同一个工作簿；
- 自动合并、页码覆盖、页内序号唯一性、基金代码、公式和短页校验；
- 明确区分 `--`、空白字段和数值零，不擅自补全截图中未显示的信息。

主要文件：

- `skills/fund-screenshot-digitization/SKILL.md`：跨 Agent 的核心执行规范；
- `skills/fund-screenshot-digitization/README.md`：安装、调用和兼容性说明；
- `skills/fund-screenshot-digitization/agents/openai.yaml`：Codex 的宿主适配配置；
- `skills/fund-screenshot-digitization/scripts/merge_workbooks.py`；
- `skills/fund-screenshot-digitization/scripts/validate_workbooks.py`。

Codex 使用示例：

```text
使用 $fund-screenshot-digitization，逐页识别这些基金交易截图，生成单页复核表，并合并成一个单标签页统计输入文件。
```

其他 Agent 使用时，以 `SKILL.md` 为唯一核心规范；如果宿主支持自动发现 skill，按其目录规则安装即可；如果不支持，则在任务中直接提供该文件路径或加载其内容。

## 仓库级质量与边界

这些 Skill 是个人工作流工具和实验性 AI 辅助工具，不代表任何官方机构或专业意见。输出结果应结合原始材料进行人工复核，不能替代专家判断。

本人没有系统学习过编程，主要依靠 AI 辅助制作工具，肯定存在疏漏和不足，工具也会不定期迭代。欢迎交流、提建议和提交改进。

请勿把真实、敏感、涉密或未经授权的材料提交到公开 issue、PR 或其他不可信环境。

基金交易截图 Skill 只提供截图转录和表格整理能力，不提供投资建议、基金推荐、收益预测或交易决策。截图识别可能存在遗漏或误读，所有数字和状态都应依据原图复核。

## 安装与调用

不同 Agent 的自动发现机制可能不同。通常应将目标 Skill 的整个目录放入宿主的 skills、instructions 或规则目录，并确保读取其中的 `SKILL.md`。

Codex 用户可将 Skill 目录复制到：

```text
%USERPROFILE%\\.codex\\skills\\<skill-name>
```

例如基金截图 Skill：

```text
%USERPROFILE%\\.codex\\skills\\fund-screenshot-digitization
```

然后使用：

```text
$fund-screenshot-digitization
```

其他 Agent 如果不支持自动发现，可在任务中直接提供 `SKILL.md` 的路径或加载其内容。各目录中的 `agents/openai.yaml` 是可选的 Codex 宿主适配文件，不替代 `SKILL.md`。

## 仓库结构

```text
Durden_skills/
├── README.md
├── LICENSE
├── DISCLAIMER.md
├── SECURITY.md
├── CHANGELOG.md
└── skills/
    ├── nsfc-mianshang-review/
    ├── nsfc-review-ranking/
    ├── ai-news-72h/
    ├── ai-biomedical-journal-watch/
    └── fund-screenshot-digitization/
```

每个 Skill 通常包含：

- `SKILL.md`：核心执行规范；
- `README.md`：安装、使用和详细说明；
- `agents/openai.yaml`：可选的 Codex 宿主适配配置；
- `scripts/`：辅助脚本；
- `references/`：数据契约、来源策略或其他参考资料；
- `tests/`：回归测试或示例输入。

## 配套文件

- [MIT License](./LICENSE)
- [DISCLAIMER.md](./DISCLAIMER.md)
- [SECURITY.md](./SECURITY.md)
- [CHANGELOG.md](./CHANGELOG.md)

This repository is intended to hold reusable skill bundles rather than full applications.
