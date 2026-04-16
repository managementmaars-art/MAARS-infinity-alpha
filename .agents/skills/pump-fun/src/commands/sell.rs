use anyhow::Result;
use clap::Args;
use serde::Serialize;

use crate::config::DEFAULT_SLIPPAGE_BPS;
use crate::onchainos::{self, SOL_MINT};

#[derive(Args, Debug)]
pub struct SellArgs {
    /// Token mint address (base58)
    #[arg(long)]
    pub mint: String,

    /// Readable token amount to sell (e.g. "1000000"). Omit to sell entire balance.
    #[arg(long)]
    pub token_amount: Option<String>,

    /// Slippage tolerance in basis points (default: 100 = 1%)
    #[arg(long, default_value_t = DEFAULT_SLIPPAGE_BPS)]
    pub slippage_bps: u64,
}

#[derive(Serialize, Debug)]
struct SellOutput {
    ok: bool,
    mint: String,
    token_amount: String,
    slippage_bps: u64,
    tx_hash: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    dry_run: Option<bool>,
}

pub async fn execute(args: &SellArgs, dry_run: bool) -> Result<()> {
    // Resolve amount: explicit or full balance
    let amount = match &args.token_amount {
        Some(a) => a.clone(),
        None => {
            if dry_run {
                "<full balance>".to_string()
            } else {
                onchainos::get_token_balance(&args.mint)?
                    .ok_or_else(|| anyhow::anyhow!("No balance found for mint {}", args.mint))?
            }
        }
    };

    if dry_run {
        println!(
            "{}",
            serde_json::to_string_pretty(&SellOutput {
                ok: true,
                mint: args.mint.clone(),
                token_amount: amount,
                slippage_bps: args.slippage_bps,
                tx_hash: String::new(),
                dry_run: Some(true),
            })?
        );
        return Ok(());
    }

    let result =
        onchainos::swap_execute_solana(&args.mint, SOL_MINT, &amount, args.slippage_bps).await?;

    let tx_hash = onchainos::extract_tx_hash(&result)?;

    println!(
        "{}",
        serde_json::to_string_pretty(&SellOutput {
            ok: true,
            mint: args.mint.clone(),
            token_amount: amount,
            slippage_bps: args.slippage_bps,
            tx_hash,
            dry_run: None,
        })?
    );
    Ok(())
}
