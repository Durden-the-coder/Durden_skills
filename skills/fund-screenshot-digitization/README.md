# Fund Screenshot Digitization

一个用于将基金交易截图逐页数字化为 Excel，并汇总为单标签页统计输入文件的 Codex Skill。

## 适用场景

- 基金网站不支持交易记录导出，只能从截图恢复数据；
- 需要按页精细识别日期、时间、产品、基金代码、交易类型、申请/确认数值、单位、账户和状态；
- 需要将多个逐页 Excel 合并成可供其他项目统计的单表文件；
- 需要对页码覆盖、行号唯一性、基金代码格式、公式和短页进行自动检查。

## 安装

将整个目录复制到 Codex skill 目录：

```text
%USERPROFILE%\.codex\skills\fund-screenshot-digitization
```

新建 Codex 任务后调用：

```text
$fund-screenshot-digitization
```

## 使用示例

```text
使用 $fund-screenshot-digitization，逐页识别这些基金交易截图，生成单页复核表，并合并成一个单标签页统计输入文件。
```

## 工作方式

1. 按文件名排序建立页码与原图的映射；
2. 每页独立识别，不让多个 agent 同时写同一个工作簿；
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
