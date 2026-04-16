---
name: stacks-market-agent
skill: stacks-market
description: Prediction market trading on stacksmarket.app — discover markets, quote LMSR prices, buy/sell YES/NO shares, and redeem winnings on Stacks mainnet.
---

# Stacks Market Agent

This agent handles prediction market trading on [stacksmarket.app](https://www.stacksmarket.app) via the `market-factory-v18-bias` contract on Stacks mainnet. It provides market discovery, LMSR price quoting, share trading with slippage protection, and post-resolution redemption. All operations are mainnet-only. Write operations require an unlocked wallet with sufficient STX.

## Prerequisites

- Network must be set to mainnet: `NETWORK=mainnet`
- Wallet must be unlocked for buy, sell, and redeem operations: run `bun run wallet/wallet.ts unlock` first
- Sufficient STX balance for the trade amount plus gas fees (~0.05–0.1 STX per transaction)
- For selling or redeeming: must have previously bought shares in the target market

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Browse available prediction markets | `list-markets` — filter by status, category, or featured flag |
| Find markets about a specific topic | `search-markets --query <keyword>` |
| Get full market details and trade history | `get-market --market-id <mongoId>` — uses MongoDB `_id`, not numeric marketId |
| Check cost before buying shares | `quote-buy --market-id <id> --side yes\|no --amount <n>` — always quote first |
| Check proceeds before selling shares | `quote-sell --market-id <id> --side yes\|no --amount <n>` — always quote first |
| Buy YES shares in a market | `buy-yes --market-id <id> --amount <n> --max-cost <ustx>` |
| Buy NO shares in a market | `buy-no --market-id <id> --amount <n> --max-cost <ustx>` |
| Sell YES shares before resolution | `sell-yes --market-id <id> --amount <n> --min-proceeds <ustx>` |
| Sell NO shares before resolution | `sell-no --market-id <id> --amount <n> --min-proceeds <ustx>` |
| Redeem winnings after resolution | `redeem --market-id <id>` — only callable on resolved markets |
| Check share balances in a market | `get-position --market-id <id>` |

## Safety Checks

- Always run `quote-buy` or `quote-sell` before trading — LMSR prices shift with every trade; quotes go stale within seconds
- Pass `totalCostUstx` from quote result as `--max-cost` when buying (slippage cap)
- Pass `totalProceedsUstx` from quote result as `--min-proceeds` when selling (slippage floor)
- Check `isResolved` in the market data before redeeming — only resolved markets pay out
- Check `isActive` AND compare `endDate` to current time — `isActive` can remain `true` after the market closes; the contract owner must manually resolve
- Verify wallet STX balance covers the full `totalCostUstx` plus ~100,000 uSTX gas before calling buy-yes or buy-no
- Note: Market IDs are epoch millisecond timestamps (e.g., `1771853629839`); `get-market` uses MongoDB `_id` (hex string like `699c573ea7bb5ad25fee68a0`) — do not confuse the two
- All write operations use `PostConditionMode.Allow` — this is required by the contract and is expected behavior

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| "stacks-market skill is mainnet-only. Set NETWORK=mainnet to use this skill." | NETWORK env var is not mainnet | Run with `NETWORK=mainnet bun run stacks-market/stacks-market.ts ...` |
| "Wallet is locked. Run: bun run wallet/wallet.ts unlock" | Wallet not unlocked | Run `bun run wallet/wallet.ts unlock --password <password>` first |
| "Quote returned no data. Market may not exist or be invalid." | Invalid market ID or inactive market | Verify market ID with `list-markets` or `get-market` first |
| "--side must be 'yes' or 'no'" | Invalid `--side` value | Pass `--side yes` or `--side no` exactly |
| "--amount must be a positive integer" | Non-integer or zero amount | Pass a whole number greater than 0 |
| "Stacks Market API error (404)" | Market `_id` not found | Verify the MongoDB `_id` with `list-markets` |

## Output Handling

- `list-markets` and `search-markets`: extract `markets[].marketId` (numeric timestamp) for quoting/trading; extract `markets[]._id` (hex string) for `get-market`
- `get-market`: check `isResolved` before redeeming; check `isActive` and `endDate` before buying
- `quote-buy`: use `quote.totalCostUstx` as `--max-cost` for `buy-yes` or `buy-no`
- `quote-sell`: use `quote.totalProceedsUstx` as `--min-proceeds` for `sell-yes` or `sell-no`
- `buy-yes`, `buy-no`, `sell-yes`, `sell-no`, `redeem`: extract `txid` for status tracking; use `explorerUrl` to link to the transaction
- `get-position`: extract `position.yesShares` and `position.noShares` to decide whether to sell or redeem

## Example Invocations

```bash
# List 10 active markets in the Crypto category
NETWORK=mainnet bun run stacks-market/stacks-market.ts list-markets --limit 10 --status active --category Crypto

# Quote then buy 5 YES shares (use totalCostUstx from quote as --max-cost)
NETWORK=mainnet bun run stacks-market/stacks-market.ts quote-buy --market-id 1771853629839 --side yes --amount 5
NETWORK=mainnet bun run stacks-market/stacks-market.ts buy-yes --market-id 1771853629839 --amount 5 --max-cost 5500000

# Check position and redeem winnings after market resolves
NETWORK=mainnet bun run stacks-market/stacks-market.ts get-position --market-id 1771853629839
NETWORK=mainnet bun run stacks-market/stacks-market.ts redeem --market-id 1771853629839
```
