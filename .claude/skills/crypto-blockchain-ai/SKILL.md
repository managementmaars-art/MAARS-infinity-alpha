---
name: crypto-blockchain-ai
description: AI crypto/blockchain skills — smart contracts, DeFi analysis, NFT, Web3 integration, on-chain data, trading bots, tokenomics for MAARS crypto agents
---

# Crypto & Blockchain AI — MAARS Reference

## Smart Contract Development
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract MaarsToken is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 100_000_000 * 1e18;
    mapping(address => bool) public blacklisted;
    
    event TokensMinted(address indexed to, uint256 amount);
    
    constructor() ERC20("MAARS Token", "MAARS") Ownable(msg.sender) {
        _mint(msg.sender, 10_000_000 * 1e18); // 10M initial supply
    }
    
    function mint(address to, uint256 amount) external onlyOwner {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        require(!blacklisted[to], "Address blacklisted");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }
    
    // Override transfer to add blacklist check
    function _update(address from, address to, uint256 value) 
        internal override {
        require(!blacklisted[from] && !blacklisted[to], "Blacklisted");
        super._update(from, to, value);
    }
}
```

## Web3 Python Integration
```python
from web3 import Web3
from eth_account import Account
import json

# Connect to network
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_KEY}"))
# or: Alchemy, QuickNode, etc.

# Load contract
def load_contract(address: str, abi_path: str):
    with open(abi_path) as f:
        abi = json.load(f)
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

# Read contract state
async def get_token_balance(token_contract, wallet: str) -> float:
    balance = token_contract.functions.balanceOf(wallet).call()
    decimals = token_contract.functions.decimals().call()
    return balance / (10 ** decimals)

# Send transaction
def send_transaction(private_key: str, to: str, value_eth: float, data: bytes = b""):
    account = Account.from_key(private_key)
    tx = {
        "from": account.address,
        "to": to,
        "value": w3.to_wei(value_eth, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address),
        "data": data,
    }
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)
```

## DeFi Protocol Integration
```python
# Uniswap V3 — Swap tokens
from uniswap import Uniswap

uniswap = Uniswap(
    address=WALLET_ADDRESS,
    private_key=PRIVATE_KEY,
    version=3,
    provider=f"https://mainnet.infura.io/v3/{INFURA_KEY}",
)

def swap_tokens(token_in: str, token_out: str, amount_in: float, slippage: float = 0.5):
    """Swap ERC20 tokens. slippage in %"""
    amount_in_wei = int(amount_in * 1e18)
    return uniswap.make_trade(token_in, token_out, amount_in_wei, slippage=slippage/100)

# Aave — Flash loan template
AAVE_FLASH_LOAN_TEMPLATE = """
// Flash loan callback
function executeOperation(
    address[] calldata assets,
    uint256[] calldata amounts,
    uint256[] calldata premiums,
    address initiator,
    bytes calldata params
) external override returns (bool) {
    // YOUR ARBITRAGE LOGIC HERE
    // assets[0] = borrowed token, amounts[0] = borrowed amount
    
    // Repay: approve pool for amount + premium
    uint amountOwed = amounts[0] + premiums[0];
    IERC20(assets[0]).approve(address(POOL), amountOwed);
    return true;
}
"""
```

## On-Chain Data Analysis
```python
# Dune Analytics — SQL for blockchain data
DUNE_QUERIES = {
    "whale_movements": """
SELECT
    block_time,
    tx_hash,
    from AS sender,
    to AS receiver,
    value / 1e18 AS eth_amount,
    value / 1e18 * price AS usd_value
FROM ethereum.transactions t
JOIN prices.usd p ON p.symbol = 'ETH' 
    AND date_trunc('hour', t.block_time) = p.minute
WHERE value > 1000 * 1e18  -- >1000 ETH
    AND block_time > NOW() - INTERVAL '24' HOUR
ORDER BY value DESC
""",
    "dex_volume": """
SELECT
    DATE_TRUNC('day', block_time) AS day,
    project,
    SUM(amount_usd) AS volume_usd
FROM dex.trades
WHERE block_time > NOW() - INTERVAL '30' DAY
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
""",
}

# The Graph — Query protocol subgraphs
import requests

def query_subgraph(subgraph_url: str, graphql_query: str):
    return requests.post(subgraph_url, json={"query": graphql_query}).json()["data"]

UNISWAP_QUERY = """
{
  pools(first: 10, orderBy: volumeUSD, orderDirection: desc) {
    id
    token0 { symbol }
    token1 { symbol }
    volumeUSD
    totalValueLockedUSD
    feeTier
  }
}
"""
```

## NFT Operations
```python
# OpenSea API
import requests

def get_nft_collection_stats(slug: str):
    return requests.get(
        f"https://api.opensea.io/api/v2/collections/{slug}/stats",
        headers={"X-API-KEY": OPENSEA_API_KEY}
    ).json()

def get_nft_listings(collection_slug: str, limit: int = 20):
    return requests.get(
        f"https://api.opensea.io/api/v2/listings/collection/{collection_slug}/best",
        headers={"X-API-KEY": OPENSEA_API_KEY},
        params={"limit": limit}
    ).json()

# ERC-721 NFT Minting
NFT_CONTRACT = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract MaarsNFT is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    mapping(uint256 => string) private _tokenURIs;
    
    constructor() ERC721("MAARS NFT", "MAARSNFT") {}
    
    function mint(address to, string memory tokenURI) public returns (uint256) {
        _tokenIds.increment();
        uint256 newId = _tokenIds.current();
        _mint(to, newId);
        _tokenURIs[newId] = tokenURI;
        return newId;
    }
}
"""
```

## Tokenomics Analysis
```python
TOKENOMICS_ANALYSIS_PROMPT = """
Analyze the tokenomics for: {project_name}

Token: {token_symbol}
Total Supply: {total_supply}
Allocation:
{allocation_breakdown}

Vesting schedule:
{vesting_schedule}

Evaluate:
1. DISTRIBUTION HEALTH: Team/investor vs community balance
2. INFLATION SCHEDULE: Emission rate, dilution impact
3. UTILITY: Token use cases, demand drivers
4. SELL PRESSURE: When do VC/team tokens unlock?
5. RED FLAGS: Centralization, anonymous team, rug risk
6. FAIR LAUNCH SCORE: 1-10

Compare to: {comparable_projects}
"""
```

## Crypto Market Data
```python
# CoinGecko API (free tier)
import requests

def get_crypto_price(coin_id: str, currency: str = "usd"):
    return requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": coin_id, "vs_currencies": currency, "include_24hr_change": True}
    ).json()

def get_market_data(limit: int = 100):
    return requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={"vs_currency": "usd", "order": "market_cap_desc",
                "per_page": limit, "sparkline": True}
    ).json()

# Fear & Greed Index
def get_fear_greed():
    return requests.get("https://api.alternative.me/fng/").json()
```

## Models to Use
- **Smart contract audit**: `claude-opus-4-6` (best at subtle Solidity bugs)
- **Tokenomics analysis**: `claude-opus-4-6` + `gpt-4o`
- **On-chain data SQL**: `gpt-4o` (Dune/The Graph query writing)
- **Market analysis**: `perplexity/sonar-pro` (real-time prices + news)
- **Trading bot logic**: `claude-sonnet-4-6` (strategy → code)
- **Whitepaper summary**: `moonshot/kimi-latest` (1M context for long docs)
