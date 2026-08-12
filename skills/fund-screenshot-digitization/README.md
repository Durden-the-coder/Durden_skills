# Fund Screenshot Digitization

一个以 `SKILL.md` 为核心规范、优先保证 Codex 完整调用，同时兼容其他 Agent 的基金交易截图数字化 skill。它将截图逐页转录为 Excel，并汇总为单标签页统计输入文件。

## Codex 支持（首要兼容目标）

仓库保留了 Codex 所需的宿主适配文件 `agents/openai.yaml`，不要在安装或迁移时删除、重命名或跳过它。

将整个目录复制到 Codex skill 目录：

```text
%USERPROFILE%\\.codex\\skills\\fund-screenshot-digitization
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

## 其他 Agent 兼容方式

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

## 适用场景

- 基金网站不支持交易记录导出，只能从截图恢复数据；
- 需要按页精细识别日期、时间、产品、基金代码、交易类型、申请/确认数值、单位、账户和状态；
- 需要将多个逐页 Excel 合并成可供其他项目统计的单表文件；
- 需要对页码覆盖、行号唯一性、基金代码格式、公式和短页进行自动检查。

## 工作方式

1. 按文件名排序建立页码与原图的映射；
2. 每页独立识别，不让多个 Agent 同时写同一个工作簿；
3. 使用第 13 页模板生成页面级 Excel，并保留 `交易记录`、`数字字段` 两个工作表；
4. 对特殊状态、`--`、空白字段、异常单位和短页原样保留；
5. 通过合并脚本生成一个 `交易明细` 标签页；
6. 运行校验脚本检查缺页、重复页内序号、基金代码、公式和记录数。

## 目录

```text
SKILL.md
agents/openai.yaml
scripts/merge_workbooks.py
scripts/validate_workbooks.py
references/data-contract.md
```

## 免责声明

本 Skill 只提供截图转录和表格整理能力，不提供投资建议、基金推荐、收益预测或交易决策。截图识别可能存在遗漏或误读，所有数字和状态都应由使用者依据原图复核。使用者应自行负责数据保密、合规和由数据使用产生的后果。本项目不隶属于天天基金、任何基金管理人或金融监管机构。

## 许可证

本 Skill 采用 [MIT License](../../LICENSE)。仓库级免责条款见 [DISCLAIMER.md](../../DISCLAIMER.md)。
