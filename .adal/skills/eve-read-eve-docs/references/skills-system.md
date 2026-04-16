# Skills System

## Use When
- You need to install, update, or reason about skill availability and resolution order.
- You need pack structure or SKILL discovery conventions across org projects.
- You need to control which skills are loaded for agents, CI, or repo clones.

## Load Next
- `references/agents-teams.md` for team/agent workflows that consume skills.
- `references/overview.md` for environment context and architecture assumptions.
- `references/cli.md` for install and resolve commands.

## Ask If Missing
- Confirm whether installation is local, repository-scoped, or organization-scoped.
- Confirm preferred source (`skills.txt` local path vs remote URL).
- Confirm whether you are using pack lockfile mode via `x-eve.packs`.

Eve Horizon installs skills via the `skills` CLI. Skills follow the OpenSkills
SKILL.md format: YAML frontmatter for metadata, imperative instructions in the
body, and optional bundled resources. Install happens at clone time from a
manifest into `.agents/skills/`.

## SKILL.md Format

```yaml
---
name: my-skill          # Required. Hyphen-case identifier.
description: One-line summary of what this skill does
---
```

Write the body in imperative form ("Check the config", not "You should check").
Keep SKILL.md under 5,000 words. Move detailed content to `references/`.

Progressive disclosure layers:
- **Metadata** (name, description) -- always available for discovery
- **Body** (SKILL.md instructions) -- loaded when the skill is invoked
- **Resources** (`references/`, `scripts/`, `assets/`) -- loaded on demand

| Resource dir | Purpose | Loaded |
|--------------|---------|--------|
| `references/` | Detailed documentation, guides | On demand |
| `scripts/` | Executable utilities | Never (executed via CLI) |
| `assets/` | Templates, images, configs | Never (used by scripts) |

## Pack Structure

Skills are grouped into **packs** -- directories of related skills. The public
eve-skillpacks repo ships three packs:

```
eve-skillpacks/
├── eve-work/                  # Productive work patterns
│   ├── README.md
│   ├── eve-orchestration/     # Parallel decomposition, job relations
│   ├── eve-job-lifecycle/     # Job states, completion, failure
│   ├── eve-job-debugging/     # Diagnosing stuck/failed jobs
│   ├── eve-read-eve-docs/     # Platform reference lookup
│   └── eve-skill-distillation/
├── eve-se/                    # Platform-specific engineering
│   ├── README.md
│   ├── eve-manifest-authoring/
│   ├── eve-deploy-debugging/
│   ├── eve-pipelines-workflows/
│   └── ...                    # auth, bootstrap, CLI, troubleshooting
├── eve-design/                # Architecture & design thinking
│   ├── README.md
│   └── eve-agent-native-design/
└── ARCHITECTURE.md
```

Each pack includes a `README.md` covering purpose, skills, audience, and
installation instructions.

## Installing Skills

### skills.txt (Legacy)

One source per line. Blank lines and `#` comments are ignored. Always prefix
local paths with `./`, `../`, `/`, or `~` to distinguish from `org/repo`.

```txt
./skillpacks/my-pack/*                   # All skills in a local pack
./skillpacks/my-pack/specific-skill      # One specific skill
https://github.com/incept5/eve-skillpacks  # Remote source
```

Run `./bin/eh skills install` to read the manifest, install each source into
`.agents/skills/`, and symlink `.claude/skills` -> `.agents/skills/`.

### AgentPacks (Preferred)

Declare packs in `.eve/manifest.yaml` under `x-eve.packs` for reproducible,
lockfile-based installation:

```yaml
x-eve:
  packs:
    - source: github.com/incept5/eve-skillpacks
      packs: [eve-work, eve-se]
```

Commands:

```bash
eve packs status              # Show current pack state
eve packs resolve --dry-run   # Preview resolution without writing lockfile
eve agents sync               # Resolve and write packs.lock.yaml
```

The lockfile `.eve/packs.lock.yaml` pins exact versions. To migrate from
`skills.txt`, run `eve migrate skills-to-packs`, review the output, merge it
into `.eve/manifest.yaml`, and remove `skills.txt`.

## Glob Pattern Syntax

| Pattern | Meaning | Example |
|---------|---------|---------|
| `./path/*` | All direct child skills | `./skillpacks/my-pack/*` |
| `./path/**` | All nested skills recursively | `./skillpacks/**` |
| `./path/skill` | Single specific skill | `./skillpacks/my-pack/my-skill` |

The installer expands globs, finds directories containing `SKILL.md`, and
installs each. The directory name becomes the skill identifier.

## Worker-Side Installation

The worker runs `.eve/hooks/on-clone.sh` after cloning a fresh workspace:

1. Prefer `./bin/eh skills install` when the project provides it
2. Skip install if `.agent/skills` is already tracked in the repo
3. Fall back to `eve-skills install` (minimal helper bundled in worker images)

Install targets (`.agents/skills/`, `.claude/skills/`) are always gitignored.
Tracked sources live under repo-local pack paths, listed in `skills.txt` or
resolved from `packs.lock.yaml`.

## Skill Resolution and Loading

When `skill read <name>` is invoked, OpenSkills searches (first match wins):

1. `./.agents/skills/` (project universal)
2. `~/.agents/skills/` (global universal)
3. `./.claude/skills/` (project Claude-specific)
4. `~/.claude/skills/` (global Claude-specific)

Project skills shadow global skills with the same name. Output includes the
skill body and a base directory for resolving bundled resources.

## Naming Conventions

- Use **hyphen-case**: `my-skill`, not `mySkill` or `my_skill`
- Prefix domain-specific skills to avoid collisions: `eve-`, `team-`
- The directory name is the skill identifier -- choose it carefully

## Creating a Custom Skill Pack

**1. Create the pack and README:**

```bash
mkdir -p skillpacks/my-pack
# Write README.md with purpose, skills, audience, install instructions
```

**2. Add skills:**

```bash
mkdir -p skillpacks/my-pack/my-skill
cat > skillpacks/my-pack/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Handles X when user asks about Y
---
# My Skill

## When to Use
Load this skill when working on X.

## Instructions
To accomplish X:
1. Check configuration in `config/`
2. Apply patterns from references/patterns.md
3. Validate the output
EOF
```

**3. Register and install:**

For skills.txt, add `./skillpacks/my-pack/*`. For AgentPacks, add under
`x-eve.packs` and run `eve agents sync`.

**4. Commit:** Track pack sources and manifest. Never commit install targets.

## Best Practices

**Authoring:** Write in imperative form. Include a "When to Use" section so
agents self-select. Keep the body focused; push detail to `references/`.

**Organization:** Group by domain, not team. Keep packs cohesive. Always
include a README.

**Distribution:** Project-specific skills go in-repo (`skillpacks/`). Team
skills live in a shared Git repo. Personal skills install to `~/.agents/skills/`.

**Version control:** Commit pack sources and manifests. Gitignore install
targets (`.agents/skills/`, `.claude/skills/`).

## Examples

**Personal pack** -- `skills.txt`:
```txt
./skillpacks/personal/*
```

**Team pack via Git** -- `skills.txt`:
```txt
git@github.com:your-org/team-skills
```

**Mixed installation** -- `skills.txt`:
```txt
./skillpacks/my-pack/*                     # Local pack (all skills)
./skillpacks/another-pack/special-skill    # Single skill from another pack
https://github.com/incept5/eve-skillpacks  # Remote packs
```
