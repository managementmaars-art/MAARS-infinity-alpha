---
name: upstage-api
description: Upstage Solar models — document parsing, OCR, multilingual models, Solar Pro for MAARS document processing agents
---

# Upstage API — MAARS Reference

## Models
```python
UPSTAGE_MODELS = {
    "solar-pro": {
        "context": "32K",
        "strengths": "Strong reasoning, multilingual, efficient",
        "params": "22B",
        "best_for": "Enterprise reasoning tasks, multilingual chat",
        "pricing": "$0.50/1M input, $1.50/1M output",
    },
    "solar-mini": {
        "context": "32K",
        "strengths": "Fast, cost-efficient",
        "pricing": "$0.20/1M input, $0.60/1M output",
        "best_for": "High-volume classification, simple tasks",
    },
    "document-parse": {
        "type": "Document OCR + structure extraction",
        "strengths": "Best-in-class document parsing (PDFs, images, tables)",
        "output": "Markdown with structure preserved",
        "best_for": "PDF parsing for RAG, contract analysis, invoice processing",
    },
    "solar-embedding-1": {
        "dims": 4096,
        "strengths": "Multilingual embeddings (100+ languages)",
        "best_for": "Multilingual RAG, semantic search",
    },
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.upstage.ai/v1",
    api_key=UPSTAGE_API_KEY,
)

def call_solar(prompt: str, model: str = "solar-pro") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="solar-embedding-1",
        input=text,
    )
    return response.data[0].embedding
```

## Document Parse (Key Differentiator)
```python
import requests

def parse_document(file_path: str, output_format: str = "markdown") -> dict:
    """
    Upstage Document Parse — extracts text, tables, figures from PDFs/images
    Returns clean markdown ready for LLM processing / RAG
    """
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://api.upstage.ai/v1/document-digitization",
            headers={"Authorization": f"Bearer {UPSTAGE_API_KEY}"},
            files={"document": f},
            data={
                "output_formats": '["markdown", "html"]',
                "ocr": "force",  # Always OCR, even PDFs with text layer
                "coordinates": True,  # Include element positions
                "chart_recognition": True,
                "table_recognition": True,
            }
        )
    result = resp.json()
    return {
        "markdown": result["content"]["markdown"],
        "html": result["content"]["html"],
        "elements": result["elements"],  # Structured: paragraphs, tables, figures
        "pages": result["usage"]["pages"],
    }

def process_invoice(invoice_path: str) -> dict:
    """Extract structured data from invoice using Document Parse + Solar"""
    # Step 1: Parse document to markdown
    parsed = parse_document(invoice_path)
    markdown = parsed["markdown"]
    
    # Step 2: Extract structured data with Solar
    extraction_prompt = f"""
Extract invoice data from this document and return as JSON:
{markdown}

Return: vendor_name, invoice_number, date, due_date, line_items (list), 
subtotal, tax, total_amount, currency
"""
    import json
    result = call_solar(extraction_prompt, model="solar-mini")
    # Parse the JSON response
    json_start = result.find("{")
    json_end = result.rfind("}") + 1
    return json.loads(result[json_start:json_end])
```

## RAG Pipeline with Upstage
```python
def build_document_rag(pdf_paths: list, query: str) -> str:
    """
    Upstage Document Parse → Chunk → Embed → Retrieve → Answer
    Best pipeline for PDF-heavy RAG
    """
    all_chunks = []
    
    for path in pdf_paths:
        # Parse with structure preservation
        parsed = parse_document(path)
        
        # Smart chunking (by element, not arbitrary chars)
        for element in parsed["elements"]:
            if element["category"] in ["paragraph", "table", "figure"]:
                all_chunks.append({
                    "text": element["content"]["markdown"],
                    "type": element["category"],
                    "page": element["page"],
                    "source": path,
                })
    
    # Embed all chunks
    embeddings = [get_embedding(chunk["text"]) for chunk in all_chunks]
    
    # Retrieve top-k
    query_embedding = get_embedding(query)
    
    import numpy as np
    similarities = [np.dot(query_embedding, e) for e in embeddings]
    top_k_indices = np.argsort(similarities)[-5:][::-1]
    
    context = "\n\n".join(all_chunks[i]["text"] for i in top_k_indices)
    
    return call_solar(f"Context:\n{context}\n\nQuestion: {query}")
```

## When to Use Upstage
- **Document-heavy RAG**: Best document parsing (PDFs, scanned docs, tables)
- **Invoice/receipt processing**: Structured extraction from financial docs
- **Korean/multilingual**: Upstage is Korean company, strong Korean + multilingual
- **Cost-effective reasoning**: Solar Pro at $0.50/1M is competitive
- **OCR pipelines**: Document Parse handles complex layouts other parsers miss
