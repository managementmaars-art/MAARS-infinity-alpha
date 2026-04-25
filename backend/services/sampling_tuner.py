"""Per-task sampling defaults — temperature / top_p that actually match
what the task wants.

Every provider SDK ships with temperature=1.0 default, which is wrong
for every task except creative writing. Using the right temperature per
task is a free quality upgrade — no extra calls, no extra cost.

Empirical defaults (aggregated from OpenAI cookbook, Anthropic cookbook,
published prompt-engineering benchmarks):

  code_generation  : temp=0.15, top_p=0.95  — deterministic, low hallucination
  classification   : temp=0.0,  top_p=1.0   — always pick the argmax
  extraction       : temp=0.0,  top_p=1.0   — same
  summarization    : temp=0.2,  top_p=0.9   — mildly diverse, high fidelity
  reasoning_math   : temp=0.0,  top_p=1.0   — CoT is better with greedy decode
  qna_factual      : temp=0.1,  top_p=0.95  — low hallucination
  chat_general     : temp=0.7,  top_p=1.0   — natural conversational variety
  creative_writing : temp=0.9,  top_p=0.95  — high diversity
  brainstorming    : temp=1.0,  top_p=0.95  — maximum divergence
  rewriting        : temp=0.5,  top_p=0.9   — paraphrase without drift

Caller passes the task label; we return (temperature, top_p). If the
caller already set explicit values, we respect them — they win.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SamplingDefaults:
    temperature: float
    top_p: float


_DEFAULTS: dict[str, SamplingDefaults] = {
    "code_generation":  SamplingDefaults(0.15, 0.95),
    "classification":   SamplingDefaults(0.00, 1.00),
    "extraction":       SamplingDefaults(0.00, 1.00),
    "summarization":    SamplingDefaults(0.20, 0.90),
    "reasoning_math":   SamplingDefaults(0.00, 1.00),
    "qna_factual":      SamplingDefaults(0.10, 0.95),
    "chat_general":     SamplingDefaults(0.70, 1.00),
    "creative_writing": SamplingDefaults(0.90, 0.95),
    "brainstorming":    SamplingDefaults(1.00, 0.95),
    "rewriting":        SamplingDefaults(0.50, 0.90),
}


def defaults_for(task: str | None) -> SamplingDefaults:
    if not task:
        return SamplingDefaults(temperature=0.7, top_p=1.0)
    return _DEFAULTS.get(task.lower().strip(), SamplingDefaults(temperature=0.7, top_p=1.0))


def resolve(
    *,
    task: str | None,
    user_temperature: float | None,
    user_top_p: float | None = None,
) -> tuple[float, float]:
    """Return the (temperature, top_p) to actually use.

    If the caller passed an explicit value, respect it. Otherwise fill
    from the per-task default. If task is unknown, conservative generic
    chat defaults are used (temp=0.7, top_p=1.0).
    """
    d = defaults_for(task)
    t = d.temperature if user_temperature is None else user_temperature
    p = d.top_p if user_top_p is None else user_top_p
    return t, p


_INFER_CLUES = (
    ("code_generation", ("write code", "implement", "fix bug", "refactor", "python function", "typescript")),
    ("reasoning_math", ("solve", "calculate", "what is the sum", "compute", "prove")),
    ("classification", ("classify", "label this", "which category", "is this a")),
    ("extraction", ("extract", "list all", "pull out", "find all the")),
    ("summarization", ("summarize", "tl;dr", "in one paragraph", "key points")),
    ("creative_writing", ("write a poem", "story about", "fictional", "in the style of")),
    ("brainstorming", ("ideas for", "brainstorm", "suggest ways", "what are some")),
    ("rewriting", ("rewrite", "paraphrase", "rephrase", "improve the tone")),
    ("qna_factual", ("what is", "who is", "when did", "where is", "why does")),
)


def infer_task(text: str) -> str | None:
    """Cheap keyword inference — only used when the caller didn't tag
    the task. Not accurate; just better than nothing for temperature
    selection."""
    if not text:
        return None
    low = text.lower()[:500]
    for task, clues in _INFER_CLUES:
        if any(c in low for c in clues):
            return task
    return None
