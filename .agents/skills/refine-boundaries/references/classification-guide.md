# Boundaries Classification Guide

Full reference for the 3-tier classification used by `/refine-boundaries`.
SKILL.md has the short decision tree; this file expands each tier with
worked examples and edge cases.

## The three tiers

### Always do

Rules that describe **default behavior during a category of work**.
The agent should fall into these by default whenever it is doing work
that fits the rule's scope.

**Shape:** Imperative present tense, no hedging. Describes an action
that should be taken, not avoided.

**Examples (cross-cutting):**
- "Run the project's test suite before suggesting a commit"
- "Check `git status` before destructive operations"
- "Read existing code before proposing a refactor"

**Examples (topic-inline):**
- Code Style: "Use zod schemas for all API input validation"
- Testing: "Write a failing test first when fixing a bug"
- Git Workflow: "Reference the issue number in the commit body"

**Common misclassification.** If the rule starts with "Don't forget to..."
it is almost certainly an Always do rule, not a Never do. The action is
the positive form.

### Ask first

Rules that describe **reversible but visible actions**. The action can
be undone, but it affects other people or external systems, and the
user's intent is not always obvious enough to act on without checking.

**Shape:** A gerund (noun form) naming the kind of action, optionally
with a qualifier.

**Examples (cross-cutting):**
- "Adding a new package dependency"
- "Running a database migration"
- "Sending a message via Slack, email, or other notification"
- "Creating, closing, or commenting on issues or PRs"
- "Modifying CI/CD pipeline files"

**Examples (topic-inline rare.)** Topic sections rarely host "Ask first"
rules because they describe actions, not pauses. If an "Ask first" rule
feels topic-scoped, it usually belongs in Boundaries anyway.

**Common misclassification.** "Ask first" is not the same as "tell me
before continuing". It means: **stop, ask a yes/no question, wait for
answer**. If the agent should continue after merely mentioning the
action, that is not Ask first — it is Always do ("Always announce
package additions in the response summary").

### Never do

Rules that describe **irreversible or boundary-violating actions**. The
agent must refuse these even if instructed, unless the user explicitly
overrides the rule in-session.

**Shape:** Imperative negative, often prefixed with **NEVER** or
**Never**. Describes an action to refuse.

**Examples (cross-cutting):**
- "Commit secrets, credentials, or `.env` files"
- "Skip git hooks with `--no-verify` or bypass signing"
- "Force-push to `main` or other protected branches"
- "Delete files or branches the user did not mention"
- "Run `rm -rf` on paths outside the current working directory"

**Examples (topic-inline):**
- Code Style: "**NEVER** use `any` type"
- Testing: "**NEVER** mock the database in integration tests"
- Git Workflow: "**NEVER** amend or rebase published commits"

**Common misclassification.** If the consequence of the action is
"annoying to fix" but technically recoverable (e.g., creating a PR
with a typo in the title), it belongs in **Ask first**, not Never do.
Reserve Never do for irreversible damage.

## Severity comparison when multiple branches match

When a rule could belong to more than one tier, prefer the **stronger**
tier in this order: Never > Ask > Always.

**Example.** "Don't push changes without running tests."
- Interpretation A (Always): "Always run tests before push" → default behavior
- Interpretation B (Never): "Never push without running tests" → refusal
- Decision: **Never** wins. The user is describing a refusal condition.

## The inline vs cross-cutting decision test

After choosing a tier, decide whether the rule lives inline in a topic
section or cross-cutting in `## Boundaries`.

| Question | Inline | Cross-cutting |
|---|---|---|
| "Is this about **how** to do one kind of task?" | ✓ | |
| "Is this about **when** to pause and check before any action?" | | ✓ |
| "Does the rule reference a specific file/tool/subsystem?" | ✓ | |
| "Does the rule apply to 'any action' or 'any commit' or 'any change'?" | | ✓ |
| "Can the rule be phrased as 'when writing X...'?" | ✓ | |
| "Can the rule be phrased as 'before taking action Y...'?" | | ✓ |

**Tie-breaker.** If the rule could live in either place, prefer
**inline**. Inline rules are closer to the context where they matter
and reduce Boundaries bloat. Only move to Boundaries when the rule
genuinely spans multiple topics or has no topic at all.

## Things that look like boundaries but are not

These should be redirected elsewhere, not added to Boundaries:

| Looks like | Actually belongs in |
|---|---|
| "Use TypeScript strict mode" | `tsconfig.json` (linter config), not AGENTS.md |
| "Indent with 2 spaces" | `.prettierrc` or `.editorconfig` |
| "Name files kebab-case" | Linter or `## Code Style` inline |
| "Use the `gh` CLI for GitHub actions" | `## External Tools > CLIs` |
| "Main branch is `main`, not `master`" | `## Git Workflow` body |
| "We use Jest" | Derivable from `package.json` — not worth writing anywhere |
| "Write good commit messages" | Truism — redirect to conventional commit rule in `## Git Workflow` |

When a user tries to add one of these, gently redirect:

> "That rule is better placed in [target]. Adding it to Boundaries
> would make the section too noisy and the rule would be easier to
> ignore. Would you like me to [alternative action]?"

## Security rule density heuristic

When scanning existing Never do rules for security density, match on
these keywords (case-insensitive): `secret`, `credential`, `password`,
`token`, `auth`, `authorization`, `authentication`, `env`, `.env`,
`encrypt`, `decrypt`, `PII`, `personally identifiable`, `permission`,
`sudo`, `root`, `admin`, `CSRF`, `XSS`, `SQL injection`, `OWASP`,
`vulnerability`, `CVE`.

Threshold: **5 or more matches** triggers the "extract to `## Security`"
suggestion. Below 5, inline placement is fine — even 4 security rules
in Boundaries does not justify a dedicated section.

The extraction is optional. Small projects often prefer the flat
Boundaries even at 10+ rules. Security-sensitive domains (auth,
payment, healthcare, fintech) benefit from the named section because
reviewers instinctively look for it.
