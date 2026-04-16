# Evolution Log

## 2026-03-02 — Initial Creation

**Origin**: Manual workflow developed during a session to download ~12-hour YouTube audiobook content and transfer to BookPlayer on iPhone via USB.

**Pipeline**: `yt-dlp` → `exiftool` → `pymobiledevice3` HouseArrest API

**Key Discoveries**:

1. **VendDocuments vs VendContainer**: The `pymobiledevice3 apps push` CLI command uses VendContainer mode internally. BookPlayer exposes its Documents directory via VendDocuments mode. The CLI command fails silently — no error, but the file never appears in BookPlayer. The Python API with `documents_only=True` parameter correctly uses VendDocuments mode and works.

2. **BookPlayer auto-import**: Files placed in `/Documents/` are automatically detected by BookPlayer on next app launch. No special naming convention required — BookPlayer reads M4A metadata (title, artist, album) for display.

3. **Large file handling**: ~12-hour audiobooks produce ~300-500MB M4A files. The `set_file_contents()` API handles these without issue, but reading entire files into memory is required. For extremely large files (>1GB), chunked approaches may be needed.

4. **yt-dlp audio quality**: `--audio-quality 0` gives the best available quality. Combined with `--audio-format m4a`, yt-dlp auto-invokes ffmpeg for conversion. The `%(title).100B` template truncates filenames to 100 bytes to avoid filesystem issues.

5. **Metadata tagging**: exiftool's `-Title`, `-Artist`, `-Album` tags map directly to what BookPlayer displays. The `-overwrite_original` flag prevents `.m4a_original` backup files cluttering the temp directory.

**Codified as**: `media-tools:youtube-to-bookplayer` skill in cc-skills marketplace.
