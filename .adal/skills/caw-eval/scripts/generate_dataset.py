#!/usr/bin/env python3
"""
Script 1: 生成 CAW Agent 评测数据集并上传到 Langfuse（dataset project）

用法:
    python generate_dataset.py [--dataset-name NAME] [--dry-run]
                               [--public-key KEY] [--secret-key KEY] [--host URL]

功能:
    根据 SCENARIO_RULES 中定义的场景规则展开测试用例，以 Langfuse Dataset
    格式上传（通过 Langfuse SDK 直接写入）。每条规则描述一类场景的评分标准模板
    和各难度变体参数；expand_rules() 将规则展开为完整的 input/expected/metadata 结构。

规则结构:
    id             - 规则编号（01-09），展开后 item ID 格式: E2E-{id}{difficulty}
    operation_type - 操作类型
    category       - 场景分类标签
    description    - 人类可读的场景说明
    eval_criteria  - S1-S3 各阶段评分标准（s1: 意图, s2: pact, s3: 执行）
    variants       - 各难度变体（L1/L2/L3），含 user_message / pact_hints / sN_overrides

数据集 project 凭证（优先级）:
    --public-key / --secret-key / --host
    LANGFUSE_DATASET_PUBLIC_KEY / LANGFUSE_DATASET_SECRET_KEY / LANGFUSE_DATASET_HOST
    LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST（通用回退）
    内置默认值（sandbox dataset project）
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 自动加载同目录下的 .env（不覆盖已设置的环境变量）
load_dotenv(Path(__file__).parent / ".env", override=False)

_DEFAULT_HOST = "https://langfuse.1cobo.com"


def _dataset_langfuse_config(
    public_key: str = "",
    secret_key: str = "",
    host: str = "",
) -> tuple[str, str, str]:
    """Resolve Langfuse dataset project credentials.

    Priority: explicit arg → LANGFUSE_DATASET_* → LANGFUSE_* → .env file.
    """
    def _pick(arg: str, specific: str, generic: str) -> str:
        return arg or os.environ.get(specific, "") or os.environ.get(generic, "")

    pub = _pick(public_key, "LANGFUSE_DATASET_PUBLIC_KEY", "LANGFUSE_PUBLIC_KEY")
    sec = _pick(secret_key, "LANGFUSE_DATASET_SECRET_KEY", "LANGFUSE_SECRET_KEY")
    hst = _pick(host, "LANGFUSE_DATASET_HOST", "LANGFUSE_HOST") or _DEFAULT_HOST
    if not pub or not sec:
        print("[WARN] Langfuse dataset-project credentials not set. "
              "Set LANGFUSE_DATASET_PUBLIC_KEY + LANGFUSE_DATASET_SECRET_KEY "
              "in .env or environment variables.")
    return pub, sec, hst


# ── 场景规则 ─────────────────────────────────────────────────────────────────
#
# 规则说明：
#   eval_criteria  - S1-S3 评分基线（s1/s2/s3，各难度共享）
#   variants[*].sN_overrides - 覆盖该难度特有的差异字段（仅 s1-s3）
#   expand_rules() 将规则展开为完整的 DATASET_ITEMS
#
# 测试环境：sandbox 测试网（EVM: Base Sepolia / Ethereum Sepolia；SOL: devnet）
# 操作金额：较小，符合测试网使用习惯

SCENARIO_RULES: list[dict] = [
    # ── 01 单链转账 ──────────────────────────────────────────────────────────
    {
        "id": "01",
        "operation_type": "transfer",
        "category": "transfer",
        "description": "单链资产转账：识别代币/金额/目标地址/链，创建 single_transaction Pact 后执行",
        "eval_criteria": {
            "s1": {
                "operation_type": "transfer",
                "key_entities": ["token", "amount", "to_address", "chain"],
                "constraints": [],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["check_balance", "create_pact", "execute_transfer"],
                "dependencies": [],
                "protocol": None,
            },
            "s3": {
                "pact_type": "single_transaction",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["native_token", "simple", "evm"],
                "user_message": "转 0.001 ETH 到 0xabcdef1234567890abcdef1234567890abcdef12",
                "pact_hints": {"token": "ETH", "amount": "0.001", "chain": "base"},
                "success_criteria": "agent calls caw tx transfer with correct params on Base",
                "s1_overrides": {
                    "key_entities": {"token": "ETH", "amount": "0.001",
                                     "to_address": "0xabcdef1234567890abcdef1234567890abcdef12",
                                     "chain": "base"},
                },
                "s3_overrides": {
                    "policy": {"token": "ETH", "max_amount": "0.001", "chain": "base"},
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["erc20", "specify_chain", "evm"],
                "user_message": "把 5 USDC 转到 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef，用 Base 链",
                "pact_hints": {"token": "USDC", "amount": "5", "chain": "base"},
                "success_criteria": "agent uses Base chain for ERC-20 USDC transfer",
                "s1_overrides": {
                    "key_entities": {"token": "USDC", "amount": "5",
                                     "to_address": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                                     "chain": "base"},
                    "constraints": ["chain=base explicitly specified"],
                },
                "s3_overrides": {
                    "policy": {"token": "USDC", "max_amount": "5", "chain": "base"},
                },
            },
            {
                "difficulty": "L3",
                "chain": "solana",
                "tags": ["solana", "spl_token", "devnet"],
                "user_message": "发 1 USDC 到 HN7cABrd5bkhDg2YNGz5oQqWzHGtBmPMgFNqXpBFVKMt，走 Solana",
                "pact_hints": {"token": "USDC", "amount": "1", "chain": "solana"},
                "success_criteria": "agent handles Solana SPL token transfer with correct address format",
                "s1_overrides": {
                    "key_entities": {"token": "USDC", "amount": "1",
                                     "to_address": "HN7cABrd5bkhDg2YNGz5oQqWzHGtBmPMgFNqXpBFVKMt",
                                     "chain": "solana"},
                    "constraints": ["solana SPL token; address format differs from EVM"],
                },
                "s2_overrides": {"steps": ["check_solana_balance", "transfer_spl_token"]},
                "s3_overrides": {"policy": {"token": "USDC", "chain": "solana"}},
            },
        ],
    },

    # ── 02 DEX Swap ──────────────────────────────────────────────────────────
    {
        "id": "02",
        "operation_type": "swap",
        "category": "dex_swap",
        "description": "DEX 兑换：识别输入/输出代币、滑点约束、协议选择，生成 approve+swap 多步 Pact",
        "eval_criteria": {
            "s1": {
                "operation_type": "swap",
                "key_entities": ["token_in", "amount_in", "token_out"],
                "constraints": [],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["approve_token_in", "execute_swap"],
                "dependencies": ["approve_before_swap"],
                "protocol": "default_dex",
            },
            "s3": {
                "pact_type": "multi_transaction",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["approve_required", "default_protocol", "evm"],
                "user_message": "用 2 USDC 换 ETH（Base 链）",
                "pact_hints": {"token_in": "USDC", "token_out": "ETH", "amount_in": "2", "chain": "base"},
                "success_criteria": "agent generates approve + swap transaction sequence on Base",
                "s1_overrides": {
                    "key_entities": {"token_in": "USDC", "amount_in": "2", "token_out": "ETH",
                                     "chain": "base"},
                },
                "s3_overrides": {
                    "policy": {"approve": "USDC",
                               "swap": {"token_in": "USDC", "token_out": "ETH",
                                        "amount_in": "2", "chain": "base"}},
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["specify_protocol", "slippage_constraint", "evm"],
                "user_message": "在 Base 上用 Uniswap V3 把 3 USDC 换成 ETH，滑点不超过 1%",
                "pact_hints": {"token_in": "USDC", "token_out": "ETH", "amount_in": "3",
                               "chain": "base", "protocol": "uniswap_v3", "slippage_max": "1%"},
                "success_criteria": "agent specifies correct chain, protocol, and slippage constraint",
                "s1_overrides": {
                    "key_entities": {"token_in": "USDC", "amount_in": "3", "token_out": "ETH",
                                     "chain": "base", "protocol": "uniswap_v3", "slippage": "1%"},
                    "constraints": ["slippage <= 1%", "chain = base", "protocol = uniswap_v3"],
                },
                "s2_overrides": {"steps": ["approve_usdc", "swap_uniswap_v3"], "protocol": "uniswap_v3"},
                "s3_overrides": {
                    "policy": {"chain": "base", "protocol": "uniswap_v3",
                               "max_slippage": "1%", "token_in": "USDC", "amount_in": "3"},
                },
            },
            {
                "difficulty": "L3",
                "chain": "solana",
                "tags": ["solana", "jupiter", "route_optimization", "devnet"],
                "user_message": "用 Jupiter 在 Solana 上把 2 USDC 换 SOL，最优路由",
                "pact_hints": {"token_in": "USDC", "token_out": "SOL",
                               "chain": "solana", "protocol": "jupiter", "amount_in": "2"},
                "success_criteria": "agent handles Solana DEX swap via Jupiter with route optimization",
                "s1_overrides": {
                    "key_entities": {"token_in": "USDC", "amount_in": "2", "token_out": "SOL",
                                     "chain": "solana", "protocol": "jupiter"},
                    "constraints": ["optimize route"],
                },
                "s2_overrides": {
                    "steps": ["get_jupiter_quote", "execute_swap"],
                    "dependencies": [],
                    "protocol": "jupiter",
                },
                "s3_overrides": {
                    "pact_type": "single_transaction",
                    "policy": {"chain": "solana", "protocol": "jupiter",
                               "token_in": "USDC", "amount_in": "2"},
                },
            },
        ],
    },

    # ── 03 DeFi Lending ──────────────────────────────────────────────────────
    {
        "id": "03",
        "operation_type": "lend",
        "category": "lending",
        "description": "Aave V3 存款/借款/还款：识别 approve + action 依赖，必要时先查仓位",
        "eval_criteria": {
            "s1": {
                "operation_type": "lend",
                "key_entities": ["action", "token", "amount", "protocol"],
                "constraints": [],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["approve_token", "aave_action"],
                "dependencies": ["approve_before_action"],
                "protocol": "aave_v3",
            },
            "s3": {
                "pact_type": "multi_transaction",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["aave", "deposit", "evm"],
                "user_message": "把 3 USDC 存到 Aave（Base 链）",
                "pact_hints": {"action": "deposit", "token": "USDC",
                               "amount": "3", "protocol": "aave_v3", "chain": "base"},
                "success_criteria": "agent generates approve + Aave deposit transaction on Base",
                "s1_overrides": {
                    "key_entities": {"action": "deposit", "token": "USDC",
                                     "amount": "3", "protocol": "aave_v3", "chain": "base"},
                },
                "s3_overrides": {
                    "policy": {"protocol": "aave_v3", "action": "deposit",
                               "token": "USDC", "amount": "3", "chain": "base"},
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["aave", "deposit", "borrow", "collateral", "evm"],
                "user_message": "存 0.005 ETH 到 Aave 作为抵押，借出 2 USDC",
                "pact_hints": {"steps": ["deposit_eth", "borrow_usdc"],
                               "collateral": {"token": "ETH", "amount": "0.005"},
                               "borrow": {"token": "USDC", "amount": "2"},
                               "chain": "base"},
                "success_criteria": "agent plans deposit + borrow sequence, checks health factor",
                "s1_overrides": {
                    "key_entities": {"collateral": {"token": "ETH", "amount": "0.005"},
                                     "borrow": {"token": "USDC", "amount": "2"},
                                     "protocol": "aave_v3", "chain": "base"},
                    "constraints": ["health_factor >= 1.5"],
                    "multi_intent": True,
                },
                "s2_overrides": {
                    "steps": ["aave_deposit_eth", "check_health_factor", "aave_borrow_usdc"],
                    "dependencies": ["deposit_before_borrow"],
                },
                "s3_overrides": {
                    "policy": {"deposit": {"token": "ETH", "amount": "0.005"},
                               "borrow": {"token": "USDC", "amount": "2"},
                               "health_factor_min": "1.5", "chain": "base"},
                },
            },
            {
                "difficulty": "L3",
                "chain": "base",
                "tags": ["aave", "withdraw", "repay", "balance_dependent", "evm"],
                "user_message": "把 Aave 里的 USDC 全部取出来还贷（Base 链）",
                "pact_hints": {"steps": ["query_balance", "repay", "withdraw"],
                               "requires_query": True, "chain": "base"},
                "success_criteria": "agent queries Aave balance first, then plans repay + withdraw",
                "s1_overrides": {
                    "key_entities": {"action": "withdraw_and_repay",
                                     "token": "USDC", "amount": "all", "chain": "base"},
                    "constraints": ["requires_balance_query_first"],
                    "multi_intent": True,
                },
                "s2_overrides": {
                    "steps": ["query_aave_usdc_balance", "repay_debt_if_any", "withdraw_remaining"],
                    "dependencies": ["query_first", "repay_before_withdraw"],
                },
                "s3_overrides": {
                    "policy": {"requires_balance_query": True, "actions": ["repay", "withdraw"],
                               "chain": "base"},
                },
            },
        ],
    },

    # ── 04 DCA 策略 ──────────────────────────────────────────────────────────
    {
        "id": "04",
        "operation_type": "dca",
        "category": "dca",
        "description": "定期定投：识别频率/金额/币对/期限约束，创建 recurring Pact 并配置 usage_limit",
        "eval_criteria": {
            "s1": {
                "operation_type": "dca",
                "key_entities": ["token_in", "token_out", "amount_per_period", "frequency"],
                "constraints": [],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["setup_dca_strategy"],
                "dependencies": [],
                "note": "recurring pact required; not a single transaction",
            },
            "s3": {
                "pact_type": "recurring",
                "policy": {},
                "usage_limit": {"rolling_24h": "amount_per_period"},
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["daily", "open_ended", "evm"],
                "user_message": "每天买 1 USDC 的 ETH（Base 链）",
                "pact_hints": {"token_in": "USDC", "token_out": "ETH",
                               "amount_per_period": "1", "period": "daily", "chain": "base"},
                "success_criteria": "agent sets up recurring daily DCA without end date",
                "s1_overrides": {
                    "key_entities": {"token_in": "USDC", "token_out": "ETH",
                                     "amount_per_period": "1", "frequency": "daily"},
                    "constraints": ["no end date"],
                },
                "s3_overrides": {
                    "policy": {"token_in": "USDC", "amount_per_period": "1",
                               "frequency": "daily", "chain": "base"},
                    "usage_limit": {"rolling_24h": "1"},
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["weekly", "duration_limited", "amount_cap", "evm"],
                "user_message": "每周买 2 USDC 的 ETH，持续 1 个月，单次不超过 3 USDC",
                "pact_hints": {"token_in": "USDC", "token_out": "ETH", "amount_per_period": "2",
                               "period": "weekly", "duration": "1_month", "max_per_tx": "3",
                               "chain": "base"},
                "success_criteria": "agent correctly sets period, duration, and per-tx limit",
                "s1_overrides": {
                    "key_entities": {"token_in": "USDC", "token_out": "ETH",
                                     "amount_per_period": "2", "frequency": "weekly",
                                     "duration": "1_month", "max_per_tx": "3"},
                    "constraints": ["duration=1month", "per_tx_cap=3"],
                },
                "s2_overrides": {"note": "must encode duration limit and per-tx amount cap"},
                "s3_overrides": {
                    "policy": {"token_in": "USDC", "amount_per_period": "2",
                               "frequency": "weekly", "max_per_tx": "3", "chain": "base"},
                    "usage_limit": {"rolling_24h": "3", "end_date": "+1_month"},
                },
            },
        ],
    },

    # ── 05 跨链 Bridge ───────────────────────────────────────────────────────
    {
        "id": "05",
        "operation_type": "bridge",
        "category": "bridge",
        "description": "跨链桥接：识别源链/目标链/代币/金额，处理 approve + bridge 序列",
        "eval_criteria": {
            "s1": {
                "operation_type": "bridge",
                "key_entities": ["token", "amount", "from_chain", "to_chain"],
                "constraints": [],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["approve_token", "bridge_to_target_chain"],
                "dependencies": ["approve_before_bridge"],
                "protocol": "bridge_default",
            },
            "s3": {
                "pact_type": "multi_transaction",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["cross_chain", "usdc", "evm"],
                "user_message": "把 2 USDC 从 Ethereum 转到 Base",
                "pact_hints": {"token": "USDC", "amount": "2",
                               "from_chain": "ethereum", "to_chain": "base"},
                "success_criteria": "agent generates bridge transaction with correct chains",
                "s1_overrides": {
                    "key_entities": {"token": "USDC", "amount": "2",
                                     "from_chain": "ethereum", "to_chain": "base"},
                },
                "s3_overrides": {
                    "policy": {"bridge": {"token": "USDC", "from_chain": "ethereum",
                                          "to_chain": "base", "amount": "2"}},
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["cross_chain", "bridge_then_swap", "evm"],
                "user_message": "把 0.001 ETH 从 Ethereum 桥接到 Base，然后换成 USDC",
                "pact_hints": {"steps": ["bridge_eth", "swap_eth_to_usdc"],
                               "chains": ["ethereum", "base"],
                               "eth_amount": "0.001"},
                "success_criteria": "agent plans bridge + swap sequence, handles chain dependency",
                "s1_overrides": {
                    "operation_type": "multi_step",
                    "key_entities": {
                        "bridge": {"token": "ETH", "amount": "0.001",
                                   "from": "ethereum", "to": "base"},
                        "swap": {"token_in": "ETH", "token_out": "USDC", "chain": "base"},
                    },
                    "multi_intent": True,
                },
                "s2_overrides": {
                    "steps": ["bridge_eth_to_base", "swap_eth_to_usdc_on_base"],
                    "dependencies": ["bridge_must_complete_before_swap"],
                    "protocol": "bridge + default_dex",
                },
                "s3_overrides": {
                    "policy": {
                        "bridge": {"token": "ETH", "amount": "0.001",
                                   "chains": ["ethereum", "base"]},
                        "swap": {"token_in": "ETH", "token_out": "USDC", "chain": "base"},
                    },
                },
            },
        ],
    },

    # ── 06 收益优化 ──────────────────────────────────────────────────────────
    {
        "id": "06",
        "operation_type": "yield",
        "category": "yield",
        "description": "收益率查询与优化：对比多链利率，规划 withdraw+bridge+deposit 迁移路径",
        "eval_criteria": {
            "s1": {
                "operation_type": "query",
                "key_entities": ["token", "action"],
                "constraints": ["read_only"],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["query_rates"],
                "dependencies": [],
                "note": "query-only; no execution",
            },
            "s3": {
                "pact_type": "none",
                "policy": {},
                "usage_limit": None,
                "note": "No pact needed for query-only operation",
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "multi",
                "tags": ["query_only", "yield_comparison", "evm"],
                "user_message": "帮我看看哪个链上 USDC 存款利率最高",
                "pact_hints": {"action": "compare_yield_rates", "token": "USDC"},
                "success_criteria": "agent queries yield rates across chains without executing transactions",
                "s1_overrides": {
                    "key_entities": {"action": "compare_yield_rates", "token": "USDC"},
                    "constraints": ["read_only", "no_transaction"],
                },
                "s2_overrides": {"steps": ["query_aave_rates_multi_chain"]},
            },
            {
                "difficulty": "L2",
                "chain": "multi",
                "tags": ["migrate_yield", "multi_step", "evm"],
                "user_message": "把 Aave Ethereum 上的 USDC（假设 5 USDC）转到 Base 的 Aave，那边利率更高",
                "pact_hints": {"steps": ["aave_withdraw", "bridge_usdc", "aave_deposit"],
                               "chains": ["ethereum", "base"], "amount": "5"},
                "success_criteria": "agent plans withdraw + bridge + deposit sequence",
                "s1_overrides": {
                    "operation_type": "multi_step",
                    "key_entities": {
                        "from": {"protocol": "aave", "chain": "ethereum", "token": "USDC"},
                        "to": {"protocol": "aave", "chain": "base", "token": "USDC"},
                    },
                    "constraints": ["requires_current_balance_query"],
                    "multi_intent": True,
                },
                "s2_overrides": {
                    "steps": ["query_aave_eth_position", "aave_withdraw_eth",
                              "bridge_usdc_to_base", "aave_deposit_base"],
                    "dependencies": ["query_first", "withdraw_before_bridge", "bridge_before_deposit"],
                    "protocol": "aave_v3 + bridge",
                },
                "s3_overrides": {
                    "pact_type": "multi_transaction",
                    "policy": {"actions": ["query", "withdraw", "bridge", "deposit"],
                               "token": "USDC"},
                },
            },
        ],
    },

    # ── 07 多步骤复合操作 ────────────────────────────────────────────────────
    {
        "id": "07",
        "operation_type": "multi_step",
        "category": "multi_step",
        "description": "复合多意图：识别子意图依赖顺序，规划跨协议执行计划",
        "eval_criteria": {
            "s1": {
                "operation_type": "multi_step",
                "key_entities": ["sub_operations"],
                "constraints": ["sequential execution"],
                "multi_intent": True,
            },
            "s2": {
                "steps": ["step1", "step2"],
                "dependencies": ["step1_before_step2"],
                "protocol": "multi_protocol",
            },
            "s3": {
                "pact_type": "multi_transaction",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["swap_then_transfer", "evm"],
                "user_message": "把 0.001 ETH 换成 USDC，然后转给 0xabcdef1234567890abcdef1234567890abcdef12",
                "pact_hints": {"steps": ["swap_eth_to_usdc", "transfer_usdc"],
                               "eth_amount": "0.001"},
                "success_criteria": "agent plans swap + transfer in correct order on Base",
                "s1_overrides": {
                    "key_entities": {
                        "swap": {"token_in": "ETH", "amount": "0.001", "token_out": "USDC"},
                        "transfer": {"token": "USDC",
                                     "to": "0xabcdef1234567890abcdef1234567890abcdef12"},
                    },
                },
                "s2_overrides": {
                    "steps": ["swap_eth_to_usdc", "transfer_usdc_to_recipient"],
                    "dependencies": ["swap_before_transfer"],
                    "protocol": "default_dex",
                },
                "s3_overrides": {
                    "policy": {
                        "swap": {"token_in": "ETH", "amount": "0.001", "token_out": "USDC"},
                        "transfer": {"token": "USDC", "to": "0xabcdef..."},
                    },
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["swap_lend_dca", "balance_split", "evm"],
                "user_message": "用一半 ETH 换 USDC 存 Aave，剩下的设置每周定投 USDC（Base 链）",
                "pact_hints": {"steps": ["swap_half_eth", "aave_deposit", "setup_dca"],
                               "requires_balance_query": True, "chain": "base"},
                "success_criteria": "agent handles 3-step operation: swap + lend + DCA setup",
                "s1_overrides": {
                    "key_entities": {
                        "amount_type": "half_eth",
                        "op1": "swap_eth_to_usdc",
                        "op2": "aave_deposit",
                        "op3": "setup_weekly_dca",
                    },
                    "constraints": ["balance_dependent", "split_calculation"],
                },
                "s2_overrides": {
                    "steps": ["query_eth_balance", "calculate_half",
                              "swap_half_eth_to_usdc", "aave_deposit_usdc", "setup_dca"],
                    "dependencies": ["query_first", "swap_before_deposit", "deposit_before_dca"],
                    "protocol": "default_dex + aave_v3",
                },
                "s3_overrides": {"pact_type": "multi_transaction+recurring"},
            },
        ],
    },

    # ── 08 错误恢复 ──────────────────────────────────────────────────────────
    {
        "id": "08",
        "operation_type": "error_handling",
        "category": "error_handling",
        "description": "异常场景：余额不足/全仓操作等，Agent 应优雅拒绝或调整并给出明确解释",
        "eval_criteria": {
            "s1": {
                "operation_type": "transfer",
                "key_entities": ["token", "amount"],
                "constraints": ["error_condition_present"],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["detect_error", "refuse_or_adjust"],
                "dependencies": [],
                "should_abort": True,
            },
            "s3": {
                "pact_type": "none",
                "policy": {},
                "usage_limit": None,
                "note": "should refuse before creating pact",
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "base",
                "tags": ["insufficient_balance", "safe_failure", "evm"],
                "user_message": "转 9999 USDC 到 0xabcdef1234567890abcdef1234567890abcdef12（Base 链）",
                "pact_hints": {"expected_outcome": "insufficient_balance", "should_refuse": True},
                "success_criteria": "agent detects insufficient USDC balance and explains clearly",
                "s1_overrides": {
                    "key_entities": {"token": "USDC", "amount": "9999",
                                     "chain": "base"},
                    "constraints": ["insufficient_balance_detected"],
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["all_balance", "gas_reservation", "evm"],
                "user_message": "把我所有的 ETH 换成 USDC（Base 链）",
                "pact_hints": {"operation_type": "swap", "amount_type": "all",
                               "should_reserve_gas": True, "chain": "base"},
                "success_criteria": "agent reserves gas for transaction and doesn't swap 100% of ETH",
                "s1_overrides": {
                    "operation_type": "swap",
                    "key_entities": {"token_in": "ETH", "amount_type": "all",
                                     "token_out": "USDC", "chain": "base"},
                    "constraints": ["must_reserve_gas"],
                },
                "s2_overrides": {
                    "steps": ["calculate_max_swappable_eth", "swap_eth_minus_gas_reserve"],
                    "should_abort": False,
                    "note": "must subtract gas reserve from ETH balance",
                },
                "s3_overrides": {"pact_type": "single_transaction"},
            },
        ],
    },

    # ── 09 边缘情况 ──────────────────────────────────────────────────────────
    {
        "id": "09",
        "operation_type": "edge_case",
        "category": "edge_case",
        "description": "极端/异常输入：不支持链、高风险地址、超范围金额，Agent 应正确识别并处理",
        "eval_criteria": {
            "s1": {
                "operation_type": "transfer",
                "key_entities": ["token", "address_or_chain"],
                "constraints": ["edge_condition"],
                "multi_intent": False,
            },
            "s2": {
                "steps": ["refuse_immediately"],
                "dependencies": [],
                "should_abort": True,
            },
            "s3": {
                "pact_type": "none",
                "policy": {},
                "usage_limit": None,
            },
        },
        "variants": [
            {
                "difficulty": "L1",
                "chain": "tron",
                "tags": ["unsupported_chain"],
                "user_message": "在 Tron 链上转 1 USDT",
                "pact_hints": {"expected_outcome": "unsupported_chain", "should_refuse": True},
                "success_criteria": "agent clearly explains Tron is not supported",
                "s1_overrides": {
                    "key_entities": {"token": "USDT", "amount": "1", "chain": "tron"},
                    "constraints": ["unsupported_chain"],
                },
            },
            {
                "difficulty": "L2",
                "chain": "base",
                "tags": ["zero_address", "risk_warning", "evm"],
                "user_message": "转 1 USDC 到 0x0000000000000000000000000000000000000000",
                "pact_hints": {"expected_outcome": "zero_address_warning", "should_warn": True},
                "success_criteria": "agent warns about zero address risk and requests confirmation",
                "s1_overrides": {
                    "key_entities": {"token": "USDC", "amount": "1",
                                     "to_address": "0x0000000000000000000000000000000000000000"},
                    "constraints": ["high_risk_zero_address"],
                },
                "s2_overrides": {
                    "steps": ["detect_risk", "warn_user", "request_explicit_confirmation"],
                    "should_abort": False,
                    "note": "do not proceed without explicit user confirmation",
                },
                "s3_overrides": {"pact_type": "none_until_confirmed"},
            },
            {
                "difficulty": "L3",
                "chain": "base",
                "tags": ["unreasonable_amount", "safe_refusal", "evm"],
                "user_message": "转 99999999999 ETH 到 0xabcdef1234567890abcdef1234567890abcdef12",
                "pact_hints": {"expected_outcome": "unreasonable_amount", "should_refuse": True},
                "success_criteria": "agent identifies unreasonable amount and refuses",
                "s1_overrides": {
                    "key_entities": {"token": "ETH", "amount": "99999999999", "chain": "base"},
                    "constraints": ["amount_exceeds_total_eth_supply"],
                },
            },
        ],
    },
]


# ── 规则展开 ─────────────────────────────────────────────────────────────────

def expand_rules(rules: list[dict]) -> list[dict]:
    """
    根据 SCENARIO_RULES 展开生成完整的测试用例列表。

    对每条规则的每个难度变体：
      1. 从 eval_criteria 取各阶段基线
      2. 用 variant.sN_overrides 逐字段覆盖
      3. 组装 input / expected / metadata
    """
    items: list[dict] = []
    for rule in rules:
        rule_id = rule["id"]
        default_criteria: dict = rule.get("eval_criteria", {})
        for variant in rule.get("variants", []):
            difficulty = variant["difficulty"]
            item_id = f"E2E-{rule_id}{difficulty}"

            # Merge stage criteria: default baseline + variant-specific overrides
            stage_criteria: dict = {}
            for stage in ("s1", "s2", "s3"):
                base = dict(default_criteria.get(stage, {}))
                override = variant.get(f"{stage}_overrides", {})
                stage_criteria[stage] = {**base, **override}

            pact_hints = {
                "operation_type": rule["operation_type"],
                **variant.get("pact_hints", {}),
            }

            items.append({
                "id": item_id,
                "input": {
                    "user_message": variant["user_message"],
                },
                "expected": {
                    "pact_hints": pact_hints,
                    "success_criteria": variant.get("success_criteria", ""),
                    "stage_criteria": stage_criteria,
                },
                "metadata": {
                    "difficulty": difficulty,
                    "operation_type": rule["operation_type"],
                    "chain": variant.get("chain", "base"),
                    "category": rule["category"],
                    "tags": variant.get("tags", []),
                },
            })
    return items


# 展开后的完整测试用例列表（供 generate_dataset() 使用）
DATASET_ITEMS: list[dict] = expand_rules(SCENARIO_RULES)


# ── 上传逻辑 ─────────────────────────────────────────────────────────────────

def generate_dataset(
    dataset_name: str,
    public_key: str,
    secret_key: str,
    host: str = _DEFAULT_HOST,
    dry_run: bool = False,
) -> None:
    print(f"[INFO] Langfuse (dataset project): {host}")
    print(f"[INFO] Dataset  : {dataset_name}")
    print(f"[INFO] Rules    : {len(SCENARIO_RULES)} scenarios")
    print(f"[INFO] Items    : {len(DATASET_ITEMS)} total")

    if dry_run:
        print("\n[DRY-RUN] Items to upload:")
        for item in DATASET_ITEMS:
            meta = item["metadata"]
            print(f"  {item['id']:12s} | {meta['difficulty']} | "
                  f"{meta['operation_type']:15s} | {meta['chain']:10s} | "
                  f"{', '.join(meta.get('tags', []))}")
        return

    from langfuse import Langfuse

    lf = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

    # Create dataset
    try:
        lf.create_dataset(
            name=dataset_name,
            description=(
                "CAW Agent E2E 评测数据集 | "
                "覆盖 transfer/swap/lend/dca/bridge/yield/multi_step/error/edge 场景，"
                "每条用例含 S1-S3 各阶段期望评分标准"
            ),
            metadata={
                "version": "3.0",
                "source": "02-全流程测评方案.md",
                "rules": len(SCENARIO_RULES),
            },
        )
        print(f"[OK] Dataset '{dataset_name}' created/confirmed")
    except Exception as e:
        print(f"[WARN] Dataset creation: {e}")

    # Upload items
    ok_count = 0
    for item in DATASET_ITEMS:
        try:
            lf.create_dataset_item(
                dataset_name=dataset_name,
                id=item["id"],
                input=item["input"],
                expected_output=item["expected"],
                metadata=item["metadata"],
            )
            print(f"  [+] {item['id']}")
            ok_count += 1
        except Exception as e:
            print(f"  [ERR] {item['id']}: {e}")

    lf.flush()
    print(f"\n[DONE] Uploaded {ok_count}/{len(DATASET_ITEMS)} items to '{dataset_name}'")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-name",
        default="caw-agent-eval-v1",
        help="Langfuse dataset name (default: caw-agent-eval-v1)",
    )
    parser.add_argument(
        "--public-key",
        default="",
        help="Langfuse dataset project public key (or set LANGFUSE_DATASET_PUBLIC_KEY / LANGFUSE_PUBLIC_KEY)",
    )
    parser.add_argument(
        "--secret-key",
        default="",
        help="Langfuse dataset project secret key (or set LANGFUSE_DATASET_SECRET_KEY / LANGFUSE_SECRET_KEY)",
    )
    parser.add_argument(
        "--host",
        default="",
        help="Langfuse host URL (or set LANGFUSE_DATASET_HOST / LANGFUSE_HOST)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print items without uploading",
    )
    args = parser.parse_args()

    public_key, secret_key, host = _dataset_langfuse_config(
        args.public_key, args.secret_key, args.host,
    )

    generate_dataset(args.dataset_name, public_key=public_key, secret_key=secret_key,
                     host=host, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
