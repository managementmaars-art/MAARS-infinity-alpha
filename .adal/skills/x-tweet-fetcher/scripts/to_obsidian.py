#!/usr/bin/env python3
"""
to_obsidian.py - 把 X/Twitter 推文保存为 Obsidian Markdown

支持两种输入：
  A) HTML（推荐，格式完整，图片位置准确）
  B) fetch_tweet.py JSON（纯文本，格式丢失）

用法：
  # 方式A：HTML（推荐）
  python3 to_obsidian.py \
    --html /tmp/tweet_article.html \
    --tweet-url "https://x.com/yanhua1010/status/xxx" \
    --username yanhua1010 \
    --date 2026-03-04 \
    --output ~/Obsidian/导入文档/

  # 方式B：直接传URL（纯文本，无格式）
  python3 to_obsidian.py \
    --url "https://x.com/user/status/123" \
    --output ~/Obsidian/导入文档/

"""

import json
import os
import re
import sys
import argparse
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser


LONGFORM_TYPE_MAP = {
    'unstyled': 'p',
    'header-one': 'h1',
    'header-two': 'h2',
    'header-three': 'h3',
    'code-block': 'code',
    'blockquote': 'quote',
    'ordered-list-item': 'ol',
    'unordered-list-item': 'ul',
    'header-four': 'h4',
    'header-five': 'h5',
    'header-six': 'h6',
    'pre': 'code',
    'atomic': 'atomic',
}

TRAILER_PATTERNS = [
    r'Want to publish your own Article\?',
    r'Upgrade to Premium',
    r'\d+:\d+ [AP]M\s*[·•]\s*\w+ \d+, \d{4}',
    r'Read \d+ repl',
]


# 代码行检测模式
CODE_LINE_PATTERNS = [
    r'^(if|def|class|for|while|import|from|return|print|async|await|try|except|finally|with|as|yield|raise|pass|break|continue|lambda)\s+',
    r'^\s*(if|def|class|for|while|import|from|return|print|async|await|try|except|finally|with|as|yield|raise|pass|break|continue|lambda)\s+',
    r'^\s*#.*',  # 注释行
    r'^\s*""".*"""$',  # docstring 单行
    r"^\s*'''.*'''$",  # docstring 单行
    r'^\s*=>',  # arrow function
    r'^\s*->',  # return type hint
    r'^\s*\]',  # list end (likely from array)
    r'^\s*\)',  # parenthesis close
    r'^\s*\"',  # string start
    r"^\s*'",  # string start
    r'^\s*\{',  # object start
    r'^\s*\}',  # object end
    r'\[\s*$',  # array start
    r'\(\s*$',  # function call open
]


def _is_code_line(line):
    """检测一行是否为代码"""
    line_stripped = line.strip()
    # 空行不中断代码块，但也不是代码行
    if not line_stripped:
        return None  # 返回 None 表示空行，不中断代码块
    # 检测是否是代码行
    for pattern in CODE_LINE_PATTERNS:
        if re.match(pattern, line_stripped):
            return True
    # 检测缩进 + 特定符号（可能是代码 continuation）
    if line.startswith('    ') or line.startswith('\t'):
        if any(c in line_stripped for c in '(){}[]=:,"\'-'):
            return True
    # 检测包含函数调用或数组开头的行（如 propose_variants([ / fn( )
    if '(' in line_stripped or '[' in line_stripped:
        if not line_stripped.startswith('#') and not line_stripped.startswith('http'):
            # 排除中文句子（常见于中文推文）
            if not any('\u4e00' <= c <= '\u9fff' for c in line_stripped):
                return True
    # 检测包含 = 的赋值语句
    if '=' in line_stripped and not '==' in line_stripped:
        if any(kw in line_stripped for kw in ['==', '!=', '<=', '>=', '=>']):
            pass  # 比较运算符，交给上面的模式
        elif not line_stripped.startswith('#') and not line_stripped.startswith('http') and len(line_stripped) < 100:
            # 排除中文
            if not any('\u4e00' <= c <= '\u9fff' for c in line_stripped):
                return True
    return False


def _detect_and_wrap_code_blocks(text):
    """检测纯文本中的代码模式并包裹成代码块"""
    lines = text.split('\n')
    result = []
    i = 0
    in_code_block = False
    code_lang = None

    while i < len(lines):
        line = lines[i]
        is_code = _is_code_line(line)

        # 空行不中断代码块
        if is_code is None:
            if in_code_block:
                result.append(line)  # 保留空行在代码块内
            else:
                result.append(line)
            i += 1
            continue

        # 检测是否为代码行
        if is_code:
            if not in_code_block:
                # 开始新的代码块
                code_lang = _detect_code_language(lines, i)
                result.append(f'```{code_lang}\n')
                in_code_block = True
            result.append(line)
        else:
            if in_code_block:
                # 代码块结束
                result.append('```\n')
                in_code_block = False
            result.append(line)
        i += 1

    # 如果代码块未闭合，关闭它
    if in_code_block:
        result.append('```')

    return '\n'.join(result)


def _detect_code_language(lines, start_idx):
    """尝试检测代码语言"""
    # 向前看几行来检测语言
    for i in range(start_idx, min(start_idx + 5, len(lines))):
        line = lines[i]
        if 'import ' in line or 'from ' in line:
            return 'python'
        if 'function ' in line or 'const ' in line or 'let ' in line or 'var ' in line:
            return 'javascript'
        if '{' in line and ':' in line and '}' not in line[:line.index(':')]:
            return 'json'
        if '<html' in line.lower() or '<div' in line.lower():
            return 'html'
    return ''


def sanitize_filename(text, max_len=50):
    text = re.sub(r'[^\w\u4e00-\u9fff\-\s]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text[:max_len]


def parse_date(created_at):
    if not created_at:
        return datetime.now().strftime('%Y-%m-%d')
    try:
        dt = datetime.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')


def get_image_filename(url):
    name_match = re.search(r'/media/([A-Za-z0-9_\-]+)\?format=(\w+)', url)
    if name_match:
        return f'{name_match.group(1)}.{name_match.group(2)}'
    path = urlparse(url).path
    name = os.path.basename(path).split(':')[0]
    if '.' not in name:
        name += '.jpg'
    return name


def download_image(url, assets_dir):
    filename = get_image_filename(url)
    dest = assets_dir / filename
    if dest.exists():
        print(f'  ⏭️  已存在：{filename}')
        return filename
    try:
        fetch_url = re.sub(r'name=\w+', 'name=orig', url)
        req = urllib.request.Request(fetch_url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                          'Version/18.3 Safari/605.1.15'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            dest.write_bytes(resp.read())
        print(f'  ✅ 下载图片：{filename}')
        return filename
    except Exception as e:
        print(f'  ⚠️  图片下载失败 {url}：{e}')
        return None


def clean_trailing_junk(text):
    for pattern in TRAILER_PATTERNS:
        m = re.search(pattern, text)
        if m:
            text = text[:m.start()].rstrip()
    return text


def _apply_inline_styles(text, ranges):
    if not text:
        return ''
    chars = list(text)
    starts = {}
    ends = {}
    style_map = {
        'Bold': ('**', '**'),
        'Italic': ('*', '*'),
        'Strikethrough': ('~~', '~~'),
        'Code': ('`', '`'),
    }
    for r in ranges or []:
        style = r.get('style')
        if style not in style_map:
            continue
        start = r.get('offset', 0)
        end = start + r.get('length', 0)
        if start < 0 or end > len(chars) or start >= end:
            continue
        open_tok, close_tok = style_map[style]
        starts.setdefault(start, []).append((end - start, open_tok))
        ends.setdefault(end, []).append((end - start, close_tok))

    out = []
    for i in range(len(chars) + 1):
        if i in ends:
            for _, tok in sorted(ends[i], key=lambda x: x[0]):
                out.append(tok)
        if i in starts:
            for _, tok in sorted(starts[i], key=lambda x: -x[0]):
                out.append(tok)
        if i < len(chars):
            out.append(chars[i])
    return ''.join(out)


def _fx_article_to_markdown(article, local_images=None):
    content = (article or {}).get('content', {}) or {}
    blocks = content.get('blocks', []) or []
    if not blocks:
        return article.get('full_text', '')

    local_images = local_images or {}
    entity_map_raw = content.get('entityMap', []) or []
    entity_map = {}
    if isinstance(entity_map_raw, list):
        for item in entity_map_raw:
            try:
                entity_map[int(item.get('key'))] = item.get('value', {})
            except Exception:
                continue
    elif isinstance(entity_map_raw, dict):
        for k, v in entity_map_raw.items():
            try:
                entity_map[int(k)] = v
            except Exception:
                continue

    parts = []
    list_state = None
    ol_counter = 0
    for block in blocks:
        raw_text = (block.get('text') or '').rstrip('\n')
        text = _apply_inline_styles(raw_text, block.get('inlineStyleRanges', []))
        btype = block.get('type', 'unstyled')

        if btype == 'atomic':
            if list_state is not None:
                parts.append('')
                list_state = None
                ol_counter = 0
            for er in block.get('entityRanges', []) or []:
                ent = entity_map.get(er.get('key')) or {}
                ent_type = ent.get('type')
                
                # 处理 MEDIA 类型（图片等）
                if ent_type == 'MEDIA':
                    media_items = (((ent.get('data') or {}).get('mediaItems')) or [])
                    if not media_items:
                        continue
                    media_id = media_items[0].get('mediaId')
                    local_name = local_images.get(str(media_id)) or local_images.get(media_id)
                    if local_name:
                        parts.append(f'![图片](assets/{local_name})')
                
                # 处理 MARKDOWN 类型（代码块等）
                elif ent_type == 'MARKDOWN':
                    markdown_data = ent.get('data', {})
                    markdown_content = markdown_data.get('markdown', '')
                    if markdown_content:
                        parts.append(markdown_content)
                
                # 处理 LINK 类型
                elif ent_type == 'LINK':
                    link_data = ent.get('data', {})
                    link_url = link_data.get('url', '')
                    if link_url:
                        parts.append(link_url)
            continue

        if btype in ('unordered-list-item', 'ordered-list-item'):
            if list_state != btype:
                parts.append('')
                ol_counter = 0
                list_state = btype
            if btype == 'unordered-list-item':
                for line in text.split('\n'):
                    parts.append(f'- {line}' if line.strip() else '-')
            else:
                ol_counter += 1
                for idx, line in enumerate(text.split('\n')):
                    prefix = f'{ol_counter}. ' if idx == 0 else '   '
                    parts.append(f'{prefix}{line}')
            continue
        else:
            if list_state is not None:
                parts.append('')
                list_state = None
                ol_counter = 0

        if btype == 'header-one':
            parts.append(f'# {text}')
        elif btype == 'header-two':
            parts.append(f'## {text}')
        elif btype == 'header-three':
            parts.append(f'### {text}')
        elif btype == 'header-four':
            parts.append(f'#### {text}')
        elif btype == 'header-five':
            parts.append(f'##### {text}')
        elif btype == 'header-six':
            parts.append(f'###### {text}')
        elif btype == 'blockquote':
            # text 已经是应用了 inline styles 的结果，直接加 > 前缀
            for line in text.split('\n'):
                parts.append(f'> {line}' if line.strip() else '>')
        elif btype in ('code-block', 'pre'):
            parts.append(f'```\n{text}\n```')
        else:
            parts.append(text)

    return '\n\n'.join(p for p in parts if p is not None).strip()


def _classify_longform(cls):
    m = re.search(r'longform-([a-z\-]+)', cls)
    if not m:
        return None, None
    suffix = m.group(1)
    block_type = LONGFORM_TYPE_MAP.get(suffix)
    if block_type is None:
        return 'p', suffix
    return block_type, None


class XArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.unknown_types = set()
        self._cur_block_type = None
        self._cur_tokens = []
        self._bold_depth = 0
        self._seen_img_urls = set()
        self._cur_link_href = None
        self._cur_link_tokens = []
        self._in_md_code_block = False
        self._md_code_lang = None
        self._md_code_lang_done = False
        self._md_code_tokens = []
        self._in_copy_button = False
        self._md_code_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        style = attrs_dict.get('style', '')
        testid = attrs_dict.get('data-testid', '')

        if testid == 'markdown-code-block':
            self._flush_block()
            self._in_md_code_block = True
            self._md_code_lang = None
            self._md_code_lang_done = False
            self._md_code_tokens = []
            self._in_copy_button = False
            self._md_code_depth = 1
            return

        if self._in_md_code_block:
            if tag == 'div':
                self._md_code_depth += 1
            if tag == 'button' and attrs_dict.get('aria-label', '') == 'Copy to clipboard':
                self._in_copy_button = True
            return

        block_type, unknown_suffix = _classify_longform(cls)
        if block_type is not None:
            self._flush_block()
            self._cur_block_type = block_type
            self._cur_tokens = []
            if unknown_suffix:
                self.unknown_types.add(unknown_suffix)
        elif tag in ('h1', 'h2', 'h3') and not self._cur_block_type:
            self._flush_block()
            self._cur_block_type = tag
            self._cur_tokens = []

        if tag == 'span' and self._cur_block_type != 'code':
            if ('font-weight: bold' in style or 'font-weight:bold' in style or 'font-weight:700' in style):
                self._bold_depth += 1

        if tag == 'a':
            href = attrs_dict.get('href', '')
            if href.startswith('http') and 'rel' in attrs_dict:
                self._cur_link_href = href
                self._cur_link_tokens = []
            return

        if tag == 'img':
            src = attrs_dict.get('src', '')
            if 'pbs.twimg.com/media' in src and src not in self._seen_img_urls:
                self._seen_img_urls.add(src)
                self._flush_block()
                self.blocks.append(('img', src))

    def handle_endtag(self, tag):
        if tag == 'a' and self._cur_link_href:
            link_text = ''.join(self._cur_link_tokens).strip()
            href = self._cur_link_href
            if link_text and self._cur_block_type:
                if link_text == href:
                    self._cur_tokens.append(f'\n{href}\n')
                else:
                    self._cur_tokens.append(f'\n[{link_text}]({href})\n')
            self._cur_link_href = None
            self._cur_link_tokens = []
            return

        if self._in_md_code_block:
            if tag == 'button':
                self._in_copy_button = False
            if tag == 'div':
                self._md_code_depth -= 1
                if self._md_code_depth <= 0:
                    code = ''.join(self._md_code_tokens)
                    code = code.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<').replace('&quot;', '"')
                    if code.strip():
                        lang = self._md_code_lang or ''
                        self.blocks.append(('code', code.strip(), lang))
                    self._in_md_code_block = False
            return

        if tag == 'span' and self._bold_depth > 0:
            self._bold_depth -= 1

    def handle_data(self, data):
        if self._in_md_code_block:
            if self._in_copy_button:
                return
            if not self._md_code_lang_done:
                if data.strip():
                    self._md_code_lang = data.strip()
                    self._md_code_lang_done = True
            else:
                self._md_code_tokens.append(data)
            return

        if not self._cur_block_type:
            return
        if self._cur_block_type == 'code':
            self._cur_tokens.append(data)
        elif data.strip():
            token = f'**{data}**' if self._bold_depth > 0 else data
            if self._cur_link_href is not None:
                self._cur_link_tokens.append(data)
            else:
                self._cur_tokens.append(token)

    def _flush_block(self):
        if self._cur_block_type and self._cur_tokens:
            text = ''.join(self._cur_tokens)
            if self._cur_block_type != 'code':
                text = text.strip()
            if text:
                self.blocks.append((self._cur_block_type, text))
        self._cur_block_type = None
        self._cur_tokens = []
        self._bold_depth = 0

    def close(self):
        self._flush_block()
        super().close()


def _blocks_to_markdown(blocks, img_local):
    parts = []
    prev_kind = None
    ol_counter = 0
    for block in blocks:
        kind = block[0]
        content = block[1]
        lang = block[2] if len(block) > 2 else ''

        if kind in ('ul', 'ol'):
            if prev_kind not in ('ul', 'ol'):
                parts.append('')
            if kind == 'ul':
                parts.append(f'- {content}')
            else:
                ol_counter += 1
                parts.append(f'{ol_counter}. {content}')
        else:
            if prev_kind in ('ul', 'ol'):
                parts.append('')
                ol_counter = 0
            if kind == 'h1':
                parts.append(f'\n# {content}\n')
            elif kind == 'h2':
                parts.append(f'\n## {content}\n')
            elif kind == 'h3':
                parts.append(f'\n### {content}\n')
            elif kind == 'h4':
                parts.append(f'\n#### {content}\n')
            elif kind == 'h5':
                parts.append(f'\n##### {content}\n')
            elif kind == 'h6':
                parts.append(f'\n###### {content}\n')
            elif kind == 'p':
                parts.append(content)
            elif kind == 'code':
                fence = f'```{lang}' if lang else '```'
                parts.append(f'\n{fence}\n{content.strip()}\n```\n')
            elif kind == 'quote':
                parts.append(f'> {content}')
            elif kind == 'atomic':
                pass
            elif kind == 'img':
                local = img_local.get(content)
                if local:
                    parts.append(f'\n![图片](assets/{local})\n')
        prev_kind = kind
    return '\n'.join(parts)


def extract_cover_image(html):
    header_img = re.search(
        r'data-testid="twitterArticleHeaderImage"[^>]*>.*?'
        r'src="(https://pbs\.twimg\.com/media/[^"]+)"',
        html, re.DOTALL
    )
    if header_img:
        return header_img.group(1)
    rich_idx = html.find('twitterArticleRichTextView')
    if rich_idx < 0:
        return None
    header_html = html[:rich_idx]
    imgs = re.findall(r'https://pbs\.twimg\.com/media/([A-Za-z0-9_\-]+)\?format=(\w+)', header_html)
    if imgs:
        name, fmt = imgs[0]
        return f'https://pbs.twimg.com/media/{name}?format={fmt}&name=small'
    return None


def extract_article_title(html_content):
    m = re.search(r'data-testid="twitter-article-title"[^>]*>(?:<[^>]+>)*([^<]{2,})', html_content)
    if m:
        return m.group(1).strip()
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html_content)
    if m:
        return m.group(1).strip()
    m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']', html_content)
    if m:
        return m.group(1).strip()
    m = re.search(r'<title[^>]*>([^<]+)</title>', html_content)
    if m:
        t = m.group(1).strip()
        t = re.sub(r'\s*[/|]\s*X\s*$', '', t)
        t = re.sub(r'\s+on X\s*$', '', t)
        return t.strip()
    return None


def html_to_markdown(html_content, assets_dir, url, username, date_str, tags_line=None):
    assets_dir.mkdir(parents=True, exist_ok=True)
    cover_url = extract_cover_image(html_content)
    cover_local = download_image(cover_url, assets_dir) if cover_url else None

    rich_idx = html_content.find('data-testid="twitterArticleRichTextView"')
    article_html = html_content if rich_idx < 0 else html_content[rich_idx:]

    parser = XArticleParser()
    parser.feed(article_html)
    parser.close()

    for t in sorted(parser.unknown_types):
        print(f'⚠️ 未知 block 类型：longform-{t}（已降级为段落，请报告以便补充映射）')

    img_local = {}
    for block in parser.blocks:
        if block[0] == 'img':
            local = download_image(block[1], assets_dir)
            if local:
                img_local[block[1]] = local

    title = extract_article_title(html_content)
    if not title:
        for block in parser.blocks:
            if block[0] in ('h1', 'h2'):
                title = block[1]
                break
    if not title:
        for block in parser.blocks:
            if block[0] == 'p':
                title = block[1][:60]
                break
    if not title:
        title = f'X @{username} {date_str}'
    print(f'📌 文章标题：{title}')

    body_md = clean_trailing_junk(_blocks_to_markdown(parser.blocks, img_local))

    parts = []
    if cover_local:
        parts.append(f'![封面图](assets/{cover_local})\n')
    parts.append(f'> 来源：X @{username} | {date_str}')
    parts.append(f'> 链接：{url}')
    if tags_line:
        parts.append(f'{tags_line}\n')
    parts.append(body_md)
    return title, '\n'.join(parts)


def collect_images_from_json(tweet_data):
    images = []
    tweet = tweet_data.get('tweet', {})
    for img in tweet.get('photos', []) or []:
        url = img if isinstance(img, str) else img.get('url', '')
        if url and url not in images:
            images.append(url)
    for media in tweet.get('media', []) or []:
        url = media if isinstance(media, str) else media.get('url', media.get('media_url_https', ''))
        if url and url not in images:
            images.append(url)
    article = tweet.get('article', {}) or {}
    for img in article.get('images', []) or []:
        url = img if isinstance(img, str) else img.get('url', '')
        if url and url not in images:
            images.append(url)
    return images


def json_to_markdown(tweet_data, assets_dir, detect_code=False, tags_line=None):
    tweet = tweet_data.get('tweet', {})
    username = tweet_data.get('username') or tweet.get('screen_name', 'unknown')
    url = tweet_data.get('url', '')
    date_str = parse_date(tweet.get('created_at', ''))
    is_article = tweet.get('is_article', False)
    article = tweet.get('article', {}) or {}
    thread = tweet_data.get('thread', []) or []

    assets_dir.mkdir(parents=True, exist_ok=True)
    all_images = collect_images_from_json(tweet_data)
    thread_images = []
    for t in thread:
        imgs = []
        for img in t.get('photos', []) or []:
            img_url = img if isinstance(img, str) else img.get('url', '')
            if img_url and img_url not in all_images:
                all_images.append(img_url)
            if img_url:
                imgs.append(img_url)
        thread_images.append(imgs)

    local_images = {}
    media_id_to_local = {}
    for img_url in all_images:
        local_name = download_image(img_url, assets_dir)
        if local_name:
            local_images[img_url] = local_name

    if is_article:
        for media in article.get('images', []) or []:
            if isinstance(media, dict):
                media_id = media.get('media_id')
                img_url = media.get('url')
                if media_id and img_url and img_url in local_images:
                    media_id_to_local[str(media_id)] = local_images[img_url]

    cover_image = local_images.get(all_images[0]) if all_images else None
    if is_article and article.get('title'):
        title = article['title']
    else:
        first_line = tweet.get('text', '').strip().split('\n')[0]
        title = first_line[:60] if first_line else f'X @{username} {date_str}'

    parts = []
    if cover_image:
        parts.append(f'![封面图](assets/{cover_image})\n')
    parts.append(f'> 来源：X @{username} | {date_str}')
    parts.append(f'> 链接：{url}')
    if tags_line:
        parts.append(f'{tags_line}\n')

    if is_article and article.get('full_text'):
        article_body = article.get('full_text', '')
        fx_content = article.get('_fx_content') or {}
        if fx_content.get('blocks'):
            # 有 fx_content - 使用富文本 blocks，包含了 MARKDOWN entity，不需要代码检测
            article_body = _fx_article_to_markdown({'content': fx_content, 'full_text': article_body}, media_id_to_local)
            parts.append(article_body)
        else:
            # 无 fx_content - 使用纯文本，需要代码检测来包裹代码块
            if detect_code:
                article_body = _detect_and_wrap_code_blocks(article_body)
            parts.append(article_body)
            for i, img_url in enumerate(all_images):
                if i == 0 and cover_image:
                    continue
                if img_url in local_images:
                    parts.append(f'\n![图片](assets/{local_images[img_url]})')
    elif thread:
        parts.append(tweet.get('text', ''))
        for i, img_url in enumerate(all_images):
            if i == 0 and cover_image:
                continue
            if img_url in local_images:
                parts.append(f'\n![图片](assets/{local_images[img_url]})')
        for i, t in enumerate(thread):
            parts.append('\n---\n')
            parts.append(t.get('text', ''))
            for img_url in thread_images[i]:
                if img_url in local_images:
                    parts.append(f'\n![图片](assets/{local_images[img_url]})')
    else:
        parts.append(tweet.get('text', ''))
        for i, img_url in enumerate(all_images):
            if i == 0 and cover_image:
                continue
            if img_url in local_images:
                parts.append(f'\n![图片](assets/{local_images[img_url]})')

    likes = tweet.get('likes', 0) or 0
    retweets = tweet.get('retweets', 0) or 0
    bookmarks = tweet.get('bookmarks', 0) or 0
    views = tweet.get('views', 0) or 0
    replies = tweet.get('replies_count', 0) or 0
    body = clean_trailing_junk('\n'.join(parts))
    body += f'\n\n💬 {replies} · 🔁 {retweets} · 🔖 {bookmarks} · 👁 {views} · 回复 {replies}'
    return title, date_str, body


def auto_toc(output_path, has_leading_meta=False):
    print('\n📋 自动生成目录...')
    try:
        content = output_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        toc_start = ''
        toc_end = ''
        if toc_start in content:
            print('  ⏭ 已有目录，跳过')
            return
        re_md = re.compile(r'^(#{1,6})\s+(.+)$')
        re_num = re.compile(r'^(\d+(?:\.\d+)*)[ \t ]+(\S.*)$')
        headings = []
        for line in lines:
            s = line.rstrip()
            m = re_md.match(s)
            if m:
                headings.append((len(m.group(1)), m.group(2).strip()))
                continue
            m = re_num.match(s)
            if m:
                num = m.group(1)
                headings.append((num.count('.') + 1, f'{num} {m.group(2).strip()}'))
        if not headings:
            print('  ⚠️ 未找到标题，跳过')
            return
        min_level = min(h[0] for h in headings)
        toc_lines = ['**目录**', '']
        for level, text in headings:
            indent = ' ' * (level - min_level)
            toc_lines.append(f'{indent}- [{text}](#{text})')
        toc = '\n'.join(toc_lines)
        insert_at = 0
        if has_leading_meta:
            for i, line in enumerate(lines):
                if line.strip() == '':
                    insert_at = i + 1
                    break
        new_lines = lines[:insert_at] + ['', toc, ''] + lines[insert_at:]
        new_content = re.sub(r'\n{3,}', '\n\n', '\n'.join(new_lines))
        output_path.write_text(new_content, encoding='utf-8')
        print(f'  ✅ 已生成目录（{len(headings)} 个标题）')
    except Exception as e:
        print(f'  ⚠️ 目录生成失败：{e}')




def fetch_json(tweet_url, skill_dir):
    fetch_script = skill_dir / 'scripts' / 'fetch_tweet.py'
    if not fetch_script.exists():
        print(f'❌ 找不到 fetch_tweet.py：{fetch_script}')
        sys.exit(1)
    print(f'🔍 抓取推文：{tweet_url}')
    result = subprocess.run([sys.executable, str(fetch_script), '--url', tweet_url, '--pretty'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ fetch_tweet.py 执行失败：\n{result.stderr}')
        sys.exit(1)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f'❌ JSON解析失败：{e}\n输出：{result.stdout[:500]}')
        sys.exit(1)

    tweet = data.get('tweet', {}) or {}
    if tweet.get('is_article'):
        username = data.get('username') or tweet.get('screen_name')
        tweet_id = data.get('tweet_id')
        if username and tweet_id:
            fx_url = f'https://api.fxtwitter.com/{username}/status/{tweet_id}'
            try:
                req = urllib.request.Request(fx_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    raw = json.loads(resp.read().decode('utf-8'))
                raw_article = ((raw or {}).get('tweet') or {}).get('article') or {}
                article = tweet.setdefault('article', {})
                if raw_article.get('content', {}).get('blocks'):
                    article['_fx_content'] = raw_article.get('content')
                enriched_images = []
                cover = raw_article.get('cover_media') or {}
                cover_info = (cover.get('media_info') or {})
                if cover.get('media_id') and cover_info.get('original_img_url'):
                    enriched_images.append({'type': 'cover', 'media_id': str(cover.get('media_id')), 'url': cover_info.get('original_img_url')})
                for entity in raw_article.get('media_entities', []) or []:
                    info = (entity.get('media_info') or {})
                    if entity.get('media_id') and info.get('original_img_url'):
                        enriched_images.append({'type': 'image', 'media_id': str(entity.get('media_id')), 'url': info.get('original_img_url')})
                if enriched_images:
                    article['images'] = enriched_images
            except Exception as e:
                print(f'  ⚠️  获取 X Article 富文本块失败，将退回纯文本：{e}')
    return data


def main():
    parser = argparse.ArgumentParser(description='把X推文保存为Obsidian Markdown')
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--html', help='HTML文件（推荐，格式完整）')
    input_group.add_argument('--url', help='推文URL，自动调用fetch_tweet.py（纯文本）')
    input_group.add_argument('--json', help='已有的JSON文件（纯文本）')
    parser.add_argument('--tweet-url', help='推文原始URL（用--html时必填）')
    parser.add_argument('--username', help='作者用户名不含@（用--html时必填）')
    parser.add_argument('--date', help='推文日期 YYYY-MM-DD（用--html时可选）')
    parser.add_argument('--output', default='.', help='输出目录（默认当前目录）')
    parser.add_argument('--tags-line', default='', help='optional tags/header line to insert near the top, e.g. "#tag1 #tag2"')
    parser.add_argument('--detect-code', action='store_true', help='enable heuristic code block detection for plain-text article bodies')
    parser.add_argument('--no-toc', action='store_true', help='do not auto-insert a table of contents')
    args = parser.parse_args()

    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    
    if args.html:
        if not args.tweet_url:
            print('❌ --html 模式必须同时提供 --tweet-url')
            sys.exit(1)
        if not args.username:
            print('❌ --html 模式必须同时提供 --username')
            sys.exit(1)
        html_path = Path(args.html)
        if not html_path.exists():
            print(f'❌ 找不到HTML文件：{html_path}')
            sys.exit(1)
        html_content = html_path.read_text(encoding='utf-8')
        date_str = args.date or datetime.now().strftime('%Y-%m-%d')
        print('📝 解析HTML，生成Markdown...')
        # 临时目录，后续重命名
        temp_assets_dir = output_dir / 'temp_assets'
        title, md_content = html_to_markdown(html_content, temp_assets_dir, url=args.tweet_url, username=args.username, date_str=date_str, tags_line=args.tags_line or None)
    else:
        if args.url:
            tweet_data = fetch_json(args.url, skill_dir)
        else:
            json_path = Path(args.json)
            if not json_path.exists():
                print(f'❌ 找不到JSON文件：{json_path}')
                sys.exit(1)
            tweet_data = json.loads(json_path.read_text(encoding='utf-8'))
        print('📝 生成Markdown（纯文本模式）...')
        # 临时目录，后续重命名
        temp_assets_dir = output_dir / 'temp_assets'
        title, date_str, md_content = json_to_markdown(tweet_data, temp_assets_dir, detect_code=args.detect_code, tags_line=args.tags_line or None)

    safe_title = sanitize_filename(title)
    # 文件名不包含日期前缀
    filename = f'{safe_title}.md'
    
    # 用文档名在 assets 下创建专属子目录
    doc_name = filename.replace('.md', '')
    assets_subdir = output_dir / 'assets' / doc_name
    
    # 更新 markdown 里的图片引用路径
    md_content = md_content.replace('](assets/', f'](assets/{doc_name}/')
    
    output_path = output_dir / filename
    output_path.write_text(md_content, encoding='utf-8')
    
    # 重命名临时目录到 assets 子目录
    temp_assets_dir = output_dir / 'temp_assets'
    if temp_assets_dir.exists():
        assets_subdir.parent.mkdir(parents=True, exist_ok=True)
        if assets_subdir.exists():
            import shutil
            shutil.rmtree(assets_subdir)
        temp_assets_dir.rename(assets_subdir)

    print(f'\n✅ 保存完成：{output_path}')
    print(f'📁 图片目录：{assets_subdir}')

    if not args.no_toc:
        auto_toc(output_path, has_leading_meta=bool(args.tags_line))


if __name__ == '__main__':
    main()
