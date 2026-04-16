#!/usr/bin/env python3
"""
detect-input.py — Detect URL vs plain text, fetch content if URL.
Usage: python3 detect-input.py <state_file>
Reads state.input_raw, writes state.input_type + state.fetched_content atomically.
"""
import json, os, re, sys

URL_RE = re.compile(r'^https?://', re.IGNORECASE)

def fetch_url(url):
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Strip HTML tags simply
        text = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:8000]  # cap at 8k chars
    except Exception as e:
        return f"[fetch error: {e}]"

def atomic_write(state_file, state):
    tmp = state_file + ".tmp." + str(os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_file)

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: detect-input.py <state_file>\n")
        sys.exit(1)

    state_file = sys.argv[1]
    state = json.load(open(state_file, encoding="utf-8"))
    input_raw = state.get("input_raw", "")

    if URL_RE.match(input_raw.strip()):
        print(f"Detected URL: {input_raw.strip()}", flush=True)
        state["input_type"] = "url"
        state["fetched_content"] = fetch_url(input_raw.strip())
        print(f"Fetched {len(state['fetched_content'])} chars", flush=True)
    else:
        state["input_type"] = "text"
        state["fetched_content"] = input_raw
        print("Detected plain text input", flush=True)

    atomic_write(state_file, state)

if __name__ == "__main__":
    main()
