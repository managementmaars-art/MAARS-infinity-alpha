"""Admin code viewer API — browse and read the full system codebase."""
import os
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_DIR = "/app"
ALLOWED_DIRS = ["backend", "frontend/src"]
EXCLUDED_DIRS = {
    "node_modules", "__pycache__", ".git", ".emergent", "venv", ".venv",
    "dist", "build", ".next", "coverage", "uploads", ".cache",
}
EXCLUDED_FILES = {".pyc", ".pyo", ".so", ".o", ".class", ".lock", ".map"}
MAX_FILE_SIZE = 500_000  # 500KB


def _build_tree(path: str, rel: str = "", depth: int = 0, max_depth: int = 6) -> list:
    """Recursively build a file tree."""
    if depth > max_depth:
        return []
    items = []
    try:
        entries = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
    except PermissionError:
        return []

    for entry in entries:
        full = os.path.join(path, entry)
        rel_path = f"{rel}/{entry}" if rel else entry

        if entry.startswith(".") and entry not in (".env",):
            continue
        if entry in EXCLUDED_DIRS:
            continue

        if os.path.isdir(full):
            children = _build_tree(full, rel_path, depth + 1, max_depth)
            items.append({
                "name": entry,
                "path": rel_path,
                "type": "directory",
                "children": children,
                "count": sum(1 for c in children if c["type"] == "file") + sum(c.get("count", 0) for c in children if c["type"] == "directory"),
            })
        else:
            ext = os.path.splitext(entry)[1].lower()
            if ext in EXCLUDED_FILES:
                continue
            size = os.path.getsize(full)
            items.append({
                "name": entry,
                "path": rel_path,
                "type": "file",
                "size": size,
                "extension": ext,
                "language": _ext_to_language(ext),
            })

    return items


def _ext_to_language(ext: str) -> str:
    lang_map = {
        ".py": "python", ".js": "javascript", ".jsx": "javascript",
        ".ts": "typescript", ".tsx": "typescript", ".json": "json",
        ".html": "html", ".css": "css", ".md": "markdown",
        ".yml": "yaml", ".yaml": "yaml", ".txt": "text",
        ".env": "shell", ".sh": "shell", ".toml": "toml",
        ".cfg": "ini", ".ini": "ini", ".sql": "sql",
    }
    return lang_map.get(ext, "text")


@router.get("/admin/code/tree")
async def get_code_tree(current_user: User = Depends(get_current_user)):
    """Get the full codebase file tree (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")

    tree = []
    for allowed in ALLOWED_DIRS:
        dir_path = os.path.join(BASE_DIR, allowed)
        if os.path.isdir(dir_path):
            children = _build_tree(dir_path, allowed)
            tree.append({
                "name": allowed,
                "path": allowed,
                "type": "directory",
                "children": children,
                "count": sum(1 for c in children if c["type"] == "file") + sum(c.get("count", 0) for c in children if c["type"] == "directory"),
            })

    # Add root-level files
    for entry in sorted(os.listdir(BASE_DIR)):
        full = os.path.join(BASE_DIR, entry)
        if os.path.isfile(full) and not entry.startswith("."):
            ext = os.path.splitext(entry)[1].lower()
            if ext not in EXCLUDED_FILES:
                tree.append({
                    "name": entry,
                    "path": entry,
                    "type": "file",
                    "size": os.path.getsize(full),
                    "extension": ext,
                    "language": _ext_to_language(ext),
                })

    return {"tree": tree}


@router.get("/admin/code/file")
async def get_code_file(
    path: str = Query(..., description="Relative file path"),
    current_user: User = Depends(get_current_user),
):
    """Read a file's content (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")

    # Security: prevent path traversal
    clean = os.path.normpath(path)
    if ".." in clean or clean.startswith("/"):
        raise HTTPException(400, "Invalid file path")

    # Must be in allowed directories or root files
    allowed = any(clean.startswith(d) for d in ALLOWED_DIRS)
    is_root_file = "/" not in clean and os.path.isfile(os.path.join(BASE_DIR, clean))
    if not allowed and not is_root_file:
        raise HTTPException(403, "Access denied for this path")

    full_path = os.path.join(BASE_DIR, clean)
    if not os.path.isfile(full_path):
        raise HTTPException(404, "File not found")

    size = os.path.getsize(full_path)
    if size > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large ({size:,} bytes, max {MAX_FILE_SIZE:,})")

    ext = os.path.splitext(clean)[1].lower()
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        raise HTTPException(500, f"Failed to read file: {str(e)[:100]}")

    return {
        "path": clean,
        "name": os.path.basename(clean),
        "content": content,
        "language": _ext_to_language(ext),
        "size": size,
        "lines": content.count("\n") + 1,
    }


@router.get("/admin/code/search")
async def search_code_files(
    q: str = Query(..., description="Search query"),
    current_user: User = Depends(get_current_user),
):
    """Search file names in the codebase (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(403, "Admin access required")

    query = q.lower()
    results = []

    for allowed in ALLOWED_DIRS:
        dir_path = os.path.join(BASE_DIR, allowed)
        if not os.path.isdir(dir_path):
            continue
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
            for fname in files:
                if query in fname.lower():
                    rel = os.path.relpath(os.path.join(root, fname), BASE_DIR)
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in EXCLUDED_FILES:
                        results.append({
                            "name": fname,
                            "path": rel,
                            "language": _ext_to_language(ext),
                            "size": os.path.getsize(os.path.join(root, fname)),
                        })
            if len(results) >= 50:
                break

    return {"results": results[:50]}
