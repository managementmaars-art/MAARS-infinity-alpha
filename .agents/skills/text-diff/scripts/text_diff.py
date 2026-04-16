#!/usr/bin/env python3
"""
Text Diff Tool
Based on Python's difflib: https://github.com/python/cpython

Usage:
    python text_diff.py file1.txt file2.txt
    python text_diff.py old.py new.py --unified
"""

import argparse
import difflib
import sys
from pathlib import Path

def read_file(filepath):
    """Read file and return lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()

def unified_diff(file1, file2, lines1, lines2, context=3):
    """Generate unified diff."""
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1, tofile=file2,
        lineterm=''
    )
    return '\n'.join(diff)

def context_diff(file1, file2, lines1, lines2, context=3):
    """Generate context diff."""
    diff = difflib.context_diff(
        lines1, lines2,
        fromfile=file1, tofile=file2,
        lineterm=''
    )
    return '\n'.join(diff)

def html_diff(file1, file2, lines1, lines2):
    """Generate HTML diff."""
    differ = difflib.HtmlDiff()
    return differ.make_file(lines1, lines2, file1, file2)

def main():
    parser = argparse.ArgumentParser(description="Compare files")
    parser.add_argument('file1', help='First file')
    parser.add_argument('file2', help='Second file')
    parser.add_argument('--unified', '-u', action='store_true', help='Unified format')
    parser.add_argument('--context', '-c', type=int, default=3, help='Context lines')
    parser.add_argument('--html', action='store_true', help='HTML output')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--patch', '-p', action='store_true', help='Patch format')
    args = parser.parse_args()
    
    lines1 = read_file(args.file1)
    lines2 = read_file(args.file2)
    
    if lines1 == lines2:
        print("✓ Files are identical")
        return
    
    if args.html:
        result = html_diff(args.file1, args.file2, lines1, lines2)
    elif args.unified or args.patch:
        result = unified_diff(args.file1, args.file2, lines1, lines2, args.context)
    else:
        # Simple diff
        differ = difflib.Differ()
        diff = differ.compare(lines1, lines2)
        result = ''.join(diff)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✓ Diff saved to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
