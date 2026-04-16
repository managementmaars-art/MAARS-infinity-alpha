---
name: "pr-creator"
description: 'Create review-ready pull requests from the current branch by validating repo state, comparing against a user-specified base branch, drafting a title and body from the real branch diff, suggesting reviewers and labels, previewing the result, and creating the PR only after explicit confirmation. Use when the user asks to create or open a PR, draft pull request, merge request, code review request, or says their work is ready for review.'
---

# PR Creator

Create a review-ready pull request from the current branch. This skill keeps the
user in the loop at every decision point: gather missing inputs, validate branch
state, draft the PR from the actual compare diff, preview the result, apply user
edits, and submit only after explicit confirmation.

## Inputs

| Input | Required | Example |
| ----- | -------- | ------- |
| `TARGET_BRANCH` | No | `main` |
| `PR_STATE` | No | `draft` |
| `REVIEWERS` | No | `alice,bob` |
| `TITLE_OVERRIDE` | No | `docs(skills): refine pr-creator workflow` |
| `BODY_OVERRIDE` | No | `## Summary ...` |
| `LABELS_OVERRIDE` | No | `documentation,enhancement` |

Ask for any missing inputs during the workflow. `PR_STATE` defaults to `draft`.

## Output Contract

For GitHub remotes, finish with all of these:

- A created PR URL.
- Final values for base branch, head branch, title, description, reviewers,
  labels, and PR state.
- A preview shown to the user and explicitly approved before `gh pr create`.

For non-GitHub remotes:

- Detect the platform from `remote.origin.url`.
- Read `./references/platform-adaptation.md`.
- Follow the matching create flow before submitting anything.

## Workflow Overview

```text
repo + remote state
        |
        v
preflight validation
        |
        v
branch comparison and diff analysis
        |
        v
title/body draft
        |
        v
reviewer and label suggestions
        |
        v
preview -> revise if needed -> confirm
        |
        v
create PR -> verify URL
```

## How This Skill Works

This skill does exactly five things:

- Inspect the repository, hosting platform, and branch state.
- Validate that the chosen base and head branches can produce a meaningful PR.
- Draft the PR title and description from the real compare diff.
- Suggest reviewers and labels from repo metadata.
- Create the PR only after the user approves the preview.

Keep only short structured state between steps: platform, base/head branches,
changed files, diff size signal, drafted title/body, suggested reviewers/labels,
and the current preview. Use direct `git` and the platform-appropriate CLI
inline because each result is used immediately in the user confirmation loop.

## Execution Steps

1. **Identify repo, platform, and head branch**

   Run:

   ```bash
   git config --get remote.origin.url
   git rev-parse --abbrev-ref HEAD
   git status --short --branch
   ```

   Then:

   - Detect the hosting platform from `remote.origin.url`, including GitHub
     Enterprise hosts that should follow the GitHub branch.
   - If the working tree has uncommitted changes, tell the user those changes
     are not part of the PR until they are committed.
   - Ask for `TARGET_BRANCH` if it was not already supplied.
   - If the remote is not GitHub, read `./references/platform-adaptation.md`
     and follow the matching platform branch for the GitHub-only command blocks
     in steps 2, 6, 8, and 9.

2. **Run preflight validation**

   For GitHub remotes, run:

   ```bash
   git fetch origin --prune
   gh auth status
   git ls-remote --heads origin <current_branch>
   git rev-parse --verify origin/<target_branch>
   git rev-list --left-right --count origin/<current_branch>...<current_branch>
   ```

   Then:

   - If `gh auth status` fails, stop with `AUTH`.
   - If the head branch is not on the remote, or local commits are ahead of
     `origin/<current_branch>`, tell the user a push is required before the PR
     can be created and before the compare diff is trustworthy.
   - Ask for confirmation, then run:

     ```bash
     git push -u origin <current_branch>
     ```

   - If the user declines the push, stop with `HEAD_BRANCH_UNPUSHED`.

   - If the target branch does not exist on the remote, stop with
     `BASE_BRANCH_MISSING` and ask the user for a valid base branch.
   - For non-GitHub remotes, follow the matching preflight and auth flow in
     `./references/platform-adaptation.md` before moving to the diff step.

3. **Analyze the full branch diff**

   Run:

   ```bash
   git log --oneline origin/<target_branch>..origin/<current_branch>
   git diff --shortstat origin/<target_branch>...origin/<current_branch>
   git diff --stat origin/<target_branch>...origin/<current_branch>
   git diff --name-only origin/<target_branch>...origin/<current_branch>
   git diff origin/<target_branch>...origin/<current_branch>
   ```

   Use this data to understand the whole PR, not just the latest commit.

   Validation rules:

   - If there are no commits or no diff, stop with `EMPTY_DIFF`.
   - If the diff is roughly over 1000 lines, or clearly spans unrelated areas,
     ask the user whether to proceed or split the work into smaller PRs.
   - Only continue after the user explicitly confirms a large PR should proceed.

4. **Draft the PR title**

   Pick the most accurate conventional commit type from the branch diff:

   - `feat` for new functionality
   - `fix` for bug fixes
   - `chore` for maintenance or housekeeping
   - `docs` for documentation-only changes
   - `style` for formatting-only changes
   - `refactor` for structural improvements without behavior change
   - `test` for test-only changes
   - `perf` for performance improvements
   - `ci` for CI/CD changes
   - `build` for build tooling or dependency system changes

   Add an optional scope only when one module, domain, or subsystem clearly
   dominates the diff.

   Title rules:

   - Format as `type(scope): description` or `type: description`
   - Keep the description concise and lowercase
   - Wrap code identifiers, file names, and technical keywords in backticks
   - If `TITLE_OVERRIDE` is supplied, use it exactly

   Examples:

   - `feat(pricing): include volume discounts in quote calculation`
   - `fix(auth): handle missing refresh token in sessionStore`
   - `docs(skills): tighten pr-creator validation flow`
   - `refactor(api): extract review metadata mapping`

5. **Draft the PR description**

   Use this structure unless `BODY_OVERRIDE` is supplied:

   ```markdown
   ## Summary

   A 2-3 sentence overview of what changed and why it matters.

   ## Key Changes

   - Specific change 1 with relevant detail
   - Specific change 2 with relevant detail
   - Add more bullets only when they carry distinct value

   ## Impact

   - Who or what is affected
   - Migration, rollout, or deployment considerations
   - Testing notes, if the diff shows them
   ```

   Description rules:

   - Write from the actual diff, not from assumptions.
   - Be specific about file paths, behaviors, and user-visible outcomes.
   - Mention tests only when they were added, changed, or are relevant to risk.

6. **Suggest reviewers and labels**

   For reviewers:

   - Check `.github/CODEOWNERS`, then `CODEOWNERS`, if either file exists.
   - Match changed files against the most relevant owners.
   - Present the suggested reviewers to the user and let them edit the list.
   - If no CODEOWNERS file exists, ask the user for at least one reviewer.
   - Require at least one reviewer before creation.

   For GitHub labels:

   ```bash
   gh label list --limit 100
   ```

   Then:

   - Suggest only labels that actually exist in the repository.
   - Use the PR type and diff content to guide suggestions.
   - Skip labels silently if none fit.
   - If `LABELS_OVERRIDE` is supplied, use it instead of auto-suggestions.
   - For non-GitHub remotes, follow the platform-specific label guidance in
     `./references/platform-adaptation.md` instead of calling `gh`.

7. **Preview, validate, and revise**

   Show the complete preview before creating anything:

   ```text
   PR Preview
   ----------
   Title:      <generated title>
   Target:     <target_branch>
   Source:     <current_branch>
   Reviewers:  <reviewer list>
   Labels:     <label list or "none">
   Status:     <draft or ready>

   Description:
   <generated description>
   ```

   Ask the user to confirm or request edits.

   Validation loop:

   - Apply requested title, body, reviewer, label, or status changes.
   - Show the updated preview again.
   - If three preview cycles still do not converge, ask the user for explicit
     final values instead of continuing to redraft.

8. **Create the PR**

   After explicit confirmation, create the PR with the CLI that matches the
   detected hosting platform. Prefer a heredoc or body file for long
   descriptions.

   GitHub draft PR:

   ```bash
   gh pr create \
     --base "<target_branch>" \
     --head "<current_branch>" \
     --title "<title>" \
     --body "<description>" \
     --draft \
     --reviewer "<reviewer1>,<reviewer2>"
   ```

   GitHub ready PR:

   ```bash
   gh pr create \
     --base "<target_branch>" \
     --head "<current_branch>" \
     --title "<title>" \
     --body "<description>" \
     --reviewer "<reviewer1>,<reviewer2>"
   ```

   For GitHub, add labels only when they exist and the user approved them. Use
   `-l` or `--label` in the form supported by the installed `gh` version.
   For non-GitHub remotes, follow the matching create flow in
   `./references/platform-adaptation.md`.

9. **Verify the result**

   After creation:

   - Capture and return the PR URL.
   - Confirm the created PR uses the intended base and head branches.
   - For non-GitHub remotes, use the platform-specific verification flow from
     `./references/platform-adaptation.md` instead of GitHub-only checks.
   - If creation fails, stop with a structured failure category and explain the
     next action clearly.

## Failure Handling

When the workflow cannot continue, report the issue in this format:

```text
PR_CREATE: <CATEGORY>
Reason: <one line>
Next step: <one clear action>
```

Use these categories:

- `AUTH` - the platform CLI is missing, unauthenticated, or lacks permission
- `BASE_BRANCH_MISSING` - the requested target branch does not exist remotely
- `HEAD_BRANCH_UNPUSHED` - the source branch must be pushed before PR creation
- `EMPTY_DIFF` - the source branch has nothing to compare against the target
- `CREATE_ERROR` - the platform create command failed after confirmation

## Reference Files

- `./references/platform-adaptation.md` - load only when the remote is not
  GitHub

## Example

<example>
Input:
- Current branch: `docs/pr-creator-skill`
- Target branch: `main`
- PR state: `draft`

Flow:
1. Inspect the remote URL, current branch, and working tree state.
2. Fetch remote refs and confirm `gh auth status` passes.
3. Compare `origin/main...origin/docs/pr-creator-skill`.
4. Draft:
   - Title: `docs(skills): strengthen the pr-creator workflow`
   - Reviewers: `@docs-team`
   - Labels: `documentation`
5. Show preview and let the user edit it.
6. After confirmation, run the platform-appropriate create command.

Output:
- PR URL returned to the user
- Final preview values recorded in the reply
</example>
