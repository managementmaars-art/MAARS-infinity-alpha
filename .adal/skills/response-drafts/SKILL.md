---
name: response-drafts
description: "Draft support response suggestions with tone matching, KB integration, and solution suggestions"
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# Response Drafts Skill

Generate AI-powered support response drafts with intelligent tone matching, knowledge base integration, and multiple solution options. Perfect for customer support teams using Zendesk, internal ticketing systems, or any support workflow.

## Features

- **Multiple Draft Options**: Get 2-3 different response options for each ticket
- **Tone Matching**: Automatic tone detection or manual selection (professional, empathetic, technical, casual, apologetic, confident)
- **KB Integration**: Automatically suggests relevant knowledge base articles
- **Template System**: Pre-built and custom templates for common scenarios
- **SQLite Storage**: Tracks all drafts, templates, and KB articles locally
- **Optional Zendesk Support**: Can be extended for Zendesk API integration

## Installation

```bash
cd skills/response-drafts
npm install
npm run build
```

## CLI Usage

### Check Health

```bash
node dist/cli.js health
```

### Generate Response Drafts

```bash
# Generate drafts for a ticket
node dist/cli.js generate TICKET-123 \
  --subject "Can't login to account" \
  --description "I'm getting an 'Invalid credentials' error when trying to login" \
  --priority high \
  --requester "John Doe"

# Force specific tone
node dist/cli.js generate TICKET-456 \
  --subject "Payment failed" \
  --description "My card was declined but I have funds" \
  --tone empathetic

# Generate more drafts
node dist/cli.js generate TICKET-789 \
  --subject "Feature request" \
  --description "Please add dark mode" \
  --count 3
```

### View Drafts

```bash
# List drafts for a specific ticket
node dist/cli.js drafts TICKET-123

# List all drafts
node dist/cli.js all-drafts --limit 20
```

### Manage Templates

```bash
# List all templates
node dist/cli.js templates

# Filter by category
node dist/cli.js templates --category resolution

# View specific template
node dist/cli.js template acknowledgment

# Apply template with variables
node dist/cli.js use-template acknowledgment \
  --vars '{"requesterName":"Jane","subject":"billing issue","agentName":"Support Team"}'

# Add custom template
node dist/cli.js add-template \
  --name "feature-request" \
  --category "product" \
  --tone "professional" \
  --content "Hi {{requesterName}},\n\nThank you for your suggestion about {{subject}}. We appreciate customer feedback and have logged this in our feature request tracker.\n\nBest regards,\n{{agentName}}"
```

### Knowledge Base Management

```bash
# List KB articles
node dist/cli.js kb

# Filter by category
node dist/cli.js kb --category billing

# Add KB article
node dist/cli.js kb-add \
  --id "kb-custom-001" \
  --title "How to Reset Password" \
  --content "Go to Settings > Security > Change Password" \
  --category account \
  --tags "password,reset,security"
```

### Statistics and Administration

```bash
# View usage statistics
node dist/cli.js stats

# List available tones
node dist/cli.js tones

# Mark draft as sent
node dist/cli.js send 42
```

## JavaScript/TypeScript API

### Initialize

```typescript
import { ResponseDraftsSkill, Ticket } from '@openclaw/response-drafts';

const skill = new ResponseDraftsSkill();
```

### Generate Response Drafts

```typescript
const ticket: Ticket = {
  id: 'TICKET-123',
  subject: 'Cannot access account',
  description: 'I forgot my password and reset email is not arriving',
  priority: 'high',
  requesterName: 'John Smith',
  tags: ['login', 'password']
};

const drafts = await skill.generateDrafts(ticket, {
  tone: 'empathetic',
  count: 3,
  includeKBArticles: true
});

for (const draft of drafts) {
  console.log(`Tone: ${draft.tone}`);
  console.log(`Confidence: ${draft.confidence}`);
  console.log(`Content:\n${draft.content}\n`);
  
  if (draft.kbArticles && draft.kbArticles.length > 0) {
    console.log('Related KB Articles:');
    draft.kbArticles.forEach(a => console.log(`  - ${a.title}`));
  }
}
```

### Work with Templates

```typescript
// Get all templates
const templates = await skill.getTemplates('resolution');

// Get specific template
const template = await skill.getTemplate('acknowledgment');
if (template) {
  // Apply with variables
  const response = skill.applyTemplate(template, {
    requesterName: 'Jane',
    subject: 'billing issue',
    agentName: 'Support Team'
  });
  console.log(response);
}

// Add custom template
const newTemplate = await skill.addTemplate({
  name: 'custom-response',
  category: 'product',
  content: 'Hi {{name}}, thanks for your feedback on {{topic}}.',
  tone: 'professional',
  tags: ['custom', 'feedback'],
  variables: ['name', 'topic']
});
```

### Knowledge Base Management

```typescript
// Add KB article
await skill.addKBArticle({
  id: 'kb-101',
  title: 'Two-Factor Authentication Setup',
  content: 'Go to Settings > Security > 2FA to enable.',
  category: 'security',
  tags: ['2fa', 'security', 'authentication']
});

// Get all articles
const articles = await skill.getKBArticles('security');

// Articles are automatically matched to tickets based on keywords
```

### Draft Management

```typescript
// Get drafts for a ticket
const drafts = await skill.getDraftsForTicket('TICKET-123');

// Get all drafts
const allDrafts = await skill.getAllDrafts(50);

// Mark as sent
await skill.markDraftAsSent(42);

// Get statistics
const stats = await skill.getStats();
console.log(`Total: ${stats.totalDrafts}, Sent: ${stats.sentDrafts}`);
```

### Health Check

```typescript
const health = await skill.healthCheck();
if (health.status === 'healthy') {
  console.log(health.message);
}
```

### Cleanup

```typescript
await skill.close();
```

## Available Tones

| Tone | Description | Best Used For |
|------|-------------|---------------|
| `professional` | Clear, business-appropriate language | General inquiries |
| `empathetic` | Shows understanding and compassion | Frustrated customers |
| `technical` | Precise, detailed explanations | Technical issues |
| `casual` | Friendly, conversational style | Informal interactions |
| `apologetic` | Acknowledges issues with regret | Service failures |
| `confident` | Assures resolution capability | Complex problems |

## Built-in Templates

| Template | Category | Description |
|----------|----------|-------------|
| `acknowledgment` | general | Initial response acknowledging receipt |
| `solution-provided` | resolution | Delivering a solution |
| `escalation` | escalation | Handing off to specialist team |
| `need-more-info` | follow-up | Requesting additional details |
| `apology` | general | Professional apology response |

## Database Schema

Data is stored in SQLite at `~/.openclaw/skills/response-drafts/drafts.db`:

### Tables

- **response_drafts** - Generated response drafts
  - `id`, `ticket_id`, `content`, `tone`, `kb_articles`, `confidence`, `created_at`, `was_sent`

- **response_templates** - Response templates
  - `id`, `name`, `category`, `content`, `tone`, `tags`, `variables`

- **kb_articles** - Knowledge base articles
  - `id`, `title`, `content`, `category`, `tags`, `url`

- **kb_mappings** - Keyword to article mappings
  - `id`, `keyword`, `article_id`, `relevance_score`

## Zendesk Integration (Optional)

This skill can be extended for Zendesk API integration:

```typescript
// Example: Fetch ticket from Zendesk and generate drafts
async function processZendeskTicket(ticketId: string) {
  // Fetch from Zendesk API
  const zdTicket = await fetchZendeskTicket(ticketId);
  
  const ticket: Ticket = {
    id: zdTicket.id,
    subject: zdTicket.subject,
    description: zdTicket.description,
    priority: zdTicket.priority,
    requesterName: zdTicket.requester.name,
    tags: zdTicket.tags
  };
  
  const drafts = await skill.generateDrafts(ticket);
  
  // Optionally add as Zendesk comments
  for (const draft of drafts) {
    await addZendeskComment(ticketId, draft.content);
  }
}
```

## Tone Detection

The skill automatically detects tone based on:

1. **Ticket priority** - Urgent → Empathetic
2. **Keywords** - "error", "bug" → Technical
3. **Sentiment** - "frustrated", "disappointed" → Apologetic
4. **Content** - "thank you", "great" → Casual

## KB Article Matching

Articles are matched based on:

1. Tag keywords in ticket content
2. Title word matches
3. Category relevance

Add more KB articles and mappings to improve suggestions.

## Error Handling

```typescript
try {
  const drafts = await skill.generateDrafts(ticket);
} catch (error) {
  if (error.message.includes('not initialized')) {
    console.log('Database error - check permissions');
  } else {
    console.error('Error:', error.message);
  }
}
```

## Testing

```bash
# Type checking
npm run typecheck

# Build
npm run build

# Health check
npm run cli -- health

# Generate test drafts
npm run cli -- generate TEST-001 \
  --subject "Test ticket" \
  --description "This is a test" \
  --requester "Test User"
```

## Troubleshooting

### "Database error"

Check that the data directory is writable:
```bash
ls -la ~/.openclaw/skills/response-drafts/
```

### "No KB articles found"

Add some KB articles:
```bash
node dist/cli.js kb-add --id "kb-001" --title "Help" --content "Content" --category general
```

## Dependencies

- `sqlite3`: Local database storage
- No external API dependencies by default

## Security Notes

- All data stored locally in SQLite
- No external API calls (except optional Zendesk extension)
- Templates and KB content are user-controlled
