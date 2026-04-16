#!/usr/bin/env python3
"""Load a Textual app and dump its DOM tree, modes, screens, and active bindings as JSON."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Textual app headlessly and dump its DOM/bindings as JSON."
    )
    parser.add_argument(
        "target",
        help="Either a Python file path or an import target like package.module[:AppClass].",
    )
    parser.add_argument(
        "--class-name",
        default=None,
        help="Optional app class name when loading from a file or module.",
    )
    parser.add_argument(
        "--size",
        nargs=2,
        type=int,
        default=[100, 30],
        metavar=("WIDTH", "HEIGHT"),
        help="Headless terminal size to use (default: 100 30).",
    )
    return parser.parse_args()


def load_module_from_target(target: str):
    path = Path(target)
    if path.exists():
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load module from file: {0}".format(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    module_name, _, class_name = target.partition(":")
    module = importlib.import_module(module_name)
    if class_name:
        setattr(module, "__requested_app_class__", class_name)
    return module


def find_app_class(module, explicit_class_name: Optional[str]):
    class_name = explicit_class_name or getattr(module, "__requested_app_class__", None)
    if class_name:
        try:
            return getattr(module, class_name)
        except AttributeError as error:
            raise RuntimeError("Module does not define app class {0!r}".format(class_name)) from error

    try:
        from textual.app import App
    except Exception as error:
        raise RuntimeError("Textual is not importable: {0}".format(error)) from error

    matches = []
    for value in module.__dict__.values():
        if isinstance(value, type) and issubclass(value, App) and value is not App:
            matches.append(value)
    if not matches:
        raise RuntimeError("Could not locate a Textual App subclass in the target module.")
    return matches[0]


def node_record(node) -> Dict[str, Any]:
    classes = []
    if hasattr(node, "classes"):
        try:
            classes = sorted(str(name) for name in node.classes)
        except Exception:
            classes = []
    return {
        "type": node.__class__.__name__,
        "id": getattr(node, "id", None),
        "classes": classes,
        "disabled": getattr(node, "disabled", None),
        "can_focus": getattr(node, "can_focus", None),
    }


async def run_dump(app_class, size):
    app = app_class()
    async with app.run_test(size=tuple(size)) as pilot:
        await pilot.pause()
        nodes = []
        for node in app.screen.walk_children(with_self=True):
            nodes.append(node_record(node))

        bindings = {}
        for key, active in app.active_bindings.items():
            bindings[key] = {
                "action": getattr(active.binding, "action", ""),
                "description": getattr(active.binding, "description", ""),
            }

        app_info = {
            "app_class": app_class.__name__,
            "title": getattr(app, "title", ""),
            "sub_title": getattr(app, "sub_title", ""),
            "current_mode": getattr(app, "current_mode", None),
            "modes": sorted(getattr(app_class, "MODES", {}).keys()) if hasattr(app_class, "MODES") else [],
            "screens": sorted(getattr(app_class, "SCREENS", {}).keys()) if hasattr(app_class, "SCREENS") else [],
            "bindings": bindings,
            "dom": nodes,
        }
        return app_info


def main() -> int:
    args = parse_args()
    try:
        import textual  # noqa: F401
    except Exception as error:
        print("Error: Textual is not installed or importable in this environment: {0}".format(error), file=sys.stderr)
        return 2

    try:
        module = load_module_from_target(args.target)
        app_class = find_app_class(module, args.class_name)
        payload = asyncio.run(run_dump(app_class, args.size))
    except Exception as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
