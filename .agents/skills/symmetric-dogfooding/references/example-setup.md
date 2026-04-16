# Example: trading-fitness and rangebar-py

Real-world symmetric dogfooding implementation between two polyrepos.

## Integration Surface

```
trading-fitness ◄──────────────────────► rangebar-py

trading-fitness EXPORTS:              rangebar-py EXPORTS:
- ITH metrics (PyO3 bindings)         - Range bar construction
- Bounded [0,1] LSTM features         - Microstructure features
- Rolling window computation          - Tick data aggregation

trading-fitness VALIDATES WITH:       rangebar-py VALIDATES WITH:
- rangebar range bars                 - trading-fitness ITH metrics
- Real Binance market data            - Real NAV series from bars
```

## Dependency Configuration

**trading-fitness side:**

```toml
# packages/ith-python/pyproject.toml
[project.optional-dependencies]
validation = ["rangebar"]

[tool.uv.sources]
rangebar = { git = "https://github.com/terrylica/rangebar-py", tag = "<tag>" }  # SSoT-OK
```

**rangebar-py side (if implementing full pattern):**

```toml
# pyproject.toml
[project.optional-dependencies]
validation = ["trading-fitness-metrics"]

[tool.uv.sources]
trading-fitness-metrics = {
    git = "https://github.com/terrylica/trading-fitness",
    subdirectory = "packages/metrics-rust",
    tag = "<tag>"  # SSoT-OK
}
```

## Validation Flow

```
1. trading-fitness runs E2E pipeline
   └── Uses rangebar to fetch range bars from Binance
   └── Computes ITH features on real market data
   └── Validates feature bounds [0,1]

2. rangebar-py (hypothetical) runs validation
   └── Uses trading-fitness ITH on constructed bars
   └── Validates metrics work on edge cases
   └── Confirms API compatibility
```

## Pre-Release Coordination

When releasing rangebar-py:

1. Run trading-fitness E2E with new rangebar version
2. Verify no breaking changes in range bar format
3. Update trading-fitness version pin
4. Release rangebar-py

When releasing trading-fitness:

1. Run ITH tests with current rangebar version
2. Verify feature outputs remain bounded
3. Coordinate if API changes affect rangebar consumers
4. Release trading-fitness

## Lessons Learned

1. **Checksum verification** - rangebar-py added SHA-256 verification after trading-fitness identified the need (issue #43)
2. **Polars schema compatibility** - Discovered datetime precision mismatch (μs vs ns) during cross-repo testing (issue #44)
3. **Version pinning** - Always pin to tags, not main branch, to avoid surprise breaks
