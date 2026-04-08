---
name: ai-research-inference
description: LLM inference optimization with vLLM, TensorRT-LLM, llama.cpp, SGLang, quantization methods, and continuous batching.
---

# AI Research: Inference

## Overview

Efficient LLM inference is critical for production deployment. Key techniques include continuous batching, KV-cache management, quantization, and speculative decoding to maximize throughput and minimize latency.

## vLLM (Production Inference Server)

```bash
pip install vllm

# Start OpenAI-compatible server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3.1-8B-Instruct \
    --tensor-parallel-size 2 \           # Split across 2 GPUs
    --max-model-len 8192 \
    --max-num-seqs 256 \                 # Max concurrent sequences
    --gpu-memory-utilization 0.9 \
    --enable-prefix-caching \            # Cache common prefixes (system prompts)
    --quantization fp8 \                 # FP8 quantization
    --served-model-name llama-3.1-8b \
    --port 8000
```

```python
# Python vLLM engine
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    tensor_parallel_size=2,
    max_model_len=8192,
    gpu_memory_utilization=0.9,
    enable_prefix_caching=True,
    quantization="fp8",
    max_lora_rank=64,              # Enable LoRA serving
    enable_lora=True,
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    top_k=50,
    max_tokens=512,
    stop=["<|eot_id|>", "<|end_of_text|>"],
    repetition_penalty=1.1,
)

# Batch inference (processes all at once with continuous batching)
prompts = [
    "Explain quantum computing",
    "Write a Python function to sort a list",
    "What is the capital of France?",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt[:50]}")
    print(f"Output: {output.outputs[0].text}")
    print(f"Tokens/sec: {output.metrics.tokens_per_second:.1f}")

# LoRA adapter switching at serving time
outputs = llm.generate(
    prompts,
    sampling_params,
    lora_request=LoRARequest(
        lora_name="coding-adapter",
        lora_int_id=1,
        lora_path="./adapters/coding",
    ),
)

# Async streaming
from vllm.entrypoints.openai.api_server import AsyncLLMEngine

async def stream_response(prompt: str):
    async for output in engine.generate(prompt, sampling_params, request_id="req-1"):
        yield output.outputs[0].text

# vLLM with OpenAI client
from openai import AsyncOpenAI

client = AsyncOpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

async def chat_completion(messages: list) -> str:
    response = await client.chat.completions.create(
        model="llama-3.1-8b",
        messages=messages,
        temperature=0.7,
        max_tokens=512,
        stream=True,
    )
    full_response = ""
    async for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    return full_response
```

## llama.cpp / Ollama

```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j LLAMA_CUDA=1  # CUDA support

# Quantize a model
python convert_hf_to_gguf.py ./llama-3.1-8b --outtype f16
./quantize ./models/llama-3.1-8b-f16.gguf ./models/llama-3.1-8b-Q4_K_M.gguf Q4_K_M

# Run inference
./llama-cli -m ./models/llama-3.1-8b-Q4_K_M.gguf \
    -p "Explain quantum entanglement" \
    -n 512 \
    --temp 0.7 \
    --ctx-size 8192 \
    --threads 8

# OpenAI-compatible server
./llama-server -m ./models/llama-3.1-8b-Q4_K_M.gguf \
    --port 8080 \
    --ctx-size 8192 \
    --n-gpu-layers 35 \  # Offload layers to GPU
    --parallel 4          # Handle 4 requests in parallel
```

```python
# Python bindings with llama-cpp-python
from llama_cpp import Llama, LlamaGrammar

llm = Llama(
    model_path="./models/llama-3.1-8b-Q4_K_M.gguf",
    n_gpu_layers=-1,        # All layers on GPU
    n_ctx=8192,
    n_batch=512,
    n_threads=8,
    verbose=False,
)

# Chat completion
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about Python programming"},
    ],
    temperature=0.7,
    max_tokens=200,
    stream=True,
)

for chunk in response:
    delta = chunk["choices"][0]["delta"]
    if "content" in delta:
        print(delta["content"], end="", flush=True)

# Constrained JSON generation with grammar
grammar = LlamaGrammar.from_string("""
root   ::= object
value  ::= object | array | string | number | ("true" | "false" | "null") ws
object ::= "{" ws (string ":" ws value ("," ws string ":" ws value)*)? "}" ws
array  ::= "[" ws (value ("," ws value)*)? "]" ws
string ::= "\"" char* "\"" ws
char   ::= [^"\\] | "\\" ["\\/bfnrt]
number ::= "-"? [0-9]+ ("." [0-9]+)? ([eE] [-+]? [0-9]+)?
ws     ::= [ \t\n]*
""")

output = llm("Extract JSON from: Alice is 30 years old", grammar=grammar, max_tokens=100)
```

## SGLang (Structured Generation)

```python
# pip install sglang[all]
import sglang as sgl

@sgl.function
def classify_and_respond(s, text):
    s += sgl.system("You are a helpful AI assistant.")
    s += sgl.user(f"Classify this text sentiment: {text}")

    # Constrained generation
    s += sgl.assistant(sgl.gen("sentiment", choices=["positive", "negative", "neutral"]))

    s += sgl.user("Now write a brief response based on the sentiment.")
    s += sgl.assistant(sgl.gen("response", max_tokens=200))

# Initialize runtime
sgl.set_default_backend(sgl.RuntimeEndpoint("http://localhost:30000"))

# Run batch
states = classify_and_respond.run_batch(
    [{"text": "I love this product!"}, {"text": "This is terrible."}],
    temperature=0.7,
    num_threads=2,
)

for state in states:
    print(f"Sentiment: {state['sentiment']}")
    print(f"Response: {state['response']}")
```

## Quantization

```python
# GPTQ quantization
from transformers import AutoModelForCausalLM, GPTQConfig

gptq_config = GPTQConfig(
    bits=4,
    dataset="wikitext2",
    desc_act=False,
    group_size=128,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B",
    quantization_config=gptq_config,
    torch_dtype="auto",
    device_map="auto",
)
model.save_pretrained("./llama-3.1-8b-gptq-4bit")

# AWQ quantization (often better quality than GPTQ)
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3.1-8B",
    safetensors=True,
)

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM",
}

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B")
model.quantize(tokenizer, quant_config=quant_config)
model.save_quantized("./llama-3.1-8b-awq-4bit")
tokenizer.save_pretrained("./llama-3.1-8b-awq-4bit")
```

## Speculative Decoding

```python
# Speculative decoding with vLLM (draft + target model)
llm = LLM(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
    speculative_model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    num_speculative_tokens=5,         # Draft 5 tokens, verify with target
    speculative_draft_tensor_parallel_size=1,
    tensor_parallel_size=4,
)
# 2-4x throughput improvement with same output quality
```

## Benchmarking

```python
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

def benchmark_throughput(endpoint: str, prompts: list, concurrency: int = 10):
    """Measure tokens/second at given concurrency."""
    from openai import OpenAI
    client = OpenAI(base_url=endpoint, api_key="not-needed")

    results = []

    def run_request(prompt: str) -> dict:
        start = time.time()
        response = client.chat.completions.create(
            model="default",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        elapsed = time.time() - start
        tokens = response.usage.completion_tokens
        return {"tokens": tokens, "latency": elapsed, "tps": tokens / elapsed}

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(run_request, p) for p in prompts]
        results = [f.result() for f in futures]

    total_tokens = sum(r["tokens"] for r in results)
    total_time = max(r["latency"] for r in results)
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print(f"Throughput: {total_tokens / total_time:.1f} tokens/sec")
    print(f"Avg latency: {avg_latency * 1000:.0f}ms")
    print(f"P95 latency: {sorted(r['latency'] for r in results)[int(len(results)*0.95)] * 1000:.0f}ms")
```

## Key Patterns

- **vLLM** is the best choice for production GPU serving — continuous batching, prefix caching
- **llama.cpp** for CPU/local deployment — Q4_K_M gives best quality/size tradeoff
- **AWQ** quantization generally outperforms GPTQ at same bit-width
- **Prefix caching** is critical when serving with a fixed system prompt (saves KV computation)
- **Speculative decoding** with a small draft model gives 2-4x speedup for free
- **Tensor parallelism** splits model across GPUs — use when model doesn't fit in single GPU

## Models to Use

- **claude-opus-4-5**: Inference architecture design, performance optimization strategy
- **claude-sonnet-4-5**: Server configuration, quantization pipeline, benchmarking
- **claude-haiku-3-5**: Simple inference scripts, client code, config edits
