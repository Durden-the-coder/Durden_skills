# 更新日志

本文档记录 `nsfc-mianshang-review` 的重要变更。
版本号采用轻量语义化规则：
- `MAJOR`：不兼容的 workflow 或决策模型变化
- `MINOR`：新增能力或明显的流程扩展
- `PATCH`：bug 修复、文案修正、边界补充、小型路由修正

## 0.5.7 - 2026-05-07

- README 安装部分前置提醒：正式评审建议同时安装 `scientific-critical-thinking`、`literature-review`、`reviewer-2-simulator`、`peer-review` 和 `scientific-writing`。
- 明确说明 fallback 能保证 workflow 不中断，但 supporting skills 显式调用通常能提升文献核查、严苛反驳和中文润色质量。
- 补充每个 review 阶段对应的 supporting skill 关系，以及权限确认和 provenance 记录要求。

## 0.5.6 - 2026-05-07

- 批处理结束后新增 `_batch/review_prompts.txt`，把每个 READY 项目的新窗口/session 短 prompt 全部写入一个文件。
- 控制台不再只显示第一个 task card，而是逐条打印所有可复制粘贴的审阅 prompt，减少手动打开任务卡查找路径的操作。
- 修复 `batch_extract_and_qc.py` 生成任务卡时的中文提示乱码。

## 0.5.5 - 2026-05-07

- 将批量 workflow 收束为 deterministic preparation：批量阶段只做 PDF/TXT 提取、QC、目录初始化和任务卡生成，不再建议在同一 session 内批量审阅多个项目。
- `batch_extract_and_qc.py` 新增 `_batch/review_tasks/*.md` 和 `_batch/review_task_index.tsv`，每个 READY 项目生成一个可复制到新窗口/session 的审阅任务卡。
- 批处理结束后在控制台强提醒用户新建窗口/session，并给出首个 task card 路径和总任务数。

## 0.5.4 - 2026-05-07

- 基于 `0.5.3` 修复评分输出容易退化为通用 0-5 综合均分的问题。
- `04_peer_review_draft.txt` 和 `05_final_review.txt` 必须使用 `scoring-rubric.txt` 中对应研究属性的精确维度和权重。
- 评分输出必须包含 `raw score /5`、`weighted points`、`Total weighted score: x/100`、cap rules 和最终 A/B/C，不得合并、拆分、重命名或替换 rubric 维度。
- `review_completion_qc.py` 增加对 `/100` 加权总分和评分表关键字段的检查。

## 0.5.3 - 2026-05-07

- 修复批量 workflow 的人工确认边界：单项目可自动跑完，但批量任务在 pilot review 完成后必须停止。
- 明确规定：初始批量请求、pilot 前的 `go`、提取 QC 通过或 pilot 成功，均不能被解释为授权剩余项目批量评审。
- 新增 `WAITING_FOR_HUMAN_APPROVAL` 状态，用于标记 pilot 后等待人工确认的批量队列。

## 0.5.2 - 2026-05-07

- 将 kill-mode 输出从宽松语义要求收束为固定标题 `KILL-MODE DECISION`。
- 要求 `04_peer_review_draft.txt`、`05_final_review.txt` 和 `06_submitted_review_comment.txt` 均保留该段，避免最终润色或表格化评价意见阶段丢失严格判定。
- 更新 review completion QC：若 `05_final_review.txt` 或 `06_submitted_review_comment.txt` 缺少 `KILL-MODE DECISION`，则标记为 `NEEDS_ATTENTION`。

## 0.5.1 - 2026-05-07

- 新增 `06_submitted_review_comment.txt`，作为基于 `05_final_review.txt` 的提交版评价意见文件。
- `06_submitted_review_comment.txt` 按自由探索类/目标导向类评审表格组织内容，包括综合评价、资助意见、科学评价说明和三条具体评价意见。
- 文件末尾强制保留人工审核提醒，覆盖非文本图件、技术路线图、机制模式图、实验图像、代表作、简历、伦理/生物安全/合规附件等。
- `extract_nsfc_text.py --init-review-files`、`batch_extract_and_qc.py`、`review_completion_qc.py`、`README.md` 与 `output-templates.txt` 已同步新的 06 阶段。

## 0.5.0 - 2026-05-07

- 新增自由探索类/目标导向类研究属性匹配规则，包括证据链判断和 `none` / `mild` / `moderate` / `severe` 错配等级。
- 重写 `references/scoring-rubric.txt`，加入 0-5 单项打分、两类项目差异化权重、伦理合规门槛、上限规则和 A/B/C 映射。
- `04_peer_review_draft.txt` 和 `05_final_review.txt` 必须包含研究属性匹配、评分摘要、上限规则、伦理合规门槛和 Kill-mode 判定。
- `review_completion_qc.py` 增加对研究属性判断、评分摘要和 cap-rule 检查的提示。
- `references/output-templates.txt` 同步更新为 ASCII 模板，避免中文模板在部分 Windows/agent 环境中乱码。

## 0.4.9 - 2026-05-07

- 在 `SKILL.md` 顶部新增 `Execution Fast Path`，让 agent 先看到完整 01-05 执行主线；保留原有详细规则，不改变默认输出内容。
- 将 `extract_nsfc_text.py --init-review-files` 生成的 01-05 skeleton 提示统一改为 ASCII 英文，避免 Windows 控制台或文件编码导致中文提示乱码。
- 收束 `skill_call_result` 为封闭枚举：`success`、`not_installed`、`permission_blocked`、`runtime_not_supported`、`call_failed`、`not_attempted`。
- 新增 `scripts/review_completion_qc.py`，把 extraction/preparation QC 与 review completion QC 分开。
- 同步更新 `references/output-templates.txt`，适配 01-05 阶段结构。
- 暂不改变自由探索类/目标导向类研究属性判断和 scoring 机制；这些内容需要先进一步论证。

## 0.4.8 - 2026-05-07

- 将 final review 拆成两个独立阶段文件：`04_peer_review_draft.txt` 与 `05_final_review.txt`。
- `04_peer_review_draft.txt` 专门由 `peer-review` 生成结构化评审草稿，并默认包含 Kill-mode 判定。
- `05_final_review.txt` 专门由 `scientific-writing` 润色最终中文评审，避免 agent 将写作润色“顺手合并”到 peer-review 阶段而跳过显式调用。
- `scientific-writing` 被明确限制为改善表达、结构和中文质量，不得改变证据判断、资助建议或 Kill-mode 结论。
- `extract_nsfc_text.py --init-review-files` 与批量 QC 已同步新的五阶段 review 文件结构。

## 0.4.7 - 2026-05-06

- `allowed-tools` 增加 `Skill`，使支持该字段的 agent 更容易执行显式 supporting skill 调用。
- 收紧 supporting skill routing：每个阶段写入前必须先尝试显式调用对应 supporting skill；fallback 只能用于未安装、不可加载、权限阻断、运行时不支持或调用失败。
- provenance header 新增 `attempted_skill_call` / `attempted_skill_calls` 和 `skill_call_result` / `skill_call_results` 字段。
- 新增 `status: completed_with_protocol_violation`，用于标记 supporting skill 可见或已安装但未显式尝试调用的产物。
- `extract_nsfc_text.py --init-review-files` 生成的 review 骨架已同步到 0.4.7 provenance 格式。
- 批量 QC 增加 protocol violation 与新 provenance 字段检查。

## 0.4.6 - 2026-05-06

- 新增强制 provenance header 规范，要求每个阶段文件声明 workflow skill、版本、stage、supporting skill、execution mode、status、input/output 文件和 fallback reason。
- `04_final_review.txt` 新增 final provenance header，必须声明 `synthesized_from` 的 stage 文件清单。
- 明确 `explicit_skill_call` 只能在运行时确实显式调用 supporting skill 时使用；若由当前 agent 代替完成，必须标记为 `fallback_agent_role`。
- `extract_nsfc_text.py --init-review-files` 生成的 review 阶段骨架文件现在预置 provenance header 模板。
- 下游 `nsfc-review-ranking` 可据此更可靠地区分完整 workflow、fallback 产物、来源不明产物和未完成骨架。
- 新增 `scripts/batch_extract_and_qc.py`，支持批量 PDF/TXT 提取、确定性质控、manifest、review queue 和 review status 文件生成。
- 新增批量工作流：先批量 extraction/QC，再单本 pilot review，人工审核通过后进入批量 review。
- 修复 PDF 抽取将 `中文摘要` 拆成纵向单字换行时，`01_section_index.txt` 误匹配后文项目摘要的问题。
- 批量 QC 新增章节顺序检查，若 `中文摘要` 出现在 `立项依据` 之后会标记为异常。

## 0.4.5 - 2026-05-05

- 修复 `01_section_index.txt` 偶发缺少 `（三）研究基础` 的问题。
- 将正文主章节定位从“全文关键词扫描”改为“按章节顺序定位”：
  - 先定位 `（一）立项依据`
  - 再从其后定位 `（二）研究内容`
  - 再从其后定位 `（三）研究基础`
- 支持章节标题中出现空格、全角空格或换行拆分，降低 PDF 文本提取格式差异对章节索引的影响。
- 避免目录、摘要、填报说明或前文中的普通“研究基础”字样误导正文章节定位。

## 0.4.4 - 2026-05-05

- 规范化 `SKILL.md` frontmatter，补充 `allowed-tools: Read Write Edit Bash WebSearch`，减少 Claude Code 在 skill 内执行读写、脚本和检索时的重复 permission/action 提示。
- 补充 `license: MIT license` 与 `metadata.skill-author`，使 skill 更接近常见学术 skills 的发布格式。
- 精简 description，使 agent 更容易判断触发场景。
- 新增 `When to Use This Skill` 和 `When Not to Use This Skill`，降低误触发和误用概率。
- 新增 `Non-Interactive Execution Policy`，明确正常阶段边界不应反复等待用户输入 `go`。

## 0.4.3 - 2026-05-04

- 将 workflow 明确升级为“优先显式调用 supporting skills，失败时角色 fallback”的 harness：
  - 优先调用 `scientific-critical-thinking`
  - 优先调用 `literature-review`
  - 优先调用 `reviewer-2-simulator`
  - 优先调用 `peer-review`
  - 优先调用 `scientific-writing`
- 明确：如果运行时不支持 skill-to-skill routing，或 supporting skill 未安装，不应中断 workflow；当前 agent 必须按相同角色完成阶段文件。
- 将默认输出目录前缀从 `nsfc_review_` 改为 `nsfc-review-`。
- 默认输出目录仍位于项目书文件夹的上一级，以保持原始项目书文件夹整洁。
- 强化“一步输入”规则：用户原则上只需提供项目书路径和 PDF 密码，workflow 应自动完成提取、建目录、建骨架和后续评审阶段。
- `extract_nsfc_text.py` 的 review 阶段骨架文件增加 supporting skill routing / fallback 提醒。
- 恢复并重写中文 README，修复此前乱码问题，并补充安装、调用、输出目录、fallback 机制和人工审核边界说明。

## 0.4.2 - 2026-05-01

- `extract_nsfc_text.py` 增加 `--init-review-files` 可选参数。
- 当提取成功时，可预先生成以下 review 阶段骨架文件，帮助 Claude Code 等环境在外部目录中继续 workflow：
  - `01_scientific_critique.txt`
  - `02_literature_checks.txt`
  - `03_reviewer2_stress_test.txt`
  - `04_final_review.txt`
- 该增强不改变既有 Codex workflow，只是让“脚本先落骨架、agent 再补内容”的模式更容易复现。
- `SKILL.md` 补充说明：在文件写入不稳定的环境中，可在提取命令后追加 `--init-review-files`。

## 0.4.1 - 2026-05-01

- 明确：当输入为 PDF 时，workflow 默认先自动执行本地 PDF 转 TXT，不应要求用户手动逐步准备，除非提取被阻塞。
- 增加 PDF 准备阶段需要人工介入的条件说明：
  - PDF 加密且没有可用密码
  - PDF 为扫描版且没有可用 OCR 文本
  - 提取结果过于残缺或损坏，无法支持后续评审
  - 无法创建安全的本地 review 工作目录
- 强化工作环境边界：
  - 所有脚本执行必须限制在用户指定的 review 工作目录，或 proposal 上一级自动创建的 review 目录中
  - 默认不向系统盘缓存、全局 skill 目录、agent home、用户 profile cache 等位置写入 workflow 产物
- README 中补充安装和使用方法，包括：
  - 安装方式
  - 输入准备
  - PDF/TXT workflow 运行方式
  - kill-mode 调用示例
  - 输出文件结构
  - 使用边界说明

## 0.4.0 - 2026-05-01

- 在 `SKILL.md` 中加入显式版本号元数据。
- 新增可分享的 `README.md`，说明 workflow 的设计原则、文件流、状态机和决策哲学。
- 强化 NSFC 2026 固定结构的 section 路由：
  - 标题
  - 中文摘要
  - 立项依据
  - 研究内容
  - 研究基础
- 修复 `section_index` 的识别逻辑，使其优先匹配 NSFC 编号章节标题，而不是普通关键词首次出现位置。
- 强化 novelty 判断逻辑：
  - 区分“新靶点/新对象”“新机制”“新转化方向”
  - 避免在已有公开证据存在时过度拔高创新性
- 增加更严格的内部 triage / kill-mode 判定规则：
  - 结构性缺陷优先于一般亮点
  - 若存在两项及以上未被化解的结构性缺陷，默认给出负向资助建议
  - `scientific-critical-thinking` 与 `reviewer-2-simulator` 主导 fundability 判断
- 增加 `FATAL FLAWS OR DECISION-LEVEL DEFECTS` 这一类 kill-mode 输出要求。
- 补充人工审核提醒边界：
  - 工作条件
  - 简历 / 代表作
  - 项目重叠 / 延续性
  - 附件一致性
- 增加“非文本图像证据”的人工审核边界：
  - 机制模式图
  - 技术路线图 / 流程图
  - 实验结果图
  - 显微图、凝胶图、免疫印迹、统计图及其他多面板图像证据
- 明确 PDF 只在 PDF-to-TXT 提取阶段读取，提取完成后不再回读 PDF。

## 0.3.0 - 2026-05-01

- 创建初版 NSFC General Program workflow skill。
- 增加 PDF/TXT 提取流程。
- 增加 review cache、scientific critique、literature checks、reviewer-2 stress test 和 final review 的文件约定。
- 增加默认 proposal 上一级 review 工作目录推断逻辑。
