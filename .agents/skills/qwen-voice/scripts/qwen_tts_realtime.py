#!/usr/bin/env python3
import argparse
import base64
import os
import subprocess
import sys
import wave
from pathlib import Path

from qwen_common import get_dashscope_key, ensure_dir, default_work_dir, default_venv_dir


def ensure_dashscope_venv(venv_dir: Path) -> Path:
    py = venv_dir / "bin" / "python"
    pip = venv_dir / "bin" / "pip"
    if py.exists():
        return py

    ensure_dir(venv_dir)
    subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
    subprocess.run([str(pip), "-q", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "-q", "install", "dashscope>=1.23.9"], check=True)
    return py


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--voice", required=True, help="voice param string (from enrollment)")
    ap.add_argument("--model", default="qwen3-tts-vc-realtime-2026-01-15")
    ap.add_argument("--out", required=True, help="output .wav (pcm 24k mono 16bit)")
    ap.add_argument("--work-dir", default=default_work_dir())
    args = ap.parse_args()

    key = get_dashscope_key()
    work = Path(args.work_dir)
    ensure_dir(work)

    venv_py = ensure_dashscope_venv(Path(default_venv_dir()))

    # Run realtime TTS via dashscope SDK in venv and write PCM frames to a temp file
    script = work / "_tts_realtime_call.py"
    script.write_text(
        """
import base64
import os
import pathlib
import threading
import time

import dashscope
from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat

class CB(QwenTtsRealtimeCallback):
    def __init__(self, out_pcm_path: str):
        self.out_pcm_path = out_pcm_path
        self.f = open(out_pcm_path, 'wb')
        self.done = threading.Event()

    def on_open(self):
        pass

    def on_close(self, code, msg):
        try:
            self.f.close()
        finally:
            self.done.set()

    def on_event(self, response: dict):
        t = response.get('type','')
        if t == 'response.audio.delta':
            self.f.write(base64.b64decode(response['delta']))
        elif t in ('response.done','session.finished'):
            try:
                self.f.close()
            finally:
                self.done.set()

key=os.getenv('DASHSCOPE_API_KEY')
dashscope.api_key=key

out_pcm=os.getenv('QWEN_OUT_PCM')
voice=os.getenv('QWEN_VOICE')
model=os.getenv('QWEN_MODEL')
text=os.getenv('QWEN_TEXT')

cb=CB(out_pcm)
q=QwenTtsRealtime(model=model, callback=cb, url='wss://dashscope.aliyuncs.com/api-ws/v1/realtime')
q.connect()
q.update_session(voice=voice, response_format=AudioFormat.PCM_24000HZ_MONO_16BIT, mode='server_commit')
q.append_text(text)
time.sleep(0.05)
q.finish()
cb.done.wait(timeout=120)
""".lstrip(),
        encoding="utf-8",
    )

    pcm_path = work / "tts_realtime.pcm"

    env = os.environ.copy()
    env["DASHSCOPE_API_KEY"] = key
    env["QWEN_OUT_PCM"] = str(pcm_path)
    env["QWEN_VOICE"] = args.voice
    env["QWEN_MODEL"] = args.model
    env["QWEN_TEXT"] = args.text

    subprocess.run([str(venv_py), str(script)], check=True, env=env)

    # Wrap PCM into WAV
    out_wav = Path(args.out)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_path.read_bytes())

    print(str(out_wav))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"realtime tts failed: {e}", file=sys.stderr)
        sys.exit(2)
