# Convex Reference

## Overview

Convex is a backend-as-a-service platform providing:

- **Reactive Database**: Real-time, document-relational database
- **Serverless Functions**: TypeScript/JavaScript functions in the cloud
- **Scheduled Jobs**: Cron jobs and scheduled functions
- **Zero Infrastructure**: No server management or connection strings

## Quick Reference

| Feature    | Description                                                |
| ---------- | ---------------------------------------------------------- |
| Database   | Document-based, ACID transactions, automatic indexing      |
| Functions  | Queries (read), Mutations (write), Actions (external APIs) |
| Scheduling | Cron jobs + dynamic scheduling                             |
| Deployment | `npx convex deploy` with deploy key                        |
| Dashboard  | [dashboard.convex.dev](https://dashboard.convex.dev)       |

## Function Types

| Type         | Purpose        | Can Call External APIs | Database Access |
| ------------ | -------------- | ---------------------- | --------------- |
| **Query**    | Read data      | ❌                     | Read-only       |
| **Mutation** | Write data     | ❌                     | Read-write      |
| **Action**   | External calls | ✅                     | Via mutations   |
| **Internal** | Backend-only   | Depends on type        | Depends on type |

### Example Usage

```typescript
// Query - read-only
export const listScheduled = query({
  handler: async (ctx) => {
    return await ctx.db.query('scheduled_messages').collect();
  },
});

// Mutation - read-write
export const scheduleMessage = mutation({
  args: { title: v.string(), scheduled_time: v.number() },
  handler: async (ctx, args) => {
    return await ctx.db.insert('scheduled_messages', args);
  },
});

// Action - external API calls
export const sendMessage = action({
  args: { text: v.string() },
  handler: async (ctx, args) => {
    await fetch('https://api.telegram.org/...');
  },
});
```

## Scheduling

### Cron Jobs (Static)

Defined in `convex/crons.ts`:

```typescript
import { cronJobs } from 'convex/server';

const crons = cronJobs();
crons.interval(
  'process-messages',
  { minutes: 1 },
  internal.telegram.processScheduledMessages
);
export default crons;
```

### Dynamic Scheduling

Schedule functions from other functions:

```typescript
await ctx.scheduler.runAfter(delay, internal.myFunction, args);
```

## Deployment

### Deploy Key Setup

```bash
# Set environment variable
export CONVEX_DEPLOY_KEY="prod:deployment-name|key..."

# Deploy
npx convex deploy
```

Deploy keys grant permission to:

- Push code and update schema
- Set environment variables
- View logs and dashboard

### Environment Variables

```bash
# Set variables
npx convex env set TELEGRAM_BOT_TOKEN "123456:ABC..."
npx convex env set TELEGRAM_USER_ID "123456789"

# List variables
npx convex env list

# Remove variable
npx convex env unset VARIABLE_NAME
```

Access in functions: `process.env.VARIABLE_NAME`

### Deployment URL

Derived from deploy key:

- Key: `prod:deployment-name|secret...`
- URL: `https://deployment-name.convex.cloud`

## Dashboard

Access at [dashboard.convex.dev](https://dashboard.convex.dev):

| Section       | Purpose                            |
| ------------- | ---------------------------------- |
| **Data**      | View/edit database tables          |
| **Functions** | See function definitions and logs  |
| **Logs**      | Real-time execution logs           |
| **Crons**     | Monitor cron job runs              |
| **Settings**  | Deploy keys, environment variables |

## Free Tier

| Resource            | Limit        |
| ------------------- | ------------ |
| Database storage    | Unlimited    |
| Function executions | Unlimited    |
| Bandwidth           | Unlimited    |
| Credit card         | Not required |
| Time limit          | None         |

Perfect for personal projects and small-scale use.

## CLI Commands

```bash
# Deploy to cloud
npx convex deploy

# View logs
npx convex logs
npx convex logs --watch  # Real-time

# Environment variables
npx convex env list
npx convex env set KEY "value"
npx convex env unset KEY

# Development (local)
npx convex dev
```

## Resources

- **Documentation**: [docs.convex.dev](https://docs.convex.dev)
- **Dashboard**: [dashboard.convex.dev](https://dashboard.convex.dev)
- **Status**: [status.convex.dev](https://status.convex.dev)
- **Examples**: [github.com/get-convex/convex-demos](https://github.com/get-convex/convex-demos)
