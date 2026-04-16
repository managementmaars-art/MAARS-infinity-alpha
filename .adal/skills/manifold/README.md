# Manifold Skill

Teaches AI agents how to interact with [Manifold](https://manifold.markets) — a prediction market platform where users create and trade on questions about real-world events using play-money (mana) and prize-cash.

## What This Skill Provides

The `SKILL.md` file gives your agent full context on:

- **Authentication** — Simple API key via `Authorization: Key {key}` header
- **REST API** — Market discovery, search, trading, market creation, resolution, comments, portfolios, and mana transfers
- **WebSocket API** — Real-time streaming for new bets, market updates, comments, and per-market events
- **Market types** — Binary, multiple choice, pseudo-numeric, bounty, and poll markets
- **Type definitions** — Full type specs for `LiteMarket`, `FullMarket`, `Bet`, `ContractMetric`, `User`, and more
- **Rate limits, fees, and error handling**

## When to Use This Skill

Use the Manifold skill when your agent needs to:

- Browse, search, and discover prediction markets
- Read market probabilities, positions, and trading history
- Place bets or limit orders on markets
- Sell shares or cancel open limit orders
- Create new markets (binary, multiple choice, numeric, bounty, poll)
- Resolve markets the agent has created
- Monitor portfolios and user positions
- Post comments on markets
- Stream real-time updates via WebSocket
- Send mana to other users

## Getting Started

### 1. Get API Access

- **Read-only (no setup required):** All market data, probabilities, positions, bets, comments, and user info endpoints are fully public — no authentication needed.
- **Trading & writing:** Create a free account at [manifold.markets](https://manifold.markets) and generate an API key.

### 2. Generate an API Key

1. Log in to [Manifold](https://manifold.markets).
2. Go to your profile and click "edit".
3. Scroll to the API key field at the bottom and click "refresh".
4. Copy the key and store it securely. Clicking refresh again will invalidate the old key.

### 3. Environment Variables

Never hardcode API keys. Store credentials as environment variables or in a `.env` file:

```
MANIFOLD_API_KEY=your-api-key
```

## Key Concepts

| Concept | Description |
|---|---|
| **Market (Contract)** | A tradeable question with an outcome type (binary, multiple choice, numeric, etc.) |
| **Mana (M$)** | Play-money currency used for most markets. Cannot be withdrawn. |
| **Prize Cash (CASH)** | Real-money currency on select markets. Can be withdrawn. |
| **Probability** | A number between 0 and 1 representing the market's implied chance of YES |
| **Topic (Group)** | A tag applied to markets for categorization |
| **CPMM** | Constant Product Market Maker — the automated market maker backing most markets |
| **Limit Order** | A bet that only executes at a specified probability price or better |
| **Resolution** | The final outcome of a market: YES, NO, MKT (probability), or CANCEL |

## API at a Glance

Manifold uses a single unified API with all endpoints under one base URL:

| Component | URL |
|---|---|
| **REST API** | `https://api.manifold.markets/v0` |
| **WebSocket** | `wss://api.manifold.markets/ws` |

### Endpoint Categories

| Category | Examples | Auth Required |
|---|---|---|
| **Market discovery** | `/markets`, `/search-markets`, `/slug/[slug]` | No |
| **Probabilities** | `/market/[id]/prob`, `/market-probs` | No |
| **Positions** | `/market/[id]/positions`, `/get-user-portfolio` | No |
| **Users** | `/user/[username]`, `/users`, `/me` | No (`/me` requires auth) |
| **Bets & comments** | `/bets`, `/comments` | No |
| **Trading** | `/bet`, `/multi-bet`, `/market/[id]/sell` | Yes |
| **Market management** | `/market` (create), `/market/[id]/resolve` | Yes |
| **Social** | `/comment` (create), `/managram` | Yes |

## Tips

- **Public endpoints need no auth** — start fetching market data immediately with zero setup
- **Probabilities are 0–1** — a probability of 0.65 means the market implies 65% chance of YES
- **All timestamps are UNIX milliseconds** — JavaScript `Date.now()` style, not seconds
- **Limit orders use whole percentages** — `limitProb` must be two decimal places (e.g., `0.01`, `0.50`, `0.99`)
- **Use `dryRun: true`** to simulate bets without placing them
- **Check the `token` field** — markets can be `MANA` (play-money) or `CASH` (prize-cash)
- **Market URLs are flexible** — the username in `manifold.markets/[username]/[slug]` doesn't need to be correct
- **Combine REST + WebSocket** — REST for initial state, WebSocket for real-time deltas
- **Paginate with `beforeTime`** for deep pagination on `/search-markets` with `sort=newest`
- **Comments cost M$1** when posted via the API
- **Respect rate limits** — 500 requests/minute per IP; implement exponential backoff on 429 responses
- **The API is in alpha** — things may change or break; monitor the docs and Discord for updates

## Resources

| Resource | URL |
|---|---|
| Manifold Platform | [manifold.markets](https://manifold.markets) |
| API Documentation | [docs.manifold.markets/api](https://docs.manifold.markets/api) |
| Source Code (GitHub) | [github.com/manifoldmarkets/manifold](https://github.com/manifoldmarkets/manifold) |
| API Type Definitions | [common/src/api/schema.ts](https://github.com/manifoldmarkets/manifold/tree/main/common/src/api/schema.ts) |
| Terms of Service | [docs.manifold.markets/terms](https://docs.manifold.markets/terms) |
| Data Downloads | [docs.manifold.markets/data](https://docs.manifold.markets/data) |
| Discord Community | [discord.com/invite/eHQBNBqXuh](https://discord.com/invite/eHQBNBqXuh) |