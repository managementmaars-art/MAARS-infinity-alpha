---
name: agentic-rag
description: |
  Build autonomous RAG agents that reason, plan, and use tools for complex retrieval tasks.
  Use this skill when simple retrieve-and-generate isn't enough.
  Activate when: agentic RAG, RAG agent, multi-step retrieval, tool-using RAG, autonomous retrieval, query decomposition.
---

# Agentic RAG

**Build RAG systems that reason, plan, and adaptively retrieve information.**

## When to Use

- Questions require multiple retrieval steps
- Need to combine information from different sources
- Query needs decomposition into sub-queries
- Results need validation or refinement
- Complex reasoning over retrieved documents

## Simple RAG vs Agentic RAG

```
Simple RAG:
Query → Retrieve → Generate → Answer

Agentic RAG:
Query → Plan → [Retrieve → Analyze → Decide]*n → Synthesize → Answer
```

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Question                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
                ┌───────────────────┐
                │   Query Analyzer  │
                │   (Decompose?)    │
                └─────────┬─────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Sub-Q 1  │    │ Sub-Q 2  │    │ Sub-Q 3  │
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Retrieve │    │ Retrieve │    │ Retrieve │
   └────┬─────┘    └────┬─────┘    └────┬─────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
              ┌───────────────────┐
              │    Synthesizer    │
              │  (Combine & Cite) │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │   Final Answer    │
              └───────────────────┘
```

## Implementation with LangGraph

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    question: str
    sub_questions: List[str]
    retrieved_docs: Annotated[List, operator.add]
    current_step: int
    final_answer: str

# Nodes
def analyze_query(state: AgentState) -> AgentState:
    """Decompose complex query into sub-questions."""
    llm = ChatOpenAI(model="gpt-4")

    prompt = f"""Analyze this question and break it into sub-questions if needed.
    Question: {state['question']}

    Return a JSON list of sub-questions, or just the original if simple."""

    response = llm.invoke(prompt)
    sub_questions = parse_questions(response.content)

    return {"sub_questions": sub_questions, "current_step": 0}

def retrieve_for_subquery(state: AgentState) -> AgentState:
    """Retrieve documents for current sub-question."""
    current_q = state["sub_questions"][state["current_step"]]
    docs = retriever.invoke(current_q)

    return {
        "retrieved_docs": docs,
        "current_step": state["current_step"] + 1
    }

def should_continue(state: AgentState) -> str:
    """Check if more sub-questions to process."""
    if state["current_step"] < len(state["sub_questions"]):
        return "retrieve"
    return "synthesize"

def synthesize_answer(state: AgentState) -> AgentState:
    """Combine all retrieved info into final answer."""
    llm = ChatOpenAI(model="gpt-4")

    context = "\n\n".join([doc.page_content for doc in state["retrieved_docs"]])

    prompt = f"""Based on the following context, answer the question.
    Cite sources using [1], [2], etc.

    Question: {state['question']}

    Context:
    {context}
    """

    response = llm.invoke(prompt)
    return {"final_answer": response.content}

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("analyze", analyze_query)
workflow.add_node("retrieve", retrieve_for_subquery)
workflow.add_node("synthesize", synthesize_answer)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "retrieve")
workflow.add_conditional_edges("retrieve", should_continue, {
    "retrieve": "retrieve",
    "synthesize": "synthesize"
})
workflow.add_edge("synthesize", END)

agent = workflow.compile()

# Run
result = agent.invoke({"question": "Compare AWS and GCP pricing for ML workloads"})
```

## Self-RAG: Retrieve When Needed

```python
def self_rag_node(state: AgentState) -> AgentState:
    """Decide whether retrieval is needed."""
    llm = ChatOpenAI(model="gpt-4")

    prompt = f"""Given this question, do you need to retrieve external information?
    Question: {state['question']}

    Consider:
    - Is this factual or requires current data? → RETRIEVE
    - Is this reasoning/math/coding? → NO RETRIEVE
    - Do you have high confidence? → NO RETRIEVE

    Answer: RETRIEVE or NO_RETRIEVE"""

    response = llm.invoke(prompt)

    if "RETRIEVE" in response.content and "NO" not in response.content:
        return {"needs_retrieval": True}
    return {"needs_retrieval": False}
```

## Tool-Using RAG Agent

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool

# Define retrieval tools
tools = [
    Tool(
        name="search_docs",
        func=lambda q: retriever.invoke(q),
        description="Search internal documentation"
    ),
    Tool(
        name="search_code",
        func=lambda q: code_retriever.invoke(q),
        description="Search codebase for examples"
    ),
    Tool(
        name="search_tickets",
        func=lambda q: jira_retriever.invoke(q),
        description="Search JIRA tickets and issues"
    ),
    Tool(
        name="calculator",
        func=lambda x: eval(x),
        description="Perform calculations"
    )
]

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Agent decides which tools to use
result = executor.invoke({
    "input": "What's the average response time mentioned in our API docs, and how does it compare to ticket #1234?"
})
```

## Adaptive Retrieval

```python
def adaptive_retrieve(query: str, min_score: float = 0.7) -> list:
    """Retrieve with quality check, expand if needed."""

    # Initial retrieval
    results = retriever.invoke(query)
    scores = [doc.metadata.get("score", 0) for doc in results]

    # Check quality
    if max(scores) < min_score:
        # Try query expansion
        expanded = expand_query(query)
        for eq in expanded:
            more_results = retriever.invoke(eq)
            results.extend(more_results)

        # Deduplicate
        results = deduplicate(results)

    # Rerank
    results = rerank(query, results)

    return results[:5]

def expand_query(query: str) -> list:
    """Generate alternative phrasings."""
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"Generate 3 alternative phrasings for: {query}"
    response = llm.invoke(prompt)
    return parse_alternatives(response.content)
```

## Patterns Summary

| Pattern | When to Use | Complexity |
|---------|------------|------------|
| Query Decomposition | Multi-part questions | Medium |
| Self-RAG | Uncertain if retrieval needed | Low |
| Tool-Using Agent | Multiple data sources | High |
| Adaptive Retrieval | Variable quality needs | Medium |
| Iterative Refinement | Research tasks | High |

## Best Practices

1. **Start simple** - add agency only when needed
2. **Limit iterations** - set max steps to prevent loops
3. **Log decisions** - track when/why agent retrieves
4. **Validate outputs** - agent can hallucinate tool usage
5. **Cost awareness** - more steps = more LLM calls
