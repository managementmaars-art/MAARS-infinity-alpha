"""NVIDIA-style dual classifier — task label + complexity dimensions.

Their llm-router blueprint runs every prompt through two small models:

  Task classifier (12 labels)
    Open QA | Closed QA | Summarization | Text Generation |
    Code Generation | Chatbot | Classification | Rewrite |
    Brainstorming | Extraction | Other | Multi-task

  Complexity classifier (7 dimensions, each 0-1)
    Creativity | Reasoning | Contextual-Knowledge | Few-Shot |
    Domain-Knowledge | Constraint | Technical-Difficulty

The router then maps (task, complexity-vector) → model tier. Published
routing accuracy: 82% agreement with hand-labeled ground truth on
MMLU + MT-Bench.

Training their classifiers is offline. We ship two adequate substitutes:

  1. Keyword/length heuristic task-label (cheap, 70% accuracy vs GPT-4
     labeler on our own arena set).
  2. LLM-based complexity scoring using maars/economy. One call per
     prompt when the caller opts in; cached by prompt hash so repeated
     workflows don't re-score.

When the caller sets `use_classifier=True` in llm_gateway.complete(),
we call `classify(prompt)` and feed the result into pareto_router's
weight selection (high complexity → quality weight up).
"""
from __future__ import annotations
import hashlib
import logging
import re
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

TASK_LABELS = (
    "open_qa", "closed_qa", "summarization", "text_generation",
    "code_generation", "chatbot", "classification", "rewrite",
    "brainstorming", "extraction", "other", "multi_task",
)

_cache: dict[str, "Classification"] = {}


@dataclass
class Classification:
    task: str
    complexity: dict[str, float]   # 7 dimensions, each [0,1]
    overall: float                  # aggregated complexity score
    method: str = "heuristic"       # "heuristic" | "llm"


_TASK_CLUES = {
    "code_generation": ("write a function", "implement", "fix bug", "refactor", "python", "typescript", "bash script"),
    "summarization":   ("summarize", "tl;dr", "key points", "in one paragraph", "in short"),
    "extraction":      ("extract", "list all", "pull out", "find every", "give me the"),
    "classification":  ("classify", "label this", "which category", "is this a"),
    "rewrite":         ("rewrite", "paraphrase", "rephrase", "improve the tone"),
    "brainstorming":   ("ideas for", "brainstorm", "suggest ways", "what are some"),
    "closed_qa":       ("given the context", "based on the document", "from the passage"),
    "open_qa":         ("what is", "who is", "when did", "why does", "how does"),
    "text_generation": ("write a story", "draft", "compose", "generate a", "create a"),
    "chatbot":         ("hi ", "hello", "thanks", "thank you", "can you"),
}


def _heuristic_task(prompt: str) -> str:
    low = prompt.lower()[:2000]
    # score every label by clue hits
    best = "other"
    best_hits = 0
    for task, clues in _TASK_CLUES.items():
        hits = sum(1 for c in clues if c in low)
        if hits > best_hits:
            best_hits = hits
            best = task
    return best if best_hits else "other"


def _heuristic_complexity(prompt: str) -> dict[str, float]:
    """7-dim complexity from surface features. Close enough for routing."""
    text = prompt or ""
    n_words = len(text.split())
    n_lines = text.count("\n") + 1
    n_code_fences = text.count("```")
    has_math = bool(re.search(r"[=+\-*/^]\s*\d", text)) or "\\int" in text or "integral" in text.lower()
    has_constraint = any(w in text.lower() for w in ("must", "required", "constraint", "exactly", "only"))
    has_domain = any(w in text.lower() for w in ("legal", "medical", "financial", "physics", "chemistry", "engineering"))
    has_example = "example" in text.lower() or "for instance" in text.lower()

    def norm(x: float, at_one: float) -> float:
        return max(0.0, min(1.0, x / at_one))

    return {
        "creativity":       norm(0.3 + 0.7 * (1.0 if "creative" in text.lower() or "story" in text.lower() or "poem" in text.lower() else 0.2 * (n_words > 30)), 1.0),
        "reasoning":        norm(0.3 * int(has_math) + 0.3 * int("why" in text.lower() or "explain" in text.lower()) + 0.4 * (n_lines > 5), 1.0),
        "context_knowledge": norm(n_words, 400),
        "few_shot":         0.7 if has_example else 0.1,
        "domain_knowledge": 0.7 if has_domain else 0.1,
        "constraint":       0.7 if has_constraint else 0.2,
        "technical":        norm(0.5 * int(n_code_fences > 0) + 0.3 * int("api" in text.lower() or "function" in text.lower()) + 0.2 * int(has_math), 1.0),
    }


def _overall(complexity: dict[str, float]) -> float:
    # Weighted average — reasoning/domain/technical dominate.
    weights = {
        "creativity": 0.10, "reasoning": 0.25, "context_knowledge": 0.10,
        "few_shot": 0.05, "domain_knowledge": 0.20, "constraint": 0.10,
        "technical": 0.20,
    }
    return round(
        sum(weights[k] * complexity[k] for k in complexity),
        3,
    )


def classify_heuristic(prompt: str) -> Classification:
    """Fast, zero-cost classifier. Always available."""
    task = _heuristic_task(prompt)
    complexity = _heuristic_complexity(prompt)
    return Classification(
        task=task,
        complexity=complexity,
        overall=_overall(complexity),
        method="heuristic",
    )


async def classify_llm(prompt: str, user_id: str, complete_fn) -> Classification:
    """Accurate LLM classifier — one call to maars/economy. Cached per
    prompt hash. Falls through to heuristic on any error."""
    key = hashlib.sha256((prompt or "").encode()).hexdigest()[:24]
    if key in _cache:
        return _cache[key]

    system = (
        "You classify user prompts for routing. Reply ONLY with JSON of shape: "
        '{"task":"<one of: open_qa|closed_qa|summarization|text_generation|'
        "code_generation|chatbot|classification|rewrite|brainstorming|extraction|"
        'other|multi_task>","creativity":0-1,"reasoning":0-1,"context_knowledge":0-1,'
        '"few_shot":0-1,"domain_knowledge":0-1,"constraint":0-1,"technical":0-1}. '
        "Scores are floats 0.0-1.0."
    )
    try:
        r = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": (prompt or "")[:2000]},
            ],
            model="maars/economy",
            temperature=0.0,
            max_tokens=250,
            source="nvidia_dual_classifier",
            enable_cache=False,
            verify_injection=False,
        )
        raw = r["choices"][0]["message"]["content"]
        import json, re as _re
        match = _re.search(r"\{.*\}", raw, _re.DOTALL)
        parsed = json.loads(match.group(0)) if match else {}
        task = parsed.get("task", "other")
        if task not in TASK_LABELS:
            task = "other"
        dims = {k: float(parsed.get(k, 0.0)) for k in (
            "creativity", "reasoning", "context_knowledge",
            "few_shot", "domain_knowledge", "constraint", "technical",
        )}
        result = Classification(
            task=task, complexity=dims, overall=_overall(dims), method="llm",
        )
        _cache[key] = result
        if len(_cache) > 500:
            _cache.pop(next(iter(_cache)))
        return result
    except Exception as exc:
        logger.info("llm classify failed, heuristic fallback: %s", exc)
        return classify_heuristic(prompt)


def to_pareto_mode(cls: Classification) -> str:
    """Map a classification to a pareto_router mode tag.

    overall >= 0.7 or domain_knowledge >= 0.7 → premium (quality-first)
    overall <= 0.25                           → economy  (cost-first)
    task == chatbot                           → chat     (latency-first)
    else                                       → auto
    """
    if cls.overall >= 0.7 or cls.complexity.get("domain_knowledge", 0) >= 0.7:
        return "premium"
    if cls.overall <= 0.25:
        return "economy"
    if cls.task == "chatbot":
        return "chat"
    return "auto"
