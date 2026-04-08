---
name: bedrock-api
description: AWS Bedrock API — Nova Pro/Lite, Claude on Bedrock, Llama on Bedrock — enterprise cloud AI with AWS compliance, VPC, and IAM integration
---

# AWS Bedrock — MAARS Reference

## Models
| Model ID | Provider | Strength |
|----------|---------|----------|
| `amazon.nova-pro-v1:0` | Amazon | Flagship Nova, multimodal |
| `amazon.nova-lite-v1:0` | Amazon | Fast, cost-efficient |
| `amazon.nova-micro-v1:0` | Amazon | Ultra-fast text only |
| `anthropic.claude-opus-4-6-20251101-v1:0` | Anthropic | Best Claude on AWS |
| `anthropic.claude-sonnet-4-6-20251101-v1:0` | Anthropic | Balanced Claude on AWS |
| `meta.llama4-maverick-17b-instruct-v1:0` | Meta | Llama 4 on AWS |
| `mistral.mistral-large-2402-v1:0` | Mistral | Mistral on AWS |

## Python Client (boto3)
```python
import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def invoke_nova(prompt: str, model_id: str = "amazon.nova-pro-v1:0") -> str:
    body = {
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 4096, "temperature": 0.7},
    }
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
    )
    return json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]
```

## Streaming
```python
def stream_nova(prompt: str) -> str:
    body = {"messages": [{"role": "user", "content": [{"text": prompt}]}]}
    response = bedrock.invoke_model_with_response_stream(
        modelId="amazon.nova-pro-v1:0",
        body=json.dumps(body),
    )
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if "contentBlockDelta" in chunk:
            yield chunk["contentBlockDelta"]["delta"]["text"]
```

## OpenAI-Compatible (Bedrock Converse)
```python
# Use LiteLLM for OpenAI-compat interface
import litellm

response = await litellm.acompletion(
    model="bedrock/amazon.nova-pro-v1:0",
    messages=messages,
    aws_region_name="us-east-1",
)
```

## MAARS Use Cases
- Enterprise clients requiring AWS compliance (SOC2, HIPAA, FedRAMP)
- Data residency requirements (keep data in specific AWS regions)
- VPC-isolated inference for sensitive workloads
- AWS-native integration (Lambda, S3, SageMaker pipelines)

## MAARS Config
```python
{
    "model_provider": "bedrock",
    "model_name": "amazon.nova-pro-v1:0",
    "api_key_env": "AWS_ACCESS_KEY_ID",
    "region": "us-east-1",
}
```
