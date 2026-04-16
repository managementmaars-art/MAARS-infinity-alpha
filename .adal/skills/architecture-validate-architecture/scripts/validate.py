#!/usr/bin/env python3
"""Architecture Validation Script.

Validates architectural patterns and layer boundaries.
Supports Clean Architecture, Hexagonal, Layered, and MVC patterns.

Usage:
    python validate.py                    # Validate entire codebase
    python validate.py --files file.py    # Validate specific files
    python validate.py --strict           # Fail on any violation
    python validate.py --architecture clean  # Specify pattern explicitly

Exit codes:
    0: No violations (or only LOW/MEDIUM if not strict)
    1: Critical or High violations found
    2: Configuration error
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final


class Severity(Enum):
    """Violation severity levels"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ArchitecturePattern(Enum):
    """Supported architecture patterns"""

    CLEAN = "clean"
    HEXAGONAL = "hexagonal"
    LAYERED = "layered"
    MVC = "mvc"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class LayerRule:
    """Rules for a specific layer.

    Attributes:
        name: Layer name (e.g., 'domain', 'application').
        paths: Path patterns that identify files in this layer.
        can_import: Modules this layer is allowed to import from.
        cannot_import: Modules this layer must not import from.
    """

    name: str
    paths: tuple[str, ...]
    can_import: tuple[str, ...]
    cannot_import: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Violation:
    """Architecture violation detected during validation.

    Attributes:
        severity: How critical the violation is.
        file_path: Absolute path to the file with the violation.
        line_number: Line number where the violation occurs.
        code: The actual import statement that violates the rule.
        issue: Human-readable description of the problem.
        fix: Suggested remediation action.
        impact: Consequences of not fixing this violation.
    """

    severity: Severity
    file_path: str
    line_number: int
    code: str
    issue: str
    fix: str
    impact: str


@dataclass(slots=True)
class ValidationResult:
    """Result of architecture validation.

    Attributes:
        pattern: The architecture pattern that was validated against.
        files_checked: Number of source files analyzed.
        violations: List of violations found during validation.
    """

    pattern: ArchitecturePattern
    files_checked: int
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True if no violations were found."""
        return len(self.violations) == 0

    @property
    def critical_count(self) -> int:
        """Count of CRITICAL severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Count of HIGH severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.HIGH)

    @property
    def medium_count(self) -> int:
        """Count of MEDIUM severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.MEDIUM)

    @property
    def low_count(self) -> int:
        """Count of LOW severity violations."""
        return sum(1 for v in self.violations if v.severity == Severity.LOW)


class ArchitectureDetector:
    """Detects architecture pattern from project documentation.

    Examines ARCHITECTURE.md and README.md to determine which
    architectural pattern the project follows.
    """

    def __init__(self, project_root: Path) -> None:
        """Initialize with the project root directory.

        Args:
            project_root: Path to the project root containing docs.
        """
        self.project_root = project_root

    def detect(self) -> ArchitecturePattern:
        """Detect architecture pattern from ARCHITECTURE.md or README.md.

        Returns:
            The detected architecture pattern, or UNKNOWN if not detected.
        """
        # Try to read ARCHITECTURE.md first
        arch_doc = self.project_root / "ARCHITECTURE.md"
        if arch_doc.exists():
            content = arch_doc.read_text(encoding="utf-8").lower()
            return self._detect_from_content(content)

        # Fallback to README.md
        readme = self.project_root / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8").lower()
            return self._detect_from_content(content)

        return ArchitecturePattern.UNKNOWN

    def _detect_from_content(self, content: str) -> ArchitecturePattern:
        """Detect pattern from documentation content.

        Args:
            content: Lowercase documentation text to analyze.

        Returns:
            The detected architecture pattern.
        """
        if "clean architecture" in content:
            return ArchitecturePattern.CLEAN

        if "hexagonal" in content or "ports and adapters" in content:
            return ArchitecturePattern.HEXAGONAL

        if "layered architecture" in content:
            return ArchitecturePattern.LAYERED

        if "mvc" in content or "model-view-controller" in content:
            return ArchitecturePattern.MVC

        return ArchitecturePattern.UNKNOWN


class LayerRuleEngine:
    """Defines and enforces layer rules for different architecture patterns.

    Contains predefined rule sets for Clean Architecture, Hexagonal,
    Layered, and MVC architectural patterns.
    """

    CLEAN_ARCHITECTURE_RULES: Final[tuple[LayerRule, ...]] = (
        LayerRule(
            name="domain",
            paths=("domain/", "core/"),
            can_import=("domain", "typing", "__future__", "dataclasses", "enum", "abc"),
            cannot_import=("application", "infrastructure", "interfaces", "adapters"),
        ),
        LayerRule(
            name="application",
            paths=("application/", "usecases/"),
            can_import=("domain", "application", "typing", "__future__", "dataclasses"),
            cannot_import=("interfaces", "api", "cli", "mcp"),
        ),
        LayerRule(
            name="infrastructure",
            paths=("infrastructure/", "adapters/secondary"),
            can_import=("domain", "application", "infrastructure"),
            cannot_import=("interfaces", "api", "cli", "mcp"),
        ),
        LayerRule(
            name="interface",
            paths=("interfaces/", "api/", "cli/", "mcp/", "adapters/primary"),
            can_import=("application", "domain", "interfaces"),
            cannot_import=(),
        ),
    )

    HEXAGONAL_RULES: Final[tuple[LayerRule, ...]] = (
        LayerRule(
            name="core",
            paths=("domain/", "core/"),
            can_import=("domain", "core", "typing", "__future__", "dataclasses"),
            cannot_import=("ports", "adapters"),
        ),
        LayerRule(
            name="ports",
            paths=("ports/",),
            can_import=("domain", "core", "ports", "typing"),
            cannot_import=("adapters",),
        ),
        LayerRule(
            name="adapters",
            paths=("adapters/",),
            can_import=("ports", "adapters"),
            cannot_import=("domain", "core"),  # Adapters use ports, not core directly
        ),
    )

    LAYERED_RULES: Final[tuple[LayerRule, ...]] = (
        LayerRule(
            name="presentation",
            paths=("presentation/", "ui/", "views/"),
            can_import=("business", "presentation"),
            cannot_import=("data", "database", "repositories"),
        ),
        LayerRule(
            name="business",
            paths=("business/", "services/"),
            can_import=("data", "business"),
            cannot_import=("presentation", "ui", "views"),
        ),
        LayerRule(
            name="data",
            paths=("data/", "repositories/"),
            can_import=("data",),
            cannot_import=("business", "presentation"),
        ),
    )

    MVC_RULES: Final[tuple[LayerRule, ...]] = (
        LayerRule(
            name="model",
            paths=("models/", "entities/"),
            can_import=("models", "typing"),
            cannot_import=("views", "controllers", "templates"),
        ),
        LayerRule(
            name="view",
            paths=("views/", "templates/"),
            can_import=("models", "views"),
            cannot_import=("controllers",),
        ),
        LayerRule(
            name="controller",
            paths=("controllers/",),
            can_import=("models", "views", "controllers"),
            cannot_import=(),
        ),
    )

    @classmethod
    def get_rules(cls, pattern: ArchitecturePattern) -> tuple[LayerRule, ...]:
        """Get layer rules for the specified architecture pattern.

        Args:
            pattern: The architecture pattern to get rules for.

        Returns:
            Tuple of LayerRule instances for the pattern, or empty tuple
            if pattern is UNKNOWN.
        """
        rules_map: dict[ArchitecturePattern, tuple[LayerRule, ...]] = {
            ArchitecturePattern.CLEAN: cls.CLEAN_ARCHITECTURE_RULES,
            ArchitecturePattern.HEXAGONAL: cls.HEXAGONAL_RULES,
            ArchitecturePattern.LAYERED: cls.LAYERED_RULES,
            ArchitecturePattern.MVC: cls.MVC_RULES,
        }
        return rules_map.get(pattern, ())


class FileReadError(Exception):
    """Raised when a source file cannot be read."""

    def __init__(self, file_path: Path, cause: Exception) -> None:
        """Initialize with file path and underlying cause.

        Args:
            file_path: Path to the file that couldn't be read.
            cause: The original exception that occurred.
        """
        self.file_path = file_path
        self.cause = cause
        super().__init__(f"Failed to read {file_path}: {cause}")


class ImportAnalyzer:
    """Analyzes imports in Python source files.

    Uses regex patterns to extract import statements and their
    line numbers from source code.
    """

    IMPORT_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
        re.compile(r"^from\s+([a-zA-Z0-9_\.]+)\s+import"),  # from X import Y
        re.compile(r"^import\s+([a-zA-Z0-9_\.]+)"),  # import X
    )

    def extract_imports(
        self, file_path: Path
    ) -> dict[int, list[tuple[str, str]]]:
        """Extract imports from a Python source file.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            Dict mapping line number to list of (module_name, full_line) tuples.

        Raises:
            FileReadError: If the file cannot be read.
        """
        imports: dict[int, list[tuple[str, str]]] = {}

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise FileReadError(file_path, e) from e

        for line_num, line in enumerate(content.splitlines(), start=1):
            stripped_line = line.strip()
            for pattern in self.IMPORT_PATTERNS:
                match = pattern.match(stripped_line)
                if match:
                    module = match.group(1)
                    if line_num not in imports:
                        imports[line_num] = []
                    imports[line_num].append((module, stripped_line))
                    break

        return imports


class LayerIdentifier:
    """Identifies which architectural layer a file belongs to.

    Matches file paths against layer path patterns to determine
    which layer the file is part of.
    """

    def __init__(
        self, rules: tuple[LayerRule, ...], project_root: Path
    ) -> None:
        """Initialize with layer rules and project root.

        Args:
            rules: Tuple of layer rules to match against.
            project_root: Root directory of the project.
        """
        self.rules = rules
        self.project_root = project_root

    def identify_layer(self, file_path: Path) -> LayerRule | None:
        """Identify which layer a file belongs to.

        Args:
            file_path: Absolute path to the file.

        Returns:
            The LayerRule for the matching layer, or None if not in any layer.
        """
        try:
            relative_path = str(file_path.relative_to(self.project_root))
        except ValueError:
            # File is not under project root
            return None

        for rule in self.rules:
            for layer_path in rule.paths:
                if layer_path in relative_path:
                    return rule

        return None


class ViolationDetector:
    """Detects architecture violations in source files.

    Analyzes imports in each file and checks them against
    layer rules to find violations.
    """

    def __init__(
        self, rules: tuple[LayerRule, ...], project_root: Path
    ) -> None:
        """Initialize with layer rules and project root.

        Args:
            rules: Tuple of layer rules to enforce.
            project_root: Root directory of the project.
        """
        self.layer_identifier = LayerIdentifier(rules, project_root)
        self.import_analyzer = ImportAnalyzer()
        self._unreadable_files: list[Path] = []

    @property
    def unreadable_files(self) -> list[Path]:
        """Files that could not be read during analysis."""
        return self._unreadable_files.copy()

    def detect_violations(self, file_path: Path) -> list[Violation]:
        """Detect violations in a single file.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            List of violations found in the file.
        """
        violations: list[Violation] = []

        # Identify layer
        layer = self.layer_identifier.identify_layer(file_path)
        if not layer:
            return violations  # File not in any layer

        # Extract imports
        try:
            imports = self.import_analyzer.extract_imports(file_path)
        except FileReadError:
            self._unreadable_files.append(file_path)
            return violations

        # Check each import against layer rules
        for line_num, import_list in imports.items():
            for module, code in import_list:
                violation = self._check_import(
                    file_path, line_num, code, module, layer
                )
                if violation:
                    violations.append(violation)

        return violations

    def _check_import(
        self,
        file_path: Path,
        line_num: int,
        code: str,
        module: str,
        layer: LayerRule,
    ) -> Violation | None:
        """Check if an import violates layer rules.

        Args:
            file_path: Path to the file containing the import.
            line_num: Line number of the import statement.
            code: The full import statement.
            module: The module being imported.
            layer: The layer rule for the file's layer.

        Returns:
            A Violation if the import is forbidden, None otherwise.
        """
        # Skip allowed imports
        if any(allowed in module for allowed in layer.can_import):
            return None

        # Check forbidden imports
        for forbidden in layer.cannot_import:
            if forbidden in module:
                return self._create_violation(
                    file_path, line_num, code, layer.name, forbidden
                )

        return None

    def _create_violation(
        self,
        file_path: Path,
        line_num: int,
        code: str,
        layer_name: str,
        forbidden_layer: str,
    ) -> Violation:
        """Create a violation object for a forbidden import.

        Args:
            file_path: Path to the file with the violation.
            line_num: Line number of the violation.
            code: The import statement that violates the rule.
            layer_name: Name of the layer containing the file.
            forbidden_layer: Name of the layer that was imported.

        Returns:
            A Violation object describing the issue.
        """
        return Violation(
            severity=Severity.CRITICAL if layer_name == "domain" else Severity.HIGH,
            file_path=str(file_path),
            line_number=line_num,
            code=code,
            issue=f"{layer_name.title()} layer importing from {forbidden_layer} layer",
            fix=f"Remove {forbidden_layer} import. Use dependency inversion instead.",
            impact=f"Breaks {layer_name} layer isolation, creates tight coupling",
        )


class ArchitectureValidator:
    """Main validator orchestrator.

    Coordinates architecture detection, file discovery, and violation
    detection to validate a project's architecture.
    """

    # File patterns to check for imports
    SOURCE_PATTERNS: Final[tuple[str, ...]] = ("**/*.py", "**/*.js", "**/*.ts")

    # Directories to exclude from scanning
    EXCLUDE_DIRS: Final[frozenset[str]] = frozenset(
        {".venv", "venv", "node_modules", "__pycache__", ".git", "dist", "build"}
    )

    def __init__(
        self, project_root: Path, pattern: ArchitecturePattern | None = None
    ) -> None:
        """Initialize the validator.

        Args:
            project_root: Root directory of the project to validate.
            pattern: Optional architecture pattern to use. If not provided,
                the pattern will be auto-detected from documentation.
        """
        self.project_root = project_root

        # Detect or use provided pattern
        if pattern is not None:
            self.pattern = pattern
        else:
            detector = ArchitectureDetector(project_root)
            self.pattern = detector.detect()

        # Get rules for pattern
        self.rules = LayerRuleEngine.get_rules(self.pattern)
        self.detector = ViolationDetector(self.rules, project_root)

    def validate(self, files: list[Path] | None = None) -> ValidationResult:
        """Validate architecture of the project.

        Args:
            files: Optional list of specific files to validate.
                If not provided, all source files will be validated.

        Returns:
            ValidationResult containing pattern, file count, and violations.
        """
        # Find files to validate
        files_to_check = files if files is not None else self._find_source_files()

        result = ValidationResult(
            pattern=self.pattern, files_checked=len(files_to_check)
        )

        # Check each file
        for file_path in files_to_check:
            violations = self.detector.detect_violations(file_path)
            result.violations.extend(violations)

        return result

    def _find_source_files(self) -> list[Path]:
        """Find all source files to validate.

        Returns:
            List of paths to source files, excluding vendor directories.
        """
        files: list[Path] = []

        for pattern in self.SOURCE_PATTERNS:
            for file_path in self.project_root.glob(pattern):
                # Skip if any excluded directory is in the path
                if any(
                    excluded_dir in file_path.parts
                    for excluded_dir in self.EXCLUDE_DIRS
                ):
                    continue
                if file_path.is_file():
                    files.append(file_path)

        return files


class ResultFormatter:
    """Formats validation results for human-readable output."""

    def format(self, result: ValidationResult, *, verbose: bool = True) -> str:
        """Format validation result as a string.

        Args:
            result: The validation result to format.
            verbose: If True, include detailed violation information.

        Returns:
            Formatted string representation of the result.
        """
        lines: list[str] = []

        if result.passed:
            lines.extend(
                [
                    "[PASS] Architecture Validation: PASSED",
                    "",
                    f"Pattern: {result.pattern.value}",
                    f"Files checked: {result.files_checked}",
                    "Violations: 0",
                    "",
                    "All layer boundaries respected.",
                ]
            )
        else:
            lines.extend(
                [
                    "[FAIL] Architecture Validation: FAILED",
                    "",
                    f"Pattern: {result.pattern.value}",
                    f"Files checked: {result.files_checked}",
                    f"Violations: {len(result.violations)} "
                    f"({result.critical_count} critical, {result.high_count} high, "
                    f"{result.medium_count} medium, {result.low_count} low)",
                    "",
                ]
            )

            if verbose:
                lines.extend(["Violations:", ""])
                self._format_violations_by_severity(result.violations, lines)

        return "\n".join(lines)

    def _format_violations_by_severity(
        self, violations: list[Violation], lines: list[str]
    ) -> None:
        """Format violations grouped by severity.

        Args:
            violations: List of violations to format.
            lines: List to append formatted lines to (mutated in place).
        """
        for severity in (
            Severity.CRITICAL,
            Severity.HIGH,
            Severity.MEDIUM,
            Severity.LOW,
        ):
            severity_violations = [
                v for v in violations if v.severity == severity
            ]
            if not severity_violations:
                continue

            lines.extend([f"{severity.value} Violations:", ""])

            for i, violation in enumerate(severity_violations, 1):
                lines.extend(
                    [
                        f"{i}. {violation.issue}",
                        f"   File: {violation.file_path}:{violation.line_number}",
                        f"   Code: {violation.code}",
                        f"   Fix: {violation.fix}",
                        f"   Impact: {violation.impact}",
                        "",
                    ]
                )


def main() -> int:
    """Main entry point for architecture validation CLI.

    Returns:
        Exit code: 0 for success, 1 for violations, 2 for configuration error.
    """
    parser = argparse.ArgumentParser(
        description="Validate architecture patterns and layer boundaries"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--architecture",
        type=str,
        choices=["clean", "hexagonal", "layered", "mvc"],
        help="Architecture pattern (auto-detected if not specified)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        type=Path,
        help="Specific files to validate (default: all source files)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any violation (default: fail on critical/high only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Show detailed violation information",
    )

    args = parser.parse_args()

    # Validate project root exists
    project_root: Path = args.project_root.resolve()
    if not project_root.is_dir():
        print(f"Error: Project root does not exist: {project_root}", file=sys.stderr)
        return 2

    # Convert architecture string to enum
    pattern: ArchitecturePattern | None = None
    if args.architecture:
        pattern = ArchitecturePattern(args.architecture)

    # Convert relative paths to absolute paths for --files argument
    files: list[Path] | None = None
    if args.files:
        files = [f.resolve() for f in args.files]
        # Validate all files exist
        for file_path in files:
            if not file_path.is_file():
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                return 2

    # Validate
    validator = ArchitectureValidator(project_root, pattern)
    result = validator.validate(files)

    # Format and print results
    formatter = ResultFormatter()
    output = formatter.format(result, verbose=args.verbose)
    print(output)

    # Determine exit code
    if result.passed:
        return 0

    if args.strict:
        return 1  # Any violations

    # Non-strict: fail only on critical/high
    if result.critical_count > 0 or result.high_count > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
