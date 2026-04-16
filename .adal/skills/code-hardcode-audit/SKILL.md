---
name: code-hardcode-audit
description: Detect hardcoded values, magic numbers, and leaked secrets. TRIGGERS - hardcode audit, magic numbers, PLR2004, secret scanning.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Code Hardcode Audit

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## When to Use This Skill

Use this skill when the user mentions:

- "hardcoded values", "hardcodes", "magic numbers"
- "constant detection", "find constants"
- "duplicate constants", "DRY violations"
- "code audit", "hardcode audit"
- "PLR2004", "semgrep", "jscpd", "gitleaks", "ast-grep", "SSoT violations"
- "secret scanning", "leaked secrets", "API keys", "bandit", "trufflehog", "whispers"
- "passwords in code", "credential leaks", "entropy detection"
- "config file secrets", "hardcoded credentials"

## Quick Start

```bash
# Preflight — verify all tools installed and configured
uv run --python 3.13 --script scripts/preflight.py -- .

# Full audit (all 9 tools, preflight + both outputs)
uv run --python 3.13 --script scripts/audit_hardcodes.py -- src/

# Individual tools (all respect .gitignore):

# Python credential detection (passwords, tokens, API keys in variable names)
uv run --python 3.13 --script scripts/run_bandit.py -- src/

# Entropy-based secret detection (catches secrets regex can't)
uv run --python 3.13 --script scripts/run_trufflehog.py -- src/

# Config file secrets (YAML, JSON, Dockerfile, .env, .properties)
uv run --python 3.13 --script scripts/run_whispers.py -- src/

# AST-based hardcode detection (numeric args, URLs, paths, sleep)
uv run --python 3.13 --script scripts/run_ast_grep.py -- src/

# Python magic numbers only (fastest)
uv run --python 3.13 --script scripts/run_ruff_plr.py -- src/

# Pattern-based detection (URLs, ports, paths, sleep, circuit breaker)
uv run --python 3.13 --script scripts/run_semgrep.py -- src/

# Env-var coverage audit (BaseSettings cross-reference)
uv run --python 3.13 --script scripts/audit_env_coverage.py -- src/

# Copy-paste detection
uv run --python 3.13 --script scripts/run_jscpd.py -- src/

# Regex-based secret scanning (API keys, tokens, passwords)
uv run --python 3.13 --script scripts/run_gitleaks.py -- src/
```

## Tool Overview

| Tool             | Detection Focus                                | Language Support | Speed   |
| ---------------- | ---------------------------------------------- | ---------------- | ------- |
| **Preflight**    | Tool availability + config validation          | N/A              | Instant |
| **Bandit**       | Hardcoded passwords, tokens in Python (B105-7) | Python           | Fast    |
| **TruffleHog**   | Entropy-based secret + API verification        | Any (file-based) | Medium  |
| **Whispers**     | Config file secrets (YAML, JSON, Docker, .env) | Config files     | Medium  |
| **ast-grep**     | Hardcoded literals in args, sleep, URLs, paths | Multi-language   | Fast    |
| **Ruff PLR2004** | Magic value comparisons                        | Python           | Fast    |
| **Semgrep**      | URLs, ports, paths, credentials, retry config  | Multi-language   | Medium  |
| **Env-coverage** | BaseSettings cross-reference, coverage gaps    | Python           | Fast    |
| **jscpd**        | Duplicate code blocks                          | Multi-language   | Slow    |
| **gitleaks**     | Regex-based secrets, API keys, passwords       | Any (file-based) | Fast    |

## Output Formats

### JSON (--output json)

```json
{
  "summary": {
    "total_findings": 42,
    "by_tool": { "ruff": 15, "semgrep": 20, "jscpd": 7 },
    "by_severity": { "high": 5, "medium": 25, "low": 12 }
  },
  "findings": [
    {
      "id": "MAGIC-001",
      "tool": "ruff",
      "rule": "PLR2004",
      "file": "src/config.py",
      "line": 42,
      "column": 8,
      "message": "Magic value used in comparison: 8123",
      "severity": "medium",
      "suggested_fix": "Extract to named constant"
    }
  ],
  "refactoring_plan": [
    {
      "priority": 1,
      "action": "Create constants/ports.py",
      "finding_ids": ["MAGIC-001", "MAGIC-003"]
    }
  ]
}
```

### Compiler-like Text (--output text)

```
src/config.py:42:8: PLR2004 Magic value used in comparison: 8123 [ruff]
src/probe.py:15:1: hardcoded-url Hardcoded URL detected [semgrep]
src/client.py:20-35: Clone detected (16 lines, 95% similarity) [jscpd]

Summary: 42 findings (ruff: 15, semgrep: 20, jscpd: 7)
```

## CLI Options

```
--output {json,text,both}  Output format (default: both)
--tools {all,ast-grep,ruff,semgrep,jscpd,gitleaks,env-coverage,bandit,trufflehog,whispers}  Tools to run
--severity {all,high,medium,low}  Filter by severity (default: all)
--exclude PATTERN  Glob pattern to exclude (repeatable)
--no-parallel  Disable parallel execution
--skip-preflight  Skip tool availability check
```

## References

- [Tool Comparison](./references/tool-comparison.md) - Detailed tool capabilities
- [Output Schema](./references/output-schema.md) - JSON schema specification
- [Troubleshooting](./references/troubleshooting.md) - Common issues and fixes

## Related

- ADR-0046: Semantic Constants Abstraction
- ADR-0047: Code Hardcode Audit Skill
- `code-clone-assistant` - PMD CPD-based clone detection (DRY focus)

---

## Troubleshooting

| Issue                    | Cause                       | Solution                                                                 |
| ------------------------ | --------------------------- | ------------------------------------------------------------------------ |
| Ruff PLR2004 zero output | PLR2004 globally suppressed | Run preflight: `uv run --python 3.13 --script scripts/preflight.py -- .` |
| Ruff PLR2004 not found   | Ruff not installed or old   | `uv tool install ruff` or upgrade                                        |
| ast-grep not found       | Binary not installed        | `cargo install ast-grep` or `brew install ast-grep`                      |
| Semgrep timeout          | Large codebase scan         | Use `--exclude` to limit scope                                           |
| jscpd memory error       | Too many files              | Increase Node heap: `NODE_OPTIONS=--max-old-space-size=4096`             |
| gitleaks false positives | Test data flagged           | Add patterns to `.gitleaks.toml` allowlist                               |
| Env-coverage misses      | Not using BaseSettings      | Only detects pydantic BaseSettings; other config patterns skipped        |
| No findings in output    | Wrong directory specified   | Verify path exists and contains source files                             |
| JSON parse error         | Tool output malformed       | Run tool individually with `--output text`                               |
| Missing tool in PATH     | Tool not installed globally | Run preflight first, then install missing tools                          |
| Bandit false positives   | `password = ''` in init     | Filter B105 by confidence: `--confidence HIGH`                           |
| TruffleHog timeout       | Scanning .venv/node_modules | All tools respect `.gitignore`; ensure large dirs are gitignored         |
| TruffleHog regex error   | Glob patterns in .gitignore | Complex globs (`**/*.rs.bk`) are auto-skipped; only simple names used    |
| Whispers slow scan       | Large directories           | Exclude via `.gitignore`; whispers config auto-generated from it         |
| Whispers zero findings   | No config files in scope    | Whispers targets YAML/JSON/Docker/INI; use on project root, not src/     |
| Severity filter empty    | No findings at that level   | Use `--severity all` to see all findings                                 |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
