---
name: shipp
description: >
  Shipp is a real-time data connector. Use it to fetch authoritative, changing
  external data (e.g., sports schedules, live events) via the Shipp API.

metadata:
  author: Outsharp Inc.
  version: 0.3.0

compatibility:
  requirements:
    - Internet access
    - Shipp API Key (Get from https://platform.shipp.ai)
  notes:
    - All endpoints require authorization via API key.
    - Requests and responses are JSON.
    - If the Shipp CLI (`shipp`) is available in PATH, prefer it over curl for API interactions. If not installed, recommend installing it.

allowed-tools:
  - Bash(curl:https://docs.shipp.ai/*)
  - Bash(curl:https://shipp.ai/*)
  - Bash(curl:https://api.shipp.ai/*)
  - Bash(curl:https://platform.shipp.ai/*)
  - Bash(curl:https://markdown.new/docs.shipp.ai/*)
  - Bash(curl:https://gitlab.com/outsharp/shipp/cli/*)
  - Bash(jq:*)
  - Bash(shipp:*)

---

# Shipp API

[Shipp.ai](https://shipp.ai) is the real-time data connector for AI builders.

[Create an API Key](https://platform.shipp.ai)

Implement as many tests as possible as soon as possible.
Verify data and how the app uses data.
Be flexible in schema — event rows are schema-flexible JSON and fields vary by sport, feed, and event.

Base URL: `https://api.shipp.ai/api/v1`

---

## Sitemap & Documentation Index

If docs change or you need the latest page list, fetch the sitemap:

```
curl -sL "https://markdown.new/docs.shipp.ai/sitemap.xml"
```

To read any doc page as clean markdown:

```
curl -sL "https://markdown.new/docs.shipp.ai/<path>"
```

### Full Sitemap

| Page | markdown.new URL |
|---|---|
| Getting Started | https://markdown.new/docs.shipp.ai/ |
| Setup Instructions | https://markdown.new/docs.shipp.ai/instructions/setup/ |
| Test Your Connection | https://markdown.new/docs.shipp.ai/instructions/test/ |
| Shipp Your Product | https://markdown.new/docs.shipp.ai/instructions/shipp/ |
| How to Shipp | https://markdown.new/docs.shipp.ai/how-to/ |
| API Reference | https://markdown.new/docs.shipp.ai/api-reference/ |
| Create Connection | https://markdown.new/docs.shipp.ai/api-reference/connections-create/ |
| List Connections | https://markdown.new/docs.shipp.ai/api-reference/connections-list/ |
| Run Connection | https://markdown.new/docs.shipp.ai/api-reference/connections-run/ |
| Sport Schedule | https://markdown.new/docs.shipp.ai/api-reference/sport-schedule/ |
| Data Shape | https://markdown.new/docs.shipp.ai/api-reference/connections-run-data-shape/ |
| Error Format | https://markdown.new/docs.shipp.ai/api-reference/error-format/ |
| Usage Tips | https://markdown.new/docs.shipp.ai/api-reference/usage-tips/ |
| Versioning | https://markdown.new/docs.shipp.ai/api-reference/versioning/ |
| x402 Payments | https://markdown.new/docs.shipp.ai/api-reference/x402/ |
| Platform Guides | https://markdown.new/docs.shipp.ai/platform-guides/ |
| Lovable Guide | https://markdown.new/docs.shipp.ai/platform-guides/lovable/ |
| Base44 Guide | https://markdown.new/docs.shipp.ai/platform-guides/base44/ |
| Claude Code Guide | https://markdown.new/docs.shipp.ai/platform-guides/claude-code/ |
| Blink Guide | https://markdown.new/docs.shipp.ai/platform-guides/blink/ |
| Replit Guide | https://markdown.new/docs.shipp.ai/platform-guides/replit/ |

---

## Getting Started

Shipp enables a faster way to create connections to real-time data. It's cost-effective, fast to run, and easy to start.

1. Sign up on [Shipp](https://platform.shipp.ai)
2. Paste your API key into your favorite AI builder. See [Platform Guides](https://markdown.new/docs.shipp.ai/platform-guides/)
3. Shipp works with your AI builder to provide the live data your app needs

Following the instructions ([Setup](https://markdown.new/docs.shipp.ai/instructions/setup/), [Test](https://markdown.new/docs.shipp.ai/instructions/test/), [Shipp](https://markdown.new/docs.shipp.ai/instructions/shipp/)) is the best way to create your first Connection.

### Available Data

- **Sports:** NBA, NFL, NCAA Football, MLB, Soccer (Multiple Leagues)
- News, Financials, Travel, Shopping, Social, Prediction Markets, Weather — coming soon

---

## Authentication

All endpoints require an API key. The API supports several methods:

| Method | Example |
|---|---|
| Query parameter `api_key` | `?api_key=YOUR_API_KEY` |
| Query parameter `apikey` | `?apikey=YOUR_API_KEY` |
| `Authorization` header (Bearer) | `Authorization: Bearer YOUR_API_KEY` |
| `Authorization` header (Basic) | `Authorization: Basic base64(:YOUR_API_KEY)` |
| `X-API-Key` header | `X-API-Key: YOUR_API_KEY` |
| `User-API-Key` header | `User-API-Key: YOUR_API_KEY` |
| `API-Key` header | `API-Key: YOUR_API_KEY` |

Pick whichever method works best for your client.

---

## Endpoints

### `POST /api/v1/connections/create`

Create a new **raw-data connection** by providing natural-language `filter_instructions` that describe what games, teams, sports, or events you want to track.

**Request body:**

```json
{
  "filter_instructions": "string (required)"
}
```

**Response (200):**

```json
{
  "connection_id": "01KFXTX1WDQ68A1GS77T1XJ5YB",
  "enabled": true,
  "name": "string",
  "description": "string"
}
```

**Errors:** 400 (invalid JSON, empty body, missing `filter_instructions`), 500

Use at build time — there is time and credit overhead. Store and reuse the returned `connection_id`.

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/connections-create/)

---

### `POST /api/v1/connections/{connection_id}`

Run a connection and return **raw event data**.

**Path params:** `connection_id` (required, ULID)

**Body params (all optional):**

- `since` (string, ISO 8601): reference time to pull from. Default: 48 hours ago
- `limit` (int): max events to return. Default: 100
- `since_event_id` (ULID): last event id received — only returns newer events. Causes events to be ordered asc by `wall_clock_start`

**Response (200):**

```json
{
  "connection_id": "01KFXTX1WDQ68A1GS77T1XJ5YB",
  "data": [
    { "any": "shape varies by feed + event data availability" }
  ]
}
```

**Errors:** 400 (missing/invalid `connection_id`, over limit / not authorized), 500

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/connections-run/)

---

### `GET /api/v1/connections`

List all connections in the current org scope. Free to call.

**Response (200):**

```json
{
  "connections": [
    {
      "connection_id": "01KFXTX1WDQ68A1GS77T1XJ5YB",
      "enabled": true,
      "name": "string (optional)",
      "description": "string (optional)"
    }
  ]
}
```

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/connections-list/)

---

### `GET /api/v1/sports/{sport}/schedule`

Get upcoming and recent games (past 24 hours through next 7 days).

**Path params:** `sport` (required) — e.g. `nba`, `nfl`, `mlb`, `ncaafb`, `soccer` (case-insensitive)

**Response (200):**

```json
{
  "schedule": [
    {
      "sport": "Soccer",
      "game_status": "live",
      "game_id": "01KGREKH8PXFV8AHA4Q9H2Z68F",
      "scheduled": "2026-02-06T15:00:00Z",
      "home": "Al-Ittifaq FC",
      "home_team_players": null,
      "away": "Damac FC",
      "away_team_players": null
    }
  ]
}
```

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/sport-schedule/)

---

### `POST /api/v1/connections/inline` (x402)

Create and run a connection in one step, paid via x402 — **no API key required**. Requires a crypto wallet funded with USDC on Base.

**Body params:**

- `filter_instructions` (string, required)
- `since` (string, ISO 8601, optional)
- `limit` (int, optional)
- `since_event_id` (ULID, optional)

**Flow:**

1. Agent sends request — gets `402 Payment Required` with pricing details
2. Agent signs payment with funded wallet
3. Agent retries with `PAYMENT-SIGNATURE` header
4. Server returns data (same shape as Run Connection)

Use an x402-compatible library (`x402-fetch`, Coinbase SDK) to handle the 402 → pay → retry loop automatically.

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/x402/)

---

## Data Shape

Each element of `data[]` is a schema-flexible JSON object. Fields vary by sport, feed, and event.

**Identifiers:** `game_id`, `home_id`, `away_id`, `attribution_id`, `posession_id`

**Text / enums:** `sport`, `home_name`, `away_name`, `game_clock`, `game_period_sub`, `desc`, `type`, `category`, `score_method`, `score_missed_outcome`

**Numeric:** `home_points`, `away_points`, `game_period`, `game_num`, `down`, `yards_first_down`, `location_yard_line`, `injury_time_minutes`

**Time:** `wall_clock_start`, `wall_clock_end`

**Booleans:** `fake_punt`, `fake_field_goal`, `screen_pass`, `play_action`, `run_pass_options`

Not every row has every field. Treat every field as optional. Agents and clients should be defensive and handle missing keys.

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/connections-run-data-shape/)

---

## Error Format

Errors are returned as JSON:

```json
{
  "error": "string",
  "status": 400
}
```

| Status | Meaning |
|---|---|
| 400 | Invalid request — check JSON and required fields |
| 401 | Missing or invalid API key |
| 402 | Billing changes required — manage at https://platform.shipp.ai/billing |
| 403 | API key lacks access to this resource |
| 404 | Connection not found or doesn't belong to your org |
| 429 | Rate-limited — retry with backoff |
| 5xx | Server error — retry later or contact support@shipp.ai |

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/error-format/)

---

## How to Shipp — Integration Pattern

> [Full guide](https://markdown.new/docs.shipp.ai/how-to/)

### Mental Model

Shipp "Connections" = reusable live-data queries. You **create** a connection with `filter_instructions` in plain English, then **run** it to retrieve raw event data in a schema-flexible `data[]` array.

### Step-by-Step

1. **Write a "Real-Time Contract"** for one screen — define: user promise, triggering events, data shape needed, freshness window, failure mode.

2. **Translate the contract into `filter_instructions`** — keep them short, explicit, testable, scoped. Include the domain (e.g., "NBA"), scope to an entity/time, and name what you want surfaced.

3. **Create a Connection once, store the `connection_id`** — don't create per-run. Saves time, cost, and stability.

4. **Run the Connection to fetch updates** — use pull-based polling:
   - On page load: run with a reasonable `since`
   - On interval (5–30s): re-run with `since_event_id` set to the most recent event
   - Merge/dedupe events into UI state

5. **Handle schema-flexible `data[]` defensively** — treat every field as optional, prefer safe access, log unknown shapes.

6. **Deduplicate, order, and reconcile** — keep a rolling set of seen event IDs, order by timestamp or ID (lexicographically stable), send the largest event ID as `since_event_id`.

### Sports-Specific Helper

Use the [schedule endpoint](https://markdown.new/docs.shipp.ai/api-reference/sport-schedule/) to discover current games. Use game context to craft `filter_instructions` and create connections.

---

## Setup Instructions

> [Full docs](https://markdown.new/docs.shipp.ai/instructions/setup/)

1. **Create a connection:** POST to `/api/v1/connections/create` with `filter_instructions` describing desired data (e.g., "Track all NBA games today and include scoring and play-by-play context")
2. **Store the `connection_id`** from the response
3. **List connections:** GET `/api/v1/connections` to look up saved connections (free to call)

---

## Testing Your Connection

> [Full docs](https://markdown.new/docs.shipp.ai/instructions/test/)

Call the connection with optional params to reduce cost and time:

```bash
curl https://api.shipp.ai/api/v1/connections/CONNECTION_ID?api_key=YOUR_KEY -d '{
  "since": "2026-01-27T16:48:41-05:00",
  "limit": 100
}'
```

Once tested, use `since_event_id` for efficient polling — save the largest event ID and pass it on subsequent calls.

After testing, add the connection to your app. Route requests through your backend (never expose API key to clients).

---

## Shipping Your Product

> [Full docs](https://markdown.new/docs.shipp.ai/instructions/shipp/)

- Do not distribute the API key to consumers — store it securely, route calls through an edge function
- The API is designed for direct runtime use — no caching or database setup required
- Include a footer credit to Shipp when using the APIs (see docs for HTML snippet)
- Use `since` & `limit` in your edge function to control costs

---

## Usage Tips

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/usage-tips/)

- Keep `filter_instructions` short, explicit, and testable. Mention the sport/league and scope.
- Store and reuse `connection_id` — don't create a new connection per run.
- Use `since_event_id` for efficient polling (cursor-based pagination).
- Use the schedule endpoint to discover `game_id`s and team names before creating connections.
- Surface error messages directly to users when limits are hit.
- Treat every field in `data[]` as optional — use existence checks and graceful fallbacks.
- Log unknown data shapes in development to refine `filter_instructions`.
- Polling interval: 5–30 seconds depending on domain and cost sensitivity.
- Deduplicate events by keeping a rolling set of seen event IDs.

---

## Platform Guides

> [Full index](https://markdown.new/docs.shipp.ai/platform-guides/)

| Platform | Guide |
|---|---|
| Lovable | https://markdown.new/docs.shipp.ai/platform-guides/lovable/ |
| Base44 | https://markdown.new/docs.shipp.ai/platform-guides/base44/ |
| Claude Code | https://markdown.new/docs.shipp.ai/platform-guides/claude-code/ |
| Blink | https://markdown.new/docs.shipp.ai/platform-guides/blink/ |
| Replit | https://markdown.new/docs.shipp.ai/platform-guides/replit/ |

For platforms without a guide: tell the platform to read the docs at `https://docs.shipp.ai`.

For Claude Code specifically:
1. Use the shipp skill (this file) or `curl -fsSL "https://shipp.ai/SKILL.md" > ~/.claude/skills/shipp/SKILL.md`
2. Add API key to `.env`: `SHIPP_API_KEY=shipp-live-123-your-api-key`
3. Test the integration

---

## Shipp CLI

The official command-line interface for Shipp. Use it to create accounts, manage connections, and fetch live event data directly from the terminal.

**Source:** https://gitlab.com/outsharp/shipp/cli

### Install the CLI

If `shipp` is not in your PATH, install it:

```sh
curl -fsSL https://shipp.ai/install.sh | bash
```

On Windows (PowerShell):

```powershell
irm https://gitlab.com/outsharp/shipp/cli/-/raw/master/scripts/install.ps1 | iex
```

Supports macOS (Apple Silicon & Intel), Linux (x86_64 & ARM64), and Windows (x86_64 & ARM64).

### Quick Start

```sh
# 1. Create an account
shipp account create --email you@example.com

# 2. Log in (paste API key when prompted — stored at ~/.config/shipp/config.zon)
shipp account login

# 3. Create a connection
shipp connections create --filter_instructions "NBA games, scoring plays only"

# 4. Run the connection
shipp connections run --id CONNECTION_ID
```

### Commands

#### `shipp account`

| Command | Description |
|---|---|
| `shipp account create --email <email>` | Create a new Shipp account |
| `shipp account login` | Log in with your API key |
| `shipp account logout` | Clear stored credentials |

#### `shipp connections`

| Command | Description |
|---|---|
| `shipp connections create --filter_instructions <text>` | Create a connection with natural language filtering |
| `shipp connections list` | List all your connections |
| `shipp connections run --id <connection_id>` | Run a connection and fetch matching events |

#### `connections run` options

| Option | Description |
|---|---|
| `--id <string>` | **(required)** The connection ID to run |
| `--limit <int>` | Max events to return (default: 100) |
| `--since <string>` | ISO 8601 timestamp — only return events after this time (default: 48h ago) |
| `--since-event-id <string>` | ULID of the last event received — only return newer events |

#### Global options

| Option | Description |
|---|---|
| `-v`, `--version` | Print the CLI version |
| `--raw` | Output raw JSON instead of formatted tables |
| `--help` | Show help for any command |

### Examples

```sh
# List connections
shipp connections list

# Get last 10 events
shipp connections run --id CONNECTION_ID --limit 10

# Get events from the last hour
shipp connections run --id CONNECTION_ID --since "2026-03-08T12:00:00Z"

# Raw JSON output piped to jq
shipp connections run --id CONNECTION_ID --raw | jq '.data[].desc'

# Incremental polling
LAST_ID=$(shipp connections run --id CONNECTION_ID --raw | jq -r '.data[-1].id')
shipp connections run --id CONNECTION_ID --since-event-id "$LAST_ID"
```

---

## Versioning

This API is versioned under `/api/v1/`. New versions will be introduced under a new prefix when breaking changes are required.

> [Full docs](https://markdown.new/docs.shipp.ai/api-reference/versioning/)
