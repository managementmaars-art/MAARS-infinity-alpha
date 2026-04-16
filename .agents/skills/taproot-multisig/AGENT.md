---
name: taproot-multisig-agent
skill: taproot-multisig
description: Execute Bitcoin Taproot M-of-N multisig transactions between autonomous agents using BIP-340 Schnorr signatures and OP_CHECKSIGADD. Handles key registration, sighash signing, co-signer verification, and coordination through APIs like QuorumClaw.
---

# Taproot Multisig Agent

This agent coordinates Bitcoin Taproot multisig transactions between autonomous agents using BIP-340 Schnorr signatures and BIP-342 OP_CHECKSIGADD. It handles deriving the correct public key for registration, verifying co-signer signatures, and printing the full multisig workflow guide. Signing sighashes is delegated to the `signing` skill. Proven on mainnet: 2-of-2 (block 937,849, Arc + Aetos) and 3-of-3 (block 938,206, Arc + Aetos + Bitclaw).

## Prerequisites

- Wallet must be unlocked for `get-pubkey` — use `bun run wallet/wallet.ts unlock --password <password>` first
- `verify-cosig` and `guide` do not require an unlocked wallet
- Signing skill must be available for sighash signing (`signing/signing.ts schnorr-sign-digest`)
- Only mainnet-tested — use on mainnet; testnet behavior is not guaranteed

## Decision Logic

| Goal | Subcommand |
|------|-----------|
| Get your x-only internal pubkey to register with a coordinator | `get-pubkey` — share `internalPubKey`, NOT the tweaked key |
| Verify a co-signer's BIP-340 signature before trusting it | `verify-cosig --digest <hex> --signature <hex> --public-key <hex>` |
| Print the full M-of-N multisig workflow as JSON | `guide` — covers key registration through broadcast |
| Sign a sighash received from a coordinator | Use `signing/signing.ts schnorr-sign-digest --digest <sighash_hex> --confirm-blind-sign` |

## Safety Checks

- **Register `internalPubKey`, not the tweaked key** — the signing skill signs with the internal key; registering the tweaked key causes signature verification failures at the coordinator
- Before signing a sighash: verify it comes from a trusted coordinator — you cannot decode what you are signing
- Run `verify-cosig` on each co-signer's signature before the coordinator broadcasts — confirms every co-signer's key actually signed this sighash
- Do not sign the same sighash twice without confirmation — some coordinators treat duplicate submissions as errors
- The `--confirm-blind-sign` flag on `schnorr-sign-digest` is required; the first call without it shows the digest for review

## Error Handling

| Error message | Cause | Fix |
|--------------|-------|-----|
| "Wallet is not unlocked. Run: bun run wallet/wallet.ts unlock ..." | `get-pubkey` called without unlocked wallet | Unlock wallet before running get-pubkey |
| "Taproot keys not available. Ensure the wallet has Taproot key derivation." | Wallet does not expose Taproot keys | Use a managed wallet; env-var wallets may not have Taproot derivation |
| "--digest must be exactly 32 bytes (64 hex chars)" | Wrong-length digest passed to `verify-cosig` | Use the full 64-character hex sighash from the coordinator |
| "--signature must be exactly 64 bytes (128 hex chars)" | Wrong-length signature | Use the 128-character hex Schnorr signature |
| "--public-key must be exactly 32 bytes (64 hex chars)" | Wrong-length public key | Use the 64-character x-only hex pubkey |
| Coordinator rejects signature | Internal vs tweaked key mismatch | Re-derive tweaked private key formula: `d' = d + H_TapTweak(P) mod n` (with Y-parity) — or re-register using `internalPubKey` |

## Output Handling

- `get-pubkey`: share `internalPubKey` (32-byte hex) with the multisig coordinator; `taprootAddress` is for receiving funds only
- `verify-cosig`: check `isValid` — if `false`, do not proceed; the co-signer's key did not sign this digest
- `guide`: machine-readable JSON workflow; pass `workflow` array to another agent for step-by-step coordination; `criticalGotcha` documents the internal vs tweaked key distinction

## Example Invocations

```bash
# Get your pubkey for registration with a coordinator
bun run taproot-multisig/taproot-multisig.ts get-pubkey

# Sign a sighash received from QuorumClaw (signing skill handles this)
bun run signing/signing.ts schnorr-sign-digest \
  --digest a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890ab \
  --confirm-blind-sign

# Verify a co-signer's signature before trusting it
bun run taproot-multisig/taproot-multisig.ts verify-cosig \
  --digest a1b2c3... \
  --signature 64byteHex... \
  --public-key 32byteHex...
```
