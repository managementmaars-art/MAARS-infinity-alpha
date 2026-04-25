"""Prompt-enhancement layer — turns "just get it done" prompts into
production-quality creative briefs.

Before this module existed, a user prompt like "make me a logo for a
coffee shop" went directly to gpt-image-1 / Sora — producing generic
stock output. This module uses a cheap LLM (Gemini Flash, Groq's
llama-3.1-8b, or Cerebras) to rewrite the prompt as a detailed brief
that matches the quality tier requested.

Design:
  * Pure LLM prompt (uses your own Universal Gateway — free providers,
    so enhancement is effectively zero-cost).
  * Per-modality brief structure:
      - Image: subject, style, lighting, composition, color palette,
               detail level, aspect ratio, medium.
      - Video: scene, camera movement, duration pacing, transitions,
               mood/music cues, resolution target.
      - TTS:  voice character, pacing, emotional tone, emphasis markers.
  * Quality tiers: "draft" (skip enhancement for speed), "standard"
    (default — 50% longer brief), "premium" (detailed 200+ word
    creative brief, ready for Sora / MidJourney level prompts).
  * Retains the user's original intent verbatim — we ADD context,
    never change the subject.
  * Falls back to the original prompt if the enhancer LLM itself
    errors, so a bad enhancement never kills a generation.
"""
from __future__ import annotations
import logging
from typing import Literal

logger = logging.getLogger(__name__)

Modality = Literal["image", "video", "tts", "content"]
QualityTier = Literal["draft", "standard", "premium"]


_IMAGE_BRIEF_TEMPLATE = """You are a creative director writing a detailed image-generation brief.

Rewrite the user's request below as a production-quality prompt for an AI image model (gpt-image-1 / DALL-E 3 / Gemini Imagen). Keep the user's intent EXACT — add specificity, not new subject matter.

Include where reasonable:
  - Subject + action (who/what is doing what)
  - Style (photorealistic / illustration / 3D render / editorial / cinematic)
  - Lighting (golden hour / studio softbox / dramatic rim / flat overcast)
  - Composition (rule of thirds / centered / wide establishing / macro)
  - Color palette (warm earth tones / saturated neon / muted monochrome)
  - Detail (hyper-detailed / minimalist / textured / smooth)
  - Medium (35mm film / digital art / oil painting / vector)
  - Aspect ratio / framing hint (square / landscape / portrait)

Output ONLY the rewritten prompt. No preamble, no explanations, no markdown. {length_rule}

USER REQUEST: {prompt}

REWRITTEN PROMPT:"""


_VIDEO_BRIEF_TEMPLATE = """You are a director writing a detailed video-generation brief.

Rewrite the user's request below as a production-quality prompt for an AI video model (Sora / Runway / Pika). Keep the user's intent EXACT — add specificity, not new subject matter.

Include where reasonable:
  - Opening scene / subject + action
  - Camera (static / slow dolly-in / orbital / handheld / drone pullback)
  - Lighting + time of day
  - Pacing across the {duration}s duration (hold, pan, cut)
  - Mood / atmosphere
  - Color grading (teal-orange / desaturated / warm filmic)
  - Ending frame / resolution
  - Style (cinematic / documentary / stylized 3D / anime)

Output ONLY the rewritten prompt. No preamble, no markdown. {length_rule}

USER REQUEST: {prompt}

REWRITTEN PROMPT:"""


_CONTENT_BRIEF_TEMPLATE = """Rewrite the user's request below into a detailed content brief that another AI writer can execute without clarification.

Include where relevant:
  - Target audience + their pain point
  - Tone + voice (witty / authoritative / conversational / technical)
  - Structure (listicle / narrative / Q&A / step-by-step)
  - Length target
  - Call to action
  - Key facts or framing to include

Output ONLY the rewritten brief. No markdown, no preamble. {length_rule}

USER REQUEST: {prompt}

CONTENT BRIEF:"""


_LENGTH_RULES = {
    "standard": "Keep the rewrite to 40-80 words.",
    "premium":  "Write 120-200 words of rich, specific detail.",
}


def _template_for(modality: Modality) -> str:
    if modality == "image": return _IMAGE_BRIEF_TEMPLATE
    if modality == "video": return _VIDEO_BRIEF_TEMPLATE
    if modality == "content": return _CONTENT_BRIEF_TEMPLATE
    # TTS enhancement is different — it shapes SSML, not prompt prose.
    # Keep here as a placeholder; route_tts does its own hinting.
    return _CONTENT_BRIEF_TEMPLATE


async def enhance_prompt(
    prompt: str,
    modality: Modality = "image",
    quality: QualityTier = "standard",
    *,
    duration: int = 4,
    user_id: str | None = None,
) -> tuple[str, dict]:
    """Return (enhanced_prompt, meta). Meta has: ok, enhancer_model,
    original_length, enhanced_length, error.

    Draft tier = passthrough (zero-latency). Standard + Premium run
    through a free-tier LLM on your Universal Gateway.
    """
    meta = {
        "ok": True,
        "tier": quality,
        "modality": modality,
        "original_length": len(prompt),
        "enhanced_length": None,
        "enhancer_model": None,
        "error": None,
    }
    if quality == "draft" or not prompt:
        meta["enhanced_length"] = len(prompt)
        return prompt, meta

    try:
        # Route through the Universal Gateway so enhancement cost flows
        # into gateway_usage_logs like everything else. Use maars/auto +
        # task-complexity "light" so the router picks a free provider.
        from services.llm_gateway import complete
        tpl = _template_for(modality)
        length_rule = _LENGTH_RULES.get(quality, _LENGTH_RULES["standard"])
        sys_prompt = tpl.format(
            prompt=prompt.strip(),
            duration=duration,
            length_rule=length_rule,
        )
        resp = await complete(
            user_id=user_id or "system_prompt_enhancer",
            messages=[{"role": "user", "content": sys_prompt}],
            model="maars/auto",
            source="prompt_enhancer",
            max_tokens=400 if quality == "premium" else 160,
        )
        enhanced = (
            resp.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
        )
        if not enhanced:
            raise ValueError("Empty enhancement")
        # Guard against the enhancer adding "Here's the rewrite:" preambles.
        for junk in ("REWRITTEN PROMPT:", "CONTENT BRIEF:", "Here is", "Here's"):
            if enhanced.startswith(junk):
                enhanced = enhanced[len(junk):].lstrip(": \n")
        meta["enhanced_length"] = len(enhanced)
        meta["enhancer_model"] = resp.get("model")
        return enhanced, meta
    except Exception as exc:
        # If enhancement fails, the caller gets the original prompt back —
        # never break a generation because the enhancer blew up.
        logger.warning("Prompt enhancement failed (%s); using original", exc)
        meta["ok"] = False
        meta["error"] = f"{type(exc).__name__}: {exc}"
        meta["enhanced_length"] = len(prompt)
        return prompt, meta
