"""24/7 HIGH-STRESS test — verify 0 fallbacks under burst load.

Differs from sim_realistic.py (which is production-natural-pacing):
  - 6 concurrent workers (vs 2)
  - Shorter gap: exp(μ=0.4s) bounded at 2s (vs μ=1.5s at 6s)
  - Same 9-category weighted mix

Purpose: prove that wait_for_slot + atomic try_claim + 55% safety factor
deliver zero internal fallbacks even when 6 workers hammer the router
continuously.
"""
import asyncio, sys, time, random, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv(str(Path(__file__).resolve().parent.parent.parent / ".env"))

USER_ID = "user_36301191e2cb"
from scripts.sim200 import POOLS  # noqa: E402

CATEGORY_WEIGHTS = {
    "general":   0.25, "coding":   0.20, "webdesign": 0.10,
    "social":    0.10, "content":  0.12, "research":  0.10,
    "image":     0.05, "video":    0.03, "heavy":     0.05,
}


def weighted_category():
    r = random.random()
    acc = 0.0
    for c, w in CATEGORY_WEIGHTS.items():
        acc += w
        if r < acc:
            return c
    return "general"


_progress = {"completed": 0, "errors": 0, "start": 0.0, "per_cat": {}}


async def worker(wid, target, queue, complete_fn, user_id, tag):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            return
        i, category, prompt = item
        t0 = time.time()
        try:
            resp = await complete_fn(
                user_id=user_id,
                messages=[{"role": "user", "content": prompt}],
                model="maars/auto",
                source=tag,
            )
            wall = round((time.time() - t0) * 1000)
            preview = resp.get("choices", [{}])[0].get("message", {}).get("content", "")[:22]
        except Exception as exc:
            _progress["errors"] += 1
            wall = round((time.time() - t0) * 1000)
            preview = f"FAIL {str(exc)[:18]}"

        _progress["completed"] += 1
        _progress["per_cat"][category] = _progress["per_cat"].get(category, 0) + 1
        done = _progress["completed"]
        if done % 100 == 0 or done <= 3 or done == target:
            elapsed_s = time.time() - _progress["start"]
            rate = done / elapsed_s * 60
            eta_min = (target - done) / max(rate / 60, 0.01) / 60
            print(f"  [{done:>4}/{target}] w{wid} {category:9s} {wall:>5}ms "
                  f"{preview:22s}  ({rate:>5.1f} rpm · ETA {eta_min:.1f}m)")

        # HIGH-STRESS pacing: exp(μ=0.4s), capped 2s. Workers hammer
        # concurrently — rate-limiter has to keep up.
        gap = min(random.expovariate(1 / 0.4), 2.0)
        await asyncio.sleep(gap)
        queue.task_done()


async def main():
    from db import db
    from services.llm_gateway import complete

    target = int(os.environ.get("SIM_TARGET", "3000"))
    tag = os.environ.get("SIM_TAG", "client_sim_stress")
    concurrency = int(os.environ.get("SIM_CONCURRENCY", "6"))

    await db.gateway_usage_logs.delete_many({"source": tag})
    random.seed(int(time.time()))

    print(f"HIGH-STRESS sim: {target} requests, {concurrency} workers, "
          f"exp(μ=0.4s) gaps, 9-cat mix.")

    queue = asyncio.Queue()
    for i in range(1, target + 1):
        category = weighted_category()
        prompt = random.choice(POOLS[category])
        await queue.put((i, category, prompt))
    for _ in range(concurrency):
        await queue.put(None)

    _progress["start"] = time.time()
    _progress["per_cat"] = {}
    workers = [asyncio.create_task(worker(w+1, target, queue, complete, USER_ID, tag))
               for w in range(concurrency)]
    await asyncio.gather(*workers)

    elapsed = round(time.time() - _progress["start"])
    print(f"\nDone in {elapsed}s ({elapsed/60:.1f}m). Errors: {_progress['errors']}/{target}")
    from services.costing.blended_cost import invalidate_cache
    invalidate_cache()


if __name__ == "__main__":
    asyncio.run(main())
