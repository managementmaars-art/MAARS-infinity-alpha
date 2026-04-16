# Troubleshooting

## Known Issues

| Problem                                                         | Cause                                                      | Solution                                                                                 |
| --------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `pymobiledevice3 usbmux list` returns empty                     | No device connected, or missing USB trust                  | Connect iPhone via USB cable, unlock device, tap "Trust This Computer" if prompted       |
| `pymobiledevice3 apps push` succeeds but file not in BookPlayer | CLI uses VendContainer mode; BookPlayer uses VendDocuments | Use Python API with `documents_only=True` — see [tool-reference.md](./tool-reference.md) |
| BookPlayer shows file but wrong title/artist                    | Missing or incorrect metadata tags                         | Run `exiftool -Title="..." -Artist="..." file.m4a` before pushing                        |
| BookPlayer doesn't see newly pushed file                        | App needs restart to scan `/Documents/`                    | Force-quit BookPlayer and reopen; file should appear                                     |
| `yt-dlp` returns HTTP 403                                       | YouTube rate limiting or geo-restriction                   | Wait a few minutes and retry; try with `--cookies-from-browser safari` if persistent     |
| `yt-dlp` errors about ffmpeg                                    | ffmpeg not installed                                       | `brew install ffmpeg`                                                                    |
| Python script fails with `ConnectionFailedError`                | Device locked or USB not trusted                           | Unlock iPhone, re-plug USB, tap "Trust"                                                  |
| `lockdown` creation fails with pairing error                    | Device has never been paired with this Mac                 | Open Finder, click the device, confirm trust on both Mac and iPhone                      |
| Out of memory during large file push                            | File read into memory exceeds available RAM                | Rare for audio files (<1GB); if hit, close other apps or use chunked read                |
| `uvx` not found                                                 | mise/uv not in PATH                                        | Ensure `mise` is activated in your shell profile                                         |

## Diagnostic Commands

```bash
# Check all tool availability
command -v yt-dlp && echo "yt-dlp: OK" || echo "yt-dlp: MISSING"
command -v ffmpeg && echo "ffmpeg: OK" || echo "ffmpeg: MISSING"
command -v exiftool && echo "exiftool: OK" || echo "exiftool: MISSING"
command -v pymobiledevice3 && echo "pmd3: OK" || echo "pmd3: MISSING (use uvx)"

# List connected iOS devices
pymobiledevice3 usbmux list

# Check if BookPlayer is installed
pymobiledevice3 apps list --no-color 2>/dev/null | grep -i bookplayer

# Test HouseArrest access (Python)
uvx --python 3.13 --from pymobiledevice3 python3 -c '
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.house_arrest import HouseArrestService
lockdown = create_using_usbmux()
svc = HouseArrestService(lockdown=lockdown, bundle_id="com.tortugapower.audiobookplayer", documents_only=True)
print("Documents:", svc.listdir("/Documents/"))
'

# Check yt-dlp can reach a URL (metadata only, no download)
yt-dlp --dump-json --no-download "https://www.youtube.com/watch?v=EXAMPLE"
```
