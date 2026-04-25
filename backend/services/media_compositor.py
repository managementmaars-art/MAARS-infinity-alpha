"""ffmpeg-backed video compositor.

The Video Creator office's SOP ends with a `composite` step: stitch a
list of clip URLs in scene order, overlay a voice-over track, optionally
burn subtitles, and return a single MP4. This module owns that step so
the workflow tool + admin `run_sop` path share one implementation.

ffmpeg is called via `asyncio.create_subprocess_exec` — no python-ffmpeg
wrapper — so the only dependency is the `ffmpeg` binary on PATH. On
Windows installs without ffmpeg, `composite_video` raises a clear error
the route bubbles up to the operator UI.
"""
from __future__ import annotations
import asyncio
import logging
import shutil
import uuid
from pathlib import Path
from typing import Any, Optional

from shared.constants import UPLOAD_DIR
from services.storage import fetch_to_file, upload_bytes

logger = logging.getLogger(__name__)


RES_MAP = {
    "4k":    (3840, 2160),
    "1080p": (1920, 1080),
    "720p":  (1280,  720),
    "480p":  ( 854,  480),
}
ASPECT_OVERRIDES = {
    "9:16":  lambda w, h: (h,  w),    # swap for vertical
    "1:1":   lambda w, h: (h,  h),
    "16:9":  lambda w, h: (w,  h),
    "4:3":   lambda w, h: (int(h * 4 / 3), h),
}


def _resolve_size(resolution: str, aspect: str) -> tuple[int, int]:
    base = RES_MAP.get((resolution or "720p").lower(), RES_MAP["720p"])
    transformer = ASPECT_OVERRIDES.get(aspect or "16:9")
    if transformer is None:
        return base
    return transformer(*base)


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


async def _run(cmd: list[str]) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    return proc.returncode or 0, stderr.decode("utf-8", errors="replace")[-2000:]


async def _write_srt(items: list[dict], path: Path) -> None:
    """Convert a simple subtitles list [{start_s,end_s,text}] to an SRT file."""
    def fmt(t: float) -> str:
        ms = int((t - int(t)) * 1000)
        t = int(t)
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    lines: list[str] = []
    for i, sub in enumerate(items, start=1):
        start = float(sub.get("start_s", 0))
        end   = float(sub.get("end_s", start + 2))
        text  = str(sub.get("text", "")).strip()
        lines.append(str(i))
        lines.append(f"{fmt(start)} --> {fmt(end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


async def composite_video(
    clip_urls: list[str],
    *,
    audio_url: Optional[str] = None,
    subtitles: Optional[Any] = None,
    aspect: str = "16:9",
    resolution: str = "720p",
    filename: Optional[str] = None,
    user_id: Optional[str] = None,
) -> dict:
    """Stitch clips → overlay audio → optionally burn subtitles → write MP4.

    Returns: {video_url, thumbnail_url, duration_s, width, height,
              provider:"ffmpeg", clip_count}.

    Raises RuntimeError if ffmpeg is not on PATH or the composite fails.
    """
    if not _ffmpeg_available():
        raise RuntimeError(
            "ffmpeg binary not found on PATH. Install ffmpeg to enable "
            "video compositing (https://ffmpeg.org/download.html)."
        )
    if not clip_urls:
        raise RuntimeError("composite_video: clip_urls is empty")

    width, height = _resolve_size(resolution, aspect)
    work_dir = Path(UPLOAD_DIR) / f"composite_{uuid.uuid4().hex[:8]}"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Download every remote clip to local tmp files.
    local_clips: list[Path] = []
    for i, url in enumerate(clip_urls):
        try:
            p = await fetch_to_file(url, suffix=f"_clip{i:02d}.mp4")
        except Exception as exc:
            raise RuntimeError(f"clip {i} fetch failed: {exc}")
        local_clips.append(p)

    # 2. Normalize each clip to the target size + framerate so concat works
    #    regardless of source resolution. Writes intermediate *.norm.mp4.
    normalized: list[Path] = []
    for i, clip in enumerate(local_clips):
        out = work_dir / f"norm_{i:02d}.mp4"
        rc, err = await _run([
            "ffmpeg", "-y", "-i", str(clip),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                   f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps=30",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-an",  # drop source audio — we overlay voice-over separately
            str(out),
        ])
        if rc != 0 or not out.exists():
            raise RuntimeError(f"normalize clip {i} failed: {err[:500]}")
        normalized.append(out)

    # 3. Concat list file + concat demuxer pass.
    list_file = work_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in normalized),
        encoding="utf-8",
    )
    stitched = work_dir / "stitched.mp4"
    rc, err = await _run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy", str(stitched),
    ])
    if rc != 0 or not stitched.exists():
        raise RuntimeError(f"concat failed: {err[:500]}")

    # 4. Overlay voice-over if provided.
    with_audio = stitched
    if audio_url:
        audio_path = await fetch_to_file(audio_url, suffix=".mp3")
        with_audio = work_dir / "with_audio.mp4"
        rc, err = await _run([
            "ffmpeg", "-y", "-i", str(stitched), "-i", str(audio_path),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(with_audio),
        ])
        if rc != 0 or not with_audio.exists():
            raise RuntimeError(f"audio overlay failed: {err[:500]}")

    # 5. Burn subtitles if provided.
    final = with_audio
    if subtitles:
        if isinstance(subtitles, str) and subtitles.endswith(".srt"):
            srt_path = await fetch_to_file(subtitles, suffix=".srt")
        elif isinstance(subtitles, list):
            srt_path = work_dir / "subs.srt"
            await _write_srt(subtitles, srt_path)
        else:
            srt_path = None
        if srt_path:
            final = work_dir / "final.mp4"
            # Escape colon/backslash per ffmpeg's subtitles filter syntax.
            fpath = str(srt_path).replace("\\", "/").replace(":", r"\:")
            rc, err = await _run([
                "ffmpeg", "-y", "-i", str(with_audio),
                "-vf", f"subtitles='{fpath}'",
                "-c:a", "copy", str(final),
            ])
            if rc != 0 or not final.exists():
                raise RuntimeError(f"subtitle burn failed: {err[:500]}")

    # 6. Extract a thumbnail at 1s.
    thumb_path = work_dir / "thumb.jpg"
    await _run([
        "ffmpeg", "-y", "-i", str(final), "-ss", "1", "-frames:v", "1",
        "-q:v", "3", str(thumb_path),
    ])

    # 7. Probe duration.
    duration_s: Optional[float] = None
    if shutil.which("ffprobe"):
        rc, out = await _run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(final),
        ])
        try:
            duration_s = float(out.strip().splitlines()[-1])
        except Exception:
            duration_s = None

    # 8. Publish to /files/ via upload_bytes (re-read -> write).
    out_name = filename or f"composite_{uuid.uuid4().hex[:10]}.mp4"
    video_url = await upload_bytes(final.read_bytes(), out_name,
                                   content_type="video/mp4", user_id=user_id)
    thumb_url = None
    if thumb_path.exists():
        thumb_url = await upload_bytes(
            thumb_path.read_bytes(),
            out_name.rsplit(".", 1)[0] + "_thumb.jpg",
            content_type="image/jpeg", user_id=user_id,
        )

    return {
        "video_url":     video_url,
        "thumbnail_url": thumb_url,
        "duration_s":    duration_s,
        "width":         width,
        "height":        height,
        "clip_count":    len(clip_urls),
        "provider":      "ffmpeg",
        "has_audio":     bool(audio_url),
        "has_subtitles": bool(subtitles),
    }
