---
name: rag-evaluation
description: |
  Comprehensive RAG evaluation with retrieval metrics, generation quality, and end-to-end testing.
  Use this skill when measuring and improving RAG system performance.
  Activate when: RAG evaluation, RAGAS, retrieval metrics, generation quality, RAG testing, MRR, recall, faithfulness.
---

# RAG Evaluation

**Measure, monitor, and improve RAG system performance with comprehensive metrics.**

## When to Use

- Setting up RAG evaluation pipelines
- Comparing retrieval strategies
- Measuring generation quality
- Building regression tests for RAG
- Debugging poor RAG performance

## Evaluation Framework

```
┌─────────────────────────────────────────────────────────┐
│                  RAG Evaluation                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Retrieval  │  │ Generation  │  │  End-to-End │     │
│  │  Metrics    │  │  Metrics    │  │   Metrics   │     │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤     │
│  │ • MRR       │  │ • Faithful- │  │ • Answer    │     │
│  │ • Recall@k  │  │   ness      │  │   Correct-  │     │
│  │ • Precision │  │ • Relevance │  │   ness      │     │
│  │ • NDCG      │  │ • Coherence │  │ • Latency   │     │
│  │ • Hit Rate  │  │ • Toxicity  │  │ • Cost      │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Retrieval Metrics

### Implementation

```python
import numpy as np
from typing import List, Dict

def mean_reciprocal_rank(results: List[List[str]], relevant: List[List[str]]) -> float:
    """
    Calculate MRR across queries.
    results: List of ranked document IDs per query
    relevant: List of relevant document IDs per query
    """
    mrr_sum = 0.0
    for res, rel in zip(results, relevant):
        rel_set = set(rel)
        for rank, doc_id in enumerate(res, 1):
            if doc_id in rel_set:
                mrr_sum += 1.0 / rank
                break
    return mrr_sum / len(results)

def recall_at_k(results: List[List[str]], relevant: List[List[str]], k: int) -> float:
    """Calculate Recall@k."""
    recall_sum = 0.0
    for res, rel in zip(results, relevant):
        retrieved_k = set(res[:k])
        relevant_set = set(rel)
        if relevant_set:
            recall_sum += len(retrieved_k & relevant_set) / len(relevant_set)
    return recall_sum / len(results)

def precision_at_k(results: List[List[str]], relevant: List[List[str]], k: int) -> float:
    """Calculate Precision@k."""
    precision_sum = 0.0
    for res, rel in zip(results, relevant):
        retrieved_k = set(res[:k])
        relevant_set = set(rel)
        precision_sum += len(retrieved_k & relevant_set) / k
    return precision_sum / len(results)

def ndcg_at_k(results: List[List[str]], relevant: List[List[str]], k: int) -> float:
    """Calculate NDCG@k."""
    def dcg(scores):
        return sum(s / np.log2(i + 2) for i, s in enumerate(scores))

    ndcg_sum = 0.0
    for res, rel in zip(results, relevant):
        rel_set = set(rel)
        gains = [1 if doc in rel_set else 0 for doc in res[:k]]
        ideal_gains = sorted(gains, reverse=True)

        dcg_val = dcg(gains)
        idcg_val = dcg(ideal_gains)

        ndcg_sum += dcg_val / idcg_val if idcg_val > 0 else 0

    return ndcg_sum / len(results)

def hit_rate(results: List[List[str]], relevant: List[List[str]], k: int) -> float:
    """Calculate Hit Rate (any relevant doc in top-k)."""
    hits = 0
    for res, rel in zip(results, relevant):
        if set(res[:k]) & set(rel):
            hits += 1
    return hits / len(results)
```

### Evaluation Runner

```python
class RetrievalEvaluator:
    def __init__(self, retriever, test_dataset: List[Dict]):
        """
        test_dataset: [{"query": str, "relevant_docs": [str]}]
        """
        self.retriever = retriever
        self.dataset = test_dataset

    def evaluate(self, k_values: List[int] = [1, 3, 5, 10]) -> Dict:
        # Run retrieval for all queries
        results = []
        relevant = []

        for item in self.dataset:
            docs = self.retriever.invoke(item["query"])
            doc_ids = [d.metadata["id"] for d in docs]
            results.append(doc_ids)
            relevant.append(item["relevant_docs"])

        # Calculate metrics
        metrics = {"mrr": mean_reciprocal_rank(results, relevant)}

        for k in k_values:
            metrics[f"recall@{k}"] = recall_at_k(results, relevant, k)
            metrics[f"precision@{k}"] = precision_at_k(results, relevant, k)
            metrics[f"ndcg@{k}"] = ndcg_at_k(results, relevant, k)
            metrics[f"hit_rate@{k}"] = hit_rate(results, relevant, k)

        return metrics
```

## Generation Metrics with RAGAS

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from datasets import Dataset

def evaluate_with_ragas(test_data: List[Dict]) -> Dict:
    """
    test_data: [{
        "question": str,
        "answer": str,  # Generated answer
        "contexts": [str],  # Retrieved contexts
        "ground_truth": str  # Expected answer (optional)
    }]
    """
    dataset = Dataset.from_list(test_data)

    metrics = [
        faithfulness,      # Is answer grounded in context?
        answer_relevancy,  # Is answer relevant to question?
        context_precision, # Are retrieved contexts precise?
        context_recall,    # Do contexts cover ground truth?
    ]

    # Add answer_correctness if ground truth available
    if "ground_truth" in test_data[0]:
        metrics.append(answer_correctness)

    result = evaluate(dataset, metrics=metrics)
    return result.to_pandas().mean().to_dict()
```

## Custom LLM-as-Judge Evaluation

```python
from langchain_openai import ChatOpenAI

FAITHFULNESS_PROMPT = """Rate if the answer is faithful to the context (uses only information from context).

Context: {context}
Answer: {answer}

Score 1-5:
1: Completely unfaithful, makes up information
2: Mostly unfaithful, significant hallucinations
3: Partially faithful, some unsupported claims
4: Mostly faithful, minor extrapolations
5: Completely faithful, all claims supported

Return JSON: {{"score": N, "reasoning": "..."}}"""

RELEVANCE_PROMPT = """Rate if the answer is relevant to the question.

Question: {question}
Answer: {answer}

Score 1-5:
1: Completely irrelevant
2: Tangentially related
3: Partially answers the question
4: Mostly answers the question
5: Fully and directly answers the question

Return JSON: {{"score": N, "reasoning": "..."}}"""

class LLMJudge:
    def __init__(self, model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def judge_faithfulness(self, context: str, answer: str) -> Dict:
        prompt = FAITHFULNESS_PROMPT.format(context=context, answer=answer)
        result = self.llm.invoke(prompt).content
        return json.loads(result)

    def judge_relevance(self, question: str, answer: str) -> Dict:
        prompt = RELEVANCE_PROMPT.format(question=question, answer=answer)
        result = self.llm.invoke(prompt).content
        return json.loads(result)

    def evaluate_batch(self, test_data: List[Dict]) -> Dict:
        faithfulness_scores = []
        relevance_scores = []

        for item in test_data:
            context = "\n".join(item["contexts"])

            faith = self.judge_faithfulness(context, item["answer"])
            faithfulness_scores.append(faith["score"])

            rel = self.judge_relevance(item["question"], item["answer"])
            relevance_scores.append(rel["score"])

        return {
            "avg_faithfulness": np.mean(faithfulness_scores),
            "avg_relevance": np.mean(relevance_scores),
            "faithfulness_scores": faithfulness_scores,
            "relevance_scores": relevance_scores
        }
```

## End-to-End RAG Evaluation

```python
import time
from dataclasses import dataclass

@dataclass
class RAGEvalResult:
    query: str
    retrieved_docs: List
    generated_answer: str
    latency_ms: float
    retrieval_metrics: Dict
    generation_metrics: Dict
    cost_usd: float

class RAGEvaluator:
    def __init__(self, rag_pipeline, judge: LLMJudge):
        self.pipeline = rag_pipeline
        self.judge = judge

    def evaluate_single(self, query: str, ground_truth: Dict = None) -> RAGEvalResult:
        # Measure latency
        start = time.time()
        result = self.pipeline.invoke(query)
        latency_ms = (time.time() - start) * 1000

        # Retrieval metrics (if ground truth available)
        retrieval_metrics = {}
        if ground_truth and "relevant_docs" in ground_truth:
            retrieved_ids = [d.metadata["id"] for d in result["documents"]]
            relevant_ids = ground_truth["relevant_docs"]
            retrieval_metrics = {
                "recall@5": len(set(retrieved_ids[:5]) & set(relevant_ids)) / len(relevant_ids),
                "precision@5": len(set(retrieved_ids[:5]) & set(relevant_ids)) / 5
            }

        # Generation metrics
        context = "\n".join([d.page_content for d in result["documents"]])
        generation_metrics = {
            "faithfulness": self.judge.judge_faithfulness(context, result["answer"]),
            "relevance": self.judge.judge_relevance(query, result["answer"])
        }

        return RAGEvalResult(
            query=query,
            retrieved_docs=result["documents"],
            generated_answer=result["answer"],
            latency_ms=latency_ms,
            retrieval_metrics=retrieval_metrics,
            generation_metrics=generation_metrics,
            cost_usd=estimate_cost(result)
        )

    def evaluate_dataset(self, test_dataset: List[Dict]) -> Dict:
        results = []
        for item in test_dataset:
            result = self.evaluate_single(
                item["query"],
                item.get("ground_truth")
            )
            results.append(result)

        # Aggregate metrics
        return {
            "avg_latency_ms": np.mean([r.latency_ms for r in results]),
            "avg_faithfulness": np.mean([r.generation_metrics["faithfulness"]["score"] for r in results]),
            "avg_relevance": np.mean([r.generation_metrics["relevance"]["score"] for r in results]),
            "total_cost_usd": sum([r.cost_usd for r in results]),
            "detailed_results": results
        }
```

## Continuous Evaluation Pipeline

```python
def setup_eval_pipeline(rag_pipeline, test_dataset_path: str):
    """Set up automated evaluation."""

    # Load test dataset
    with open(test_dataset_path) as f:
        test_data = json.load(f)

    evaluator = RAGEvaluator(rag_pipeline, LLMJudge())

    def run_evaluation() -> Dict:
        results = evaluator.evaluate_dataset(test_data)

        # Log to monitoring
        log_metrics({
            "rag_latency_p50": np.percentile([r.latency_ms for r in results["detailed_results"]], 50),
            "rag_latency_p99": np.percentile([r.latency_ms for r in results["detailed_results"]], 99),
            "rag_faithfulness": results["avg_faithfulness"],
            "rag_relevance": results["avg_relevance"]
        })

        # Alert on regression
        if results["avg_faithfulness"] < 3.5:
            alert("RAG faithfulness dropped below threshold!")

        return results

    return run_evaluation
```

## Best Practices

1. **Build golden dataset** - manually curated query-answer pairs
2. **Test edge cases** - ambiguous queries, no-answer scenarios
3. **Track over time** - metrics should improve, not regress
4. **Separate retrieval vs generation** - diagnose issues precisely
5. **Use multiple judges** - LLM judges can disagree
6. **Monitor production** - sample and evaluate live traffic
