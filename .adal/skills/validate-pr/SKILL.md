---
name: validate-pr
description: Validate the current Pull Request branch name, body, and status against Marshroom conventions
---

Validate the current Pull Request against Marshroom conventions.

Steps:
1. Read `${MARSHROOM_STATE:-~/.config/marshroom/state.json}` and parse the JSON
2. Run `git branch --show-current` to get the current branch name
3. Find the cart entry whose `branchName` matches the current git branch. If no match, tell the user they're not on a cart issue branch
4. Get the current PR info: `gh pr view --json title,body,headRefName`
5. Validate the following:

**Branch Name Check:**
- The PR's head branch should match the matched cart entry's `branchName`
- Expected format: `Feature/#N` or `HotFix/#N`
- If mismatched, show: "Branch mismatch: expected '{branchName}', got '{actual}'"

**PR Body Check:**
- The body MUST contain `close #{issueNumber}`
- If missing, suggest: `gh pr edit --body "$(gh pr view --json body -q '.body')\n\nclose #<issueNumber>"`

**Status Check:**
- Read the `status` field from the matched cart entry
- After PR creation, status should be `"pending"`
- If status is still `"running"`, warn that the status was not updated (suggest running `marsh pr`)
- If status is `"soon"`, warn that `/start-issue` may not have been run

**Summary:**
- Show pass/fail status for each check
- If all checks pass, confirm the PR is valid
- If any check fails, provide the fix commands
