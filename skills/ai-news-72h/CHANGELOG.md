# Changelog

## 2026-07-01

### Changed

- 扩展并核对 AI for Science 生命与医学期刊列表，共19本期刊。
- 将完整 journal list 同步至 reference 专项验证清单。
- 修正 `Science Translational Medicine` 的期刊名称大小写。
- 强制每次 Skill 运行使用 `fork_context=false` 的 fresh subagent，避免当前会话上下文污染。
- 增加 `execution_role: isolated_worker` 无递归协议，防止 subagent 重复创建嵌套 agent。
- 当运行环境不支持 subagent 时禁止静默回退到当前会话执行。
- 要求输出写入 Markdown 文件，并在扩展名前加入实际执行模型名称。
- 增加默认文件名格式：`ai-news-72h_<YYYY-MM-DD>_<model-name>.md`。
- 要求正文开头记录实际生成模型。
- 同步更新 README 和 `agents/openai.yaml`。
- 修复 gents/openai.yaml 中中文界面元数据的 UTF-8 编码。

### Validation

- journal list 与专项验证清单一致：19/19。
- 隔离执行角色、`fork_context=false`、防递归和失败关闭规则均已检查。
- 文件名模型后缀、正文模型标识及 README 元数据均已检查。
- 工作区与本机 Codex 安装目录文件哈希一致。