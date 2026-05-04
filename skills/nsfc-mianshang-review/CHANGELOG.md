# 更新日志

本文档记录 `nsfc-mianshang-review` 的重要变更。
版本号采用轻量语义化规则：
- `MAJOR`：不兼容的 workflow 或决策模型变化
- `MINOR`：新增能力或明显的流程扩展
- `PATCH`：bug 修复、文案修正、边界补充、小型路由修正

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
