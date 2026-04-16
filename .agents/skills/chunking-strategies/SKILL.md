---
name: chunking-strategies
description: |
  Expert guidance on document chunking strategies for RAG systems.
  Use this skill when designing how to split documents for vector embeddings.
  Activate when: chunking, chunk size, text splitting, document segmentation, overlap, semantic chunking, recursive splitting.
---

# Chunking Strategies for RAG

**Optimize document splitting for retrieval accuracy and context preservation.**

## When to Use

- Designing a new RAG pipeline
- Retrieval quality is poor due to chunk boundaries
- Documents have mixed content types (code, tables, prose)
- Need to balance context window limits with retrieval precision

## Chunking Methods

### 1. Fixed-Size Chunking

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separator="\n"
)
chunks = splitter.split_text(document)
```

**Best for**: Homogeneous content, quick prototyping
**Avoid when**: Documents have natural boundaries (sections, paragraphs)

### 2. Recursive Character Splitting

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " ", ""]
)
chunks = splitter.split_documents(docs)
```

**Best for**: General-purpose text, maintains paragraph integrity
**Hierarchy**: Tries larger separators first, falls back to smaller

### 3. Semantic Chunking

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
chunks = splitter.split_text(document)
```

**Best for**: When meaning matters more than size
**Trade-off**: Slower, requires embedding calls

### 4. Document-Specific Chunking

#### Markdown
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
chunks = splitter.split_text(markdown_doc)
```

#### Code
```python
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=2000,
    chunk_overlap=200
)
chunks = splitter.split_documents(code_docs)
```

#### HTML
```python
from langchain.text_splitter import HTMLHeaderTextSplitter

splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=[("h1", "h1"), ("h2", "h2"), ("h3", "h3")]
)
chunks = splitter.split_text(html_doc)
```

## Chunk Size Guidelines

| Content Type | Recommended Size | Overlap |
|--------------|------------------|---------|
| Dense technical docs | 500-1000 tokens | 10-20% |
| Conversational/FAQ | 200-500 tokens | 5-10% |
| Legal/contracts | 1000-1500 tokens | 15-20% |
| Code | 1500-2000 tokens | 10-15% |
| Mixed content | 800-1200 tokens | 15% |

## Advanced: Parent-Child Chunking

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Small chunks for retrieval, large chunks for context
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
```

**Why**: Small chunks = precise retrieval, large chunks = better context

## Metadata Enrichment

Always attach metadata to chunks:

```python
for i, chunk in enumerate(chunks):
    chunk.metadata.update({
        "source": doc.metadata["source"],
        "chunk_index": i,
        "total_chunks": len(chunks),
        "doc_type": detect_doc_type(chunk.page_content),
        "has_code": bool(re.search(r'```', chunk.page_content)),
        "timestamp": datetime.now().isoformat()
    })
```

## Evaluation Checklist

- [ ] Chunks don't break mid-sentence
- [ ] Code blocks stay intact
- [ ] Tables aren't split across chunks
- [ ] Headers stay with their content
- [ ] Overlap preserves context continuity
- [ ] Metadata enables filtering

## Best Practices

1. **Start with recursive splitting** - works for 80% of cases
2. **Test retrieval quality** - not just chunk count
3. **Use overlap** - 10-20% prevents context loss at boundaries
4. **Match chunk size to model** - consider embedding model's optimal input
5. **Preserve structure** - use document-aware splitters when possible
