# Swap Quote — Quote → Swap → Sign → Submit

Full swap flow using the Carbium Swap API: get a quote, fetch the swap transaction, sign it, and submit via RPC.

## Prerequisites

```bash
npm install @solana/web3.js
export CARBIUM_RPC_KEY="your-key"
export CARBIUM_API_KEY="your-swap-api-key"
```

## Full Flow

```typescript
import { Connection, VersionedTransaction, Keypair } from "@solana/web3.js";

const connection = new Connection(
  `https://rpc.carbium.io/?apiKey=${process.env.CARBIUM_RPC_KEY}`,
  "confirmed"
);

const API_KEY = process.env.CARBIUM_API_KEY!;
const SOL_MINT = "So11111111111111111111111111111111111111112";
const USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

// Step 1: Get quote
async function getQuote(amountLamports: number) {
  const url = new URL("https://api.carbium.io/api/v2/quote");
  url.searchParams.set("src_mint", SOL_MINT);
  url.searchParams.set("dst_mint", USDC_MINT);
  url.searchParams.set("amount_in", amountLamports.toString());
  url.searchParams.set("slippage_bps", "100");

  const res = await fetch(url, {
    headers: { "X-API-KEY": API_KEY },
  });

  if (!res.ok) throw new Error(`Quote failed: ${res.status}`);
  return res.json();
}

// Step 2: Get swap transaction
async function getSwapTx(ownerAddress: string, amountLamports: number) {
  const url = new URL("https://api.carbium.io/api/v2/swap");
  url.searchParams.set("owner", ownerAddress);
  url.searchParams.set("fromMint", SOL_MINT);
  url.searchParams.set("toMint", USDC_MINT);
  url.searchParams.set("amount", amountLamports.toString());
  url.searchParams.set("slippage", "100");
  url.searchParams.set("provider", "raydium");

  const res = await fetch(url, {
    headers: { accept: "text/plain", "X-API-KEY": API_KEY },
  });

  if (!res.ok) throw new Error(`Swap failed: ${res.status}`);
  return res.json();
}

// Step 3: Sign and submit
async function executeSwap(wallet: Keypair, amountLamports: number) {
  const quote = await getQuote(amountLamports);
  console.log("Quote:", quote);

  const { transaction } = await getSwapTx(
    wallet.publicKey.toBase58(),
    amountLamports
  );

  const tx = VersionedTransaction.deserialize(
    Buffer.from(transaction, "base64")
  );
  tx.sign([wallet]);

  const sig = await connection.sendRawTransaction(tx.serialize(), {
    maxRetries: 3,
  });

  await connection.confirmTransaction(sig, "confirmed");
  console.log("Swap confirmed:", sig);
  return sig;
}

// Run:
// const wallet = Keypair.fromSecretKey(/* your key */);
// await executeSwap(wallet, 100_000_000); // 0.1 SOL
```
