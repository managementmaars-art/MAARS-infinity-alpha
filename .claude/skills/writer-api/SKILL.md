---
name: writer-api
description: Writer AI platform — Palmyra models, enterprise AI applications, content generation, knowledge graph, RAG for MAARS enterprise content agents
---

# Writer API — MAARS Reference

## Models
```python
WRITER_MODELS = {
    "palmyra-x-004": {
        "context": "128K tokens",
        "strengths": "Enterprise-grade, instruction following, reliable output",
        "features": ["Tool use", "Structured output", "Knowledge Graph RAG"],
        "best_for": "Enterprise workflows, consistent brand voice, content ops",
        "pricing": "$6.00/1M input, $12.00/1M output",
    },
    "palmyra-x-004-instruct": {
        "context": "128K tokens",
        "best_for": "Chat, instructions, Q&A",
    },
    "palmyra-vision": {
        "multimodal": True,
        "best_for": "Document understanding, image analysis for enterprise",
    },
    "palmyra-med-70b": {
        "domain": "Healthcare",
        "best_for": "Medical documentation, clinical notes, health content",
    },
    "palmyra-fin-32k": {
        "domain": "Finance",
        "best_for": "Financial reports, market analysis, compliance docs",
    },
}
```

## API Integration
```python
import writer

client = writer.Writer(api_key=WRITER_API_KEY)

# Chat completions
def call_palmyra(messages: list, model: str = "palmyra-x-004"):
    response = client.chat.chat(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# OpenAI-compatible
from openai import OpenAI

compat_client = OpenAI(
    base_url="https://api.writer.com/v1",
    api_key=WRITER_API_KEY,
)

response = compat_client.chat.completions.create(
    model="palmyra-x-004",
    messages=[{"role": "user", "content": "Write a product description"}],
)
```

## Knowledge Graph (Writer's Enterprise RAG)
```python
# Writer Knowledge Graph — enterprise knowledge base
# Index company documents, policies, brand guidelines

def add_to_knowledge_graph(file_path: str, graph_id: str):
    """Index documents into Writer's Knowledge Graph"""
    with open(file_path, "rb") as f:
        file_obj = client.files.upload(content=f.read(),
                                        content_disposition=f"inline; filename={file_path.split('/')[-1]}")
    
    # Add file to graph
    client.graphs.add_file_to_graph(
        graph_id=graph_id,
        file_id=file_obj.id,
    )

def query_knowledge_graph(question: str, graph_id: str):
    """RAG query against Writer Knowledge Graph"""
    response = client.graphs.question(
        graph_id=graph_id,
        question=question,
        subqueries=True,
    )
    return {
        "answer": response.answer,
        "sources": [s.file_id for s in response.sources],
    }
```

## Content Generation Workflows
```python
# AI Studio workflows — no-code AI app builder
WORKFLOW_EXAMPLES = {
    "blog_post_pipeline": {
        "steps": [
            "Research query → Palmyra + web search",
            "Outline generation → Palmyra structured",
            "Section drafting → Palmyra with brand voice",
            "SEO optimization → check keyword density",
            "Brand compliance → Knowledge Graph check",
        ],
    },
    "brand_voice_enforcement": {
        "description": "Ensure all content matches brand guidelines",
        "setup": [
            "Upload brand guidelines to Knowledge Graph",
            "Use system prompt with KG retrieval",
            "Score output against brand rubric",
        ],
    },
}

def enforce_brand_voice(draft: str, brand_guide_id: str) -> dict:
    """Check and rewrite content for brand compliance"""
    # First check against brand knowledge
    compliance = query_knowledge_graph(
        f"Does this text comply with our brand voice? Text: {draft[:500]}",
        brand_guide_id
    )
    
    if "non-compliant" in compliance["answer"].lower():
        # Rewrite for compliance
        rewritten = call_palmyra([{
            "role": "system",
            "content": f"Brand guidelines: {compliance['answer']}\nRewrite the following to comply:"
        }, {
            "role": "user",
            "content": draft,
        }])
        return {"status": "rewritten", "content": rewritten}
    
    return {"status": "compliant", "content": draft}
```

## Tool Use / Function Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_database",
        "description": "Search the company product database",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string", "enum": ["products", "pricing", "specs"]},
            },
            "required": ["query"],
        },
    }
}]

response = compat_client.chat.completions.create(
    model="palmyra-x-004",
    messages=[{"role": "user", "content": "What's the price of product X?"}],
    tools=tools,
    tool_choice="auto",
)
```

## When to Use Writer
- **Enterprise content at scale**: Built for content ops teams
- **Brand voice compliance**: Knowledge Graph keeps content on-brand
- **Domain-specific**: Palmyra-Med for healthcare, Palmyra-Fin for finance
- **No-code AI apps**: AI Studio for non-technical teams
- **SOC 2 Type II**: Enterprise security and compliance
