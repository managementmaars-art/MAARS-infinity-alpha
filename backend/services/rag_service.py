"""RAG (Retrieval-Augmented Generation) service for MAARS Command.
Uses TF-IDF + cosine similarity for fast, effective document search without external API calls."""

import logging
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file with page markers."""
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


async def search_knowledge_base(
    db, agent_id: str, query: str, top_k: int = 5, threshold: float = 0.10,
) -> List[Dict]:
    """Search an agent's knowledge base using TF-IDF similarity."""
    chunks = await db.knowledge_chunks.find(
        {"agent_id": agent_id},
        {"_id": 0, "text": 1, "doc_id": 1, "doc_title": 1, "pages": 1, "chunk_index": 1}
    ).to_list(None)

    if not chunks:
        return []

    chunk_texts = [c["text"] for c in chunks]

    # TF-IDF vectorization with query
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    all_texts = chunk_texts + [query]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    query_vec = tfidf_matrix[-1]
    chunk_vecs = tfidf_matrix[:-1]

    similarities = sklearn_cosine(query_vec, chunk_vecs).flatten()

    scored = []
    for i, score in enumerate(similarities):
        if score >= threshold:
            scored.append({
                "text": chunks[i]["text"],
                "score": round(float(score), 4),
                "doc_title": chunks[i].get("doc_title", "Unknown"),
                "doc_id": chunks[i].get("doc_id", ""),
                "pages": chunks[i].get("pages", []),
                "chunk_index": chunks[i].get("chunk_index", 0),
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
