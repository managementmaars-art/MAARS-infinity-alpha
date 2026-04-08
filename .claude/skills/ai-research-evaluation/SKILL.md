---
name: ai-research-evaluation
description: "lm-evaluation-harness, BigCode Eval, MMLU/HumanEval benchmarks, custom evals, LLM-as-judge"
---

# AI Research: Model Evaluation

Comprehensive LLM evaluation: running standard benchmarks with lm-evaluation-harness and BigCode Eval, building custom evaluation pipelines, and implementing LLM-as-judge systems.

## lm-evaluation-harness

The standard framework for evaluating language models on academic benchmarks:

```bash
# Install
pip install lm-eval

# Evaluate a HuggingFace model on MMLU and HellaSwag
lm_eval \
  --model hf \
  --model_args "pretrained=meta-llama/Llama-3-8B,dtype=bfloat16" \
  --tasks mmlu,hellaswag,arc_challenge,winogrande,truthfulqa_mc1 \
  --num_fewshot 5 \
  --batch_size 16 \
  --output_path results/llama3-8b/ \
  --log_samples \
  --device cuda:0

# Evaluate an OpenAI-compatible API endpoint
lm_eval \
  --model openai-completions \
  --model_args "model=my-finetuned-model,base_url=http://localhost:8000/v1" \
  --tasks mmlu \
  --num_fewshot 5 \
  --batch_size 1

# Evaluate VLLM-served model (fast)
lm_eval \
  --model vllm \
  --model_args "pretrained=meta-llama/Llama-3-70B,dtype=bfloat16,tensor_parallel_size=4" \
  --tasks mmlu,gsm8k,humaneval \
  --num_fewshot 0 \
  --batch_size auto \
  --output_path results/
```

```python
# Programmatic evaluation with lm-eval
import lm_eval
from lm_eval import evaluator, utils
from lm_eval.models.huggingface import HFLM

model = HFLM(
    pretrained="meta-llama/Llama-3-8B-Instruct",
    dtype="bfloat16",
    batch_size=16,
    device="cuda",
)

results = evaluator.simple_evaluate(
    model=model,
    tasks=["mmlu", "gsm8k", "arc_challenge"],
    num_fewshot=5,
    limit=None,                # None = full eval; int = subset for quick checks
    bootstrap_iters=10000,
    log_samples=True,
)

# Extract key metrics
for task, metrics in results["results"].items():
    print(f"{task}: acc={metrics.get('acc,none', 'N/A'):.4f} "
          f"±{metrics.get('acc_stderr,none', 0):.4f}")
```

## Custom Task for lm-evaluation-harness

```python
# custom_task.py — Add a custom benchmark
from lm_eval.api.task import ConfigurableTask
from lm_eval.api.instance import Instance
from lm_eval.api.metrics import mean

class MyCustomTask(ConfigurableTask):
    VERSION = 1
    DATASET_PATH = "my-org/my-eval-dataset"
    DATASET_NAME = None

    def has_training_docs(self): return False
    def has_validation_docs(self): return True
    def has_test_docs(self): return True

    def validation_docs(self):
        return self.dataset["validation"]

    def test_docs(self):
        return self.dataset["test"]

    def doc_to_text(self, doc) -> str:
        return f"Question: {doc['question']}\nAnswer:"

    def doc_to_target(self, doc) -> str:
        return f" {doc['answer']}"

    def construct_requests(self, doc, ctx, **kwargs):
        return [Instance(
            request_type="generate_until",
            doc=doc,
            arguments=(ctx, {"until": ["\n", "Question:"], "max_gen_toks": 256}),
            idx=0,
        )]

    def process_results(self, doc, results) -> dict:
        prediction = results[0].strip()
        gold = doc["answer"].strip()
        exact_match = prediction.lower() == gold.lower()
        f1 = self._token_f1(prediction, gold)
        return {"exact_match": exact_match, "f1": f1}

    def aggregation(self) -> dict:
        return {"exact_match": mean, "f1": mean}

    def higher_is_better(self) -> dict:
        return {"exact_match": True, "f1": True}

    def _token_f1(self, pred: str, gold: str) -> float:
        pred_tokens = set(pred.lower().split())
        gold_tokens = set(gold.lower().split())
        if not gold_tokens: return 0.0
        common = pred_tokens & gold_tokens
        if not common: return 0.0
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(gold_tokens)
        return 2 * precision * recall / (precision + recall)
```

## BigCode Evaluation (HumanEval / MBPP)

```bash
# BigCode Evaluation Harness for code models
pip install bigcode-evaluation-harness

# HumanEval (164 Python programming problems)
accelerate launch main.py \
  --model meta-llama/CodeLlama-34B-Python \
  --max_length_generation 512 \
  --tasks humaneval \
  --n_samples 20 \
  --temperature 0.8 \
  --batch_size 10 \
  --allow_code_execution \
  --save_generations \
  --save_generations_path results/humaneval_generations.json \
  --metric_output_path results/humaneval_metrics.json

# MBPP (Mostly Basic Python Problems)
accelerate launch main.py \
  --model meta-llama/CodeLlama-34B-Python \
  --tasks mbpp \
  --n_samples 15 \
  --temperature 0.8 \
  --allow_code_execution

# EvalPlus (HumanEval+ — harder test cases)
pip install evalplus
evalplus.evaluate \
  --model meta-llama/CodeLlama-34B-Python \
  --dataset humaneval \
  --backend vllm \
  --greedy
```

## LLM-as-Judge

```python
import openai
import json
from dataclasses import dataclass
from enum import Enum

class Verdict(Enum):
    A_BETTER = "A"
    B_BETTER = "B"
    TIE = "TIE"
    BOTH_BAD = "BOTH_BAD"

@dataclass
class JudgeResult:
    verdict: Verdict
    score_a: float      # 1-10
    score_b: float      # 1-10
    reasoning: str

JUDGE_PROMPT = """You are an expert evaluator assessing the quality of AI-generated responses.

## Evaluation Criteria
- **Accuracy**: Is the information correct and factually accurate?
- **Completeness**: Does the response fully address the question?
- **Clarity**: Is the response well-organized and easy to understand?
- **Helpfulness**: Is the response practically useful?

## Task
Question: {question}

Response A:
{response_a}

Response B:
{response_b}

## Instructions
Evaluate both responses on each criterion (1-10). Then give your verdict.

Respond in JSON:
{{
  "accuracy_a": <int>, "accuracy_b": <int>,
  "completeness_a": <int>, "completeness_b": <int>,
  "clarity_a": <int>, "clarity_b": <int>,
  "helpfulness_a": <int>, "helpfulness_b": <int>,
  "reasoning": "<2-3 sentence explanation>",
  "verdict": "<A|B|TIE|BOTH_BAD>"
}}"""

def judge_pair(
    question: str,
    response_a: str,
    response_b: str,
    judge_model: str = "gpt-4o",
) -> JudgeResult:
    """Compare two responses using LLM-as-judge."""
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=judge_model,
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=question, response_a=response_a, response_b=response_b
            )
        }],
        temperature=0.0,  # deterministic judging
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)
    score_a = (data["accuracy_a"] + data["completeness_a"] +
               data["clarity_a"] + data["helpfulness_a"]) / 4
    score_b = (data["accuracy_b"] + data["completeness_b"] +
               data["clarity_b"] + data["helpfulness_b"]) / 4

    return JudgeResult(
        verdict=Verdict(data["verdict"]),
        score_a=score_a,
        score_b=score_b,
        reasoning=data["reasoning"],
    )

def run_tournament_eval(
    test_cases: list[dict],
    model_a: callable,
    model_b: callable,
    judge_model: str = "gpt-4o",
    swap_and_average: bool = True,  # reduces position bias
) -> dict:
    """Run tournament-style evaluation between two models."""
    results = []
    for case in test_cases:
        question = case["question"]
        resp_a = model_a(question)
        resp_b = model_b(question)

        result = judge_pair(question, resp_a, resp_b, judge_model)
        results.append({"original": result})

        if swap_and_average:
            # Swap order to detect position bias
            swapped = judge_pair(question, resp_b, resp_a, judge_model)
            results[-1]["swapped"] = swapped

    wins_a = sum(1 for r in results if r["original"].verdict == Verdict.A_BETTER)
    wins_b = sum(1 for r in results if r["original"].verdict == Verdict.B_BETTER)
    ties = sum(1 for r in results if r["original"].verdict == Verdict.TIE)
    avg_score_a = sum(r["original"].score_a for r in results) / len(results)
    avg_score_b = sum(r["original"].score_b for r in results) / len(results)

    return {
        "wins_a": wins_a, "wins_b": wins_b, "ties": ties,
        "win_rate_a": wins_a / len(results),
        "avg_score_a": round(avg_score_a, 2),
        "avg_score_b": round(avg_score_b, 2),
        "n_samples": len(results),
    }
```

## MMLU Evaluation Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_mmlu_results(results_path: str) -> pd.DataFrame:
    """Analyze MMLU results by subject and category."""
    import json
    with open(results_path) as f:
        results = json.load(f)

    MMLU_CATEGORIES = {
        "STEM": ["abstract_algebra", "college_chemistry", "computer_security",
                 "high_school_mathematics", "machine_learning"],
        "Humanities": ["high_school_history", "philosophy", "world_religions"],
        "Social Sciences": ["econometrics", "high_school_psychology", "sociology"],
        "Other": ["clinical_knowledge", "medical_genetics", "professional_law"],
    }

    rows = []
    for task, metrics in results["results"].items():
        if not task.startswith("mmlu_"): continue
        subject = task.replace("mmlu_", "").replace("_", " ")
        category = next(
            (cat for cat, subjects in MMLU_CATEGORIES.items()
             if task.replace("mmlu_", "") in subjects),
            "Other"
        )
        rows.append({
            "task": task, "subject": subject, "category": category,
            "accuracy": metrics.get("acc,none", 0),
            "stderr": metrics.get("acc_stderr,none", 0),
            "n_shots": metrics.get("num_fewshot", 0),
        })

    df = pd.DataFrame(rows)

    # Category averages
    category_avg = df.groupby("category")["accuracy"].agg(["mean", "std"])
    print("\nMMLU Results by Category:")
    print(category_avg.round(4).to_string())
    print(f"\nOverall MMLU: {df['accuracy'].mean():.4f}")

    return df
```

## Evaluation Best Practices

```python
# Avoid contamination: check test set overlap with training data
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_contamination(
    test_questions: list[str],
    training_texts: list[str],
    threshold: float = 0.8
) -> list[tuple[int, float]]:
    """Find test questions potentially contaminated in training data."""
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))
    all_texts = test_questions + training_texts
    tfidf = vectorizer.fit_transform(all_texts)

    test_vecs = tfidf[:len(test_questions)]
    train_vecs = tfidf[len(test_questions):]

    contaminated = []
    for i, test_vec in enumerate(test_vecs):
        sims = cosine_similarity(test_vec, train_vecs)[0]
        max_sim = sims.max()
        if max_sim > threshold:
            contaminated.append((i, float(max_sim)))

    return contaminated

# Statistical significance testing
from scipy import stats

def compare_models_significance(
    model_a_scores: list[float],
    model_b_scores: list[float],
    alpha: float = 0.05
) -> dict:
    """McNemar's test for paired binary outcomes (e.g., correct/incorrect)."""
    # For accuracy differences
    t_stat, p_value = stats.ttest_rel(model_a_scores, model_b_scores)
    mean_diff = np.mean(model_a_scores) - np.mean(model_b_scores)
    ci = stats.t.interval(1 - alpha, len(model_a_scores) - 1,
                          loc=mean_diff, scale=stats.sem(
                              np.array(model_a_scores) - np.array(model_b_scores)))

    return {
        "mean_a": np.mean(model_a_scores),
        "mean_b": np.mean(model_b_scores),
        "mean_diff": mean_diff,
        "p_value": p_value,
        "significant": p_value < alpha,
        "ci_95": ci,
    }
```

## Best Practices

- Always report confidence intervals and sample size — a 1% accuracy difference is meaningless without statistical testing
- Use 5-shot prompting for MMLU (standard); 0-shot for HumanEval; match published settings for comparability
- Check for test-set contamination in your training data before reporting benchmark results
- Run each benchmark with multiple seeds and report mean ± std for generative tasks
- For LLM-as-judge, swap response order in 50% of comparisons to measure and correct for position bias
- Use `limit=100` for quick iteration during development; full eval only before reporting
- Store all raw model outputs — you'll want to re-analyze them with different metrics later
- Calibration matters as much as accuracy — overconfident wrong answers are worse than uncertain ones
- Build domain-specific evals for your use case — academic benchmarks don't always correlate with production quality
- Use identical system prompts and temperature=0 for reproducible evaluation

## Models to Use

- **Default**: `claude-sonnet-4-5` — custom eval tasks, judge prompts, analysis scripts
- **Eval design**: `claude-opus-4-5` — benchmark methodology, multi-criteria rubrics, contamination analysis
- **Quick scripts**: `claude-haiku-3-5` — metric calculations, result parsing, plot generation
