# nsfc-mianshang-review

**当前版本：** `0.4.2`

这是一个面向 **国家自然科学基金面上项目（2026版）** 的评审 workflow skill。
它不是单纯“写评语”的提示词，而是一套 **分阶段、低 token、可复用、可审计** 的评审流程。

## 重要声明

本 skill 是非官方、实验性的项目书内部预审辅助工具，不隶属于国家自然科学基金委员会，也不提供正式资助判断。所有输出均可能存在遗漏或错误，必须由人类专家复核。

使用真实项目书时，请注意保密和合规：不要把未公开申请书、附件、图件、个人信息或 PDF 密码提交到公开 issue、PR、讨论区或不可信环境中。

默认适合两类场景：

1. 申报前内部预审
2. 面向正式函评风格的结构化审阅

并默认输出**润色过的中文评审文本**。

---

## 安装和使用

### 目录结构

```text
nsfc-mianshang-review/
  SKILL.md
  README.md
  CHANGELOG.md
  scripts/
    extract_nsfc_text.py
  references/
    scoring-rubric.txt
    output-templates.txt
```

### 输入

支持以下输入之一：

- 项目书 PDF
- 已导出的 TXT
- OCR 后文本

如果 PDF 加密，还需要：

- PDF 密码
- 或解密后的 PDF

### 运行方式

当输入是 PDF 时，本 skill 默认先自动进入本地文本提取阶段。只有在以下情况发生时，才需要人工介入：

- PDF 加密且没有可用密码
- PDF 为扫描版且没有可用 OCR 文本
- 提取结果严重缺损或损坏
- 无法创建安全的本地 review 工作目录

提取命令：

```bash
<python> scripts/extract_nsfc_text.py --proposal <proposal.pdf> --workdir <review_dir>
```

如果环境对外部目录首次写文件不稳定，可追加：

```bash
--init-review-files
```

示例：

```bash
<python> scripts/extract_nsfc_text.py --proposal "D:\path\proposal.pdf" --password "your-password" --workdir "D:\path\nsfc_review_proposal" --init-review-files
```

如果不指定 `--workdir`，workflow 会默认在项目书所在文件夹的上一级创建：

```text
nsfc_review_<proposal-stem>/
```

### 输出文件

```text
review_dir/
  extracted/
    00_full_text.txt
    01_section_index.txt
    extraction_report.txt
  review/
    nsfc_review_cache.txt
    01_scientific_critique.txt
    02_literature_checks.txt
    03_reviewer2_stress_test.txt
    04_final_review.txt
```

---

## 核心原则

### 1. PDF 只读一次

如果输入是 PDF，本 workflow 只在 **PDF -> TXT** 转换阶段读取 PDF。
转换成功后，后续所有工作只基于：

- `00_full_text.txt`
- `01_section_index.txt`
- `nsfc_review_cache.txt`
- 各阶段 review 文件

### 2. TXT 是主工作副本

中间工作文件优先用 `.txt`，不是 Markdown。
原因是：

- 更轻
- 更适合中文长文本处理
- 对 LLM 更稳定
- 便于检索、切片和缓存

### 3. cache-first，而不是全文总结

这个 skill 不追求“把整本申请书总结一遍”，而是先提取决策相关内容，写成 review cache，再做 critique / reviewer-2 / final review。

### 4. 结构性缺陷优先于亮点加分

在 kill-mode 下，以下因素不能自动推高资助建议：

- 题目重要
- 平台条件不错
- 有一定前期基础
- 申请人会做技术

如果 proposal 仍存在多个**结构性缺陷**，最终建议应偏负面。

---

## 依赖的其他 skills

- `scientific-critical-thinking`
- `literature-review`
- `reviewer-2-simulator`
- `peer-review`
- `scientific-writing`

推荐理解方式：

- `scientific-critical-thinking` 负责“问题是不是真的严重”
- `reviewer-2-simulator` 负责“这些问题会不会导致被毙”
- `peer-review` 负责“把判断组织起来”
- `scientific-writing` 负责“把组织好的判断写得专业”

---

## 默认评审范围

默认重点审这 5 个部分：

1. 标题
2. 中文摘要
3. 立项依据
4. 研究内容（包含特色与创新点、年度计划）
5. 研究基础（包含可行性分析）

默认不优先处理：

- 预算细项
- 附件目录机制
- 常规表格合规项
- 推荐函 / 公章 / 声明类流程文件

---

## 人工审核边界

以下内容默认仍需人工补查：

1. 工作条件
2. 个人简历 / 代表作
3. 模式图 / 机制示意图
4. 技术路线图 / 实验流程图
5. 实验结果图、显微图、凝胶图、免疫印迹、统计图等图像证据

---

## 适合谁用

适合：

- 做国自然面上项目内部预审的人
- 想把长 PDF 评审流程结构化的人
- 想复用评审底稿和中间状态的人

不适合：

- 想直接让 AI 一键生成完整申请书的人
- 不愿意人工复核关键判断的人
- 需要全自动处理预算和形式审查细节的人

---

## 一句话总结

这个 skill 的核心不是“写得像评审”，而是：

**把基金评审这件事，从一次性长文本聊天，变成一个分阶段、可审计、可追责、可复用的判断流程。**
