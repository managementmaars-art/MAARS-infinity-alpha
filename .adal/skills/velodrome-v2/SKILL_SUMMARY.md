
# velodrome-v2 -- Skill Summary

## Overview
This skill enables interaction with Velodrome V2's classic AMM pools on Optimism, supporting token swaps, liquidity management, and reward claiming. It handles both volatile (constant-product) and stable (low-slippage curve) pool types, with automatic pool routing and built-in safety confirmations for all write operations.

## Usage
Install the binary via the auto-injected setup commands, ensure onchainos CLI is configured with your wallet, then use commands like `velodrome-v2 swap` or `velodrome-v2 add-liquidity` with the `--confirm` flag to execute transactions.

## Commands
| Command | Description |
|---------|-------------|
| `quote` | Get swap quotes without executing transactions |
| `swap` | Execute token swaps via Velodrome Router |
| `pools` | Query pool addresses and reserve information |
| `positions` | View LP token balances for your wallet |
| `add-liquidity` | Add liquidity to volatile or stable pools |
| `remove-liquidity` | Remove LP tokens and withdraw underlying assets |
| `claim-rewards` | Claim VELO emissions from pool gauges |

## Triggers
Activate this skill when users want to trade tokens, provide liquidity, or manage DeFi positions specifically on Velodrome V2 on Optimism. Use for Optimism-native DeFi operations involving WETH, USDC, VELO, and other major tokens.
