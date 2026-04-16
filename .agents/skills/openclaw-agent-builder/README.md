# OpenClaw Agent Builder Skill

Build specialized openclaw agents with complete workspace structure, identity, and skills.

## Quick Start

1. **Ask clarifying questions** about agent purpose, style, and requirements
2. **Create workspace directory**: `~/.openclaw/workspace-<agent-name>`
3. **Build core files**: IDENTITY.md, SOUL.md, AGENTS.md, USER.md, TOOLS.md
4. **Add skills** (optional): Create `skills/` directory with SKILL.md files
5. **Setup memory**: Create `memory/` directory
6. **Register agent**: Add to openclaw config
7. **Configure routing**: Set up bindings if multi-agent

## Templates Available

- `templates/IDENTITY-template.md` - Agent identity structure
- `templates/SOUL-template.md` - Personality and expertise
- `templates/AGENTS-template.md` - Operating instructions

## Design Principles

1. **Single focus** - One agent, one purpose
2. **Clear identity** - Distinct personality and expertise
3. **Concise by default** - Professional, direct communication
4. **Skill-equipped** - Capabilities through workspace skills

## Examples

See real agents:
- `~/.openclaw/workspace-android-spec-agent` - Spec generator
- `~/.openclaw/workspace-seo-expert` - SEO specialist
- `~/.openclaw/workspace-beet-agent` - Domain-specific agent

## Resources

- [OpenClaw Docs](https://docs.openclaw.org/)
- [AgentSkills.io](https://agentskills.io/)
- [Skills.sh](https://skills.sh/)
