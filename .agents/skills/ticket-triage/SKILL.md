---
name: ticket-triage
description: AI-powered support ticket classification and triage system
version: 1.0.0
author: OpenClaw
entrypoint:
  type: module
  module: ./dist/index.js
  export: TicketTriageSkill
---

# Ticket Triage Skill

AI-powered support ticket classification system that automatically categorizes, prioritizes, and routes support tickets.

## Features

- Priority classification (critical, high, medium, low)
- Category detection (bug, feature_request, question, complaint, billing, technical, account, other)
- Auto-assignment based on category and workload
- Spam filtering with confidence scoring
- SQLite storage for classification history
- Rule-based overrides for known patterns

## Usage

```typescript
import { TicketTriageSkill } from '@openclaw/ticket-triage';

const triage = new TicketTriageSkill();

// Classify a ticket
const classification = await triage.classify({
  id: 'TICKET-001',
  subject: 'Unable to login to my account',
  body: 'I keep getting an error when trying to login...',
  from: 'customer@example.com',
  createdAt: new Date()
});

// Get classification results
console.log(classification.category);    // 'technical'
console.log(classification.priority);    // 'high'
console.log(classification.confidence);  // 0.85
console.log(classification.assignedTo);  // 'tech-team'

await triage.close();
```

## CLI

```bash
# Classify a ticket
ticket-triage classify --subject "Login error" --body "Cannot access account"

# List tickets by category
ticket-triage category bug

# List tickets by priority
ticket-triage priority critical

# Add classification rule
ticket-triage add-rule --pattern "billing" --category billing --priority high

# View statistics
ticket-triage stats
```

## Configuration

No external API dependencies. Uses local AI classification algorithms.
