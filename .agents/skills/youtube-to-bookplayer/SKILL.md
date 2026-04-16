---
name: youtube-to-bookplayer
description: Download YouTube audio and push to BookPlayer on iPhone via USB. TRIGGERS - youtube audio, bookplayer, download youtube, push to iphone, youtube to bookplayer, audiobook from youtube, youtube bookplayer
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: "[YouTube URL]"
---

# youtube-to-bookplayer

Download audio from a YouTube video, tag metadata, and push to BookPlayer on iPhone via USB.

BookPlayer is an iOS audiobook player that resumes playback position — ideal for long-form YouTube content (lectures, audiobooks, podcasts). Files pushed to its `/Documents/` directory are auto-imported on next app launch.

---

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Task Template

Execute phases 0–5 sequentially. Each phase has a `[Preflight]`, `[Ask]`, `[Execute]`, or `[Verify]` tag indicating its nature. **Do not skip phases.**

---

### Phase 0: Preflight [Preflight]

Check all required tools and device connectivity. **Fail fast** — do not proceed if any check fails.

```bash
# Tool availability
TOOLS_OK=true
for tool in yt-dlp ffmpeg exiftool; do
  if command -v "$tool" &>/dev/null; then
    echo "$tool: OK ($(command -v "$tool"))"
  else
    echo "$tool: MISSING"
    TOOLS_OK=false
  fi
done

# pymobiledevice3 (may only be available via uvx)
if command -v pymobiledevice3 &>/dev/null; then
  echo "pymobiledevice3: OK ($(command -v pymobiledevice3))"
else
  if uvx --python 3.13 --from pymobiledevice3 pymobiledevice3 --help &>/dev/null 2>&1; then
    echo "pymobiledevice3: OK (via uvx)"
  else
    echo "pymobiledevice3: MISSING"
    TOOLS_OK=false
  fi
fi

echo "---"
[ "$TOOLS_OK" = true ] && echo "All tools OK" || echo "BLOCKED: Install missing tools (see table below)"
```

**If tools are missing:**

| Tool              | Install Command                                                   |
| ----------------- | ----------------------------------------------------------------- |
| `yt-dlp`          | `brew install yt-dlp`                                             |
| `ffmpeg`          | `brew install ffmpeg`                                             |
| `exiftool`        | `brew install exiftool`                                           |
| `pymobiledevice3` | `uvx --python 3.13 --from pymobiledevice3 pymobiledevice3 --help` |

**Device check** (only after tools pass):

```bash
# Check for connected iOS device
pymobiledevice3 usbmux list 2>/dev/null || uvx --python 3.13 --from pymobiledevice3 pymobiledevice3 usbmux list

# Check BookPlayer is installed
pymobiledevice3 apps list --no-color 2>/dev/null | grep -i "audiobookplayer\|bookplayer" || \
  uvx --python 3.13 --from pymobiledevice3 pymobiledevice3 apps list --no-color 2>/dev/null | grep -i "audiobookplayer\|bookplayer"
```

If no device found: ask user to connect iPhone via USB, unlock it, and tap "Trust This Computer".
If BookPlayer not found: ask user to install BookPlayer from the App Store.

---

### Phase 1: Accept URL & Confirm [Ask]

**If `$ARGUMENTS[0]` is provided**, use it as the YouTube URL. Otherwise, use AskUserQuestion to ask for the URL.

**Preview metadata before proceeding:**

```bash
yt-dlp --dump-json --no-download "$URL" 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
hrs, rem = divmod(int(d.get('duration', 0)), 3600)
mins, secs = divmod(rem, 60)
print(f\"Title:    {d.get('title', 'Unknown')}\")
print(f\"Channel:  {d.get('channel', 'Unknown')}\")
print(f\"Duration: {hrs}h {mins}m {secs}s\")
print(f\"Upload:   {d.get('upload_date', 'Unknown')}\")
"
```

Use AskUserQuestion to confirm:

- Title, channel, duration look correct
- Whether to customize the metadata (title/artist/album) or use defaults from yt-dlp

---

### Phase 2: Download Audio [Execute]

```bash
WORK_DIR=$(mktemp -d)
echo "Working directory: $WORK_DIR"

yt-dlp -x --audio-format m4a --audio-quality 0 --no-playlist \
  -o "$WORK_DIR/%(title).100B.%(ext)s" \
  "$URL"

# Show result
ls -lh "$WORK_DIR"/*.m4a
```

**Notes:**

- `--audio-quality 0` = best available quality
- `%(title).100B` truncates filename to 100 bytes (prevents filesystem issues)
- `--no-playlist` ensures single video download even from playlist URLs
- ffmpeg is auto-invoked by yt-dlp for M4A conversion

---

### Phase 3: Tag Metadata [Execute]

Extract metadata from yt-dlp JSON and apply to the M4A file:

```bash
# Get the downloaded file path
M4A_FILE=$(ls "$WORK_DIR"/*.m4a | head -1)

# Apply metadata (use values confirmed in Phase 1, or yt-dlp defaults)
exiftool -overwrite_original \
  -Title="$TITLE" \
  -Artist="$ARTIST" \
  -Album="YouTube Audio" \
  "$M4A_FILE"

# Verify tags
exiftool -Title -Artist -Album "$M4A_FILE"
```

**Variables** (from Phase 1 confirmation):

- `$TITLE` — Video title (or user-customized)
- `$ARTIST` — Channel name (or user-customized)
- Album defaults to "YouTube Audio" unless user specifies otherwise

---

### Phase 4: Push to BookPlayer [Execute]

> **CRITICAL**: Use the Python API with `documents_only=True`. The CLI `pymobiledevice3 apps push` uses VendContainer mode and **will not work** with BookPlayer.

```bash
M4A_FILE=$(ls "$WORK_DIR"/*.m4a | head -1)
FILENAME=$(basename "$M4A_FILE")

uvx --python 3.13 --from pymobiledevice3 python3 << 'PYEOF'
import sys
from pathlib import Path
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.house_arrest import HouseArrestService

local_path = sys.argv[1] if len(sys.argv) > 1 else None
if not local_path:
    # Find the m4a file from environment
    import glob, os
    work_dir = os.environ.get("WORK_DIR", "/tmp")
    files = glob.glob(os.path.join(work_dir, "*.m4a"))
    if not files:
        print("ERROR: No .m4a file found in work directory")
        sys.exit(1)
    local_path = files[0]

file_path = Path(local_path)
filename = file_path.name
file_data = file_path.read_bytes()
size_mb = len(file_data) / (1024 * 1024)

print(f"Pushing: {filename} ({size_mb:.1f} MB)")

lockdown = create_using_usbmux()
service = HouseArrestService(
    lockdown=lockdown,
    bundle_id="com.tortugapower.audiobookplayer",
    documents_only=True  # CRITICAL: VendDocuments mode
)

service.set_file_contents(f"/Documents/{filename}", file_data)
print(f"SUCCESS: {filename} pushed to BookPlayer /Documents/")
PYEOF
```

**Anti-pattern — DO NOT USE:**

```bash
# WRONG: This uses VendContainer mode and fails silently on BookPlayer
pymobiledevice3 apps push com.tortugapower.audiobookplayer /path/to/file.m4a
```

---

### Phase 5: Verify [Verify]

List BookPlayer's `/Documents/` directory to confirm the file arrived:

```bash
uvx --python 3.13 --from pymobiledevice3 python3 << 'PYEOF'
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.house_arrest import HouseArrestService

lockdown = create_using_usbmux()
service = HouseArrestService(
    lockdown=lockdown,
    bundle_id="com.tortugapower.audiobookplayer",
    documents_only=True
)

files = service.listdir("/Documents/")
print("BookPlayer /Documents/ contents:")
for f in sorted(files):
    if f.startswith('.'):
        continue
    try:
        info = service.stat(f"/Documents/{f}")
        size_mb = info.get('st_size', 0) / (1024 * 1024)
        print(f"  {f} ({size_mb:.1f} MB)")
    except Exception:
        print(f"  {f}")
PYEOF
```

**Report to user:**

- File name and size in BookPlayer
- Duration (from Phase 1 metadata)
- Remind: open BookPlayer on iPhone to see the new file (force-quit and reopen if it doesn't appear)

**Cleanup:**

```bash
# Remove temp working directory
rm -rf "$WORK_DIR"
echo "Cleaned up: $WORK_DIR"
```

---

## Troubleshooting Quick Reference

| Problem                | Quick Fix                                                         |
| ---------------------- | ----------------------------------------------------------------- |
| No device found        | Unlock iPhone, re-plug USB, tap "Trust"                           |
| File not in BookPlayer | You used the CLI — must use Python API with `documents_only=True` |
| Wrong metadata shown   | Re-run Phase 3 with correct `-Title`/`-Artist` values             |

Full troubleshooting: [references/troubleshooting.md](./references/troubleshooting.md)

---

## References

- [Tool Reference](./references/tool-reference.md) — yt-dlp flags, pymobiledevice3 API, exiftool tags
- [Troubleshooting](./references/troubleshooting.md) — Known issues, diagnostic commands
- [Evolution Log](./references/evolution-log.md) — Origin and key discoveries

---

## Post-Change Checklist

When modifying this skill, verify:

- [ ] Phase 0 preflight catches all missing tools with correct install commands
- [ ] Phase 4 uses Python API with `documents_only=True` (never CLI `apps push`)
- [ ] No hardcoded paths — uses `$HOME`, `mktemp`, `command -v`, `create_using_usbmux()`
- [ ] Python commands use `--python 3.13` (per global policy)
- [ ] Anti-pattern warning is preserved in Phase 4

## Post-Execution Reflection

After this skill completes, reflect before closing the task:

0. **Locate yourself.** — Find this SKILL.md's canonical path (Glob for this skill's name) before editing. All corrections target THIS file and its sibling references/ — never other documentation.
1. **What failed?** — Fix the instruction that caused it. If it could recur, add it as an anti-pattern.
2. **What worked better than expected?** — Promote it to recommended practice. Document why.
3. **What drifted?** — Any script, reference, or external dependency that no longer matches reality gets fixed now.
4. **Log it.** — Every change gets an evolution-log entry with trigger, fix, and evidence.

Do NOT defer. The next invocation inherits whatever you leave behind.
---
