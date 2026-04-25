"""Chain-of-Verification (CoVe) — cut hallucinations with a cheap 2nd pass.

Meta AI's 2023 paper: after a model produces an answer, generate a small
set of verification questions, answer those, then have the model
regenerate the final answer conditioned on its own verification. Ran
on Wikidata + multi-span QA: hallucinated facts dropped 30-50%.

We use the 'joint' variant (single call, not multiple) to keep cost down:
one extra round-trip instead of four. Roughly 2× latency / 2× cost for
~35% fewer factual errors. Invoked opt-in via `verify=True` in
llm_gateway.complete(). Default OFF (cost matters); we'll flip it on
for agent-tool calls where hallucination is most expensive.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

_COVE_PROMPT = """You just produced this answer:

---
{answer}
---

Now verify it in two steps. Be terse.

1) List the 1-3 specific factual claims the answer depends on.
2) For each claim, state whether you are CONFIDENT, UNCERTAIN, or LIKELY_WRONG.
3) Produce a FINAL REVISED ANSWER that removes any LIKELY_WRONG claims
   and hedges any UNCERTAIN ones. If the original was fully confident
   and correct, return it unchanged.

Return only the FINAL REVISED ANSWER. No preamble, no verification trace.
"""


async def verify(
    *,
    original_answer: str,
    complete_fn,
    user_id: str,
    model: str = "maars/economy",
    source: str = "cov_verify",
) -> str:
    """Run the verification pass and return the (possibly revised) answer.

    complete_fn : the llm_gateway.complete function (passed in to avoid
                  a circular import since llm_gateway imports this module).
    model       : default to maars/economy — verification doesn't need
                  the flagship tier to work.
    """
    if not original_answer or len(original_answer) < 20:
        return original_answer
    try:
        response = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": "You verify your own answers for factual reliability."},
                {"role": "user", "content": _COVE_PROMPT.format(answer=original_answer)},
            ],
            model=model,
            temperature=0.0,
            max_tokens=min(2048, max(256, len(original_answer) // 2)),
            source=source,
        )
        revised = response["choices"][0]["message"]["content"]
        return revised.strip() if revised else original_answer
    except Exception as exc:
        logger.info("cov_verifier fell through to original: %s", exc)
        return original_answer
