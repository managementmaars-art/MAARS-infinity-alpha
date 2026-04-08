---
name: ai21-api
description: AI21 Labs Jamba models — long context, RAG-optimized, enterprise LLMs via AI21 Studio API for MAARS LLM routing
---

# AI21 Labs API — MAARS Reference

## Models
```python
AI21_MODELS = {
    "jamba-1.6-large": {
        "context": "256K tokens",
        "architecture": "SSM + Transformer hybrid (Mamba)",
        "strengths": "Long context at low cost, fast inference",
        "params": "94B active / 398B total (MoE)",
        "best_for": "Document analysis, RAG, long summarization",
        "pricing": "$2.00/1M input, $8.00/1M output",
    },
    "jamba-1.6-mini": {
        "context": "256K tokens",
        "strengths": "Very fast, cost-efficient, 256K context",
        "params": "12B active / 52B total",
        "best_for": "High-volume classification, quick Q&A over docs",
        "pricing": "$0.20/1M input, $0.40/1M output",
    },
    "jamba-1.5-large": {
        "context": "256K tokens",
        "architecture": "Hybrid SSM-Transformer",
        "pricing": "$2.00/1M input, $8.00/1M output",
    },
    "jamba-1.5-mini": {
        "context": "256K tokens",
        "pricing": "$0.20/1M input, $0.40/1M output",
    },
}
```

## API Integration
```python
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

client = AI21Client(api_key=AI21_API_KEY)

def call_jamba(prompt: str, model: str = "jamba-1.6-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[ChatMessage(role="user", content=prompt)],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Streaming
def stream_jamba(prompt: str):
    response = client.chat.completions.create(
        model="jamba-1.6-mini",
        messages=[ChatMessage(role="user", content=prompt)],
        stream=True,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

## OpenAI-Compatible Interface
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.ai21.com/studio/v1",
    api_key=AI21_API_KEY,
)

response = client.chat.completions.create(
    model="jamba-1.6-mini",
    messages=[{"role": "user", "content": "Summarize this document: ..."}],
    max_tokens=1024,
)
```

## Long Document Analysis (Key Use Case)
```python
def analyze_long_document(document_text: str, questions: list[str]) -> dict:
    """
    Jamba's 256K context = ~200,000 words = full-length books, contracts, codebases
    """
    system_prompt = """You are a document analyst. Answer questions about the 
    provided document with precision. Cite specific sections."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document:\n{document_text}\n\nQuestions:\n" + 
                                    "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))}
    ]
    
    response = client.chat.completions.create(
        model="jamba-1.6-large",
        messages=messages,
        max_tokens=4096,
        temperature=0.1,  # Low temp for factual extraction
    )
    return {"answers": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens}

# Typical usage: entire legal contracts, full codebases, long research papers
```

## RAG with Jamba
```python
def jamba_rag(query: str, retrieved_chunks: list[str], top_k: int = 20) -> str:
    """
    Jamba can handle more retrieved chunks than other models due to long context.
    Pass top_k=20 chunks instead of typical top_k=5 for better recall.
    """
    context = "\n\n---\n\n".join(retrieved_chunks)
    
    response = client.chat.completions.create(
        model="jamba-1.6-mini",
        messages=[{
            "role": "system",
            "content": "Answer based only on the provided context. Cite sources."
        }, {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }],
        max_tokens=1024,
        temperature=0.0,
    )
    return response.choices[0].message.content
```

## When to Use AI21 Jamba
- **Long documents**: 256K context at lower cost than competing models
- **High-volume classification**: Jamba Mini at $0.20/1M input
- **Document Q&A**: Feed entire document in context (no chunking needed)
- **Enterprise RAG**: Pass many more chunks → better answers
- **Cost-sensitive long context**: Cheaper than Claude/GPT for same context size
