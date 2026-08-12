#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从天天基金（东方财富）免费拉取公募基金历史净值数据，保存为 CSV。

特点：
- 完全免费，无需会员 / 登录 / cookie 账号。
- 走基金档案页真实「历史净值」接口 api.fund.eastmoney.com/f10/lsjz，
  数据为官方逐日披露值（单位净值 / 累计净值 / 日增长率）。
- 支持按「基金名称」或「6 位代码」输入；名称会自动查代码。
- 用 Playwright 浏览器 + 路由拦截翻页，绕开反爬与 CORS。
- 输出命名规则：<代码>_<名称>_净值_完整_<起始年>-<结束年>.csv

依赖：
- playwright（pip install playwright && playwright install chromium，或本机已装 Edge）
- 标准库：asyncio / json / re / os / csv / argparse / urllib

用法示例：
  # 按名称批量拉取（先自动查代码）
  python fetch_fund_nav.py --funds "易方达上证50增强A,兴全合润混合A"

  # 直接给代码
  python fetch_fund_nav.py --codes "110003,163406"

  # 名称+代码一一对应（跳过查代码）
  python fetch_fund_nav.py --funds "易方达上证50增强A" --codes "110003"

  # 从已有映射 JSON（{名称:代码}）拉取
  python fetch_fund_nav.py --codes-json fund_codes.json

  # 自定义输出目录
  python fetch_fund_nav.py --codes "110003" --outdir "D:/基金净值数据"
"""

import asyncio
import csv
import json
import os
import re
import argparse
import urllib.parse

from playwright.async_api import async_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Windows 文件名非法字符清洗：把 \ / : * ? " < > | 替换为 _
_ILLEGAL = re.compile(r'[\\/:*?"<>|]')


def safe(name: str) -> str:
    return _ILLEGAL.sub("_", (name or "").strip())


def split_list(s: str):
    return [x.strip() for x in re.split(r"[,;，；]", s) if x.strip()]


# ---------------------------------------------------------------------------
# 1) 名称 -> 代码 解析（天天基金搜索接口）
# ---------------------------------------------------------------------------
async def resolve_codes(page, names):
    """返回 {name: code}；无精确匹配时取候选首条，并打印告警。"""
    res = {}
    for name in names:
        url = "https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?m=1&key=" + urllib.parse.quote(name)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            txt = await page.locator("body").inner_text()
            data = json.loads(txt)
            datas = data.get("Datas", [])
            pick = None
            warn = False
            for d in datas:
                if d.get("NAME") == name:
                    pick = d
                    break
            if pick is None:
                for d in datas:
                    n = d.get("NAME", "")
                    if name in n or n in name:
                        pick = d
                        break
            if pick is None and datas:
                pick = datas[0]
                warn = True
            print(f"=== {name} ===")
            for d in datas[:6]:
                mark = " <<<" if d is pick else ""
                print(f"  {d.get('CODE')}  {d.get('NAME')}{mark}")
            if warn:
                print("  !! 无精确匹配，已取候选首条，请核对")
            if pick:
                res[name] = pick.get("CODE")
        except Exception as e:
            print(f"ERR 查代码失败 {name}: {e!r}")
    return res


# ---------------------------------------------------------------------------
# 2) 单只基金净值拉取（路由拦截 + 翻页）
# ---------------------------------------------------------------------------
async def fetch_one(ctx, code, name):
    page = await ctx.new_page()
    captured = []
    done = asyncio.Event()
    paging = {"v": False}
    ref = f"http://fundf10.eastmoney.com/jjjz_{code}.html"

    async def handle(route):
        url = route.request.url
        if "lsjz" in url and "fund.eastmoney.com" in url:
            if paging["v"]:
                # 内层翻页请求重入，放行到真实网络，避免递归
                await route.continue_()
                return
            paging["v"] = True
            cb = re.search(r"callback=([^&]+)", url)
            cbname = cb.group(1) if cb else "cb"
            all_list = []
            pg = 1
            try:
                while True:
                    u = re.sub(r"pageIndex=\d+", f"pageIndex={pg}", url)
                    r = await route.fetch(url=u, headers={"Referer": ref})
                    b = await r.text()
                    m = re.search(r"\{[\s\S]*\}", b)
                    if not m:
                        break
                    obj = json.loads(m.group(0))
                    lst = (obj.get("Data") or {}).get("LSJZList") or []
                    if not lst:
                        break
                    all_list += lst
                    if len(lst) < 20:
                        break
                    pg += 1
                    if pg > 400:
                        break
                captured.append(all_list)
                r0 = await route.fetch(url=re.sub(r"pageIndex=\d+", "pageIndex=1", url), headers={"Referer": ref})
                obj0 = json.loads(re.search(r"\{[\s\S]*\}", await r0.text()).group(0))
                obj0["Data"]["LSJZList"] = all_list
                await route.fulfill(
                    body=f"{cbname}({json.dumps(obj0, ensure_ascii=False)})".encode("utf-8"),
                    content_type="application/javascript; charset=utf-8",
                )
            except Exception as e:
                print(f"  [翻页异常] {code} {e!r}")
                await route.continue_()
            finally:
                paging["v"] = False
                done.set()
        else:
            await route.continue_()

    await page.route("**/*", handle)
    print(f"== {code} {name} ==")
    await page.goto(ref, wait_until="domcontentloaded", timeout=30000)
    try:
        await asyncio.wait_for(done.wait(), timeout=120)
    except asyncio.TimeoutError:
        print(f"  !! 超时未捕获 {code}")
    await page.close()

    if not captured:
        print(f"  !! 未捕获数据 {code}")
        return None
    lsjz = captured[0]
    rows = []
    seen = set()
    for it in lsjz:
        d = it.get("FSRQ")
        if not d or d in seen:
            continue
        seen.add(d)
        rows.append({
            "日期": d,
            "单位净值": it.get("DWJZ"),
            "累计净值": it.get("LJJZ"),
            "日增长率": it.get("JZZZL"),
        })
    rows.sort(key=lambda x: x["日期"])
    if not rows:
        print(f"  !! 空数据 {code}")
        return None
    sy = rows[0]["日期"][:4]
    ey = rows[-1]["日期"][:4]
    span = sy if sy == ey else f"{sy}-{ey}"
    fname = f"{code}_{safe(name)}_净值_完整_{span}.csv"
    return rows, fname


# ---------------------------------------------------------------------------
# 3) CSV 写出
# ---------------------------------------------------------------------------
def write_csv(outdir, fname, rows):
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, fname)
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["日期", "单位净值", "累计净值", "日增长率"])
        w.writeheader()
        w.writerows(rows)
    return out


# ---------------------------------------------------------------------------
# 4) 浏览器启动（优先 Edge，回退 Playwright chromium）
# ---------------------------------------------------------------------------
async def launch_browser(p):
    try:
        return await p.chromium.launch(headless=True, channel="msedge")
    except Exception as e:
        print(f"[提示] channel=msedge 启动失败（{e!r}），改用 Playwright 自带 chromium")
        return await p.chromium.launch(headless=True)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
async def main():
    ap = argparse.ArgumentParser(description="天天基金净值免费批量拉取")
    ap.add_argument("--funds", help="基金名称，逗号分隔")
    ap.add_argument("--codes", help="基金代码(6位)，逗号分隔；与 --funds 一一对应或单独使用")
    ap.add_argument("--codes-json", help="已存在的 {名称:代码} 映射 JSON 文件")
    ap.add_argument("--outdir", default="D:/基金净值数据", help="输出目录，默认 D:/基金净值数据")
    args = ap.parse_args()

    # 构造 name->code 映射
    if args.codes_json:
        with open(args.codes_json, encoding="utf-8") as f:
            mapping = json.load(f)
    elif args.funds and args.codes:
        names = split_list(args.funds)
        codes = split_list(args.codes)
        mapping = dict(zip(names, codes))
    elif args.funds:
        names = split_list(args.funds)
        async with async_playwright() as p:
            browser = await launch_browser(p)
            ctx = await browser.new_context(user_agent=UA)
            page = await ctx.new_page()
            mapping = await resolve_codes(page, names)
            await browser.close()
    elif args.codes:
        codes = split_list(args.codes)
        mapping = {c: c for c in codes}
    else:
        print("请至少提供 --funds / --codes / --codes-json 之一")
        return

    if not mapping:
        print("没有任何可拉取的基金，退出")
        return

    results = []
    async with async_playwright() as p:
        browser = await launch_browser(p)
        ctx = await browser.new_context(user_agent=UA)
        for name, code in mapping.items():
            try:
                ret = await fetch_one(ctx, code, name)
                if ret is None:
                    results.append((code, name, None))
                    continue
                rows, fname = ret
                out = write_csv(args.outdir, fname, rows)
                print(f"  行数={len(rows)}  区间={rows[0]['日期']} ~ {rows[-1]['日期']}  -> {fname}")
                results.append((code, name, out))
            except Exception as e:
                print(f"!! 基金失败 {code} {name}: {e!r}")
                results.append((code, name, None))
        await browser.close()

    print("\n===== 汇总 =====")
    for code, name, out in results:
        print(f"{code} {name}: {'OK ' + os.path.basename(out) if out else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
