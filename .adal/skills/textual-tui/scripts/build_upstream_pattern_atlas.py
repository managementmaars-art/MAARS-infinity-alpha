#!/usr/bin/env python3
"""Build markdown summaries from a local clone or snapshot of the Textual repository."""

from __future__ import annotations

import argparse
import ast
import collections
import os
from pathlib import Path
from typing import Counter, Dict, Iterable, List, Tuple

WIDGET_MODULE = "textual.widgets"
IGNORE_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}


def iter_py_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                yield Path(dirpath) / filename


def safe_parse(path: Path):
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception:
        return None


def count_subdirs(root: Path, relative_subdir: str) -> List[Tuple[str, int]]:
    subdir = root / relative_subdir
    counts: Counter[str] = collections.Counter()
    if not subdir.exists():
        return []
    for path in subdir.rglob("*"):
        if path.is_file():
            rel = path.relative_to(subdir)
            top = rel.parts[0] if rel.parts else path.name
            counts[top] += 1
    return counts.most_common(20)


def widget_import_counts(paths: Iterable[Path]) -> List[Tuple[str, int]]:
    counts: Counter[str] = collections.Counter()
    for path in paths:
        tree = safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "") == WIDGET_MODULE:
                for alias in node.names:
                    counts[alias.name] += 1
    return counts.most_common(30)


def feature_example_paths(repo_root: Path) -> Dict[str, List[str]]:
    feature_terms = {
        "breakpoints": "HORIZONTAL_BREAKPOINTS",
        "command_palette": "COMMANDS = App.COMMANDS",
        "modes": "MODES =",
        "workers": "@work",
        "delivery": "deliver_text(",
        "text_area": "TextArea",
        "directory_tree": "DirectoryTree",
        "data_table": "DataTable",
    }
    results: Dict[str, List[str]] = {key: [] for key in feature_terms}
    search_roots = [
        repo_root / "examples",
        repo_root / "docs" / "examples",
        repo_root / "tests",
    ]
    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in iter_py_files(search_root):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            relative = path.relative_to(repo_root).as_posix()
            for feature, token in feature_terms.items():
                if token in text and len(results[feature]) < 8:
                    results[feature].append(relative)
    return results


def widget_file_count(repo_root: Path) -> int:
    widgets_dir = repo_root / "src" / "textual" / "widgets"
    return len(list(widgets_dir.glob("_*.py"))) if widgets_dir.exists() else 0


def build_repo_map(repo_root: Path) -> str:
    doc_example_areas = count_subdirs(repo_root, "docs/examples")
    test_areas = count_subdirs(repo_root, "tests")
    widgets_count = widget_file_count(repo_root)

    lines = [
        "# Repository map",
        "",
        "This summary was generated from the bundled Textual repository snapshot used to build this skill.",
        "",
        "## High-value directories",
        "",
        "- `src/textual/` — framework source.",
        "- `src/textual/widgets/` — built-in widgets (`{0}` widget implementation files detected).".format(widgets_count),
        "- `examples/` — standalone example apps worth mining for architecture and styling patterns.",
        "- `docs/examples/` — guide/tutorial examples, usually minimal and focused on one concept.",
        "- `tests/` — excellent source of behaviour contracts and edge-case handling.",
        "",
        "## docs/examples hot spots",
        "",
    ]
    for name, count in doc_example_areas:
        lines.append("- `{0}` — {1} files".format(name, count))
    lines.extend(
        [
            "",
            "## tests hot spots",
            "",
        ]
    )
    for name, count in test_areas:
        lines.append("- `{0}` — {1} files".format(name, count))
    lines.extend(
        [
            "",
            "## Practical search order",
            "",
            "1. Look in `examples/` for full app structure.",
            "2. Look in `docs/examples/guide/` for the smallest focused example of a feature.",
            "3. Look in `tests/` when behaviour, edge cases, or event names are unclear.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def build_pattern_atlas(repo_root: Path) -> str:
    example_paths = list(iter_py_files(repo_root / "examples")) if (repo_root / "examples").exists() else []
    docs_example_paths = list(iter_py_files(repo_root / "docs" / "examples")) if (repo_root / "docs" / "examples").exists() else []
    widget_counts = widget_import_counts(example_paths + docs_example_paths)
    features = feature_example_paths(repo_root)

    lines = [
        "# Upstream pattern atlas",
        "",
        "This file was generated from the bundled Textual repository snapshot.",
        "",
        "## Most-imported widgets in examples",
        "",
    ]
    for widget, count in widget_counts[:20]:
        lines.append("- `{0}` — {1} imports".format(widget, count))

    lines.extend(
        [
            "",
            "## Example paths by feature",
            "",
        ]
    )
    for feature, paths in sorted(features.items()):
        lines.append("### {0}".format(feature.replace("_", " ").title()))
        if paths:
            for path in paths:
                lines.append("- `{0}`".format(path))
        else:
            lines.append("- No matching examples found in this snapshot.")
        lines.append("")

    lines.extend(
        [
            "## How to mine upstream effectively",
            "",
            "- Prefer `examples/` when you want a complete app shell or a realistic layout.",
            "- Prefer `docs/examples/guide/` when you want the smallest reproducible example of a feature.",
            "- Prefer `tests/` when you need event names, edge cases, or confirmation that a behaviour is supported.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate markdown summaries from a local Textual repository snapshot."
    )
    parser.add_argument("repo_root", help="Path to the Textual repository root.")
    parser.add_argument("--repo-map-out", default=None, help="Optional output path for the repository map markdown.")
    parser.add_argument("--atlas-out", default=None, help="Optional output path for the pattern atlas markdown.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    repo_map = build_repo_map(repo_root)
    atlas = build_pattern_atlas(repo_root)

    if args.repo_map_out:
        Path(args.repo_map_out).write_text(repo_map, encoding="utf-8")
    else:
        print(repo_map)

    if args.atlas_out:
        Path(args.atlas_out).write_text(atlas, encoding="utf-8")
    elif args.repo_map_out:
        print(atlas)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
