# Durden_skills

Peer-review skills and review workflows for NSFC grant applications.

本仓库用于存放面向科研评审和项目书预审的 reusable skills / workflow。当前重点是国自然面上项目评审 workflow，后续可能继续追加其他类型的科研评审或写作辅助 skill。

## 声明

本项目是一个非官方、实验性的 AI workflow skill，用于学习交流、内部预审和工作流探索。

- 本项目不隶属于国家自然科学基金委员会，也不代表任何官方评审意见。
- 输出内容不能替代专家判断，使用者应自行进行人工复核。
- 请勿把真实、敏感、涉密或未经授权的项目书材料提交到公开 issue、PR 或不可信环境中。
- 本项目以 MIT License 开源，欢迎学习、交流、fork 和改进。

## Skills

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

## 质量与边界

当前 skill 经过人工核查，验证了输出结果具备较高质量，可以作为快速审阅本子的底稿，节约时间并帮助减少关键细节遗漏。不过它仍然不是正式评审系统，也不保证判断完全准确。

本人没有系统学习过编程，主要依靠 AI 辅助制作工具，肯定存在疏漏和不足，工具也会不定期迭代。欢迎交流、提建议和提交改进。

## 配套文件

- `LICENSE`: MIT 开源许可证
- `DISCLAIMER.md`: 免责声明
- `SECURITY.md`: 安全与敏感材料处理说明

This repository is intended to hold reusable skill bundles rather than full applications.
