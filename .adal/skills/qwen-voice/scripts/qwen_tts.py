#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

from qwen_common import get_dashscope_key, ensure_dir, default_work_dir, default_venv_dir


def ensure_dashscope_venv(venv_dir: Path) -> Path:
    py = venv_dir / "bin" / "python"
    pip = venv_dir / "bin" / "pip"
    if py.exists():
        return py

    ensure_dir(venv_dir)
    subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
    subprocess.run([str(pip), "-q", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "-q", "install", "dashscope"], check=True)
    return py


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def download_file(url: str, out_path: Path, timeout_sec: float = 60.0) -> None:
    with urlopen(url, timeout=timeout_sec) as resp:
        out_path.write_bytes(resp.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--voice", default="Cherry", help="preset voice name (e.g., Cherry)")
    ap.add_argument("--voice-profile", default="", help="JSON file created by qwen_voice_clone.py")
    ap.add_argument("--language", default="Chinese")
    ap.add_argument("--out", required=True, help="output path (.ogg recommended)")
    ap.add_argument("--work-dir", default=default_work_dir(), help="scratch dir")
    args = ap.parse_args()

    key = get_dashscope_key()
    work = Path(args.work_dir)
    ensure_dir(work)

    out = Path(args.out)

    # If voice-profile is provided, use realtime VC model (PCM->WAV->OGG)
    if args.voice_profile:
        import json

        vp = Path(args.voice_profile)
        j = json.loads(vp.read_text("utf-8"))
        voice_param = j["voice"]
        model = j.get("target_model") or "qwen3-tts-vc-realtime-2026-01-15"

        wav_out = work / "tts_vc.wav"
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("qwen_tts_realtime.py")),
                "--text",
                args.text,
                "--voice",
                voice_param,
                "--model",
                model,
                "--out",
                str(wav_out),
                "--work-dir",
                str(work),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        if out.suffix.lower() == ".wav":
            wav_out.replace(out)
            print(str(out))
            return

        run(["ffmpeg", "-y", "-i", str(wav_out), "-c:a", "libopus", "-b:a", "32k", str(out)])
        print(str(out))
        return

    # Otherwise: preset TTS via MultiModalConversation
    venv_py = ensure_dashscope_venv(Path(default_venv_dir()))

    # call dashscope SDK in a subprocess to avoid importing dependency in system python
    script = work / "_tts_call.py"
    script.write_text(
        """
import os
import sys
import dashscope

dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

resp = dashscope.MultiModalConversation.call(
    model='qwen3-tts-flash',
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    text=os.getenv('QWEN_TTS_TEXT'),
    voice=os.getenv('QWEN_TTS_VOICE'),
    language_type=os.getenv('QWEN_TTS_LANG'),
)

# Basic response validation
if getattr(resp, 'status_code', 200) != 200:
    print(f"API Error: {getattr(resp,'status_code',None)} {getattr(resp,'code',None)} {getattr(resp,'message',None)}", file=sys.stderr)
    sys.exit(1)

out = getattr(resp, 'output', None)
if out is None or getattr(out, 'audio', None) is None or getattr(out.audio, 'url', None) is None:
    print('API returned empty audio url', file=sys.stderr)
    sys.exit(1)

print(out.audio.url)
""".lstrip(),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["DASHSCOPE_API_KEY"] = key
    env["QWEN_TTS_TEXT"] = args.text
    env["QWEN_TTS_VOICE"] = args.voice
    env["QWEN_TTS_LANG"] = args.language

    proc = subprocess.run([str(venv_py), str(script)], capture_output=True, text=True, env=env, check=True)
    url = proc.stdout.strip().splitlines()[-1].strip()

    wav = work / "tts.wav"
    download_file(url, wav)

    if out.suffix.lower() == ".wav":
        wav.replace(out)
        print(str(out))
        return

    # default: convert to opus ogg (telegram voice note friendly)
    run(["ffmpeg", "-y", "-i", str(wav), "-c:a", "libopus", "-b:a", "32k", str(out)])
    print(str(out))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"tts failed: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
