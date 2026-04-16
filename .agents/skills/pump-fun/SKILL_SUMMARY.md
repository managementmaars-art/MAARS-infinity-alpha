
# pump-fun -- Skill Summary

## Overview
This skill enables AI agents to interact with pump.fun's bonding curve mechanism on Solana mainnet, allowing for token trading, price discovery, and market analysis. It provides both read-only operations for price checking and bonding curve state monitoring, as well as write operations for buying and selling tokens through the pump.fun protocol and graduated DEX pools.

## Usage
Use commands like `pump-fun get-price` to check token prices, `pump-fun buy` to purchase tokens, and `pump-fun sell` to trade back to SOL. All write operations support dry-run previews and require user confirmation before execution.

## Commands
| Command | Description |
|---------|-------------|
| `get-token-info --mint <ADDRESS>` | Fetch bonding curve state, reserves, and graduation progress |
| `get-price --mint <ADDRESS> --direction <buy/sell> --amount <AMOUNT>` | Calculate expected output for buy/sell operations |
| `buy --mint <ADDRESS> --sol-amount <AMOUNT> [--dry-run]` | Buy tokens on bonding curve with SOL |
| `sell --mint <ADDRESS> [--token-amount <AMOUNT>] [--dry-run]` | Sell tokens back to bonding curve for SOL |

## Triggers
Activate this skill when users want to trade memecoins on pump.fun, check bonding curve prices, monitor token graduation progress, or interact with Solana-based token launchpads. Trigger phrases include "buy pump.fun token," "sell pump.fun token," "check pump.fun price," and "pump.fun bonding curve."
