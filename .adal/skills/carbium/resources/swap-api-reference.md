# Carbium Swap API Reference

Base URL: `https://api.carbium.io/api/v2`
Auth: `X-API-KEY` header on all requests

## GET /quote

Get optimized quote with optional executable transaction.

| Param | Type | Required | Description |
|---|---|---|---|
| `src_mint` | string | Yes | Input token mint address |
| `dst_mint` | string | Yes | Output token mint address |
| `amount_in` | integer | Yes | Input amount in smallest unit (lamports for SOL) |
| `slippage_bps` | integer | Yes | Slippage tolerance in basis points (100 = 1%) |
| `user_account` | string | No | User wallet address. If included, response includes `txn` field with base64 serialized transaction ready for signing |

**Response:** JSON with quote details. If `user_account` provided, includes `txn` field.

---

## GET /quote/all

Compare quotes from all supported DEX providers simultaneously.

| Param | Type | Required | Description |
|---|---|---|---|
| `fromMint` | string | Yes | Input token mint address |
| `toMint` | string | Yes | Output token mint address |
| `amount` | integer | Yes | Input amount in smallest unit |
| `slippage` | integer | Yes | Slippage in basis points |

**Response:** JSON with quotes from each available provider for the given pair.

> **Note:** This endpoint uses `fromMint`/`toMint` naming (like `/swap`), not `src_mint`/`dst_mint` (like `/quote`).

---

## GET /swap

Get a serialized swap transaction for a specific provider.

| Param | Type | Required | Description |
|---|---|---|---|
| `owner` | string | Yes | Wallet address of the user (signer) |
| `fromMint` | string | Yes | Input token mint address |
| `toMint` | string | Yes | Output token mint address |
| `amount` | integer | Yes | Input amount in smallest unit |
| `slippage` | integer | Yes | Slippage in basis points |
| `provider` | string | Yes | DEX provider to route through (see supported list below) |
| `pool` | string | No | Custom pool address for direct routing |
| `feeLamports` | integer | No | Custom fee amount in lamports |
| `feeReceiver` | string | No | Account receiving the custom fee (required if `feeLamports` set) |
| `priorityMicroLamports` | integer | No | Compute unit price for priority fees |
| `mevSafe` | boolean | No | If `true`, includes Jito tip instruction for MEV protection |
| `gasless` | boolean | No | If `true`, gasless swap. **Only valid if output token is SOL** |

**Response:** base64-encoded serialized `VersionedTransaction`. Deserialize → sign → submit via RPC.

**Error responses:**
- `400`: `{ error: { message: "No pool found" } }` — invalid pair or no liquidity
- `401`: `{ error: { message: "API Key not found" } }` — missing/invalid key

---

## GET /swap/bundle

Submit a signed transaction via Jito bundle for MEV protection.

| Param | Type | Required | Description |
|---|---|---|---|
| `signedTransaction` | string | Yes | Base64-encoded signed transaction |

**Response:** JSON with bundle ID and transaction hash.

**Flow:** Get transaction from `/swap` → sign locally → submit via `/swap/bundle`.

---

## GET /fee/custom

Generate a custom fee transfer transaction.

| Param | Type | Required | Description |
|---|---|---|---|
| `payer` | string | Yes | Address of the fee payer |
| `receiver` | string | Yes | Address of the fee receiver |
| `lamports` | integer | Yes | Fee amount in lamports |

**Response:** JSON with serialized transaction.

---

## Supported Providers

| Provider | ID | Type |
|---|---|---|
| Raydium | `raydium` | AMM |
| Raydium CPMM | `raydium-cpmm` | Constant Product |
| Orca | `orca` | CLMM |
| Meteora | `meteora` | AMM |
| Meteora DLMM | `meteora-dlmm` | Dynamic Liquidity |
| Pump.fun | `pump-fun` | Bonding Curve |
| Moonshot | `moonshot` | Bonding Curve |
| Stabble | `stabble` | Stable |
| PrintDEX | `printdex` | AMM |
| GooseFX | `goosefx` | AMM |

---

## Naming Inconsistency Warning

The Quote and Swap endpoints use **different parameter names** for the same concepts:

| Concept | `/quote` param | `/swap` param |
|---|---|---|
| Input token | `src_mint` | `fromMint` |
| Output token | `dst_mint` | `toMint` |
| Amount | `amount_in` | `amount` |
| Slippage | `slippage_bps` | `slippage` |

Use the exact parameter names for each endpoint. Mismatched names will return silent bad results or errors.

---

## Slippage Recommendations

| Pair Type | BPS | Percentage |
|---|---|---|
| Stablecoin swaps | 5-10 | 0.05-0.1% |
| Major pairs (SOL/USDC) | 10-50 | 0.1-0.5% |
| Volatile tokens | 50-100 | 0.5-1% |
| Arbitrage | 10 | 0.1% |
