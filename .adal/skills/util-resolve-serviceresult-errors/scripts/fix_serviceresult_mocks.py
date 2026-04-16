#!/usr/bin/env python3
"""Auto-fix ServiceResult mock errors in test files.

This script automatically fixes common ServiceResult mock mistakes:
1. Mocks returning dicts instead of ServiceResult
2. Missing ServiceResult.ok() wrappers
3. Incorrect AsyncMock configurations
4. Missing ServiceResult imports

Usage:
    python fix_serviceresult_mocks.py <test_file.py>
    python fix_serviceresult_mocks.py --check <test_file.py>  # Dry run
    python fix_serviceresult_mocks.py --all tests/          # Fix all test files
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

# Setup: Add .claude/tools to path for utilities
_CLAUDE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_CLAUDE_ROOT / "tools"))

from skill_utils import ensure_path_setup  # noqa: E402

ensure_path_setup()


class ServiceResultMockFixer(ast.NodeTransformer):
    """AST transformer to fix ServiceResult mock patterns."""

    def __init__(self) -> None:
        self.changes: list[dict[str, Any]] = []
        self.needs_serviceresult_import = False

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Fix mock return_value assignments."""
        self.generic_visit(node)

        # Check for AsyncMock/Mock with return_value
        if isinstance(node.func, ast.Name) and node.func.id in (
            "AsyncMock",
            "Mock",
            "MagicMock",
        ):
            for keyword in node.keywords:
                if keyword.arg == "return_value":
                    fixed_value = self._fix_return_value(keyword.value)
                    if fixed_value != keyword.value:
                        keyword.value = fixed_value
                        self.changes.append(
                            {
                                "type": "mock_return_value",
                                "line": node.lineno,
                                "original": ast.unparse(keyword.value),
                                "fixed": ast.unparse(fixed_value),
                            }
                        )
                        self.needs_serviceresult_import = True

        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Fix mock method assignments like: mock.method = AsyncMock(...)."""
        self.generic_visit(node)

        # Check if RHS is AsyncMock/Mock call
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id in (
                "AsyncMock",
                "Mock",
                "MagicMock",
            ):
                for keyword in node.value.keywords:
                    if keyword.arg == "return_value":
                        fixed_value = self._fix_return_value(keyword.value)
                        if fixed_value != keyword.value:
                            keyword.value = fixed_value
                            self.changes.append(
                                {
                                    "type": "mock_assignment",
                                    "line": node.lineno,
                                    "target": ast.unparse(node.targets[0]),
                                    "original": ast.unparse(keyword.value),
                                    "fixed": ast.unparse(fixed_value),
                                }
                            )
                            self.needs_serviceresult_import = True

        return node

    def _fix_return_value(self, value_node: ast.expr) -> ast.expr:
        """Fix a return_value to wrap it in ServiceResult.ok()."""
        # If already wrapped in ServiceResult.ok() or ServiceResult.fail(), skip
        if self._is_serviceresult_call(value_node):
            return value_node

        # If it's a dict, list, or other literal, wrap it
        if isinstance(value_node, (ast.Dict, ast.List, ast.Constant, ast.Tuple)):
            return self._wrap_in_serviceresult_ok(value_node)

        # If it's a Name (variable), wrap it
        if isinstance(value_node, ast.Name):
            return self._wrap_in_serviceresult_ok(value_node)

        return value_node

    def _is_serviceresult_call(self, node: ast.expr) -> bool:
        """Check if node is ServiceResult.ok() or ServiceResult.fail()."""
        if not isinstance(node, ast.Call):
            return False

        if isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            return node.func.value.id == "ServiceResult" and node.func.attr in (
                "ok",
                "fail",
                "failure",
            )

        return False

    def _wrap_in_serviceresult_ok(self, value_node: ast.expr) -> ast.Call:
        """Wrap a value in ServiceResult.ok()."""
        return ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="ServiceResult", ctx=ast.Load()),
                attr="ok",
                ctx=ast.Load(),
            ),
            args=[value_node],
            keywords=[],
        )


class ImportAnalyzer(ast.NodeVisitor):
    """Analyze imports to check if ServiceResult is imported."""

    def __init__(self) -> None:
        self.has_serviceresult_import = False
        self.import_line = 0
        self.last_import_line = 0

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for ServiceResult import."""
        self.last_import_line = max(self.last_import_line, node.lineno)

        if node.module == "project_watch_mcp.domain.common":
            for alias in node.names:
                if alias.name == "ServiceResult":
                    self.has_serviceresult_import = True
                    self.import_line = node.lineno
                    break

    def visit_Import(self, node: ast.Import) -> None:
        """Track last import line."""
        self.last_import_line = max(self.last_import_line, node.lineno)


def add_serviceresult_import(
    source_lines: list[str], last_import_line: int
) -> list[str]:
    """Add ServiceResult import to the file."""
    import_statement = "from project_watch_mcp.domain.common import ServiceResult\n"

    # Insert after the last import
    if last_import_line > 0:
        source_lines.insert(last_import_line, import_statement)
    else:
        # No imports found, add at the top after docstring
        insert_line = 0
        for i, line in enumerate(source_lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Find end of docstring
                j = i + 1
                while j < len(source_lines):
                    if '"""' in source_lines[j] or "'''" in source_lines[j]:
                        insert_line = j + 1
                        break
                    j += 1
                break

        source_lines.insert(insert_line, import_statement)

    return source_lines


def fix_file(file_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Fix ServiceResult mocks in a file.

    Args:
        file_path: Path to the test file
        dry_run: If True, only report changes without modifying file

    Returns:
        Dictionary with fix results
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}

    # Check existing imports
    import_analyzer = ImportAnalyzer()
    import_analyzer.visit(tree)

    # Fix mocks
    fixer = ServiceResultMockFixer()
    fixed_tree = fixer.visit(tree)

    if not fixer.changes:
        return {"status": "no_changes", "file": str(file_path)}

    # Add import if needed
    if (
        fixer.needs_serviceresult_import
        and not import_analyzer.has_serviceresult_import
    ):
        source_lines = source.splitlines(keepends=True)
        source_lines = add_serviceresult_import(
            source_lines, import_analyzer.last_import_line
        )
        source = "".join(source_lines)

    # Generate fixed code
    fixed_code = ast.unparse(fixed_tree)

    result = {
        "status": "fixed",
        "file": str(file_path),
        "changes": fixer.changes,
        "import_added": fixer.needs_serviceresult_import
        and not import_analyzer.has_serviceresult_import,
    }

    if not dry_run:
        # Write fixed code
        file_path.write_text(fixed_code)
        result["written"] = True

    return result


def fix_directory(directory: Path, dry_run: bool = False) -> list[dict[str, Any]]:
    """Fix all test files in a directory.

    Args:
        directory: Path to directory containing test files
        dry_run: If True, only report changes without modifying files

    Returns:
        List of fix results for each file
    """
    results = []

    for test_file in directory.rglob("test_*.py"):
        result = fix_file(test_file, dry_run=dry_run)
        results.append(result)

    return results


def print_report(results: list[dict[str, Any]]) -> None:
    """Print a summary report of fixes."""
    total_files = len(results)
    fixed = sum(1 for r in results if r.get("status") == "fixed")
    errors = sum(1 for r in results if "error" in r)
    no_changes = sum(1 for r in results if r.get("status") == "no_changes")

    print("\n=== ServiceResult Mock Fix Report ===\n")
    print(f"Files analyzed: {total_files}")
    print(f"Files fixed: {fixed}")
    print(f"No changes needed: {no_changes}")
    print(f"Errors: {errors}\n")

    if fixed > 0:
        print("Fixed files:")
        for result in results:
            if result.get("status") == "fixed":
                print(f"\n  {result['file']}")
                if result.get("import_added"):
                    print("    + Added ServiceResult import")

                print(f"    Changes: {len(result['changes'])}")
                for change in result["changes"][:5]:  # Show first 5 changes
                    print(f"      - {change['type']} at line {change['line']}")
                    print(f"        {change['original']} -> {change['fixed']}")

                if len(result["changes"]) > 5:
                    print(f"      ... and {len(result['changes']) - 5} more changes")

    if errors > 0:
        print("\nErrors encountered:")
        for result in results:
            if "error" in result:
                print(f"  {result['file']}: {result['error']}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: fix_serviceresult_mocks.py [OPTIONS] <test_file.py|tests_directory>"
        )
        print("\nOptions:")
        print(
            "  --check           Dry run mode - show what would be fixed without modifying files"
        )
        print("  --all             Fix all test files in directory")
        print("\nExamples:")
        print("  python fix_serviceresult_mocks.py tests/unit/test_service.py")
        print("  python fix_serviceresult_mocks.py --check tests/unit/test_service.py")
        print("  python fix_serviceresult_mocks.py --all tests/")
        sys.exit(1)

    dry_run = "--check" in sys.argv
    fix_all = "--all" in sys.argv

    if fix_all:
        # Find directory argument
        directory_arg = next(
            (arg for arg in sys.argv if arg not in ("--check", "--all", sys.argv[0])),
            "tests/",
        )
        directory = Path(directory_arg)

        if not directory.is_dir():
            print(f"ERROR: Directory not found: {directory}")
            sys.exit(1)

        results = fix_directory(directory, dry_run=dry_run)
        print_report(results)
        if dry_run:
            print("\nDry run mode - no files were modified")
    else:
        # Single file mode
        file_arg = next(
            (arg for arg in sys.argv if arg not in ("--check", sys.argv[0])), None
        )
        if not file_arg:
            print("ERROR: No file specified")
            sys.exit(1)

        file_path = Path(file_arg)
        result = fix_file(file_path, dry_run=dry_run)

        if "error" in result:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

        if result["status"] == "no_changes":
            print(f"No changes needed in {file_path}")
        else:
            print(f"\n{file_path}")
            if result.get("import_added"):
                print("  + Added ServiceResult import")

            print(f"  Changes made: {len(result['changes'])}")
            for change in result["changes"]:
                print(f"    - {change['type']} at line {change['line']}")

        if dry_run:
            print("\nDry run mode - no files were modified")


if __name__ == "__main__":
    main()
