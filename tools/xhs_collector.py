#!/usr/bin/env python3
"""
小红书博主采集器（Playwright 浏览器登录态）

用法：
  1. 首次使用先安装依赖：
       pip install playwright
       playwright install chromium

  2. 第一次运行会弹出浏览器，手动扫码登录小红书，然后回车继续：
       python3 xhs_collector.py --user-id 61716aad000000000201caae --out ./raw/xhs

  3. 之后再运行会复用登录态（保存在 ./.xhs_user_data/）。

输出：
  ./raw/xhs/
    profile.json         # 博主基本信息
    notes/{note_id}.json # 每条笔记的标题/正文/标签/互动数
    notes_index.md       # 索引，便于 colleague-skill 直接 Read

参数：
  --user-id   博主 user_id（profile URL 末段）
  --out       输出目录
  --max       最多采集多少条（默认 50）
  --headful   显示浏览器窗口（默认显示，第一次必须）
"""

import argparse
import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

PROFILE_URL = "https://www.xiaohongshu.com/user/profile/{uid}"
USER_DATA_DIR = Path(".xhs_user_data").resolve()


def _extract_note_id(href: str) -> str | None:
    patterns = [
        r"/explore/([A-Za-z0-9]+)",
        r"/discovery/item/([A-Za-z0-9]+)",
    ]
    for p in patterns:
        m = re.search(p, href)
        if m:
            return m.group(1)
    return None


async def collect(user_id: str, out_dir: Path, max_notes: int, headful: bool):
    out_dir.mkdir(parents=True, exist_ok=True)
    notes_dir = out_dir / "notes"
    notes_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=not headful,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await ctx.new_page()
        await page.goto(PROFILE_URL.format(uid=user_id), wait_until="domcontentloaded")

        # 检测登录
        await page.wait_for_timeout(3000)
        if await page.locator("text=登录").count() > 0 and await page.locator(".user-info").count() == 0:
            print("⚠️  未登录。请在弹出的浏览器中扫码登录小红书，登录完成后回到终端按回车继续...")
            input()
            await page.goto(PROFILE_URL.format(uid=user_id), wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

        # 抓取博主信息
        profile = await page.evaluate("""() => {
            const name = document.querySelector('.user-name, .nickname')?.innerText || '';
            const desc = document.querySelector('.user-desc, .desc')?.innerText || '';
            const stats = [...document.querySelectorAll('.user-interactions .count, .data-info .count')]
                .map(e => e.innerText);
            return { name, desc, stats };
        }""")
        profile["user_id"] = user_id
        (out_dir / "profile.json").write_text(
            json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✅ 博主：{profile.get('name')}  {profile.get('stats')}")

        # 滚动加载笔记列表
        seen = set()
        last_count = 0
        stagnate = 0
        while len(seen) < max_notes and stagnate < 5:
            try:
                hrefs = await page.evaluate("""() => {
                    const links = [...document.querySelectorAll('a[href]')]
                        .map(a => a.getAttribute('href'))
                        .filter(Boolean);
                    return links.filter(h =>
                        h.includes('/explore/') || h.includes('/discovery/item/')
                    );
                }""")
            except Exception:
                # 页面可能发生重定向，短暂等待后继续
                await page.wait_for_timeout(1000)
                continue

            for h in hrefs:
                nid = _extract_note_id(h)
                if nid:
                    seen.add((nid, h))
            if len(seen) == last_count:
                stagnate += 1
            else:
                stagnate = 0
                last_count = len(seen)
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1200)

        note_list = list(seen)[:max_notes]
        if not note_list:
            print("⚠️ 未抓到笔记链接，可能是页面结构变化或内容未加载完成。")
        print(f"📄 发现 {len(note_list)} 条笔记，开始抓取详情...")

        index_lines = [f"# {profile.get('name','')} 的小红书笔记\n"]
        for i, (nid, href) in enumerate(note_list, 1):
            url = href if href.startswith("http") else f"https://www.xiaohongshu.com{href}"
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
                data = await page.evaluate("""() => {
                    const title = document.querySelector('#detail-title, .title')?.innerText || '';
                    const content = document.querySelector('#detail-desc, .desc, .content')?.innerText || '';
                    const tags = [...document.querySelectorAll('.tag, a.tag')].map(e => e.innerText);
                    const time = document.querySelector('.date, .publish-date')?.innerText || '';
                    const likes = document.querySelector('.like-wrapper .count, .like-active .count')?.innerText || '';
                    const comments = [...document.querySelectorAll('.comment-item .content, .parent-comment .content')]
                        .slice(0, 20).map(e => e.innerText);
                    return { title, content, tags, time, likes, comments };
                }""")
                data["note_id"] = nid
                data["url"] = url
                (notes_dir / f"{nid}.json").write_text(
                    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                index_lines.append(
                    f"## {i}. {data.get('title') or '(无标题)'}\n"
                    f"- 时间: {data.get('time')}  点赞: {data.get('likes')}\n"
                    f"- 标签: {' '.join(data.get('tags', []))}\n"
                    f"- 链接: {url}\n\n{data.get('content','')}\n"
                )
                print(f"  [{i}/{len(note_list)}] {data.get('title','')[:30]}")
            except Exception as e:
                print(f"  [{i}] 失败: {e}")

        (out_dir / "notes_index.md").write_text("\n".join(index_lines), encoding="utf-8")
        await ctx.close()
        print(f"\n🎉 完成。输出目录：{out_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user-id", required=True)
    ap.add_argument("--out", default="./raw/xhs")
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--headful", action="store_true", default=True)
    args = ap.parse_args()
    asyncio.run(collect(args.user_id, Path(args.out), args.max, args.headful))


if __name__ == "__main__":
    main()
