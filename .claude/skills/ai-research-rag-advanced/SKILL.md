---
name: ai-research-rag-advanced
description: "Advanced RAG: HyDE, RAPTOR, GraphRAG, ColBERT, late interaction, multi-hop reasoning"
---

# Advanced RAG Patterns

Beyond naive RAG: HyDE (hypothetical document embeddings), RAPTOR (recursive summarization), GraphRAG (knowledge graph retrieval), ColBERT late interaction for dense retrieval, and multi-hop reasoning chains.

## HyDE: Hypothetical Document Embeddings

Instead of embedding the raw question, generate a hypothetical answer and embed that — it matches the document distribution better:

```python
from openai import OpenAI
import numpy as np
from typing import Callable

client = OpenAI()

def generate_hypothetical_document(question: str, domain: str = "general") -> str:
    """Generate a hypothetical answer that looks like a retrieved document."""
    system = f"""You are an expert in {domain}. Write a detailed, factual passage that would 
DIRECTLY answer the following question. Write as if you are writing an encyclopedia entry.
Do not say 'I' or reference the question. Just write the passage."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Question: {question}"}
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content

def get_embedding(text: str, model: str = "text-embedding-3-large") -> list[float]:
    return client.embeddings.create(input=text, model=model).data[0].embedding

def hyde_retrieve(
    question: str,
    vector_store,
    k: int = 5,
    n_hypothetical: int = 3,
    domain: str = "general",
) -> list[dict]:
    """HyDE retrieval: generate multiple hypothetical documents, embed, and average."""
    hypotheticals = [generate_hypothetical_document(question, domain) for _ in range(n_hypothetical)]

    # Average embeddings from multiple hypothetical documents (reduces variance)
    embeddings = np.array([get_embedding(h) for h in hypotheticals])
    averaged_embedding = embeddings.mean(axis=0)
    averaged_embedding = averaged_embedding / np.linalg.norm(averaged_embedding)

    return vector_store.similarity_search_by_vector(averaged_embedding.tolist(), k=k)
```

## RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

Builds a hierarchical tree of document summaries, enabling retrieval at multiple levels of abstraction:

```python
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import numpy as np
import umap

def raptor_build_tree(
    documents: list[str],
    max_levels: int = 3,
    cluster_size: int = 5,
) -> dict:
    """Build RAPTOR tree: cluster documents, summarize clusters, repeat."""
    tree = {"level_0": documents, "summaries": {}}
    current_texts = documents

    for level in range(1, max_levels + 1):
        if len(current_texts) <= cluster_size:
            break

        # Embed current level texts
        embeddings = np.array([get_embedding(t) for t in current_texts])

        # Reduce dimensions with UMAP before clustering (handles high-dim better)
        n_components = min(len(current_texts) - 1, 10)
        reducer = umap.UMAP(n_components=n_components, random_state=42, metric="cosine")
        reduced = reducer.fit_transform(embeddings)

        # Determine optimal number of clusters with BIC
        n_clusters = max(2, len(current_texts) // cluster_size)
        gmm = GaussianMixture(n_components=n_clusters, random_state=42, covariance_type="full")
        gmm.fit(reduced)
        labels = gmm.predict(reduced)

        # Summarize each cluster
        summaries = []
        for cluster_id in range(n_clusters):
            cluster_texts = [t for t, l in zip(current_texts, labels) if l == cluster_id]
            if not cluster_texts:
                continue
            summary = summarize_cluster(cluster_texts)
            summaries.append(summary)

        tree[f"level_{level}"] = summaries
        tree["summaries"][f"level_{level}"] = {
            "texts": summaries,
            "source_clusters": {i: [t for t, l in zip(current_texts, labels) if l == i]
                                for i in range(n_clusters)}
        }
        current_texts = summaries

    return tree

def summarize_cluster(texts: list[str], max_length: int = 500) -> str:
    combined = "\n\n".join(texts[:10])  # cap context
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Synthesize the following passages into a comprehensive summary "
                       f"(max {max_length} words):\n\n{combined}"
        }],
        max_tokens=max_length * 2,
    )
    return response.choices[0].message.content

def raptor_retrieve(question: str, tree: dict, k: int = 5) -> list[str]:
    """Retrieve from all tree levels, then deduplicate and rank."""
    all_texts = []
    for level in range(len([k for k in tree if k.startswith("level")])):
        all_texts.extend(tree[f"level_{level}"])

    # Embed query and all texts, rank by similarity
    q_emb = np.array(get_embedding(question))
    similarities = []
    for text in all_texts:
        t_emb = np.array(get_embedding(text))
        sim = np.dot(q_emb, t_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(t_emb))
        similarities.append((text, float(sim)))

    ranked = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [text for text, _ in ranked[:k]]
```

## GraphRAG: Knowledge Graph-Enhanced Retrieval

```python
from neo4j import GraphDatabase
import json

class GraphRAG:
    """RAG system that uses a knowledge graph for relationship-aware retrieval."""

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_pass: str, vector_store):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        self.vector_store = vector_store

    def build_graph_from_documents(self, documents: list[dict]):
        """Extract entities and relationships, store in Neo4j."""
        for doc in documents:
            entities = self._extract_entities(doc["content"])

            with self.driver.session() as session:
                # Create document node
                session.run("""
                    MERGE (d:Document {id: $doc_id})
                    SET d.content = $content, d.title = $title
                """, doc_id=doc["id"], content=doc["content"], title=doc.get("title", ""))

                for entity in entities:
                    session.run("""
                        MERGE (e:Entity {name: $name, type: $type})
                        MERGE (d:Document {id: $doc_id})
                        MERGE (d)-[:MENTIONS]->(e)
                    """, name=entity["name"], type=entity["type"], doc_id=doc["id"])

                    for related in entity.get("related_to", []):
                        session.run("""
                            MERGE (a:Entity {name: $name})
                            MERGE (b:Entity {name: $related})
                            MERGE (a)-[:RELATED_TO {relation: $relation}]->(b)
                        """, name=entity["name"], related=related["name"],
                             relation=related.get("relation", "related_to"))

    def _extract_entities(self, text: str) -> list[dict]:
        """Use LLM to extract entities and relationships."""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""Extract entities and relationships from this text as JSON.
Format: [{{"name": "...", "type": "PERSON|ORG|CONCEPT|PLACE", "related_to": [{{"name": "...", "relation": "..."}}]}}]
Text: {text[:2000]}"""
            }],
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(response.choices[0].message.content)
            return data if isinstance(data, list) else data.get("entities", [])
        except (json.JSONDecodeError, AttributeError):
            return []

    def retrieve(self, question: str, k: int = 5) -> list[str]:
        """Hybrid retrieval: vector similarity + graph traversal."""
        # 1. Vector retrieval
        vector_docs = self.vector_store.similarity_search(question, k=k)

        # 2. Extract entities from question
        question_entities = self._extract_entities(question)
        entity_names = [e["name"] for e in question_entities]

        # 3. Graph traversal to find related documents
        graph_docs = []
        if entity_names:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (e:Entity)-[:RELATED_TO*1..2]-(related:Entity)
                    WHERE e.name IN $entity_names
                    MATCH (d:Document)-[:MENTIONS]->(related)
                    RETURN DISTINCT d.content AS content, d.id AS doc_id,
                           count(*) AS relevance_score
                    ORDER BY relevance_score DESC
                    LIMIT $limit
                """, entity_names=entity_names, limit=k)
                graph_docs = [r["content"] for r in result]

        # 4. Merge and deduplicate
        all_contexts = [d.page_content for d in vector_docs] + graph_docs
        seen = set()
        unique_contexts = []
        for ctx in all_contexts:
            key = ctx[:100]  # deduplicate by prefix
            if key not in seen:
                seen.add(key)
                unique_contexts.append(ctx)

        return unique_contexts[:k * 2]
```

## ColBERT: Late Interaction Dense Retrieval

```python
# Using RAGatouille wrapper for ColBERT v2
from ragatouille import RAGPretrainedModel

# Index documents with ColBERT
RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
RAG.index(
    collection=documents,          # list of strings
    index_name="my_knowledge_base",
    max_document_length=256,
    split_documents=True,
    document_metadatas=metadata,   # list of dicts
)

# Load existing index
RAG = RAGPretrainedModel.from_index("my_knowledge_base")

def colbert_retrieve(query: str, k: int = 10) -> list[dict]:
    """Late interaction retrieval: MaxSim over token embeddings."""
    results = RAG.search(query=query, k=k)
    return [
        {
            "content": r["content"],
            "score": r["score"],
            "metadata": r.get("document_metadata", {}),
        }
        for r in results
    ]

# ColBERT vs. bi-encoder:
# Bi-encoder: embed query → single vector; embed doc → single vector; dot product
# ColBERT: embed query → token matrix; embed doc → token matrix; MaxSim aggregation
# ColBERT is more accurate but stores ~100x more data and requires dedicated server
```

## Multi-Hop Reasoning

```python
class MultiHopRAG:
    """Iteratively retrieves evidence for complex multi-step questions."""

    def __init__(self, vector_store, max_hops: int = 3):
        self.vector_store = vector_store
        self.max_hops = max_hops

    def answer(self, question: str) -> dict:
        """Decompose question and retrieve evidence iteratively."""
        evidence = []
        sub_questions = self._decompose_question(question)

        for hop, sub_q in enumerate(sub_questions[:self.max_hops]):
            # Retrieve evidence for this hop
            docs = self.vector_store.similarity_search(
                sub_q + " " + " ".join(e["answer"] for e in evidence),  # context-aware query
                k=3,
            )
            context = "\n".join(d.page_content for d in docs)

            # Generate intermediate answer
            intermediate_answer = self._answer_with_context(sub_q, context)
            evidence.append({"question": sub_q, "context": context, "answer": intermediate_answer})

        # Final synthesis
        final_answer = self._synthesize(question, evidence)
        return {"answer": final_answer, "evidence_chain": evidence}

    def _decompose_question(self, question: str) -> list[str]:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""Decompose this complex question into 2-4 simpler sub-questions 
that should be answered in order. Return a JSON list of strings.
Question: {question}"""
            }],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return data if isinstance(data, list) else data.get("questions", [question])

    def _answer_with_context(self, question: str, context: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}\n\nBrief answer:"
            }],
            max_tokens=256,
        )
        return response.choices[0].message.content

    def _synthesize(self, original_question: str, evidence: list[dict]) -> str:
        evidence_text = "\n".join(
            f"Step {i+1}: Q: {e['question']}\nA: {e['answer']}"
            for i, e in enumerate(evidence)
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Using the following reasoning chain, answer the original question.

Reasoning chain:
{evidence_text}

Original question: {original_question}

Comprehensive answer:"""
            }],
            max_tokens=1024,
        )
        return response.choices[0].message.content
```

## Contextual Compression and Reranking

```python
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cuda")

def rerank(query: str, documents: list[str], top_k: int = 5) -> list[str]:
    """Rerank retrieved documents with a cross-encoder."""
    pairs = [[query, doc] for doc in documents]
    scores = cross_encoder.predict(pairs, batch_size=32, show_progress_bar=False)
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]

def compress_context(query: str, document: str, max_tokens: int = 300) -> str:
    """Extract only the relevant portion of a document."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"""Extract ONLY the parts of the document that are directly relevant 
to the question. Preserve exact wording. If nothing is relevant, reply 'NOT_RELEVANT'.

Question: {query}
Document: {document}

Relevant extract:"""
        }],
        max_tokens=max_tokens,
    )
    result = response.choices[0].message.content
    return "" if "NOT_RELEVANT" in result else result
```

## Best Practices

- **Baseline first**: always benchmark naive RAG before implementing HyDE, RAPTOR, or GraphRAG — complexity has a cost
- **HyDE** helps most when the query style differs significantly from document style (e.g., questions vs. reports)
- **RAPTOR** excels for long-document question answering where the answer spans multiple sections
- **GraphRAG** is best for relationship-heavy domains (medical, legal, financial) where entity connections matter
- **ColBERT** beats bi-encoders on complex queries but costs ~100x more storage — use for high-stakes retrieval
- Always **rerank** with a cross-encoder after initial retrieval — it's cheap and gives significant accuracy gains
- Use **contextual compression** before feeding to LLM — reduce noise, stay within context window
- For multi-hop: **decompose-then-retrieve** beats single-shot retrieval on 2+ step reasoning by ~20%
- Monitor **retrieval precision** separately from **generation quality** — they fail for different reasons
- Test RAG with **RAGAS** framework: context_precision, context_recall, answer_relevancy, faithfulness

## Models to Use

- **Default**: `claude-sonnet-4-5` — RAG pipelines, reranking, multi-hop chains
- **Complex research**: `claude-opus-4-5` — GraphRAG architecture, custom retrieval models, novel RAG variants
- **Quick utilities**: `claude-haiku-3-5` — entity extraction prompts, simple summarization, context compression
