# grill-diff

Grill the diff. Specialists evaluate every finding internally — only high-value findings reach the user for discussion.

## How It Works

1. **Determine diff scope** — file scope and diff baseline are independent and combine freely.
2. **Gather context** — asks if there is a related spec or plan file.
3. **Read all changed files** — builds the full picture before starting.
4. **Review file by file** — interrogate every aspect of each change.
5. **Specialist filter** — every finding is evaluated by 3 specialists (detective, attacker, gatekeeper). Only confirmed or uncertain findings reach the user.
6. **Discuss** — surviving findings are presented one at a time, discussing until shared understanding.

## Usage

```
/grill-diff
```

Against a specific target:

```
/grill-diff against develop
```

Narrow to specific files:

```
/grill-diff src/auth.ts src/api.ts
/grill-diff against develop src/auth.ts
```

Review a pull request:

```
/grill-diff https://github.com/org/repo/pull/123
```

## Installation

```bash
npx skills add shihyuho/skills --skill grill-diff -g
```
