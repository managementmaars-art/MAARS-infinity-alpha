# CAW Skill 评测报告

**评测日期**：2026-04-11
**数据集**：caw-agent-eval-seth-v2（14 case，Ethereum Sepolia 测试链）
**执行模型**：Claude Sonnet（Sonnet 独立额度，不消耗主额度）
**评分模型**：Claude Sonnet（LLM-as-Judge）
**环境**：sandbox，wallet 已完整 onboard（signing_ready=true）

---

## 1. 总览

| 指标 | 分数 |
|------|:----:|
| **E2E 综合分** | **0.75** |
| S1 意图理解 | 0.93 |
| S2 Pact 协商 | 0.77 |
| S3 执行 | 0.79 |
| Task Completion | 0.61 |

**综合分计算**：`E2E = task_completion × 0.3 + (S1×0.15 + S2×0.45 + S3×0.4) × 0.7`

---

## 2. 逐 Case 评分

| Case | 类型 | S1 | S2 | S3 | TC | E2E | 结果 |
|------|------|:--:|:--:|:--:|:--:|:--:|------|
| E2E-05L1 | bridge L1 | 0.70 | 0.00 | 0.40 | 0.00 | **0.19** | 跨链桥不可行，直接放弃 |
| E2E-03L1 | lend L1 | 1.00 | 0.80 | 0.62 | 0.00 | 0.53 | Aave USDC ≠ Circle USDC，供应失败 |
| E2E-09L3 | edge L3 | 0.70 | 0.69 | 0.82 | 0.50 | 0.67 | 未主动识别天量金额，被余额不足拦截 |
| E2E-04L2 | dca L2 | 0.90 | 0.68 | 0.76 | 0.50 | 0.67 | DCA 首次 swap 成功 + 写了复用脚本 |
| E2E-04L1 | dca L1 | 1.00 | 0.83 | 0.72 | 0.50 | 0.72 | Pact+approve 成功，swap 因池子无流动性 revert |
| E2E-02L2 | swap L2 | 1.00 | 0.79 | 0.81 | 0.50 | 0.73 | Uniswap V3 上链但滑点保护未实现 |
| E2E-08L1 | error L1 | 0.90 | 0.82 | 0.87 | 0.50 | 0.75 | 正确报告余额不足 |
| E2E-01L3 | transfer L3 | 1.00 | 1.00 | 0.78 | 0.50 | 0.79 | Pact 正确，USDC 余额不足 |
| E2E-01L2 | transfer L2 | 1.00 | 1.00 | 0.88 | 0.50 | 0.82 | Pact 正确，USDC 余额不足 |
| E2E-02L1 | swap L1 | 1.00 | 0.77 | 0.84 | 1.00 | **0.88** | 先换 USDC 再执行 swap |
| E2E-03L2 | lend L2 | 1.00 | 0.73 | 0.91 | 1.00 | **0.89** | Aave 存 ETH+借 USDC 成功 |
| E2E-08L2 | error L2 | 0.85 | 0.86 | 0.83 | 1.00 | **0.89** | 保留 gas 后全量 swap 成功 |
| E2E-07L1 | multi_step L1 | 1.00 | 0.93 | 0.89 | 1.00 | **0.95** | swap+transfer 两步成功 |
| E2E-01L1 | transfer L1 | 1.00 | 0.93 | 0.94 | 1.00 | **0.96** | 交易成功上链 |

---

## 3. 运行指标分析

### 逐 Case 运行指标

| Case | 时长 | Tokens | 工具调用 | caw 命令 | pact submit | tx 命令 | 错误数 | TC |
|------|:----:|:------:|:-------:|:-------:|:-----------:|:------:|:-----:|:--:|
| E2E-08L1 error L1 | 0:58 | 30,269 | 8 | 5 | 2 | 1 | 2 | 0.5 |
| E2E-09L3 edge L3 | 1:03 | 33,594 | 9 | 6 | 3 | 1 | 2 | 0.5 |
| E2E-01L1 transfer L1 | 1:27 | 34,490 | 13 | 10 | 3 | 1 | 1 | 1.0 |
| E2E-01L2 transfer L2 | 1:27 | 34,070 | 12 | 9 | 3 | 1 | 2 | 0.5 |
| E2E-05L1 bridge L1 | 1:56 | 34,264 | 12 | 9 | 0 | 0 | 1 | 0.0 |
| E2E-01L3 transfer L3 | 2:43 | 38,584 | 16 | 10 | 3 | 1 | 2 | 0.5 |
| E2E-08L2 error L2 | 4:34 | 55,544 | 24 | 18 | 3 | 5 | 3 | 1.0 |
| E2E-07L1 multi_step L1 | 5:12 | 49,499 | 27 | 20 | 3 | 6 | 4 | 1.0 |
| E2E-02L2 swap L2 | 7:34 | 68,667 | 50 | 33 | 4 | 5 | 7 | 0.5 |
| E2E-03L2 lend L2 | 7:52 | 71,075 | 40 | 32 | 4 | 6 | 5 | 1.0 |
| E2E-04L2 dca L2 | 11:54 | 91,275 | 74 | 36 | 5 | 3 | 7 | 0.5 |
| E2E-02L1 swap L1 | 15:29 | 82,281 | 73 | 36 | 6 | 9 | 8 | 1.0 |
| E2E-03L1 lend L1 | 15:41 | 92,283 | 72 | 37 | 6 | 10 | 5 | 0.0 |
| E2E-04L1 dca L1 | 16:29 | 91,645 | 84 | 45 | 4 | 7 | 6 | 0.5 |
| **合计** | **94:19** | **807,540** | **514** | **306** | **49** | **56** | **55** | |
| **平均** | **6:44** | **57,681** | **36** | **21** | **3.5** | **4** | **3.9** | |

### 异常指标分析

#### caw 命令数异常（理想值：5-10，异常阈值：> 25）

简单操作（transfer/error/edge）的 caw 命令在 5-10 之间，属于正常。以下 case 明显偏高：

| Case | caw 命令 | 理想值 | 原因 | 解决办法 |
|------|:--------:|:-----:|------|---------|
| **E2E-04L1** dca L1 | **45** | ~10 | Agent 反复尝试不同 fee tier（3000/500）的 swap，每次都要重新构造 calldata；创建 DCA 脚本过程中多次调试 API 调用 | Skill 提供 Sepolia 上可用的 pool fee tier 列表，减少盲目尝试 |
| **E2E-03L1** lend L1 | **37** | ~8 | 混淆 Aave testnet USDC 和 Circle USDC，分别尝试 approve + supply 两条路径都失败，还尝试了 faucet mint | `caw recipe search` 返回正确的测试网合约地址 |
| **E2E-02L1** swap L1 | **36** | ~8 | 先用 SETH 换 USDC（额外的准备步骤），再执行目标 swap；中间 SwapRouter 地址错误导致多次重试 | Skill 明确 SwapRouter02 地址，避免试错 |
| **E2E-04L2** dca L2 | **36** | ~10 | Router 地址首次截断（缺末位 'E'），revoke 重建；脚本调试中 src_addr 参数多次出错 | `caw pact submit` 增加地址格式校验（42 字符） |
| **E2E-02L2** swap L2 | **33** | ~8 | 首次 pact 合约地址截断，revoke 重建；calldata 构造尝试了多个 function selector | 同上 |
| **E2E-03L2** lend L2 | **32** | ~8 | 首次 borrow 用了错误的 USDC 地址，revoke 后重建 pact | 同上（recipe 地址问题） |

**共性根因**：DeFi 操作中 Agent 需要**手动拼接合约地址和 calldata**，容易出错导致反复重试。每次重试都消耗额外的 caw 命令。

**统一解决办法**：
1. `caw recipe search` 返回完整的合约地址（含测试网），Agent 不需要自己搜索
2. `caw pact submit` 增加 `--policies` JSON 的前端校验（地址长度、JSON 格式）
3. Skill 中维护"常用合约地址 + function selector"速查表

---

#### pact submit 次数异常（理想值：1，异常阈值：> 3）

每个操作理想情况下只需 1 次 pact submit。以下 case 明显偏高（注：统计含 `caw schema pact submit` 查帮助被误计，实际 submit 次数略低于表中数字）：

| Case | pact submit（含 schema 查询） | 实际创建 pact 数 | 理想值 | 主要多余原因 |
|------|:---------------------------:|:--------------:|:-----:|------------|
| **E2E-02L1** swap L1 | 6 | **~4** | 1 | 地址错误重建 + tx_count 耗尽重建 + 前置 swap 独立 pact |
| **E2E-03L1** lend L1 | 6 | **~4** | 1 | Circle USDC vs Aave USDC 反复尝试，每次都新建 pact |
| **E2E-04L2** dca L2 | 5 | **~3** | 1 | Router 地址截断 → revoke → 重建 |
| **E2E-02L2** swap L2 | 4 | **~3** | 1 | 合约地址截断 → 新建 pact |
| **E2E-03L2** lend L2 | 4 | **~3** | 1 | USDC 地址错误 → tx_count 耗尽 → 新建 pact |

**注意**：大部分多余 pact 不是通过 `caw pact revoke` 产生的（显式 revoke 只有 2 次），而是**旧 pact 的 tx_count 被失败交易耗尽后自动 completed**，Agent 被迫创建新 pact 继续执行。这比 revoke 更浪费，因为 Agent 直到执行时才发现 pact 已完成。

**影响**：每次多余的 pact 会：
- 消耗用户等待时间（pact 审批 + 状态轮询）
- 消耗 API token
- 如果是 paired wallet，每次 submit 都需要用户在 Human App 上审批

**统一解决办法**：
1. **地址校验前置**：`caw pact submit` 校验 policies JSON 中的地址格式（42 字符 hex），格式错误时拒绝提交而不是提交后链上失败
2. **completion_conditions 预留**：Skill 指导 tx_count = 预期交易数 + 2（为重试预留额度），避免因 tx_count 耗尽而重建 pact
3. **recipe 地址准确**：`caw recipe search` 返回的地址区分主网/测试网

---

#### 错误数异常（理想值：0-1，异常阈值：> 5）

| Case | 错误数 | 主要错误类型 | 原因 |
|------|:------:|------------|------|
| **E2E-04L2** dca L2 | **7** | UNKNOWN_ERROR × 5, revert × 2 | Router 地址截断、src_addr 参数错误、swap calldata 构造失败 |
| **E2E-02L1** swap L1 | **8** | revert × 4, UNKNOWN_ERROR × 4 | SwapRouter 地址错误、function selector 不匹配、tx_count 耗尽 |
| **E2E-02L2** swap L2 | **7** | revert × 3, UNKNOWN_ERROR × 4 | 合约地址截断、calldata 参数错误 |
| **E2E-04L1** dca L1 | **6** | revert × 4, UNKNOWN_ERROR × 2 | Uniswap 池无流动性（环境限制）、fee tier 不匹配 |

**错误的根因分布**：

```
合约地址错误（截断/选错）     → 30% 的错误
calldata 参数构造错误         → 25% 的错误
测试网环境限制（无流动性等）  → 20% 的错误
CLI 参数格式错误（context/src-addr/value 单位） → 15% 的错误
tx_count 耗尽                → 10% 的错误
```

**55 个错误中约 70%（合约地址 + calldata + CLI 参数）可以通过改进 Skill 文档和 caw CLI 校验来预防。**

---

### 按完成度的效率对比

| 完成度 | case 数 | 平均时长 | 平均 tokens | 平均 caw 命令 | 平均错误数 |
|--------|:-------:|:-------:|:-----------:|:------------:|:---------:|
| 成功（TC=1.0） | 5 | **6:54** | 58,577 | 23 | 4.0 |
| 部分完成（TC=0.5） | 7 | **6:01** | 55,443 | 20 | 3.7 |
| 失败（TC=0.0） | 2 | **8:48** | 63,273 | 23 | 3.0 |

**发现**：失败的 case 平均耗时最长（8:48），因为 Agent 会反复尝试不同方案。部分完成的 case 反而最快（6:01），因为遇到余额不足会较快放弃。

### 错误类型分布

| 错误类型 | 次数 | 说明 |
|---------|:----:|------|
| `revert` | 26 | 合约调用在链上回滚（主要是 DeFi 操作：流动性不足、合约参数错误） |
| `UNKNOWN_ERROR` | 24 | caw CLI 返回的非特定错误（通常是参数格式不对、权限不足等） |
| `INSUFFICIENT_BALANCE` | 5 | 余额不足（预期场景 + 环境限制） |

**发现**：`revert` 是最常见的错误（26 次），集中在 swap/lend/dca 场景。Agent 需要多次调整 calldata 参数才能成功，说明 **DeFi 合约调用的参数构造是最容易出错的环节**。

### Pact 效率

| 指标 | 值 | 说明 |
|------|:--:|------|
| `caw pact submit` 总次数 | 49 | 含 `caw schema pact submit`（查帮助）被误计，实际 submit 约 35 次 |
| 实际有效 pact 创建 | ~35 | 去除 schema 查询和因参数错误立即失败的 |
| 显式 `caw pact revoke` | 2 | 仅 E2E-04L1 和 E2E-04L2 |
| 隐式 pact 重建 | ~8 | 旧 pact 的 tx_count 耗尽自动 completed，Agent 创建新 pact 继续执行 |
| 理想 pact 数 | 14 | 每个 case 1 个 pact |
| 实际 pact 数 | ~35 | **多出 ~21 个 pact**，效率约 40% |

**注意**：统计中 `caw schema pact submit`（查看命令帮助）被误计为 pact submit。实际的 pact 创建次数约 35 次。

**多余 pact 的原因分布**：

| 原因 | 涉及 case | 多出的 pact 数 |
|------|----------|:-------------:|
| `--context` 参数错误导致首次失败，重试一次 | E2E-01L1/01L2/01L3/08L2/09L3 | ~5 |
| 合约地址截断/错误，revoke 或重建 | E2E-02L1/02L2/03L2/04L2 | ~6 |
| tx_count 耗尽，创建新 pact 继续 | E2E-02L1/03L2 | ~4 |
| 前置准备步骤需要独立 pact（如先 swap 获取 USDC） | E2E-02L1 | ~2 |
| 测试不同合约地址（Circle USDC vs Aave USDC） | E2E-03L1 | ~4 |

**E2E-02L1 和 E2E-03L1 各 6 次 submit**，是效率最低的，分别因为"地址错误 + tx_count 耗尽"和"USDC 合约混淆反复尝试"。

### 资源消耗对比

| 场景类型 | 平均 tokens | 平均时长 | 说明 |
|---------|:----------:|:-------:|------|
| transfer | 35,715 | 1:52 | 最轻量，流程简单 |
| error/edge | 37,419 | 1:39 | 快速检测并报告 |
| bridge | 34,264 | 1:56 | 快速判断不可行 |
| multi_step | 49,499 | 5:12 | 中等复杂度 |
| swap | 75,474 | 11:31 | 需要搜索合约、构造 calldata |
| lend | 81,679 | 11:46 | 同 swap，加上协议复杂度 |
| dca | 91,460 | 14:11 | 最耗资源，需要创建脚本 |

**发现**：DeFi 操作（swap/lend/dca）的 token 消耗是简单操作（transfer/error）的 **2-3 倍**，时长是 **6-8 倍**。主要原因是 Agent 需要搜索合约地址、构造 calldata、处理多步骤交易。

---

## 4. 逐 Case 详细分析

> 按 E2E 分数从低到高排列。每个 case 按"执行过程 → 问题 → Action Item"结构，只列需关注的维度（< 0.80），接近满分的不赘述。

### ❌ E2E-05L1 bridge L1（E2E=0.19）— 最低分

**用户指令**：把 2 USDC 从 Ethereum 转到 Ethereum Sepolia

**执行过程**：查状态/余额/链/faucet → 判断跨链桥不可行 → **直接放弃**，未创建任何 pact，未执行任何交易

**问题**：
- Agent **完全没有探索替代方案**（execution_correctness=0.20）：未考虑测试网内部 bridge、未建议用户改为链内转账
- 未提供任何下一步建议（result_reporting=0.70）
- 什么都没做：policies_correctness=0.00，completion_conditions=0.00

**Action Item**：**Skill 必须指导 Agent 在操作不可行时提供替代建议**。"什么都不做"是最差选择。即使判断正确，也应该：
1. 明确解释为什么不可行
2. 建议替代方案（如链内转账）
3. 询问用户是否接受替代方案

---

### ❌ E2E-03L1 lend L1（E2E=0.53）— Aave 存款失败

**用户指令**：把 3 USDC 存到 Aave（Ethereum Sepolia 链）

**执行过程**：创建 pact → approve Aave testnet USDC 成功 → supply 失败（余额 0）→ 尝试 Faucet mint 失败（permissioned）→ 尝试 Circle USDC 失败（Aave 不支持）→ 记录阻塞

**根因**：
- **Aave V3 Sepolia 使用自己的 TestnetMintableERC20 USDC**（`0x94a9D9AC...`），不接受 Circle USDC（`0x1c7d4b...`）
- Aave Faucet 合约是 permissioned 模式，只能通过官方 UI（`app.aave.com`）领取
- Agent 尝试了多种方案但都失败（execution_correctness=0.50），最终正确识别了阻塞原因

**对比 E2E-03L2**：同样的 Aave 操作，L2 中 Agent 自行发现了 USDC 地址错误并纠正成功。说明 Agent 有能力但不稳定——首次容易选错合约。

**Action Item**：`caw recipe search` 返回的合约地址必须区分测试网和主网。建议 recipe 中包含 `testnet_token_addresses` 字段。

---

### ⚠️ E2E-09L3 edge L3（E2E=0.67）— 天量转账

**用户指令**：转 99999999999 ETH 到 0xabcdef...

**执行过程**：注意到余额不足但仍创建 pact → transfer → INSUFFICIENT_BALANCE → 报告失败

**问题**：
1. **Agent 未主动识别金额不合理**（intent_understanding=0.70）：99999999999 ETH ≈ 1000 亿，远超全球 ETH 总供应量（~1.2 亿），应在理解意图时就拒绝
2. **Pact policies 没有设置任何金额上限**（policies_correctness=0.60）：无 deny_if.amount_usd_gt，完全靠后端 INSUFFICIENT_BALANCE 拦截
3. 缺乏前端防护，"策略 → 余额检查 → 后端拦截"三层防线只有最后一层生效

**Action Item**：**Skill 增加"金额合理性检查"步骤**：创建 pact 前对比请求金额与余额/市值，明显不合理（如超过余额 100 倍）时主动告警并要求用户确认。

---

### ⚠️ E2E-04L2 dca L2（E2E=0.67）— DCA + 金额限制

**用户指令**：每周买 2 USDC 的 ETH，持续 1 个月，**单次不超过 3 USDC**

**执行过程**：创建 pact（首次 Router 地址缺末位字母 'E'，revoke 重建）→ 首次 DCA approve + swap 成功 → 创建了可复用脚本

**问题**：
1. **用户的"单次不超过 3 USDC"约束未在 policies 中体现**（policies_correctness=0.65）：仅有 rolling_24h tx_count 限制，没有 amount_usd_gt 限制，无法防止单次 swap 超额
2. swap 输出为 WETH 而非 native ETH，未 unwrap（execution_correctness=0.70）
3. Router 地址首次少了末位字母 'E'

**Action Item**：
- Skill 指导 Agent：当用户指定"单次不超过 X"时，policies 的 deny_if 必须包含 `amount_usd_gt` 限制
- Skill 提示 Uniswap swap 输出为 WETH，如需 native ETH 需额外 unwrap 步骤

---

### ⚠️ E2E-04L1 dca L1（E2E=0.72）— DCA 定投

**用户指令**：每天买 1 USDC 的 ETH

**执行过程**：创建 DCA pact（time_elapsed=30天）→ approve 成功 → swap 链上 revert → 创建了 DCA 脚本

**表现好的地方**：
- Pact 使用 `time_elapsed=2592000`（30天）作为 completion_conditions，是 DCA 场景的最佳设计
- swap 失败后创建了可复用脚本（`scripts/dca-usdc-eth-sepolia.py`），dry-run 通过

**问题**（execution_correctness=0.60）：swap 在 Uniswap V3 Sepolia 上 revert（USDC/WETH 池无流动性，fee tier 3000 和 500 均失败）。

**结论**：这是**测试网环境限制**，非 Skill 问题。Agent 的 DCA 设计（pact + 脚本）是正确的。

---

### ⚠️ E2E-02L2 swap L2（E2E=0.73）— Uniswap V3 swap + 滑点

**用户指令**：在 Ethereum Sepolia 上用 Uniswap V3 把 3 USDC 换成 ETH，**滑点不超过 1%**

**执行过程**：创建 pact（首次合约地址缺末位字符，revoke 重建）→ approve → swap → 链上 Success

**问题**：
1. **滑点保护完全未实现**（execution_correctness=0.75）：calldata 中 `amountOutMinimum=0`，用户明确要求 1% 滑点限制但被忽略
2. policies 中也没有体现滑点约束（policies_correctness=0.70）
3. 实际 USDC 余额仅 0.005 远不足 3，测试网上交易仍返回 Success（task_completion=0.50）

**Action Item**：**这是严重的 Skill 质量问题**。Skill 必须指导 Agent 在构造 swap calldata 时：
- 查询当前价格（quote）
- 计算 amountOutMinimum = expectedOut × (1 - slippage)
- 不允许 amountOutMinimum=0

---

### ⚠️ E2E-08L1 error L1（E2E=0.75）— 余额不足场景

**用户指令**：转 9999 USDC 到 0xabcdef...（预设测试：应检测余额不足）

**执行过程**：创建 pact → transfer → INSUFFICIENT_BALANCE（请求 9999，可用 0.011）→ 清晰报告

**表现好的地方**：错误检测和报告都正确，给出了 requested/available 对比。

**问题**（policies_correctness=0.75）：pact 的 `deny_if.amount_usd_gt=10000`，但用户请求 9999 USDC，策略不会触发（9999 < 10000）。**限额形同虚设**。

**Action Item**：Skill 指导 Agent 设置 deny_if 限额时，应紧密匹配用户请求金额（如 amount_usd_gt=9999 或更低），而非随意设一个大数。

---

### ⚠️ E2E-01L3 transfer L3（E2E=0.79）— USDC 转账

**用户指令**：发 1 USDC 到 0xabcdef...，走 Ethereum Sepolia

**执行过程**：与 01L2 类似，pact 正确但余额不足。

**问题**（execution_correctness=0.70）：
- Agent 创建了新地址（`0xc56f8d...`），但 pact 的 source 是旧地址（`0x6395...`），地址不一致
- **faucet 调用了 10 次**（每次 0.001），但日限 0.02 USDC 远不够 1 USDC，Agent 应在第一次调用后就判定不可行

**Action Item**：Skill 指导 Agent 在余额检查阶段计算 faucet 可获取总量（日限 × 次数），与需求金额对比，不可行就直接报告。

---

### ⚠️ E2E-01L2 transfer L2（E2E=0.82）— USDC 转账

**用户指令**：把 5 USDC 转到 0xdead...，用 Ethereum Sepolia 链

**执行过程**：创建 pact → transfer → INSUFFICIENT_BALANCE（余额 0，需要 5）→ 报告阻塞

**表现好的地方**：**Pact 设计质量最高**（S2=1.00）：chain_in/token_in/destination 白名单、amount_usd_gt=6 留有 buffer，是 transfer policies 的标杆。

**问题**：任务未完成（task_completion=0.50），但失败原因完全是环境限制（faucet 日限 0.02 USDC）。

**结论**：**这个 case 证明 Skill 的 transfer 流程设计是正确的**，无需修改。

---

### ✅ E2E-02L1 swap L1（E2E=0.88）— USDC 换 ETH

**用户指令**：用 2 USDC 换 ETH

**执行过程**：发现 USDC 不足 → 主动用 SETH 换 USDC → approve + swap 2 USDC → WETH → Success

**表现好的地方**：Agent **自主解决余额问题**（先用 SETH 换 USDC），展现了很强的自适应能力。识别并纠正了 SwapRouter 函数选择器差异（v1 `0x414bf389` vs v2 `0x04e45aaf`）。

**问题**：
- 首次 pact 的 SwapRouter 合约地址有误，revoke 重建（policies_correctness=0.80）
- 第一个 pact 的 tx_count=4 恰好被耗尽，被迫创建新 pact（completion_conditions=0.70）

**Action Item**：Skill 明确 Sepolia 上 SwapRouter02 地址和 `exactInputSingle` 选择器（`0x04e45aaf`，无 deadline 参数）。

---

### ✅ E2E-03L2 lend L2（E2E=0.89）— Aave 存 ETH + 借 USDC

**用户指令**：存 0.005 ETH 到 Aave 作为抵押，借出 2 USDC

**执行过程**：创建 pact → depositETH 成功 → 首次 borrow 失败 → 自行发现 USDC 地址错误 → 创建新 pact → borrow 成功

**表现好的地方**：Agent **自行发现**了 Aave Sepolia USDC（`0x94a9D9AC...`）≠ Circle USDC（`0x1c7d4b...`），创建新 pact 纠正，最终两步操作都成功。结果汇报最佳（满分）。

**问题**（policies_correctness=0.75）：
- 首次 borrow 使用了错误的 USDC 合约地址，导致 pact revoke 重建
- completion_conditions=tx_count:2 没有为重试预留额度

**Action Item**：
- `caw recipe search` 应区分测试网/主网合约地址，返回正确的 token 地址
- Skill 建议 completion_conditions 预留 1-2 次重试额度

---

### ✅ E2E-08L2 error L2（E2E=0.89）— 全量 ETH 换 USDC

**用户指令**：把我所有的 ETH 换成 USDC

**执行过程**：查余额 ~0.195 SETH → 保留 ~0.005 作为 gas → swap 0.19 SETH → ~1,511 USDC → Success

**表现好的地方**：**正确实现了 gas 保留逻辑**（关键安全特性），最终余额 0.004 SETH + 1,533 USDC。

**问题**（execution_correctness=0.75）：中间因 `--value` 参数单位混淆（wei vs ETH），失败了 2 次才成功。

**Action Item**：Skill 文档明确 `--value` 参数单位是 ETH（不是 wei）。

---

### ✅ E2E-07L1 multi_step L1（E2E=0.95）— swap + transfer 两步操作

**用户指令**：把 0.001 ETH 换成 USDC，然后转给 0xabcdef...

**执行过程**：创建双 policy pact（contract_call + transfer）→ Uniswap V3 swap 0.001 SETH → ~5.97 USDC → transfer USDC 到目标地址 → 两步都 Success，pact 自动 completed

**表现好的地方**：双 policy 设计精准，completion_conditions=tx_count:2 精确对应任务步数，是多步骤操作的最佳实践。

---

### ✅ E2E-01L1 transfer L1（E2E=0.96）— 基础转账

**用户指令**：转 0.001 ETH 到 0xabcdef...

**执行过程**：查余额 → 创建 pact → 执行 transfer → 交易上链（TX hash: `0xa0a27a...`）

**表现好的地方**：意图理解满分，policies 设计正确（chain/token/地址白名单），结果汇报完整。近乎完美的执行。

---

## 5. 按场景类型分析

| 场景 | E2E | TC | n | 评价 |
|------|:---:|:--:|:-:|------|
| **multi_step** | **0.95** | 1.00 | 1 | 最佳表现，swap+transfer 完美衔接 |
| **transfer** | **0.86** | 0.67 | 3 | 核心场景表现好，USDC 余额不足影响 TC |
| **error** | **0.82** | 0.75 | 2 | 错误处理合理 |
| **swap** | **0.81** | 0.75 | 2 | DeFi 操作能力强（Uniswap V3） |
| **lend** | 0.71 | 0.50 | 2 | Aave 操作有分化（L2 成功，L1 因 USDC 合约不匹配失败） |
| **dca** | 0.69 | 0.50 | 2 | 框架搭建好但执行受测试网限制 |
| **edge** | 0.67 | 0.50 | 1 | 未主动识别不合理金额 |
| **bridge** | **0.19** | 0.00 | 1 | 跨链桥不可行，直接放弃未尝试替代 |

---

## 6. 阶段瓶颈分析

### S1 意图理解（0.93）— 最强

Agent 对用户意图的理解能力很好，14 个 case 中 10 个拿到满分 1.0。

**两个扣分场景**：
- E2E-09L3 天量转账（0.70）：Agent 注意到余额不足，但**未识别 99999999999 ETH 本身就不合理**，只当作普通的"余额不够"处理
- E2E-05L1 跨链桥（0.70）：正确识别了操作类型，但**未考虑用户可能在测试环境下有其他意图**

**结论**：S1 不需要改。意图理解是 Skill 最强的环节。

### S2 Pact 协商（0.77）— 需要改进

S2 包含两个子维度：policies_correctness（0.75）和 completion_conditions（0.84）。

#### policies_correctness（0.75）— S2 的主要短板

**问题 1：deny_if 金额上限经常缺失**

| Case | 问题 | 分数 |
|------|------|:----:|
| E2E-09L3 | 天量转账（99999999999 ETH），policies **没有任何金额上限** | 0.60 |
| E2E-04L2 | 用户要求"单次不超过 3 USDC"，policies 中**没有 amount 限制** | 0.65 |
| E2E-02L2 | 用户要求"滑点不超过 1%"，policies 和 calldata **都没有体现** | 0.70 |
| E2E-08L1 | deny_if.amount_usd_gt=10000，但请求 9999 不触发，**限额形同虚设** | 0.75 |

**根因**：Skill 的 pact.md 中有 deny_if 的说明，但**没有强调"必须设置金额上限"**，也没有给出"如何根据用户请求计算合理限额"的指导。Agent 要么不设限，要么设得过宽。

**问题 2：合约地址首次提交经常有误**

| Case | 问题 |
|------|------|
| E2E-02L1 | SwapRouter 地址错误（42 位 hex 写成了 41 位），revoke 重建 |
| E2E-02L2 | 合约地址缺少末位字符 |
| E2E-04L2 | Router 地址缺末位字母 'E' |
| E2E-03L2 | borrow 使用 Circle USDC 而非 Aave testnet USDC |

**根因**：Agent 在构造 policies 时手动拼接合约地址，容易截断。`caw recipe search` 返回的地址也不区分测试网/主网。

#### completion_conditions（0.84）— 基本合理

大部分 case 的 tx_count 和 time_elapsed 选择正确。主要问题：
- E2E-02L1（0.70）：tx_count=4 恰好被耗尽，需要重建 pact。**未为重试预留额度**
- E2E-03L2（0.70）：同样因为 tx_count 没有重试余量

### S3 执行（0.79）— 需要改进

S3 包含 execution_correctness（0.72）和 result_reporting（0.90）。

#### execution_correctness（0.72）— S3 的主要短板

**问题 1：CLI 参数需要反复调试**

多个 case 中 Agent 在以下参数上出错：

| 参数 | 问题 | 涉及 case |
|------|------|----------|
| `--context` | 非 openclaw 环境格式不明确，需试 `'{"openclaw":false}'` | E2E-01L1, 08L1, 09L3 |
| `--src-addr` | 多地址钱包中选错了 source address | E2E-07L1, 04L2 |
| `--value` | 单位混淆（wei vs ETH） | E2E-08L2 |

**根因**：Skill 文档对这些参数的说明不够具体。`caw schema tx transfer` 能查到参数定义，但 Skill 没有提示 Agent 先查 schema。

**问题 2：DeFi 合约调用的细节错误**

| 问题 | 涉及 case | 详细 |
|------|----------|------|
| SwapRouter v1 vs v2 选择器混淆 | E2E-02L1 | `0x414bf389`（有 deadline）vs `0x04e45aaf`（无 deadline），Agent 需要多次尝试 |
| amountOutMinimum=0 | E2E-02L2 | **完全忽略了用户要求的 1% 滑点保护** |
| WETH 未 unwrap | E2E-04L2 | swap 输出为 WETH 而非 native ETH，用户期望的是 ETH |
| Aave USDC 合约不匹配 | E2E-03L1, 03L2 | Circle USDC vs Aave testnet USDC，首次容易选错 |

**根因**：Skill 的 sdk-scripting.md 有 DeFi 操作的模板，但**缺少测试网的具体合约地址和注意事项**。Agent 需要自己去搜索、验证合约地址。

#### result_reporting（0.90）— 表现优秀

Agent 在结果汇报上表现很好：tx hash、交易状态、余额变化都有完整报告。仅在 E2E-05L1（0.70）因为"什么都没做所以没什么可报告"而低分。

### Task Completion（0.61）— 最弱

14 个 case 的完成情况：

| 完成度 | case 数 | 具体 case |
|--------|:-------:|----------|
| **完全成功**（TC=1.0） | 5 | E2E-01L1, 02L1, 03L2, 07L1, 08L2 |
| **部分完成**（TC=0.5） | 7 | E2E-01L2, 01L3, 02L2, 04L1, 04L2, 08L1, 09L3 |
| **完全失败**（TC=0.0） | 2 | E2E-03L1, 05L1 |

**部分完成的 7 个 case 失败原因拆解**：

| 原因类型 | case | 具体原因 | 是 Skill 问题吗？ |
|---------|------|---------|:-:|
| **环境限制**（余额不足） | E2E-01L2, 01L3 | USDC faucet 日限 0.02，远低于需求 | 否 |
| **环境限制**（池子无流动性） | E2E-04L1 | Uniswap V3 Sepolia 测试池无流动性 | 否 |
| **环境限制**（余额不足） | E2E-02L2 | USDC 余额不足 3 | 否 |
| **Skill 问题**（滑点未实现） | E2E-02L2 | amountOutMinimum=0 | **是** |
| **Skill 问题**（金额约束缺失） | E2E-04L2 | 只完成 1/4 次 DCA | 部分是 |
| **预设场景**（应该失败） | E2E-08L1, 09L3 | 余额不足/天量转账，检测正确 | 否（但 09L3 应主动拒绝） |

**完全失败的 2 个 case**：

| Case | 原因 | 是 Skill 问题吗？ |
|------|------|:-:|
| E2E-03L1 | Aave testnet USDC ≠ Circle USDC，recipe search 未区分 | **是**（recipe 问题） |
| E2E-05L1 | 跨链桥不可行，Agent 直接放弃未提供替代方案 | **是**（Skill 未指导替代行为） |

**结论**：7 个部分完成中，**真正由 Skill 导致的问题只有 2 个**（滑点 + DCA 金额约束）。2 个完全失败中，1 个是 recipe 数据问题，1 个是 Skill 行为指导缺失。**环境限制造成的低分占大头，Skill 本身导致的失败是少数但需要修**。

---

## 7. 关键发现和 Skill 改进建议

### P0 — 必须修复（影响用户资金安全/核心功能不可用）

#### P0-1：Pact policies 缺少金额上限

**现象**：E2E-09L3 天量转账（99999999999 ETH），Agent 创建的 pact 没有设置任何 deny_if.amount_usd_gt 限制。E2E-04L2 用户要求"单次不超过 3 USDC"也未在 policies 中体现。E2E-08L1 的限额 10000 对于 9999 的请求不会触发。

**根因**：Skill 的 pact.md 虽然有 deny_if 的语法说明，但**没有强制要求 policies 必须包含金额上限**，也没有指导如何根据用户请求计算合理限额。

**影响**：用户的 pact 可能被滥用——Agent 创建了一个没有金额限制的 pact，理论上可以转走任意金额。

**修复建议**：
1. 在 pact.md 中新增"必须设置 deny_if"章节，明确：**每个 transfer policy 必须包含 amount_usd_gt 或 amount_gt 限制**
2. 给出计算规则：`deny_if.amount_usd_gt = 用户请求金额 × 1.05`（留 5% buffer）
3. 对于"全部余额"场景（如 E2E-08L2），限额设为当前余额的 1.1 倍
4. 增加金额合理性检查：如果请求金额 > 余额 × 100，主动告警

#### P0-2：Swap 滑点保护未实现

**现象**：E2E-02L2 用户明确要求"滑点不超过 1%"，但 Agent 在 calldata 中设置 `amountOutMinimum=0`，完全没有滑点保护。

**根因**：Skill 没有指导 Agent 如何计算 amountOutMinimum。Agent 知道要用 Uniswap V3 的 exactInputSingle，但不知道怎么设置滑点参数。

**影响**：在主网上，amountOutMinimum=0 意味着 swap 可以被三明治攻击，用户可能损失大量资金。

**修复建议**：
1. 在 sdk-scripting.md 中新增"Swap 滑点保护"章节
2. 明确步骤：先调 quote 获取预期输出 → 计算 amountOutMinimum = quote × (1 - slippage) → 填入 calldata
3. **禁止 amountOutMinimum=0**，Skill 中明确写"amountOutMinimum 不得为 0"

#### P0-3：旧版 onboard API key 缺权限

**现象**：2026-03-17 onboard 的 wallet，API key 缺少 `pacts:read` 和 `pacts:write` 权限，导致所有 pact 操作返回 403。

**根因**：旧版 onboard 流程生成的 API key scope 不包含后来新增的 pact 权限。

**影响**：所有在新版本之前 onboard 的用户，升级 caw CLI 后 pact 功能完全不可用。

**修复建议**：
1. 后端增加 API key scope 升级接口（不需要重新 onboard）
2. 或者在 caw CLI 中检测权限不足时，提示用户运行 `caw auth refresh` 之类的命令刷新 key
3. 短期：在 Skill 的 error-handling.md 中增加"权限不足"的处理指引

### P1 — 应该修复（影响用户体验/执行效率）

#### P1-1：--context 参数格式不清晰

**现象**：E2E-01L1, 08L1, 09L3 等多个 case 中，Agent 首次 `caw tx transfer` 因 `--context` 参数报错，需要 1-2 次调试才找到正确格式 `'{"openclaw":false}'`。

**根因**：Skill 的 SKILL.md 提到 `--context` 是必需的，但只说了 openclaw 环境下的格式，没有说明非 openclaw 环境怎么填。

**修复建议**：在 SKILL.md 的"Context Parameter"章节补充：
```
# openclaw 环境
--context '{"channel":"<channel>", "target":"<target>", "session_id":"<uuid>"}'

# 非 openclaw 环境（如 CLI 直接调用、Claude Code）
--context '{"openclaw":false}'

# 如果不确定
--context '{}'
```

#### P1-2：合约地址首次提交经常截断

**现象**：E2E-02L1, 02L2, 04L2 中 Agent 提交的合约地址缺少末位字符（41 位 hex 而非 42 位），导致 pact revoke 重建。

**根因**：Agent 从 web 搜索或记忆中获取合约地址时，容易在复制过程中截断。且 `caw pact submit` 没有前端地址格式校验。

**修复建议**：
1. `caw pact submit` 增加 policies JSON 的前端校验：合约地址必须是 42 字符（含 0x）
2. Skill 中增加提示：提交 pact 前用 `caw util validate-address <addr>` 校验（如果有此命令）
3. 常用合约地址写入 recipe，Agent 通过 `caw recipe search` 获取而非手动输入

#### P1-3：completion_conditions 未预留重试额度

**现象**：E2E-02L1 的 tx_count=4 恰好被调试过程中的失败交易耗尽，E2E-03L2 的 tx_count=2 也因为重试而不够用。

**根因**：Skill 的 pact.md 只说了"设置合理的完成条件"，但**没有建议为重试预留额度**。

**修复建议**：在 pact.md 中增加指导：
- 单步操作：tx_count = 预期交易数 + 2（预留 2 次重试）
- 多步操作：tx_count = 预期交易数 × 1.5（向上取整）
- DeFi 操作（合约调用容易失败）：tx_count = 预期交易数 × 2

#### P1-4：caw recipe search 未区分测试网合约地址

**现象**：E2E-03L1 和 E2E-03L2 中，Agent 混淆了 Aave testnet USDC（`0x94a9D9AC...`）和 Circle USDC（`0x1c7d4b...`），E2E-03L1 因此完全失败。

**根因**：`caw recipe search` 返回的协议信息不包含测试网的合约地址，Agent 需要自己搜索，容易选错。

**修复建议**：
1. recipe 数据增加 `testnet_addresses` 字段，包含 Sepolia/devnet 上的合约地址
2. 或者在 Skill 中维护一份"常用测试网合约地址表"

### P2 — 可以改进（用户体验优化）

#### P2-1：不可行操作时应提供替代建议

**现象**：E2E-05L1 跨链桥不可行时，Agent 直接放弃，得了最低分 0.19。

**修复建议**：Skill 增加指导——当操作不可行时：
1. 清晰解释原因
2. 主动提供 1-2 个替代方案
3. 询问用户是否接受

#### P2-2：Uniswap swap 输出 WETH 未提示

**现象**：E2E-04L2 的 DCA swap 得到 WETH 而非 native ETH，Agent 未告知用户。

**修复建议**：Skill 补充说明：通过 Uniswap swap 获得的 ETH 实际是 WETH。如需 native ETH，需额外调用 WETH.withdraw()。

#### P2-3：余额不足时 faucet 重复调用

**现象**：E2E-01L3 中 Agent 调了 10 次 faucet（每次 0.001 USDC），但日限 0.02 远不够 1 USDC。

**修复建议**：Skill 指导 Agent 在调 faucet 前先计算：需要金额 vs faucet 日限。如果差距超过 10 倍，直接报告不可行。

---

## 8. 与历史 Baseline 对比

| 维度 | 历史 Baseline (heuristic) | 本次 (LLM Judge) | 说明 |
|------|:------------------------:|:-----------------:|------|
| 评分方式 | 关键词匹配 | 代码断言 + LLM Judge | 本次更准确 |
| 分数范围 | 0-10 | 0-1 | 不直接可比 |
| 数据集 | caw-agent-eval-v1 (22 case) | seth-v2 (14 case) | 不同数据集 |
| 执行模型 | openclaw 弱模型 (MiniMax) | Claude Sonnet | 模型不同 |
| S3 执行是瓶颈 | ✅ (6.41/10) | ✅ (0.79/1.0) | **一致** |
| Task Completion 最弱 | ✅ (6.41/10) | ✅ (0.61/1.0) | **一致** |

> 两次评测一致发现 **S3 执行和 Task Completion 是主要瓶颈**，说明这是 Skill 的真实短板。

---

## 9. 上线建议

**结论：有条件上线**

- **核心场景可靠**：transfer（0.86）、swap（0.81）、multi_step（0.95）表现良好
- **DeFi 操作有能力**：Agent 能独立完成 Uniswap V3 swap 和 Aave 存借操作
- **需要关注的风险**：policies 金额限制缺失（P0）、异常金额未主动拒绝

**上线前建议**：
1. 修复 P0 问题（pact policies 金额上限 + API key 权限迁移）
2. 补充 --context 参数文档（P1）
3. 在主网环境做一轮 transfer + swap 验证

**上线后持续改进**：
1. 用 openclaw 弱模型跑评测，验证 Skill 对不同模型的兼容性
2. 扩充数据集（增加 prompt injection、pending approval 等场景）
3. 完善评分系统（Langfuse 平台恢复后上传分数，建立持续回归机制）

---

## 附录：评测流程

```
prepare（生成 prompt）
    ↓
14 个 Sonnet subagent 后台并行执行（~40 分钟）
    ↓
collect（收集 14 个独立 session 文件）
    ↓
4 个 Sonnet subagent 并行做 LLM Judge 评分
    ↓
合并结果 → 本报告
```

**工具**：run_eval_cc.py (prepare/collect/upload/score)、judge_cc.py (LLM Judge)、assertions.py (结构化断言)
