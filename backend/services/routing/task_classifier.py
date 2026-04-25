"""Task-complexity classifier — decides whether a prompt is trivial,
medium, or hard BEFORE routing so the smart router can pick an
appropriately-sized model.

Why this matters for cost + quality:

  trivial → Groq Llama-8B / Gemini-Flash is fine. Free. Fast. Cheap.
  medium  → GPT-4o-mini / Llama-70B. Still free or low-cost on most
            aggregators. Capable enough for most business chat.
  hard    → Opus / GPT-5.2 / o4. Paid. The customer came to us for this.

Without this classifier, the router picks purely by cost/quality
Pareto — which means trivial questions sometimes end up on Opus
(wasted $) and hard questions sometimes on Gemini-Flash (customer
gets a bad answer and churns).

Heuristic-only today — no LLM call, no tokenization. Runs in <1ms so
it stays on the synchronous hot path.
"""
from __future__ import annotations
import re

# Regex-based signals. Tuned against real chat workloads — precision
# over recall (better to misclassify HARD as MEDIUM than the reverse,
# because MEDIUM users tolerate stronger models without complaining).

_HARD_SIGNALS = re.compile(
    r"\b(analyze|analyse|compare|contrast|explain|derive|prove|"
    r"step.?by.?step|think.?step.?by.?step|reason|reasoning|"
    r"comprehensive|detailed|thoroughly|critically|evaluate|"
    r"research|investigate|debug|refactor|architect|design\s+a|"
    r"implement\s+a|multi.?step|complex|nuanced|subtle|"
    r"legal|contract|compliance|medical|clinical|financial\s+model|"
    r"optimi[sz]ation|algorithmic|proof|theorem|"
    r"end.to.end|full\s+(system|stack|implementation)|"
    r"write\s+an?\s+(essay|article|blog\s+post|report|paper)|"
    r"long.form|3000.?\+?\s*words|5000.?\+?\s*words)\b",
    re.I,
)

_TRIVIAL_SIGNALS = re.compile(
    r"^(hi|hey|hello|yo|sup|yep|nope|ok|okay|ty|thanks|"
    r"thank\s*you|cool|nice|got\s*it|sure|fine|yes|no|"
    r"right|exactly|agreed|true|false|good|great)[\s\.\!\?]*$",
    re.I,
)

_CODE_SIGNALS = re.compile(
    r"\b(write\s+(a\s+)?(function|class|script|program|code|module)|"
    r"implement|fix\s+(this|the)\s+(bug|error)|refactor|"
    r"optimize\s+(this|the)\s+code|code\s+review|"
    r"stack\s+trace|compile\s+error|runtime\s+error|"
    r"```|def\s+\w+\(|function\s+\w+\(|class\s+\w+|import\s+\w+)\b",
    re.I,
)

_REASONING_SIGNALS = re.compile(
    r"\b(math|equation|calculate|compute|solve|proof|"
    r"logic|logical|deduce|infer|syllogism|"
    r"probability|statistics|theorem|lemma)\b",
    re.I,
)


def _token_count_rough(text: str) -> int:
    """~1 token per 4 chars. Good enough for gatekeeping."""
    return max(1, len(text) // 4)


def classify(prompt: str, *, messages: list[dict] | None = None) -> dict:
    """Classify a prompt into trivial / medium / hard with signals.

    Inputs:
      prompt   — the user-visible text of the latest user turn
      messages — optional full conversation (for turn-count heuristic)

    Output:
      {
        "complexity": "trivial" | "medium" | "hard",
        "signals":    list of human-readable triggers,
        "task_type":  "chat" | "code" | "reasoning" | "creative" | "unknown",
        "token_estimate": int (rough token count of the prompt),
        "suggested_max_tokens": int (response cap appropriate for complexity),
      }
    """
    if not prompt or not prompt.strip():
        return {
            "complexity": "trivial", "signals": ["empty"],
            "task_type": "chat", "token_estimate": 0,
            "suggested_max_tokens": 20,
        }
    text = prompt.strip()
    tokens = _token_count_rough(text)
    signals: list[str] = []
    task_type = "chat"

    # Turn count — long conversations skew harder on average.
    turns = len(messages or [])

    # HARD: explicit long-form, analysis, reasoning, multi-step, legal/med/fin
    if _HARD_SIGNALS.search(text):
        signals.append("hard_keywords")
    if tokens > 600:
        signals.append("long_prompt")
    if turns >= 8:
        signals.append("many_turns")

    # CODE: programming signals
    if _CODE_SIGNALS.search(text):
        signals.append("code_markers")
        task_type = "code"

    # REASONING: math/logic
    if _REASONING_SIGNALS.search(text):
        signals.append("reasoning_markers")
        if task_type == "chat":
            task_type = "reasoning"

    # TRIVIAL: short greetings / acks
    if _TRIVIAL_SIGNALS.match(text) or (tokens <= 3 and "?" not in text):
        signals.append("trivial_utterance")
        return {
            "complexity": "trivial", "signals": signals,
            "task_type": "chat", "token_estimate": tokens,
            "suggested_max_tokens": 60,
        }

    # Decide complexity by signal weight
    hard_score = sum(1 for s in signals
                     if s in ("hard_keywords", "long_prompt", "many_turns",
                              "code_markers", "reasoning_markers"))
    if hard_score >= 2 or "long_prompt" in signals:
        return {
            "complexity": "hard", "signals": signals,
            "task_type": task_type, "token_estimate": tokens,
            "suggested_max_tokens": 2000,
        }
    if hard_score == 1 or tokens > 150:
        return {
            "complexity": "medium", "signals": signals,
            "task_type": task_type, "token_estimate": tokens,
            "suggested_max_tokens": 800,
        }
    # Short-to-medium chat without hard signals → trivial/simple
    return {
        "complexity": "trivial" if tokens <= 30 else "medium",
        "signals": signals or ["no_hard_signals"],
        "task_type": task_type,
        "token_estimate": tokens,
        "suggested_max_tokens": 120 if tokens <= 30 else 500,
    }


# ── Complexity → allowed-quality-floor shift ─────────────────────────
# Even within a tier, trivial questions can drop one quality step.
# This is what lets the router send Groq to a $5k premium customer
# when they ask "hi" — no one expects Opus for that.

def floor_adjustment_for_complexity(complexity: str) -> float:
    """How much to LOWER the tier's min-quality floor based on task
    complexity. Trivial questions don't need premium quality even for
    premium users. Hard questions tighten the floor (never give a
    premium user a budget model for a reasoning problem)."""
    return {
        "trivial": -0.15,
        "medium":   0.0,
        "hard":    +0.05,
    }.get(complexity, 0.0)
