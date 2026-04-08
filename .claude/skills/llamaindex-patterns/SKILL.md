---
name: llamaindex-patterns
description: LlamaIndex nodes, indexes, query engines, agents, multi-modal RAG, and advanced retrieval patterns.
---

# LlamaIndex Patterns

## Overview

LlamaIndex (formerly GPT Index) specializes in data ingestion and retrieval for LLM applications. It provides sophisticated indexing, retrieval strategies, agents, and multi-modal support out of the box.

## Installation

```bash
pip install llama-index llama-index-llms-anthropic llama-index-llms-openai
pip install llama-index-embeddings-openai llama-index-vector-stores-chroma
pip install llama-index-readers-file llama-index-multi-modal-llms-anthropic
```

## Setup

```python
from llama_index.core import Settings
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Global settings (applies to all indexes/queries)
Settings.llm = Anthropic(model="claude-opus-4-5", max_tokens=4096)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
Settings.chunk_size = 512
Settings.chunk_overlap = 64
```

## Document Ingestion & Nodes

```python
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
    HierarchicalNodeParser,
)
from llama_index.core.schema import TextNode, NodeRelationship

# Load documents from directory
documents = SimpleDirectoryReader(
    "./docs",
    required_exts=[".pdf", ".txt", ".md"],
    recursive=True,
    filename_as_id=True,
).load_data()

# Or create manually
doc = Document(
    text="This is the document content...",
    metadata={
        "source": "manual",
        "category": "tech",
        "date": "2024-01-01",
    },
    excluded_llm_metadata_keys=["date"],  # Don't send to LLM
    excluded_embed_metadata_keys=["source"],
)

# Sentence-based splitting (preserves context)
sentence_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
nodes = sentence_splitter.get_nodes_from_documents(documents)

# Semantic splitting (splits on topic boundaries)
semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=Settings.embed_model,
)
semantic_nodes = semantic_splitter.get_nodes_from_documents(documents)

# Hierarchical splitting (for parent-child retrieval)
hierarchical_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]  # Parent -> child -> grandchild
)
all_nodes = hierarchical_parser.get_nodes_from_documents(documents)

print(f"Loaded {len(documents)} docs -> {len(nodes)} nodes")
```

## Vector Store Index

```python
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Chroma vector store
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("my_docs")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Build index (embeds and stores)
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    show_progress=True,
)

# Or add nodes incrementally
index.insert_nodes(new_nodes)

# Load existing index (no re-embedding)
index = VectorStoreIndex.from_vector_store(vector_store)

# Query
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="tree_summarize",  # tree_summarize | refine | compact | simple_summarize
)
response = query_engine.query("What is the main topic?")
print(response.response)

# Access source nodes
for node in response.source_nodes:
    print(f"Score: {node.score:.3f} | {node.text[:100]}")
```

## Advanced Retrieval

```python
from llama_index.core.retrievers import (
    VectorIndexRetriever,
    BM25Retriever,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
    MetadataReplacementPostProcessor,
    LLMRerank,
    SentenceTransformerRerank,
)
from llama_index.core.retrievers import QueryFusionRetriever

# Hybrid retrieval (BM25 + vector)
bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)
vector_retriever = VectorIndexRetriever(index=index, similarity_top_k=10)

hybrid_retriever = QueryFusionRetriever(
    [bm25_retriever, vector_retriever],
    similarity_top_k=5,
    num_queries=4,          # Generate query variants
    mode="reciprocal_rerank",
    use_async=True,
)

# Reranking for precision
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=3,
)

query_engine = RetrieverQueryEngine(
    retriever=hybrid_retriever,
    node_postprocessors=[
        SimilarityPostprocessor(similarity_cutoff=0.7),
        reranker,
    ],
)

# Small-to-big retrieval (retrieve small chunks, return parent context)
from llama_index.core.node_parser import get_leaf_nodes, get_root_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.storage.docstore import SimpleDocumentStore

docstore = SimpleDocumentStore()
docstore.add_documents(all_nodes)

base_retriever = index.as_retriever(similarity_top_k=12)
auto_merging_retriever = AutoMergingRetriever(
    base_retriever,
    storage_context=StorageContext.from_defaults(docstore=docstore),
    verbose=True,
)
```

## LlamaIndex Agents

```python
from llama_index.core.agent import ReActAgent, FunctionCallingAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool

# Function tools
def search_products(query: str, max_results: int = 5) -> str:
    """Search the product catalog for items matching the query."""
    results = product_db.search(query, limit=max_results)
    return "\n".join(f"- {r['name']}: ${r['price']}" for r in results)

def get_inventory(product_id: str) -> dict:
    """Get current inventory level for a product."""
    return inventory_service.get(product_id)

search_tool = FunctionTool.from_defaults(fn=search_products)
inventory_tool = FunctionTool.from_defaults(fn=get_inventory)

# Query engine as a tool
docs_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="product_documentation",
    description="Search product documentation, manuals, and FAQs.",
)

# ReAct agent
agent = ReActAgent.from_tools(
    [search_tool, inventory_tool, docs_tool],
    llm=Settings.llm,
    verbose=True,
    max_iterations=10,
)

response = agent.chat("What products do you have under $50 and are they in stock?")
print(response.response)

# Multi-agent orchestration
from llama_index.core.agent.runner.planner import StructuredPlannerAgent

planner = StructuredPlannerAgent.from_defaults(
    tools=[search_tool, inventory_tool, docs_tool],
    llm=Settings.llm,
    verbose=True,
)
```

## Multi-Modal RAG

```python
from llama_index.core.indices.multi_modal import MultiModalVectorStoreIndex
from llama_index.core.schema import ImageDocument
from llama_index.multi_modal_llms.anthropic import AnthropicMultiModal

# Load images as documents
image_documents = SimpleDirectoryReader(
    "./images",
    required_exts=[".jpg", ".png"],
).load_data()

# Create multi-modal index
mm_index = MultiModalVectorStoreIndex.from_documents(
    documents + image_documents,   # Text + images
    image_embed_model="clip",
)

# Multi-modal query
mm_llm = AnthropicMultiModal(model="claude-opus-4-5", max_tokens=2048)
mm_query_engine = mm_index.as_query_engine(
    multi_modal_llm=mm_llm,
    similarity_top_k=3,
)

response = mm_query_engine.query("What products are shown in the catalog images?")
```

## Document Summary Index

```python
from llama_index.core import DocumentSummaryIndex

# Build summary index for each document
summary_index = DocumentSummaryIndex.from_documents(
    documents,
    show_progress=True,
    summary_query="Summarize the key points of this document in 2-3 sentences.",
)

# Query by document summary
summary_retriever = summary_index.as_retriever(
    retriever_mode="embedding",     # or "llm"
    similarity_top_k=3,
)

# Get summary for a specific document
summary = summary_index.get_document_summary("doc_id")
```

## Evaluation

```python
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
    BatchEvalRunner,
)

faithfulness_evaluator = FaithfulnessEvaluator()
relevancy_evaluator = RelevancyEvaluator()

# Evaluate a single response
query = "What is the return policy?"
response = query_engine.query(query)

faith_result = faithfulness_evaluator.evaluate_response(response=response)
rel_result = relevancy_evaluator.evaluate_response(query=query, response=response)

print(f"Faithful: {faith_result.passing} (score: {faith_result.score})")
print(f"Relevant: {rel_result.passing} (score: {rel_result.score})")

# Batch evaluation
runner = BatchEvalRunner(
    {"faithfulness": faithfulness_evaluator, "relevancy": relevancy_evaluator},
    workers=4,
)
eval_results = await runner.aevaluate_queries(
    query_engine,
    queries=["Query 1", "Query 2", "Query 3"],
)
```

## Key Patterns

- **SemanticSplitter** produces topic-coherent chunks — better than fixed-size for RAG
- **Auto-merging retrieval** retrieves small chunks but returns surrounding parent context
- **Hybrid retrieval** (BM25 + vector) outperforms pure vector search for keyword-heavy queries
- **LLM reranking** dramatically improves precision but adds latency — use SentenceTransformer for speed
- **DocumentSummaryIndex** enables document-level routing before chunk retrieval
- **Evaluation** with faithfulness/relevancy metrics is essential for production RAG

## Models to Use

- **claude-opus-4-5**: Complex agent design, multi-modal RAG, research pipelines
- **claude-sonnet-4-5**: Standard RAG pipelines, custom retrievers, evaluation setup
- **claude-haiku-3-5**: Simple index queries, document loading, embedding operations
