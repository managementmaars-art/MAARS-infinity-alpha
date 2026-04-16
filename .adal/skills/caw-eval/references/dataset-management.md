# 数据集管理

创建、选择、更新 CAW 评测数据集。当用户需要创建新数据集或修改测试用例时，按以下步骤操作。

---

## Dataset Structure

每个 dataset item 的格式：

```json
{
  "id": "E2E-01L1",
  "input": {
    "user_message": "帮我把 0.001 ETH 转到 0x742d35Cc6634C0532925a3b8D4C9A8a6b7c8f9e1 (Ethereum Sepolia)"
  },
  "expected_output": {
    "pact_hints": {
      "operation_type": "transfer",
      "token": "SETH",
      "chain": "SETH",
      "amount": "0.001"
    },
    "success_criteria": "agent creates pact, calls caw tx transfer with correct params"
  },
  "metadata": {
    "difficulty": "L1",
    "operation_type": "transfer",
    "chain": "ethereum_sepolia",
    "category": "transfer",
    "tags": ["native_token", "testnet"]
  }
}
```

**Item ID 格式：** `E2E-{scenario_id}{difficulty}` — e.g. `E2E-01L1`, `E2E-03L2`

**测试网覆盖：**
- EVM: Ethereum Sepolia (`SETH`), Base Sepolia (`TBASE_SETH`)
- Solana: Devnet (`SOLDEV_SOL`)

---

## 已有数据集

| 数据集 | case 数 | 说明 |
|--------|:-------:|------|
| `caw-agent-eval-seth-v2` | 14 | **默认**，SETH 测试链，含完整 expected_output |
| `caw-agent-eval-seth-v1` | 14 | 旧版，expected_output 不完整 |
| `caw-agent-eval-v1` | 22 | 主网场景，sandbox 环境无法执行大部分 case |

```bash
# 验证数据集可访问
cd <repo>/cobo-agent-wallet
.venv/bin/python sdk/skills/caw-eval/scripts/run_eval_cc.py prepare \
  --dataset-name caw-agent-eval-seth-v2
```

---

## 创建 / 重新上传数据集

当需要创建新数据集或重置现有数据集时：

```bash
cd <repo>/cobo-agent-wallet

# 预览（不上传）
.venv/bin/python sdk/skills/caw-eval/scripts/generate_dataset.py --dry-run

# 上传到默认数据集 caw-agent-eval-v1
.venv/bin/python sdk/skills/caw-eval/scripts/generate_dataset.py

# 指定不同的数据集名称
.venv/bin/python sdk/skills/caw-eval/scripts/generate_dataset.py \
  --dataset-name caw-agent-eval-v2

# 使用自定义 Langfuse 凭证
.venv/bin/python sdk/skills/caw-eval/scripts/generate_dataset.py \
  --public-key pk-lf-xxx --secret-key sk-lf-xxx
```

**注意：** 如果数据集已存在，重新上传会用相同 ID 覆盖已有 items（Langfuse SDK upsert 语义）。

---

## 修改测试场景

测试场景定义在 `scripts/generate_dataset.py` 的 `SCENARIO_RULES` 列表中。每条规则对应一类场景，包含多个难度变体（L1/L2/L3）。

**场景覆盖（22 个 item）：**

| ID | 场景 | 变体 | 说明 |
|----|------|------|------|
| 01 | transfer | L1/L2/L3 | ETH/ERC-20/SOL 转账 |
| 02 | dex_swap | L1/L2/L3 | Uniswap/指定路由/Jupiter Swap |
| 03 | lending | L1/L2/L3 | Aave 存款/存借/提取还款 |
| 04 | dca | L1/L2 | 日/周定投 |
| 05 | bridge | L1/L2 | 跨链/桥接+Swap |
| 06 | yield | L1/L2 | 利率查询/收益迁移 |
| 07 | multi_step | L1/L2 | 复合操作 |
| 08 | error_handling | L1/L2 | 余额不足/全仓操作 |
| 09 | edge_case | L1/L2/L3 | 不支持链/零地址/天文数字 |

**修改步骤：**

1. 编辑 `scripts/generate_dataset.py` 中对应的 `SCENARIO_RULES` 条目
2. 用 `--dry-run` 预览展开结果
3. 重新上传到 Langfuse

```python
# generate_dataset.py 中的规则结构
{
    "id": "01",
    "operation_type": "transfer",
    "category": "transfer",
    "description": "...",
    "eval_criteria": {          # S1-S3 评分基线（s1/s2/s3，各难度共享）
        "s1": { "operation_type": "transfer", "key_entities": [...] },
        "s2": { "steps": [...] },
        # ...
    },
    "variants": [               # 各难度变体
        {
            "difficulty": "L1",
            "user_message": "帮我把 0.001 ETH 转到 ...",
            "pact_hints": { "operation_type": "transfer" },
            # sN_overrides: 覆盖该难度特有的 eval_criteria 差异字段
        },
    ],
}
```

---

## Adding New Items Manually

如需向已有数据集追加单个 item（不重新生成全部），可用 Langfuse SDK 直接写入：

```python
from langfuse import Langfuse

lf = Langfuse()
lf.create_dataset_item(
    dataset_name="caw-agent-eval-seth-v2",
    id="E2E-10L1",
    input={"user_message": "..."},
    expected_output={"pact_hints": {...}, "success_criteria": "..."},
    metadata={"difficulty": "L1", "operation_type": "...", "category": "..."},
)
lf.flush()
```

---

## Langfuse Default Credentials

凭证通过 `scripts/.env` 文件配置（复制 `scripts/.env.example` 填入真实值，`.env` 已 gitignore）。

| 变量 | 说明 |
|------|------|
| `LANGFUSE_DATASET_HOST` | Langfuse 服务地址（默认 `https://langfuse.1cobo.com`） |
| `LANGFUSE_DATASET_PUBLIC_KEY` | Dataset project 公钥（见 `.env.example`） |
| `LANGFUSE_DATASET_SECRET_KEY` | Dataset project 私钥（见 `.env.example`） |

覆盖优先级：CLI 参数 `--public-key`/`--secret-key` > `LANGFUSE_DATASET_*` > `LANGFUSE_*`。
