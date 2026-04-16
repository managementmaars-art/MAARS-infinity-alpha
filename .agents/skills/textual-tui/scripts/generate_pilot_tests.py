#!/usr/bin/env python3
"""Generate starter Pilot tests for an existing Textual app."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from _textual_skill_utils import json_dumps, safe_key_for_test, scan_project, write_text_file


def derive_import_target(file_path: str, project_root: Path, output_path: Path) -> str:
    relative = Path(file_path)
    abs_path = project_root / relative
    rel_from_test = abs_path.relative_to(output_path.parent.resolve().parents[0] if output_path.parent.exists() else project_root)
    return rel_from_test.as_posix()


def choose_app(project: Dict[str, object], requested_module: Optional[str], requested_class: Optional[str]) -> Optional[Dict[str, str]]:
    apps = project["apps"]
    if requested_module or requested_class:
        for app in apps:
            module_match = requested_module is None or Path(app["path"]).stem == requested_module
            class_match = requested_class is None or app["class_name"] == requested_class
            if module_match and class_match:
                return app
        return None
    return apps[0] if apps else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate starter pytest + Pilot tests for a Textual app."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project directory containing the Textual app (default: current directory).",
    )
    parser.add_argument(
        "--module",
        default=None,
        help="Specific module/file stem to target, e.g. 'my_app'.",
    )
    parser.add_argument(
        "--class-name",
        default=None,
        help="Specific app class to target, e.g. 'MyApp'.",
    )
    parser.add_argument(
        "--output",
        default="tests/test_generated_textual.py",
        help="Path for the generated test file.",
    )
    parser.add_argument(
        "--include-snapshot",
        action="store_true",
        help="Also include a snapshot-test skeleton that uses `snap_compare`.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the test file if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    project = scan_project(project_root)
    app = choose_app(project, args.module, args.class_name)
    if app is None:
        print("Error: could not identify a target Textual app.", file=sys.stderr)
        return 2

    file_scan = next(scan for scan in project["files"] if scan["path"] == app["path"])
    app_scan = next(record for record in file_scan["app_classes"] if record["name"] == app["class_name"])
    button_ids = [
        call["id"]
        for call in file_scan["template_calls"]
        if call["widget"] == "Button" and "id" in call
    ]
    input_ids = [
        call["id"]
        for call in file_scan["template_calls"]
        if call["widget"] == "Input" and "id" in call
    ]
    binding_candidates = [binding for binding in app_scan["bindings"] if safe_key_for_test(binding)]

    output = Path(args.output).expanduser().resolve()
    module_path = (project_root / app["path"]).resolve()
    module_path_literal = module_path.as_posix()

    lines: List[str] = [
        '"""Generated starter tests for a Textual app.',
        "",
        "These are intentionally conservative: they give you a smoke test and",
        "interaction shells with TODO assertions to tighten after you inspect",
        "the specific behaviour of the app.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import importlib.util",
        "from pathlib import Path",
        "",
        "import pytest",
        "",
        'MODULE_PATH = Path(r"{0}")'.format(module_path_literal),
        'APP_CLASS_NAME = "{0}"'.format(app["class_name"]),
        "",
        "",
        "def load_app_class():",
        '    """Load the app class directly from the source file."""',
        "    spec = importlib.util.spec_from_file_location(MODULE_PATH.stem, MODULE_PATH)",
        "    if spec is None or spec.loader is None:",
        '        raise RuntimeError("Could not load module spec for {0}".format(MODULE_PATH))',
        "    module = importlib.util.module_from_spec(spec)",
        "    spec.loader.exec_module(module)",
        "    return getattr(module, APP_CLASS_NAME)",
        "",
        "",
        "@pytest.mark.asyncio",
        "async def test_smoke_runs() -> None:",
        "    AppClass = load_app_class()",
        "    app = AppClass()  # TODO: pass constructor args here if your app needs them",
        "    async with app.run_test(size=(100, 30)) as pilot:",
        "        await pilot.pause()",
        "        assert app is not None",
        "",
    ]

    if input_ids:
        first_input = input_ids[0]
        lines.extend(
            [
                "@pytest.mark.asyncio",
                "async def test_input_flow() -> None:",
                "    AppClass = load_app_class()",
                "    app = AppClass()",
                "    async with app.run_test(size=(100, 30)) as pilot:",
                '        await pilot.click("#{0}")'.format(first_input),
                '        await pilot.press("h", "e", "l", "l", "o")',
                "        await pilot.pause()",
                "        # TODO: assert the visible state change caused by typing.",
                "        assert True",
                "",
            ]
        )

    for button_id in button_ids[:2]:
        test_name = re.sub(r"[^A-Za-z0-9_]+", "_", button_id).strip("_") or "button"
        lines.extend(
            [
                "@pytest.mark.asyncio",
                "async def test_button_{0}() -> None:".format(test_name),
                "    AppClass = load_app_class()",
                "    app = AppClass()",
                "    async with app.run_test(size=(100, 30)) as pilot:",
                '        await pilot.click("#{0}")'.format(button_id),
                "        await pilot.pause()",
                "        # TODO: replace this with a real user-visible assertion.",
                "        assert True",
                "",
            ]
        )

    if binding_candidates:
        binding = binding_candidates[0]
        test_name = re.sub(r"[^A-Za-z0-9_]+", "_", binding["key"]).strip("_") or "binding"
        lines.extend(
            [
                "@pytest.mark.asyncio",
                "async def test_binding_{0}() -> None:".format(test_name),
                "    AppClass = load_app_class()",
                "    app = AppClass()",
                "    async with app.run_test(size=(100, 30)) as pilot:",
                '        await pilot.press("{0}")'.format(binding["key"]),
                "        await pilot.pause()",
                '        # TODO: assert the effect of `{0}` -> `{1}`.'.format(binding["key"], binding["action"]),
                "        assert True",
                "",
            ]
        )

    if args.include_snapshot:
        rel_app_path = app["path"].replace("\\", "/")
        lines.extend(
            [
                "def test_snapshot_default(snap_compare):",
                '    assert snap_compare("{0}")'.format(rel_app_path),
                "",
            ]
        )

    content = "\n".join(lines).rstrip() + "\n"
    try:
        write_text_file(output, content, force=args.force)
    except FileExistsError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 2

    print(
        json_dumps(
            {
                "written_file": str(output),
                "app_path": app["path"],
                "class_name": app["class_name"],
                "button_ids": button_ids[:2],
                "binding_tested": binding_candidates[0] if binding_candidates else None,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
