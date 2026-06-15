# ai-news-72h

用于检索、核验并撰写最近 72 小时全球 AI 新闻和 AI for Science 研究动态的 Codex Skill。

除基础模型、Agent、硬件、软件和应用新闻外，本 Skill 重点捕捉刚发布的科研消息，包括早期预印本、生命医学重点期刊论文，以及主要实验室首次公开的新研究或科研资源。

## 主要能力

- 按用户时区计算精确的最近 72 小时时间窗
- 区分事件发生时间、首次公开时间和媒体发布时间
- 检索模型、Agent、硬件、软件、应用和产业新闻
- 监测 arXiv、bioRxiv 和 medRxiv 的首次发布预印本
- 核对 arXiv `v1` 时间，排除 `v2`、`v3` 等后续更新
- 监测指定生命与医学重点期刊的新在线原创研究
- 监测主要实验室首次公开的新研究、模型、数据集和科研工具
- 提供摘要、验证情况、重要性评价、局限和原始来源
- 执行时间、事实、来源、研究类型和链接检查

## AI for Science 信源

### 早期预印本

- arXiv
- bioRxiv
- medRxiv

只纳入最近 72 小时内首次发布的版本：

- arXiv 使用 `v1` 首次提交时间；
- bioRxiv 和 medRxiv 使用首个版本发布日期；
- 不纳入 `v2`、`v3` 等版本更新；
- 不因网页更新时间改变而将旧论文视为新研究。

### 生命与医学重点期刊

- Nature
- Science
- Cell
- Nature Medicine
- Nature Biotechnology
- Nature Methods
- Nature Genetics
- Cancer Cell

只纳入 AI 或机器学习构成核心方法或主要贡献的原创研究，并使用 `Published online` 日期判断时间窗。

不使用 PubMed 作为发现或纳入来源。

### 实验室官方渠道

重点包括：

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

只纳入首次公开的新研究、模型、数据集、科研工具或实验系统。不纳入旧论文的新博客、重新宣传或成果回顾。

## AI for Science 纳入范围

AI 或机器学习必须是核心方法、主要技术贡献、主要研究对象，或对科学发现和实验流程具有实质作用。重点包括：

- 生物学基础模型和生物医学多模态模型
- 蛋白质结构预测、功能建模和生成式设计
- AI 药物发现与分子生成
- 基因组学、单细胞和空间组学机器学习
- AI 医学影像与数字病理
- 虚拟细胞和数据驱动的生物系统模拟
- AI 辅助实验设计与自动化实验室
- 生物医学科学 Agent
- 临床 AI 模型和医疗多模态模型

排除：

- 仅使用常规统计分析的研究
- 仅使用传统生物信息学流程的研究
- 只在摘要或讨论中提及 AI 的论文
- AI 不是主要方法或贡献的普通生命医学论文
- 一般医疗软件或普通行业新闻
- News、Editorial、Comment、Perspective 和普通综述

## 预印本处理

刚发布的预印本可以仅依据原始论文页面纳入，无须等待媒体报道，但必须：

- 标注“预印本，尚未同行评议”；
- 核对首次版本和发布时间；
- 区分作者声明与本简报判断；
- 使用“综合评价”，不声称存在第三方共识；
- 检查代码、数据和模型是否开放；
- 不把作者报告的基准结果视为独立验证。

## 输出内容

默认包括：

1. 精确统计窗口与检索截止时间
2. Introduction
3. 模型、Agent、硬件、软件和应用新闻
4. AI for Science 早期研究
5. 生命与医学重点期刊论文
6. 实验室官方科研动态
7. 科学问题、AI 方法、数据和关键结果
8. 计算、湿实验或临床验证情况
9. 代码、数据和模型开放情况
10. 综合重要性评价与主要局限
11. 原始来源链接
12. 全文总结与方法局限

## 使用示例

```text
搜索最近 72 小时 AI 领域的新闻，并单列 AI for Science。
检查 arXiv、bioRxiv、medRxiv、生命医学重点期刊和主要实验室官方渠道。
预印本只纳入首次发布版本，arXiv 必须核对 v1 时间。
```

## 安装

将本目录放入 Codex Skills 目录：

```text
~/.codex/skills/ai-news-72h
```

## 文件结构

```text
ai-news-72h/
├── SKILL.md
├── README.md
├── references/
│   └── ai-for-science-sources.md
└── agents/
    └── openai.yaml
```

- [`SKILL.md`](./SKILL.md)：核心工作流和通用验证清单
- [`references/ai-for-science-sources.md`](./references/ai-for-science-sources.md)：AI for Science 信源、筛选、输出和专项验证规则

## 免责声明

本 Skill 用于新闻研究、资料整理和辅助写作。预印本尚未同行评议，期刊论文和机构声明也需要结合原始数据、实验设计和后续验证进行人工判断。
