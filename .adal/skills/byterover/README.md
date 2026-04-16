# ByteRover Skill for OpenClaw

ByteRover CLI for OpenClaw - Context engineering platform to manage project knowledge, decisions, and patterns with AI coding agents.

## About

ByteRover is a context engineering platform that eliminates memory fragmentation by:
- 📚 **Curating context** - Patterns, decisions, and learnings from your projects
- 🤖 **AI agent integration** - Works with 19+ AI coding agents
- 🔄 **Auto-sync** - Context syncs across team members automatically
- 🚫 **No markdown clutter** - Zero manual context management files

This skill uses Docker to run ByteRover CLI in an isolated environment, making it work even in headless server environments.

## Why ByteRover?

**Prevent Memory Fragmentation:**
- Centralized knowledge base instead of scattered markdown files
- Structured context tree (architecture, testing, deployment patterns)
- Query-based retrieval instead of file searching

**Team Collaboration:**
- Shared context across all team members
- Agents work with the same knowledge base
- No more "knowledge silos"

**Zero Maintenance:**
- No manual markdown file management
- Automatic organization and tagging
- Always synced and up-to-date

## Installation

### Prerequisites

- Docker
- Docker Compose
- ByteRover account with team and space

### Setup

1. Copy this skill directory to your OpenClaw workspace:
   ```bash
   cp -r byterover ~/.openclaw/workspace/skills/
   ```

2. Create the API configuration file:
   ```bash
   cat > ~/.clawdbot/byterover-config.json << 'EOF'
   {
     "apiKey": "your_byterover_api_key_here",
     "team": "your_team_name",
     "space": "your_space_name"
   }
   EOF
   ```

3. Build and start the Docker container:
   ```bash
   cd ~/.openclaw/workspace/skills/byterover
   docker-compose build
   docker-compose up -d
   ```

## Usage

The skill provides Bash helper scripts for common operations:

### Check Status
```bash
~/.openclaw/workspace/skills/byterover/scripts/status.sh
```

### Query Context
```bash
~/.openclaw/workspace/skills/byterover/scripts/query.sh "What are the testing strategies?"
```

### Add Context
```bash
~/.openclaw/workspace/skills/byterover/scripts/curate.sh "Document the API authentication patterns"
```

### Sync Changes
```bash
~/.openclaw/workspace/skills/byterover/scripts/sync.sh
```

## Docker Commands

### Direct Docker Usage

**Login with API Key:**
```bash
cd ~/.openclaw/workspace/skills/byterover
BRV_API_KEY=your_key docker-compose exec byterover brv login --api-key $BRV_API_KEY
```

**Initialize Project:**
```bash
docker-compose exec byterover brv init --headless --team "MyTeam" --space "MySpace"
```

**Query Knowledge:**
```bash
docker-compose exec byterover brv query "How do we handle authentication?" --headless
```

**Add Context:**
```bash
docker-compose exec byterover brv curate "Document rate limiting strategy" --headless
```

**Sync with Remote:**
```bash
docker-compose exec byterover brv pull --headless  # Pull latest
docker-compose exec byterover brv push --headless  # Push local changes
```

### Container Management

**View logs:**
```bash
cd ~/.openclaw/workspace/skills/byterover
docker-compose logs -f byterover
```

**Stop container:**
```bash
docker-compose down
```

**Restart container:**
```bash
docker-compose restart
```

**Enter container shell:**
```bash
docker-compose exec byterover bash
```

## Context Tree Structure

ByteRover organizes knowledge into structured domains:

- **Structure** - Project architecture and design patterns
- **Database** - Schema, migrations, relationships
- **Backend** - API endpoints, business logic
- **Frontend** - UI components, state management
- **Testing** - Test strategies, fixtures, patterns
- **Deployment** - Infrastructure, CI/CD
- **Documentation** - Guides, API docs

## Use Cases

### For AI Coding Agents

**Example prompt to Claude Code:**
> Use brv query to check what authentication patterns are used in this project

**Agent executes:**
```bash
brv query "What authentication patterns are used?" --headless --format json
```

### For Developers

**Check project architecture:**
```bash
~/.openclaw/workspace/skills/byterover/scripts/query.sh "What is the project architecture?"
```

**Add decision documentation:**
```bash
~/.openclaw/workspace/skills/byterover/scripts/curate.sh "We chose PostgreSQL over MongoDB for relational data requirements"
```

**Review testing strategies:**
```bash
~/.openclaw/workspace/skills/byterover/scripts/query.sh "What are our testing strategies?"
```

## Configuration

Configuration is stored in `~/.clawdbot/byterover-config.json`:

```json
{
  "apiKey": "your_api_key_here",
  "team": "your_team_name",
  "space": "your_space_name"
}
```

### Environment Variables

- `BRV_API_KEY` - ByteRover API key
- `BRV_TEAM` - Team name
- `BRV_SPACE` - Space name
- `BRV_HEADLESS` - Enable headless mode
- `BRV_FORMAT` - Output format (json/text)

## Headless Mode

ByteRover CLI supports headless mode for automation:
- No interactive prompts
- Machine-readable JSON output
- CI/CD friendly
- Perfect for OpenClaw automation

**Supported commands:**
- `brv init` --headless --team X --space Y
- `brv status` --headless
- `brv query` --headless
- `brv curate` --headless
- `brv push` --headless
- `brv pull` --headless

## Integration with AI Agents

ByteRover works with 19+ AI coding agents:

### Modern Integration
- **Claude Code** - Skill files
- **Cursor** - Skill files
- **Windsurf** - MCP tools

### Legacy Integration
- **GitHub Copilot** - Rule-based
- **Tabnine** - MCP tools
- **Continue** - MCP tools

## Docker Architecture

**Why Docker?**

ByteRover CLI requires:
- Node.js 20+
- libsecret for credential storage
- Python for native dependencies
- Desktop environment for OAuth

**Docker Solution:**
- Isolated environment with all dependencies
- Works on headless servers
- No OAuth required (API key auth)
- Persistent credential storage

**Dockerfile includes:**
- Node.js 20 base image
- Build tools for native modules
- libsecret for credential storage
- ByteRover CLI pre-installed

## Troubleshooting

**Container won't start:**
```bash
# Check if port is available
docker-compose ps
# View logs
docker-compose logs
```

**Build fails:**
```bash
# Rebuild without cache
docker-compose build --no-cache
```

**Login fails:**
```bash
# Verify API key
cat ~/.clawdbot/byterover-config.json | jq '.apiKey'
# Check team/space names
```

**No context returned:**
```bash
# Initialize project
docker-compose exec byterover brv init --headless --team "Team" --space "Space"
# Pull latest context
docker-compose exec byterover brv pull --headless
```

## Requirements

- Docker
- Docker Compose
- ByteRover account
- Active team and space

## License

MIT

## Author

Created for OpenClaw by Jun Suzuki

---

For more information about ByteRover, visit: https://docs.byterover.dev/
