---
name: grimoire-across
description: Fetches Across Protocol bridge quotes, routes, and deposit status using the Grimoire venue CLI. Use when you need bridge quotes, route availability, or cross-chain deposit tracking.
---

# Grimoire Across Skill

Use this skill to query Across Protocol bridge data for cross-chain strategy inputs.

Preferred invocations:

- `grimoire venue across ...`
- `npx -y @grimoirelabs/cli venue across ...` (no-install)
- `bun run packages/cli/src/index.ts venue across ...` (repo-local)
- `grimoire-across ...` (direct binary from `@grimoirelabs/venues`)

Recommended preflight:

- `grimoire venue doctor --adapter across --chain 1 --rpc-url <rpc> --json`

## Commands

- `grimoire venue across info` — adapter metadata and supported chains
- `grimoire venue across chains` — list supported bridge chains
- `grimoire venue across quote --asset <symbol|address> --from <chainId> --to <chainId> --amount <wei> [--recipient <address>]` — get a bridge quote with fees and limits
- `grimoire venue across status --tx-hash <hash> [--api-url <url>]` — check deposit status by origin tx hash
- `grimoire venue across routes --asset <symbol>` — list available bridge routes for an asset

## Examples

```bash
grimoire venue across info
grimoire venue across chains
grimoire venue across quote --asset USDC --from 1 --to 8453 --amount 1000000000
grimoire venue across quote --asset WETH --from 42161 --to 1 --amount 500000000000000000
grimoire venue across status --tx-hash 0xabc123...
grimoire venue across routes --asset USDC
grimoire venue across routes --asset WETH
```

## Supported Chains

| Chain | ID |
|-------|----|
| Ethereum | 1 |
| Optimism | 10 |
| Polygon | 137 |
| Base | 8453 |
| Arbitrum | 42161 |

## Quote Response

The `quote` command returns:

- `inputAmount` / `outputAmount` — amounts in smallest unit (wei)
- `estimatedFillTimeSec` — expected bridge time
- `isAmountTooLow` — whether the amount is below minimum
- `limits.minDeposit` / `limits.maxDeposit` / `limits.maxDepositInstant`
- `fees.lpFee` / `fees.relayerGasFee` / `fees.relayerCapitalFee` / `fees.totalRelayFee`
- `route.spokePoolAddress` — spoke pool contract used

## Metric Surface (Spell Comparisons)

Across exposes `quote_out` for bridge output comparisons:

```spell
across_out = metric("quote_out", across, USDC, "to_chain=8453,amount=1000000")
```

Selector fields:

- required: `to_chain`
- optional: `amount` (defaults to 1 unit of input asset), `asset_out` (defaults to input asset)

## Spell Constraints

When writing bridge actions in `.spell` files targeting Across, use `with` clauses:

```spell
across.bridge(USDC, params.amount, 8453) with (
  max_slippage=50,
  require_quote=true,
)
```

| Constraint | Type | Description |
|-----------|------|-------------|
| `max_slippage` | integer (bps) | Maximum slippage in basis points (converted to min_output) |
| `min_output` | integer (wei) | Explicit minimum output amount floor |
| `require_quote` | boolean | Fail if quote fetch fails |
| `require_simulation` | boolean | Fail if simulation unavailable |
| `max_gas` | integer (wei) | Validate gas estimate against cap |

## Notes

- Amounts are always in the token's smallest unit (wei). For USDC (6 decimals): 1000 USDC = `1000000000`.
- The `status` command queries the Across public API (`https://app.across.to/api/deposits/status`).
- Routes are computed from the built-in token registry; use raw addresses for unlisted tokens.
- Prefer `--format json` in automation; the CLI defaults to `toon` format for interactive use.
