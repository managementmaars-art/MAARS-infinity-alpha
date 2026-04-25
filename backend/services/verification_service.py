"""
Verification service — second-model review of a primary LLM response.

Given a prompt, a primary response, and optional context, invokes a second
(typically cheaper) model to score confidence, flag issues, and — if
`correct=True` and confidence is below threshold — generate a corrected answer.

Delegates to the provider abstraction so verification participates in the same
health-check + fallback path as regular traffic.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from services.providers import get_provider

logger = logging.getLogger(__name__)

DEFAULT_VERIFIER_PROVIDER = "groq"
DEFAULT_VERIFIER_MODEL = "llama-3.3-70b-versatile"

_VERIFY_SYSTEM = """You are an AI response reviewer. Given a user's prompt and an AI's answer, \
return STRICT JSON with this shape:
{
  "confidence": <integer 0-100>,
  "issues": [<string>, ...],
  "verdict": "pass" | "needs_correction" | "fail"
}
Be concise. Prefer `pass` unless there are concrete factual, logical, or safety issues.
"""


@dataclass
class VerificationResult:
    confidence: int
    verdict: str
    issues: list[str] = field(default_factory=list)
    corrected_answer: Optional[str] = None
    raw_review: str = ""
    verifier_model: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence": self.confidence,
            "verdict": self.verdict,
            "issues": self.issues,
            "corrected_answer": self.corrected_answer,
            "verifier_model": self.verifier_model,
        }


def _extract_json(text: str) -> Optional[dict[str, Any]]:
    """Lift the first JSON object out of a model response."""
    if not text:
        return None
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


async def verify(
    *,
    prompt: str,
    response: str,
    context: str = "",
    confidence_threshold: int = 60,
    correct: bool = False,
    provider: str = DEFAULT_VERIFIER_PROVIDER,
    model: str = DEFAULT_VERIFIER_MODEL,
) -> VerificationResult:
    """Score the primary response; optionally ask for a correction if confidence low."""
    p = get_provider(provider)
    if p is None or not p.available:
        logger.warning("verifier provider %s unavailable — returning pass-through", provider)
        return VerificationResult(
            confidence=100, verdict="pass",
            raw_review="verifier unavailable",
            verifier_model=f"{provider}/{model}",
        )

    review_msgs = [
        {"role": "system", "content": _VERIFY_SYSTEM},
        {"role": "user", "content": (
            f"Context:\n{context}\n\n" if context else ""
        ) + f"User prompt:\n{prompt}\n\nAI answer:\n{response}"},
    ]
    try:
        review_resp = await p.execute_chat_completion(model=model, messages=review_msgs)
        review_text = (
            (review_resp.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    except Exception as exc:
        logger.warning("verifier call failed: %s", exc)
        return VerificationResult(
            confidence=100, verdict="pass", issues=[f"verifier_error: {exc}"],
            raw_review="", verifier_model=f"{provider}/{model}",
        )

    parsed = _extract_json(review_text) or {}
    confidence = int(parsed.get("confidence", 80))
    verdict = str(parsed.get("verdict", "pass")).lower()
    issues = [str(i) for i in parsed.get("issues", [])[:10]]

    result = VerificationResult(
        confidence=max(0, min(100, confidence)),
        verdict=verdict if verdict in ("pass", "needs_correction", "fail") else "pass",
        issues=issues,
        raw_review=review_text,
        verifier_model=f"{provider}/{model}",
    )

    # Correction loop — only if requested and review actually flagged concerns.
    if correct and result.confidence < confidence_threshold:
        correct_msgs = [
            {"role": "system", "content":
                "You are refining an AI answer. Produce ONLY the improved answer — "
                "no preamble, no meta-commentary."},
            {"role": "user", "content":
                f"Original prompt:\n{prompt}\n\nPrior answer:\n{response}\n\n"
                f"Reviewer issues:\n- " + "\n- ".join(issues) if issues else
                f"Original prompt:\n{prompt}\n\nPrior answer:\n{response}"},
        ]
        try:
            corrected = await p.execute_chat_completion(model=model, messages=correct_msgs)
            result.corrected_answer = (
                (corrected.get("choices") or [{}])[0]
                .get("message", {})
                .get("content", "")
            )
        except Exception as exc:
            logger.warning("correction call failed: %s", exc)

    return result
