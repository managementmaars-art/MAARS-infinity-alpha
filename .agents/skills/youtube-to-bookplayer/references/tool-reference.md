# Tool Reference

## yt-dlp

YouTube audio extraction tool. Handles authentication, format selection, and download.

### Key Flags

| Flag                     | Purpose                                                      |
| ------------------------ | ------------------------------------------------------------ |
| `-x` / `--extract-audio` | Extract audio only (no video)                                |
| `--audio-format m4a`     | Convert to M4A (AAC) — BookPlayer's preferred format         |
| `--audio-quality 0`      | Best available audio quality                                 |
| `--no-playlist`          | Download single video even if URL is part of a playlist      |
| `--dump-json`            | Print metadata JSON without downloading (for preview)        |
| `--no-download`          | Skip download (combine with `--dump-json` for metadata only) |
| `-o TEMPLATE`            | Output filename template                                     |

### Output Template

```bash
yt-dlp -x --audio-format m4a --audio-quality 0 --no-playlist \
  -o "$WORK_DIR/%(title).100B.%(ext)s" "$URL"
```

- `%(title).100B` — Video title, truncated to 100 bytes (avoids filesystem path limits)
- `%(ext)s` — File extension (will be `m4a` after conversion)

### Metadata JSON (Key Fields)

```bash
yt-dlp --dump-json --no-download "$URL"
```

Useful fields: `title`, `duration` (seconds), `channel`, `upload_date`, `description`, `thumbnail`.

---

## pymobiledevice3

Python library and CLI for iOS device communication via USB.

### Critical: VendDocuments API (Python)

BookPlayer uses **VendDocuments** mode. The CLI `apps push` command uses VendContainer and **will not work**.

**Correct approach — Python API:**

```python
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.house_arrest import HouseArrestService

lockdown = create_using_usbmux()
bundle_id = "com.tortugapower.audiobookplayer"

service = HouseArrestService(lockdown=lockdown, bundle_id=bundle_id, documents_only=True)
service.set_file_contents(f"/Documents/{filename}", file_data)
```

**Run via uvx:**

```bash
uvx --python 3.13 --from pymobiledevice3 python3 -c '
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.house_arrest import HouseArrestService
# ... script body
'
```

### Anti-Pattern (WRONG — VendContainer)

```bash
# THIS DOES NOT WORK FOR BOOKPLAYER
pymobiledevice3 apps push com.tortugapower.audiobookplayer /path/to/file.m4a
```

The CLI uses VendContainer mode internally. BookPlayer's container is not accessible this way.

### Useful CLI Commands

| Command                                | Purpose                                   |
| -------------------------------------- | ----------------------------------------- |
| `pymobiledevice3 usbmux list`          | List connected iOS devices                |
| `pymobiledevice3 apps list --no-color` | List installed apps (grep for BookPlayer) |

### Listing Files (Verification)

```python
service = HouseArrestService(lockdown=lockdown, bundle_id=bundle_id, documents_only=True)
files = service.listdir("/Documents/")
```

---

## exiftool

Metadata tagging for M4A/AAC audio files.

### Key Tags

| Tag       | Maps To       | BookPlayer Display  |
| --------- | ------------- | ------------------- |
| `-Title`  | Track title   | Main title          |
| `-Artist` | Artist/author | Author line         |
| `-Album`  | Album name    | Collection grouping |

### Usage

```bash
exiftool -overwrite_original \
  -Title="Video Title" \
  -Artist="Channel Name" \
  -Album="YouTube Audio" \
  "/path/to/file.m4a"
```

- `-overwrite_original` prevents creation of `.m4a_original` backup files

---

## ffmpeg

Audio format conversion engine. **Not invoked directly** — yt-dlp calls ffmpeg automatically when `--audio-format m4a` is specified.

### Prerequisite

Must be installed (`brew install ffmpeg`) for yt-dlp's audio extraction to work. yt-dlp will error clearly if ffmpeg is missing.
