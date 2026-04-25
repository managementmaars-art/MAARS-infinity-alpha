// Centralized pricing math — mirrors backend/services/pricing_math.py.
// All UI call sites (PricingManagerTab, ProviderIntelligencePage,
// AdminPackagesPage) should use these helpers so formulas stay in lockstep
// with the backend. If you change a formula or default here, update the
// Python module too (they're both consumed by the same admin flows).

// MUST match backend DEFAULT_ENGINE_CONFIG. Drift between frontend/backend
// defaults was the source of the TOKENS_PER_CREDIT=500-vs-1000 bug.
//
// UNIFIED MODEL — 2026-04-24 · 1 credit = 100,000 tokens · matches
// backend/services/billing/token_quota.py and pricing_math.py
// Media credits_per_action recalibrated vs. measured provider costs.
export const DEFAULT_ENGINE_CONFIG = {
  tokens_per_credit:         100000,   // aligned with token_quota hard cap
  // Per-action rates for chat + code — operator-editable. 0.015 ≈ 1500
  // tokens per chat × 100k tok/cr; 0.04 ≈ 4000 tokens per code run.
  // Set 0 to make that category free on the given plan.
  chat_credits_per_msg:      0.015,
  code_credits_per_run:      0.04,
  image_std_credits:         0,        // Pollinations free (router-first)
  image_hd_credits:          6,        // Flux-dev paid fallback
  video_credits_per_sec:     1,        // Fal LTX $0.005/sec
  tts_credits_per_min:       0,        // Edge TTS free
  voiceover_credits_per_min: 3,        // ElevenLabs Turbo paid fallback
  stt_credits_per_min:       0,        // Groq Whisper free
};

export const DEFAULT_AI_COST_PER_CREDIT = 0.00003;
export const DEFAULT_MARGIN_PCT         = 200;
export const DEFAULT_BDT_RATE           = 107;

const round4 = (n) => Math.round(n * 10000) / 10000;
const round2 = (n) => Math.round(n * 100) / 100;

// ── Pure formula primitives ─────────────────────────────────────────────

export const aiCostUsd = (credits, costPerCredit) =>
  round4((credits || 0) * (costPerCredit || 0));

export const profitUsd = (priceUsd, aiCost) =>
  round2((priceUsd || 0) - (aiCost || 0));

export const marginPct = (profit, aiCost) => {
  if (!aiCost || aiCost <= 0) return 999999;
  return Math.round((profit / aiCost) * 1000) / 10;
};

export const operatorSharePct = (profit, priceUsd) => {
  if (!priceUsd || priceUsd <= 0) return 0;
  return Math.round((profit / priceUsd) * 10000) / 100;
};

export const suggestedPrice = (aiCost, marginTargetPct) =>
  round2((aiCost || 0) * (1 + (marginTargetPct || 0) / 100));

export const usdToBdt = (usd, rate) =>
  Math.round((usd || 0) * (rate || DEFAULT_BDT_RATE));

export const creditsToTokens = (credits, engineConfig) => {
  const tpc = (engineConfig && engineConfig.tokens_per_credit)
    || DEFAULT_ENGINE_CONFIG.tokens_per_credit;
  return Math.floor((credits || 0) * tpc);
};

export const mediaCapacity = (credits, engineConfig) => {
  const ec = { ...DEFAULT_ENGINE_CONFIG, ...(engineConfig || {}) };
  const vsec = ec.video_credits_per_sec || 1;
  const videoClips4s = Math.floor((credits || 0) / (vsec * 4));
  return {
    images_standard:   Math.floor((credits || 0) / (ec.image_std_credits || 1)),
    images_hd:         Math.floor((credits || 0) / (ec.image_hd_credits || 1)),
    video_seconds:     Math.round(((credits || 0) / vsec) * 10) / 10,
    video_clips_4sec:  videoClips4s,
    video_incapable:   videoClips4s < 1,
    tts_minutes:       Math.floor((credits || 0) / (ec.tts_credits_per_min || 1)),
    voiceover_minutes: Math.floor((credits || 0) / (ec.voiceover_credits_per_min || 1)),
    stt_minutes:       Math.floor((credits || 0) / (ec.stt_credits_per_min || 1)),
  };
};

export const planEconomics = ({
  credits, priceUsd, costPerCredit,
  marginTargetPct = DEFAULT_MARGIN_PCT,
  bdtRate = DEFAULT_BDT_RATE,
}) => {
  const cost = aiCostUsd(credits, costPerCredit);
  const profit = profitUsd(priceUsd, cost);
  return {
    credits,
    priceUsd,
    aiCost:             cost,
    profit,
    marginPct:          marginPct(profit, cost),
    operatorSharePct:   operatorSharePct(profit, priceUsd),
    suggestedPrice:     priceUsd > 0 ? suggestedPrice(cost, marginTargetPct) : 0,
    priceBdt:           usdToBdt(priceUsd, bdtRate),
    monthlyCapUsd:      cost,
    profitable:         profit > 0,
  };
};

// Stamps computed BDT + monthly_cap onto a plan dict. Mirrors backend
// pricing_math.stamp_plan so a round-trip through PUT /admin/pricing
// produces identical derived fields.
export const stampPlan = (plan, bdtRate, costPerCredit) => ({
  ...plan,
  price_bdt:       usdToBdt(plan.price_usd || 0, bdtRate),
  monthly_cap_usd: aiCostUsd(plan.credits || 0, costPerCredit),
});

export const stampPlans = (plans, bdtRate, costPerCredit) =>
  Object.fromEntries(
    Object.entries(plans || {}).map(([id, p]) => [id, stampPlan(p, bdtRate, costPerCredit)])
  );
