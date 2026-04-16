# Platform Adaptation

> Read this file only when `remote.origin.url` does not point to GitHub.
>
> Preserve the same workflow: validate auth, compare the full branch diff, show
> a preview, wait for explicit confirmation, create the PR or MR, then return
> the resulting URL.

## GitLab

Use the same drafting logic from the main skill, then adapt the full execution
path to GitLab:

1. Confirm `glab` is installed and authenticated before continuing.
2. Fetch remote refs and verify the target branch exists on the remote.
3. Verify the source branch exists on the remote and is up to date with the
   local branch tip. If it is missing or stale, ask the user for permission to
   push it first. If the user declines, stop with `PR_CREATE: HEAD_BRANCH_UNPUSHED`.
4. Reuse the same title, body, reviewer, label, and draft decisions from the
   preview loop.
5. If the installed `glab` version clearly supports listing labels, use that to
   suggest existing labels. Otherwise skip auto-suggested labels or ask the user
   for explicit labels instead of guessing.
6. Create the merge request with `glab mr create`, mapping:
   - base branch -> target branch
   - head branch -> source branch
   - title -> title
   - description -> description
   - draft state -> draft or ready
   - reviewers -> reviewer equivalents supported by the installed `glab` version
7. Verify the created merge request URL and confirm it uses the intended base
   and head branches before returning it to the user.

If the local `glab` version exposes different flag names, use its built-in help
to map the preview fields to the correct create command instead of guessing.

## Bitbucket

Bitbucket workflows vary more by team and hosting setup, so keep the same
preview-first flow and then:

1. Detect whether the repository uses a supported Bitbucket CLI or a custom API
   wrapper.
2. If no supported CLI or API flow is available, stop and ask the user which
   Bitbucket workflow their team expects. Do not fall back to `gh`.
3. Reuse the drafted title, body, reviewer, label, and draft decisions.
4. If the Bitbucket tooling can list labels reliably, use it. Otherwise skip
   label suggestions or ask the user for explicit labels.
5. Create the pull request with the repository's standard tooling.
6. Return the resulting PR URL and confirm the chosen base/head branches.

## Failure Mapping

Use the main skill's failure format for non-GitHub flows too:

- `AUTH` when the platform CLI is missing, unauthenticated, or lacks permission
- `BASE_BRANCH_MISSING` when the target branch does not exist remotely
- `HEAD_BRANCH_UNPUSHED` when the head branch must be pushed and the user
  declines or the push cannot complete
- `EMPTY_DIFF` when there is nothing meaningful to compare
- `CREATE_ERROR` when the platform create command fails after confirmation

## Platform Invariants

Keep these rules unchanged across platforms:

- Ask for the target branch when it was not supplied.
- Base the title and description on the actual compare diff.
- Require at least one reviewer before creation.
- Show the full preview before creating anything.
- Create only after explicit confirmation.
- Return the final URL and the chosen base/head branches.
