---
name: stackspot-agent
skill: stackspot
description: Stackspot stacking lottery pots on Stacks mainnet — join STX pots that stack via PoX, claim sBTC rewards if selected as VRF winner, and manage pot lifecycle.
---

# Stackspot Agent

This agent handles stacking lottery pot operations on stackspot.app. Participants pool STX into pots that are stacked via Proof of Transfer (PoX) for one cycle. A VRF mechanism selects one winner who receives the stacking yield in sBTC; all participants receive their original STX back. All operations are mainnet-only. Write operations require an unlocked wallet.

## Prerequisites

- Set `NETWORK=mainnet` — all stackspot operations will error on testnet or default network
- Wallet unlocked via `bun run wallet/wallet.ts unlock --password <password>` for write operations (join-pot, start-pot, claim-rewards, cancel-pot)
- Sufficient STX balance to meet pot minimum (Genesis: 20 STX, BuildOnBitcoin: 100 STX, STXLFG: 21 STX)
- Read operations (list-pots, get-pot-state) require no wallet unlock

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Browse available pots and fill status | `list-pots` — shows all known pots with current value and lock status |
| Inspect full on-chain state for a specific pot | `get-pot-state --contract-name <name>` — returns value, participant count, lock status, configs |
| Contribute STX to a pot | `join-pot --contract-name <name> --amount <microStx>` — STX locked for one PoX cycle |
| Trigger stacking for a full pot | `start-pot --contract-name <name>` — must be called during PoX prepare phase |
| Claim sBTC rewards after pot completes | `claim-rewards --contract-name <name>` — only VRF winner receives sBTC; all get STX back |
| Cancel a pot and recover STX | `cancel-pot --contract-name <name>` — only before stacking starts |

## Safety Checks

- Verify NETWORK=mainnet before any operation — all calls on testnet will error
- Check PoX prepare phase timing before `start-pot` via `bun run stacking/stacking.ts get-pox-info`; calling outside the prepare phase will fail
- Confirm STX available balance meets pot minimum before `join-pot`; contributed STX is locked for ~2 weeks
- Do not join a pot with STX needed for other operations within the stacking cycle duration
- Run `get-pot-state` before `join-pot` to confirm the pot is not already locked
- `cancel-pot` requires pot to not be locked (stacking not yet started); verify lock status first
- Only the VRF-selected winner receives sBTC rewards — participating does not guarantee sBTC income

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| "stackspot skill is mainnet-only" | NETWORK is not set to mainnet | Run with `NETWORK=mainnet bun run stackspot/stackspot.ts ...` |
| "Wallet is locked" | Write operation without unlocked wallet | Run `bun run wallet/wallet.ts unlock --password <password>` |
| "--amount ... is below the minimum" | Contribution below pot minimum | Increase `--amount` to meet the pot's minimum micro-STX |
| "Read-only call ... failed" | Contract not deployed or function error | Verify the contract name is correct via `list-pots` |
| `start-pot` transaction fails | Called outside PoX prepare phase | Check `bun run stacking/stacking.ts get-pox-info` and wait for prepare phase |

## Output Handling

- `list-pots` → `pots[]` with `name`, `contract`, `maxParticipants`, `minAmountStx`, `currentValueUstx`, `isLocked`; use `contract` as `--contract-name` input
- `get-pot-state` → `state.isLocked` to check join eligibility; `state.potValueUstx` to gauge fill progress
- `join-pot` → `txid` and `explorerUrl` for transaction tracking; `pot.amountUstx` confirms contribution
- `start-pot` → `txid` and `explorerUrl`; monitor via explorer until confirmed on-chain
- `claim-rewards` → `txid` and `explorerUrl`; sBTC transfer visible in transaction details if winner
- `cancel-pot` → `txid` and `explorerUrl`; STX returned to wallet after transaction confirms

## Example Invocations

```bash
# List all known pots with current value and lock status
NETWORK=mainnet bun run stackspot/stackspot.ts list-pots

# Get full on-chain state for the STXLFG pot
NETWORK=mainnet bun run stackspot/stackspot.ts get-pot-state \
  --contract-name SPT4SQP5RC1BFAJEQKBHZMXQ8NQ7G118F335BD85.STXLFG

# Join STXLFG pot with 21 STX (21,000,000 micro-STX)
NETWORK=mainnet bun run stackspot/stackspot.ts join-pot \
  --contract-name STXLFG --amount 21000000

# Claim sBTC rewards after pot cycle completes
NETWORK=mainnet bun run stackspot/stackspot.ts claim-rewards \
  --contract-name STXLFG
```
