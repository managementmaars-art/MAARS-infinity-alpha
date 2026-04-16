# test-skill

Return a fixed verification message when the user asks whether LinkSoft Skills are working.

## Contents

- `SKILL.md`: core trigger and exact response instructions
- `evals/evals.json`: starter evaluation prompts for this skill

## What this skill covers

- questions asking whether LinkSoft Skills are working
- equivalent wording such as whether the skills system works
- minor misspellings or typos in that question
- returning one exact verification message with no extra text

## Validation notes

Before finalizing, validate that the skill is discoverable and installable:

```bash
npx skills add . --list
npx skills add . --skill test-skill
```
