"""MediaCrawler 爬虫桥接模块 — 基于 Playwright 浏览器自动化的数据采集。

灵感来源: https://github.com/NanmiCoder/MediaCrawler
技术原理: 利用 Playwright 控制浏览器，通过保留登录态的上下文获取平台数据，
         无需逆向复杂加密算法，无需付费 API Key。

⚠️ 免责声明:
本模块仅供学习和研究目的。使用者必须遵守相关法律法规及各平台的服务条款。
禁止用于商业用途、大规模数据采集或任何非法活动。

Author: Jesse (https://github.com/Jesseovo)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

COOKIE_DIR = Path.home() / ".config" / "last30days-cn" / "browser_cookies"
_playwright_available: Optional[bool] = None


def is_playwright_available() -> bool:
    """检查 Playwright 是否已安装并可用。"""
    global _playwright_available
    if _playwright_available is not None:
        return _playwright_available
    try:
        from playwright.sync_api import sync_playwright
        _playwright_available = True
    except ImportError:
        _playwright_available = False
    return _playwright_available


def _ensure_cookie_dir():
    COOKIE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cookie_path(platform: str) -> Path:
    _ensure_cookie_dir()
    return COOKIE_DIR / f"{platform}_cookies.json"


def save_cookies(platform: str, cookies: list):
    path = _get_cookie_path(platform)
    path.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")


def load_cookies(platform: str) -> Optional[list]:
    path = _get_cookie_path(platform)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", str(text))
    return re.sub(r"\s+", " ", text).strip()


def crawl_weibo(topic: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过浏览器自动化爬取微博搜索结果。"""
    if not is_playwright_available():
        return []

    items = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
                )
                cookies = load_cookies("weibo")
                if cookies:
                    context.add_cookies(cookies)

                page = context.new_page()
                search_url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{topic}&page_type=searchall"
                page.goto(f"https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D{topic}")
                page.wait_for_timeout(2000)

                response = page.evaluate("""
                    async (url) => {
                        const resp = await fetch(url);
                        return await resp.json();
                    }
                """, search_url)

                if isinstance(response, dict):
                    cards = response.get("data", {}).get("cards", [])
                    for card in cards[:limit]:
                        if card.get("card_type") == 9:
                            mblog = card.get("mblog", {})
                            if mblog:
                                items.append(_parse_weibo_mblog(mblog))
                        elif card.get("card_type") == 11:
                            for group in card.get("card_group", []):
                                mblog = group.get("mblog", {})
                                if mblog:
                                    items.append(_parse_weibo_mblog(mblog))

                save_cookies("weibo", context.cookies())
            finally:
                browser.close()
    except Exception as e:
        sys.stderr.write(f"[爬虫-微博] 浏览器爬取失败: {e}\n")
    return items


def _parse_weibo_mblog(mblog: dict) -> Dict[str, Any]:
    text = _clean_html(mblog.get("text", ""))
    user = mblog.get("user", {})
    mid = mblog.get("mid", "") or mblog.get("id", "")

    return {
        "text": text,
        "url": f"https://weibo.com/{user.get('id', '')}/{mid}",
        "author_handle": user.get("screen_name", ""),
        "author_id": str(user.get("id", "")),
        "date": _parse_relative_date(mblog.get("created_at", "")),
        "engagement": {
            "reposts": mblog.get("reposts_count", 0),
            "comments": mblog.get("comments_count", 0),
            "likes": mblog.get("attitudes_count", 0),
        },
        "source": "crawler",
    }


def crawl_xiaohongshu(topic: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过浏览器自动化爬取小红书搜索结果。"""
    if not is_playwright_available():
        return []

    items = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                cookies = load_cookies("xiaohongshu")
                if cookies:
                    context.add_cookies(cookies)

                page = context.new_page()
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={topic}&source=web_search_result_notes"
                page.goto(search_url)
                page.wait_for_timeout(3000)

                note_elements = page.query_selector_all('section.note-item, div[class*="note-item"], a[class*="cover"]')
                for elem in note_elements[:limit]:
                    try:
                        title_el = elem.query_selector('span[class*="title"], div[class*="title"]')
                        title = title_el.inner_text() if title_el else ""
                        link = elem.get_attribute("href") or ""
                        if link and not link.startswith("http"):
                            link = f"https://www.xiaohongshu.com{link}"

                        author_el = elem.query_selector('span[class*="name"], div[class*="author"]')
                        author = author_el.inner_text() if author_el else ""

                        likes_el = elem.query_selector('span[class*="like"], span[class*="count"]')
                        likes_text = likes_el.inner_text() if likes_el else "0"
                        likes = _parse_count(likes_text)

                        items.append({
                            "title": title,
                            "desc": "",
                            "url": link,
                            "author_name": author,
                            "author_id": "",
                            "date": None,
                            "engagement": {
                                "likes": likes,
                                "collects": 0,
                                "comments": 0,
                                "shares": 0,
                            },
                            "hashtags": [],
                            "images": [],
                            "source": "crawler",
                        })
                    except Exception:
                        continue

                save_cookies("xiaohongshu", context.cookies())
            finally:
                browser.close()
    except Exception as e:
        sys.stderr.write(f"[爬虫-小红书] 浏览器爬取失败: {e}\n")
    return items


def crawl_douyin(topic: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过浏览器自动化爬取抖音搜索结果。"""
    if not is_playwright_available():
        return []

    items = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                cookies = load_cookies("douyin")
                if cookies:
                    context.add_cookies(cookies)

                page = context.new_page()
                search_url = f"https://www.douyin.com/search/{topic}?type=video"
                page.goto(search_url)
                page.wait_for_timeout(3000)

                video_elements = page.query_selector_all('div[class*="video-card"], li[class*="search-result"]')
                for elem in video_elements[:limit]:
                    try:
                        title_el = elem.query_selector('a[class*="title"], span[class*="title"], p[class*="desc"]')
                        title = title_el.inner_text() if title_el else ""

                        link_el = elem.query_selector("a[href*='/video/']")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href") or ""
                            if href.startswith("/"):
                                link = f"https://www.douyin.com{href}"
                            else:
                                link = href

                        author_el = elem.query_selector('span[class*="author"], span[class*="nickname"]')
                        author = author_el.inner_text() if author_el else ""

                        likes_el = elem.query_selector('span[class*="like"], span[class*="digg"]')
                        likes = _parse_count(likes_el.inner_text() if likes_el else "0")

                        items.append({
                            "text": title,
                            "url": link,
                            "author_name": author,
                            "author_id": "",
                            "date": None,
                            "engagement": {
                                "views": 0,
                                "likes": likes,
                                "comments": 0,
                                "shares": 0,
                            },
                            "hashtags": [],
                            "duration": 0,
                            "source": "crawler",
                        })
                    except Exception:
                        continue

                save_cookies("douyin", context.cookies())
            finally:
                browser.close()
    except Exception as e:
        sys.stderr.write(f"[爬虫-抖音] 浏览器爬取失败: {e}\n")
    return items


def crawl_bilibili(topic: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过浏览器自动化爬取B站搜索结果。"""
    if not is_playwright_available():
        return []

    items = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )

                page = context.new_page()
                search_url = f"https://search.bilibili.com/all?keyword={topic}&order=totalrank"
                page.goto(search_url)
                page.wait_for_timeout(3000)

                video_elements = page.query_selector_all('div.bili-video-card, div[class*="video-list-item"]')
                for elem in video_elements[:limit]:
                    try:
                        title_el = elem.query_selector('h3[class*="title"], a[class*="title"]')
                        title = _clean_html(title_el.inner_text()) if title_el else ""

                        link_el = elem.query_selector("a[href*='/video/']")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href") or ""
                            if href.startswith("//"):
                                link = f"https:{href}"
                            elif href.startswith("/"):
                                link = f"https://www.bilibili.com{href}"
                            else:
                                link = href

                        author_el = elem.query_selector('span[class*="name"], span.bili-video-card__info--author')
                        author = author_el.inner_text() if author_el else ""

                        views_el = elem.query_selector('span[class*="play"], span[class*="view"]')
                        views = _parse_count(views_el.inner_text() if views_el else "0")

                        items.append({
                            "title": title,
                            "url": link,
                            "bvid": "",
                            "channel_name": author,
                            "author_mid": "",
                            "date": None,
                            "duration": "",
                            "description": "",
                            "engagement": {
                                "views": views,
                                "danmaku": 0,
                                "comments": 0,
                                "favorites": 0,
                                "likes": 0,
                            },
                            "source": "crawler",
                        })
                    except Exception:
                        continue

            finally:
                browser.close()
    except Exception as e:
        sys.stderr.write(f"[爬虫-B站] 浏览器爬取失败: {e}\n")
    return items


def crawl_zhihu(topic: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过浏览器自动化爬取知乎搜索结果。"""
    if not is_playwright_available():
        return []

    items = []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                cookies = load_cookies("zhihu")
                if cookies:
                    context.add_cookies(cookies)

                page = context.new_page()
                search_url = f"https://www.zhihu.com/search?type=content&q={topic}"
                page.goto(search_url)
                page.wait_for_timeout(3000)

                result_elements = page.query_selector_all('div.SearchResult-Card, div[class*="List-item"]')
                for elem in result_elements[:limit]:
                    try:
                        title_el = elem.query_selector('h2[class*="ContentItem-title"], span[class*="Highlight"]')
                        title = _clean_html(title_el.inner_text()) if title_el else ""

                        link_el = elem.query_selector("a[href*='/question/'], a[href*='/p/']")
                        link = ""
                        if link_el:
                            href = link_el.get_attribute("href") or ""
                            if href.startswith("/"):
                                link = f"https://www.zhihu.com{href}"
                            else:
                                link = href

                        excerpt_el = elem.query_selector('span[class*="RichText"], div[class*="RichText"]')
                        excerpt = _clean_html(excerpt_el.inner_text()[:300]) if excerpt_el else ""

                        author_el = elem.query_selector('span[class*="AuthorInfo"] a, a[class*="UserLink"]')
                        author = author_el.inner_text() if author_el else ""

                        voteup_el = elem.query_selector('button[class*="VoteButton"] span, span[class*="vote"]')
                        voteups = _parse_count(voteup_el.inner_text() if voteup_el else "0")

                        items.append({
                            "title": title,
                            "excerpt": excerpt,
                            "url": link,
                            "author": author,
                            "date": None,
                            "content_type": "search_result",
                            "engagement": {
                                "voteups": voteups,
                                "comments": 0,
                                "collects": 0,
                            },
                            "source": "crawler",
                        })
                    except Exception:
                        continue

                save_cookies("zhihu", context.cookies())
            finally:
                browser.close()
    except Exception as e:
        sys.stderr.write(f"[爬虫-知乎] 浏览器爬取失败: {e}\n")
    return items


def _parse_count(text: str) -> int:
    """解析数量文本，支持 '1.2万' / '1.2w' / '12k' 等格式。"""
    if not text:
        return 0
    text = text.strip().replace(",", "")
    try:
        if "万" in text or text.lower().endswith("w"):
            num = float(re.sub(r"[万wW]", "", text))
            return int(num * 10000)
        elif "亿" in text:
            num = float(text.replace("亿", ""))
            return int(num * 100000000)
        elif text.lower().endswith("k"):
            num = float(text[:-1])
            return int(num * 1000)
        return int(float(re.sub(r"[^\d.]", "", text or "0")))
    except (ValueError, TypeError):
        return 0


def _parse_relative_date(date_str: str) -> Optional[str]:
    """解析微博的相对时间格式。"""
    if not date_str:
        return None

    from datetime import timedelta
    now = datetime.now()

    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    if "分钟前" in date_str:
        m = re.search(r"(\d+)", date_str)
        if m:
            return (now - timedelta(minutes=int(m.group(1)))).strftime("%Y-%m-%d")
    if "小时前" in date_str:
        m = re.search(r"(\d+)", date_str)
        if m:
            return (now - timedelta(hours=int(m.group(1)))).strftime("%Y-%m-%d")
    if "昨天" in date_str:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")

    m = re.match(r"(\d{2})-(\d{2})", date_str)
    if m:
        return f"{now.year}-{m.group(1)}-{m.group(2)}"
    return None


def get_crawler_status() -> Dict[str, Any]:
    """获取爬虫引擎的状态信息。"""
    pw_available = is_playwright_available()
    cached_platforms = []

    if COOKIE_DIR.exists():
        for f in COOKIE_DIR.glob("*_cookies.json"):
            platform = f.stem.replace("_cookies", "")
            cached_platforms.append(platform)

    return {
        "playwright_available": pw_available,
        "cached_logins": cached_platforms,
        "cookie_dir": str(COOKIE_DIR),
    }
