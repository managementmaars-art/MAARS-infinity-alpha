---
name: yield-dashboard-agent
skill: yield-dashboard
description: Cross-protocol DeFi yield dashboard — aggregates positions across Zest, ALEX, Bitflow, and STX stacking. Read-only, mainnet-only.
---

# Yield Dashboard Agent

This agent provides a unified read-only view of DeFi positions across all major Stacks protocols: Zest Protocol (lending), ALEX DEX (AMM LP), Bitflow (DEX LP), and STX stacking. No funds are moved. Use it to understand current portfolio composition, compare live yields, and get rebalance suggestions before delegating to write-capable skills.

## Prerequisites

- Network must be set to mainnet: `NETWORK=mainnet`
- Wallet must be unlocked for `overview`, `positions`, and `rebalance` — these need the wallet address for position lookups
- `apy-breakdown` does not require a wallet — it is pure market data and works without unlock

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Full portfolio summary with total value and weighted APY | `overview` — returns totals plus per-protocol breakdown |
| Detailed breakdown of each protocol position | `positions` — returns array with amounts, APY, risk score |
| Current APY rates without wallet context | `apy-breakdown` — no wallet needed, use before deciding where to deploy |
| Rebalancing suggestions for a given risk level | `rebalance --risk-tolerance low\|medium\|high` |

## Safety Checks

- This skill is read-only — no transactions are submitted, no funds can be lost
- APY figures are point-in-time estimates from on-chain state; do not treat them as guaranteed rates
- ALEX LP positions and Bitflow LP positions currently show `valueSats: 0` even if you hold LP tokens — LP balance reading is not yet implemented; APY is still correct
- `totalValueSats` in `overview` excludes STX stacking (different unit); see `totalValueStx` separately
- Bitflow APY falls back to 2.8% estimate if the Bitflow public API is unavailable; output will include `apySource: "fallback estimate"`
- ALEX pool uses aBTC (ALEX wrapped BTC), not native sBTC — different trust model from Zest sBTC lending
- Stacking APY (8.0%) is a static estimate, not a live on-chain value

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| `"yield-dashboard is mainnet-only. Set NETWORK=mainnet to use this skill."` | NETWORK is not mainnet | Run with `NETWORK=mainnet bun run yield-dashboard/yield-dashboard.ts ...` |
| "Wallet is locked. Run: bun run wallet/wallet.ts unlock" | Wallet not unlocked for address-dependent commands | Run `bun run wallet/wallet.ts unlock --password <password>` first, or use `apy-breakdown` which needs no wallet |
| `"error": "API 4xx for <function>"` | Hiro API or contract call failed | Retry; may be a transient API issue |
| Bitflow position shows `apyPct: 2.8` with `apySource: "fallback estimate"` | Bitflow public API unavailable | Not an error; fallback APY is used automatically |

## Output Handling

- `overview`: use `protocols.<name>.apyPct` to compare yields; `totalValueSats` and `totalValueBtc` for BTC-denominated total; `totalValueMicroStx`/`totalValueStx` for stacking; `walletSbtcSats` and `walletStxMicroStx` for uninvested wallet balances
- `positions`: iterate `positions[]` — `valueSats`/`valueBtc` for BTC assets, `valueMicroStx`/`valueStx` for STX; `details.error` indicates a failed read for that protocol (non-fatal)
- `apy-breakdown`: extract `rates[].supplyApyPct` (Zest) or `rates[].apyPct` (others) and `rates[].riskScore` for yield-vs-risk comparison; use as pre-trade research
- `rebalance`: use `suggestions[]` as human-readable action items; `suggestedAllocation` gives target percentages; pass context to `yield-hunter` or `defi` skill when acting on suggestions

## Example Invocations

```bash
# Get full portfolio overview
NETWORK=mainnet bun run yield-dashboard/yield-dashboard.ts overview

# Check current APY rates across all protocols (no wallet needed)
NETWORK=mainnet bun run yield-dashboard/yield-dashboard.ts apy-breakdown

# Get rebalance suggestions with conservative risk tolerance
NETWORK=mainnet bun run yield-dashboard/yield-dashboard.ts rebalance --risk-tolerance low
```
