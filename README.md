# Durden_skills

个人 Agent Skill 仓库。

这里收录我在实际工作中整理、验证和持续迭代的可复用 Skill。每个 Skill 都以自身目录中的 `SKILL.md` 为核心执行规范，并根据需要附带脚本、参考资料、测试样例和宿主适配配置。

仓库中的 Skill 按“首次进入本仓库的 GitHub 提交时间”排序。时间使用 GitHub 提交记录中的 UTC 时间；后续更新不会改变其首次发布日期。

## Skills

### 1. `nsfc-mianshang-review`

首次进入仓库：2026-05-02

国家自然科学基金面上项目评审工作流。用于将申请书转换为可检索文本，采用缓存优先、分阶段的方式完成科学性评议、创新性检查、可行性分析、内部快速筛查和中文评审意见生成。

- [Skill 目录](https://github.com/Durden-the-coder/Durden_skills/tree/main/skills/nsfc-mianshang-review)
- [核心规范](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/nsfc-mianshang-review/SKILL.md)
- 适合：面上项目申请书预审、内部评议、结构化审阅和评审意见整理。

### 2. `nsfc-review-ranking`

首次进入仓库：2026-05-08

对多个已经生成的 NSFC 面上项目评审结果进行横向比较、量化评分、A/B/C 分档、来源审计和排序总结。不重新阅读原始申请书 PDF，重点使用已有的评审 TXT 结果。

- [Skill 目录](https://github.com/Durden-the-coder/Durden_skills/tree/main/skills/nsfc-review-ranking)
- [核心规范](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/nsfc-review-ranking/SKILL.md)
- 适合：批量评审结果排序、项目遴选、分层比较和汇总报告。

### 3. `ai-news-72h`

首次进入仓库：2026-06-15

检索、核验并撰写最近 72 小时的全球 AI 新闻简报，覆盖基础模型、Agent、硬件、软件、应用、公司动态、AI for Science，以及部分生命医学 AI 研究和实验室官方信息。

- [Skill 目录](https://github.com/Durden-the-coder/Durden_skills/tree/main/skills/ai-news-72h)
- [核心规范](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/ai-news-72h/SKILL.md)
- 适合：每日 AI 简报、行业动态、公司与模型进展、AI 科研新闻追踪。

### 4. `ai-biomedical-journal-watch`

首次进入仓库：2026-07-30

追踪 18 本重点期刊中的生物医学 AI 研究和趋势内容。支持时间窗口设置、候选发现、证据补全、语义筛选、期刊优先级排序、结果审计和中文报告生成。

- [Skill 目录](https://github.com/Durden-the-coder/Durden_skills/tree/main/skills/ai-biomedical-journal-watch)
- [核心规范](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/ai-biomedical-journal-watch/SKILL.md)
- 适合：生物医学 AI 期刊监测、研究筛选、趋势追踪和可审计简报。

### 5. `fund-screenshot-digitization`

首次进入仓库：2026-08-12

将无法导出的基金交易截图逐页转录为高精度 Excel，并合并为一个供统计项目使用的单标签页输入文件。重点处理数字识别、页码对应、短页、异常字段、并行逐页识别和最终复核。

- [Skill 目录](https://github.com/Durden-the-coder/Durden_skills/tree/main/skills/fund-screenshot-digitization)
- [核心规范](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/fund-screenshot-digitization/SKILL.md)
- [Skill README](https://github.com/Durden-the-coder/Durden_skills/blob/main/skills/fund-screenshot-digitization/README.md)
- 适合：基金网站无导出功能时，从截图恢复交易记录并生成统计输入数据。

## 使用方式

### Codex

将所需 Skill 的整个目录复制到：

```text
%USERPROFILE%\.codex\skills\<skill-name>
```

重新打开任务后，按宿主支持的 Skill 名称调用。以基金交易截图 Skill 为例：

```text
$fund-screenshot-digitization
```

该 Skill 的 `agents/openai.yaml` 提供 Codex 宿主适配配置；`SKILL.md` 仍然是实际执行规范。

### 其他 Agent

将 Skill 目录放入目标 Agent 的 skills、instructions 或规则目录，并确保 Agent 读取其中的 `SKILL.md`。如果宿主不支持自动发现，直接在任务中提供 `SKILL.md` 的路径或内容即可。

Skill 目录中的脚本和 references 是可选的配套资源，应按照各自 `SKILL.md` 的要求使用。不同宿主的调用语法可以不同，但不应改变 `SKILL.md` 规定的工作流、输入要求、质量检查和输出约束。

## 目录结构

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
- `README.md`：安装和使用说明；
- `agents/openai.yaml`：可选的 Codex 宿主适配配置；
- `scripts/`：可执行辅助脚本；
- `references/`：数据契约、来源策略或其他参考资料；
- `tests/`：回归测试或示例输入。

## 仓库边界

- 这些 Skill 是个人工作流工具和实验性 AI 辅助工具，不代表任何官方机构或专业意见。
- 输出结果应结合原始材料进行人工复核，不能替代专家判断。
- 请勿把真实、敏感、涉密或未经授权的材料提交到公开 issue、PR 或其他不可信环境。
- 基金交易截图 Skill 不提供投资建议、基金推荐、收益预测或交易决策。

## 许可证与声明

- [MIT License](https://github.com/Durden-the-coder/Durden_skills/blob/main/LICENSE)
- [DISCLAIMER.md](https://github.com/Durden-the-coder/Durden_skills/blob/main/DISCLAIMER.md)
- [SECURITY.md](https://github.com/Durden-the-coder/Durden_skills/blob/main/SECURITY.md)

新增 Skill 时，请在本 README 中按其首次进入仓库的时间追加到正确位置，并同时补充 Skill 目录、核心规范和适用场景链接。
