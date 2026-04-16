# WOLF v4 Learnings & Trading Discipline

## Proven Session Results (Feb 23, 2026)

**20+ trades, 67% win rate, +$1,500 realized on $6.5k→$7k budget.**

### Top Winners
- HYPE SHORT: +$560 (Tier 1→4, +15.5% ROE, let DSL run)
- XRP SHORT #1: +$303 (Tier 3 in 19 min)
- ETH SHORT #2: +$274 (Tier 1→4, ~18% ROE)
- SNDK SHORT: +$237 locked (Tier 3, +19% peak ROE in 65 min)
- LIT SHORT: +$205
- APT SHORT: +$178 (stagnation close at +9.3% ROE)

### Key Losses
- NVDA LONG: -$114 (3/3 Phase 1 breaches, counter-trend)
- SILVER SHORT: -$72
- MON SHORT: -$62 (too few traders)
- MU SHORT: -$58 (dead weight, conv 0)

### Pattern
Winners move FAST. XRP Tier 3 in 19 min, XMR Tier 2 in 37 min, SNDK +19% ROE in 45 min. If not moving within 30 min, probably won't. Speed of initial move is a quality signal.

---

## Key Learnings

1. **Rank climb IS the entry signal — conviction is lagging.** Don't gate entries on conviction ≥4. By the time conviction is 4, the move is priced in.

2. **Catch movers at #50→#35→#20.** Find big movers climbing from deep positions before they reach top 15.

3. **PnL/contribution acceleration > trader count.** A fast-accelerating asset at rank #30 with 15 traders beats a stale rank #10 with 100 traders.

4. **Conviction collapse = instant cut.** ETH went conv 4→1 (220→24 traders) in 10 min. Cut for -$12 instead of -$100+.

5. **Don't anchor on past positions.** Evaluate every signal fresh. Past losses shouldn't make you gun-shy on the same asset.

6. **Concentrate, don't spread thin.** 6 positions averaging -6% = slow death. 2-3 high-conviction positions is the way.

7. **Hourly trend > SM signals.** SM conviction 4 on a 1-min bounce doesn't override a 2-week downtrend. NEVER go counter-trend on hourly.

8. **Tier 1 lock doesn't guarantee profit.** SILVER hit Tier 1 then retraced through floor below entry. Tier locks protect from HW, but if price dumps below entry, you still lose.

9. **Oversold decline rule.** Skip short entries when RSI < 30 AND extended 24h move (> -4%). Even high-scoring shorts should be declined when oversold — bounce risk eats leveraged shorts.

10. **Speed of move = quality signal.** If a position doesn't move meaningfully in 30 min, it's probably not going to. Don't hold dead weight hoping for a late move.

---

## Known Bugs & Footguns

1. **Senpi `create_position` with `dryRun:true` ACTUALLY EXECUTES** — do NOT use dryRun.

2. **DSL transient API failures**: Clearinghouse queries can fail transiently. DSL v4 retries (deactivates at 10 consecutive failures). Don't panic on 1 failure — use `execution_get_open_position_details` to verify before manual intervention.

3. **Health check can't see XYZ positions**: `job-health-check.py` doesn't query `dex=xyz`, causing false ORPHAN_DSL warnings for XYZ assets. Known issue.

4. **Multiple cron jobs can race**: Scanner/SM closes a position, DSL fires 1-3 min later and finds it gone. Always deactivate DSL + disable cron when ANY job closes a position.

5. **Max leverage varies per asset**: Scanner's `leverage` field is a conservative suggestion, NOT the actual max. Check `max-leverage.json`. E.g., WLFI is only 5x max.

6. **`close_position` is the tool to close positions** (not `edit_position` with action=close).

7. **XYZ positions**: Use `leverageType: "ISOLATED"` in `create_position`. The WALLET isn't cross/isolated — individual POSITIONS are.

---

## Trading Discipline Rules

- **Empty slot > mediocre position** — never enter just to fill a slot
- **Act on first IMMEDIATE_MOVER** — don't wait for confirmation scans
- **Mechanical DSL exits** — never override the DSL, let it do its job
- **Race condition prevention** — deactivate DSL + disable cron in the same action when any job closes a position
- **Dead weight rule** — SM conviction 0 + negative ROE for 30+ min = cut immediately
- **Rotation bias** — favor swapping into higher-conviction setups over holding stale positions
- **Budget discipline** — all sizing from wolf-strategy.json, never hard-code dollar amounts
