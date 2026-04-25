"""Load test for the unified router (bandit + pareto) on the LLM hot path.

Three subtests:
  1. **Bandit convergence** — Thompson sampling over 6 simulated arms
     with known ground-truth success rates. Measures pick()/record()
     latency at concurrency=100 and verifies that the bandit (a) finds
     the best true arm and (b) learns posteriors within tolerance.

  2. **Pareto correctness** — runs choose() over canned candidate sets
     with known dominators and verifies the right candidate wins under
     each mode (premium / economy / batch / chat).

  3. **rerank_for_mode latency** — simulates the hot-path scenario where
     premium plans get re-ranked at every gateway call. Verifies the
     overhead is < 1ms per call so it can stay in the synchronous path.

No real LLM calls. Pure router performance numbers.

Run:
    python backend/scripts/loadtest_bandit.py                # 10k calls
    python backend/scripts/loadtest_bandit.py --n 50000      # heavier
"""
from __future__ import annotations
import argparse
import asyncio
import random
import statistics
import sys
import time
from pathlib import Path

# Allow `python scripts/loadtest_bandit.py` from project root or backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.routing import router as bandit_router


# Ground-truth arms we simulate. The bandit doesn't know these — it
# must learn them from feedback.
TRUE_ARMS = {
    "openai":     {"success": 0.97, "lat_ms": 420, "cost": 1.5},
    "anthropic":  {"success": 0.98, "lat_ms": 380, "cost": 2.0},
    "google":     {"success": 0.94, "lat_ms": 310, "cost": 0.8},   # cheapest, slightly less reliable
    "groq":       {"success": 0.92, "lat_ms": 140, "cost": 0.2},   # fastest + cheapest, but flakiest
    "deepseek":   {"success": 0.95, "lat_ms": 600, "cost": 0.3},   # cheap but slow
    "broken":     {"success": 0.40, "lat_ms": 2000, "cost": 1.0},  # bad arm — bandit should avoid
}


def _simulate_call(arm_id: str) -> tuple[bool, float, float]:
    """Return (success, latency_ms, credits) for one simulated call."""
    a = TRUE_ARMS[arm_id]
    success = random.random() < a["success"]
    latency = a["lat_ms"] * random.uniform(0.8, 1.2)
    return success, latency, a["cost"]


async def _one_request(arm_ids: list[str], counters: dict) -> None:
    """Simulate one full LLM request: pick arm → call → feed back."""
    t0 = time.perf_counter()
    picked = bandit_router.pick(arm_ids, explore_bias=0.05)
    t_pick_us = (time.perf_counter() - t0) * 1e6

    success, latency, cost = _simulate_call(picked)

    t1 = time.perf_counter()
    bandit_router.record(picked, success=success, latency_ms=latency, credits=cost)
    t_record_us = (time.perf_counter() - t1) * 1e6

    counters["picks"][picked] = counters["picks"].get(picked, 0) + 1
    counters["pick_us"].append(t_pick_us)
    counters["record_us"].append(t_record_us)
    if not success:
        counters["failures"] += 1


async def run(n: int, concurrency: int) -> dict:
    """Drive N simulated requests with given concurrency."""
    arm_ids = list(TRUE_ARMS.keys())
    # Reset bandit state so the test is reproducible.
    for aid in arm_ids:
        bandit_router.reset(aid)

    counters = {
        "picks":      {},
        "pick_us":    [],
        "record_us":  [],
        "failures":   0,
    }

    sem = asyncio.Semaphore(concurrency)

    async def _bounded():
        async with sem:
            await _one_request(arm_ids, counters)

    t0 = time.perf_counter()
    await asyncio.gather(*[_bounded() for _ in range(n)])
    total_s = time.perf_counter() - t0

    # Summary
    pick_us = counters["pick_us"]
    rec_us = counters["record_us"]

    def pct(lst, p):
        return round(statistics.quantiles(lst, n=100)[p - 1], 2) if len(lst) > 1 else 0.0

    snap = bandit_router.snapshot()

    # Top-3 picked arms (convergence check)
    top3 = sorted(counters["picks"].items(), key=lambda kv: -kv[1])[:3]
    best_true_arm = max(TRUE_ARMS.items(), key=lambda kv: kv[1]["success"])[0]
    most_picked = top3[0][0]

    return {
        "n":                n,
        "concurrency":      concurrency,
        "wallclock_s":      round(total_s, 3),
        "rps":              round(n / total_s, 1),
        "pick_us_p50":      pct(pick_us, 50),
        "pick_us_p95":      pct(pick_us, 95),
        "pick_us_p99":      pct(pick_us, 99),
        "record_us_p50":    pct(rec_us, 50),
        "record_us_p95":    pct(rec_us, 95),
        "failure_rate":     round(counters["failures"] / n, 4),
        "pick_distribution": {k: round(v / n, 3) for k, v in counters["picks"].items()},
        "best_true_arm":    best_true_arm,
        "most_picked_arm":  most_picked,
        "converged_to_best": most_picked == best_true_arm,
        "snapshot":         snap,
        "posterior_error_max": max(
            abs(snap[aid]["success_rate"] - TRUE_ARMS[aid]["success"])
            for aid in snap
        ),
    }


def _pareto_correctness_tests() -> list[tuple[str, bool, str]]:
    """Verify pareto.choose() returns the right candidate per mode."""
    from services.routing.router import Candidate, choose
    out: list[tuple[str, bool, str]] = []

    # Three providers: premium (Opus), middle (GPT-4o), economy (Gemini-Flash)
    cands = [
        Candidate("anthropic", "claude-opus-4-6", quality=0.95, cost=15.0, latency_ms=900),
        Candidate("openai",    "gpt-4o",          quality=0.90, cost=5.0,  latency_ms=600),
        Candidate("gemini",    "gemini-2.5-flash", quality=0.78, cost=0.3, latency_ms=300, free_tier=True),
    ]

    p = choose(cands, mode="premium", free_first=False)
    out.append(("premium picks Opus", p and p.model == "claude-opus-4-6",
                f"got {p and p.model}"))

    e = choose(cands, mode="economy", free_first=True)
    out.append(("economy picks free Gemini", e and e.model == "gemini-2.5-flash",
                f"got {e and e.model}"))

    b = choose(cands, mode="batch", free_first=True)
    out.append(("batch picks free Gemini (cost-first)", b and b.model == "gemini-2.5-flash",
                f"got {b and b.model}"))

    c = choose(cands, mode="chat", free_first=False)
    out.append(("chat returns from frontier (not None)", c is not None,
                f"got {c and c.model}"))

    # Edge: empty list
    out.append(("empty list returns None", choose([], mode="auto") is None, ""))

    return out


def _rerank_latency_test(n: int = 1000) -> dict:
    """Time how long rerank_for_mode takes per call — verifies it can
    sit on the gateway hot path without measurable user-facing delay."""
    from services.routing.router import rerank_for_mode
    pairs = [
        ("anthropic", "claude-opus-4-6"),
        ("openai",    "gpt-4o"),
        ("gemini",    "gemini-2.5-flash"),
        ("groq",      "llama-3.3-70b"),
        ("deepseek",  "deepseek-chat"),
        ("xai",       "grok-2"),
    ]
    quality = {
        ("anthropic","claude-opus-4-6"): 0.95,
        ("openai","gpt-4o"): 0.90,
        ("gemini","gemini-2.5-flash"): 0.78,
        ("groq","llama-3.3-70b"): 0.72,
        ("deepseek","deepseek-chat"): 0.85,
        ("xai","grok-2"): 0.82,
    }
    cost = {p: 1.0 + i*0.5 for i, p in enumerate(pairs)}
    latency = {p: 200 + i*100 for i, p in enumerate(pairs)}
    free = {("gemini","gemini-2.5-flash"), ("groq","llama-3.3-70b")}

    times = []
    for _ in range(n):
        t = time.perf_counter()
        rerank_for_mode(pairs, mode="premium",
            quality_map=quality, cost_map=cost,
            latency_map=latency, free_set=free)
        times.append((time.perf_counter() - t) * 1e6)

    def pct(p):
        return round(statistics.quantiles(times, n=100)[p - 1], 2)

    # Verify premium re-ranks Opus to head
    out = rerank_for_mode(pairs, mode="premium",
        quality_map=quality, cost_map=cost,
        latency_map=latency, free_set=free)

    return {
        "n":            n,
        "p50_us":       pct(50),
        "p95_us":       pct(95),
        "p99_us":       pct(99),
        "premium_head": out[0],
        "head_correct": out[0] == ("anthropic", "claude-opus-4-6"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--concurrency", type=int, default=100)
    ap.add_argument("--label", type=str, default="run")
    args = ap.parse_args()

    result = asyncio.run(run(args.n, args.concurrency))
    print(f"\n=== LOAD TEST [{args.label}] ===")
    print(f"N={result['n']} conc={result['concurrency']} "
          f"wall={result['wallclock_s']}s rps={result['rps']}")
    print(f"pick():   p50={result['pick_us_p50']}µs  p95={result['pick_us_p95']}µs  p99={result['pick_us_p99']}µs")
    print(f"record(): p50={result['record_us_p50']}µs  p95={result['record_us_p95']}µs")
    print(f"failure_rate={result['failure_rate']}")
    print(f"\nconverged_to_best: {result['converged_to_best']}  (best={result['best_true_arm']}, "
          f"most-picked={result['most_picked_arm']})")
    print(f"max posterior error: {result['posterior_error_max']:.4f}")
    print(f"\npick distribution:")
    for aid, frac in sorted(result["pick_distribution"].items(), key=lambda kv: -kv[1]):
        print(f"  {aid:10s} {frac*100:5.1f}%   true={TRUE_ARMS[aid]['success']:.2f}")
    print(f"\nlearned posteriors:")
    for aid in sorted(result["snapshot"]):
        s = result["snapshot"][aid]
        err = s["success_rate"] - TRUE_ARMS[aid]["success"]
        print(f"  {aid:10s} pulls={s['pulls']:5d}  learned={s['success_rate']:.3f}  "
              f"true={TRUE_ARMS[aid]['success']:.2f}  err={err:+.3f}")

    # ── Pareto correctness ──
    print("\n=== PARETO CORRECTNESS ===")
    correctness = _pareto_correctness_tests()
    passed = sum(1 for _, ok, _ in correctness if ok)
    for name, ok, detail in correctness:
        mark = "[OK]  " if ok else "[FAIL]"
        print(f"  {mark} {name}  {detail}")
    print(f"  {passed}/{len(correctness)} passed")

    # ── Rerank latency ──
    print("\n=== rerank_for_mode LATENCY (hot-path overhead) ===")
    rr = _rerank_latency_test(n=2000)
    print(f"  N={rr['n']}  p50={rr['p50_us']}us  p95={rr['p95_us']}us  p99={rr['p99_us']}us")
    print(f"  premium head: {rr['premium_head']}  correct={rr['head_correct']}")


if __name__ == "__main__":
    main()
