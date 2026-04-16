# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Preflight check for hardcode audit tools.

Usage:
    uv run --python 3.13 --script preflight.py -- <path> [--output {json,text}]

Verifies all audit tools are installed and properly configured.
Detects silent misconfigurations like globally suppressed Ruff PLR2004.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolCheck:
    """Result of checking a single tool."""

    name: str
    installed: bool
    version: str | None = None
    issues: list[str] = field(default_factory=list)
    install_cmd: str = ""

    def to_dict(self) -> dict:
        d = {"name": self.name, "installed": self.installed, "version": self.version, "issues": self.issues}
        if not self.installed:
            d["install_cmd"] = self.install_cmd
        return d


def _get_version(cmd: list[str]) -> str | None:
    """Run a version command and extract the version string."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Take first line, strip common prefixes
            line = result.stdout.strip().splitlines()[0]
            # Extract version-like substring
            for part in line.split():
                if part[0].isdigit():
                    return part
            return line
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError):
        pass
    return None


def _find_ruff_config(target: Path) -> Path | None:
    """Walk up from target to find ruff config file."""
    search = target.resolve()
    if search.is_file():
        search = search.parent

    while True:
        for name in ("ruff.toml", ".ruff.toml", "pyproject.toml"):
            candidate = search / name
            if candidate.is_file():
                return candidate
        parent = search.parent
        if parent == search:
            break
        search = parent
    return None


def _check_plr2004_suppressed(config_path: Path) -> list[str]:
    """Check if PLR2004 is suppressed in a ruff config file."""
    issues = []
    try:
        data = tomllib.loads(config_path.read_text())
    except Exception:
        return issues

    # pyproject.toml nests under [tool.ruff]
    ruff_cfg = data
    if config_path.name == "pyproject.toml":
        ruff_cfg = data.get("tool", {}).get("ruff", {})

    lint = ruff_cfg.get("lint", {})

    # Check global ignore list
    ignore = lint.get("ignore", [])
    for rule in ignore:
        if rule in ("PLR2004", "PLR"):
            issues.append(f"PLR2004 globally suppressed in {config_path.name} [tool.ruff.lint.ignore]")
            break

    # Check per-file-ignores
    per_file = lint.get("per-file-ignores", {})
    for pattern, rules in per_file.items():
        if pattern in ("*", "*.py", "**/*.py"):
            for rule in rules:
                if rule in ("PLR2004", "PLR"):
                    issues.append(f"PLR2004 suppressed for '{pattern}' in {config_path.name} [tool.ruff.lint.per-file-ignores]")
                    break

    # Check select — if select is specified but doesn't include PLR/PLR2004
    select = lint.get("select", None)
    if select is not None and "ALL" not in select:
        has_plr = any(r in select for r in ("PLR", "PLR2004", "PL"))
        if not has_plr:
            issues.append(f"PLR2004 not in [tool.ruff.lint.select] in {config_path.name} — rule won't run")

    return issues


def check_ruff(target: Path) -> ToolCheck:
    """Check ruff installation and PLR2004 configuration."""
    check = ToolCheck(name="ruff", installed=False, install_cmd="uv tool install ruff")
    path = shutil.which("ruff")
    if not path:
        return check

    check.installed = True
    check.version = _get_version(["ruff", "--version"])

    # Check PLR2004 suppression in project config
    config = _find_ruff_config(target)
    if config:
        check.issues.extend(_check_plr2004_suppressed(config))

    return check


def check_semgrep() -> ToolCheck:
    """Check semgrep installation."""
    check = ToolCheck(name="semgrep", installed=False, install_cmd="brew install semgrep")
    if shutil.which("semgrep"):
        check.installed = True
        check.version = _get_version(["semgrep", "--version"])
    return check


def check_jscpd() -> ToolCheck:
    """Check jscpd availability via npx."""
    check = ToolCheck(name="jscpd", installed=False, install_cmd="npm install -g jscpd")
    if shutil.which("npx"):
        check.installed = True
        check.version = "via npx"
    return check


def check_gitleaks() -> ToolCheck:
    """Check gitleaks installation."""
    check = ToolCheck(name="gitleaks", installed=False, install_cmd="mise use --global gitleaks")
    if shutil.which("gitleaks"):
        check.installed = True
        check.version = _get_version(["gitleaks", "version"])
    return check


def check_ast_grep() -> ToolCheck:
    """Check ast-grep installation (binary name: sg or ast-grep)."""
    check = ToolCheck(name="ast-grep", installed=False, install_cmd="cargo install ast-grep")
    for binary in ("sg", "ast-grep"):
        if shutil.which(binary):
            check.installed = True
            check.version = _get_version([binary, "--version"])
            break
    return check


def check_bandit() -> ToolCheck:
    """Check bandit installation."""
    check = ToolCheck(name="bandit", installed=False, install_cmd="uv tool install bandit")
    if shutil.which("bandit"):
        check.installed = True
        check.version = _get_version(["bandit", "--version"])
    return check


def check_trufflehog() -> ToolCheck:
    """Check trufflehog installation."""
    check = ToolCheck(name="trufflehog", installed=False, install_cmd="brew install trufflehog")
    if shutil.which("trufflehog"):
        check.installed = True
        check.version = _get_version(["trufflehog", "--version"])
    return check


def check_whispers() -> ToolCheck:
    """Check whispers installation."""
    check = ToolCheck(name="whispers", installed=False, install_cmd="uv tool install whispers")
    if shutil.which("whispers"):
        check.installed = True
        check.version = _get_version(["whispers", "--version"])
    return check


def run_preflight(target: Path, output_format: str = "text") -> int:
    """Run all preflight checks and report results."""
    checks = [
        check_ruff(target),
        check_semgrep(),
        check_jscpd(),
        check_gitleaks(),
        check_ast_grep(),
        check_bandit(),
        check_trufflehog(),
        check_whispers(),
    ]

    has_missing = any(not c.installed for c in checks)
    has_issues = any(c.issues for c in checks)

    if has_missing:
        status = "fail"
    elif has_issues:
        status = "warn"
    else:
        status = "pass"

    if output_format == "json":
        output = {
            "status": status,
            "tools": [c.to_dict() for c in checks],
        }
        print(json.dumps(output, indent=2))
    else:
        print("=== Hardcode Audit Preflight ===\n")
        for c in checks:
            if c.installed:
                icon = "✓" if not c.issues else "⚠"
                ver = f" ({c.version})" if c.version else ""
                print(f"  {icon} {c.name}{ver}")
                for issue in c.issues:
                    print(f"    ⚠ {issue}")
            else:
                print(f"  ✗ {c.name} — not found")
                print(f"    Install: {c.install_cmd}")

        print()
        if status == "pass":
            print("Status: PASS — all tools available and configured")
        elif status == "warn":
            print("Status: WARN — tools available but configuration issues detected")
        else:
            print("Status: FAIL — missing required tools")

    return 0 if status in ("pass", "warn") else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight check for hardcode audit tools")
    parser.add_argument("path", type=Path, help="Target path (used to find ruff config)")
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    # uv run --script <file> -- <args> passes literal '--' to the script
    argv = [a for a in sys.argv[1:] if a != "--"]
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    return run_preflight(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
