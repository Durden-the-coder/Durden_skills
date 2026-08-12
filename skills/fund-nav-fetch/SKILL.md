---
name: fund-nav-fetch
description: |
  This skill should be used when the user wants to download or obtain complete
  historical fund NAV (净值) data for Chinese public mutual funds (公募基金) from
  天天基金 / 东方财富 (East Money) — free of charge, no membership or login.
  Trigger on requests like "下载某基金净值 CSV", "拉取基金历史净值", "从天天基金获取净值数据",
  or any batch fetch of 单位净值/累计净值/日增长率 by fund name or 6-digit code.
  It resolves fund names to codes, paginates the official 历史净值 API through a
  real browser (bypassing anti-scraping), and saves per-fund CSVs named
  代码_名称_净值_完整_起始年-结束年.csv.
agent_created: true
---

# 天天基金净值批量拉取（免费）

## Overview

从天天基金（东方财富）**免费**拉取公募基金自成立以来的完整历史净值，输出为本地 CSV。
数据来自基金档案页真实的「历史净值」接口，包含 **单位净值 / 累计净值 / 日增长率**，按交易日逐日披露、真实准确。

与理杏仁等付费源不同：天天基金无需会员、无导出区间限制、不会因会员到期而被截断。

## When to Use

- 用户要下载某只或多只基金的净值 CSV（按名称或代码）。
- 用户要做基金收益 / 回撤对比分析，需要先拿到净值序列。
- 用户提到「天天基金」「东方财富」「基金净值」「历史净值」「单位净值」「累计净值」。
- 注意：这是**公募基金净值**，不是股票 / 指数估值（指数估值见 index-value-download 类场景）。

## Resources

- `scripts/fetch_fund_nav.py` — 主脚本：查代码 + 浏览器翻页拉取 + 写 CSV，一行命令批量完成。
- `references/tips.md` — 接口细节与踩坑笔记（反爬、递归重入、pageSize 忽略、名称模糊匹配、非法文件名等）。**改脚本前必读。**

## Workflow

### 方式一：按基金名称批量拉取（最常见）

直接把用户给的名称交给脚本，脚本会自动查代码再拉取：

```bash
python scripts/fetch_fund_nav.py --funds "易方达上证50增强A,兴全合润混合A,招商中证白酒指数(LOF)A"
```

- 名称会以逗号 / 分号分隔，逐个走天天基金搜索接口查 6 位代码。
- 若某名称无精确匹配，脚本会取搜索候选首条并**打印 `!! 无精确匹配` 告警**，必须把实际代码反馈给用户核对（易混淆名称如「博时/时生」可能匹配错）。

### 方式二：直接给代码

```bash
python scripts/fetch_fund_nav.py --codes "110003,163406,161725"
```
只给代码时，文件名用代码本身作为名称占位。

### 方式三：名称与代码一一对应（跳过查代码）

```bash
python scripts/fetch_fund_nav.py --funds "易方达上证50增强A" --codes "110003"
```

### 方式四：用已有映射 JSON

若用户已提供 `{名称: 代码}` 的 JSON（如前一轮的产物），直接喂入避免重复查：

```bash
python scripts/fetch_fund_nav.py --codes-json fund_codes.json
```

### 自定义输出目录

默认输出到 `D:/基金净值数据`，可用 `--outdir` 覆盖：

```bash
python scripts/fetch_fund_nav.py --codes "110003" --outdir "F:/Claws/Daily_work/nav"
```

## Output & Naming Convention

每个基金生成一个 CSV，命名严格遵循：

```
代码_名称_净值_完整_起始年-结束年.csv
```

示例：`110003_易方达上证50增强A_净值_完整_2004-2026.csv`

- 列：`日期, 单位净值, 累计净值, 日增长率`
- 行数 = 该基金成立日至最新披露日的全部记录（升序、同日去重）。
- 中文以 `utf-8-sig` 编码，Excel 直接打开不乱码。
- 名称中的 Windows 非法字符（斜杠、反斜杠、冒号、星号、问号、引号、尖括号、竖线）已自动替换为 `_`。
- 区间年份取实际发行年–最新年（同年只写一年）。

## Important Notes (必读 references/tips.md)

以下坑都已固化进脚本，改动前务必理解：

1. **唯一可信接口**是 `api.fund.eastmoney.com/f10/lsjz`（历史净值）。不要用 `pingzhongdata.js` 的 `Data_netWorthTrend`（走势图抽样/插值，数值不准）或已废弃的 `F10DataApi.aspx`。
2. 该接口**忽略 `pageSize`、固定每页 20 条**，必须按 `pageIndex` 逐页翻到不足 20 条为止。
3. 必须用真实浏览器（Playwright + Edge/Chromium）走网络栈，带 `Referer` 和 cookie 才能绕开反爬；Python `requests` 直连或页面内 `fetch` 都会被拦成空数据。
4. 路由拦截翻页存在**递归重入**陷阱，脚本用 `paging` 守卫解决——不要去掉该守卫。
5. QDII / 海外基金末条日期可能早于 A 股基金，属正常披露节奏差异。
6. 运行依赖：`pip install playwright` 且需 Chromium 内核浏览器（脚本优先用本机 Edge，失败回退 Playwright 自带 chromium，需先 `playwright install chromium`）。

## 运行环境要点

- 用隔离的 venv Python 运行：`…/.workbuddy/binaries/python/envs/default/Scripts/python scripts/fetch_fund_nav.py …`
- 若未装 Playwright：`…/python -m pip install playwright` 与 `playwright install chromium`。
