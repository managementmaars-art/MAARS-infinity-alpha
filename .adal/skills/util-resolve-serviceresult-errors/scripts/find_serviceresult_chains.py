#!/usr/bin/env python3
"""Analyze ServiceResult chaining opportunities.

This script analyzes code to find:
1. Nested ServiceResult operations that could use composition
2. Manual unwrapping that could use utils
3. Sequential checks that could use chain_results
4. Opportunities to use map_result, compose_results, etc.

Usage:
    python find_serviceresult_chains.py src/
    python find_serviceresult_chains.py --suggest-refactor src/
    python find_serviceresult_chains.py --complexity-threshold 3 src/
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


class ServiceResultChainAnalyzer(ast.NodeVisitor):
    """Analyze ServiceResult chaining patterns."""

    def __init__(self, file_path: str, complexity_threshold: int = 2) -> None:
        self.file_path = file_path
        self.complexity_threshold = complexity_threshold
        self.opportunities: list[dict[str, Any]] = []
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function for chaining opportunities."""
        old_function = self.current_function
        self.current_function = node.name

        self._analyze_function_body(node)

        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async function for chaining opportunities."""
        old_function = self.current_function
        self.current_function = node.name

        self._analyze_function_body(node)

        self.generic_visit(node)
        self.current_function = old_function

    def _analyze_function_body(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Analyze function body for patterns."""
        # Check for sequential ServiceResult operations
        sequential_checks = self._find_sequential_checks(node)
        if len(sequential_checks) >= self.complexity_threshold:
            self.opportunities.append(
                {
                    "type": "sequential_checks",
                    "complexity": len(sequential_checks),
                    "file": self.file_path,
                    "line": node.lineno,
                    "function": node.name,
                    "message": f"Found {len(sequential_checks)} sequential ServiceResult checks",
                    "suggestion": "Consider using compose_results or chain_results",
                    "example": self._generate_composition_example(sequential_checks),
                    "code_snippet": ast.unparse(node),
                }
            )

        # Check for manual unwrapping
        manual_unwraps = self._find_manual_unwraps(node)
        if manual_unwraps:
            for unwrap in manual_unwraps:
                self.opportunities.append(
                    {
                        "type": "manual_unwrap",
                        "complexity": 1,
                        "file": self.file_path,
                        "line": unwrap["line"],
                        "function": node.name,
                        "message": "Manual unwrapping pattern detected",
                        "suggestion": "Use unwrap_or, unwrap_or_raise, or composition utilities",
                        "example": unwrap["example"],
                    }
                )

        # Check for transformations (could use map_result)
        transformations = self._find_transformations(node)
        if transformations:
            for transform in transformations:
                self.opportunities.append(
                    {
                        "type": "transformation",
                        "complexity": 1,
                        "file": self.file_path,
                        "line": transform["line"],
                        "function": node.name,
                        "message": "ServiceResult transformation could use map_result",
                        "suggestion": "Use map_result for cleaner transformations",
                        "example": transform["example"],
                    }
                )

        # Check for list of results (could use collect_results)
        list_patterns = self._find_list_collection_patterns(node)
        if list_patterns:
            for pattern in list_patterns:
                self.opportunities.append(
                    {
                        "type": "list_collection",
                        "complexity": 2,
                        "file": self.file_path,
                        "line": pattern["line"],
                        "function": node.name,
                        "message": "Manual collection of ServiceResults",
                        "suggestion": "Use collect_results or flatten_results",
                        "example": pattern["example"],
                    }
                )

    def _find_sequential_checks(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[dict[str, Any]]:
        """Find sequential if result.success checks."""
        checks = []

        class SequentialChecker(ast.NodeVisitor):
            def __init__(self) -> None:
                self.checks = []
                self.nesting_level = 0

            def visit_If(self, node: ast.If) -> None:
                # Check if this is a .success check
                if self._is_success_check(node.test):
                    self.checks.append(
                        {
                            "line": node.lineno,
                            "nesting": self.nesting_level,
                            "test": ast.unparse(node.test),
                        }
                    )

                # Visit nested content
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def _is_success_check(self, node: ast.expr) -> bool:
                if isinstance(node, ast.Attribute):
                    return node.attr in ("success", "is_success")
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        return node.left.attr in ("success", "is_success")
                return False

        checker = SequentialChecker()
        checker.visit(node)

        # Find sequences of checks (nested or sequential)
        if len(checker.checks) >= 2:
            # Group by proximity
            current_sequence = [checker.checks[0]]
            for check in checker.checks[1:]:
                last_check = current_sequence[-1]
                if check["nesting"] >= last_check["nesting"]:
                    current_sequence.append(check)
            checks = current_sequence

        return checks

    def _find_manual_unwraps(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[dict[str, Any]]:
        """Find manual unwrapping patterns like: if result.success: data = result.data."""

        class UnwrapFinder(ast.NodeVisitor):
            def __init__(self) -> None:
                self.unwraps = []

            def visit_If(self, node: ast.If) -> None:
                # Check for pattern: if result.success: data = result.data
                if self._is_success_check(node.test):
                    var_name = self._extract_var_name(node.test)
                    if var_name:
                        # Check if body accesses .data
                        for stmt in node.body:
                            if isinstance(stmt, ast.Assign):
                                if isinstance(stmt.value, ast.Attribute):
                                    if (
                                        isinstance(stmt.value.value, ast.Name)
                                        and stmt.value.value.id == var_name
                                        and stmt.value.attr == "data"
                                    ):
                                        self.unwraps.append(
                                            {
                                                "line": node.lineno,
                                                "var": var_name,
                                                "example": self._generate_unwrap_example(
                                                    var_name
                                                ),
                                            }
                                        )

                self.generic_visit(node)

            def _is_success_check(self, node: ast.expr) -> bool:
                if isinstance(node, ast.Attribute):
                    return node.attr in ("success", "is_success")
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        return node.left.attr in ("success", "is_success")
                return False

            def _extract_var_name(self, node: ast.expr) -> str | None:
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        return node.value.id
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        if isinstance(node.left.value, ast.Name):
                            return node.left.value.id
                return None

            def _generate_unwrap_example(self, var_name: str) -> str:
                return f"""# Instead of:
if {var_name}.success:
    data = {var_name}.data
    # use data...
else:
    return ServiceResult.fail({var_name}.error)

# Use:
data = {var_name}.unwrap_or_raise()  # Raises on failure
# or
data = {var_name}.unwrap_or(default_value)  # Returns default on failure
"""

        finder = UnwrapFinder()
        finder.visit(node)
        return finder.unwraps

    def _find_transformations(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[dict[str, Any]]:
        """Find transformation patterns that could use map_result."""

        class TransformFinder(ast.NodeVisitor):
            def __init__(self) -> None:
                self.transforms = []

            def visit_If(self, node: ast.If) -> None:
                # Look for: if result.success: new_data = transform(result.data)
                if self._is_success_check(node.test):
                    var_name = self._extract_var_name(node.test)
                    if var_name:
                        for stmt in node.body:
                            if isinstance(stmt, ast.Assign):
                                # Check if RHS is a function call using result.data
                                if isinstance(stmt.value, ast.Call):
                                    if self._uses_result_data(stmt.value, var_name):
                                        self.transforms.append(
                                            {
                                                "line": node.lineno,
                                                "example": self._generate_map_example(
                                                    var_name
                                                ),
                                            }
                                        )

                self.generic_visit(node)

            def _is_success_check(self, node: ast.expr) -> bool:
                if isinstance(node, ast.Attribute):
                    return node.attr in ("success", "is_success")
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        return node.left.attr in ("success", "is_success")
                return False

            def _extract_var_name(self, node: ast.expr) -> str | None:
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        return node.value.id
                if isinstance(node, ast.Compare):
                    if isinstance(node.left, ast.Attribute):
                        if isinstance(node.left.value, ast.Name):
                            return node.left.value.id
                return None

            def _uses_result_data(self, call_node: ast.Call, var_name: str) -> bool:
                """Check if call uses result.data."""
                for arg in call_node.args:
                    if isinstance(arg, ast.Attribute) and (
                        isinstance(arg.value, ast.Name)
                        and arg.value.id == var_name
                        and arg.attr == "data"
                    ):
                        return True
                return False

            def _generate_map_example(self, var_name: str) -> str:
                return f"""# Instead of:
if {var_name}.success:
    transformed = transform({var_name}.data)
    return ServiceResult.ok(transformed)
else:
    return {var_name}

# Use:
from project_watch_mcp.domain.common.service_result_utils import map_result
return map_result(transform, {var_name})
"""

        finder = TransformFinder()
        finder.visit(node)
        return finder.transforms

    def _find_list_collection_patterns(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[dict[str, Any]]:
        """Find manual collection of ServiceResults into lists."""

        class CollectionFinder(ast.NodeVisitor):
            def __init__(self) -> None:
                self.patterns = []

            def visit_For(self, node: ast.For) -> None:
                # Look for pattern: for item in items: result = process(item); results.append(result)
                has_result_append = False
                has_failure_check = False

                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Attribute):
                            if stmt.func.attr == "append":
                                has_result_append = True
                    if isinstance(stmt, ast.If):
                        if isinstance(stmt.test, ast.Attribute):
                            if stmt.test.attr in (
                                "is_failure",
                                "success",
                                "is_success",
                            ):
                                has_failure_check = True

                if has_result_append and has_failure_check:
                    self.patterns.append(
                        {
                            "line": node.lineno,
                            "example": self._generate_collect_example(),
                        }
                    )

                self.generic_visit(node)

            def _generate_collect_example(self) -> str:
                return """# Instead of:
results = []
for item in items:
    result = process(item)
    if result.is_failure:
        return result
    results.append(result.data)
return ServiceResult.ok(results)

# Use:
from project_watch_mcp.domain.common.service_result_utils import collect_results
results = [process(item) for item in items]
return collect_results(results)
"""

        finder = CollectionFinder()
        finder.visit(node)
        return finder.patterns

    def _generate_composition_example(self, checks: list[dict[str, Any]]) -> str:
        """Generate example of how to use composition utilities."""
        return f"""# Instead of {len(checks)} nested checks:
result1 = operation1()
if result1.success:
    result2 = operation2(result1.data)
    if result2.success:
        result3 = operation3(result2.data)
        if result3.success:
            return result3
        return result3
    return result2
return result1

# Use compose_results:
from project_watch_mcp.domain.common.service_result_utils import compose_results

result = operation1()
result = compose_results(operation2, result)
result = compose_results(operation3, result)
return result
"""


def analyze_file(file_path: Path, complexity_threshold: int = 2) -> dict[str, Any]:
    """Analyze a file for ServiceResult chaining opportunities.

    Args:
        file_path: Path to the Python file
        complexity_threshold: Minimum complexity to report

    Returns:
        Dictionary with analysis results
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}"}

    analyzer = ServiceResultChainAnalyzer(str(file_path), complexity_threshold)
    analyzer.visit(tree)

    return {
        "file": str(file_path),
        "opportunities": analyzer.opportunities,
        "total_complexity": sum(o["complexity"] for o in analyzer.opportunities),
    }


def analyze_directory(
    directory: Path, complexity_threshold: int = 2
) -> list[dict[str, Any]]:
    """Analyze all Python files in a directory.

    Args:
        directory: Path to directory
        complexity_threshold: Minimum complexity to report

    Returns:
        List of analysis results for each file
    """
    results = []

    for py_file in directory.rglob("*.py"):
        # Skip test files and __init__.py
        if py_file.name.startswith("test_") or py_file.name == "__init__.py":
            continue

        result = analyze_file(py_file, complexity_threshold)
        if result.get("opportunities"):
            results.append(result)

    return results


def print_report(results: list[dict[str, Any]], suggest_refactor: bool = False) -> None:
    """Print analysis report.

    Args:
        results: List of analysis results
        suggest_refactor: If True, show refactoring suggestions
    """
    total_opportunities = sum(len(r.get("opportunities", [])) for r in results)
    total_complexity = sum(r.get("total_complexity", 0) for r in results)

    print("\n=== ServiceResult Chaining Analysis Report ===\n")
    print(f"Total opportunities found: {total_opportunities}")
    print(f"Total complexity score: {total_complexity}\n")

    # Sort by complexity
    sorted_results = sorted(
        results, key=lambda r: r.get("total_complexity", 0), reverse=True
    )

    for result in sorted_results:
        if "error" in result:
            print(f"ERROR in {result['file']}: {result['error']}\n")
            continue

        print(f"File: {result['file']}")
        print(f"  Opportunities: {len(result['opportunities'])}")
        print(f"  Complexity: {result['total_complexity']}")

        for opp in result["opportunities"]:
            icon = "[CHAIN]" if opp["type"] == "sequential_checks" else "[TIP]"
            print(f"\n  {icon} {opp['message']} (Line {opp['line']})")
            print(f"     Type: {opp['type']}")
            print(f"     Suggestion: {opp['suggestion']}")

            if suggest_refactor:
                print("     Example:")
                for line in opp["example"].split("\n"):
                    if line.strip():
                        print(f"       {line}")

        print()

    # Count opportunity types
    opp_types = {}
    for result in results:
        for opp in result.get("opportunities", []):
            otype = opp["type"]
            opp_types[otype] = opp_types.get(otype, 0) + 1

    if opp_types:
        print("\nSummary by Type:")
        for otype, count in sorted(opp_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {otype}: {count}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: find_serviceresult_chains.py [OPTIONS] <directory_or_file>")
        print("\nOptions:")
        print(
            "  --suggest-refactor          Show refactoring suggestions with examples"
        )
        print(
            "  --complexity-threshold N    Only show opportunities with complexity >= N (default: 2)"
        )
        print("\nExamples:")
        print("  python find_serviceresult_chains.py src/")
        print("  python find_serviceresult_chains.py --suggest-refactor src/")
        print("  python find_serviceresult_chains.py --complexity-threshold 3 src/")
        sys.exit(1)

    suggest_refactor = "--suggest-refactor" in sys.argv
    complexity_threshold = 2

    # Check for complexity threshold
    if "--complexity-threshold" in sys.argv:
        idx = sys.argv.index("--complexity-threshold")
        if idx + 1 < len(sys.argv):
            complexity_threshold = int(sys.argv[idx + 1])

    # Find directory/file argument
    target = None
    for arg in sys.argv[1:]:
        if (
            arg
            not in (
                "--suggest-refactor",
                "--complexity-threshold",
                str(complexity_threshold),
            )
            and arg != sys.argv[0]
        ):
            target = arg
            break

    if not target:
        sys.exit(1)

    target_path = Path(target)

    if target_path.is_file():
        results = [analyze_file(target_path, complexity_threshold)]
    elif target_path.is_dir():
        results = analyze_directory(target_path, complexity_threshold)
    else:
        sys.exit(1)

    print_report(results, suggest_refactor=suggest_refactor)


if __name__ == "__main__":
    main()
