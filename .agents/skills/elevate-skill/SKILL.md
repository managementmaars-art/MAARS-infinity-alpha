---
name: elevate-skill
description: Elevate a project-local skill to the shared ai-skills repo. Use when you want a project skill available in other repos.
---

## When to invoke
- User wants to share a project-local skill with other repos
- User says "elevate skill", "share this skill", "move skill to ai-skills"

## Steps

1. **Discover local skills**: List directories in `.claude/skills/` whose name is NOT a key in `skills-lock.json` (if it exists). These are locally-authored project skills.

2. **Ask which skill to elevate**: Present the list and let the user choose.

3. **Find ai-skills repo**: Use `$AI_SKILLS_REPO` if set, else try `~/projects/camacho/ai-skills`, else ask the user.

4. **Copy to ai-skills**:
   ```bash
   cp -r .claude/skills/<name> <ai-skills-path>/skills/<name>
   ```
   Verify the SKILL.md has correct frontmatter (`name` matches folder name).

5. **Commit + push in ai-skills**:
   ```bash
   cd <ai-skills-path>
   git add skills/<name>
   git commit -m "feat: add <name> skill"
   git push
   ```

6. **Remove local copy and install from repo**:
   ```bash
   rm -rf .claude/skills/<name>
   npx skills add <ai-skills-path> --skill <name> -a claude-code -y
   ```

7. **Commit in current project**:
   ```bash
   git add skills-lock.json .claude/skills/
   git commit -m "chore: elevate <name> skill to ai-skills"
   ```

## Discovery logic
```bash
# Local skills = dirs in .claude/skills/ NOT tracked by lockfile
if [ -f skills-lock.json ]; then
  LOCKED=$(python3 -c "import json; print(' '.join(json.load(open('skills-lock.json'))['skills'].keys()))")
fi
for dir in .claude/skills/*/; do
  name=$(basename "$dir")
  if ! echo "$LOCKED" | grep -qw "$name"; then
    echo "$name (local)"
  fi
done
```
