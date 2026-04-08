---
name: ai-research-distributed-training
description: "DeepSpeed ZeRO, FSDP, Megatron-Core, gradient checkpointing, mixed precision, multi-node"
---

# AI Research: Distributed Training

Production-scale distributed training: DeepSpeed ZeRO stages, PyTorch FSDP, Megatron-LM tensor/pipeline parallelism, gradient checkpointing, mixed precision, and multi-node launch configurations.

## DeepSpeed ZeRO Configuration

ZeRO (Zero Redundancy Optimizer) partitions optimizer states, gradients, and parameters across data-parallel ranks:

```json
// ds_config_zero3.json — ZeRO-3 for very large models (>10B params)
{
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto",
  "gradient_accumulation_steps": "auto",
  "gradient_clipping": 1.0,

  "zero_optimization": {
    "stage": 3,
    "overlap_comm": true,
    "contiguous_gradients": true,
    "sub_group_size": 1e9,
    "reduce_bucket_size": "auto",
    "stage3_prefetch_bucket_size": "auto",
    "stage3_param_persistence_threshold": "auto",
    "stage3_max_live_parameters": 1e9,
    "stage3_max_reuse_distance": 1e9,
    "stage3_gather_16bit_weights_on_model_save": true
  },

  "bf16": {
    "enabled": true
  },

  "optimizer": {
    "type": "AdamW",
    "params": {
      "lr": "auto",
      "betas": [0.9, 0.95],
      "eps": 1e-8,
      "weight_decay": 0.1
    }
  },

  "scheduler": {
    "type": "WarmupCosineAnnealing",
    "params": {
      "warmup_min_lr": 0,
      "warmup_max_lr": "auto",
      "warmup_num_steps": "auto",
      "total_num_steps": "auto"
    }
  },

  "activation_checkpointing": {
    "partition_activations": true,
    "cpu_checkpointing": false,
    "contiguous_memory_optimization": true,
    "number_checkpoints": null,
    "synchronize_checkpoint_boundary": false,
    "profile": false
  },

  "flops_profiler": {
    "enabled": false,
    "profile_step": 1,
    "module_depth": -1
  },

  "comms_logger": {
    "enabled": false
  }
}
```

```python
# Training with DeepSpeed
import deepspeed
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")

parameters = filter(lambda p: p.requires_grad, model.parameters())

model_engine, optimizer, train_loader, scheduler = deepspeed.initialize(
    args=args,
    model=model,
    model_parameters=parameters,
    training_data=train_dataset,
    config="ds_config_zero3.json",
)

for step, batch in enumerate(train_loader):
    input_ids = batch["input_ids"].to(model_engine.local_rank)
    labels = batch["labels"].to(model_engine.local_rank)

    outputs = model_engine(input_ids=input_ids, labels=labels)
    loss = outputs.loss

    model_engine.backward(loss)
    model_engine.step()

    if step % 100 == 0 and model_engine.local_rank == 0:
        print(f"Step {step}: loss={loss.item():.4f}")

# Save ZeRO-3 checkpoint (consolidates shards)
model_engine.save_checkpoint("checkpoints/", tag=f"step_{step}")
# Consolidate to HuggingFace format:
# deepspeed.utils.zero_to_fp32.get_fp32_state_dict_from_zero_checkpoint("checkpoints/step_1000")
```

## PyTorch FSDP

```python
import torch
import torch.distributed as dist
from torch.distributed.fsdp import (
    FullyShardedDataParallel as FSDP,
    ShardingStrategy,
    MixedPrecision,
    BackwardPrefetch,
    CPUOffload,
)
from torch.distributed.fsdp.wrap import (
    transformer_auto_wrap_policy,
    size_based_auto_wrap_policy,
)
from transformers.models.llama.modeling_llama import LlamaDecoderLayer
import functools

def setup_distributed():
    dist.init_process_group("nccl")
    torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))

def create_fsdp_model(model_name: str, sharding_strategy: str = "FULL_SHARD"):
    local_rank = int(os.environ["LOCAL_RANK"])

    # Mixed precision policy
    bf16_policy = MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
        buffer_dtype=torch.bfloat16,
    )

    # Auto-wrap based on transformer layer type
    auto_wrap_policy = functools.partial(
        transformer_auto_wrap_policy,
        transformer_layer_cls={LlamaDecoderLayer},
    )

    strategy_map = {
        "FULL_SHARD": ShardingStrategy.FULL_SHARD,          # ZeRO-3
        "SHARD_GRAD_OP": ShardingStrategy.SHARD_GRAD_OP,    # ZeRO-2
        "NO_SHARD": ShardingStrategy.NO_SHARD,              # DDP
        "HYBRID_SHARD": ShardingStrategy.HYBRID_SHARD,      # ZeRO-3 within node
    }

    with torch.device("meta"):
        model = AutoModelForCausalLM.from_pretrained(model_name)

    model = FSDP(
        model,
        auto_wrap_policy=auto_wrap_policy,
        mixed_precision=bf16_policy,
        sharding_strategy=strategy_map[sharding_strategy],
        backward_prefetch=BackwardPrefetch.BACKWARD_PRE,
        cpu_offload=CPUOffload(offload_params=False),
        device_id=torch.cuda.current_device(),
        sync_module_states=True,
        param_init_fn=lambda module: module.to_empty(device=torch.cuda.current_device()),
    )

    return model

# Saving FSDP checkpoints
from torch.distributed.fsdp import StateDictType, FullStateDictConfig

def save_fsdp_checkpoint(model, optimizer, step, save_dir):
    cfg = FullStateDictConfig(offload_to_cpu=True, rank0_only=True)
    with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT, cfg):
        state_dict = model.state_dict()
        if dist.get_rank() == 0:
            torch.save({"model": state_dict, "step": step}, f"{save_dir}/checkpoint_{step}.pt")
```

## Megatron-Core Tensor Parallelism

```python
# Megatron-LM tensor parallelism setup
# Combines TP (tensor) + PP (pipeline) + DP (data) parallelism

from megatron.core import parallel_state
from megatron.core.tensor_parallel import ColumnParallelLinear, RowParallelLinear

def initialize_megatron(
    tensor_model_parallel_size: int = 8,
    pipeline_model_parallel_size: int = 4,
    world_size: int = 256,
):
    """Initialize 3D parallelism: TP=8, PP=4, DP=8 for 256 GPUs."""
    parallel_state.initialize_model_parallel(
        tensor_model_parallel_size=tensor_model_parallel_size,
        pipeline_model_parallel_size=pipeline_model_parallel_size,
    )

# Tensor-parallel attention implementation
class TensorParallelAttention(torch.nn.Module):
    def __init__(self, hidden_size: int, num_heads: int):
        super().__init__()
        self.tp_size = parallel_state.get_tensor_model_parallel_world_size()
        self.local_heads = num_heads // self.tp_size

        # QKV projection — split across TP ranks (column parallel)
        self.qkv_proj = ColumnParallelLinear(
            hidden_size, 3 * hidden_size,
            bias=False,
            gather_output=False,  # keep output sharded
        )

        # Output projection — gather from TP ranks (row parallel)
        self.out_proj = RowParallelLinear(
            hidden_size, hidden_size,
            bias=False,
            input_is_parallel=True,
        )

    def forward(self, x):
        qkv, _ = self.qkv_proj(x)
        # ... attention computation on local heads ...
        output, _ = self.out_proj(attn_output)
        return output
```

## Gradient Checkpointing and Mixed Precision

```python
import torch
from torch.cuda.amp import autocast, GradScaler
from torch.utils.checkpoint import checkpoint_sequential

# Gradient checkpointing — trade compute for memory
# Saves only boundary activations, recomputes internals on backward pass
model.gradient_checkpointing_enable()

# Or manual with checkpoint_sequential for sequential models
def forward_with_checkpointing(model, x, segments=4):
    layers = list(model.transformer.layers)
    return checkpoint_sequential(layers, segments, x, use_reentrant=False)

# Mixed precision training
def train_step_amp(model, batch, optimizer, scaler: GradScaler):
    optimizer.zero_grad(set_to_none=True)   # faster than zero_grad()

    with autocast(dtype=torch.bfloat16):    # bf16 preferred over fp16 for stability
        outputs = model(**batch)
        loss = outputs.loss / gradient_accumulation_steps

    scaler.scale(loss).backward()

    if (step + 1) % gradient_accumulation_steps == 0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()

# Flash Attention 2 for memory-efficient attention
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
```

## Multi-Node Launch

```bash
# torchrun (recommended for PyTorch 2.x)
# 4 nodes, 8 GPUs each = 32 total GPUs
torchrun \
  --nnodes=4 \
  --nproc-per-node=8 \
  --node-rank=$NODE_RANK \
  --master-addr=$MASTER_ADDR \
  --master-port=29500 \
  --rdzv-backend=c10d \
  --rdzv-endpoint=$MASTER_ADDR:29500 \
  train.py \
    --model-name meta-llama/Llama-3-70B \
    --batch-size 2 \
    --gradient-accumulation-steps 8 \
    --max-steps 100000

# SLURM sbatch script for HPC clusters
#!/bin/bash
#SBATCH --job-name=llm-train
#SBATCH --nodes=16
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:8
#SBATCH --time=72:00:00
#SBATCH --partition=gpu-h100

export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=29500
export WORLD_SIZE=$((SLURM_NNODES * 8))

srun --label torchrun \
  --nnodes=$SLURM_NNODES \
  --nproc-per-node=8 \
  --rdzv-backend=c10d \
  --rdzv-endpoint=$MASTER_ADDR:$MASTER_PORT \
  train.py

# DeepSpeed launch
deepspeed --num_nodes=4 --num_gpus=8 --hostfile=hostfile train_ds.py \
  --deepspeed_config ds_config_zero3.json
```

## Best Practices

- **ZeRO stage selection**: ZeRO-1 for optimizer state (minimal overhead), ZeRO-2 for +gradients, ZeRO-3 for +parameters (largest models); FSDP is roughly equivalent to ZeRO-3
- **Gradient checkpointing** saves ~60-70% memory at the cost of ~30% more compute — essential for 7B+ models on 80GB GPUs
- **BF16 over FP16**: BF16 has the same dynamic range as FP32, avoiding the overflow issues that require loss scaling; use FP16 only on older hardware (V100)
- Always use `set_to_none=True` in `optimizer.zero_grad()` — saves memory by deallocating gradient tensors
- Use `torch.compile()` (PyTorch 2.x) for ~20-40% throughput improvement with minimal code changes
- Profile with `torch.profiler` or NVIDIA Nsight before optimizing — find the real bottleneck
- Use **activation offloading** to CPU only as a last resort — it's 10-100x slower than GPU memory
- Set `NCCL_DEBUG=INFO` to diagnose collective communication hangs in multi-node training
- Always checkpoint every N steps — GPU clusters have hardware failure rates that make long runs risky
- Monitor GPU utilization, memory, and MFU (Model FLOP Utilization) — target >50% MFU for efficiency

## Models to Use

- **Default**: `claude-sonnet-4-5` — DeepSpeed config, FSDP setup, training scripts
- **Research architecture**: `claude-opus-4-5` — 3D parallelism design, custom attention, sequence parallelism
- **Config generation**: `claude-haiku-3-5` — SLURM scripts, DeepSpeed JSON configs, launch commands
