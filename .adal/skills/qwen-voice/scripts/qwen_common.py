from __future__ import annotations

from pathlib import Path


def _read_dotenv_file(p: Path) -> dict[str, str]:
    """Read a .env file (KEY=VALUE). Returns empty dict if missing.

    Notes:
    - Ignores comments and blank lines
    - Supports optional leading `export `
    - Strips single/double quotes around values
    """
    if not p.exists():
        return {}

    out: dict[str, str] = {}
    for raw in p.read_text("utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if not k:
            continue
        out[k] = v
    return out


def _find_project_env() -> Path | None:
    """Find ./.qwen-voice/.env by walking upwards from this file."""
    cur = Path(__file__).resolve()
    for parent in [cur.parent, *cur.parents]:
        envp = parent / ".qwen-voice" / ".env"
        if envp.exists():
            return envp
    return None


def get_dashscope_key() -> str:
    """Get DASHSCOPE_API_KEY.

    IMPORTANT: We intentionally IGNORE system environment variables.
    We only read config from .env files:
      1) ~/.config/qwen-voice/.env (preferred)
      2) <repo>/.qwen-voice/.env (dev/testing)

    If not found, raise a clear error instructing the user to configure it.
    """
    user_env = Path.home() / ".config" / "qwen-voice" / ".env"
    user_cfg = _read_dotenv_file(user_env)
    if user_cfg.get("DASHSCOPE_API_KEY"):
        return user_cfg["DASHSCOPE_API_KEY"].strip()

    proj_env = _find_project_env()
    if proj_env:
        proj_cfg = _read_dotenv_file(proj_env)
        if proj_cfg.get("DASHSCOPE_API_KEY"):
            return proj_cfg["DASHSCOPE_API_KEY"].strip()

    raise RuntimeError(
        "DASHSCOPE_API_KEY not found. Configure one of:\n"
        "- ~/.config/qwen-voice/.env\n"
        "- <repo>/.qwen-voice/.env\n"
        "Example:\n"
        "  DASHSCOPE_API_KEY=your_key_here\n"
    )


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def skill_dir() -> Path:
    """Return the skill root directory (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def default_work_dir() -> str:
    """Return the default work directory inside the skill folder."""
    return str(skill_dir() / "work" / "qwen-voice")


def default_venv_dir() -> str:
    """Return the default venv directory inside the skill folder."""
    return str(skill_dir() / "work" / "venv-dashscope")
