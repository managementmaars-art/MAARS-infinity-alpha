# Principles, KPIs, and perf budgets

## The performance model to keep in your head

- Most user-perceived “jank” is a missed frame deadline.
  - 60Hz devices: ~16.67ms per frame.
  - 90Hz: ~11.11ms per frame.
  - 120Hz: ~8.33ms per frame.
- React Native problems usually fall into one of two buckets:
  1) **JS thread stalls**: React renders, JS-driven animations, event handlers, heavy computation.
  2) **UI thread overload**: layout/drawing, view compositing, native transitions, native animations.

A classic symptom split:
- Scroll is smooth but taps/transitions lag → JS thread.
- Taps are instant but scrolling stutters / visual stutter → UI thread.

## Non-negotiable measurement rules

1) **Don’t trust dev mode perf.**
   - Dev builds add validation, error overlays, logging, and debug hooks.
2) **Use production-like builds for numbers.**
   - Release builds for final truth.
   - Profileable/profile builds when you need tooling.
3) **Control the scenario.**
   - Same device class, OS version, and steps.
   - Note cold vs warm start.
   - Note network conditions.
4) **One change at a time.**
   - Keep a log of each change and which KPI moved.

## KPI menu (pick 3–6)

Choose KPIs that match what users *feel*, not what feels “technical”.

### Startup
- **Cold start time**: app launch → first meaningful paint.
- **Time to interactive (TTI)**: launch → app responds reliably to taps.

### Interaction
- **Scroll smoothness**: dropped frames or FPS on a representative long list.
- **Navigation responsiveness**: p95 time for a screen transition.
- **Input latency**: tap → UI feedback visible.

### Memory
- **Steady-state memory** after repeating a key navigation flow (5–10×).
- **Memory growth rate** over a fixed usage script.

### Network
- **p95 API latency** for your core endpoint.
- **p95 screen data-ready time**: navigation → content rendered.

## Perf budgets

A budget is a pass/fail number that you can enforce in reviews and CI.

Suggested starter budgets (adjust per app):

- Cold start → first render: **< 1.5s** on your “mid-tier Android” test device.
- Navigation p95: **< 250ms** for simple screens, **< 500ms** for heavy screens.
- Long-list scroll: **no sustained jank** in a 10s fast scroll; no obvious blanking.
- Memory: **no upward drift** after 10 loops of the key flow.
- OTA update size: **< 2–5MB** typical patch (depends on app).

### Make budgets explicit

Commit a budgets file (example in `assets/templates/perf-budgets.example.json`) and update it only when you have a clear reason (new feature, new baseline, new device target).

## A minimal “baseline loop” template

1) Define KPIs + budgets.
2) Write a scenario script (bullet steps).
3) Measure baseline (release/profile build).
4) Pick the bottleneck domain.
5) Apply one fix.
6) Re-measure.
7) Keep or revert.
8) Add/adjust regression gates.

## Links

See `references/resources.md` for official docs (React Native perf & profiling, Expo Hermes/tree shaking/EAS). 
