---
name: copy-as-image
version: 1.0.0
description: Copy Claude's last response as a beautiful terminal-style image to your clipboard. Use when you want to share Claude's output in Slack, docs, or presentations.
metadata:
  requires:
    bins: ["node"]
---

# Copy as Image

Capture the last meaningful Claude response as a styled terminal screenshot image and copy it to the clipboard.

## Selecting the right response

Look back through the conversation and find your **last substantial assistant response**. Skip over any of the following:

- One-line or very short replies (e.g. "Done.", "OK", "Sure")
- Slash command outputs (messages that start with `/`)
- Tool invocation confirmations
- This current skill invocation itself

Pick the most recent assistant message that has **meaningful multi-line content** (explanations, code, analysis, etc.).

## Steps

Do everything in a **single** Bash call. Use a timestamp-based temp file name (do NOT use mktemp with XXXXXX templates). Write the response, run the script, and clean up:

```bash
TMPFILE="/tmp/claude-response-$(date +%s%N).md"
SKILL_DIR="${CLAUDE_SKILL_DIR}"

cat > "$TMPFILE" << 'CLAUDE_EOF'
<paste the full text of the chosen response here>
CLAUDE_EOF

cd "$SKILL_DIR/scripts" && \
  (test -d ../node_modules || npm install --prefix .. --omit=dev 2>/dev/null) && \
  node copy-as-image.mjs "$TMPFILE"

rm -f "$TMPFILE"
```

After the command finishes, tell the user:
- "Image copied to clipboard! Paste anywhere with Cmd+V (macOS) or Ctrl+V (Linux)."
- Show the saved PNG file path from the script output.

## Important Notes

- Only requires **Node.js** (no bun/deno needed)
- Works on **macOS** (uses `osascript`) and **Linux** (requires `xclip` or `xsel`)
- The image uses a dark terminal theme with One Dark syntax highlighting
- Output is rendered at 2x resolution for Retina/HiDPI displays
