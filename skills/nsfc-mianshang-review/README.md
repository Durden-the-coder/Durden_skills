# nsfc-mianshang-review

**当前版本：** `0.4.3`

`nsfc-mianshang-review` 是一个面向 **国家自然科学基金面上项目（2026 版）** 的评审 workflow skill。它不是单纯的“写评语提示词”，而是一套分阶段、低 token、可复用、可审计的评审流程。

本 skill 是非官方、实验性的项目书内部预审辅助工具，不隶属于国家自然科学基金委员会，也不提供正式资助判断。所有输出都可能存在遗漏或错误，必须由人类专家复核。使用真实项目书时，请注意保密和合规，不要把未公开申请书、附件、图件、个人信息或 PDF 密码提交到公开 issue、PR、讨论区或不可信环境中。

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

### 2. 最小输入

一次完整 workflow 理想情况下只需要：

- 项目书 PDF 或 TXT 路径
- PDF 密码（仅加密 PDF 需要）

示例：

```text
使用 nsfc-mianshang-review 的 kill-mode 评审：
D:\AI projects\claude_code\2026国自然评审\项目书\proposal.pdf
PDF 密码：your-password
```

workflow 会优先执行本地 PDF/TXT 提取，并自动创建 review 工作目录。

### 3. 默认输出目录

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

### 4. 脚本运行方式

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

因此从 `0.4.3` 开始，本 workflow 的规则是：

- 能显式调用 supporting skill 时，优先调用。
- supporting skill 未安装、无法加载或运行时不支持 skill-to-skill routing 时，不中断 workflow。
- 当前 agent 必须按相同角色完成阶段文件，并在对应文件中简短记录 fallback。
- workflow 的成功标准是阶段文件完整、内容符合角色，而不是 UI 显示调用了多少个 skill。

这能保证“只输入项目书路径和 PDF 密码”后，workflow 尽量无需人工干预地跑完。

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
    04_final_review.txt
```

其中：

- `00_full_text.txt`：PDF/TXT 输入的主工作副本。
- `01_section_index.txt`：章节导航，用于定位标题、中文摘要、立项依据、研究内容、研究基础。
- `extraction_report.txt`：记录提取状态、页数、字符数、是否加密等。
- `nsfc_review_cache.txt`：决策相关信息底稿。
- `01_scientific_critique.txt`：科学性批判。
- `02_literature_checks.txt`：定向文献核查，尤其是 novelty 边界。
- `03_reviewer2_stress_test.txt`：严格预审，放大潜在否决点。
- `04_final_review.txt`：最终中文评审意见。

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

这个 workflow 不追求“把整本申请书总结一遍”，而是先提取决策相关内容：科学问题、中心假说、创新性主张、技术路线、前期基础、可行性、风险与替代方案、major/minor concerns。

### 4. 结构性缺陷优先于亮点加分

默认情况下，题目重要、平台条件不错、有一些前期基础、申请人会做相关技术，都不能自动推高资助建议。如果 proposal 仍存在多个**结构性缺陷**，最终建议应偏负面。

典型结构性缺陷包括：核心 novelty 站不住、机制链不闭环、任务过多且主线发散、高风险假说承担过高权重、转化延伸冲淡基础科学问题。

---

## 评审范围

默认重点审阅：标题、中文摘要、立项依据、研究内容（包括特色与创新点、年度计划）、研究基础（包括可行性分析）。

可按需要参考相关在研/已结题项目、团队背景和代表论文。

默认不优先处理预算细节、附件目录机制、常规表格合规项、推荐函、公章、声明类流程文件。这不代表这些内容“不重要”，而是它们默认不进入第一轮科学评审主链。

---

## 人工审核边界

本 workflow 会有意保留人工审核提醒，尤其是：

1. **工作条件**：平台是否真能支撑关键实验，是否有隐性短板。
2. **个人简历 / 代表作**：申请人是否真的做过对应难度的工作，团队过去成果是否足以支撑当前 ambition。
3. **无法可靠转成文本的图像材料**：模式图、机制示意图、技术路线图、流程图、实验结果图、显微图、凝胶图、免疫印迹、统计图、多面板结果图。

如果关键证据依赖这些图像材料，`04_final_review.txt` 必须明确提醒仍需人工补查。

---

## 遇到加密 PDF 怎么办

如果 PDF 加密且没有密码，workflow 不会直接报错退出，而是进入 action-required 状态，并提示用户选择下一步输入：PDF 密码、解密后的 PDF、导出的 TXT 或 OCR 后文本。

---

## 状态机

workflow 按状态推进，而不是每次从头重跑：

1. `PDF_OR_TXT_INPUT`
2. `TXT_READY`
3. `CACHE_READY`
4. `SCIENTIFIC_CRITIQUE_READY`
5. `LITERATURE_CHECKS_READY`
6. `STRESS_TEST_READY`
7. `FINAL_REVIEW_READY`

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
