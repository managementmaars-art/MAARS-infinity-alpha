---
name: tokens-agent
skill: tokens
description: SIP-010 fungible token operations on Stacks L2 — check balances, transfer tokens, get metadata, list all tokens for an address, and query top holders. Supports well-known symbols and full contract IDs.
---

# Tokens Agent

This agent handles SIP-010 fungible token operations on Stacks L2. It supports well-known tokens by symbol (sBTC, USDCx, ALEX, DIKO) as well as any SIP-010 token by full contract ID. Balance and info queries work without a wallet. Transfer operations require an unlocked wallet.

## Prerequisites

- For `get-balance`, `get-info`, `list-user-tokens`, `get-holders`: no wallet required
- For `transfer`: wallet must be unlocked (`bun run wallet/wallet.ts unlock`)
- Token identifier: use a known symbol (`sBTC`, `USDCx`, `ALEX`, `DIKO`) or a full contract ID (`SP2....contract-name`)

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Check a specific token balance | `get-balance` — requires `--token`; `--address` is optional |
| Transfer tokens to another address | `transfer` — requires `--token`, `--recipient`, and `--amount` |
| Look up token name, decimals, supply | `get-info` — requires `--token` |
| See all tokens held by an address | `list-user-tokens` — `--address` is optional, uses active wallet |
| Find the largest token holders | `get-holders` — requires `--token`; supports `--limit` and `--offset` |

## Safety Checks

- Before `transfer`: verify the token balance covers the intended amount — run `get-balance` first
- Before `transfer`: confirm the wallet has STX to cover the transaction fee (run `stx get-balance`)
- Token amounts are in the smallest unit — use `get-info` to read `decimals` before specifying `--amount`
- Verify the recipient address format starts with `SP` (mainnet) or `ST` (testnet) before transferring
- Transfer is irreversible once confirmed — double-check `--token`, `--recipient`, and `--amount`

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| "Wallet is locked" | Wallet session expired or not yet unlocked | Run `bun run wallet/wallet.ts unlock --password <password>` |
| "Token metadata not found" | Unknown symbol or invalid contract ID | Check `get-info` output; verify the contract ID format |
| "insufficient funds" | Token balance too low for the requested amount | Run `get-balance` first to verify available tokens |
| "ConflictingNonceInMempool" | Prior transaction still pending | Wait for pending transaction to confirm, then retry |

## Output Handling

- `get-balance`: read `balance.raw` for exact value; `balance.formatted` includes symbol; `token.decimals` is needed to interpret raw amounts
- `transfer`: extract `txid` and pass to `stx get-transaction-status` for confirmation; `token` and `amount` confirm what was sent
- `get-info`: `decimals` is the key field for interpreting all balance values; `contractId` is the canonical identifier for subsequent calls
- `list-user-tokens`: `tokens[].contractId` contains the full `address.contract::token` identifier; use these with `get-balance` or `transfer`
- `get-holders`: `holders[].address` and `holders[].balance` list top holders; `total` is the total number of holders

## Example Invocations

```bash
# Check USDCx balance for the active wallet
bun run tokens/tokens.ts get-balance --token USDCx

# List all tokens owned by an address
bun run tokens/tokens.ts list-user-tokens --address SP2...

# Transfer ALEX tokens to another address (amount in smallest unit)
bun run tokens/tokens.ts transfer --token ALEX --recipient SP2... --amount 100000000
```
