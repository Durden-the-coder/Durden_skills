# 天天基金净值拉取 — 坑点与接口笔记

本 skill 的核心是从天天基金（东方财富）免费拿公募基金历史净值。
下面是实测踩过的坑，改脚本前务必先读，避免重复踩雷。

## 1. 正确的数据接口

**只用这个**：基金档案页「历史净值」接口

```
https://api.fund.eastmoney.com/f10/lsjz?fundCode=<6位代码>&pageIndex=1&pageSize=20&_=<时间戳>&callback=jQueryxxx
```

返回 JSONP：`callback({ "Data": { "LSJZList": [ {FSRQ, DWJZ, LJJZ, JZZZL}, ... ] } })`

字段含义：
- `FSRQ`  净值日期（YYYY-MM-DD）
- `DWJZ`  单位净值
- `LJJZ`  累计净值
- `JZZZL` 日增长率（%）

## 2. 千万别用的接口 / 字段

- **`pingzhongdata/<code>.js` 里的 `Data_netWorthTrend`**：这是走势图用的**抽样/插值序列**（含周日、日期不规则、数值四舍五入），与官方逐日净值对不上，最大偏差可达 0.04。初版踩过，已弃用。
- **`F10DataApi.aspx?type=lsjz`**：旧端点已废弃 / 被封，直连只回几十字节错误。
- **`page.evaluate(() => fetch(...))` 在页面里发请求**：被 CORS 拦截（该接口不带正确 Referer 时跨域失败）。

## 3. 接口行为陷阱

- **`pageSize` 被忽略**：无论传多少（100 / 6000），接口固定每页 20 条，`TotalCount` 也常为 0。
  → 必须按 `pageIndex=1,2,3...` **逐页翻**，直到某页 `LSJZList` 不足 20 条为止。
- 需要正确的 **`Referer`**：请求头带 `Referer: http://fundf10.eastmoney.com/jjjz_<code>.html`。
  脚本里做法是先 `page.goto` 到该历史净值页建立上下文，再用 `route.fetch(..., headers={"Referer": ref})` 翻页，浏览器自带 cookie，绕开反爬。

## 4. Playwright 路由拦截翻页的「递归重入」坑

`route.fetch()` 发出的请求**仍会命中 `page.route("**/*")` 的 handler**，导致处理函数递归调用、无限循环、最终拖垮浏览器。

解法：用一个 `paging` 守卫字典。外层进入 handler 时置 `paging["v"]=True`；
内层翻页的 `route.fetch` 重入 handler 时检测到 `paging["v"]` 为 True，直接 `route.continue_()` 放行到真实网络。翻页结束在 `finally` 里复位标志并 `done.set()`。

脚本 `fetch_one` 已实现该守卫，改逻辑时务必保留。

## 5. 名称查代码的搜索接口

```
https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?m=1&key=<名称>
```

- 浏览器内 `page.goto` 该 URL，读 `body.innerText` 即为 JSON（非 JSONP）。
- 结构：`{ "Datas": [ {"CODE": "110003", "NAME": "易方达上证50增强A"}, ... ] }`
- 匹配策略：先精确 `NAME == 输入名`；否则包含匹配；再否则取候选首条并**打印告警**让用户核对。
- 模糊/笔误名称可能匹配错基金（例：用户写「时生恒生医疗保健…」实际应为「博时」，搜索首候选给了博时 014424）。名称拿不准时务必人工确认代码。

## 6. 命名与文件落盘

- 命名规则：`<代码>_<名称>_<净值_完整>_<起始年>-<结束年>.csv`
  （起始年/结束年取实际区间，同年则只写一年）。
- **Windows 文件名非法字符** `[\\/:*?"<>|]` 必须清洗（如 `融通健康产业灵活配置混合A/B` 的 `/` → `_`）。脚本 `safe()` 已处理。
- 用 `utf-8-sig`（带 BOM）写 CSV，Excel 打开中文不乱码。
- 行按日期升序排序；同日去重（理论不会出现，保险起见）。

## 7. QDII / 海外类基金的注意点

- 末条日期常早于 A 股基金（如 2026-08-07），因为海外资产净值披露节奏不同，属正常。
- 成立日至最新日之间可能含非交易披露日（半年报 / 年报日），天天基金会给出，比部分付费源更全。

## 8. 运行环境

- 需要 `playwright` + 一个 Chromium 内核浏览器。脚本优先 `channel="msedge"`（本机装了 Edge），
  失败则回退 Playwright 自带 chromium（需先 `playwright install chromium`）。
- 用本机真实浏览器而非 Python `requests` 直连：直连东方财富会被反爬返回空（`var apidata=`）。
