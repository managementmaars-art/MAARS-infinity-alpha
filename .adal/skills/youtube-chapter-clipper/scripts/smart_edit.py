#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

TIME_RE = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})")
SAFE_CHARS_RE = re.compile(r"[^A-Za-z0-9_-]+")


@dataclass
class Cue:
    start: float
    end: float
    text: str


@dataclass
class Chapter:
    start: float
    end: float
    title: str
    reason: str


def run_cmd(cmd: List[str]) -> None:
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def run_cmd_capture(cmd: List[str]) -> str:
    result = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def check_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing tool: {name}")


def parse_timecode(ts: str) -> float:
    hh, mm, rest = ts.split(":")
    ss, ms = rest.split(".")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0


def format_timecode(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    hh = total // 3600
    mm = (total % 3600) // 60
    ss = total % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}.{ms:03d}"


def parse_vtt(path: str) -> List[Cue]:
    cues: List[Cue] = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = TIME_RE.match(line)
        if not match:
            i += 1
            continue
        start = parse_timecode(match.group(1))
        end = parse_timecode(match.group(2))
        i += 1
        text_lines = []
        while i < len(lines) and lines[i].strip() != "":
            text_lines.append(lines[i].strip())
            i += 1
        text = " ".join(text_lines).strip()
        if text:
            cues.append(Cue(start=start, end=end, text=text))
        i += 1
    return cues


def is_sentence_boundary(text: str) -> bool:
    text = text.strip()
    return text.endswith(".") or text.endswith("!") or text.endswith("?")


def sanitize_title(text: str, max_words: int = 8) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        return "chapter"
    return "_".join(words[:max_words])


def sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")
    name = SAFE_CHARS_RE.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "untitled"


def build_chapters(cues: List[Cue], min_s: int, target_s: int, max_s: int) -> List[Chapter]:
    chapters: List[Chapter] = []
    if not cues:
        return chapters

    start_idx = 0
    chapter_start = cues[0].start

    i = 0
    while i < len(cues):
        cue = cues[i]
        chapter_end = cue.end
        duration = chapter_end - chapter_start

        should_cut = False
        reason = ""
        if duration >= min_s:
            if duration >= max_s:
                should_cut = True
                reason = "max_duration"
            elif duration >= target_s and is_sentence_boundary(cue.text):
                should_cut = True
                reason = "sentence_boundary"

        if should_cut:
            chapter_text = " ".join(c.text for c in cues[start_idx : i + 1])
            title = sanitize_title(chapter_text)
            chapters.append(Chapter(start=chapter_start, end=chapter_end, title=title, reason=reason))
            start_idx = i + 1
            if start_idx < len(cues):
                chapter_start = cues[start_idx].start
            i += 1
            continue

        i += 1

    if start_idx < len(cues):
        chapter_text = " ".join(c.text for c in cues[start_idx:])
        title = sanitize_title(chapter_text)
        chapters.append(Chapter(start=chapter_start, end=cues[-1].end, title=title, reason="tail"))

    return chapters


def dedupe_titles(chapters: List[Chapter]) -> List[Chapter]:
    seen = {}
    out: List[Chapter] = []
    for ch in chapters:
        base = sanitize_filename(ch.title)
        count = seen.get(base, 0) + 1
        seen[base] = count
        if count > 1:
            title = f"{base}_{count}"
        else:
            title = base
        out.append(Chapter(start=ch.start, end=ch.end, title=title, reason=ch.reason))
    return out


def resolve_id(url: Optional[str], vid: Optional[str]) -> str:
    if vid:
        return vid
    if not url:
        raise RuntimeError("Provide --url or --id")
    return run_cmd_capture(["yt-dlp", "--print", "%(id)s", url])


def resolve_title(url: Optional[str], title: Optional[str], vid: str) -> str:
    if title:
        return title
    if url:
        try:
            return run_cmd_capture(["yt-dlp", "--print", "%(title)s", url])
        except Exception:
            return vid
    return vid


def maybe_download(url: Optional[str], vid: str, vtt_path: str, mp4_path: str) -> None:
    if os.path.exists(vtt_path) and os.path.exists(mp4_path):
        return
    if not url:
        raise RuntimeError("Missing files and no --url provided for download")
    cmd = [
        "yt-dlp",
        "-f",
        "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b",
        "--merge-output-format",
        "mp4",
        "--write-subs",
        "--sub-langs",
        "en",
        "--sub-format",
        "vtt",
        "--write-auto-subs",
        "--convert-subs",
        "vtt",
        "--output",
        f"{vid}.%(ext)s",
        url,
    ]
    run_cmd(cmd)


def resolve_vtt(vid: str) -> str:
    vtt = f"{vid}.en.vtt"
    auto_vtt = f"{vid}.en.auto.vtt"
    if os.path.exists(vtt):
        return vtt
    if os.path.exists(auto_vtt):
        return auto_vtt
    raise RuntimeError("No English VTT subtitle found")


def probe_streams(path: str) -> Dict[str, str]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height",
        "-of",
        "csv=p=0",
        path,
    ]
    output = run_cmd_capture(cmd).strip()
    info: Dict[str, str] = {}
    if output:
        parts = output.split(",")
        if len(parts) >= 1:
            info["vcodec"] = parts[0].strip()
        if len(parts) >= 2:
            info["width"] = parts[1].strip()
        if len(parts) >= 3:
            info["height"] = parts[2].strip()
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "csv=p=0",
        path,
    ]
    output = run_cmd_capture(cmd).strip()
    if output:
        info["acodec"] = output.split(",")[0].strip()
    return info


def cut_clip(
    mp4_path: str,
    out_path: str,
    start: float,
    end: float,
    *,
    fast: bool,
    scale_width: int,
) -> None:
    duration = max(0.0, end - start)
    if fast:
        info = probe_streams(mp4_path)
        vcodec = info.get("vcodec", "")
        acodec = info.get("acodec", "")
        can_copy = vcodec in {"h264", "avc1"} and acodec == "aac"
        if can_copy:
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-y",
                "-ss",
                format_timecode(start),
                "-i",
                mp4_path,
                "-t",
                format_timecode(duration),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                out_path,
            ]
            run_cmd(cmd)
            return

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-ss" if fast else "-i",
    ]
    if fast:
        cmd.extend([format_timecode(start), "-i", mp4_path, "-t", format_timecode(duration)])
    else:
        cmd.extend([mp4_path, "-ss", format_timecode(start), "-to", format_timecode(end)])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast" if fast else "veryfast",
            "-crf",
            "28" if fast else "23",
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
        ]
    )
    if fast and scale_width > 0:
        cmd.extend(["-vf", f"scale='min({scale_width},iw)':-2"])
    cmd.extend(["-movflags", "+faststart", out_path])
    run_cmd(cmd)


def validate_clip(path: str) -> None:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        path,
    ]
    run_cmd(cmd)


def extract_vtt_segment(vtt_path: str, out_path: str, start: float, end: float) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-ss",
        format_timecode(start),
        "-to",
        format_timecode(end),
        "-i",
        vtt_path,
        out_path,
    ]
    run_cmd(cmd)


def vtt_to_srt(vtt_path: str, out_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        vtt_path,
        out_path,
    ]
    run_cmd(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart edit YouTube clips from VTT")
    parser.add_argument("--url", help="YouTube URL")
    parser.add_argument("--id", dest="vid", help="Video id if URL is not provided")
    parser.add_argument("--title", help="Override output directory title")
    parser.add_argument(
        "--chapter-preset",
        choices=["1-2", "2-3", "3-4", "custom"],
        default="2-3",
        help="Chapter length preset in minutes",
    )
    parser.add_argument("--min-seconds", type=int, default=120)
    parser.add_argument("--target-seconds", type=int, default=180)
    parser.add_argument("--max-seconds", type=int, default=240)
    parser.add_argument("--mode", choices=["fast", "accurate"], default="fast")
    parser.add_argument("--scale-width", type=int, default=1280)
    parser.add_argument("--keep-vtt", action="store_true")
    args = parser.parse_args()

    check_tool("ffmpeg")
    check_tool("ffprobe")
    check_tool("yt-dlp")

    vid = resolve_id(args.url, args.vid)
    mp4_path = f"{vid}.mp4"
    vtt_path = f"{vid}.en.vtt"

    maybe_download(args.url, vid, vtt_path, mp4_path)
    vtt_path = resolve_vtt(vid)

    title = resolve_title(args.url, args.title, vid)
    out_dir = sanitize_filename(title)
    os.makedirs(out_dir, exist_ok=True)

    if args.chapter_preset != "custom":
        preset_map = {
            "1-2": (60, 90, 120),
            "2-3": (120, 150, 180),
            "3-4": (180, 210, 240),
        }
        args.min_seconds, args.target_seconds, args.max_seconds = preset_map[args.chapter_preset]

    cues = parse_vtt(vtt_path)
    chapters = build_chapters(cues, args.min_seconds, args.target_seconds, args.max_seconds)
    chapters = dedupe_titles(chapters)

    for idx, ch in enumerate(chapters, start=1):
        prefix = f"{idx:02d}_"
        base = f"{prefix}{ch.title}"
        clip_path = os.path.join(out_dir, f"{base}.mp4")
        chapter_vtt = os.path.join(out_dir, f"{base}.vtt")
        chapter_srt = os.path.join(out_dir, f"{base}.en.srt")

        cut_clip(
            mp4_path,
            clip_path,
            ch.start,
            ch.end,
            fast=args.mode == "fast",
            scale_width=args.scale_width,
        )
        try:
            validate_clip(clip_path)
        except Exception:
            try:
                os.remove(clip_path)
            except OSError:
                pass
            cut_clip(
                mp4_path,
                clip_path,
                ch.start,
                ch.end,
                fast=args.mode == "fast",
                scale_width=args.scale_width,
            )
            validate_clip(clip_path)
        extract_vtt_segment(vtt_path, chapter_vtt, ch.start, ch.end)
        vtt_to_srt(chapter_vtt, chapter_srt)
        if not args.keep_vtt:
            try:
                os.remove(chapter_vtt)
            except OSError:
                pass

    print(f"output_dir={out_dir}")
    for idx, ch in enumerate(chapters, start=1):
        print(f"{idx:02d} {format_timecode(ch.start)} {format_timecode(ch.end)} {ch.title} {ch.reason}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
