"""
理杏仁指数估值数据批量下载器

凭据只从环境变量读取：LIXINGER_USER / LIXINGER_PASS
用法示例：
    python lixinger_download.py --range 上市以来 --out "D:/指数估值数据" --skip-existing
    python lixinger_download.py --range 10年 --out "D:/指数估值数据_10年" --indices "沪深300,中证500"
    python lixinger_download.py --range 10年 --out "D:/指数估值数据_10年" --check
"""
import argparse
import asyncio
import io
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

HOME = "https://www.lixinger.com"

DEFAULT_INDICES = [
    "中证医疗", "红利低波", "全指信息", "养老产业", "中证传媒",
    "中证环保", "创业板50", "上证50", "全指医药", "中证白酒",
    "中国互联网50", "中证消费", "中证500", "恒生医疗保健指数",
    "恒生指数", "中国互联网", "中证A500", "沪深300", "恒生科技指数",
    "标普500", "中证红利", "中证证保",
]
DEFAULT_METRICS = ["PE-TTM", "PB", "股息率"]


def log(msg, level="INFO"):
    prefix = {"INFO": ">>>", "OK": "[OK]", "WARN": "[!]", "FAIL": "[X]"}
    print(f"{prefix.get(level, '>>>')} {msg}", flush=True)


def metric_token(metric):
    """指标在导出文件名中的写法"""
    return metric.replace("-", "_") if metric == "PE-TTM" else metric


def already_done(save_dir: Path, index_name: str, metric: str, today: str) -> bool:
    """当天是否已下载该 指数x指标 组合（文件名形如 指数_指标_市值加权_范围_YYYYMMDD_HHMMSS.csv）"""
    for pat in (f"{index_name}_{metric}_*{today}*.csv",
                f"{index_name}_{metric_token(metric)}_*{today}*.csv"):
        if list(save_dir.glob(pat)):
            return True
    return False


def name_matches(txt: str, name: str) -> bool:
    """带边界的名称匹配：避免『中国互联网』误命中『中国互联网50』"""
    t = txt.strip()
    pos = t.find(name)
    if pos < 0:
        return False
    tail = t[pos + len(name): pos + len(name) + 1]
    if tail == "":
        return True
    return not (tail.isalnum() or "\u4e00" <= tail <= "\u9fff")


# ---------------- 登录 ----------------
async def do_login(page, username, password):
    body = await page.content()
    if "退出" in body or username in body:
        log("已登录", "OK")
        return
    try:
        btn = page.locator("text=登录 >> visible=true").first
        if await btn.is_visible(timeout=3000):
            await btn.click()
            await asyncio.sleep(1.5)
    except Exception:
        pass

    inputs = page.locator("input")
    for i in range(await inputs.count()):
        inp = inputs.nth(i)
        try:
            if not await inp.is_visible():
                continue
            ph = (await inp.get_attribute("placeholder")) or ""
            tp = (await inp.get_attribute("type")) or ""
            if "手机" in ph or "账号" in ph:
                await inp.fill(username)
            elif tp == "password":
                await inp.fill(password)
        except Exception:
            pass
    try:
        await page.locator("button:has-text('登录'):visible").first.click()
        log("提交登录", "OK")
    except Exception:
        pass
    await asyncio.sleep(3)


# ---------------- 搜索 ----------------
async def do_search(page, index_name):
    """Vue Multiselect：先点容器激活，再输入，再挑『(指数)』选项"""
    try:
        await page.locator(".multiselect").first.click(timeout=5000)
        await asyncio.sleep(0.5)
    except Exception as e:
        log(f"  搜索框点击失败: {e}", "FAIL")
        return False

    try:
        await page.locator("input.multiselect__input").first.fill(index_name)
        await asyncio.sleep(2)
    except Exception as e:
        log(f"  输入失败: {e}", "FAIL")
        return False

    options = page.locator(".multiselect__option")
    try:
        await options.first.wait_for(state="visible", timeout=6000)
    except Exception:
        log("  下拉未出现", "WARN")
        return False

    n = min(await options.count(), 15)
    texts = []
    for i in range(n):
        try:
            texts.append((await options.nth(i).text_content()) or "")
        except Exception:
            texts.append("")

    # 第一轮：边界精确匹配 + (指数)
    for i, txt in enumerate(texts):
        if "(指数)" in txt and name_matches(txt, index_name):
            await options.nth(i).click()
            log(f"  选择: {txt.strip()[:60]}", "OK")
            await asyncio.sleep(3)
            return await ensure_valuation_page(page)

    # 第二轮：包含匹配 + (指数)
    for i, txt in enumerate(texts):
        if "(指数)" in txt and index_name in txt:
            await options.nth(i).click()
            log(f"  选择[包含]: {txt.strip()[:60]}", "WARN")
            await asyncio.sleep(3)
            return await ensure_valuation_page(page)

    # 不做"兜底选第一项"，避免下错标的
    log(f"  未匹配到指数「{index_name}」，候选: {[t.strip()[:24] for t in texts[:5]]}", "FAIL")
    return False


async def ensure_valuation_page(page):
    url = page.url
    if "custom-chart" in url:
        target = url.replace("/fundamental/custom-chart", "/fundamental/valuation/primary")
        try:
            await page.goto(target, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
        except Exception as e:
            log(f"  跳转估值页失败: {e}", "WARN")
    return True


# ---------------- 下载单指标 ----------------
async def click_label(page, text):
    try:
        await page.locator(f'label.btn:has-text("{text}")').first.click(timeout=4000)
    except Exception:
        await page.evaluate(
            """(t) => {
                for (const l of document.querySelectorAll('label.btn'))
                    if (l.textContent.trim() === t) { l.click(); return true; }
                return false;
            }""",
            text,
        )
    await asyncio.sleep(1.2)


async def download_metric(page, metric, time_range):
    await click_label(page, metric)
    await click_label(page, "市值加权")

    # 时间范围
    try:
        await page.get_by_text(time_range, exact=True).click(timeout=3000)
    except Exception:
        await page.evaluate(
            """(t) => {
                for (const el of document.querySelectorAll('button, span, a, label, div')) {
                    if (el.textContent && el.textContent.trim() === t && el.offsetParent !== null) {
                        el.click(); return true;
                    }
                }
                return false;
            }""",
            time_range,
        )
    await asyncio.sleep(1.5)

    # 导出
    try:
        await page.locator('button:has-text("导出CSV"), span:has-text("导出CSV")').first.click(timeout=5000)
        await asyncio.sleep(2)
    except Exception as e:
        log(f"    导出按钮未找到: {e}", "FAIL")
        return

    # 粒度：按日 —— 全部时间段
    try:
        await page.locator("text=/按日.*全部时间段/ >> visible=true").first.click(timeout=3000)
    except Exception:
        for t in ("按日", "全部时间段"):
            try:
                await page.locator(f"text={t} >> visible=true").first.click(timeout=3000)
                await asyncio.sleep(0.5)
            except Exception:
                pass

    await asyncio.sleep(5)


# ---------------- 体检 ----------------
def run_check(save_dir: Path, indices, metrics, today):
    missing = []
    for idx in indices:
        for m in metrics:
            if not already_done(save_dir, idx, m, today):
                missing.append(f"{idx}-{m}")
    total = len(indices) * len(metrics)
    log(f"体检目录: {save_dir}  今日({today})应有 {total} 个组合")
    log(f"CSV 总数: {len(list(save_dir.glob('*.csv')))}")
    if missing:
        log(f"缺失 {len(missing)} 个: {', '.join(missing)}", "WARN")
        miss_idx = sorted({x.split('-')[0] for x in missing}, key=indices.index)
        log(f"待补指数(可直接喂给 --indices): {','.join(miss_idx)}", "WARN")
    else:
        log("全部齐全", "OK")
    return missing


# ---------------- 主流程 ----------------
async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", dest="time_range", default="上市以来")
    ap.add_argument("--out", required=True)
    ap.add_argument("--indices", default="")
    ap.add_argument("--metrics", default=",".join(DEFAULT_METRICS))
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--date", default="", help="判定『已下载』的日期戳 YYYYMMDD，默认今天；跨天续传时传首日日期")
    args = ap.parse_args()

    save_dir = Path(args.out)
    save_dir.mkdir(parents=True, exist_ok=True)
    indices = [s.strip() for s in args.indices.split(",") if s.strip()] or DEFAULT_INDICES
    metrics = [s.strip() for s in args.metrics.split(",") if s.strip()]
    today = args.date.strip() or datetime.now().strftime("%Y%m%d")

    if args.check:
        run_check(save_dir, indices, metrics, today)
        return

    username = os.environ.get("LIXINGER_USER", "").strip()
    password = os.environ.get("LIXINGER_PASS", "").strip()
    if not username or not password:
        log("缺少凭据：请设置环境变量 LIXINGER_USER 与 LIXINGER_PASS", "FAIL")
        sys.exit(2)

    total = len(indices) * len(metrics)
    log(f"任务: {len(indices)} 指数 x {len(metrics)} 指标 = {total} 个文件 | 范围={args.time_range} | 目录={save_dir}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            accept_downloads=True, viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        async def on_download(download):
            try:
                fname = download.suggested_filename
                await download.save_as(save_dir / fname)
                log(f"    已保存: {fname}", "OK")
            except Exception as e:
                log(f"    保存失败: {e}", "FAIL")

        page.on("download", on_download)

        await page.goto(HOME, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        await do_login(page, username, password)
        await asyncio.sleep(2)

        failed, done = [], 0
        for i, index_name in enumerate(indices):
            pending = [m for m in metrics
                       if not (args.skip_existing and already_done(save_dir, index_name, m, today))]
            log(f"\n{'='*55}")
            log(f"[{i+1}/{len(indices)}] {index_name} ({args.time_range})  待下载: {pending or '无(已完成)'}")
            log(f"{'='*55}")
            done += len(metrics) - len(pending)
            if not pending:
                continue

            try:
                await page.goto(HOME, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
                if not await do_search(page, index_name):
                    failed.append(index_name)
                    done += len(pending)
                    continue
                await asyncio.sleep(2)
            except Exception as e:
                log(f"  打开/搜索异常: {e}", "FAIL")
                failed.append(index_name)
                done += len(pending)
                continue

            for metric in pending:
                done += 1
                log(f"  [{done}/{total}] {index_name} - {metric}")
                try:
                    await download_metric(page, metric, args.time_range)
                except Exception as e:
                    log(f"    异常: {e}", "FAIL")

        log(f"\n本批结束。{save_dir} 共 {len(list(save_dir.glob('*.csv')))} 个CSV", "OK")
        if failed:
            log(f"失败指数: {', '.join(failed)}", "WARN")
        run_check(save_dir, indices, metrics, today)

        await context.close()
        await asyncio.sleep(1)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
