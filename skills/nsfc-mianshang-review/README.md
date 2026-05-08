# nsfc-mianshang-review

**当前版本：** `0.5.7`

`nsfc-mianshang-review` 是一个面向 **国家自然科学基金面上项目（2026 版）** 的评审 workflow skill。它不是单纯的“写评语提示词”，而是一套分阶段、低 token、可复用、可审计的评审流程。

它主要服务两类场景：

1. 申报前内部预审
2. 面向正式函评风格的结构化审阅

它特别适合中文项目书，并默认输出**润色过的中文评审文本**。

---

## 安装和使用

### 1. 安装

确认 skill 目录至少包含：

```text
nsfc-mianshang-review/
  SKILL.md
  README.md
  CHANGELOG.md
  scripts/
    extract_nsfc_text.py
  references/
    scoring-rubric.txt
    output-templates.txt
```

从 GitHub 安装时，可按目标 agent 支持的方式安装，例如：

```bash
npx skills add Durden-the-coder/Durden_skills/skills/nsfc-mianshang-review --agent codex --global --yes
```

或：

```bash
npx skills add Durden-the-coder/Durden_skills/skills/nsfc-mianshang-review --agent claude-code --global --yes
```

如果当前 agent 不支持上述命令，也可以把整个 `nsfc-mianshang-review` 文件夹复制到该 agent 的本地 skills 目录。

### 2. 推荐同时安装的 supporting skills

这个 workflow 可以在 supporting skills 缺失时使用 fallback agent role 继续完成评审，但输出质量通常会下降，尤其是文献新颖性核查、严苛反驳和最终中文润色。因此，正式评审前建议同时安装：

```text
scientific-critical-thinking
literature-review
reviewer-2-simulator
peer-review
scientific-writing
```

各阶段优先显式调用顺序为：

```text
01_scientific_critique.txt      -> scientific-critical-thinking
02_literature_checks.txt        -> literature-review
03_reviewer2_stress_test.txt    -> reviewer-2-simulator
04_peer_review_draft.txt        -> peer-review
05_final_review.txt             -> scientific-writing
06_submitted_review_comment.txt -> scientific-writing
```

如果 agent 弹出 skill 调用权限确认，建议允许上述 skill。若某个 supporting skill 未安装、被权限阻断或调用失败，stage 文件的 provenance header 必须记录真实原因，不能伪装为已调用成功。

### 3. 最小输入

一次完整 workflow 理想情况下只需要：

- 项目书 PDF 或 TXT 路径
- PDF 密码（仅加密 PDF 需要）

示例：

```text
使用 nsfc-mianshang-review 评审：
D:\AI projects\claude_code\2026国自然评审\项目书\proposal.pdf
PDF 密码：your-password
```

workflow 会优先执行本地 PDF/TXT 提取，并自动创建 review 工作目录。

### 4. 默认输出目录

如果不显式指定 `--workdir`，输出目录会自动创建在“项目书文件夹的上一级”，前缀为 `nsfc-review-`。

例如项目书位于：

```text
D:\AI projects\claude_code\2026国自然评审\项目书\proposal.pdf
```

默认输出到：

```text
D:\AI projects\claude_code\2026国自然评审\nsfc-review-proposal\
```

这样可以保持原始项目书文件夹干净，不把中间产物写进 `项目书\`。

### 5. 脚本运行方式

agent 应优先使用：

```bash
<python> scripts/extract_nsfc_text.py --proposal "D:\path\proposal.pdf" --password "your-password" --init-review-files
```

如果用户指定了 review 目录，再添加：

```bash
--workdir "D:\path\review-dir"
```

`--init-review-files` 会预先生成 review 阶段骨架文件，方便 Claude Code、Codex 或其他 agent 在同一目录下继续补全后续阶段。

---

## 这个 skill 解决什么问题

长篇基金 PDF 直接塞给模型，常见会出现 4 类问题：

1. token 消耗很高
2. 模型反复读 PDF，容易漂移
3. 评审意见容易泛泛而谈
4. 最终资助建议常被“题目重要、基础不错”这类表面优点冲淡

这个 workflow 的目标是把这些问题拆开处理：

- 先抽文本，再评审
- 先建 cache，再下判断
- 先找结构性缺陷，再写正式意见
- 把“可修改问题”和“应毙问题”区分开

---

## 支持 skills 的调用策略

这个 skill 是一个 **workflow harness / router**。它会优先尝试显式调用以下 supporting skills：

- `scientific-critical-thinking`
- `literature-review`
- `reviewer-2-simulator`
- `peer-review`
- `scientific-writing`

但不同 agent 对“skill 调用另一个 skill”的支持不一致。Claude Code、Codex、OpenClaw、腾讯 WorkBuddy 等环境可能只显示调用了 `nsfc-mianshang-review`，并不会在 UI 中展示 supporting skills 的显式调用。

因此从 `0.4.7` 开始，本 workflow 的规则进一步收紧：

- 能显式调用 supporting skill 时，必须先尝试显式调用，而不是直接由当前 agent 扮演该角色。
- supporting skill 未安装、无法加载、权限拒绝或运行时不支持 skill-to-skill routing 时，不中断 workflow。
- 当前 agent 可以按相同角色完成阶段文件，但必须在 provenance header 中记录 `attempted_skill_call`、`skill_call_result`、`execution_mode` 和 `fallback_reason`。
- 如果 supporting skill 明明可见或已安装，却没有显式尝试调用，则该阶段应标记为 `status: completed_with_protocol_violation`，而不是普通 `completed`。
- workflow 的内容可以通过 fallback 保持完整，但 provenance 必须让调用路径透明可查。

这能保证“只输入项目书路径和 PDF 密码”后，workflow 尽量无需人工干预地跑完。

从 `0.4.6` 开始，每个 review 阶段文件必须保留统一的 provenance header；从 `0.4.7` 开始，header 还必须记录是否尝试过显式 skill 调用以及调用结果；从 `0.4.8` 开始，`peer-review` 与 `scientific-writing` 被拆成两个独立阶段文件；从 `0.4.9` 开始，skeleton 文案改为 ASCII 以避免 Windows 编码污染，并新增 review completion QC；从 `0.5.0` 开始，加入自由探索类/目标导向类属性匹配、0-5 量化评分、A/B/C 映射、上限规则和伦理合规门槛；从 `0.5.1` 开始，新增 `06_submitted_review_comment.txt`，用于生成匹配国自然评审表格的提交版评价意见；从 `0.5.2` 开始，`04`、`05`、`06` 必须保留固定标题 `KILL-MODE DECISION`，QC 会检查该段是否存在；从 `0.5.3` 开始，批量 workflow 在 pilot review 完成后必须停止等待人工确认，不能自动进入剩余项目批量评审；从 `0.5.4` 开始，评分表必须使用 `scoring-rubric.txt` 的精确维度、权重、`raw score /5`、`weighted points` 和 `Total weighted score: x/100`，不能退化为 0-5 综合均分；从 `0.5.5` 开始，批量流程只做 extraction/QC 和任务卡生成，审阅任务必须一个项目一个新窗口/session 执行；从 `0.5.6` 开始，批量结束后额外生成 `_batch/review_prompts.txt`，并在控制台打印每个任务可直接复制粘贴的短 prompt；从 `0.5.7` 开始，README 在安装部分前置提醒 supporting skills，避免用户只安装主 workflow 导致质量降级。这样下游 `nsfc-review-ranking` 可以区分完整 workflow、fallback 产物、协议违规产物、来源不明内容和未完成骨架。

批量处理时，建议先运行：

```bash
<python> scripts/batch_extract_and_qc.py --proposal-dir "<项目书文件夹>"
```

该步骤只做 PDF/TXT 提取和确定性质控，生成 `_batch/manifest.tsv`、`extraction_qc_report.txt`、`review_queue.tsv`、`review_status.tsv`、`review_task_index.tsv`、`_batch/review_prompts.txt` 和 `_batch/review_tasks/*.md`。随后请新建窗口/session，逐个复制 `_batch/review_prompts.txt` 中的 prompt 执行审阅；每个 session 只审阅一个项目，避免上下文污染和 supporting skill 调用漂移。

批处理完成后，脚本会打印类似提示：

```text
NEXT STEP: OPEN A NEW AGENT WINDOW/SESSION FOR EACH REVIEW TASK
review_prompts: D:\...\_batch\review_prompts.txt
Copy/paste prompts:

【NSFC审阅任务 1/N】
请新建一个 agent 窗口/session，然后复制粘贴以下内容执行：

使用 `nsfc-mianshang-review`，只审阅这一个项目，不要处理其他项目。
读取并执行：D:\...\_batch\review_tasks\001_A.md
完成后停止，不要继续下一个任务。

一共需要执行 N 次；每次新建一个窗口/session，只执行一个 task card。
```

评审完成后，可单独运行：

```bash
<python> scripts/review_completion_qc.py --work-root "<评审工作根目录>"
```

`batch_extract_and_qc.py` 只表示 extraction/preparation 是否可进入评审；`review_completion_qc.py` 用于检查 01-05 阶段文件是否完成、是否存在 supporting skill 未尝试调用、是否包含 Kill-mode 判定、人工审核提醒和资助建议。

---

## 输出文件结构

```text
review_dir/
  extracted/
    00_full_text.txt
    01_section_index.txt
    extraction_report.txt
  review/
    nsfc_review_cache.txt
    01_scientific_critique.txt
    02_literature_checks.txt
    03_reviewer2_stress_test.txt
    04_peer_review_draft.txt
    05_final_review.txt
    06_submitted_review_comment.txt
```

其中：

- `00_full_text.txt`：PDF/TXT 输入的主工作副本。
- `01_section_index.txt`：章节导航，用于定位标题、中文摘要、立项依据、研究内容、研究基础。
- `extraction_report.txt`：记录提取状态、页数、字符数、是否加密等。
- `nsfc_review_cache.txt`：决策相关信息底稿。
- `01_scientific_critique.txt`：科学性批判。
- `02_literature_checks.txt`：定向文献核查，尤其是 novelty 边界。
- `03_reviewer2_stress_test.txt`：严格预审，放大潜在否决点。
- `04_peer_review_draft.txt`：由 `peer-review` 生成的结构化评审草稿，必须包含 kill-mode 判定。
- `05_final_review.txt`：由 `scientific-writing` 对草稿进行中文润色后的最终评审意见。
- `06_submitted_review_comment.txt`：根据 `05_final_review.txt` 生成的提交版评价意见，匹配自由探索类/目标导向类评审表格问题，并在末尾提醒人工审核。

---

## 核心设计原则

### 1. PDF 只读一次

如果输入是 PDF，本 workflow 只在 **PDF -> TXT** 转换阶段读取 PDF。转换成功后，后续工作只基于：

- `00_full_text.txt`
- `01_section_index.txt`
- `nsfc_review_cache.txt`
- 各阶段 review 文件

这样做是为了节省 token、减少上下文漂移，并让评审过程可追踪。

### 2. TXT 是主工作副本

中间工作文件优先使用 `.txt`，而不是 Markdown。TXT 更轻、更适合长中文文本处理，也更方便全文检索、切片和缓存。

### 3. cache-first，而不是全文总结

这个 workflow 不追求“把整本申请书总结一遍”，而是先提取决策相关内容：

- 科学问题
- 中心假说
- 创新性主张
- 技术路线
- 前期基础
- 可行性
- 风险与替代方案
- major/minor concerns

### 4. 结构性缺陷优先于亮点加分

默认情况下，以下因素不能自动推高资助建议：

- 题目重要
- 平台条件不错
- 有一些前期基础
- 申请人会做相关技术

如果 proposal 仍存在多个**结构性缺陷**，最终建议应偏负面。

典型结构性缺陷包括：

- 核心 novelty 站不住
- 机制链不闭环
- 任务过多、主线发散
- 高风险假说承担过高权重
- 转化延伸冲淡基础科学问题

---

## 评审范围

默认重点审阅：

1. 标题
2. 中文摘要
3. 立项依据
4. 研究内容（包括特色与创新点、年度计划）
5. 研究基础（包括可行性分析）

可按需要参考：

- 相关在研/已结题项目
- 团队背景
- 代表论文

默认不优先处理：

- 预算细节
- 附件目录机制
- 常规表格合规项
- 推荐函、公章、声明类流程文件

这不代表这些内容“不重要”，而是它们默认不进入第一轮科学评审主链。

---

## 人工审核边界

本 workflow 会有意保留人工审核提醒，尤其是：

1. **工作条件**
   - 平台是否真能支撑关键实验
   - 是否有隐性短板

2. **个人简历 / 代表作**
   - 申请人是否真的做过对应难度的工作
   - 团队过去成果是否足以支撑当前 ambition

3. **无法可靠转成文本的图像材料**
   - 模式图 / 机制示意图
   - 技术路线图 / 流程图
   - 实验结果图
   - 显微图、凝胶图、免疫印迹、统计图、多面板结果图

如果关键证据依赖这些图像材料，`05_final_review.txt` 必须明确提醒仍需人工补查。

---

## 遇到加密 PDF 怎么办

如果 PDF 加密且没有密码，workflow 不会直接报错退出，而是进入 action-required 状态，并提示用户选择下一步输入：

- PDF 密码
- 解密后的 PDF
- 导出的 TXT
- OCR 后文本

这是设计要求，不是异常行为。

---

## 状态机

workflow 按状态推进，而不是每次从头重跑：

1. `PDF_OR_TXT_INPUT`
2. `TXT_READY`
3. `CACHE_READY`
4. `SCIENTIFIC_CRITIQUE_READY`
5. `LITERATURE_CHECKS_READY`
6. `STRESS_TEST_READY`
7. `PEER_REVIEW_DRAFT_READY`
8. `FINAL_REVIEW_READY`
9. `SUBMITTED_REVIEW_COMMENT_READY`

一旦 `TXT_READY` 存在，就不应再回去读 PDF。

---

## 两种工作模式

### 正常评审模式

适合需要较均衡的评审意见，保留优点、问题和修改建议。

### kill-mode / 内部严格预审

适合内部初筛，目标是快速判断“这本子是否值得继续投入”。在这个模式下：

- `scientific-critical-thinking` 和 `reviewer-2-simulator` 权重更高
- 结构性缺陷优先于一般亮点
- 如果存在两项以上关键结构性缺陷，默认倾向“不建议支持”或“不建议本轮资助”

---

## 最后一句

这个 skill 最核心的不是“写得像评审”，而是：

**把基金评审从一次性长文本聊天，变成一个分阶段、可审计、可追责、可复用的判断流程。**
