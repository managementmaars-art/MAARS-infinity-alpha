#!/usr/bin/env python3
from __future__ import print_function

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urljoin
except ImportError:
    from urllib2 import Request, urlopen
    from urlparse import urljoin

HN_URL = 'https://news.ycombinator.com/'
USER_AGENT = 'Mozilla/5.0 (compatible; hn-top10-script/1.0)'
MAX_ITEMS = 10
MAX_LIMIT = 30
NUMBER_RE = re.compile(r'\d+')
TIMESTAMP_RE = re.compile(r'\d{8}-\d{6}')


class HNTopParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.items = []
        self.current_item = None
        self.in_rank = False
        self.rank_parts = []
        self.in_titleline = False
        self.title_anchor_taken = False
        self.capture_title = False
        self.title_parts = []
        self.current_href = None
        self.in_subtext = False
        self.in_score = False
        self.score_parts = []
        self.capture_author = False
        self.author_parts = []
        self.in_age = False
        self.capture_age = False
        self.age_parts = []
        self.capture_comments = False
        self.comment_parts = []

    def close_current_item(self):
        if self.current_item and self.current_item.get('title') and self.current_item.get('link'):
            self.items.append(self.current_item)
        self.current_item = None
        self.in_rank = False
        self.rank_parts = []
        self.in_titleline = False
        self.title_anchor_taken = False
        self.capture_title = False
        self.title_parts = []
        self.current_href = None
        self.in_subtext = False
        self.in_score = False
        self.score_parts = []
        self.capture_author = False
        self.author_parts = []
        self.in_age = False
        self.capture_age = False
        self.age_parts = []
        self.capture_comments = False
        self.comment_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get('class', '')
        classes = class_name.split()

        if tag == 'tr' and 'athing' in classes:
            self.close_current_item()
            self.current_item = {
                'rank': 0,
                'score': 0,
                'comments': 0,
                'author': '',
                'age': '',
                'title': '',
                'link': '',
            }
            return

        if self.current_item is None:
            return

        if tag == 'span' and 'rank' in classes:
            self.in_rank = True
            self.rank_parts = []
            return

        if tag == 'span' and 'titleline' in classes:
            self.in_titleline = True
            self.title_anchor_taken = False
            return

        if tag == 'a' and self.in_titleline and not self.title_anchor_taken:
            self.capture_title = True
            self.title_anchor_taken = True
            self.title_parts = []
            self.current_href = attrs_dict.get('href', '')
            return

        if tag == 'td' and 'subtext' in classes:
            self.in_subtext = True
            return

        if tag == 'span' and 'score' in classes:
            self.in_score = True
            self.score_parts = []
            return

        if tag == 'a' and self.in_subtext and 'hnuser' in classes:
            self.capture_author = True
            self.author_parts = []
            return

        if tag == 'span' and 'age' in classes:
            self.in_age = True
            return

        if tag == 'a' and self.in_age:
            self.capture_age = True
            self.age_parts = []
            return

        href = attrs_dict.get('href', '')
        if tag == 'a' and self.in_subtext and not self.in_age and not self.capture_age and href.startswith('item?id='):
            self.capture_comments = True
            self.comment_parts = []

    def handle_endtag(self, tag):
        if self.current_item is None:
            return

        if tag == 'span' and self.in_rank:
            self.current_item['rank'] = parse_number(''.join(self.rank_parts))
            self.in_rank = False
            self.rank_parts = []
            return

        if tag == 'a' and self.capture_title:
            self.current_item['title'] = ''.join(self.title_parts).strip()
            self.current_item['link'] = urljoin(HN_URL, (self.current_href or '').strip())
            self.capture_title = False
            self.title_parts = []
            self.current_href = None
            return

        if tag == 'span' and self.in_titleline:
            self.in_titleline = False
            self.title_anchor_taken = False
            return

        if tag == 'span' and self.in_score:
            self.current_item['score'] = parse_number(''.join(self.score_parts))
            self.in_score = False
            self.score_parts = []
            return

        if tag == 'a' and self.capture_author:
            self.current_item['author'] = ''.join(self.author_parts).strip()
            self.capture_author = False
            self.author_parts = []
            return

        if tag == 'a' and self.capture_age:
            self.current_item['age'] = ''.join(self.age_parts).strip()
            self.capture_age = False
            self.age_parts = []
            return

        if tag == 'span' and self.in_age:
            self.in_age = False
            return

        if tag == 'a' and self.capture_comments:
            self.current_item['comments'] = parse_number(''.join(self.comment_parts))
            self.capture_comments = False
            self.comment_parts = []
            return

        if tag == 'td' and self.in_subtext:
            self.in_subtext = False

    def handle_data(self, data):
        if self.current_item is None:
            return

        if self.in_rank:
            self.rank_parts.append(data)

        if self.capture_title:
            self.title_parts.append(data)

        if self.in_score:
            self.score_parts.append(data)

        if self.capture_author:
            self.author_parts.append(data)

        if self.capture_age:
            self.age_parts.append(data)

        if self.capture_comments:
            self.comment_parts.append(data)

    def close(self):
        HTMLParser.close(self)
        self.close_current_item()


def parse_number(text):
    match = NUMBER_RE.search(text or '')
    if not match:
        return 0
    return int(match.group(0))


def fetch_html(url):
    request = Request(url, headers={'User-Agent': USER_AGENT})
    response = urlopen(request, timeout=15)
    try:
        encoding = response.headers.get_content_charset()
    except AttributeError:
        encoding = response.headers.getparam('charset')
    data = response.read()
    return data.decode(encoding or 'utf-8', 'replace')


def parse_items(html):
    parser = HNTopParser()
    parser.feed(html)
    parser.close()
    return parser.items


def build_timestamp():
    return datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')


def resolve_output_path(output_path, json_mode):
    if not json_mode:
        return output_path

    timestamp = build_timestamp()
    if not output_path:
        return 'hn-top10-%s.json' % timestamp

    directory, filename = os.path.split(output_path)
    stem, extension = os.path.splitext(filename)
    if not extension:
        extension = '.json'
    if TIMESTAMP_RE.search(stem):
        updated_filename = stem + extension
    else:
        updated_filename = '%s-%s%s' % (stem or 'hn-top10', timestamp, extension)
    return os.path.join(directory, updated_filename)


def build_argument_parser():
    parser = argparse.ArgumentParser(description='Fetch top Hacker News stories as CSV or JSON.')
    parser.add_argument(
        '--limit',
        type=int,
        default=MAX_ITEMS,
        help='Number of stories to output, 1-%d (default: %%(default)s).' % MAX_LIMIT,
    )
    parser.add_argument(
        '--output',
        help='Write output to the given file path instead of stdout.',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON instead of CSV.',
    )
    return parser


def main():
    try:
        args = build_argument_parser().parse_args()
        if args.limit <= 0 or args.limit > MAX_LIMIT:
            sys.stderr.write('Error: --limit must be between 1 and %d.\n' % MAX_LIMIT)
            return 1

        html = fetch_html(HN_URL)
        items = parse_items(html)
    except Exception as exc:
        sys.stderr.write('Error: failed to fetch or parse Hacker News: %s\n' % exc)
        return 1

    if not items:
        sys.stderr.write('Error: no stories found on Hacker News homepage.\n')
        return 1

    output_handle = sys.stdout
    should_close = False
    selected_items = items[:args.limit]
    output_path = resolve_output_path(args.output, args.json)
    try:
        if output_path:
            output_handle = open(output_path, 'w', newline='')
            should_close = True

        if args.json:
            json.dump(selected_items, output_handle, ensure_ascii=False, indent=2)
            output_handle.write('\n')
        else:
            writer = csv.writer(output_handle)
            writer.writerow(['rank', 'score', 'comments', 'author', 'age', 'title', 'link'])
            for item in selected_items:
                writer.writerow([
                    item['rank'],
                    item['score'],
                    item['comments'],
                    item['author'],
                    item['age'],
                    item['title'],
                    item['link'],
                ])
    except Exception as exc:
        sys.stderr.write('Error: failed to write CSV: %s\n' % exc)
        return 1
    finally:
        if should_close:
            output_handle.close()

    if args.json and output_path:
        sys.stdout.write('Saved JSON: %s\n' % output_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
