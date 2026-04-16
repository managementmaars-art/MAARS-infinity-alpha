#!/usr/bin/env python3
from __future__ import annotations
"""
arxiv_author_finder.py — 从 arxiv 论文自动发现作者 X/Twitter 账号

Pipeline（4层级联）：
  Layer 1: arxiv API → 提取作者名 + GitHub URL
  Layer 2: GitHub HTML scraping → twitter_username (zero API token)
  Layer 3: Scholars on Twitter 本地数据集（需预下载）
  Layer 4: 搜索引擎兜底（SearxNG → Brave → DuckDuckGo → Nitter）

Usage:
  python3 arxiv_author_finder.py --arxiv "https://arxiv.org/abs/2603.10165"
  python3 arxiv_author_finder.py --arxiv "2603.10165" --json
  python3 arxiv_author_finder.py --arxiv "2603.10165" --scholars-db /path/to/scholars.csv

环境变量：
  GITHUB_TOKEN — GitHub Personal Access Token（5000次/小时 vs 60次/小时）

可选依赖：
  duckduckgo_search — Layer 4 网络搜索的首选后端（pip install duckduckgo-search）。
                      未安装时自动回退至本地 SearxNG。
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone

from common import (
    http_get, parse_arxiv_id, fetch_arxiv_metadata,
    scrape_github_profile, scrape_repo_contributors, is_github_org,
    extract_twitter_from_profile, normalize_name, match_name_parts,
    match_github_to_author, match_handle_to_author,
    search_web, GITHUB_REPO_RE, TWITTER_URL_RE, TWITTER_SKIP_HANDLES,
)
from config import REQUEST_DELAY


# ─── Layer 1: GitHub search for paper ────────────────────────────────────────

def search_github_for_paper(title: str) -> list[str]:
    """Try to find a GitHub repo URL by searching for the paper title."""
    query = urllib.parse.quote(f'"{title[:80]}"')
    url = f"https://github.com/search?q={query}&type=repositories"
    html = http_get(url, timeout=15)
    repos = []
    if isinstance(html, str):
        repos = re.findall(r'href="(/[^/]+/[^/"]+)"[^>]*data-testid="results-list"', html)
        if not repos:
            repos = re.findall(r'href="/([^/]+/[^/"]+)" data-hydro-click', html)


    return [r if r.startswith('http') else
            f"https://{r}" if 'github.com' in r else
            f"https://github.com/{r}"
            for r in [r.lstrip('/') for r in repos[:3]]]


# ─── Layer 2: GitHub → Twitter ───────────────────────────────────────────────

def find_twitter_via_repo(repo_url: str, authors: list[str]) -> dict[str, str]:
    """Find twitter handles for authors via GitHub repo scraping."""
    m = GITHUB_REPO_RE.match(repo_url.rstrip("/"))
    if not m:
        return {}
    owner, repo = m.group(1), m.group(2)
    results: dict[str, str] = {}

    # 1. Check repo owner's profile
    owner_profile = scrape_github_profile(owner)
    if owner_profile:
        handle = extract_twitter_from_profile(owner_profile)
        if handle:
            matched = match_github_to_author(owner_profile, authors)
            if matched:
                results[matched] = handle

    # 2. If owner is an org, try to match org twitter by handle → author name
    if is_github_org(owner):
        org_handle = owner_profile.get("twitter") if owner_profile else None
        if org_handle:
            matched = match_handle_to_author(org_handle, authors)
            if matched:
                results.setdefault(matched, org_handle)

    # 3. Check contributors from atom feed
    contributors = scrape_repo_contributors(owner, repo)
    for login in contributors[:8]:
        if login == owner:
            continue
        time.sleep(REQUEST_DELAY)
        profile = scrape_github_profile(login)
        if not profile:
            continue
        handle = extract_twitter_from_profile(profile)
        if handle:
            matched = match_github_to_author(profile, authors)
            if matched and matched not in results:
                results[matched] = handle

    return results


def search_github_users_for_author(author_name: str) -> str | None:
    """Find an author's Twitter via GitHub user search (HTML scraping)."""
    parts = author_name.strip().split()
    if len(parts) < 2:
        return None

    query = urllib.parse.quote(author_name)
    url = f"https://github.com/search?q={query}&type=users"
    html = http_get(url, timeout=15)
    if not isinstance(html, str) or len(html) < 1000:
        return None

    logins = re.findall(r'href="/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,37})"[^>]*data-', html)
    if not logins:
        logins = re.findall(r'class="[^"]*"[^>]*href="/([a-zA-Z0-9_-]+)"', html)

    skip = {"search", "features", "pricing", "login", "signup", "orgs", "topics", "settings", "explore"}
    norm_author = normalize_name(author_name)
    author_parts = norm_author.split()

    seen = set()
    for login in logins:
        if login in seen or login.lower() in skip:
            continue
        seen.add(login)
        profile = scrape_github_profile(login)
        if not profile or not profile.get("name"):
            continue
        # Word-boundary match
        if len(author_parts) >= 2 and match_name_parts(author_parts, profile["name"]):
            handle = extract_twitter_from_profile(profile)
            if handle:
                return handle
        if len(seen) >= 3:
            break
    return None


# ─── Layer 3: Scholars on Twitter dataset ────────────────────────────────────

def load_scholars_dataset(csv_path: str) -> dict[str, str]:
    """Load Scholars on Twitter dataset (CSV). Returns {normalized_name: handle}."""
    mapping = {}
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            orig_headers = list(reader.fieldnames or [])
            name_col = next((h for h in orig_headers if "name" in h.lower()), None)
            handle_col = next(
                (h for h in orig_headers if any(k in h.lower() for k in ("twitter", "screen", "handle"))),
                None
            )
            if not name_col or not handle_col:
                print(f"[WARN] Cannot identify name/handle columns in {csv_path}. Headers: {orig_headers}", file=sys.stderr)
                return {}
            for row in reader:
                name = row.get(name_col, "").strip()
                handle = row.get(handle_col, "").strip().lstrip("@")
                if name and handle:
                    mapping[normalize_name(name)] = handle
    except Exception as e:
        print(f"[WARN] Failed to load scholars dataset: {e}", file=sys.stderr)
    return mapping


def lookup_scholars(author: str, dataset: dict[str, str]) -> str | None:
    """Fuzzy match author name in scholars dataset."""
    norm = normalize_name(author)
    if norm in dataset:
        return dataset[norm]

    parts = norm.split()
    if len(parts) == 2:
        reversed_name = f"{parts[1]} {parts[0]}"
        if reversed_name in dataset:
            return dataset[reversed_name]

    if len(parts) >= 2:
        last = parts[-1]
        first_init = parts[0][0] if parts[0] else ""
        for key, handle in dataset.items():
            key_parts = key.split()
            if len(key_parts) >= 2 and key_parts[-1] == last:
                if first_init and key_parts[0].startswith(first_init):
                    return handle

    return None


# ─── Layer 4: Search fallback ────────────────────────────────────────────────

def search_twitter_for_author(author_name: str, affiliation: str = "") -> str | None:
    """Search for an author's X/Twitter account via web search."""
    queries = [
        f'"{author_name}" site:x.com',
        f'"{author_name}" site:twitter.com',
    ]
    if affiliation:
        queries.insert(0, f'"{author_name}" "{affiliation}" site:x.com')

    for query in queries:
        results = search_web(query, max_results=5)
        for r in results:
            url = r.get("url", r.get("href", ""))
            title = r.get("title", r.get("snippet", "")).lower()
            m = TWITTER_URL_RE.search(url)
            if m:
                handle = m.group(1)
                if handle.lower() not in TWITTER_SKIP_HANDLES and not handle.isdigit():
                    if _search_result_matches_author(author_name, title, handle):
                        return handle
        time.sleep(0.3)

    return None


def _search_result_matches_author(author_name: str, result_text: str, handle: str) -> bool:
    """Verify a search result actually belongs to the author."""
    parts = author_name.lower().split()
    if not parts:
        return True
    last = parts[-1]
    first = parts[0] if parts else ""
    combined = result_text.lower() + " " + handle.lower()
    if len(last) >= 3 and last in combined:
        return True
    if len(first) >= 3 and first in combined:
        return True
    return False


# ─── Main finder ─────────────────────────────────────────────────────────────

class ArxivAuthorFinder:
    def __init__(
        self,
        scholars_db: str | None = None,
        skip_search: bool = False,
        verbose: bool = False,
    ):
        self.scholars: dict[str, str] = {}
        if scholars_db and os.path.exists(scholars_db):
            self.scholars = load_scholars_dataset(scholars_db)
            if verbose:
                print(f"[INFO] Loaded {len(self.scholars)} entries from scholars dataset", file=sys.stderr)
        self.skip_search = skip_search
        self.verbose = verbose

    def find_from_github(self, github_url: str) -> dict:
        """
        Find author X/Twitter accounts from a GitHub repo URL.
        Extracts authors from README BibTeX/author section, then searches for X links.
        No ArXiv dependency.
        """
        m = GITHUB_REPO_RE.match(github_url.rstrip("/"))
        if not m:
            raise ValueError(f"Invalid GitHub repo URL: {github_url}")
        owner, repo = m.group(1), m.group(2)

        if self.verbose:
            print(f"[INFO] Fetching GitHub repo: {github_url}", file=sys.stderr)

        # Fetch README
        readme_text = None
        for branch in ["main", "master", "HEAD"]:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            readme_text = http_get(url, timeout=15)
            if isinstance(readme_text, str) and len(readme_text) > 50:
                break
            readme_text = None

        if not readme_text:
            raise RuntimeError(f"Cannot fetch README from {github_url}")

        # Extract title
        title = repo.replace("-", " ").replace("_", " ")
        # Try PDF filename
        pdf_m = re.search(r'\[(?:\*{0,2})(?:Paper|paper|PDF|pdf)(?:\*{0,2})\]\(([^)]+\.pdf)\)', readme_text)
        if pdf_m:
            pdf_name = pdf_m.group(1).rsplit('/', 1)[-1]
            pdf_name = re.sub(r'\.pdf$', '', pdf_name)
            pdf_title = re.sub(r'\s+', ' ', pdf_name.replace('_', ' ').replace('-', ' ').strip())
            if len(pdf_title) > 15:
                title = pdf_title
        # Try H1 title
        title_m = re.search(r'^#\s+(.+)', readme_text, re.MULTILINE)
        if title_m:
            raw_title = re.sub(r'[\*\[\]`]', '', title_m.group(1)).strip()
            if ':' in raw_title:
                full_part = raw_title.split(':', 1)[1].strip()
                if len(full_part) > 10:
                    title = full_part
            elif len(raw_title) > 5:
                title = raw_title

        # Extract authors from BibTeX
        authors = []
        bib_m = re.search(r'author\s*=\s*\{([^}]+)\}', readme_text)
        if bib_m:
            raw = bib_m.group(1).replace('\n', ' ')
            authors = [a.strip().rstrip(',') for a in raw.split(' and ') if a.strip() and len(a.strip()) > 2][:15]
            authors = [' '.join(reversed(a.split(', '))) if ', ' in a else a for a in authors]
        # Fallback: Authors: line
        if not authors:
            author_m = re.search(r'Authors?\s*[:\-]\s*([^\n]+)', readme_text, re.IGNORECASE)
            if author_m:
                raw = re.sub(r'[\*\[\]`]', '', author_m.group(1)).strip()
                authors = [a.strip() for a in re.split(r'[,;·•]', raw) if a.strip() and len(a.strip()) > 2][:15]

        if not authors:
            raise RuntimeError(f"Cannot extract authors from {github_url} README")

        if self.verbose:
            print(f"[INFO] Paper: {title[:60]}", file=sys.stderr)
            print(f"[INFO] Authors ({len(authors)}): {', '.join(authors)}", file=sys.stderr)

        # Check for ArXiv ID in README (optional, for metadata enrichment)
        arxiv_id = None
        arxiv_m = re.search(r'arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})', readme_text)
        if arxiv_m:
            arxiv_id = arxiv_m.group(1)

        paper = {
            "title": title,
            "authors": authors,
            "github_urls": [github_url],
            "arxiv_id": arxiv_id,
        }

        # Now run the same X-finding pipeline
        return self._find_twitter_for_paper(paper)

    def find(self, arxiv_url_or_id: str) -> dict:
        """
        Returns:
        {
          "paper": { title, authors, arxiv_url, github_urls },
          "results": { author_name: { "handle": str|None, "source": str, "confidence": str } },
          "summary": { found: int, total: int, coverage_pct: float }
        }
        """
        arxiv_id = parse_arxiv_id(arxiv_url_or_id)
        if not arxiv_id:
            raise ValueError(f"Cannot parse arxiv ID from: {arxiv_url_or_id!r}")

        if self.verbose:
            print(f"[INFO] Fetching arxiv:{arxiv_id} ...", file=sys.stderr)
        paper = fetch_arxiv_metadata(arxiv_id)
        if not paper:
            raise RuntimeError(f"Failed to fetch arxiv metadata for {arxiv_id}")

        authors = paper["authors"]
        github_urls = paper["github_urls"]
        paper["arxiv_id"] = arxiv_id

        if self.verbose:
            print(f"[INFO] Paper: {paper['title'][:60]}", file=sys.stderr)
            print(f"[INFO] Authors ({len(authors)}): {', '.join(authors)}", file=sys.stderr)
            print(f"[INFO] GitHub URLs found: {github_urls}", file=sys.stderr)

        return self._find_twitter_for_paper(paper)

    def _find_twitter_for_paper(self, paper: dict) -> dict:
        """Common pipeline: given paper dict with title/authors/github_urls, find X accounts."""
        authors = paper["authors"]
        github_urls = paper.get("github_urls", [])
        arxiv_id = paper.get("arxiv_id")

        results: dict[str, dict] = {a: {"handle": None, "url": None, "source": None, "confidence": None} for a in authors}

        # Layer 1: GitHub via repo URLs
        if github_urls:
            for repo_url in github_urls:
                found = find_twitter_via_repo(repo_url, authors)
                for author, handle in found.items():
                    if results[author]["handle"] is None:
                        results[author] = {"handle": handle, "url": f"https://x.com/{handle}", "source": "github_repo", "confidence": "high"}
                        if self.verbose:
                            print(f"  [GitHub] {author} -> @{handle}", file=sys.stderr)
        else:
            if self.verbose:
                print("[INFO] No GitHub URL in paper, trying search...", file=sys.stderr)
            found_repos = search_github_for_paper(paper["title"])
            for repo_url in found_repos[:2]:
                found = find_twitter_via_repo(repo_url, authors)
                for author, handle in found.items():
                    if results[author]["handle"] is None:
                        results[author] = {"handle": handle, "url": f"https://x.com/{handle}", "source": "github_search", "confidence": "medium"}
                        if self.verbose:
                            print(f"  [GitHub/search] {author} -> @{handle}", file=sys.stderr)

        # Layer 1b: GitHub user search
        missing = [a for a, v in results.items() if v["handle"] is None]
        for author in missing[:8]:
            time.sleep(1)
            handle = search_github_users_for_author(author)
            if handle:
                results[author] = {"handle": handle, "url": f"https://x.com/{handle}", "source": "github_user_search", "confidence": "medium"}
                if self.verbose:
                    print(f"  [GitHub/user] {author} -> @{handle}", file=sys.stderr)

        # Layer 2: Scholars on Twitter dataset
        missing = [a for a, v in results.items() if v["handle"] is None]
        for author in missing:
            handle = lookup_scholars(author, self.scholars)
            if handle:
                results[author] = {"handle": handle, "url": f"https://x.com/{handle}", "source": "scholars_dataset", "confidence": "high"}
                if self.verbose:
                    print(f"  [Scholars] {author} -> @{handle}", file=sys.stderr)

        # Layer 3: Search fallback
        if not self.skip_search:
            missing = [a for a, v in results.items() if v["handle"] is None]
            for author in missing:
                handle = search_twitter_for_author(author)
                if handle:
                    results[author] = {"handle": handle, "url": f"https://x.com/{handle}", "source": "web_search", "confidence": "low"}
                    if self.verbose:
                        print(f"  [Search] {author} -> @{handle}", file=sys.stderr)

        # Summary
        found_count = sum(1 for v in results.values() if v["handle"])
        total = len(authors)
        coverage = found_count / total * 100 if total > 0 else 0

        arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None

        return {
            "paper": {
                "title": paper["title"],
                "arxiv_id": arxiv_id,
                "arxiv_url": arxiv_url,
                "authors": authors,
                "github_urls": github_urls,
            },
            "results": results,
            "summary": {
                "found": found_count,
                "total": total,
                "coverage_pct": round(coverage, 1),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Discover X/Twitter accounts of paper authors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 arxiv_author_finder.py --arxiv 2603.10165
  python3 arxiv_author_finder.py --arxiv https://arxiv.org/abs/1706.03762 --json
  python3 arxiv_author_finder.py --github https://github.com/EverMind-AI/MSA -v
  python3 arxiv_author_finder.py --arxiv 2603.10165 --scholars-db scholars.csv
        """
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--arxiv", "-a", help="arxiv ID or URL (e.g. 2603.10165)")
    source.add_argument("--github", "-g", help="GitHub repo URL (e.g. https://github.com/EverMind-AI/MSA)")
    parser.add_argument("--scholars-db", "-s", help="Path to Scholars on Twitter CSV dataset")
    parser.add_argument("--skip-search", action="store_true", help="Skip web search fallback (faster, less coverage)")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    args = parser.parse_args()

    finder = ArxivAuthorFinder(
        scholars_db=args.scholars_db,
        skip_search=args.skip_search,
        verbose=args.verbose,
    )

    try:
        if args.github:
            output = finder.find_from_github(args.github)
        else:
            output = finder.find(args.arxiv)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    paper = output["paper"]
    results = output["results"]
    summary = output["summary"]

    print(f"\n  Paper: {paper['title']}")
    if paper.get("arxiv_url"):
        print(f"  arxiv: {paper['arxiv_url']}")
    if paper.get("github_urls"):
        print(f"  GitHub: {', '.join(paper['github_urls'])}")
    print()
    print(f"  {'Author':<30} {'Twitter':<40} {'Source':<20} {'Confidence'}")
    print("  " + "-" * 100)
    for author, info in results.items():
        twitter = info["url"] if info["url"] else "-"
        source = info["source"] or ""
        conf = info["confidence"] or ""
        print(f"  {author:<30} {twitter:<40} {source:<20} {conf}")
    print()
    print(f"  Coverage: {summary['found']}/{summary['total']} authors ({summary['coverage_pct']}%)")
    print()


if __name__ == "__main__":
    main()
