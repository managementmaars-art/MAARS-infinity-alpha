---
name: refine-boundaries
description: >
  Manage the `## Boundaries` section in AGENTS.md — the agent autonomy
  policy encoded as Always do / Ask first / Never do. Accumulates rules
  iteratively from agent mistakes and user guidance, classifies each
  rule into the right tier, and decides whether a rule belongs inline in
  a topic section (Code Style, Testing, Git Workflow) or cross-cutting in
  Boundaries. The only section in agent-collabo that is designed for
  ongoing, error-driven refinement over the life of the project.
  "refine boundaries", "add boundary", "agent did something wrong",
  "add never do", "add always do", "agent mistake",
  "restructure boundaries", "fix agent behavior", "add rule",
  Slash trigger: "/refine-boundaries".
  Auto trigger: when the user reports an agent mistake with phrasing like
  "the agent shouldn't have", "don't do X", "never do Y", "always do Z
  first", or similar corrective statements referring to a recent action.
metadata:
  author: dev-goraebap
  version: "0.1.1"
---
<!-- AUTO-GENERATED - DO NOT EDIT DIRECTLY. Edit src/ instead. -->

# refine-boundaries

Manage the `## Boundaries` section in AGENTS.md. Boundaries is the **agent autonomy policy** — the one section that most commonly grows as the user discovers what agents get wrong, and the one section that benefits from ongoing, error-driven refinement rather than one-shot init.

**Philosophy.** Every other agent-collabo skill is set-and-forget. Boundaries is the exception. Users almost never know the right rules upfront — they discover them by watching agents make mistakes. This skill turns each mistake into a durable rule, classifies it correctly, and places it where future agents will actually see it before taking the same action.

## Scope

**In scope:**
- Add a new rule to `## Boundaries` (Always do / Ask first / Never do)
- Classify a new rule into the correct tier
- Decide whether a rule belongs **inline in a topic section** (Code Style / Testing / Git Workflow) or **cross-cutting in Boundaries**
- Restructure a malformed Boundaries section into the 3-tier format
- Create the `## Boundaries` section if it does not exist
- Suggest splitting rules out to a dedicated `## Security` section when security rules accumulate (≥5)

**Out of scope:**
- Executing the rules (rules are guidance for the next agent, not runnable checks)
- Removing rules — keep this skill additive; manual removal only
- Rewriting rules the user wrote by hand (only modify when the user explicitly asks)
- Enforcing rules at runtime (AGENTS.md is context, not a policy engine)

## Guardrails

| # | Check | On failure |
|---|-------|------------|
| 1 | CWD is a Git repository | "Please run this inside a Git repository." |
| 2 | AGENTS.md exists | "AGENTS.md not found. Run /init-public-rules first." |
| - | Skill update check | **Session dedup**: if you have already fetched `manifest.json` for any agent-collabo skill earlier in this conversation, skip this check entirely and proceed. Otherwise: Let `SELF` be the value of the `name` field in this SKILL.md's frontmatter (e.g., `init-public-rules`). Let `LOCAL` be `metadata.version` from this same frontmatter. Fetch `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json` (1 HTTP request, fail silently on network error). Then evaluate exactly one case in this order: **Case A — outdated**: if `manifest.skills[SELF]` exists and `LOCAL < manifest.skills[SELF]`, tell the user (in their language) "agent-collabo `{SELF}` has a new version ({LOCAL} → {manifest.skills[SELF]}). Run `/agent-collabo-updater` when convenient. Continuing with the current task." then proceed. **Case B — up to date**: if `manifest.skills[SELF]` exists and `LOCAL === manifest.skills[SELF]`, proceed silently. **Case C — renamed away**: if `SELF` does NOT exist as a key in `manifest.skills` AND `SELF` exists as a key in `manifest.deprecated` (note: check the keys of `deprecated`, not the `renamedTo` values), tell the user "This skill `{SELF}` was renamed to `{manifest.deprecated[SELF].renamedTo}` since v{manifest.deprecated[SELF].since}. Run `/agent-collabo-updater` to migrate." then proceed. **Case D — unknown**: if `SELF` is not in `manifest.skills` and not in `manifest.deprecated`, tell the user "Skill `{SELF}` is no longer maintained. Run `/agent-collabo-updater` to clean up." then proceed with caution. Important: `manifest.deprecated` maps OLD names → NEW names. Never warn about a skill whose name is currently in `manifest.skills` just because that name appears as a `renamedTo` value somewhere in `deprecated`. **CDN cache caveat**: GitHub raw enforces `Cache-Control: max-age=300`, so right after a new release is pushed the manifest may be stale for up to 5 minutes via Fastly PoPs. If the user explicitly mentions they just released a new version (e.g., "I just pushed v0.X.Y") and this check still reports up-to-date or shows an older `manifest.version`, do not insist the local install is current — instead mention the 5-minute CDN window and suggest retrying shortly. For all other users this is invisible because they fetch long after the cache expires. |

## Language Policy

Conduct all user-facing communication in the user's language: interview questions, follow-up prompts, status messages, diagnostic reports, and summaries. Detect the language from (in order):

1. The language of the user's most recent messages in the current session
2. Declarations in their local rules file (e.g., `CLAUDE.local.md`, `.cursor/rules/local.mdc`) — look for instructions like "respond in Korean"
3. OS locale (`$LANG`, `$LC_ALL`)
4. English as fallback

Generated file content follows the file's audience: team-shared files (`AGENTS.md`, `CHANGELOG.md`) stay in English regardless of the user's language; personal files (`CLAUDE.local.md`, `GEMINI.local.md`, etc.) use the user's language unless they specify otherwise.

## 3-tier definition

The Boundaries section is always structured as three named sub-sections, in this order:

```markdown
## Boundaries

### Always do
- One-line imperative rules for "every time you do this type of work"
- Rules that describe default behavior the agent should fall into

### Ask first
- Actions that are reversible but visible (commits, PRs, messages to others)
- Actions that touch shared or external systems
- Actions where the user's intent is unclear enough to warrant confirmation

### Never do
- Destructive irreversible actions
- Actions that violate project contracts (edit build output, skip hooks, etc.)
- Security-sensitive actions (commit secrets, disable auth, bypass validation)
```

Read `references/classification-guide.md` for the full decision tree.

## Inline vs cross-cutting

A new rule may belong **inline in a topic section** instead of Boundaries:

| Scope of rule | Placement |
|---|---|
| "Every time you write code / test / commit" — completes within one topic | Topic section inline (e.g., `## Code Style`, `## Testing`, `## Git Workflow`) |
| "Every time you take any action" / "Before any destructive operation" — cross-cutting | `## Boundaries` |
| "When writing code" — topic-specific autonomy (style rule with NEVER prefix) | Topic section inline |
| "When doing anything that could break production" — autonomy policy | `## Boundaries` |

**Decision test.** Ask yourself: *"Is this rule about **how** to do one kind of task, or **when** to pause and check before taking action?"* If "how" → inline. If "when to pause" → Boundaries.

**Example split.**

```markdown
## Code Style
- **NEVER** use `any` type          ← inline (how to write code)

## Testing
- **NEVER** mock the database       ← inline (how to write tests)

## Git Workflow
- **NEVER** force-push to main      ← inline (how to do git)

## Boundaries
### Never do
- Commit secrets or credentials     ← cross-cutting (applies to any action)
- Skip git hooks (--no-verify)      ← cross-cutting (applies to any commit action)
```

## Workflow

### Step 1: Detect intent

Determine entry mode before asking anything.

| Entry signal | Mode |
|---|---|
| User explicitly invoked `/refine-boundaries` | Slash mode → Step 2 (action interview) |
| User described an agent mistake ("the agent shouldn't have", "don't do X") | Auto mode → Step 3 (classify one rule) |
| User explicitly dictated a rule ("always do X first", "never Y") | Auto mode → Step 3 (classify one rule) |

**Auto-trigger principle.** Never re-run the full interview from auto mode. Classify the single rule the user just stated, then exit.

### Step 2: Action interview (slash mode)

```
What would you like to do?

1. Add a new rule from an agent mistake or user guidance
2. Restructure an existing Boundaries section into the 3-tier format
3. Review Boundaries for security rule density
   (suggest splitting to ## Security if ≥5 security-related Never do rules)
4. Cancel
```

### Step 3: Add a new rule (classify + place)

This is the core path — called from auto mode or slash mode option 1.

#### Step 3a: Capture the rule

Ask the user to state the rule in one line, imperatively:

```
What should the agent do (or not do) next time? State it as a single
imperative sentence:

  Good examples:
    - "Never commit files with the .env extension"
    - "Always run pnpm test before suggesting a commit"
    - "Ask before creating a new GitHub issue"
```

If auto mode triggered this step, use the user's reported rule directly.

#### Step 3b: Classify the tier

Apply this decision tree:

1. Does violating this rule cause **irreversible damage** (lost data, published mistakes, secrets leaked, destroyed state)?
   → **Never do**
2. Does this rule describe an action that is **reversible but visible to others** (PR, issue, message, external API call)?
   → **Ask first**
3. Does this rule describe **default behavior** that should always happen during a category of work (run tests, check status, validate input)?
   → **Always do**

If more than one branch matches, prefer the stronger tier (Never > Ask > Always).

State the classification to the user and ask to confirm:

```
I'd classify this as:

  Tier: Never do
  Reason: Violating this rule causes irreversible damage (committed secrets)

Does this match? (y/n/change tier)
```

#### Step 3c: Decide inline vs cross-cutting

Apply the decision test above. If the rule references a specific topic (code style, testing, git), check whether that topic section exists in AGENTS.md:

| Check | Action |
|---|---|
| Rule is topic-scoped AND the matching section exists | Place inline at the end of that topic section with the tier marker (e.g., `**NEVER** ...`) |
| Rule is topic-scoped AND the matching section does NOT exist | Ask: "No `## Code Style` section yet. Place inline (which will create the section) or in Boundaries?" |
| Rule is cross-cutting | Place in `## Boundaries` under the matched tier |

State the placement to the user:

```
Placement: inline in ## Git Workflow (topic-scoped autonomy rule)

  ## Git Workflow
  ...
  - **NEVER** force-push to main branches

Apply this edit? (y/n/move to Boundaries instead)
```

#### Step 3d: Apply

- If inline: append under the target section with the tier marker as a bold prefix.
- If cross-cutting: append under the matching sub-section in `## Boundaries`. If `## Boundaries` does not exist, create it with the three sub-sections, placed as the second-to-last section of the file (before `## References` if present).
- Never reorder or delete existing rules during add operations.

### Step 4: Restructure action (slash mode option 2)

When the user invokes `/refine-boundaries` and the existing `## Boundaries` section is malformed (flat list, wrong headers, missing tiers):

1. Parse the current section and classify each existing rule into Always / Ask / Never using Step 3b.
2. Present the proposed restructure side-by-side:
   ```
   Current (malformed):
     - Don't commit .env
     - Run tests before committing
     - Ask before opening PRs

   Proposed:
     ### Always do
     - Run tests before committing

     ### Ask first
     - Opening a PR

     ### Never do
     - Commit .env files
   ```
3. Ask to confirm. On confirm, rewrite the section.
4. Do not rewrite wording the user wrote; only re-tier and re-group.

### Step 5: Security density check (slash mode option 3)

1. Scan `## Boundaries > Never do` for rules with security-related keywords: `secret`, `credential`, `password`, `token`, `auth`, `env`, `encrypt`, `PII`, `permission`, `sudo`, `root`, `admin`.
2. If 5 or more rules match, ask:
   ```
   Found 6 security-related rules in ## Boundaries > Never do.

   Consider extracting these into a dedicated ## Security section for
   visibility. This is a judgment call — small projects are fine with
   inline, but security-sensitive projects (auth, payment, PII) benefit
   from a named section.

   Extract? (y/n)
   ```
3. On confirm, move matched rules to a new `## Security` section placed immediately before `## Boundaries`. Keep a pointer in the original tier: `- (See ## Security)`.

## Interaction with other skills

- **`/init-public-rules`** does not create `## Boundaries`. It's created lazily by this skill on first add. Newly initialized projects have no Boundaries section until the user accumulates rules.
- **`/audit-rules`** runs S4 (missing Boundaries) at Low severity and suggests running this skill. It also runs A6 (malformed Boundaries) at Medium and suggests Step 4 (restructure).
- **`/git-workflow`** may place its own `**NEVER** force-push` style rules inline in `## Git Workflow`. Those stay there — this skill does not migrate them into Boundaries. The inline placement is deliberate (topic-scoped).
- **`/work-unit-ritual`** may add gate rules to `## Boundaries` during its one-time setup (e.g., "Ask first: closing an issue", "Never do: close an issue without reflecting implementation changes"). Those are cross-cutting by nature and live in this skill's territory.

## Prohibited actions

- Never remove existing rules without explicit user request (this skill is additive — users prune by hand)
- Never rewrite user-authored rule wording (only re-tier/re-group on restructure)
- Never flatten the 3-tier structure — always preserve Always/Ask/Never as named sub-sections
- Never batch-add multiple rules in one run (one rule per invocation keeps classification deliberate)
