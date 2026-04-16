#!/usr/bin/env python3
"""Utilities shared by the textual-tui-v2 helper scripts."""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

SKILL_ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}
TEXTUAL_IMPORT_PREFIX = "textual"

BINDING_VERBS_TO_SKIP = {
    "quit",
    "exit",
    "back",
    "command_palette",
}

NETWORK_CALL_PREFIXES = {
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
    "requests.request",
    "httpx.get",
    "httpx.post",
    "httpx.put",
    "httpx.delete",
    "httpx.request",
    "urllib.request.urlopen",
}
BLOCKING_CALL_PREFIXES = {
    "time.sleep",
    "subprocess.run",
    "subprocess.check_output",
    "subprocess.call",
    "os.system",
} | NETWORK_CALL_PREFIXES

TABLE_LIKE_IMPORTS = {"Table", "Column"}
BUILTIN_WIDGETS = {
    "Button",
    "Checkbox",
    "Collapsible",
    "ContentSwitcher",
    "DataTable",
    "Digits",
    "DirectoryTree",
    "Footer",
    "Header",
    "HelpPanel",
    "Input",
    "KeyPanel",
    "Label",
    "Link",
    "ListItem",
    "ListView",
    "LoadingIndicator",
    "Log",
    "Markdown",
    "MarkdownViewer",
    "MaskedInput",
    "OptionList",
    "Placeholder",
    "Pretty",
    "ProgressBar",
    "RadioButton",
    "RadioSet",
    "RichLog",
    "Rule",
    "Select",
    "SelectionList",
    "Sparkline",
    "Static",
    "Switch",
    "Tab",
    "TabbedContent",
    "TabPane",
    "Tabs",
    "TextArea",
    "Tooltip",
    "Tree",
    "Welcome",
}


def to_posix(path: Path) -> str:
    return path.as_posix()


def iter_files(root: Path, suffixes: Sequence[str]) -> Iterable[Path]:
    suffixes = tuple(suffixes)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
        for filename in filenames:
            if filename.endswith(suffixes):
                yield Path(dirpath) / filename


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def safe_parse(path: Path) -> Optional[ast.AST]:
    try:
        return ast.parse(read_text(path), filename=str(path))
    except SyntaxError:
        return None


def full_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        value = full_name(node.value)
        if value is None:
            return node.attr
        return f"{value}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return full_name(node.value)
    if isinstance(node, ast.Call):
        return full_name(node.func)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def call_name(node: ast.Call) -> Optional[str]:
    return full_name(node.func)


def string_value(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def int_value(node: ast.AST) -> Optional[int]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    return None


def bool_value(node: ast.AST) -> Optional[bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def literal_structure(node: ast.AST):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def class_base_names(class_def: ast.ClassDef) -> List[str]:
    return [full_name(base) or ast.unparse(base) for base in class_def.bases]


def class_kind(base_names: Sequence[str]) -> Optional[str]:
    simple_bases = {base.split(".")[-1] for base in base_names}
    if "App" in simple_bases:
        return "app"
    if "ModalScreen" in simple_bases or "Screen" in simple_bases:
        return "screen"
    if simple_bases & {
        "Widget",
        "Static",
        "Markdown",
        "MarkdownViewer",
        "Container",
        "VerticalScroll",
        "Horizontal",
        "Vertical",
        "ScrollableContainer",
        "DataTable",
        "DirectoryTree",
        "TextArea",
        "Log",
        "RichLog",
        "Pretty",
        "Tree",
        "ListView",
        "Input",
        "Button",
    }:
        return "widget"
    return None


def class_span(class_def: ast.ClassDef) -> int:
    if hasattr(class_def, "end_lineno") and class_def.end_lineno:
        return int(class_def.end_lineno) - int(class_def.lineno) + 1
    return 0


def decorator_names(function_def: ast.AST) -> List[str]:
    names: List[str] = []
    for decorator in getattr(function_def, "decorator_list", []):
        if isinstance(decorator, ast.Call):
            name = full_name(decorator.func)
        else:
            name = full_name(decorator)
        if name:
            names.append(name)
    return names


def method_names(class_def: ast.ClassDef, prefix: str) -> List[str]:
    names: List[str] = []
    for node in class_def.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(prefix):
            names.append(node.name)
    return names


def assignment_value(class_def: ast.ClassDef, target_name: str):
    for node in class_def.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_name:
                    return node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == target_name:
                return node.value
    return None


def extract_bindings(class_def: ast.ClassDef) -> List[Dict[str, str]]:
    bindings: List[Dict[str, str]] = []
    value = assignment_value(class_def, "BINDINGS")
    if value is None:
        return bindings
    literal = literal_structure(value)
    if isinstance(literal, (list, tuple)):
        for entry in literal:
            key = action = description = None
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                key = str(entry[0])
                action = str(entry[1])
                description = str(entry[2]) if len(entry) >= 3 else ""
            elif isinstance(entry, dict):
                key = str(entry.get("key", ""))
                action = str(entry.get("action", ""))
                description = str(entry.get("description", ""))
            if key and action:
                bindings.append(
                    {"key": key, "action": action, "description": description}
                )
    return bindings


def extract_modes(class_def: ast.ClassDef) -> Dict[str, str]:
    value = assignment_value(class_def, "MODES")
    literal = literal_structure(value) if value is not None else None
    modes: Dict[str, str] = {}
    if isinstance(literal, dict):
        for key, mode_value in literal.items():
            modes[str(key)] = str(mode_value)
    return modes


def extract_screens(class_def: ast.ClassDef) -> Dict[str, str]:
    value = assignment_value(class_def, "SCREENS")
    literal = literal_structure(value) if value is not None else None
    screens: Dict[str, str] = {}
    if isinstance(literal, dict):
        for key, screen_value in literal.items():
            screens[str(key)] = str(screen_value)
    return screens


def extract_css_paths(class_def: ast.ClassDef) -> List[str]:
    value = assignment_value(class_def, "CSS_PATH")
    literal = literal_structure(value) if value is not None else None
    if isinstance(literal, str):
        return [literal]
    if isinstance(literal, (list, tuple)):
        return [str(item) for item in literal if isinstance(item, str)]
    return []


def extract_breakpoints(class_def: ast.ClassDef) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for attr in ("HORIZONTAL_BREAKPOINTS", "VERTICAL_BREAKPOINTS"):
        value = assignment_value(class_def, attr)
        literal = literal_structure(value) if value is not None else None
        if isinstance(literal, (list, tuple)):
            out[attr.lower()] = len(literal)
    return out


def extract_template_calls(tree: ast.AST) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = full_name(node.func)
        if not func:
            continue
        widget_name = func.split(".")[-1]
        record: Dict[str, str] = {"widget": widget_name}
        for keyword in node.keywords:
            if keyword.arg == "id":
                value = string_value(keyword.value)
                if value:
                    record["id"] = value
            if keyword.arg == "placeholder":
                value = string_value(keyword.value)
                if value:
                    record["placeholder"] = value
        if "id" in record or widget_name in BUILTIN_WIDGETS:
            results.append(record)
    return results


def collect_imports(tree: ast.AST) -> Dict[str, Set[str]]:
    imports: Dict[str, Set[str]] = {"modules": set(), "widgets": set(), "other_textual": set(), "rich": set()}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(TEXTUAL_IMPORT_PREFIX):
                    imports["modules"].add(alias.name)
                elif alias.name.startswith("rich"):
                    imports["rich"].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith(TEXTUAL_IMPORT_PREFIX):
                imports["modules"].add(module)
                names = {alias.name for alias in node.names}
                if module == "textual.widgets":
                    imports["widgets"].update(names)
                else:
                    imports["other_textual"].update(names)
            elif module.startswith("rich"):
                imports["rich"].update(alias.name for alias in node.names)
    return imports


def find_calls(tree: ast.AST) -> Set[str]:
    calls: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name:
                calls.add(name)
    return calls


def handler_blocking_calls(function_def: ast.AST) -> List[str]:
    found: List[str] = []
    for node in ast.walk(function_def):
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name and any(name.startswith(prefix) for prefix in BLOCKING_CALL_PREFIXES):
                found.append(name)
    return sorted(set(found))


def scan_textual_python_file(path: Path, root_dir: Optional[Path] = None) -> Dict[str, object]:
    tree = safe_parse(path)
    text = read_text(path)
    relative = to_posix(path.relative_to(root_dir or path.parent))
    if tree is None:
        return {
            "path": relative,
            "parse_error": True,
            "textual": "textual" in text,
        }

    imports = collect_imports(tree)
    calls = find_calls(tree)
    class_records: List[Dict[str, object]] = []
    app_classes: List[Dict[str, object]] = []
    screen_classes: List[Dict[str, object]] = []
    widget_classes: List[Dict[str, object]] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = class_base_names(node)
        kind = class_kind(bases)
        record: Dict[str, object] = {
            "name": node.name,
            "bases": bases,
            "kind": kind,
            "span": class_span(node),
            "methods": {
                "actions": method_names(node, "action_"),
                "handlers": method_names(node, "on_"),
                "watchers": method_names(node, "watch_"),
                "validators": method_names(node, "validate_"),
                "computes": method_names(node, "compute_"),
            },
            "decorators": [],
        }
        if kind == "app":
            record["bindings"] = extract_bindings(node)
            record["modes"] = extract_modes(node)
            record["screens"] = extract_screens(node)
            record["css_paths"] = extract_css_paths(node)
            record["breakpoints"] = extract_breakpoints(node)
            app_classes.append(record)
        elif kind == "screen":
            record["bindings"] = extract_bindings(node)
            record["css_paths"] = extract_css_paths(node)
            record["breakpoints"] = extract_breakpoints(node)
            screen_classes.append(record)
        elif kind == "widget":
            widget_classes.append(record)
        class_records.append(record)

    handler_calls: Dict[str, List[str]] = {}
    worker_decorators: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = decorator_names(node)
            if any(name.endswith("work") or name == "work" for name in decorators):
                worker_decorators.update(decorators)
            if node.name.startswith("on_") or node.name.startswith("action_") or node.name.startswith("compute_"):
                blocking = handler_blocking_calls(node)
                if blocking:
                    handler_calls[node.name] = blocking

    template_calls = extract_template_calls(tree)
    ids = sorted({record["id"] for record in template_calls if "id" in record})
    placeholders = sorted(
        {
            record["placeholder"]
            for record in template_calls
            if "placeholder" in record
        }
    )

    textual_detected = bool(
        imports["modules"]
        or imports["widgets"]
        or app_classes
        or screen_classes
        or widget_classes
        or ".tcss" in text
    )

    return {
        "path": relative,
        "parse_error": False,
        "textual": textual_detected,
        "imports": {
            key: sorted(value) for key, value in imports.items()
        },
        "calls": sorted(calls),
        "classes": class_records,
        "app_classes": app_classes,
        "screen_classes": screen_classes,
        "widget_classes": widget_classes,
        "ids": ids,
        "placeholders": placeholders,
        "handler_blocking_calls": handler_calls,
        "uses": {
            "reactive": "reactive" in text,
            "var": "var(" in text or " var" in text,
            "workers": "run_worker" in text or "work(" in text or "@work" in text,
            "run_test": "run_test(" in text,
            "pilot": "pilot." in text or "Pilot" in text,
            "deliver": "deliver_text(" in text or "deliver_binary(" in text or "deliver_screenshot(" in text,
            "command_palette": "COMMANDS" in text or "command_palette" in text,
            "modes": "MODES" in text,
            "screens": "SCREENS" in text or "install_screen(" in text or "push_screen(" in text,
            "breakpoints": "HORIZONTAL_BREAKPOINTS" in text or "VERTICAL_BREAKPOINTS" in text,
            "notify": "notify(" in text,
            "anchor": ".anchor(" in text,
            "batch_update": "batch_update(" in text,
            "capture_print": "begin_capture_print(" in text,
        },
        "template_calls": template_calls,
    }


def scan_project(project_root: Path) -> Dict[str, object]:
    py_files = sorted(iter_files(project_root, [".py"]))
    tcss_files = sorted(iter_files(project_root, [".tcss"]))
    scans: List[Dict[str, object]] = []
    for path in py_files:
        scan = scan_textual_python_file(path, root_dir=project_root)
        if scan.get("textual"):
            scans.append(scan)

    widgets_counter: Dict[str, int] = {}
    all_ids: Set[str] = set()
    all_placeholders: Set[str] = set()
    for scan in scans:
        for widget in scan["imports"]["widgets"]:
            widgets_counter[widget] = widgets_counter.get(widget, 0) + 1
        for template_call in scan["template_calls"]:
            widget_name = template_call["widget"]
            widgets_counter[widget_name] = widgets_counter.get(widget_name, 0) + 1
        all_ids.update(scan["ids"])
        all_placeholders.update(scan["placeholders"])

    tests = [
        scan for scan in scans if "/tests/" in f"/{scan['path']}/" or scan["path"].startswith("tests/")
    ]
    apps = []
    for scan in scans:
        apps.extend(
            [
                {"path": scan["path"], "class_name": record["name"]}
                for record in scan["app_classes"]
            ]
        )

    pyproject = project_root / "pyproject.toml"
    requirements = project_root / "requirements.txt"
    dependency_hints: List[str] = []
    if pyproject.exists():
        text = read_text(pyproject)
        for line in text.splitlines():
            if "textual" in line.lower():
                dependency_hints.append(line.strip())
    if requirements.exists():
        dependency_hints.extend(
            [line.strip() for line in read_text(requirements).splitlines() if "textual" in line.lower()]
        )

    return {
        "project_root": str(project_root.resolve()),
        "textual_detected": bool(scans or tcss_files),
        "python_file_count": len(py_files),
        "textual_python_file_count": len(scans),
        "stylesheet_count": len(tcss_files),
        "stylesheets": [to_posix(path.relative_to(project_root)) for path in tcss_files],
        "apps": apps,
        "tests": [{"path": scan["path"], "uses": scan["uses"]} for scan in tests],
        "widget_usage": sorted(
            [{"widget": widget, "count": count} for widget, count in widgets_counter.items()],
            key=lambda item: (-item["count"], item["widget"]),
        ),
        "ids": sorted(all_ids),
        "placeholders": sorted(all_placeholders),
        "dependency_hints": dependency_hints,
        "files": scans,
    }


def safe_key_for_test(binding: Dict[str, str]) -> bool:
    key = binding["key"]
    action = binding["action"]
    if action.split("(")[0] in BINDING_VERBS_TO_SKIP:
        return False
    if key.lower() in {"q", "ctrl+c", "escape"}:
        return False
    return True


def render_template(text: str, replacements: Dict[str, str]) -> str:
    pattern = re.compile(r"{{([A-Z0-9_]+)}}")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in replacements:
            raise KeyError("Unknown template placeholder: {0}".format(key))
        return replacements[key]

    return pattern.sub(replace, text)


def load_asset(*parts: str) -> str:
    return (SKILL_ROOT / "assets" / Path(*parts)).read_text(encoding="utf-8")


def write_text_file(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError("Refusing to overwrite existing file without --force: {0}".format(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def json_dumps(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=False)
