---
name: workflow-audit
description: >-
  Audit GitHub Actions workflows for correctness, security, and unattended
  reliability. Use when asked to audit workflows, check CI health, review
  workflow security, or before committing workflow changes.
---

# Workflow Audit

Comprehensive audit of `.github/workflows/*.yml` files against GitHub Actions
best practices, security hardening guidelines, and project conventions.

## When to Use

- User asks to audit, review, or check workflows
- Before committing changes to any workflow file
- After a workflow failure that needs root-cause analysis
- Periodic health check (e.g., monthly)

## Workflow

1. **Discover** — Glob `.github/workflows/*.yml` and list all workflow files.
2. **Parse** — Read each file; validate YAML syntax.
3. **Audit** — Run every check in the checklist below against each file.
4. **Cross-check** — Run cross-workflow consistency checks.
5. **Report** — Output a findings table sorted by severity (critical > high > medium > low).
6. **Fix offer** — For each finding, suggest a concrete fix (diff or instruction).

## Audit Checklist

### 1. YAML Validity
- File parses as valid YAML.
- No duplicate keys at the same level.
- No tabs (GitHub Actions requires spaces).

### 2. Action Version Currency

Check every `uses:` line.

| Pattern | Severity | Rule |
|---------|----------|------|
| `actions/checkout@v4` or lower | **critical** | Upgrade to `@v6`. Node.js 20 actions break June 2, 2026 (forced to Node 24). |
| `actions/setup-node@v4` or lower | **critical** | Same — upgrade to `@v6`. |
| `actions/cache@v3` or lower | **high** | Upgrade to `@v4`. |
| `pnpm/action-setup@v3` or lower | **high** | Upgrade to `@v4`. |
| `softprops/action-gh-release@v1` | **medium** | Upgrade to `@v2`. |
| `actions/upload-pages-artifact@v2` or lower | **medium** | Upgrade to `@v3`. |
| `actions/deploy-pages@v3` or lower | **medium** | Upgrade to `@v4`. |
| Any `@main` or `@master` pin | **high** | Pin to a tag or SHA — mutable refs are a supply-chain risk. |

**Node.js deprecation timeline** (reference for findings):
- **June 2, 2026**: Node 24 becomes default (`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` to opt in early).
- **Fall 2026**: Node 20 removed entirely from runners.
- Temporary opt-out after June 2: `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` (stops working fall 2026).

### 3. Security — Script Injection

For every `run:` block, check for **untrusted context expressions used inline**:

```
# DANGEROUS — attacker-controlled input interpreted by shell
run: echo "${{ github.event.issue.title }}"

# SAFE — passed via environment variable
env:
  TITLE: ${{ github.event.issue.title }}
run: echo "$TITLE"
```

**Untrusted contexts** (must NEVER appear directly in `run:` blocks):
- `github.event.issue.title` / `.body`
- `github.event.pull_request.title` / `.body`
- `github.event.comment.body`
- `github.event.review.body` / `github.event.review_comment.body`
- `github.event.commits.*.message`
- `github.event.head_commit.message` / `.author.email` / `.author.name`
- `github.event.pull_request.head.ref` / `.head.label` / `.head.repo.default_branch`
- `github.head_ref`
- `github.event.pages.*.page_name`

**Safe contexts** (numeric or system-controlled, OK inline):
- `github.event.issue.number`, `github.event.pull_request.number`
- `github.repository`, `github.run_id`, `github.sha`
- `github.ref` (only on push/tag events, not PR)
- `secrets.*`, `env.*`, `matrix.*`

### 4. Security — Permissions

| Check | Severity | Rule |
|-------|----------|------|
| No `permissions:` block at all | **high** | Add explicit permissions — defaults give broad access. |
| `permissions: write-all` | **critical** | Never use. Specify individual scopes. |
| Unused permission scopes | **medium** | Remove permissions not needed by any step. |
| `id-token: write` without OIDC usage | **medium** | Only needed for Bedrock/Vertex/Foundry or cloud OIDC. |
| `pull_request_target` trigger | **high** | Grants write access from forks — verify checkout uses PR base, not head. |

### 5. Security — Auto-merge and Bot Patterns

| Check | Severity | Rule |
|-------|----------|------|
| `gh pr merge --auto` without author guard | **high** | Restrict to bot PRs: `if: github.event.pull_request.user.login == 'claude[bot]'` |
| `allowed_bots: '*'` in claude-code-action | **medium** | Prefer explicit bot names over wildcard. |

### 6. Reliability — Timeouts

| Check | Severity | Rule |
|-------|----------|------|
| Job without `timeout-minutes` | **high** | Default is 360 min (6 hours). Always set explicit timeouts. |
| Claude Code action jobs | **high** | Must have `timeout-minutes` (recommended: 15 for review, 30 for fix). |
| Build jobs | **medium** | Recommended: 30-45 min depending on platform. |

### 7. Reliability — Error Handling

| Check | Severity | Rule |
|-------|----------|------|
| `git push` to a protected branch | **critical** | Will fail if branch protection requires status checks. Push to unprotected branch or use PR. |
| `gh pr merge` without `\|\| true` or `continue-on-error` | **medium** | May fail if PR is not mergeable — handle gracefully. |
| Steps after a `continue-on-error` step that depend on its output | **medium** | Check if downstream steps handle the soft failure. |
| Network-dependent steps without retry or `continue-on-error` | **low** | CDN downloads, API calls can be flaky. |

### 8. Reliability — Concurrency

| Check | Severity | Rule |
|-------|----------|------|
| Scheduled workflow without `concurrency` group | **medium** | Overlapping runs waste resources. |
| `cancel-in-progress: true` on deploy workflows | **high** | Can corrupt partial deployments. Use `false` for deploys. |
| Missing `concurrency` on Claude Code jobs | **medium** | Multiple concurrent AI runs on the same issue/PR waste credits. |

### 9. Reliability — Branch Protection Awareness

| Check | Severity | Rule |
|-------|----------|------|
| Workflow pushes to `main` (or default branch) | **critical** | Check if branch protection allows this. Use a data branch or PR workflow. |
| Workflow creates commits without checking `git diff` first | **medium** | May create empty commits or fail on no-changes. |

### 10. Cross-Workflow Consistency

| Check | Severity | Rule |
|-------|----------|------|
| Different `node-version` across workflows | **high** | All workflows should use the same Node.js version (currently 22). |
| Different `pnpm` version across workflows | **high** | All workflows should use the same pnpm version (currently 10). |
| Different Rust toolchain specification | **medium** | Should be consistent unless intentionally testing multiple versions. |
| Duplicate triggers (same event in multiple workflows) | **medium** | Can cause double-execution. Verify intentional. |

### 11. Claude Code Action — Configuration

Reference: `anthropics/claude-code-action@v1`

| Check | Severity | Rule |
|-------|----------|------|
| Using `@beta` or `@v0` | **critical** | Migrate to `@v1`. v0.x inputs are deprecated. |
| Using deprecated inputs (`direct_prompt`, `model`, `allowed_tools`, `max_turns`, `timeout_minutes`) | **high** | Migrate to `prompt` + `claude_args`. |
| Missing `claude_code_oauth_token` or `anthropic_api_key` | **critical** | One auth method is required. |
| `--model` not specified in `claude_args` | **low** | Defaults to action's default model. Specify for reproducibility. |
| `--max-turns` not specified for fix/implementation jobs | **medium** | Unbounded turns burn credits. Recommend 15-25 for fixes. |
| `show_full_output: true` on review jobs | **low** | Verbose — only needed for debugging. |

**Key `claude_args` flags:**
- `--model <model-id>` — e.g., `claude-opus-4-6`, `claude-sonnet-4-6`
- `--max-turns <N>` — limit conversation turns
- `--allowedTools <tool1>,<tool2>` — restrict tool access
- `--disallowedTools <tool1>` — block specific tools
- `--system-prompt "..."` — custom system prompt

**Authentication options:**
- `anthropic_api_key` — direct Anthropic API
- `claude_code_oauth_token` — Claude Code OAuth (subscription-based)
- `use_bedrock: true` + OIDC — Amazon Bedrock
- `use_vertex: true` + OIDC — Google Vertex AI

### 12. Trigger Hygiene

| Check | Severity | Rule |
|-------|----------|------|
| `release: [published]` + `workflow_dispatch` for same logic | **medium** | Choose one trigger path to avoid double-execution. |
| `push: branches: [main]` on workflows that also have `pull_request` | **low** | Intentional for CI — but verify both are needed. |
| Scheduled workflow that only runs on default branch | **low** | Verify schedule cron syntax with crontab.guru. |
| Workflow with no `paths` filter on push trigger | **low** | Consider adding `paths:` to avoid unnecessary runs. |

## Report Format

Output a markdown table:

```markdown
## Workflow Audit Report

| # | Severity | File | Check | Finding | Fix |
|---|----------|------|-------|---------|-----|
| 1 | critical | ci.yml | Action versions | `actions/checkout@v4` — Node 20 deprecated | Upgrade to `@v6` |
| 2 | high | claude.yml | Auto-merge | Enabled for all PRs | Add `if: github.event.pull_request.user.login == 'claude[bot]'` |
```

After the table, add a **Summary** line:
`X critical, Y high, Z medium, W low findings across N workflow files.`

## Notes

- Do NOT modify workflow files during audit — report only.
- When the user asks to fix findings, apply changes and re-audit to verify.
- For security findings, always explain the attack vector (not just the rule).
- Check `.github/workflows/` only — ignore `.github/actions/` unless referenced.
