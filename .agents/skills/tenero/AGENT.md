---
name: tenero-agent
skill: tenero
description: Autonomous rules for Tenero market analytics — when to query, what to combine, safety considerations.
---

# Tenero Agent

This agent queries the Tenero API (formerly STXTools) for real-time market analytics on Stacks and related chains. All operations are read-only and require no authentication. `wallet-holdings` and `wallet-trades` fall back to the active wallet when no address is given.

## Prerequisites

- No wallet required for: `token-info`, `market-summary`, `market-stats`, `top-gainers`, `top-losers`, `trending-pools`, `whale-trades`, `holder-stats`, `search`
- Wallet must be unlocked for `wallet-holdings` and `wallet-trades` when `--address` is omitted — use `bun run wallet/wallet.ts unlock --password <password>` first, or provide `--address` explicitly

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Understand a specific token (price, volume, metadata) | `token-info` — quick overview |
| Analyze a token's price history and liquidity depth | `market-summary` — detailed stats |
| Survey the overall market condition | `market-stats` — aggregate metrics |
| Find tokens with strong recent momentum | `top-gainers` — 24h price change leaders |
| Find tokens under selling pressure | `top-losers` — 24h price change laggards |
| Audit a wallet's current token positions | `wallet-holdings` — balances + USD values |
| Review a wallet's recent trading activity | `wallet-trades` — swap history |
| Discover high-volume DEX pools | `trending-pools` — use `--timeframe 1h` for recent spikes |
| Detect large market-moving trades | `whale-trades` — identify smart money activity |
| Analyze token ownership concentration | `holder-stats` — distribution and top holders |
| Discover tokens/pools by partial name or symbol | `search` — broad discovery |

## Safety Checks

- These endpoints are read-only — no transaction risk
- Do not pass sensitive wallet data (mnemonics, passwords) to any option in this skill
- When using `wallet-holdings` or `wallet-trades` without `--address`, confirm the wallet is unlocked and the session address belongs to the intended wallet
- Interpret large `top_10_concentration` values (>50%) as centralization risk before recommending a token

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| "Tenero API error: 404 Not Found" | Token address or chain path is invalid | Verify the contract address format (`address.contract-name`) and chain name |
| "Tenero API error: 429 Too Many Requests" | Rate limit exceeded | Wait briefly before retrying |
| "Tenero API error: 5xx" | Tenero service is down | Retry after a short delay; report if persistent |
| "No Stacks address provided and wallet is not unlocked" | `wallet-holdings`/`wallet-trades` called without `--address` and wallet is locked | Provide `--address` or unlock wallet first |

## Output Handling

- `token-info`: use `price_usd` and `price_stx` for valuation; `volume_24h_usd` for liquidity assessment
- `market-summary`: use `price_change_24h` and `price_change_7d` for trend direction; `liquidity_usd` for depth; `holders` for adoption signal
- `market-stats`: use `total_volume_24h_usd` and `active_tokens` to gauge overall market health
- `top-gainers` / `top-losers`: pass `contract_id` to `token-info` or `market-summary` for deeper analysis
- `wallet-holdings`: use `total_value_usd` for portfolio summary; iterate `holdings` for per-token breakdown
- `wallet-trades`: use `type`, `token_in`, `token_out`, and `amount_in_usd` to reconstruct trade history
- `trending-pools`: use `volume_usd` and `fee_24h_usd` to identify fee-earning liquidity opportunities
- `whale-trades`: use `wallet` and `amount_usd` to track large players; pass `wallet` to `wallet-holdings` for position analysis
- `holder-stats`: use `top_10_concentration` as a decentralization signal; `total_holders` as adoption metric
- `search`: pass matching `contract_id` values from `tokens` results to `token-info` for full details

## Example Invocations

```bash
# Get info on a specific token
bun run tenero/tenero.ts token-info --token SP1AY6K3PQV5MRT6R4S671NWW2FRVPKM0BR162CT6.leo-token

# Check the active wallet's holdings
bun run tenero/tenero.ts wallet-holdings

# Find trending pools in the last hour
bun run tenero/tenero.ts trending-pools --timeframe 1h --limit 5

# Search for a token by symbol
bun run tenero/tenero.ts search --query "LEO"
```
