# AI for Science 信源与筛选规则

执行 AI for Science 检索、筛选、撰写或验证时完整读取本文件。

## 目录

- 信源
- 纳入标准
- 时间认定
- 预印本证据要求
- 消息类型
- 研究条目字段
- 输出结构
- 专项验证

## 信源

### 早期预印本

- arXiv
- bioRxiv
- medRxiv

仅纳入首次发布版本：

- arXiv 必须核对 `v1` 首次提交时间；
- bioRxiv 和 medRxiv 必须核对首个版本发布日期；
- `v2`、`v3` 等后续更新不纳入；
- 不因网页更新时间变化而将旧论文视为新研究。

### 生命与医学重点期刊

重点检查：

- Nature
- Science
- Cell
- Nature Medicine
- Nature Biotechnology
- Nature Methods
- Nature Genetics
- Nature Communications
- Science Advances
- PNAS（Proceedings of the National Academy of Sciences）
- Cell Systems
- Patterns（Cell Press AI 期刊）
- Cancer Cell
- The New England Journal of Medicine
- NEJM AI
- The Lancet
- The Lancet Digital Health
- Nature Machine Intelligence
- Science Translational Medicine

只纳入窗口内新在线发表、且 AI 或机器学习构成核心方法或主要贡献的原创研究。使用 `Published online` 日期判断，不使用卷期日期、网页更新时间或数据库收录日期。

排除：

- News、Editorial、Comment、Perspective 和普通综述；
- 与 AI 无实质关系的生命或医学论文；
- 仅使用常规统计分析或传统生物信息学流程的研究；
- 只在摘要或讨论中提及 AI 的研究。

不使用 PubMed 作为发现或纳入来源。

### 实验室官方渠道

重点检查：

- OpenAI
- Anthropic
- Google Research
- Google DeepMind
- Microsoft Research
- Meta FAIR
- NVIDIA Research
- Broad Institute
- EMBL-EBI
- Allen Institute
- Arc Institute
- Chan Zuckerberg Initiative

仅纳入窗口内首次公开的新研究、模型、数据集、科研工具或实验系统。不纳入旧论文的新博客、重新宣传、成果回顾或仅改变网页时间的内容。

## 纳入标准

仅纳入 AI 或机器学习属于核心研究方法、主要技术贡献、主要研究对象，或对科学发现和实验流程具有实质作用的内容。重点包括：

- 生物学基础模型和生物医学多模态模型；
- 蛋白质结构预测、功能建模和生成式设计；
- AI 药物发现与分子生成；
- 基因组学、单细胞和空间组学机器学习；
- AI 医学影像与数字病理；
- 虚拟细胞和数据驱动的生物系统模拟；
- AI 辅助实验设计与自动化实验室；
- 生物医学科学 Agent；
- 临床 AI 模型和医疗多模态模型。

排除一般医疗软件、普通生命医学行业新闻，以及 AI 不是主要方法或贡献的研究。

## 时间认定

| 来源 | 纳入时间标准 |
|---|---|
| arXiv | `v1` 首次提交时间 |
| bioRxiv | 首个版本发布日期 |
| medRxiv | 首个版本发布日期 |
| 指定期刊 | `Published online` 日期 |
| 实验室官方渠道 | 新研究或科研资源首次公开时间 |

只有上述首次公开时间位于最近72小时内才可纳入。

## 预印本证据要求

窗口内首次发布的预印本可以仅依据原始论文页面纳入，无须等待媒体或第三方报道，但必须：

- 明确标注“预印本，尚未同行评议”；
- 核对首次发布版本和时间；
- 区分作者声明与本简报判断；
- 将重要性评价称为“综合评价”；
- 检查代码、数据和模型是否公开；
- 不把作者报告的基准结果视为独立验证。

## 消息类型

每项内容标注为以下类型之一：

- `新预印本（v1）`
- `新同行评议论文`
- `新科研模型或工具`
- `新数据集或基准`
- `新实验室研究项目`
- `湿实验验证研究`
- `临床验证研究`

## 研究条目字段

每项研究应说明：

- 科学问题与研究对象；
- AI 方法或系统做了什么；
- 使用了什么数据；
- 最重要的新结果；
- 证据类型：模拟、回顾性数据、湿实验、临床验证或真实部署；
- 代码、数据或模型是否开放；
- 当前局限与可复现性风险。

期刊论文还应核对期刊名称、DOI、文章类型和在线发表时间。

如果指定来源在72小时内没有符合要求的新研究，明确写“未发现符合时间窗的重大公开研究”，不要使用旧研究填充。

## 输出结构

```markdown
## AI 科学研究

### 一、早期研究

#### [论文标题]
**消息类型：** 新预印本（v1）
**首次提交时间：**
**来源：** arXiv / bioRxiv / medRxiv
**状态：** 预印本，尚未同行评议

##### 摘要
说明科学问题、AI 方法、数据和关键结果。

##### 验证情况
说明是否包含计算验证、湿实验或临床验证，以及代码、数据和模型是否开放。

##### 综合重要性评价
说明为何值得关注，并指出主要限制。

##### 来源
- [预印本原始页面](URL)
- [代码、数据或模型](URL)

### 二、生命与医学重点期刊
采用相同结构，并补充期刊名称、DOI、文章类型和 `Published online` 时间。

### 三、实验室官方科研动态
仅报道首次公开的新研究、科研模型、数据集、工具或实验系统。

### 四、本期 AI for Science 总结
概括最近72小时的主要研究方向和最值得持续关注的成果。
```

## 专项验证

### 时间

- [ ] 已检索 arXiv、bioRxiv 和 medRxiv。
- [ ] arXiv 预印本已核对 `v1` 首次提交时间。
- [ ] bioRxiv 和 medRxiv 已核对首个版本发布日期。
- [ ] 没有纳入 `v2`、`v3` 等版本更新。
- [ ] 重点期刊论文按 `Published online` 日期判断。

### 来源与状态

- [ ] 已检查 Nature、Science、Cell、Nature Medicine、Nature Biotechnology、Nature Methods、Nature Genetics、Nature Communications、Science Advances、PNAS、Cell Systems、Patterns、Cancer Cell、The New England Journal of Medicine、NEJM AI、The Lancet、The Lancet Digital Health、Nature Machine Intelligence 和 Science Translational Medicine。
- [ ] 已分别检查 OpenAI、Anthropic、Google Research/DeepMind 及其他指定实验室。
- [ ] 没有使用 PubMed 作为发现或纳入来源。
- [ ] 预印本已标注未经同行评议。
- [ ] 已检查代码、数据、模型和实验验证情况。
- [ ] 期刊论文已核对 DOI、文章类型和在线发表时间。

### 内容

- [ ] 已排除 News、Editorial、Comment、Perspective 和普通综述。
- [ ] AI 或机器学习确实是研究的核心方法或主要贡献。
- [ ] 已排除仅使用常规统计分析或传统生物信息学流程的研究。
- [ ] 实验室动态确实对应首次公开的新研究或新资源。
- [ ] 没有纳入旧论文的新官方公告。
- [ ] 作者声明与本简报综合评价已经区分。
