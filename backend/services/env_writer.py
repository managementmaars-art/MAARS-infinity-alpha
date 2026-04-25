"""
Safe .env reader/writer for the in-app setup wizard.

Key contract:
    * load()       - returns {key: value} of every defined var
    * upsert(d)    - merges `d` into the file, preserving every line we don't touch
                     (comments, blank lines, ordering of pre-existing keys)
    * mask(value)  - one-way mask suitable for UI redisplay
    * sync_os(d)   - mirrors keys into os.environ so the running process sees them
                     without a restart

The .env lives at PROJECT_ROOT/.env — same path the rest of the backend reads.
"""
from __future__ import annotations

import os
import re
import threading
from pathlib import Path

# backend/services/env_writer.py  →  parents[2] = repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

_LOCK = threading.RLock()
_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def load() -> dict[str, str]:
    """Return every KEY=VALUE pair from .env (last value wins)."""
    if not ENV_PATH.exists():
        return {}
    out: dict[str, str] = {}
    with _LOCK, ENV_PATH.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = _LINE.match(line)
            if m:
                out[m.group(1)] = _unquote(m.group(2))
    return out


def upsert(updates: dict[str, str]) -> dict[str, str]:
    """
    Merge `updates` into .env. Existing lines for those keys are rewritten
    in place; brand-new keys are appended in a `# wizard updates` block.
    Returns the in-place pre-image so callers can confirm what changed.
    """
    if not updates:
        return {}

    with _LOCK:
        ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing_lines: list[str] = []
        if ENV_PATH.exists():
            existing_lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

        seen: set[str] = set()
        new_lines: list[str] = []
        previous: dict[str, str] = {}

        for raw in existing_lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                new_lines.append(raw)
                continue
            m = _LINE.match(stripped)
            if not m:
                new_lines.append(raw)
                continue
            key = m.group(1)
            if key in updates:
                previous[key] = _unquote(m.group(2))
                new_lines.append(f"{key}={_quote(updates[key])}")
                seen.add(key)
            else:
                new_lines.append(raw)

        appended = [k for k in updates if k not in seen]
        if appended:
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append("# ── wizard updates ──")
            for k in appended:
                new_lines.append(f"{k}={_quote(updates[k])}")

        # Atomic write: tmp + replace.
        tmp = ENV_PATH.with_suffix(".env.tmp")
        tmp.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        tmp.replace(ENV_PATH)

        # Lock the file down (best-effort; Windows ignores chmod silently).
        try:
            os.chmod(ENV_PATH, 0o600)
        except Exception:
            pass

    return previous


def sync_os(updates: dict[str, str]) -> None:
    """Mirror keys into os.environ for the running process."""
    for k, v in updates.items():
        if v == "":
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def mask(value: str | None) -> str:
    """One-way mask suitable for redisplay in the UI."""
    if not value:
        return ""
    s = value.strip()
    if len(s) <= 8:
        return "•" * len(s)
    return f"{s[:4]}…{s[-4:]}"


def masked_view(keys: list[str]) -> dict[str, str | None]:
    """Snapshot the current .env values for the given keys, masked."""
    raw = load()
    out: dict[str, str | None] = {}
    for k in keys:
        v = raw.get(k) or os.environ.get(k, "")
        out[k] = mask(v) if v else None
    return out


# ─────────────────────────────────────────────────────────── helpers

def _quote(value: str) -> str:
    """Quote only when needed — preserves the existing aesthetic of the file."""
    if any(ch in value for ch in (" ", "\"", "'", "#", "\\")):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f"\"{escaped}\""
    return value


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("\"", "'"):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value
