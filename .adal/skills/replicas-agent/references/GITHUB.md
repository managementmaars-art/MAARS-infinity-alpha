# GitHub Integration

This guide covers how to interact with GitHub from within your Replicas workspace.

## Prerequisites

The `gh` CLI is pre-installed and authenticated in your workspace. You can verify this:

```bash
gh auth status
```

If authenticated, you can immediately use `gh` for all GitHub operations. No additional setup is needed.

## Using the `gh` CLI

The GitHub CLI (`gh`) is the recommended way to interact with GitHub. It handles authentication, pagination, and API formatting automatically.

### Pull Requests

```bash
# Create a PR
gh pr create --title "Title" --body "Description"

# List open PRs
gh pr list

# View a specific PR
gh pr view 123

# Review/check PR status
gh pr checks 123

# Merge a PR
gh pr merge 123
```

### Issues

```bash
# Create an issue
gh issue create --title "Title" --body "Description"

# View an issue
gh issue view 123

# List issues
gh issue list

# Close an issue
gh issue close 123

# Add a comment
gh issue comment 123 --body "Your comment"
```

### Repository Operations

```bash
# View repo info
gh repo view

# Clone a repo
gh repo clone owner/repo

# List releases
gh release list
```

### GitHub Actions / Checks

```bash
# List workflow runs
gh run list

# View a specific run
gh run view RUN_ID

# Watch a run in progress
gh run watch RUN_ID

# Re-run failed jobs
gh run rerun RUN_ID --failed
```

### GitHub API (Advanced)

For operations not covered by `gh` subcommands, use the API directly:

```bash
# GET request
gh api repos/owner/repo/pulls/123/comments

# POST request
gh api repos/owner/repo/issues/123/comments -f body="Comment text"

# GraphQL query
gh api graphql -f query='{ repository(owner: "owner", name: "repo") { issues(first: 10) { nodes { title number } } } }'
```

### Working with PR Reviews

```bash
# View PR comments
gh api repos/owner/repo/pulls/123/comments

# View PR review comments
gh api repos/owner/repo/pulls/123/reviews

# Submit a review
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Changes needed"
```

## Image Uploads in PRs

GitHub does NOT have a public API for uploading images to PRs/issues. When you need to include images:
- Do NOT use placeholder image URLs
- Do NOT commit screenshots as files to the repository
- Upload images to Imgur (or another external host) and use the returned URLs in your PR markdown
- If you were triggered from Slack, also upload the images to the Slack thread so the user can see them directly
