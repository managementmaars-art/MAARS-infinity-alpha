"""RAG (Retrieval-Augmented Generation) service for MAARS Command.
Handles document processing, embedding generation, and semantic search."""

import os
import uuid
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
UPLOAD_DIR = Path(__file__).parent.parent / "backend" / "uploads"
if not UPLOAD_DIR.exists():
    UPLOAD_DIR = Path(__file__).parent / "uploads"


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    text_parts = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 400, chunk_overlap: int = 80) -> List[Dict]:
    """Split text into overlapping chunks, preserving page references."""
    chunks = []
    current_page = 1

    paragraphs = text.split("\n\n")
    current_chunk = ""
    current_sources = set()

    for para in paragraphs:
        # Track page numbers
        if para.strip().startswith("[Page "):
            try:
                current_page = int(para.strip().split("]")[0].replace("[Page ", ""))
            except ValueError:
                pass

        words_in_para = len(para.split())

        if len(current_chunk.split()) + words_in_para > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "pages": sorted(current_sources) if current_sources else [current_page],
            })
            # Keep overlap from the end of current chunk
            overlap_words = current_chunk.split()[-chunk_overlap:]
            current_chunk = " ".join(overlap_words) + " " + para
            current_sources = {current_page}
        else:
            current_chunk += "\n" + para
            current_sources.add(current_page)

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "pages": sorted(current_sources) if current_sources else [current_page],
        })

    return chunks


async def generate_embedding(text: str, api_key: str = None) -> List[float]:
    """Generate embedding vector for text using OpenAI text-embedding-3-small via Emergent proxy."""
    import litellm
    from emergentintegrations.llm.utils import get_integration_proxy_url

    key = api_key or EMERGENT_LLM_KEY
    proxy_url = get_integration_proxy_url()

    response = await litellm.aembedding(
        model="text-embedding-3-small",
        input=[text.replace("\n", " ")[:8000]],
        api_key=key,
        api_base=proxy_url + "/llm",
        custom_llm_provider="openai",
    )

    return response.data[0]["embedding"]


async def generate_embeddings_batch(texts: List[str], api_key: str = None, batch_size: int = 50) -> List[List[float]]:
    """Generate embeddings for multiple texts in batches."""
    import litellm
    from emergentintegrations.llm.utils import get_integration_proxy_url

    key = api_key or EMERGENT_LLM_KEY
    proxy_url = get_integration_proxy_url()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = [t.replace("\n", " ")[:8000] for t in texts[i:i + batch_size]]
        response = await litellm.aembedding(
            model="text-embedding-3-small",
            input=batch,
            api_key=key,
            api_base=proxy_url + "/llm",
            custom_llm_provider="openai",
        )
        all_embeddings.extend([item["embedding"] for item in response.data])

    return all_embeddings


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    dot = np.dot(a_arr, b_arr)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


async def search_knowledge_base(
    db, agent_id: str, query: str, top_k: int = 5, threshold: float = 0.65, api_key: str = None
) -> List[Dict]:
    """Search an agent's knowledge base for relevant chunks."""
    query_embedding = await generate_embedding(query, api_key)

    chunks = await db.knowledge_chunks.find(
        {"agent_id": agent_id},
        {"_id": 0, "text": 1, "embedding": 1, "doc_id": 1, "doc_title": 1, "pages": 1, "chunk_index": 1}
    ).to_list(None)

    if not chunks:
        return []

    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        if score >= threshold:
            scored.append({
                "text": chunk["text"],
                "score": round(score, 4),
                "doc_title": chunk.get("doc_title", "Unknown"),
                "doc_id": chunk.get("doc_id", ""),
                "pages": chunk.get("pages", []),
                "chunk_index": chunk.get("chunk_index", 0),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def build_rag_context(search_results: List[Dict]) -> str:
    """Build a context string from search results for injection into agent prompt."""
    if not search_results:
        return ""

    parts = ["\n--- KNOWLEDGE BASE REFERENCES ---"]
    parts.append("The following excerpts from uploaded documents are relevant to the user's question. Use them to provide accurate, cited answers.\n")

    for i, r in enumerate(search_results, 1):
        page_ref = f" (Page{'s' if len(r['pages']) > 1 else ''} {', '.join(map(str, r['pages']))})" if r.get("pages") else ""
        parts.append(f"[Source {i}: \"{r['doc_title']}\"{page_ref}]")
        parts.append(r["text"])
        parts.append("")

    parts.append("CITATION INSTRUCTIONS: When using information from the sources above, cite them like: \"According to [Document Title], Page X, ...\" or \"(Source: [Document Title], Page X)\". Be specific about which source you're referencing.")
    parts.append("--- END KNOWLEDGE BASE ---\n")
    return "\n".join(parts)
