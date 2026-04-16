# videodl (videofetch) API Cheatsheet

Use this file when you need the minimal Python API to parse a URL and extract the
download/CDN URL without downloading the video.

## Parse only (no download)

```python
from videodl import videodl as videodl_lib

video_client = videodl_lib.VideoClient(
    allowed_video_sources=["KuaishouVideoClient"]
)
video_infos = video_client.parsefromurl(url)
```

Expected structure (may vary by source). These keys commonly exist:

- `download_url` or `download_urls` (string or list)
- `url` or `urls` (string or list)

Pick the first valid string URL as the CDN URL.
