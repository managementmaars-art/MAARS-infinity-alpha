#!/usr/bin/env python3
"""
Regex Tester Tool
Based on Python's re: https://github.com/python/cpython

Usage:
    python regex_tester.py "\\d+" "abc123def456"
    python regex_tester.py "(\\w+)@(\\w+)" "user@domain" --groups
"""

import argparse
import re
import sys

COMMON_PATTERNS = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
    'phone': r'\+?[\d\s\-\(\)]{10,}',
    'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    'date': r'\d{4}-\d{2}-\d{2}',
    'time': r'\d{2}:\d{2}(:\d{2})?',
    'hex': r'#?[0-9a-fA-F]{6}',
    'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
}

def test_regex(pattern, text, flags=0, show_groups=False, find_all=False):
    """Test regex pattern against text."""
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(f"Invalid regex: {e}", file=sys.stderr)
        sys.exit(1)
    
    if find_all:
        matches = regex.findall(text)
        print(f"Pattern: {pattern}")
        print(f"Text: {text}")
        print(f"\nMatches ({len(matches)}):")
        for i, m in enumerate(matches, 1):
            print(f"  {i}. {m}")
        return
    
    match = regex.search(text)
    
    print(f"Pattern: {pattern}")
    print(f"Text: {text}")
    
    if match:
        print(f"\n✓ Match found: '{match.group()}'")
        print(f"  Position: {match.start()}-{match.end()}")
        
        if show_groups and match.groups():
            print(f"\nCapture groups:")
            for i, g in enumerate(match.groups(), 1):
                print(f"  Group {i}: '{g}'")
            
            if match.groupdict():
                print(f"\nNamed groups:")
                for name, value in match.groupdict().items():
                    print(f"  {name}: '{value}'")
    else:
        print("\n✗ No match found")

def main():
    parser = argparse.ArgumentParser(description="Test regex patterns")
    parser.add_argument('regex', nargs='?', help='Regex pattern')
    parser.add_argument('text', nargs='?', help='Text to match')
    parser.add_argument('--pattern', '-p', choices=COMMON_PATTERNS.keys(),
                       help='Use common pattern')
    parser.add_argument('--groups', '-g', action='store_true', help='Show groups')
    parser.add_argument('--all', '-a', action='store_true', help='Find all matches')
    parser.add_argument('--ignore-case', '-i', action='store_true')
    parser.add_argument('--multiline', '-m', action='store_true')
    parser.add_argument('--list', '-l', action='store_true', help='List patterns')
    args = parser.parse_args()
    
    if args.list:
        print("Common patterns:")
        for name, pattern in COMMON_PATTERNS.items():
            print(f"  {name}: {pattern}")
        return
    
    pattern = COMMON_PATTERNS.get(args.pattern) if args.pattern else args.regex
    
    if not pattern or not args.text:
        parser.error("Provide regex and text, or use --pattern with text")
    
    flags = 0
    if args.ignore_case:
        flags |= re.IGNORECASE
    if args.multiline:
        flags |= re.MULTILINE
    
    test_regex(pattern, args.text, flags, args.groups, args.all)

if __name__ == "__main__":
    main()
