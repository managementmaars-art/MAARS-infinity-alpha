#!/usr/bin/env python3
import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from qwen_common import get_dashscope_key, ensure_dir, default_work_dir

ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen3-asr-flash"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def sec_to_ts(sec: float) -> str:
    ms = int(sec * 1000)
    s = ms // 1000
    ms = ms % 1000
    h = s // 3600
    s %= 3600
    m = s // 60
    s %= 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def post_json(payload: dict, key: str, timeout_sec: float = 60.0) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        ENDPOINT,
        method="POST",
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return json.loads(body)
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"DashScope ASR HTTP {e.code}: {body}")
    except URLError as e:
        raise RuntimeError(f"DashScope ASR network error: {e}")


def asr_one_wav(wav_path: Path, key: str, out_dir: Path) -> str:
    data_uri = "data:audio/wav;base64," + base64.b64encode(wav_path.read_bytes()).decode("ascii")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": [{"text": ""}]},
            {"role": "user", "content": [{"type": "input_audio", "input_audio": {"data": data_uri}}]},
        ],
        "stream": False,
        "asr_options": {"enable_itn": False},
    }
    # keep payload for debugging
    payload_path = out_dir / (wav_path.stem + ".json")
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    resp = post_json(payload, key)
    try:
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="input audio file (.ogg/.wav/.mp3 etc)")
    ap.add_argument("--timestamps", action="store_true", help="chunk and add coarse timestamps")
    ap.add_argument("--chunk-sec", type=float, default=3.0, help="chunk size in seconds for timestamps")
    ap.add_argument("--work-dir", default=default_work_dir(), help="scratch dir")
    args = ap.parse_args()

    key = get_dashscope_key()

    inp = Path(args.inp)
    if not inp.exists():
        raise FileNotFoundError(str(inp))

    work = Path(args.work_dir)
    ensure_dir(work)

    wav = work / (inp.stem + "_16k.wav")
    run(["ffmpeg", "-y", "-i", str(inp), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])

    if not args.timestamps:
        text = asr_one_wav(wav, key, work)
        print(text)
        return

    seg_dir = work / (inp.stem + f"_seg_{int(args.chunk_sec*1000)}ms")
    ensure_dir(seg_dir)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav),
            "-f",
            "segment",
            "-segment_time",
            str(args.chunk_sec),
            "-reset_timestamps",
            "1",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(seg_dir / "chunk_%03d.wav"),
        ]
    )

    chunks = sorted(seg_dir.glob("chunk_*.wav"))
    lines = []
    for i, ch in enumerate(chunks):
        txt = asr_one_wav(ch, key, seg_dir)
        if not txt:
            continue
        start = i * args.chunk_sec
        end = (i + 1) * args.chunk_sec
        lines.append(f"[{sec_to_ts(start)} - {sec_to_ts(end)}] {txt}")

    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
