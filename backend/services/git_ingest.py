"""GitIngest — clone a GitHub repo, flatten to a single markdown blob,
ingest into RAG.

Pattern from github-rag + gitingest projects in the hub. Tiny: ~30
lines of actual work. The repo is shallow-cloned to a temp dir, the
`gitingest` library (or a manual walk fallback) turns it into one
document, then we hand it to `doc_ingest.ingest_text()` so the
corrective-RAG pipeline treats it like any other doc.

Public API:
    ingest_repo(user_id, repo_url, max_bytes=2_000_000)
"""
from __future__ import annotations
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv",
                "dist", "build", ".next", "target", "vendor", ".cache"}
_INCLUDE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".txt",
                ".json", ".yaml", ".yml", ".toml", ".go", ".rs", ".rb",
                ".java", ".kt", ".swift", ".c", ".cpp", ".h", ".hpp",
                ".css", ".html", ".sh", ".dockerfile", ".env.example"}


def _flatten_local_repo(path: Path, max_bytes: int = 2_000_000) -> str:
    """Walk the repo and concatenate source files as one markdown blob.
    Skips binaries, lockfiles, very large files, and vendor dirs."""
    chunks: list[str] = []
    total = 0
    for fp in sorted(path.rglob("*")):
        if any(part in _IGNORE_DIRS for part in fp.parts):
            continue
        if not fp.is_file():
            continue
        if fp.suffix and fp.suffix.lower() not in _INCLUDE_EXT:
            continue
        # Skip lockfiles + big files
        if fp.name in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml",
                       "poetry.lock", "Pipfile.lock"):
            continue
        try:
            size = fp.stat().st_size
        except Exception:
            continue
        if size > 200_000 or total + size > max_bytes:
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = fp.relative_to(path)
        chunks.append(f"## {rel}\n\n```{fp.suffix.lstrip('.')}\n{content}\n```\n")
        total += size
    return "\n".join(chunks)


async def ingest_repo(
    *, user_id: str, repo_url: str,
    max_bytes: int = 2_000_000,
) -> dict[str, Any]:
    """Clone + flatten + ingest. Returns doc summary from doc_ingest."""
    from services import doc_ingest
    # Sanity check URL — reject anything that isn't a plausible git URL
    if not repo_url.strip().startswith(("https://", "git@", "http://")):
        return {"ok": False, "error": "invalid_repo_url"}
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "repo"
        try:
            subprocess.run(
                ["git", "clone", "--depth=1", "--quiet", repo_url, str(dest)],
                check=True, timeout=120, capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            return {"ok": False, "error": f"clone_failed: {exc.stderr.decode('utf-8','replace')[:200]}"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "clone_timeout"}
        try:
            blob = _flatten_local_repo(dest, max_bytes=max_bytes)
        except Exception as exc:
            return {"ok": False, "error": f"flatten_failed: {exc}"}
        if not blob:
            return {"ok": False, "error": "no_text_extracted"}
    # Title = "github.com/owner/repo" from the URL tail
    title = repo_url.rstrip("/").split("://")[-1].split("@")[-1]
    return await doc_ingest.ingest_text(
        user_id=user_id, text=blob, title=title,
        metadata={"source": "gitingest", "repo_url": repo_url},
    )
