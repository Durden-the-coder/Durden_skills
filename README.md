# Durden_skills

个人 Agent Skill 仓库，收录经过实际使用、验证和持续迭代的可复用工作流。

## 内容导航

1. [mianshang-skills](#1-mianshang-skills)：国家自然科学基金面上项目评审与结果排序
2. [ai-news-72h](#2-ai-news-72h)：最近 72 小时 AI 新闻与 AI for Science 研究动态
3. [AI 生物医学期刊追踪](#3-ai-生物医学期刊追踪-skill)：重点期刊中的生物医学 AI 研究监测
4. [fund-screenshot-digitization](#4-fund-screenshot-digitization)：基金交易截图逐页数字化与 Excel 汇总

---

## 1. mianshang-skills

Peer-review skills and review workflows for NSFC grant applications.

本仓库用于存放面向科研评审和项目书预审的 reusable skills / workflow。当前重点是国自然面上（包括青C）项目评审 workflow，后续可能继续追加其他类型的科研评审或写作辅助 skill。

### 项目介绍

国家自然科学基金评审 skill 和工作流，通过多个专业 skill 的调用和协作，辅助完成项目书的结构化审阅。目前已开发 **面上项目评审（包括青C） skill**，后续可能追加其他类型项目的评审 workflow。

当前 skill 经过人工核查，验证了输出结果具备较高质量，可以作为快速审阅本子的“搭子”：帮助节约时间、搭建评审底稿，并尽量减少关键细节遗漏。

它也适合项目申请人在提交申请书之前，用来核对和检查内容质量，提前暴露创新性、研究逻辑、可行性、文献边界和结构性缺陷等问题。

这个仓库本质上也是一次练习：尝试把一个真实科研工作流，从临时 prompt 逐步整理成可复用的 skill / workflow / lightweight AI harness。欢迎交流、fork、提 issue 或提交改进。

### 声明

本项目是一个非官方、实验性的 AI workflow skill，用于学习交流、内部预审和工作流探索。

- 本项目不隶属于国家自然科学基金委员会，也不代表任何官方评审意见。
- 输出内容不能替代专家判断，使用者应自行进行人工复核。
- 请勿把真实、敏感、涉密或未经授权的项目书材料提交到公开 issue、PR 或不可信环境中。
- 本项目以 MIT License 开源，欢迎学习、交流、fork 和改进。

### Skills

#### `skills/nsfc-mianshang-review`

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

#### `skills/nsfc-review-ranking`

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

### 质量与边界

当前 skill 经过人工核查，验证了输出结果具备较高质量，可以作为快速审阅本子的底稿，节约时间并帮助减少关键细节遗漏。不过它仍然不是正式评审系统，也不保证判断完全准确。

本人没有系统学习过编程，主要依靠 AI 辅助制作工具，肯定存在疏漏和不足，工具也会不定期迭代。欢迎交流、提建议和提交改进。

### 配套文件

- `LICENSE`: MIT 开源许可证
- `DISCLAIMER.md`: 免责声明
- `SECURITY.md`: 安全与敏感材料处理说明

This repository is intended to hold reusable skill bundles rather than full applications.

---

## 2. ai-news-72h

用于检索、核验并撰写最近 72 小时全球 AI 新闻和 AI for Science 研究动态的 Codex Skill。

除基础模型、Agent、硬件、软件和应用新闻外，本 Skill 重点捕捉刚发布的科研消息，包括早期预印本、生命医学重点期刊论文，以及主要实验室首次公开的新研究或科研资源。

### 主要能力

- 按用户时区计算精确的最近 72 小时时间窗
- 区分事件发生时间、首次公开时间和媒体发布时间
- 检索模型、Agent、硬件、软件、应用和产业新闻
- 监测 arXiv、bioRxiv 和 medRxiv 的首次发布预印本
- 核对 arXiv `v1` 时间，排除 `v2`、`v3` 等后续更新
- 监测指定生命与医学重点期刊的新在线原创研究
- 监测主要实验室首次公开的新研究、模型、数据集和科研工具
- 提供摘要、验证情况、重要性评价、局限和原始来源
- 执行时间、事实、来源、研究类型和链接检查
- 使用 fresh subagent 独立运行，避免受当前会话上下文污染
- 将实际执行模型名称加入 Markdown 输出文件名

### AI for Science 信源

#### 早期预印本

- arXiv
- bioRxiv
- medRxiv

只纳入最近 72 小时内首次发布的版本：

- arXiv 使用 `v1` 首次提交时间；
- bioRxiv 和 medRxiv 使用首个版本发布日期；
- 不纳入 `v2`、`v3` 等版本更新；
- 不因网页更新时间改变而将旧论文视为新研究。

#### 生命与医学重点期刊

- Nature
- Science
- Cell
- Nature Medicine
- Nature Biotechnology
- Nature Methods
- Nature Genetics
- Nature Communications
- Science Advances
- PNAS（Proceedings of the National Academy of Sciences）
- Cell Systems
- Patterns（Cell Press AI 期刊）
- Cancer Cell
- The New England Journal of Medicine
- NEJM AI
- The Lancet
- The Lancet Digital Health
- Nature Machine Intelligence
- Science Translational Medicine

只纳入 AI 或机器学习构成核心方法或主要贡献的原创研究，并使用 `Published online` 日期判断时间窗。

不使用 PubMed 作为发现或纳入来源。

#### 实验室官方渠道

重点包括：

- OpenAI
- Anthropic
- Google Research
- Google DeepMind
- Microsoft Research
- Meta FAIR
- NVIDIA Research
- Broad Institute
- EMBL-EBI
- Allen Institute
- Arc Institute
- Chan Zuckerberg Initiative

只纳入首次公开的新研究、模型、数据集、科研工具或实验系统。不纳入旧论文的新博客、重新宣传或成果回顾。

### AI for Science 纳入范围

AI 或机器学习必须是核心方法、主要技术贡献、主要研究对象，或对科学发现和实验流程具有实质作用。重点包括：

- 生物学基础模型和生物医学多模态模型
- 蛋白质结构预测、功能建模和生成式设计
- AI 药物发现与分子生成
- 基因组学、单细胞和空间组学机器学习
- AI 医学影像与数字病理
- 虚拟细胞和数据驱动的生物系统模拟
- AI 辅助实验设计与自动化实验室
- 生物医学科学 Agent
- 临床 AI 模型和医疗多模态模型

排除：

- 仅使用常规统计分析的研究
- 仅使用传统生物信息学流程的研究
- 只在摘要或讨论中提及 AI 的论文
- AI 不是主要方法或贡献的普通生命医学论文
- 一般医疗软件或普通行业新闻
- News、Editorial、Comment、Perspective 和普通综述

### 预印本处理

刚发布的预印本可以仅依据原始论文页面纳入，无须等待媒体报道，但必须：

- 标注“预印本，尚未同行评议”；
- 核对首次版本和发布时间；
- 区分作者声明与本简报判断；
- 使用“综合评价”，不声称存在第三方共识；
- 检查代码、数据和模型是否开放；
- 不把作者报告的基准结果视为独立验证。

### 输出内容

默认包括：

1. 精确统计窗口与检索截止时间
2. Introduction
3. 模型、Agent、硬件、软件和应用新闻
4. AI for Science 早期研究
5. 生命与医学重点期刊论文
6. 实验室官方科研动态
7. 科学问题、AI 方法、数据和关键结果
8. 计算、湿实验或临床验证情况
9. 代码、数据和模型开放情况
10. 综合重要性评价与主要局限
11. 原始来源链接
12. 全文总结与方法局限

### 隔离执行与文件名

每次运行由一个不继承当前对话历史的 fresh subagent 独立完成。协调者只传递当前请求、时间与时区、输出目录、模型标识及 Skill 文件，不传递此前候选新闻或研究判断。

结果必须写入 Markdown 文件，并在 `.md` 前加入实际执行 subagent 的模型名称：

```text
ai-news-72h_YYYY-MM-DD_<model-name>.md
```

例如：

```text
ai-news-72h_2026-07-01_deepseek-V4-pro.md
```

正文开头同时记录实际生成模型。

### 使用示例

```text
搜索最近 72 小时 AI 领域的新闻，并单列 AI for Science。
检查 arXiv、bioRxiv、medRxiv、生命医学重点期刊和主要实验室官方渠道。
预印本只纳入首次发布版本，arXiv 必须核对 v1 时间。
```

### 安装

将本目录放入 Codex Skills 目录：

```text
~/.codex/skills/ai-news-72h
```

### 文件结构

```text
ai-news-72h/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── references/
│   └── ai-for-science-sources.md
└── agents/
    └── openai.yaml
```

- [`SKILL.md`](./SKILL.md)：核心工作流和通用验证清单
- [CHANGELOG.md](./CHANGELOG.md)：版本更新记录与验证结果
- [`references/ai-for-science-sources.md`](./references/ai-for-science-sources.md)：AI for Science 信源、筛选、输出和专项验证规则

### 免责声明

本 Skill 用于新闻研究、资料整理和辅助写作。预印本尚未同行评议，期刊论文和机构声明也需要结合原始数据、实验设计和后续验证进行人工判断。

---

## 3. AI 生物医学期刊追踪 Skill

`ai-biomedical-journal-watch` 用于持续追踪顶级综合期刊、医学与方法学期刊以及重要专业期刊中的生物医学 AI 内容。它会完成候选发现、证据补全、语义筛选、期刊优先级排序、结果审计和中文报告生成，并保留可追溯的 JSONL 决策记录。

当前公开版本：`v0.2.1`。

### 适用场景

- 每隔数天追踪顶级期刊中的生物医学 AI 新研究；
- 按最近72小时、96小时、7天或30天生成期刊速览；
- 重点关注临床 AI、医学影像、病理、组学、药物发现、蛋白设计、基础模型和科研智能体；
- 单独整理期刊中的 AI 新闻、社论、观点、评论和综述；
- 对抓取覆盖、文章类型、证据充分性和筛选结果进行审计；
- 在长时间窗口中限制正文长度，同时保留完整机器可读记录。

本工具定位为高频期刊监测，而不是严格意义上的系统综述。7天左右的窗口通常能在覆盖率、判断质量和阅读负担之间取得较好平衡；30天窗口候选量更大，适合回顾性扫描，但可能需要更多人工抽查。

### 监测的18本期刊

期刊层级只用于结果排序，不会把不相关内容变成符合项。

#### 第一层：顶级综合期刊

1. Nature
2. Science
3. Cell

#### 第二层：顶级医学与方法学期刊

4. Nature Medicine
5. Nature Biotechnology
6. Nature Methods
7. Nature Genetics
8. NEJM（The New England Journal of Medicine）
9. The Lancet

临床期刊只监测 NEJM 和 The Lancet 正刊，不包含 NEJM AI、The Lancet Digital Health 或其他临床子刊。

#### 第三层：高影响专业期刊

10. Nature Cell Biology
11. Nature Machine Intelligence
12. Cell Stem Cell
13. Cell Metabolism
14. Cancer Cell
15. Science Translational Medicine

#### 第四层：重要综合与专业期刊

16. Nature Communications
17. Developmental Cell
18. Science Advances

### 时间窗口

支持以下形式：

- `72h`：最近72小时；
- `96h`：最近96小时，也是默认窗口；
- `7d`：最近7天；
- `30d`：最近30天；
- 自定义时长，例如 `48h`、`14d`；
- 明确日期区间，例如 `2026-07-01..2026-07-15`。

滚动窗口采用半开区间 `[start, as_of)`。超过7天的任务按7天切片采集，最终合并去重并统一排序，避免一次性输入过大。

### 内容筛选规则

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

### 研究与趋势内容分流

报告把内容分为四类：

- `include`：符合标准的原创生物医学 AI 研究；
- `context`：与生物医学 AI 相关的 Review、Perspective、Preview、Editorial、News、Highlight、Comment、Commentary、Viewpoint 或非原创 Letter；
- `needs_evidence`：疑似相关但缺少摘要、正文或文章类型证据；
- `exclude`：非生物医学、没有实质AI作用、校正/撤稿或其他明确不符合内容。

趋势与观点不占用研究论文的20篇详写名额，默认只显示期刊、发布日期、类型、标题和链接。

### 排序与输出上限

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

### 数据来源与特殊处理

工具综合使用期刊官网、RSS、Crossref、PubMed、Europe PMC 和其他可审计来源。部分期刊具有专门策略：

- Nature Communications：必须分页枚举官网文章列表，不能只依赖少量RSS条目；
- Nature Methods：优先从官网文章页取得在线日期、文章类型、摘要或导语；
- Cell Metabolism：先检查 PubMed/Europe PMC 的文章类型及勘误、校正和撤稿关系；
- Cell Press、AAAS、The Lancet：官网受限时使用 Crossref、PubMed 和 Europe PMC 的并集；
- NEJM：使用官方RSS发现，再由 PubMed 和 OpenAlex 补充摘要证据。

单个来源失败只影响相应期刊或记录，不会让整个任务简单地变成“全部失败”。

### 安装

将整个文件夹复制到 Codex skills 目录：

```text
%USERPROFILE%\.codex\skills\ai-biomedical-journal-watch
```

重新打开一个 Codex 任务后，使用：

```text
$ai-biomedical-journal-watch
```

### 使用示例

```text
使用 $ai-biomedical-journal-watch 检索最近7天的生物医学AI期刊内容，优先展示20篇研究。
```

```text
使用 $ai-biomedical-journal-watch 检索最近30天内容，保留AI相关评论和新闻，但限制趋势列表为20条。
```

### 审计与渲染

最终报告生成前必须审计 reviewed JSONL：

```powershell
python scripts\audit_reviewed_jsonl.py --input reviewed.jsonl --output audit.json
```

审计返回非零状态时，不应生成正式报告。

生成7天报告：

```powershell
python scripts\render_report_v321.py --window 7d --input reviewed.jsonl --output report.md
```

### 已知限制

- 出版商访问限制可能导致部分记录只有单一来源；
- 数据库收录和在线发表日期可能存在延迟；
- Letter、新闻导读和数据库文章类型偶尔需要人工复核；
- 30天窗口更容易出现边界误差和较大的阅读负担；
- 本工具不能替代系统综述、Meta分析或专家最终判断。

建议将7天监测作为常规使用模式，并对30天回顾中的边界条目进行抽查。

---

## 4. fund-screenshot-digitization

一个以 `SKILL.md` 为核心规范、优先保证 Codex 完整调用，同时兼容其他 Agent 的基金交易截图数字化 skill。它将截图逐页转录为 Excel，并汇总为单标签页统计输入文件。

### Codex 支持（首要兼容目标）

仓库保留了 Codex 所需的宿主适配文件 `agents/openai.yaml`，不要在安装或迁移时删除、重命名或跳过它。

将整个目录复制到 Codex skill 目录：

```text
%USERPROFILE%\.codex\skills\fund-screenshot-digitization
```

新建 Codex 任务后调用：

```text
$fund-screenshot-digitization
```

使用示例：

```text
使用 $fund-screenshot-digitization，逐页识别这些基金交易截图，生成单页复核表，并合并成一个单标签页统计输入文件。
```

Codex 的执行依据是 `SKILL.md`；`agents/openai.yaml` 只负责宿主发现、显示名称和默认调用提示，不替代核心流程。

### 其他 Agent 兼容方式

`SKILL.md` 是跨 Agent 可复用的核心文件，不依赖 Codex API 或专有工具。对于其他支持 skill/instruction 文件的 Agent：

1. 将整个 `fund-screenshot-digitization` 目录放入该 Agent 的 skills、instructions 或可加载规则目录；
2. 确保 Agent 读取 `SKILL.md`，并把它作为本任务的执行规范；
3. 如果宿主不能自动发现 skill，则在任务中提供 `SKILL.md` 的文件路径，或直接加载其内容；
4. 使用 `scripts/merge_workbooks.py` 和 `scripts/validate_workbooks.py` 完成合并与校验；
5. 保留 `agents/openai.yaml` 即可兼容 Codex，同时不影响其他 Agent 忽略该可选适配文件。

通用调用示例：

```text
请读取 fund-screenshot-digitization/SKILL.md，逐页识别指定的基金交易截图。每页独立输出并复核，完成后合并为一个名为“交易明细”的单标签页 Excel，并运行校验脚本。
```

### 适用场景

- 基金网站不支持交易记录导出，只能从截图恢复数据；
- 需要按页精细识别日期、时间、产品、基金代码、交易类型、申请/确认数值、单位、账户和状态；
- 需要将多个逐页 Excel 合并成可供其他项目统计的单表文件；
- 需要对页码覆盖、行号唯一性、基金代码格式、公式和短页进行自动检查。

### 工作方式

1. 按文件名排序建立页码与原图的映射；
2. 每页独立识别，不让多个 Agent 同时写同一个工作簿；
3. 使用第 13 页模板生成页面级 Excel，并保留 `交易记录`、`数字字段` 两个工作表；
4. 对特殊状态、`--`、空白字段、异常单位和短页原样保留；
5. 通过合并脚本生成一个 `交易明细` 标签页；
6. 运行校验脚本检查缺页、重复页内序号、基金代码、公式和记录数。

### 目录

```text
SKILL.md
agents/openai.yaml
scripts/merge_workbooks.py
scripts/validate_workbooks.py
references/data-contract.md
```

### 免责声明

本 Skill 只提供截图转录和表格整理能力，不提供投资建议、基金推荐、收益预测或交易决策。截图识别可能存在遗漏或误读，所有数字和状态都应由使用者依据原图复核。使用者应自行负责数据保密、合规和由数据使用产生的后果。本项目不隶属于天天基金、任何基金管理人或金融监管机构。

### 许可证

本 Skill 采用 [MIT License](../../LICENSE)。仓库级免责条款见 [DISCLAIMER.md](../../DISCLAIMER.md)。


---

## 5. index-value-download

从理杏仁（lixinger.com）批量下载指数估值历史数据 CSV，支持 PE-TTM、PB 和股息率等指标，并统一使用“市值加权”和“按日—全部时间段”粒度。

主要能力：

- 支持“上市以来”、10 年、5 年和 3 年等时间范围；
- 支持断点续传、跳过已完成文件和缺口检查；
- 默认处理一组常用指数，也可以通过 `--indices` 指定指数；
- 依赖 Playwright 与 Edge 浏览器，使用真实浏览器流程完成登录和下载；
- 账号和密码只通过 `LIXINGER_USER`、`LIXINGER_PASS` 环境变量传入，不写入脚本、日志或记忆。

主要文件：

- [`SKILL.md`](skills/index-value-download/SKILL.md)：执行规范、凭据要求和操作流程；
- [`README.md`](skills/index-value-download/README.md)：安装、参数与使用说明；
- [`lixinger_download.py`](skills/index-value-download/scripts/lixinger_download.py)：批量下载脚本。

基本调用示例：

```bash
python scripts/lixinger_download.py --range "上市以来" --out "D:/指数估值数据" --skip-existing
```

使用该 Skill 前必须由用户提供本轮使用的理杏仁账号信息；不得使用历史会话、示例或缓存凭据。

## 6. fund-nav-fetch

从天天基金／东方财富公开接口获取公募基金历史净值，并按基金生成 UTF-8-SIG 编码的 CSV 文件。支持直接输入 6 位基金代码、输入基金名称自动查询代码，或读取名称到代码的 JSON 映射。

主要能力：

- 获取单位净值、累计净值和日增长率；
- 通过真实浏览器、Referer 和路由拦截绕过常见 CORS 与分页问题；
- 按 `pageIndex` 逐页获取完整历史记录，不依赖被忽略的 `pageSize`；
- 自动去重、按日期升序排列并按基金名称生成安全文件名；
- 支持 Edge，失败时可回退到 Playwright 自带 Chromium；
- 不需要会员、登录或账号密码。

主要文件：

- [`SKILL.md`](skills/fund-nav-fetch/SKILL.md)：接口约束、执行流程和运行环境；
- [`tips.md`](skills/fund-nav-fetch/references/tips.md)：接口、分页、Referer 和 Playwright 路由陷阱；
- [`fetch_fund_nav.py`](skills/fund-nav-fetch/scripts/fetch_fund_nav.py)：历史净值抓取脚本。

基本调用示例：

```bash
python scripts/fetch_fund_nav.py --codes "110003,163406"
```

输出文件按以下形式命名：

```text
<代码>_<名称>_净值_完整_<起始年>-<结束年>.csv
```

注意：该 Skill 仅用于公开历史数据抓取和整理，不构成投资建议，也不保证数据适合直接用于交易决策。
