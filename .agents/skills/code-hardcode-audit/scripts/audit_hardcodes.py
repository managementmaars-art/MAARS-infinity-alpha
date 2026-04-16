# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Orchestrator for code hardcode audit combining 9 tools.

Usage:
    uv run --script audit_hardcodes.py -- <path> [options]

Options:
    --output {json,text,both}  Output format (default: both)
    --tools {all,ruff,semgrep,jscpd,gitleaks,ast-grep,env-coverage}  Tools to run
    --severity {all,high,medium,low}  Filter by severity (default: all)
    --exclude PATTERN  Glob pattern to exclude (repeatable)
    --no-parallel  Disable parallel execution
    --skip-preflight  Skip tool availability check
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ADR: 2025-12-08-mise-env-centralized-config
# Configuration via environment variables with defaults for backward compatibility
AUDIT_PARALLEL_WORKERS = int(os.environ.get("AUDIT_PARALLEL_WORKERS", "4"))
AUDIT_JSCPD_TIMEOUT = int(os.environ.get("AUDIT_JSCPD_TIMEOUT", "300"))
AUDIT_GITLEAKS_TIMEOUT = int(os.environ.get("AUDIT_GITLEAKS_TIMEOUT", "120"))
AUDIT_ASTGREP_TIMEOUT = int(os.environ.get("AUDIT_ASTGREP_TIMEOUT", "60"))
AUDIT_BANDIT_TIMEOUT = int(os.environ.get("AUDIT_BANDIT_TIMEOUT", "120"))
AUDIT_TRUFFLEHOG_TIMEOUT = int(os.environ.get("AUDIT_TRUFFLEHOG_TIMEOUT", "300"))
AUDIT_WHISPERS_TIMEOUT = int(os.environ.get("AUDIT_WHISPERS_TIMEOUT", "120"))


@dataclass
class Finding:
    """A single finding from any tool."""

    id: str
    tool: str
    rule: str
    file: str
    line: int
    column: int = 0
    end_line: int | None = None
    message: str = ""
    severity: str = "medium"
    suggested_fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.tool,
            "rule": self.rule,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "message": self.message,
            "severity": self.severity,
            "suggested_fix": self.suggested_fix,
        }

    def to_text(self) -> str:
        loc = f"{self.file}:{self.line}"
        if self.column:
            loc += f":{self.column}"
        return f"{loc}: {self.rule} {self.message} [{self.tool}]"


@dataclass
class AuditResult:
    """Aggregated results from all tools."""

    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def summary(self) -> dict[str, Any]:
        by_tool: dict[str, int] = {}
        by_severity: dict[str, int] = {}

        for f in self.findings:
            by_tool[f.tool] = by_tool.get(f.tool, 0) + 1
            by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

        return {
            "total_findings": len(self.findings),
            "by_tool": by_tool,
            "by_severity": by_severity,
        }

    def to_json(self) -> str:
        return json.dumps(
            {
                "summary": self.summary(),
                "findings": [f.to_dict() for f in self.findings],
                "errors": self.errors,
            },
            indent=2,
        )

    def to_text(self) -> str:
        lines = [f.to_text() for f in self.findings]
        summary = self.summary()
        tool_counts = ", ".join(f"{k}: {v}" for k, v in summary["by_tool"].items())
        lines.append("")
        lines.append(f"Summary: {summary['total_findings']} findings ({tool_counts})")
        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
            for e in self.errors:
                lines.append(f"  - {e}")
        return "\n".join(lines)


def run_ruff(target: Path, excludes: list[str]) -> list[Finding]:
    """Run Ruff PLR2004 check and return findings."""
    cmd = ["ruff", "check", "--select", "PLR2004", "--output-format", "json", str(target)]
    for pattern in excludes:
        cmd.extend(["--exclude", pattern])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Ruff returns exit code 1 when findings exist
        if result.stdout:
            data = json.loads(result.stdout)
            findings = []
            for i, item in enumerate(data):
                findings.append(
                    Finding(
                        id=f"RUFF-{i + 1:03d}",
                        tool="ruff",
                        rule=item.get("code", "PLR2004"),
                        file=item.get("filename", ""),
                        line=item.get("location", {}).get("row", 0),
                        column=item.get("location", {}).get("column", 0),
                        message=item.get("message", ""),
                        severity="medium",
                        suggested_fix="Extract to named constant",
                    )
                )
            return findings
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ruff error: {e}", file=sys.stderr)
    return []


def _extract_rule_id(check_id: str) -> str:
    """Extract clean rule ID from Semgrep's path-based check_id.

    Semgrep generates check_ids like:
    'Users.terryli..claude.skills.code-hardcode-audit.assets.hardcoded-timeframe'

    This extracts just 'hardcoded-timeframe'.
    """
    # Split by dots and find the actual rule name (after 'assets' or last segment)
    parts = check_id.split(".")
    # Look for 'assets' marker, take everything after it
    if "assets" in parts:
        idx = parts.index("assets")
        return ".".join(parts[idx + 1 :]) if idx + 1 < len(parts) else check_id
    # Fallback: return last segment
    return parts[-1] if parts else check_id


def run_semgrep(target: Path, excludes: list[str]) -> list[Finding]:
    """Run Semgrep with custom rules and return findings."""
    rules_path = Path(__file__).parent.parent / "assets" / "semgrep-hardcode-rules.yaml"

    if not rules_path.exists():
        print(f"semgrep rules not found: {rules_path}", file=sys.stderr)
        return []

    cmd = ["semgrep", "--config", str(rules_path), "--json", str(target)]
    for pattern in excludes:
        cmd.extend(["--exclude", pattern])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            data = json.loads(result.stdout)
            findings = []
            for i, item in enumerate(data.get("results", [])):
                severity_map = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}
                raw_check_id = item.get("check_id", "")
                findings.append(
                    Finding(
                        id=f"SGRP-{i + 1:03d}",
                        tool="semgrep",
                        rule=_extract_rule_id(raw_check_id),
                        file=item.get("path", ""),
                        line=item.get("start", {}).get("line", 0),
                        column=item.get("start", {}).get("col", 0),
                        end_line=item.get("end", {}).get("line"),
                        message=item.get("extra", {}).get("message", ""),
                        severity=severity_map.get(
                            item.get("extra", {}).get("severity", "WARNING"), "medium"
                        ),
                        suggested_fix=item.get("extra", {})
                        .get("metadata", {})
                        .get("suggested_fix", ""),
                    )
                )
            return findings
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"semgrep error: {e}", file=sys.stderr)
    return []


def run_jscpd(target: Path, excludes: list[str]) -> list[Finding]:
    """Run jscpd via npx and return findings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        cmd = ["npx", "jscpd", "--reporters", "json", "--output", str(output_dir), str(target)]
        for pattern in excludes:
            cmd.extend(["--ignore", pattern])

        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=AUDIT_JSCPD_TIMEOUT)
            report_path = output_dir / "jscpd-report.json"
            if report_path.exists():
                data = json.loads(report_path.read_text())
                findings = []
                for i, dup in enumerate(data.get("duplicates", [])):
                    first = dup.get("firstFile", {})
                    second = dup.get("secondFile", {})
                    findings.append(
                        Finding(
                            id=f"JSCPD-{i + 1:03d}",
                            tool="jscpd",
                            rule="duplicate-code",
                            file=first.get("name", ""),
                            line=first.get("startLoc", {}).get("line", 0),
                            end_line=first.get("endLoc", {}).get("line"),
                            message=f"Clone detected with {second.get('name', '')} "
                            f"({dup.get('lines', 0)} lines, "
                            f"{dup.get('fragment', '')})",
                            severity="low",
                            suggested_fix="Extract to shared function or module",
                        )
                    )
                return findings
        except (json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"jscpd error: {e}", file=sys.stderr)
    return []


def run_gitleaks(target: Path, excludes: list[str]) -> list[Finding]:
    """Run gitleaks for secret detection and return findings.

    Uses modern 'dir' command for directory scanning (v8.19.0+).
    Exit codes: 0 = clean, 1 = secrets found (expected), 2+ = error.
    """
    cmd = [
        "gitleaks",
        "dir",
        str(target),
        "--report-format",
        "json",
        "--report-path",
        "/dev/stdout",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=AUDIT_GITLEAKS_TIMEOUT)

        # Exit code 1 = secrets found (expected, not an error)
        if result.returncode in (0, 1) and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                findings = []
                for i, item in enumerate(data):
                    findings.append(
                        Finding(
                            id=f"GITLEAKS-{i + 1:03d}",
                            tool="gitleaks",
                            rule=item.get("RuleID", "secret"),
                            file=item.get("File", ""),
                            line=item.get("StartLine", 0),
                            end_line=item.get("EndLine"),
                            message=f"Secret detected: {item.get('Match', '')[:30]}...",
                            severity="high",  # Secrets are always high severity
                            suggested_fix="Remove secret and rotate credentials",
                        )
                    )
                return findings
            except json.JSONDecodeError:
                pass
        return []
    except FileNotFoundError:
        print("gitleaks not found. Install with: mise use --global gitleaks", file=sys.stderr)
        return []
    except subprocess.TimeoutExpired:
        print(f"gitleaks timed out after {AUDIT_GITLEAKS_TIMEOUT} seconds", file=sys.stderr)
        return []


def run_ast_grep(target: Path, excludes: list[str]) -> list[Finding]:
    """Run ast-grep with hardcode detection rules and return findings."""
    import shutil

    rules_dir = Path(__file__).parent.parent / "assets" / "ast-grep-hardcode"
    if not rules_dir.exists():
        print(f"ast-grep rules not found: {rules_dir}", file=sys.stderr)
        return []

    sg = None
    for name in ("sg", "ast-grep"):
        if shutil.which(name):
            sg = name
            break
    if not sg:
        print("ast-grep not found. Install with: cargo install ast-grep", file=sys.stderr)
        return []

    cmd = [sg, "scan", str(target.resolve()), "--json=stream"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=AUDIT_ASTGREP_TIMEOUT, cwd=str(rules_dir),
        )
        findings = []
        severity_map = {"error": "high", "warning": "medium", "hint": "low", "info": "low"}
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                findings.append(Finding(
                    id=f"ASTGREP-{len(findings) + 1:03d}",
                    tool="ast-grep",
                    rule=item.get("ruleId", "unknown"),
                    file=item.get("file", ""),
                    line=item.get("range", {}).get("start", {}).get("line", 0),
                    column=item.get("range", {}).get("start", {}).get("column", 0),
                    end_line=item.get("range", {}).get("end", {}).get("line"),
                    message=item.get("message", ""),
                    severity=severity_map.get(item.get("severity", "warning"), "medium"),
                    suggested_fix=item.get("note", ""),
                ))
        return findings
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"ast-grep error: {e}", file=sys.stderr)
        return []


def run_env_coverage(target: Path, excludes: list[str]) -> list[Finding]:
    """Run env-coverage audit via subprocess and return findings."""
    script = Path(__file__).parent / "audit_env_coverage.py"
    if not script.exists():
        print(f"env-coverage script not found: {script}", file=sys.stderr)
        return []

    cmd = ["uv", "run", "--python", "3.13", "--script", str(script), "--", str(target), "--output", "json"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.stdout.strip():
            data = json.loads(result.stdout)
            findings = []
            for item in data.get("findings", []):
                findings.append(Finding(
                    id=item.get("id", f"ENVCOV-{len(findings) + 1:03d}"),
                    tool="env-coverage",
                    rule=item.get("rule", ""),
                    file=item.get("file", ""),
                    line=item.get("line", 0),
                    column=item.get("column", 0),
                    end_line=item.get("end_line"),
                    message=item.get("message", ""),
                    severity=item.get("severity", "medium"),
                    suggested_fix=item.get("suggested_fix", ""),
                ))
            return findings
    except (json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"env-coverage error: {e}", file=sys.stderr)
    return []


def _gitignore_excludes(target: Path, regex_safe: bool = False) -> list[str]:
    """Read .gitignore from target and return directory names to exclude.

    Args:
        regex_safe: If True, skip glob patterns with *, ?, [, { (for trufflehog regex mode).
    """
    excludes = []
    gitignore = target / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            clean = line.rstrip("/")
            if regex_safe and any(c in clean for c in ("*", "?", "[", "{")):
                continue
            if clean:
                excludes.append(clean)
    # Always exclude .venv even if not in .gitignore
    if ".venv" not in excludes:
        excludes.append(".venv")
    return excludes


def run_bandit(target: Path, excludes: list[str]) -> list[Finding]:
    """Run Bandit B105/B106/B107 for hardcoded credential detection."""
    gi_excludes = _gitignore_excludes(target)
    bandit_excludes = [str(target / e) for e in gi_excludes]
    cmd = [
        "bandit", "-r", str(target),
        "-t", "B105,B106,B107",
        "-f", "json",
        "--exclude", ",".join(bandit_excludes),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=AUDIT_BANDIT_TIMEOUT)
        raw = result.stdout or ""
        brace_index = raw.find("{")
        if brace_index == -1:
            return []

        data = json.loads(raw[brace_index:])
        findings = []
        for i, item in enumerate(data.get("results", [])):
            findings.append(Finding(
                id=f"BANDIT-{i + 1:03d}",
                tool="bandit",
                rule=item.get("test_id", "B105"),
                file=item.get("filename", ""),
                line=item.get("line_number", 0),
                column=item.get("col_offset", 0),
                message=item.get("issue_text", ""),
                severity="high",  # Credential findings are always high
                suggested_fix="Move to environment variable or secret manager",
            ))
        return findings
    except (json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"bandit error: {e}", file=sys.stderr)
        return []


def run_trufflehog(target: Path, excludes: list[str]) -> list[Finding]:
    """Run TruffleHog for entropy-based secret detection with .gitignore awareness."""
    gi_excludes = _gitignore_excludes(target, regex_safe=True)
    gi_excludes.append(".git")

    # trufflehog --exclude-paths expects a file with patterns
    exclude_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="trufflehog-exclude-"
    )
    try:
        exclude_file.write("\n".join(gi_excludes) + "\n")
        exclude_file.close()

        cmd = [
            "trufflehog", "filesystem", str(target),
            "--json", "--no-update",
            "--exclude-paths", exclude_file.name,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=AUDIT_TRUFFLEHOG_TIMEOUT)

        findings = []
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                fs = obj.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {})
                verified = obj.get("Verified", False)
                findings.append(Finding(
                    id=f"TRUFFLEHOG-{len(findings) + 1:03d}",
                    tool="trufflehog",
                    rule=obj.get("DetectorName", "unknown"),
                    file=fs.get("file", ""),
                    line=fs.get("line", 0),
                    message=f"{obj.get('DetectorName', '')} ({'verified' if verified else 'unverified'}): {obj.get('Raw', '')[:30]}...",
                    severity="high" if verified else "medium",
                    suggested_fix="Remove secret and rotate credentials",
                ))
        return findings
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"trufflehog error: {e}", file=sys.stderr)
        return []
    finally:
        Path(exclude_file.name).unlink(missing_ok=True)


def run_whispers(target: Path, excludes: list[str]) -> list[Finding]:
    """Run Whispers for config-file secret detection with .gitignore awareness."""
    gi_excludes = _gitignore_excludes(target)
    gi_excludes.append(".git")

    # Build whispers config YAML
    config_lines = ["exclude:", "  files:"]
    for p in gi_excludes:
        config_lines.append(f'    - "{p}/**"')
    config_yaml = "\n".join(config_lines) + "\n"

    cfg_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, prefix="whispers-config-"
    )
    try:
        cfg_file.write(config_yaml)
        cfg_file.close()

        cmd = ["whispers", str(target), "-j", "-c", cfg_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=AUDIT_WHISPERS_TIMEOUT)

        findings = []
        if result.stdout and result.stdout.strip():
            data = json.loads(result.stdout)
            for i, item in enumerate(data):
                findings.append(Finding(
                    id=f"WHISPERS-{i + 1:03d}",
                    tool="whispers",
                    rule=item.get("rule_id", "unknown"),
                    file=item.get("file", ""),
                    line=item.get("line", 0),
                    message=f"{item.get('key', '')}: {item.get('message', '')}",
                    severity={"Critical": "high", "High": "high", "Medium": "medium", "Low": "low"}.get(
                        item.get("severity", "Low"), "low"
                    ),
                    suggested_fix="Move to environment variable or secret manager",
                ))
        return findings
    except (json.JSONDecodeError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"whispers error: {e}", file=sys.stderr)
        return []
    finally:
        Path(cfg_file.name).unlink(missing_ok=True)


def run_preflight(target: Path) -> bool:
    """Run preflight check and return True if all tools available."""
    script = Path(__file__).parent / "preflight.py"
    if not script.exists():
        return True  # Skip if preflight script not available

    cmd = ["uv", "run", "--python", "3.13", "--script", str(script), "--", str(target), "--output", "text"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return True  # Don't block on preflight failures


def run_audit(
    target: Path,
    tools: list[str],
    excludes: list[str],
    parallel: bool = True,
) -> AuditResult:
    """Run selected tools and aggregate results."""
    result = AuditResult()

    tool_funcs = {
        "ruff": run_ruff,
        "semgrep": run_semgrep,
        "jscpd": run_jscpd,
        "gitleaks": run_gitleaks,
        "ast-grep": run_ast_grep,
        "env-coverage": run_env_coverage,
        "bandit": run_bandit,
        "trufflehog": run_trufflehog,
        "whispers": run_whispers,
    }

    selected = tools if tools != ["all"] else list(tool_funcs.keys())

    if parallel:
        with ThreadPoolExecutor(max_workers=AUDIT_PARALLEL_WORKERS) as executor:
            futures = {
                executor.submit(tool_funcs[name], target, excludes): name
                for name in selected
                if name in tool_funcs
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    for finding in future.result():
                        result.add_finding(finding)
                except Exception as e:
                    result.add_error(f"{name}: {e}")
    else:
        for name in selected:
            if name in tool_funcs:
                try:
                    for finding in tool_funcs[name](target, excludes):
                        result.add_finding(finding)
                except Exception as e:
                    result.add_error(f"{name}: {e}")

    # Sort by file, then line
    result.findings.sort(key=lambda f: (f.file, f.line))
    return result


def filter_by_severity(result: AuditResult, severity: str) -> AuditResult:
    """Filter findings by severity level."""
    if severity == "all":
        return result

    severity_order = {"high": 0, "medium": 1, "low": 2}
    threshold = severity_order.get(severity, 2)

    filtered = AuditResult(errors=result.errors)
    for f in result.findings:
        if severity_order.get(f.severity, 2) <= threshold:
            filtered.add_finding(f)
    return filtered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit code for hardcoded values using 9 detection tools"
    )
    parser.add_argument("path", type=Path, help="Path to audit")
    parser.add_argument(
        "--output",
        choices=["json", "text", "both"],
        default="both",
        help="Output format",
    )
    parser.add_argument(
        "--tools",
        choices=["all", "ruff", "semgrep", "jscpd", "gitleaks", "ast-grep", "env-coverage",
                 "bandit", "trufflehog", "whispers"],
        nargs="+",
        default=["all"],
        help="Tools to run",
    )
    parser.add_argument(
        "--severity",
        choices=["all", "high", "medium", "low"],
        default="all",
        help="Filter by minimum severity",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Glob pattern to exclude",
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel execution",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip tool availability preflight check",
    )

    # uv run --script <file> -- <args> passes literal '--' to the script
    argv = [a for a in sys.argv[1:] if a != "--"]
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    if not args.skip_preflight:
        run_preflight(args.path)
        print()  # Separator between preflight and audit output

    result = run_audit(
        target=args.path,
        tools=args.tools,
        excludes=args.exclude,
        parallel=not args.no_parallel,
    )

    result = filter_by_severity(result, args.severity)

    if args.output == "json":
        print(result.to_json())
    elif args.output == "text":
        print(result.to_text())
    else:  # both
        print(result.to_text())
        print("\n--- JSON Output ---")
        print(result.to_json())

    return 0 if not result.errors else 1


if __name__ == "__main__":
    sys.exit(main())
