---
name: corrective-rag
description: |
  Implement Corrective RAG (CRAG) with retrieval validation, fallback strategies, and self-correction.
  Use this skill when RAG outputs need quality guarantees and automatic error correction.
  Activate when: CRAG, corrective RAG, retrieval validation, fallback search, self-correcting RAG, grounded generation.
---

# Corrective RAG (CRAG)

**Build RAG systems that validate retrieval quality and self-correct when needed.**

## When to Use

- Need high-accuracy, grounded responses
- Want to detect and handle retrieval failures
- Combining internal knowledge with web search fallback
- Building production RAG with quality guarantees

## CRAG Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Query                          │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │   Initial Retrieval │
               └──────────┬──────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │  Relevance Grader   │
               │  (CORRECT/INCORRECT/│
               │     AMBIGUOUS)      │
               └──────────┬──────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    CORRECT          AMBIGUOUS        INCORRECT
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────────┐  ┌──────────┐
   │   Use    │    │ Use + Search │  │   Web    │
   │ As-Is    │    │   Fallback   │  │  Search  │
   └────┬─────┘    └──────┬───────┘  └────┬─────┘
         │                │               │
         └────────────────┼───────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │  Knowledge Refiner  │
               │ (Extract key info)  │
               └──────────┬──────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │   Generate Answer   │
               └─────────────────────┘
```

## Implementation

### 1. Relevance Grader

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class RelevanceGrade(BaseModel):
    """Grade for document relevance."""
    grade: str = Field(description="CORRECT, INCORRECT, or AMBIGUOUS")
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Brief explanation")

GRADER_PROMPT = """You are a relevance grader. Assess if the document is relevant to the question.

Question: {question}
Document: {document}

Grade as:
- CORRECT: Document directly answers or contains information for the question
- AMBIGUOUS: Document is somewhat related but may not fully answer
- INCORRECT: Document is not relevant to the question

Return JSON with grade, confidence (0-1), and brief reasoning."""

def grade_document(question: str, document: str) -> RelevanceGrade:
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    prompt = ChatPromptTemplate.from_template(GRADER_PROMPT)
    chain = prompt | llm.with_structured_output(RelevanceGrade)
    return chain.invoke({"question": question, "document": document})

def grade_all_documents(question: str, documents: list) -> dict:
    """Grade all documents and categorize."""
    results = {"correct": [], "ambiguous": [], "incorrect": []}

    for doc in documents:
        grade = grade_document(question, doc.page_content)
        results[grade.grade.lower()].append({
            "document": doc,
            "confidence": grade.confidence,
            "reasoning": grade.reasoning
        })

    return results
```

### 2. Web Search Fallback

```python
from langchain_community.tools import TavilySearchResults

def web_search_fallback(query: str, num_results: int = 5) -> list:
    """Search web when retrieval fails."""
    search = TavilySearchResults(max_results=num_results)
    results = search.invoke(query)

    # Convert to document format
    docs = []
    for result in results:
        docs.append(Document(
            page_content=result["content"],
            metadata={
                "source": result["url"],
                "title": result.get("title", ""),
                "type": "web_search"
            }
        ))
    return docs
```

### 3. Knowledge Refiner

```python
REFINER_PROMPT = """Extract only the information relevant to answering the question.

Question: {question}

Document:
{document}

Extract the key facts, numbers, and statements that help answer the question.
Remove irrelevant information. If nothing is relevant, return "NO_RELEVANT_INFO".

Extracted information:"""

def refine_knowledge(question: str, documents: list) -> str:
    """Extract relevant info from documents."""
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    refined_parts = []
    for doc in documents:
        prompt = REFINER_PROMPT.format(
            question=question,
            document=doc.page_content
        )
        result = llm.invoke(prompt).content

        if "NO_RELEVANT_INFO" not in result:
            refined_parts.append(result)

    return "\n\n".join(refined_parts)
```

### 4. Full CRAG Pipeline

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class CRAGState(TypedDict):
    question: str
    documents: List
    graded_docs: dict
    refined_knowledge: str
    web_results: List
    final_answer: str
    retrieval_quality: str

def retrieve(state: CRAGState) -> CRAGState:
    """Initial retrieval."""
    docs = retriever.invoke(state["question"])
    return {"documents": docs}

def grade_documents(state: CRAGState) -> CRAGState:
    """Grade retrieved documents."""
    graded = grade_all_documents(state["question"], state["documents"])

    # Determine overall quality
    if len(graded["correct"]) >= 2:
        quality = "CORRECT"
    elif len(graded["correct"]) + len(graded["ambiguous"]) >= 2:
        quality = "AMBIGUOUS"
    else:
        quality = "INCORRECT"

    return {"graded_docs": graded, "retrieval_quality": quality}

def route_by_quality(state: CRAGState) -> str:
    """Route based on retrieval quality."""
    return state["retrieval_quality"].lower()

def use_retrieved(state: CRAGState) -> CRAGState:
    """Use correctly retrieved docs."""
    correct_docs = [d["document"] for d in state["graded_docs"]["correct"]]
    refined = refine_knowledge(state["question"], correct_docs)
    return {"refined_knowledge": refined}

def search_and_combine(state: CRAGState) -> CRAGState:
    """Use retrieved + web search."""
    # Use what we have
    usable_docs = (
        [d["document"] for d in state["graded_docs"]["correct"]] +
        [d["document"] for d in state["graded_docs"]["ambiguous"]]
    )

    # Add web search
    web_docs = web_search_fallback(state["question"])

    all_docs = usable_docs + web_docs
    refined = refine_knowledge(state["question"], all_docs)
    return {"refined_knowledge": refined, "web_results": web_docs}

def web_search_only(state: CRAGState) -> CRAGState:
    """Fallback to web search."""
    web_docs = web_search_fallback(state["question"])
    refined = refine_knowledge(state["question"], web_docs)
    return {"refined_knowledge": refined, "web_results": web_docs}

def generate_answer(state: CRAGState) -> CRAGState:
    """Generate final answer from refined knowledge."""
    llm = ChatOpenAI(model="gpt-4")

    prompt = f"""Answer the question based only on the provided knowledge.
    If the knowledge is insufficient, say so.

    Question: {state['question']}

    Knowledge:
    {state['refined_knowledge']}

    Answer:"""

    answer = llm.invoke(prompt).content
    return {"final_answer": answer}

# Build the graph
workflow = StateGraph(CRAGState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("grade", grade_documents)
workflow.add_node("use_retrieved", use_retrieved)
workflow.add_node("search_and_combine", search_and_combine)
workflow.add_node("web_search", web_search_only)
workflow.add_node("generate", generate_answer)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")

workflow.add_conditional_edges(
    "grade",
    route_by_quality,
    {
        "correct": "use_retrieved",
        "ambiguous": "search_and_combine",
        "incorrect": "web_search"
    }
)

workflow.add_edge("use_retrieved", "generate")
workflow.add_edge("search_and_combine", "generate")
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

crag = workflow.compile()

# Run
result = crag.invoke({"question": "What is the latest LangChain version?"})
```

## Evaluation Metrics

```python
def evaluate_crag(test_cases: list, crag_pipeline) -> dict:
    """Evaluate CRAG performance."""
    metrics = {
        "correct_retrievals": 0,
        "fallback_triggered": 0,
        "answer_quality": [],
        "grounding_score": []
    }

    for case in test_cases:
        result = crag_pipeline.invoke({"question": case["question"]})

        # Track retrieval quality
        if result["retrieval_quality"] == "CORRECT":
            metrics["correct_retrievals"] += 1
        else:
            metrics["fallback_triggered"] += 1

        # Grade answer quality
        quality = grade_answer(
            case["question"],
            result["final_answer"],
            case.get("expected_answer")
        )
        metrics["answer_quality"].append(quality)

        # Check grounding
        grounding = check_grounding(
            result["final_answer"],
            result["refined_knowledge"]
        )
        metrics["grounding_score"].append(grounding)

    return {
        "retrieval_success_rate": metrics["correct_retrievals"] / len(test_cases),
        "fallback_rate": metrics["fallback_triggered"] / len(test_cases),
        "avg_answer_quality": sum(metrics["answer_quality"]) / len(test_cases),
        "avg_grounding": sum(metrics["grounding_score"]) / len(test_cases)
    }
```

## Best Practices

1. **Calibrate grader thresholds** - test on labeled data
2. **Log all decisions** - track when/why fallback triggers
3. **Rate limit web search** - prevent abuse and cost overruns
4. **Cache web results** - same queries shouldn't re-search
5. **Monitor grading accuracy** - grader can also make mistakes
6. **Set confidence thresholds** - don't use ambiguous docs below 0.5
