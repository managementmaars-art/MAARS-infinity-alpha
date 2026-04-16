# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Convex Cloud (24/7)                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Database (Document Store)               │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐   │   │
│  │  │ scheduled_messages  │  │   message_history   │   │   │
│  │  │ - title             │  │ - title             │   │   │
│  │  │ - message_text      │  │ - message_text      │   │   │
│  │  │ - scheduled_time    │  │ - sent_at           │   │   │
│  │  │ - status            │  │ - status            │   │   │
│  │  │ - recurring         │  │ - error             │   │   │
│  │  │ - storage_id        │  │                     │   │   │
│  │  │ - file_name         │  │                     │   │   │
│  │  └─────────────────────┘  └─────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Cron Job (every minute)                    │   │
│  │  processScheduledMessages() → Telegram API           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Functions                          │   │
│  │  Queries:    listScheduled, viewHistory              │   │
│  │  Mutations:  scheduleMessage, cancelMessage          │   │
│  │  Actions:    sendMessage, processScheduledMessages   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                    ↑                    ↓
            ┌───────────────────────────────────────┐
            │       Client Scripts (Claude)         │
            │  send_message.ts, schedule_message.ts │
            │  list_scheduled.ts, cancel_message.ts │
            │  view_history.ts, setup.ts            │
            └───────────────────────────────────────┘
```

## Convex Cloud Components

### Database

| Table                | Purpose                        | Key Fields                                                                    |
| -------------------- | ------------------------------ | ----------------------------------------------------------------------------- |
| `scheduled_messages` | Pending and completed messages | title, message_text, scheduled_time, status, recurring, storage_id, file_name |
| `message_history`    | Full send history              | title, message_text, sent_at, status, error                                   |

Features:

- Document-based storage with automatic indexing
- ACID transactions with serializable isolation
- Real-time subscriptions (available but not used)

### Functions

| Type          | Purpose                          | Examples                                             |
| ------------- | -------------------------------- | ---------------------------------------------------- |
| **Queries**   | Read-only database operations    | `listScheduled`, `viewHistory`, `getPendingMessages` |
| **Mutations** | Read-write database transactions | `scheduleMessage`, `cancelMessage`, `markAsSent`     |
| **Actions**   | External API calls (Telegram)    | `sendMessage`, `processScheduledMessages`            |
| **Internal**  | Backend-only functions           | `getPendingMessages` (internalQuery)                 |

### Cron Job

Defined in `convex/crons.ts`:

- Runs every minute
- Queries for messages where `scheduled_time <= now` and `status == "pending"`
- Sends each via Telegram API
- Updates status to "sent" or "failed"
- For recurring messages: calculates and schedules next occurrence

## Local Components

### Client Scripts (`scripts/`)

| Script                | Purpose                              |
| --------------------- | ------------------------------------ |
| `setup.ts`            | Initial deployment and configuration |
| `send_message.ts`     | Send immediate messages              |
| `schedule_message.ts` | Schedule future messages             |
| `list_scheduled.ts`   | List pending messages                |
| `cancel_message.ts`   | Cancel scheduled messages            |
| `view_history.ts`     | View message history                 |

Scripts connect to Convex via HTTP using the deployment URL derived from the deploy key.

### Configuration

Stored at `/mnt/user-data/outputs/telegram_config.json`:

```json
{
  "bot_token": "123456:ABC...",
  "user_id": "123456789",
  "deploy_key": "prod:deployment|key..."
}
```

Persists across sessions for seamless operation.

## Message Flow

### Immediate Send

```
User Request → send_message.ts → Convex Action → Telegram API → User
```

### Scheduled Send

```
User Request → schedule_message.ts → Convex Mutation → Database
                                                          ↓
User ← Telegram API ← Convex Action ← Cron Job (every min) ←
```

### Recurring Messages

```
Cron Job → Send Message → Calculate Next Time → Create New Record
              ↓                                        ↓
         message_history                    scheduled_messages
```

## File Structure

```
telegram-reminders/
├── convex/                    # Backend (Convex Cloud)
│   ├── schema.ts             # Database schema definition
│   ├── messages.ts           # Queries and mutations
│   ├── telegram.ts           # Actions (Telegram API calls)
│   ├── crons.ts              # Cron job definition
│   └── tsconfig.json         # Convex TypeScript config
├── scripts/                   # Client scripts (local)
│   ├── setup.ts              # Initial setup + deploy
│   ├── send_message.ts       # Send immediately
│   ├── schedule_message.ts   # Schedule message
│   ├── list_scheduled.ts     # List scheduled
│   ├── cancel_message.ts     # Cancel message
│   └── view_history.ts       # View history
├── references/                # Documentation
│   ├── architecture.md       # This file
│   ├── convex.md             # Convex platform reference
│   ├── telegram_api.md       # Telegram API reference
│   ├── initial_setup.md      # Setup guide
│   └── error_handling.md     # Troubleshooting guide
├── package.json              # Dependencies and scripts
└── tsconfig.json             # Root TypeScript config
```

## Security & Privacy

| Aspect            | Implementation                                   |
| ----------------- | ------------------------------------------------ |
| Bot token         | Stored encrypted in Convex environment variables |
| Deploy key        | Stored in local config file                      |
| Communication     | All HTTPS                                        |
| Platform security | Convex enterprise-grade infrastructure           |

**Never share**: bot token, user ID, or deploy key publicly.

## Dependencies

### Root Package

- `convex` - Convex client library
- `chrono-node` - Natural language time parsing
- `form-data` - File uploads to Telegram
- `tsx` - TypeScript execution runtime
- `undici` - HTTP client
- `typescript` - TypeScript compiler
- `@types/node` - Node.js type definitions

### Convex Backend

- TypeScript functions compiled automatically by Convex
- No additional dependencies required
