#!/usr/bin/env python3
"""Clip video segments based on subtitle timing ranges provided by AI analysis."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable, List, Tuple


def check_ffmpeg() -> None:
    """Check if ffmpeg is available in the system PATH."""
    if shutil.which("ffmpeg") is None:
        print(
            "Error: ffmpeg not found. Please install ffmpeg:\n"
            "  macOS:   brew install ffmpeg\n"
            "  Ubuntu:  sudo apt install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/download.html",
            file=sys.stderr,
        )
        sys.exit(1)


@dataclass
class Cue:
    """Subtitle cue with timing and text."""

    start: float
    end: float
    lines: List[str]

    @property
    def text(self) -> str:
        return " ".join(line.strip() for line in self.lines).strip()


def parse_timestamp(raw: str) -> float:
    """Convert VTT/SRT timestamp to seconds."""
    raw = raw.strip().replace(",", ".")
    parts = raw.split(":")
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
    elif len(parts) == 2:
        hours = 0
        minutes = int(parts[0])
        seconds = float(parts[1])
    else:
        raise ValueError(f"Unrecognized timestamp: {raw}")
    return hours * 3600 + minutes * 60 + seconds


def format_timestamp(seconds: float, style: str) -> str:
    """Convert seconds to VTT/SRT timestamp."""
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    secs_ms = total_ms % 60_000
    secs = secs_ms / 1000.0
    stamp = f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    if style == "srt":
        return stamp.replace(".", ",")
    return stamp


def parse_time_line(line: str) -> Tuple[str, str]:
    """Parse a timestamp line like '00:00:01.000 --> 00:00:03.000'."""
    parts = line.split("-->")
    if len(parts) < 2:
        raise ValueError(f"Invalid time line: {line}")
    start = parts[0].strip()
    end = parts[1].strip().split()[0]
    return start, end


def _parse_cues_core(lines: List[str], skip_line_num: bool = False) -> List[Cue]:
    """Core parsing logic shared by VTT and SRT."""
    cues: List[Cue] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip("\ufeff").strip()
        if not line:
            i += 1
            continue
        if line.startswith("WEBVTT"):
            i += 1
            continue
        if line.startswith("NOTE") or line.startswith("STYLE"):
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue
        if skip_line_num and line.isdigit():
            i += 1
            if i >= len(lines):
                break
            line = lines[i].strip()
        if "-->" not in line:
            i += 1
            continue
        start_raw, end_raw = parse_time_line(line)
        start = parse_timestamp(start_raw)
        end = parse_timestamp(end_raw)
        i += 1
        text_lines: List[str] = []
        while i < len(lines) and lines[i].strip():
            text_lines.append(lines[i].rstrip("\n"))
            i += 1
        cues.append(Cue(start=start, end=end, lines=text_lines))
        while i < len(lines) and not lines[i].strip():
            i += 1
    return cues


def parse_vtt(lines: List[str]) -> List[Cue]:
    """Parse VTT subtitle format."""
    return _parse_cues_core(lines, skip_line_num=False)


def parse_srt(lines: List[str]) -> List[Cue]:
    """Parse SRT subtitle format."""
    return _parse_cues_core(lines, skip_line_num=True)


def load_subtitles(path: str) -> Tuple[List[Cue], str]:
    """Load subtitles from file and return cues with format."""
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()
    if ext == ".vtt":
        return parse_vtt(lines), "vtt"
    if ext == ".srt":
        return parse_srt(lines), "srt"
    raise ValueError(f"Unsupported subtitle format: {ext}")


def write_vtt(cues: Iterable[Cue], path: str) -> None:
    """Write cues to VTT file."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("WEBVTT\n\n")
        for cue in cues:
            handle.write(
                f"{format_timestamp(cue.start, 'vtt')} --> {format_timestamp(cue.end, 'vtt')}\n"
            )
            for line in cue.lines:
                handle.write(f"{line}\n")
            handle.write("\n")


def write_srt(cues: Iterable[Cue], path: str) -> None:
    """Write cues to SRT file."""
    with open(path, "w", encoding="utf-8") as handle:
        for idx, cue in enumerate(cues, start=1):
            handle.write(f"{idx}\n")
            handle.write(
                f"{format_timestamp(cue.start, 'srt')} --> {format_timestamp(cue.end, 'srt')}\n"
            )
            for line in cue.lines:
                handle.write(f"{line}\n")
            handle.write("\n")


def shift_cues(cues: List[Cue], offset: float) -> List[Cue]:
    """Shift cue timestamps by offset (for segment subtitles)."""
    return [
        Cue(start=cue.start - offset, end=cue.end - offset, lines=cue.lines)
        for cue in cues
    ]


def clip_video(
    video_path: str,
    start: float,
    end: float,
    output_path: str,
) -> None:
    """Clip video segment using ffmpeg."""
    duration = max(0.0, end - start)
    cmd = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        video_path,
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_path,
    ]
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=3600,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"FFmpeg timed out while clipping {video_path} from {start:.3f}s to {end:.3f}s"
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"FFmpeg failed to clip {video_path} from {start:.3f}s to {end:.3f}s:\n"
            f"stderr: {e.stderr}\n"
            f"stdout: {e.stdout}"
        )


def _process_segment(args: Tuple[str, List[Cue], int, int, int, str, str]) -> None:
    """Process a single segment (clip video + write subtitles)."""
    video_path, cues, start_pos, end_pos, idx, subtitle_ext, base_name = args
    seg_start = cues[start_pos].start
    seg_end = cues[end_pos - 1].end
    seg_cues = shift_cues(cues[start_pos:end_pos], seg_start)
    base_dir = os.path.dirname(video_path)
    video_out = os.path.join(base_dir, f"{base_name}_{idx}.mp4")
    subtitle_out = os.path.join(base_dir, f"{base_name}_{idx}.{subtitle_ext}")
    clip_video(video_path, seg_start, seg_end, video_out)
    if subtitle_ext == "vtt":
        write_vtt(seg_cues, subtitle_out)
    else:
        write_srt(seg_cues, subtitle_out)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clip video segments based on AI-provided subtitle indices."
    )
    parser.add_argument("video", help="Path to source video file.")
    parser.add_argument("subtitles", help="Path to subtitle file (.vtt or .srt).")
    parser.add_argument(
        "segments",
        help="Segment ranges as 'start_idx-end_idx,start_idx-end_idx,...' (0-based cue indices). Example: '0-12,12-25,25-40'",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers for video clipping.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print segment plan without clipping.",
    )
    args = parser.parse_args()

    check_ffmpeg()
    cues, subtitle_ext = load_subtitles(args.subtitles)

    segment_ranges = []
    for seg_str in args.segments.split(","):
        start_end = seg_str.strip().split("-")
        if len(start_end) != 2:
            print(f"Invalid segment format: {seg_str}", file=sys.stderr)
            return 1
        start_idx = int(start_end[0])
        end_idx = int(start_end[1])
        segment_ranges.append((start_idx, end_idx))

    if args.dry_run:
        for idx, (start_pos, end_pos) in enumerate(segment_ranges, start=1):
            start_time = cues[start_pos].start
            end_time = cues[end_pos - 1].end
            print(
                f"{idx}: cues[{start_pos}:{end_pos}] = {start_time:.3f}s -> {end_time:.3f}s ({end_time - start_time:.2f}s)"
            )
        return 0

    base_name = os.path.splitext(os.path.basename(args.video))[0]
    segment_args = [
        (args.video, cues, start_pos, end_pos, idx, subtitle_ext, base_name)
        for idx, (start_pos, end_pos) in enumerate(segment_ranges, start=1)
    ]

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(_process_segment, arg): arg[3] for arg in segment_args
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                future.result()
                print(f"Completed segment {idx}")
            except Exception as e:
                print(f"Error processing segment {idx}: {e}", file=sys.stderr)
                raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
