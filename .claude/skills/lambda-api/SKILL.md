---
name: lambda-api
description: Lambda Cloud GPU — on-demand A100/H100 GPU instances, managed inference, Llama hosting for MAARS GPU compute and inference
---

# Lambda Cloud API — MAARS Reference

## Overview
```python
LAMBDA_OVERVIEW = {
    "type": "GPU cloud compute + managed inference API",
    "gpu_fleet": ["A100 (80GB)", "H100 (80GB)", "A10 (24GB)", "RTX 6000"],
    "pricing_advantage": "Cheapest H100 available (~$2.50/hr vs $4-6 elsewhere)",
    "use_cases": [
        "Training runs (fine-tuning, LoRA)",
        "Inference endpoints for custom models",
        "Batch processing with raw GPU access",
        "Large model hosting (405B, 70B)",
    ],
}
```

## Lambda Inference API
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.lambdalabs.com/v1",
    api_key=LAMBDA_API_KEY,
)

LAMBDA_MODELS = [
    "hermes-3-llama-3.1-405b-fp8",
    "hermes-3-llama-3.1-70b",
    "llama3.1-nemotron-70b-instruct",
    "qwen2.5-coder-32b-instruct",
    "deepseek-r1-671b",  # Full DeepSeek R1
    "deepseek-v3-0324",
    "llama4-maverick-instruct-17b",
    "llama4-scout-instruct-17b",
    "mistral-large-instruct-2407",
]

def call_lambda(prompt: str, model: str = "llama3.1-nemotron-70b-instruct") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Full DeepSeek R1 671B (only Lambda offers this at accessible price)
def deepseek_r1_full(prompt: str) -> str:
    """Full 671B DeepSeek R1 — not distilled — best reasoning"""
    response = client.chat.completions.create(
        model="deepseek-r1-671b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8192,
    )
    return response.choices[0].message.content
```

## GPU Instance Management
```python
import requests

class LambdaCloudAPI:
    BASE = "https://cloud.lambdalabs.com/api/v1"
    
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Basic {api_key}"}
    
    def list_instances(self):
        return requests.get(f"{self.BASE}/instances", headers=self.headers).json()
    
    def launch_instance(self, instance_type: str, region: str, 
                         ssh_key: str, name: str = "maars-gpu"):
        return requests.post(f"{self.BASE}/instance-operations/launch",
            headers=self.headers,
            json={
                "region_name": region,
                "instance_type_name": instance_type,
                "ssh_key_names": [ssh_key],
                "name": name,
            }
        ).json()
    
    def terminate_instance(self, instance_id: str):
        return requests.post(f"{self.BASE}/instance-operations/terminate",
            headers=self.headers,
            json={"instance_ids": [instance_id]}
        ).json()
    
    def list_instance_types(self):
        """Get available GPU types and pricing"""
        return requests.get(f"{self.BASE}/instance-types",
                           headers=self.headers).json()

# Usage
lambda_api = LambdaCloudAPI(LAMBDA_API_KEY)
# Launch H100 instance
instance = lambda_api.launch_instance(
    instance_type="gpu_8x_h100_sxm5",  # 8x H100
    region="us-east-1",
    ssh_key="my-key"
)
```

## Pricing Reference
```python
LAMBDA_PRICING = {
    # On-demand GPU instances ($/hour)
    "1x_a10": "$0.60",
    "1x_a100_40gb": "$1.29",
    "1x_a100_80gb": "$1.99",
    "1x_h100_pcie": "$2.49",
    "1x_h100_sxm5": "$2.99",
    "8x_h100_sxm5": "$23.92",  # Best multi-GPU price
    
    # Inference API ($/1M tokens)
    "llama3.1_405b_fp8": "$0.40/in, $0.40/out",
    "deepseek_r1_671b": "$0.80/in, $2.40/out",
    "llama4_maverick": "$0.20/in, $0.60/out",
    
    "verdict": "Cheapest H100 + unique full 671B DeepSeek R1 access",
}
```

## When to Use Lambda
- **Cheapest H100**: Lambda often has lowest H100 pricing
- **Full DeepSeek R1 671B**: Only accessible full-size R1 via API
- **Training/fine-tuning**: Cost-effective GPU instances for ML training
- **Persistent GPU**: Long-running jobs that need consistent hardware
- **Nemotron 70B**: NVIDIA's reasoning-optimized Llama variant
