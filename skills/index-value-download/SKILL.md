---
name: index-value-download
description: 从理杏仁（lixinger.com）批量下载指数估值数据 CSV（PE-TTM / PB / 股息率，市值加权，按日全部时间段），支持「上市以来」「10年」等时间范围与断点续传。当用户提到理杏仁、指数估值数据、估值分位、PE-TTM/PB/股息率下载、更新估值CSV时使用。执行前必须先取得用户的理杏仁账号与密码。
---

# 理杏仁指数估值数据批量下载

**版本：1.0.0**

## 0. 前置：凭据确认（硬性阻断）

调用本 skill 后的**第一件事**是检查用户本轮是否提供了理杏仁账号与密码。

- **未提供** → 立即停止，向用户提问索取，不得进入任何后续步骤：

  > 需要你的理杏仁账号信息才能开始下载：
  > 1）登录手机号／账号
  > 2）密码
  > （可选）需要下载的指数清单、时间范围、保存目录

- **严禁**使用历史会话中的账号、示例账号、缓存凭据或任何猜测值。
- **严禁**把密码写入脚本文件、日志或 memory。凭据只能通过环境变量 `LIXINGER_USER` / `LIXINGER_PASS` 传给脚本。
- 拿到凭据后，再确认（缺省即用默认值）：
  - 时间范围：`上市以来` / `10年` / `5年` / `3年`（默认 `上市以来`）
  - 保存目录：默认 `D:\指数估值数据`（10年默认 `D:\指数估值数据_10年`）
  - 指数清单：默认见下方「默认指数清单」

## 1. 默认指数清单（22个）

```
中证医疗, 红利低波, 全指信息, 养老产业, 中证传媒, 中证环保, 创业板50,
上证50, 全指医药, 中证白酒, 中国互联网50, 中证消费, 中证500,
恒生医疗保健指数, 恒生指数, 中国互联网, 中证A500, 沪深300,
恒生科技指数, 标普500, 中证红利, 中证证保
```

指标固定三项：`PE-TTM`、`PB`、`股息率`，加权方式统一 `市值加权`，导出粒度 `按日——全部时间段`。

## 2. 执行

脚本：`scripts/lixinger_download.py`（Playwright + Edge，有头模式，不要改成 headless，理杏仁会拦截）。

**先确认解释器**：默认 `python` 可能没装 playwright。本机可用的是
`C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python`（备选 `.../Programs/Python/Python311/python`）。
换机器时先探测：

```bash
python -c "import playwright" || echo "换解释器"
```

```bash
# Windows / Git Bash
PY="C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python"
export LIXINGER_USER="用户提供的账号"
export LIXINGER_PASS="用户提供的密码"

"$PY" "C:/Users/Administrator/.workbuddy/skills/index-value-download/scripts/lixinger_download.py" \
  --range "上市以来" \
  --out "D:/指数估值数据" \
  --skip-existing
```

常用参数：

| 参数 | 说明 |
|---|---|
| `--range` | 时间范围，如 `上市以来`、`10年`（默认 `上市以来`） |
| `--out` | CSV 保存目录 |
| `--indices` | 逗号分隔的指数名，覆盖默认清单；用于续传时只跑剩余指数 |
| `--metrics` | 逗号分隔指标，默认 `PE-TTM,PB,股息率` |
| `--skip-existing` | 跳过当天已下载完成的「指数×指标」组合（断点续传核心） |
| `--date` | 判定"已下载"的日期戳 YYYYMMDD，默认今天；跨天续传/事后体检时传首日日期 |
| `--check` | 只体检不下载（无需凭据）：列出缺失组合，并直接给出可喂给 `--indices` 的待补清单 |

**必须用后台方式运行**（单次任务耗时长，前台会超时）：`run_in_background: true`，然后按通知读取输出。

## 3. 分批与续传（重要）

浏览器长时间运行易崩溃（历史上多次 Exit Code 1）。因此：

1. **一次最多跑 7~8 个指数**，分批执行，而不是一口气 22 个。
2. 每批结束后运行 `--check` 体检，把结果里缺失的指数喂给下一批的 `--indices`。
3. 崩溃后不要重跑全部，用 `--check` 找出缺口再补。
4. 全部跑完后**必须再做一次 `--check`**，确认 `指数数 × 3` 个文件齐全，才能向用户报告完成。

历史教训：曾出现「中证环保 10年 股息率」单个文件静默缺失，就是因为跳过了终检。

## 4. 已知坑位

| 现象 | 原因 | 处理 |
|---|---|---|
| 搜「中国互联网」下到了「中国互联网50」 | 前缀匹配歧义 | 脚本已做名称边界匹配；**禁止**加"兜底选第一项"的逻辑 |
| 某指数只有 PE-TTM，没有 PB／股息率 | 该标的是**公司股票**不是指数（如 Nasdaq/纳斯达克OMX 交易所） | 向用户确认后跳过，不要硬凑 |
| 文件名写着「上市以来」但请求的是 10年 | 指数成立不足 10 年，两者等价 | 正常，无需处理 |
| 搜索框点不动 | Vue Multiselect 需先点容器再输入 | 脚本已处理：先 `click(".multiselect")` 再填 `input.multiselect__input` |
| 页面落到 `custom-chart` | 搜索结果跳错子页 | 脚本自动改写 URL 到 `/fundamental/valuation/primary` |

## 5. 收尾

- 不主动清理旧文件；除非用户明确要求删除。
- 向用户汇报：目录路径、CSV 总数、本次新增数、失败/跳过的指数及原因。
