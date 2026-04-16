#!/usr/bin/env python3
"""
x-mentions-nitter.py - 通过本地 Nitter 实例抓取 @mentions
纯 HTTP，零浏览器依赖。

用法：
    python3 scripts/x_mentions_nitter.py
    退出码 0 = 无新内容，1 = 有新内容
"""

import sys
import os
import json
from datetime import datetime

_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import nitter_client

USERNAME = os.environ.get("NITTER_USERNAME", "YuLin807")
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "x-mentions-nitter-cache.json")
RESULT_FILE = os.path.join(CACHE_DIR, "x-mentions-nitter-latest.json")


def load_cache():
    """加载已知 tweet IDs"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_cache(ids):
    """保存已知 tweet IDs"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(list(ids)[-500:], f)


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Nitter mentions 检查...")

    # 直接通过 nitter_client 搜索 mentions
    mentions_raw = nitter_client.search_tweets(f"@{USERNAME}", count=30)
    if not mentions_raw:
        print("⚠️ Nitter 无结果（可能实例不可用或无 mentions）")
        sys.exit(0)

    # 转换为 mentions 格式
    mentions = []
    for tw in mentions_raw:
        # 跳过自己的推文
        if tw.get("username", "").lower() == USERNAME.lower():
            continue
        mentions.append({
            "author": tw.get("username", ""),
            "text": tw.get("text", ""),
            "time": tw.get("time", ""),
            "url": tw.get("url", ""),
            "tweet_id": tw.get("tweet_id", ""),
        })

    print(f"📊 解析到 {len(mentions)} 条 mentions")

    # 对比缓存找新的
    cache = load_cache()
    new_mentions = []
    for m in mentions:
        tid = m.get("tweet_id", "")
        if tid and tid not in cache:
            new_mentions.append(m)

    # 更新缓存
    all_ids = cache | {m["tweet_id"] for m in mentions if m.get("tweet_id")}
    save_cache(all_ids)

    # 输出
    output = {
        "timestamp": datetime.now().isoformat(),
        "total": len(mentions),
        "new_count": len(new_mentions),
        "new": new_mentions[:10],
    }

    with open(RESULT_FILE, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False, indent=2))

    if new_mentions:
        print(f"\n⚠️ 发现 {len(new_mentions)} 条新 mentions！")
        sys.exit(1)
    else:
        print(f"\n✅ 无新 mentions")
        sys.exit(0)


if __name__ == "__main__":
    main()
