#!/usr/bin/env python3
"""
Extract user requests/asks from Claude Code session JSONL files.

Reads session files from the Claude projects directory, finds user-typed
messages that look like actual requests (not tool results, system messages,
continuations, or trivial confirmations), and prints them sorted by session date.

Two output sections:
  1. UNIQUE requests (deduplicated by first 100 chars)
  2. Summary of all sessions with request counts
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

SESSION_DIR = Path("/home/ubuntu/.claude/projects/-data-projects-coding-agent-session-search")
MIN_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MIN_MSG_LENGTH = 20
MAX_RESULTS = 100

# Words that indicate a user request/ask
REQUEST_KEYWORDS = re.compile(
    r'\b('
    r'add|implement|create|fix|build|make|want|need|should|please|'
    r'update|change|remove|write|delete|move|rename|refactor|'
    r'modify|replace|install|configure|set\s*up|setup|debug|'
    r'test|check|verify|ensure|run|deploy|use|try|look|'
    r'read|examine|investigate|analyze|understand|help|'
    r'extract|generate|convert|parse|handle|support|'
    r'show|display|print|list|find|search|get|fetch|'
    r'enable|disable|turn|switch|'
    r'can\s+you|could\s+you|would\s+you|'
    r'let\'?s|we\s+need|i\s+need|i\s+want|'
    r'start|stop|restart|'
    r'merge|commit|push|pull|rebase|'
    r'document|describe|explain'
    r')\b',
    re.IGNORECASE
)

# Trivial / non-request messages to skip
TRIVIAL_PATTERNS = re.compile(
    r'^(yes|no|ok|okay|sure|thanks|thank you|continue|go ahead|'
    r'proceed|done|got it|right|correct|exactly|yep|yup|nope|'
    r'y|n|k|lgtm|sounds good|perfect|great|good|fine|'
    r'agreed|absolutely|definitely|go for it)\s*[.!?]*$',
    re.IGNORECASE
)

# Skip system/automated messages
SYSTEM_PATTERNS = [
    '<task-notification>',
    '<task-id>',
    'Read the output file to retrieve the result:',
    '<output-file>',
]

# Skip context-compaction / session-continuation messages
CONTINUATION_PATTERNS = [
    'This session is being continued from a previous conversation',
    'The summary below covers the earlier portion',
    'ran out of context',
]

# Skip skill injection messages (pasted from /home/ubuntu/.claude/skills/)
SKILL_INJECTION_PATTERN = re.compile(
    r'^Base directory for this skill:\s*/home/ubuntu/\.claude/skills/',
    re.IGNORECASE
)


def extract_text_from_content(content):
    """Extract plain text from message content (string or array format)."""
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif item.get('type') == 'tool_result':
                    continue
            elif isinstance(item, str):
                texts.append(item)
        return '\n'.join(texts).strip()
    return ''


def is_system_message(text):
    for pattern in SYSTEM_PATTERNS:
        if pattern in text:
            return True
    return False


def is_continuation_message(text):
    for pattern in CONTINUATION_PATTERNS:
        if pattern in text:
            return True
    return False


def is_skill_injection(text):
    if SKILL_INJECTION_PATTERN.match(text):
        return True
    return False


def is_user_request(text):
    if len(text) < MIN_MSG_LENGTH:
        return False
    if TRIVIAL_PATTERNS.match(text):
        return False
    if is_system_message(text):
        return False
    if is_continuation_message(text):
        return False
    if is_skill_injection(text):
        return False
    if REQUEST_KEYWORDS.search(text):
        return True
    return False


def normalize_for_dedup(text):
    """Create a normalization key for deduplication."""
    # Strip common prefixes like "pick from here:" or escape sequences
    cleaned = re.sub(r'^(pick\s+(up\s+)?from\s+here:?\s*[❯>]*\s*)', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'^[\x1b\[][0-9;]*[A-Za-z]', '', cleaned)  # strip ANSI
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    return cleaned[:100]


def process_session_file(filepath):
    """Process a single session JSONL file and extract user requests."""
    results = []
    user_msg_num = 0

    with open(filepath, 'r', errors='replace') as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if obj.get('type') != 'user':
                continue
            if 'toolUseResult' in obj:
                continue

            msg = obj.get('message', {})
            if msg.get('role') != 'user':
                continue

            user_msg_num += 1
            content = msg.get('content')
            text = extract_text_from_content(content)

            if not text:
                continue

            if is_user_request(text):
                display_text = text.replace('\n', ' ').replace('\r', '')
                display_text = re.sub(r'\s+', ' ', display_text).strip()
                results.append({
                    'msg_num': user_msg_num,
                    'text': display_text[:300],
                    'full_length': len(text),
                    'dedup_key': normalize_for_dedup(display_text),
                })

    return results


def main():
    session_files = []
    for f in SESSION_DIR.glob('*.jsonl'):
        size = f.stat().st_size
        if size >= MIN_FILE_SIZE:
            mtime = f.stat().st_mtime
            session_files.append((f, size, mtime))

    session_files.sort(key=lambda x: x[2], reverse=True)

    print(f"Found {len(session_files)} session files > 5MB")
    print()

    # Collect all results across sessions
    all_results = []  # (session_id, mod_date, size_mb, result)
    session_summaries = []

    for filepath, size, mtime in session_files:
        session_id = filepath.stem
        size_mb = size / (1024 * 1024)
        mod_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

        results = process_session_file(filepath)
        session_summaries.append((session_id, mod_date, size_mb, len(results)))

        for r in results:
            all_results.append((session_id, mod_date, size_mb, r))

    # Deduplicate: keep only unique requests (first occurrence by date, newest first)
    seen_keys = set()
    unique_results = []
    duplicate_count = 0

    for session_id, mod_date, size_mb, r in all_results:
        key = r['dedup_key']
        if key in seen_keys:
            duplicate_count += 1
            continue
        seen_keys.add(key)
        unique_results.append((session_id, mod_date, size_mb, r))

    # Print unique requests
    print(f"{'=' * 120}")
    print(f"UNIQUE USER REQUESTS ({len(unique_results)} unique, {duplicate_count} duplicates filtered)")
    print(f"{'=' * 120}")

    for i, (session_id, mod_date, size_mb, r) in enumerate(unique_results[:MAX_RESULTS]):
        truncated = "..." if r['full_length'] > 300 else ""
        print(f"\n  #{i+1:3d} | Session: {session_id[:12]}... | {mod_date} | Msg #{r['msg_num']}")
        print(f"       {r['text']}{truncated}")

    # Print session summary
    print(f"\n{'=' * 120}")
    print(f"SESSION SUMMARY (sorted by date, newest first)")
    print(f"{'=' * 120}")
    print(f"  {'Session UUID':<40} {'Modified':<18} {'Size':>8} {'Requests':>10}")
    print(f"  {'-'*40} {'-'*18} {'-'*8} {'-'*10}")
    for sid, md, smb, cnt in session_summaries:
        print(f"  {sid:<40} {md:<18} {smb:>7.1f}M {cnt:>10}")

    print(f"\n  Total sessions: {len(session_summaries)}")
    print(f"  Total unique requests: {len(unique_results)}")
    print(f"  Total duplicates filtered: {duplicate_count}")


if __name__ == '__main__':
    main()
