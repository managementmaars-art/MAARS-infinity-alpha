---
name: ai-research-finetuning
description: LLM fine-tuning with LoRA, QLoRA, full fine-tuning using Axolotl and LLaMA-Factory, PEFT library, and Unsloth for fast training.
---

# AI Research: Fine-tuning

## Overview

Fine-tuning adapts pretrained LLMs to specific tasks. LoRA/QLoRA are the dominant methods — they achieve near-full-fine-tuning quality at a fraction of the compute by training low-rank adapter weights.

## PEFT with LoRA (Hugging Face)

```python
# pip install transformers peft accelerate bitsandbytes datasets
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
import torch

# QLoRA config (4-bit quantization + LoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",       # Normal float 4-bit
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    attn_implementation="flash_attention_2",
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,                        # Rank (higher = more capacity, more params)
    lora_alpha=32,               # Scaling factor (alpha/r)
    target_modules=[             # Which layers to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    modules_to_save=["embed_tokens", "lm_head"],  # Train fully (for new tokens)
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Trainable params: 20,971,520 (0.24%) | Total: 8,030,261,248
```

## Training with TRL SFTTrainer

```python
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

# Load and format dataset
dataset = load_dataset("json", data_files={"train": "train.jsonl", "test": "test.jsonl"})

def format_chat(example):
    """Format to chat template."""
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

# SFT configuration
sft_config = SFTConfig(
    output_dir="./outputs/llama-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,    # Effective batch size = 16
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",         # Memory-efficient optimizer
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    max_seq_length=2048,
    fp16=False,
    bf16=True,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=200,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to="wandb",
    run_name="llama-qlora-coding",
    packing=True,                     # Pack short samples into one sequence
)

trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    formatting_func=format_chat,
)

trainer.train()

# Save adapter weights
trainer.save_model("./outputs/llama-finetuned-adapter")
tokenizer.save_pretrained("./outputs/llama-finetuned-adapter")

# Merge adapter into base model (for deployment)
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)
merged_model = PeftModel.from_pretrained(base_model, "./outputs/llama-finetuned-adapter")
merged_model = merged_model.merge_and_unload()
merged_model.save_pretrained("./outputs/llama-merged", safe_serialization=True)
```

## Unsloth (2x Faster Training)

```python
# pip install unsloth
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template

max_seq_length = 2048

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B-Instruct",
    max_seq_length=max_seq_length,
    dtype=None,             # Auto-detect bfloat16/float16
    load_in_4bit=True,
    token=os.getenv("HF_TOKEN"),
)

# Add LoRA adapters (optimized for Unsloth)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,        # Unsloth supports optimized 0 dropout
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth's optimized checkpointing
    random_state=42,
    use_rslora=True,       # Rank-stabilized LoRA
)

# Get chat template
tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")

def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in convos]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# Train with Unsloth's optimized trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
    dataset_num_proc=2,
    packing=True,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,                 # Or num_train_epochs=3
        learning_rate=2e-4,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        output_dir="outputs",
    ),
)

trainer.train()

# Save with GGUF for llama.cpp
model.save_pretrained_gguf("model", tokenizer, quantization_method="q4_k_m")
```

## Axolotl Configuration

```yaml
# axolotl_config.yaml
base_model: meta-llama/Meta-Llama-3.1-8B-Instruct
model_type: LlamaForCausalLM
tokenizer_type: AutoTokenizer

load_in_4bit: true
strict: false

datasets:
  - path: my_dataset.jsonl
    type: chat_template
    chat_template: llama3

dataset_prepared_path: last_run_prepared
val_set_size: 0.02
output_dir: ./outputs/lora-out

adapter: lora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj

sequence_len: 4096
sample_packing: true
pad_to_sequence_len: true

gradient_accumulation_steps: 4
micro_batch_size: 2
num_epochs: 3
optimizer: paged_adamw_8bit
lr_scheduler: cosine
learning_rate: 2e-4
train_on_inputs: false    # Only train on assistant responses
group_by_length: false

bf16: auto
tf32: false
gradient_checkpointing: true
flash_attention: true

logging_steps: 10
eval_steps: 100
save_steps: 100
save_total_limit: 3

wandb_project: my-finetune
wandb_run_id: llama-qlora-v1
```

```bash
# Run Axolotl
pip install axolotl[flash-attn,deepspeed]
axolotl train axolotl_config.yaml
axolotl evaluate axolotl_config.yaml
axolotl merge-lora axolotl_config.yaml --lora-model-dir="outputs/lora-out"
```

## DPO (Direct Preference Optimization)

```python
from trl import DPOTrainer, DPOConfig

# DPO dataset format: {prompt, chosen, rejected}
dpo_dataset = load_dataset("json", data_files="dpo_data.jsonl")

dpo_config = DPOConfig(
    beta=0.1,                    # KL divergence penalty (lower = more exploration)
    loss_type="sigmoid",         # sigmoid | hinge | ipo | kto_pair
    output_dir="./dpo-output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=5e-7,          # Much lower than SFT!
    num_train_epochs=1,
    bf16=True,
)

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=None,             # Use the PEFT adapter for reference
    args=dpo_config,
    train_dataset=dpo_dataset["train"],
    tokenizer=tokenizer,
    peft_config=lora_config,
)

dpo_trainer.train()
```

## Dataset Preparation

```python
from datasets import Dataset
import json

# Create instruction-following dataset
def create_dataset(raw_data: list) -> Dataset:
    formatted = []
    for item in raw_data:
        formatted.append({
            "conversations": [
                {"role": "system", "content": item.get("system", "You are helpful.")},
                {"role": "user", "content": item["instruction"]},
                {"role": "assistant", "content": item["output"]},
            ]
        })
    return Dataset.from_list(formatted)

# Data quality filters
def filter_quality(example):
    output = example["conversations"][-1]["content"]
    return (
        len(output) > 50             # Minimum response length
        and len(output) < 4000       # Maximum response length
        and not output.startswith("I cannot")  # Filter refusals
    )

dataset = dataset.filter(filter_quality)
dataset = dataset.shuffle(seed=42)
```

## Key Patterns

- **QLoRA** (4-bit + LoRA) fits 7-13B models on a single 24GB GPU
- **`r=16, alpha=32`** is a safe default; increase r for more complex tasks
- **Unsloth** provides 2x speedup with identical outputs — use it
- **Pack sequences** (`packing=True`) maximizes GPU utilization for short examples
- **Train on completions only** (`train_on_inputs=False`) — don't predict user inputs
- **Learning rate**: SFT ~2e-4, DPO ~5e-7; DPO is very sensitive to LR

## Models to Use

- **claude-opus-4-5**: Fine-tuning strategy design, dataset curation, hyperparameter analysis
- **claude-sonnet-4-5**: Training script implementation, dataset formatting, evaluation
- **claude-haiku-3-5**: Config file edits, data formatting scripts
