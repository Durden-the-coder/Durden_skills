# 更新日志

本文档记录 `nsfc-mianshang-review` 的重要变更。
版本号采用轻量语义化规则：
- `MAJOR`：不兼容的 workflow 或决策模型变化
- `MINOR`：新增能力或明显的流程扩展
- `PATCH`：bug 修复、文案修正、边界补充、小型路由修正

## 0.4.2 - 2026-05-01

- `extract_nsfc_text.py` 增加 `--init-review-files` 可选参数。
- 提取成功后，可预先生成 review 阶段骨架文件，帮助 Claude Code 等环境在外部目录中继续 workflow。
- 该增强不改变既有 Codex workflow，只是让“脚本先落骨架、agent 再补内容”的模式更容易复现。

## 0.4.1 - 2026-05-01

- 明确：当输入为 PDF 时，workflow 默认先自动执行本地 PDF 转 TXT。
- 增加人工介入条件说明：PDF 加密、扫描版无 OCR、提取损坏、无法创建安全工作目录。
- 强化工作环境边界：所有脚本执行和产物默认限制在 review 工作目录中，不写入系统盘缓存或全局 agent 目录。
- README 中补充安装和使用方法。

## 0.4.0 - 2026-05-01

- 在 `SKILL.md` 中加入显式版本号元数据。
- 新增可分享的 `README.md`。
- 强化 NSFC 2026 固定结构的 section 路由。
- 修复 `section_index` 的识别逻辑。
- 强化 novelty 判断逻辑。
- 增加更严格的内部 triage / kill-mode 判定规则。
- 增加人工审核提醒边界和非文本图像证据边界。

## 0.3.0 - 2026-05-01

- 创建初版 NSFC General Program workflow skill。
- 增加 PDF/TXT 提取流程。
- 增加 review cache、scientific critique、literature checks、reviewer-2 stress test 和 final review 的文件约定。
- 增加默认 proposal 上一级 review 工作目录推断逻辑。
