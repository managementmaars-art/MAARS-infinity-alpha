#!/usr/bin/env python3
"""
paper_to_obsidian.py - 把学术论文（arXiv）导出为 Obsidian Markdown

支持三种输入：
  1. --arxiv 2401.02385      # 自动从 ar5iv.labs.arxiv.org 抓取
  2. --url https://ar5iv.labs.arxiv.org/html/2401.02385
  3. --html paper.html       # 本地 HTML 文件

用法：
  python3 paper_to_obsidian.py --arxiv 2401.02385 --output ./papers/
  python3 paper_to_obsidian.py --arxiv 2401.02385 --output ./papers/ --tags "llm,training"
"""

import argparse
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser

# 尝试导入 to_obsidian 的工具函数
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from to_obsidian import download_image, sanitize_filename, auto_toc
except ImportError:
    def sanitize_filename(text, max_len=80):
        text = re.sub(r'[^\w\u4e00-\u9fff\-\s]', '', text)
        text = re.sub(r'\s+', '-', text.strip())
        return text[:max_len]

    def download_image(url, assets_dir):
        from urllib.parse import urlparse
        path = urlparse(url).path
        filename = os.path.basename(path)
        if '.' not in filename:
            filename += '.png'
        dest = assets_dir / filename
        if dest.exists():
            print(f'  ⏭️  已存在：{filename}')
            return filename
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                              'Version/18.3 Safari/605.1.15'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
            print(f'  ✅ 下载图片：{filename}')
            return filename
        except Exception as e:
            print(f'  ⚠️  图片下载失败 {url}：{e}')
            return None

    def auto_toc(output_path):
        pass


AR5IV_BASE = 'https://ar5iv.labs.arxiv.org'


def strip_tags(html_str):
    """移除 HTML 标签，保留文本"""
    return re.sub(r'<[^>]+>', '', html_str).strip()


def fetch_html(arxiv_id):
    """从 ar5iv 获取论文 HTML"""
    url = f'{AR5IV_BASE}/html/{arxiv_id}'
    print(f'📥 抓取论文：{url}')
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/605.1.15'
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode('utf-8')
        print(f'✅ HTML 获取成功 ({len(html):,} bytes)')
        return html
    except Exception as e:
        print(f'❌ HTML 获取失败：{e}')
        sys.exit(1)


def fetch_arxiv_meta(arxiv_id):
    """从 arXiv API 获取元数据"""
    api_url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            root = ET.fromstring(resp.read())
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        entry = root.find('.//a:entry', ns)
        if entry is None:
            return {}
        meta = {}
        pub = entry.find('a:published', ns)
        if pub is not None and pub.text:
            meta['date'] = pub.text[:10]
        authors = []
        for author in entry.findall('a:author', ns):
            name = author.find('a:name', ns)
            if name is not None and name.text:
                authors.append(name.text.strip())
        if authors:
            meta['authors'] = authors
        cats = entry.findall('a:category', ns)
        if cats:
            meta['categories'] = [c.get('term') for c in cats if c.get('term')]
        return meta
    except Exception as e:
        print(f'  ⚠️ arXiv API 查询失败：{e}')
        return {}


# ─── 正文解析器 ───

class BodyParser(HTMLParser):
    """解析 ar5iv HTML 正文为 Markdown 块列表"""

    def __init__(self, arxiv_id):
        super().__init__()
        self.arxiv_id = arxiv_id
        self.blocks = []  # [(type, content)] — 最终输出
        self.images = []  # [(src_url, fig_id, caption)]

        # 状态
        self._skip_depth = 0      # >0 时跳过内容（header/footer/abstract）
        self._in_section = 0      # 嵌套 section 深度
        self._heading_tag = None  # 当前在 h2/h3/h4 内
        self._heading_buf = ''
        self._para_buf = None     # 段落收集
        self._math_alt = None     # 当前 math alttext
        self._in_figure = False
        self._fig_id = ''
        self._fig_caption = ''
        self._fig_img = ''
        self._in_caption = False
        self._caption_buf = ''
        self._in_bib = False
        self._bib_buf = ''
        self._bib_items = []
        self._in_list = None      # 'ul' or 'ol'
        self._list_items = []
        self._list_item_buf = ''
        self._in_table = False
        self._table_rows = []
        self._table_row = []
        self._table_cell = ''
        self._tag_stack = []

    def _cur_classes(self):
        if self._tag_stack:
            return self._tag_stack[-1][1]
        return ''

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        cls = d.get('class', '')
        self._tag_stack.append((tag, cls))

        # 跳过页面 header/footer/logo
        if any(s in cls for s in ('ltx_page_header', 'ltx_page_footer', 'ltx_page_logo', 'ltx_LaTeXML')):
            self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        # 章节标题
        if tag in ('h2', 'h3', 'h4', 'h5') and 'ltx_title' in cls:
            self._heading_tag = tag
            self._heading_buf = ''
            return

        # 摘要 — 已单独提取，跳过
        if 'ltx_abstract' in cls:
            self._skip_depth += 1
            return

        # 段落
        if tag == 'p' and 'ltx_p' in cls:
            self._para_buf = ''
            return

        # 跳过 ltx_ERROR（LaTeX 残留标记）
        if 'ltx_ERROR' in cls:
            self._skip_depth += 1
            return

        # 数学公式
        if tag == 'math' and 'ltx_Math' in cls:
            alt = d.get('alttext', '')
            if alt:
                self._math_alt = alt
            return

        # 行间公式（equation 环境）
        if tag == 'table' and 'ltx_equation' in cls:
            # equation 里的 math 会被 handle_data 处理
            return

        # 图片
        if tag == 'figure' and 'ltx_figure' in cls:
            self._in_figure = True
            self._fig_id = d.get('id', '')
            self._fig_caption = ''
            self._fig_img = ''
            return

        if tag == 'img' and self._in_figure:
            src = d.get('src', '')
            if src and not src.startswith('data:') and 'ar5iv' not in os.path.basename(src):
                if not src.startswith('http'):
                    src = f'{AR5IV_BASE}{src}'
                self._fig_img = src
            return

        if ('ltx_caption' in cls):
            self._in_caption = True
            self._caption_buf = ''
            return

        # 参考文献
        if 'ltx_biblist' in cls:
            self._in_bib = True
            self._bib_items = []
            return

        if 'ltx_bibitem' in cls:
            self._bib_buf = ''
            return

        # 列表
        if tag == 'ul' and 'ltx_itemize' in cls:
            self._in_list = 'ul'
            self._list_items = []
            self._list_item_buf = ''
            return
        if tag == 'ol' and 'ltx_enumerate' in cls:
            self._in_list = 'ol'
            self._list_items = []
            self._list_item_buf = ''
            return
        if tag == 'li' and self._in_list:
            self._list_item_buf = ''
            return

        # 表格
        if tag == 'table' and 'ltx_tabular' in cls:
            self._in_table = True
            self._table_rows = []
            self._table_row = []
            self._table_cell = ''
            return
        if tag == 'tr' and self._in_table:
            self._table_row = []
            self._table_cell = ''
            return
        if tag in ('td', 'th') and self._in_table:
            self._table_cell = ''
            return

    def handle_endtag(self, tag):
        # pop tag stack
        if self._tag_stack and self._tag_stack[-1][0] == tag:
            popped_cls = self._tag_stack.pop()[1]
        else:
            popped_cls = ''

        # skip tracking
        if self._skip_depth > 0:
            if any(s in popped_cls for s in ('ltx_page_header', 'ltx_page_footer', 'ltx_page_logo', 'ltx_LaTeXML', 'ltx_abstract', 'ltx_ERROR')):
                self._skip_depth -= 1
            return

        # 标题结束
        if tag == self._heading_tag:
            text = self._heading_buf.strip()
            text = re.sub(r'^\s*\d+(\.\d+)*\s+', '', text)  # 去数字前缀
            if text and text.lower() not in ('abstract',):
                level_map = {'h2': 2, 'h3': 3, 'h4': 4, 'h5': 5}
                level = level_map.get(tag, 2)
                prefix = '#' * level
                self.blocks.append(('heading', f'{prefix} {text}'))
            self._heading_tag = None
            return

        # 段落结束
        if tag == 'p' and self._para_buf is not None:
            text = self._para_buf.strip()
            if text:
                self.blocks.append(('para', text))
            self._para_buf = None
            return

        # caption 结束
        if self._in_caption and tag in ('figcaption', 'span', 'div'):
            if 'ltx_caption' in popped_cls:
                self._in_caption = False
                self._fig_caption = self._caption_buf.strip()
            return

        # 图片结束
        if tag == 'figure' and self._in_figure:
            self._in_figure = False
            if self._fig_img:
                self.images.append((self._fig_img, self._fig_id, self._fig_caption))
                self.blocks.append(('figure', (self._fig_img, self._fig_caption)))
            return

        # 参考文献项结束
        if tag == 'li' and self._bib_buf:
            text = self._bib_buf.strip()
            text = re.sub(r'\s+', ' ', text)
            if text:
                self._bib_items.append(text)
            self._bib_buf = ''
            return

        # 参考文献列表结束
        if tag == 'ul' and self._in_bib and 'ltx_biblist' in popped_cls:
            self._in_bib = False
            if self._bib_items:
                self.blocks.append(('references', self._bib_items))
            return

        # 列表项结束
        if tag == 'li' and self._in_list:
            text = self._list_item_buf.strip()
            if text:
                self._list_items.append(text)
            self._list_item_buf = ''
            return

        # 列表结束
        if tag in ('ul', 'ol') and self._in_list:
            if self._list_items:
                if self._in_list == 'ul':
                    md = '\n'.join(f'- {item}' for item in self._list_items)
                else:
                    md = '\n'.join(f'{i+1}. {item}' for i, item in enumerate(self._list_items))
                self.blocks.append(('list', md))
            self._in_list = None
            return

        # 表格单元格结束
        if tag in ('td', 'th') and self._in_table:
            self._table_row.append(self._table_cell.strip())
            self._table_cell = ''
            return

        # 表格行结束
        if tag == 'tr' and self._in_table:
            if self._table_row:
                self._table_rows.append(self._table_row)
            self._table_row = []
            return

        # 表格结束
        if tag == 'table' and self._in_table and 'ltx_tabular' in popped_cls:
            self._in_table = False
            if self._table_rows:
                md = self._table_to_md(self._table_rows)
                if md:
                    self.blocks.append(('table', md))
            return

    def handle_data(self, data):
        if self._skip_depth > 0:
            return

        # 数学公式 — alttext 已提取，但 handle_data 会传公式的渲染文本
        # 我们跳过 math 内的文本，用 alttext 替代
        if any(tag == 'math' for tag, _ in self._tag_stack):
            return

        # 标题
        if self._heading_tag:
            self._heading_buf += data
            return

        # caption
        if self._in_caption:
            self._caption_buf += data
            return

        # 参考文献
        if self._in_bib:
            self._bib_buf += data
            return

        # 列表项
        if self._in_list:
            self._list_item_buf += data
            return

        # 表格
        if self._in_table:
            self._table_cell += data
            return

        # 段落
        if self._para_buf is not None:
            self._para_buf += data
            return

    def handle_entityref(self, name):
        char_map = {'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"', 'apos': "'"}
        ch = char_map.get(name, f'&{name};')
        self.handle_data(ch)

    def handle_charref(self, name):
        try:
            ch = chr(int(name, 16) if name.startswith('x') else int(name))
        except (ValueError, OverflowError):
            ch = f'&#{name};'
        self.handle_data(ch)

    def _table_to_md(self, rows):
        if not rows:
            return ''
        max_cols = max(len(r) for r in rows)
        if max_cols == 0:
            return ''
        # 补齐列数
        for r in rows:
            while len(r) < max_cols:
                r.append('')
        lines = []
        for i, row in enumerate(rows):
            escaped = [c.replace('|', '\\|') for c in row]
            lines.append('| ' + ' | '.join(escaped) + ' |')
            if i == 0:
                lines.append('| ' + ' | '.join(['---'] * max_cols) + ' |')
        return '\n'.join(lines)


# ─── 公式后处理 ───

def inject_math(html):
    """把 <math alttext="..."> 替换为 $...$ 文本，简化后续解析"""
    def _replace_math(m):
        alt = m.group(1)
        full = m.group(0)
        # 判断行间还是行内
        # 如果在 equation 环境内，用 $$
        if 'display="block"' in full:
            return f'$${alt}$$'
        return f'${alt}$'

    # 替换 <math ...>...</math> 为 $alttext$
    result = re.sub(
        r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>',
        _replace_math, html, flags=re.DOTALL
    )
    return result


# ─── 元数据提取（正则） ───

def extract_meta(html, arxiv_id):
    """从 HTML 提取标题、作者、摘要"""
    meta = {}

    # 标题
    m = re.search(r'<h1[^>]*ltx_title_document[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        meta['title'] = strip_tags(m.group(1)).strip()

    # 作者 — 从 ltx_personname 里提取，处理多人在同一 span 的情况
    m = re.search(r'<span[^>]*ltx_personname[^>]*>(.*?)</span>', html, re.DOTALL)
    if m:
        raw = m.group(1)
        # 去掉 sup 标签（脚注标记）
        raw = re.sub(r'<sup[^>]*>.*?</sup>', '|SEP|', raw)
        raw = strip_tags(raw)
        # 用换行/多空格分割作者
        parts = re.split(r'\|SEP\||\n|(?:  +)', raw)
        authors = [p.strip() for p in parts if p.strip() and len(p.strip()) > 1]
        if authors:
            meta['authors'] = authors

    # 摘要
    m = re.search(r'<div[^>]*ltx_abstract[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        raw = strip_tags(m.group(1)).strip()
        raw = re.sub(r'^Abstract\s*', '', raw)
        raw = re.sub(r'\s+', ' ', raw)
        meta['abstract'] = raw

    return meta


# ─── 组装 Markdown ───

def build_markdown(meta, blocks, downloaded, safe_title, arxiv_id, tags):
    """把解析结果组装成最终 Markdown"""
    lines = []

    # YAML frontmatter
    lines.append('---')
    title = meta.get('title', arxiv_id)
    lines.append(f'title: "{title}"')

    authors = meta.get('authors', [])
    if authors:
        # YAML list
        authors_yaml = ', '.join(authors[:8])
        if len(authors) > 8:
            authors_yaml += ' et al.'
        lines.append(f'authors: [{authors_yaml}]')

    date = meta.get('date', datetime.now().strftime('%Y-%m-%d'))
    lines.append(f'date: {date}')

    if arxiv_id:
        lines.append(f'arxiv_id: "{arxiv_id}"')
        lines.append(f'url: "https://arxiv.org/abs/{arxiv_id}"')

    tag_list = [t.strip() for t in tags.split(',')] if tags else ['paper']
    lines.append(f'tags: [{", ".join(tag_list)}]')
    lines.append('---')
    lines.append('')

    # 摘要
    abstract = meta.get('abstract', '')
    if abstract:
        lines.append(f'> **Abstract**: {abstract}')
        lines.append('')

    # 正文
    for btype, content in blocks:
        if btype == 'heading':
            # 避免重复的 References 标题（已在 references block 里生成）
            if content.strip() == '## References' and any(bt == 'references' for bt, _ in blocks):
                continue
            lines.append('')
            lines.append(content)
            lines.append('')
        elif btype == 'para':
            # 过滤 LaTeX 残留标记
            if re.match(r'^(tcb@|\\begin|\\end|\\newcommand|\\def\b)', content.strip()):
                continue
            lines.append(content)
            lines.append('')
        elif btype == 'figure':
            img_url, caption = content
            local = downloaded.get(img_url)
            if local:
                lines.append(f'![{caption or "图片"}](assets/{safe_title}/{local})')
                if caption:
                    lines.append(f'*{caption}*')
                lines.append('')
        elif btype == 'table':
            lines.append(content)
            lines.append('')
        elif btype == 'list':
            lines.append(content)
            lines.append('')
        elif btype == 'references':
            lines.append('')
            lines.append('## References')
            lines.append('')
            for i, ref in enumerate(content, 1):
                # 清理编号前缀
                ref_clean = re.sub(r'^\[?\d+\]?\s*', '', ref)
                lines.append(f'{i}. {ref_clean}')
            lines.append('')

    return '\n'.join(lines)


# ─── 主函数 ───

def main():
    parser = argparse.ArgumentParser(description='把 arXiv 论文导出为 Obsidian Markdown + 本地图片')

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--arxiv', help='arXiv ID（如 2401.02385）')
    input_group.add_argument('--url', help='ar5iv 完整 URL')
    input_group.add_argument('--html', help='本地 HTML 文件')

    parser.add_argument('--output', default='.', help='输出目录（默认当前目录）')
    parser.add_argument('--tags', default='', help='标签，逗号分隔（如 "llm,training"）')
    parser.add_argument('--no-toc', action='store_true', help='不自动生成目录')

    args = parser.parse_args()
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # ─── 获取 HTML ───
    arxiv_id = ''
    if args.arxiv:
        arxiv_id = args.arxiv.strip()
        html = fetch_html(arxiv_id)
    elif args.url:
        m = re.search(r'/html/([\w.\-]+)', args.url)
        arxiv_id = m.group(1) if m else 'unknown'
        print(f'📥 抓取：{args.url}')
        req = urllib.request.Request(args.url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode('utf-8')
    else:
        html_path = Path(args.html)
        if not html_path.exists():
            print(f'❌ 找不到文件：{html_path}')
            sys.exit(1)
        html = html_path.read_text(encoding='utf-8')
        arxiv_id = html_path.stem

    # ─── 元数据 ───
    print('📝 解析元数据...')
    meta = extract_meta(html, arxiv_id)

    # 用 arXiv API 补充（作者更准确、有日期）
    if arxiv_id and arxiv_id != 'unknown':
        api_meta = fetch_arxiv_meta(arxiv_id)
        if api_meta.get('authors'):
            meta['authors'] = api_meta['authors']
        if api_meta.get('date'):
            meta['date'] = api_meta['date']

    title = meta.get('title', arxiv_id)
    print(f'📌 标题：{title}')
    print(f'👥 作者：{", ".join(meta.get("authors", [])[:3])}{"..." if len(meta.get("authors", [])) > 3 else ""}')

    # ─── 预处理：公式注入 ───
    print('📝 处理公式...')
    html = inject_math(html)

    # ─── 解析正文 ───
    print('📝 解析正文...')
    body_parser = BodyParser(arxiv_id)
    body_parser.feed(html)

    headings = sum(1 for t, _ in body_parser.blocks if t == 'heading')
    paras = sum(1 for t, _ in body_parser.blocks if t == 'para')
    refs = sum(1 for t, _ in body_parser.blocks if t == 'references')
    print(f'📑 章节：{headings} | 段落：{paras} | 图片：{len(body_parser.images)} | 参考文献：{"有" if refs else "无"}')

    # ─── 下载图片 ───
    safe_title = sanitize_filename(title)
    assets_dir = output_dir / 'assets' / safe_title
    assets_dir.mkdir(parents=True, exist_ok=True)

    print('📥 下载图片...')
    downloaded = {}  # url -> local filename
    for img_url, fig_id, caption in body_parser.images:
        local = download_image(img_url, assets_dir)
        if local:
            downloaded[img_url] = local

    # ─── 生成 Markdown ───
    md = build_markdown(meta, body_parser.blocks, downloaded, safe_title, arxiv_id, args.tags)

    filename = f'{safe_title}.md'
    output_path = output_dir / filename
    output_path.write_text(md, encoding='utf-8')
    print(f'\n✅ 保存完成：{output_path}')
    print(f'📁 图片目录：{assets_dir}')

    # 目录
    if not args.no_toc:
        try:
            auto_toc(output_path)
        except TypeError:
            # auto_toc 签名可能不同
            pass

    # 统计
    img_count = len([f for f in assets_dir.iterdir() if f.is_file()]) if assets_dir.exists() else 0
    print(f'📊 共 {img_count} 张图片，{len(md):,} 字符')


if __name__ == '__main__':
    main()
