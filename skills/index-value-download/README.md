# index-value-download

从理杏仁（lixinger.com）批量下载指数估值数据 CSV 的 Codex / Agent Skill。支持 `PE-TTM`、`PB`、`股息率` 三个指标（统一`市值加权`、`按日——全部时间段`），以及「上市以来」「10年」等多档时间范围，并内置断点续传与缺口体检。

## 适用场景

- 更新或补齐一批指数的历史估值数据；
- 按不同时间范围（上市以来 / 10 年 / 5 年 / 3 年）批量导出 CSV；
- 浏览器长时间运行崩溃后，从缺口续传而不是重跑全部。

## 凭据（重要）

调用本 skill 的**第一件事**是确认用户本轮是否提供了理杏仁账号与密码。未提供则必须先询问，禁止使用历史、示例或缓存凭据。

密码**只**通过环境变量传入，不写入脚本、日志或 memory：

```bash
export LIXINGER_USER="用户提供的账号"
export LIXINGER_PASS="用户提供的密码"
```

## 安装

将整个文件夹复制到 Agent 的 skills 目录：

```text
%USERPROFILE%\.codex\skills\index-value-download
```

如果宿主不能自动发现 skill，在任务中提供 `SKILL.md` 路径或直接加载其内容即可。

## 用法

脚本依赖 `playwright` 与 Edge（`channel="msedge"`，有头模式）。本机可用解释器示例：

```bash
PY="C:/Users/Administrator/.workbuddy/binaries/python/envs/default/Scripts/python"

# 上市以来，断点续传
"$PY" scripts/lixinger_download.py --range "上市以来" --out "D:/指数估值数据" --skip-existing

# 只跑指定指数（续传补洞）
"$PY" scripts/lixinger_download.py --range "10年" --out "D:/指数估值数据_10年" --indices "沪深300,中证500"

# 只体检不下载（无需凭据），输出待补指数清单
"$PY" scripts/lixinger_download.py --range "10年" --out "D:/指数估值数据_10年" --date 20260812 --check
```

## 参数

| 参数 | 说明 |
|---|---|
| `--range` | 时间范围：`上市以来` / `10年` / `5年` / `3年`（默认 `上市以来`） |
| `--out` | CSV 保存目录 |
| `--indices` | 逗号分隔的指数名，覆盖默认 22 个清单；用于续传 |
| `--metrics` | 逗号分隔指标，默认 `PE-TTM,PB,股息率` |
| `--skip-existing` | 跳过当天已下载完成的「指数×指标」组合 |
| `--date` | 判定"已下载"的日期戳 YYYYMMDD；跨天续传/事后体检时传首日日期 |
| `--check` | 只体检不下载，列出缺失组合并给出待补指数清单 |

## 默认指数清单（22 个）

```
中证医疗, 红利低波, 全指信息, 养老产业, 中证传媒, 中证环保, 创业板50,
上证50, 全指医药, 中证白酒, 中国互联网50, 中证消费, 中证500,
恒生医疗保健指数, 恒生指数, 中国互联网, 中证A500, 沪深300,
恒生科技指数, 标普500, 中证红利, 中证证保
```

## 已知坑位

- 搜索「中国互联网」可能误命中「中国互联网50」：脚本已做名称边界匹配，并**禁止**兜底选第一项。
- 某些标的只有 `PE-TTM`：它们是公司股票而非指数（如纳斯达克 OMX 交易所），应跳过而非硬凑。
- 文件名为「上市以来」但请求 10 年：指数成立不足 10 年，两者等价，属正常。
- 浏览器长时间运行易崩：建议一次跑 7~8 个指数，每批后 `--check`，全部完成后必须再 `--check` 终检。

## 许可证

本 Skill 随仓库采用 [MIT License](../LICENSE)。
