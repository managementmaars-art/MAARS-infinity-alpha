#!/usr/bin/env python3
"""Validate ServiceResult usage patterns across the codebase.

This script validates that ServiceResult is used correctly:
1. Service methods return ServiceResult[T]
2. Proper .data and .error access patterns
3. No bare None returns from services
4. Success/failure checks before data access
5. Proper async ServiceResult handling

Usage:
    python validate_serviceresult_usage.py src/
    python validate_serviceresult_usage.py --strict src/  # Fail on any violations
    python validate_serviceresult_usage.py --json report.json src/  # JSON output
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

# Setup: Add .claude/tools to path for utilities
_CLAUDE_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_CLAUDE_ROOT / "tools"))

from skill_utils import ensure_path_setup  # noqa: E402

ensure_path_setup()


class ServiceResultValidator(ast.NodeVisitor):
    """Validate ServiceResult usage patterns."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.violations: list[dict[str, Any]] = []
        self.current_class = None
        self.current_function = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class context."""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Validate function definitions."""
        old_function = self.current_function
        self.current_function = node.name

        # Check if service method (in a Service class)
        if self._is_service_class(self.current_class):
            self._check_service_method_return_type(node)
            self._check_bare_none_return(node)

        # Check ServiceResult usage in function body
        self._check_data_access_patterns(node)

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async function definitions."""
        old_function = self.current_function
        self.current_function = node.name

        if self._is_service_class(self.current_class):
            self._check_service_method_return_type(node)
            self._check_bare_none_return(node)

        self._check_data_access_patterns(node)

        self.generic_visit(node)
        self.current_function = old_function

    def _is_service_class(self, class_name: str | None) -> bool:
        """Check if class name suggests it's a service."""
        if not class_name:
            return False
        return (
            "Service" in class_name
            or "Handler" in class_name
            or "Repository" in class_name
        )

    def _check_service_method_return_type(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Check if service method returns ServiceResult."""
        # Skip dunder methods and private methods
        if node.name.startswith("_"):
            return

        # Check return annotation
        if node.returns:
            annotation = ast.unparse(node.returns)

            # Should return ServiceResult[T]
            if "ServiceResult" not in annotation:
                self.violations.append(
                    {
                        "type": "missing_serviceresult_return",
                        "severity": "error",
                        "file": self.file_path,
                        "line": node.lineno,
                        "class": self.current_class,
                        "method": node.name,
                        "message": f"Service method should return ServiceResult[T], got: {annotation}",
                        "suggestion": f"Change return type to ServiceResult[{annotation}]",
                    }
                )
        else:
            # Missing return annotation
            self.violations.append(
                {
                    "type": "missing_return_annotation",
                    "severity": "warning",
                    "file": self.file_path,
                    "line": node.lineno,
                    "class": self.current_class,
                    "method": node.name,
                    "message": "Service method missing return type annotation",
                    "suggestion": "Add return type annotation: -> ServiceResult[T]",
                }
            )

    def _check_bare_none_return(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Check for bare None returns instead of ServiceResult."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return):
                # Check for return None without ServiceResult wrapper
                if stmt.value is None or (
                    isinstance(stmt.value, ast.Constant) and stmt.value.value is None
                ):
                    self.violations.append(
                        {
                            "type": "bare_none_return",
                            "severity": "error",
                            "file": self.file_path,
                            "line": stmt.lineno,
                            "class": self.current_class,
                            "method": node.name,
                            "message": "Service method returns bare None instead of ServiceResult",
                            "suggestion": "Return ServiceResult.ok(None) or ServiceResult.fail(error)",
                        }
                    )

    def _check_data_access_patterns(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Check for unsafe .data access without success check."""

        class DataAccessChecker(ast.NodeVisitor):
            def __init__(self, validator) -> None:
                self.validator = validator
                self.checked_variables = set()
                self.current_if_test = None

            def visit_If(self, node: ast.If) -> None:
                """Track variables checked in if conditions."""
                old_test = self.current_if_test
                self.current_if_test = node.test

                # Check if condition checks .success or .is_success
                if self._checks_success(node.test):
                    # Extract variable name being checked
                    var_name = self._extract_variable_name(node.test)
                    if var_name:
                        self.checked_variables.add(var_name)

                # Visit if body with tracked checks
                for stmt in node.body:
                    self.visit(stmt)

                # Reset for else clause
                if node.orelse:
                    for stmt in node.orelse:
                        self.visit(stmt)

                self.current_if_test = old_test

            def visit_Attribute(self, node: ast.Attribute) -> None:
                """Check .data access patterns."""
                if node.attr == "data":
                    # Check if accessing .data on a variable
                    if isinstance(node.value, ast.Name):
                        var_name = node.value.id

                        # Check if this variable was checked for success
                        if var_name not in self.checked_variables:
                            self.validator.violations.append(
                                {
                                    "type": "unsafe_data_access",
                                    "severity": "warning",
                                    "file": self.validator.file_path,
                                    "line": node.lineno,
                                    "class": self.validator.current_class,
                                    "method": self.validator.current_function,
                                    "message": f"Accessing .data on {var_name} without checking .success first",
                                    "suggestion": f"Add check: if {var_name}.success: ... before accessing .data",
                                }
                            )

                self.generic_visit(node)

            def _checks_success(self, node: ast.expr) -> bool:
                """Check if expression checks .success or .is_success."""
                if isinstance(node, ast.Attribute):
                    return node.attr in ("success", "is_success", "is_failure")
                if isinstance(node, ast.Compare):
                    for comp in [node.left, *node.comparators]:
                        if isinstance(comp, ast.Attribute) and comp.attr in (
                            "success",
                            "is_success",
                            "is_failure",
                        ):
                            return True
                return False

            def _extract_variable_name(self, node: ast.expr) -> str | None:
                """Extract variable name from success check."""
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        return node.value.id
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        if isinstance(node.left.value, ast.Name):
                            return node.left.value.id
                return None

        checker = DataAccessChecker(self)
        checker.visit(node)


def validate_file(file_path: Path) -> dict[str, Any]:
    """Validate ServiceResult usage in a file.

    Args:
        file_path: Path to the Python file

    Returns:
        Dictionary with validation results
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}

    validator = ServiceResultValidator(str(file_path))
    validator.visit(tree)

    return {
        "file": str(file_path),
        "violations": validator.violations,
        "error_count": sum(1 for v in validator.violations if v["severity"] == "error"),
        "warning_count": sum(
            1 for v in validator.violations if v["severity"] == "warning"
        ),
    }


def validate_directory(directory: Path) -> list[dict[str, Any]]:
    """Validate all Python files in a directory.

    Args:
        directory: Path to directory

    Returns:
        List of validation results for each file
    """
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip test files and __init__.py
        if py_file.name.startswith("test_") or py_file.name == "__init__.py":
            continue

        result = validate_file(py_file)
        if result.get("violations"):
            results.append(result)

    return results


def print_report(
    results: list[dict[str, Any]], verbose: bool = False
) -> tuple[int, int]:
    """Print validation report.

    Args:
        results: List of validation results
        verbose: If True, show all violations

    Returns:
        Tuple of (total_errors, total_warnings)
    """
    total_errors = sum(r.get("error_count", 0) for r in results)
    total_warnings = sum(r.get("warning_count", 0) for r in results)
    num_files = len(results)

    print("\n=== ServiceResult Usage Validation Report ===\n")
    print(f"Files analyzed: {num_files}")
    print(f"Total errors: {total_errors}")
    print(f"Total warnings: {total_warnings}\n")

    if not verbose and total_errors + total_warnings > 20:
        print(
            f"Note: Showing first 20 violations (use --verbose to see all {total_errors + total_warnings})\n"
        )

    violation_count = 0
    for result in results:
        if "error" in result:
            print(f"ERROR in {result['file']}: {result['error']}\n")
            continue

        if result.get("violations"):
            print(f"File: {result['file']}")
            print(
                f"  Errors: {result.get('error_count', 0)}, Warnings: {result.get('warning_count', 0)}"
            )

            for violation in result["violations"]:
                if not verbose and violation_count >= 20:
                    break

                violation_count += 1

                icon = "[ERROR]" if violation["severity"] == "error" else "[WARN]"
                print(f"\n  {icon} {violation['type']} (Line {violation['line']})")
                print(f"     {violation['message']}")
                print(f"     Suggestion: {violation['suggestion']}")

                if violation.get("class"):
                    print(
                        f"     In: {violation['class']}.{violation.get('method', '?')}"
                    )

            if not verbose and len(result["violations"]) > 20:
                print(f"\n  ... and {len(result['violations']) - 20} more violations")

            print()

    # Count violation types
    violation_types = {}
    for result in results:
        for violation in result.get("violations", []):
            vtype = violation["type"]
            violation_types[vtype] = violation_types.get(vtype, 0) + 1

    if violation_types:
        print("Summary by Violation Type:")
        for vtype, count in sorted(
            violation_types.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {vtype}: {count}")

    return total_errors, total_warnings


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_serviceresult_usage.py [OPTIONS] <directory_or_file>")
        print("\nOptions:")
        print(
            "  --strict          Treat warnings as errors (exit with error code if any violations)"
        )
        print("  --verbose         Show all violations (default: show first 20)")
        print("  --json <output>   Write results to JSON file")
        print("\nExamples:")
        print("  python validate_serviceresult_usage.py src/")
        print("  python validate_serviceresult_usage.py --strict src/")
        print("  python validate_serviceresult_usage.py --json report.json src/")
        print("  python validate_serviceresult_usage.py --verbose --strict src/")
        sys.exit(1)

    strict = "--strict" in sys.argv
    verbose = "--verbose" in sys.argv
    json_output = None

    # Check for JSON output
    if "--json" in sys.argv:
        idx = sys.argv.index("--json")
        if idx + 1 < len(sys.argv):
            json_output = sys.argv[idx + 1]

    # Find directory/file argument
    target = None
    for arg in sys.argv[1:]:
        if arg not in ("--strict", "--verbose", "--json") and arg != json_output:
            target = arg
            break

    if not target:
        print("ERROR: No directory or file specified")
        sys.exit(1)

    target_path = Path(target)

    if target_path.is_file():
        results = [validate_file(target_path)]
    elif target_path.is_dir():
        results = validate_directory(target_path)
    else:
        print(f"ERROR: Path not found: {target}")
        sys.exit(1)

    # Output results
    if json_output:
        with open(json_output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results written to: {json_output}")

    total_errors, total_warnings = print_report(results, verbose=verbose)

    # Exit with error code if violations found
    if (strict and (total_errors > 0 or total_warnings > 0)) or total_errors > 0:
        exit_code = (
            1 if total_errors > 0 else (1 if strict and total_warnings > 0 else 0)
        )
        if exit_code == 1:
            print(
                f"\nValidation failed: {total_errors} errors, {total_warnings} warnings"
            )
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
