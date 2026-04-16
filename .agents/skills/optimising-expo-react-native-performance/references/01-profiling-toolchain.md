# Profiling toolchain for Expo + React Native

## Golden rule

Always profile performance in **production-like builds**:
- Release builds for final numbers.
- “Profileable” / “debugOptimized” / profiling builds when you need tooling.

Dev mode can massively distort JS thread timing.

## What to use for what

### React Native DevTools (JS + React)
Use for:
- JS execution timelines and React commit timings.
- Identifying long tasks on the JS thread.
- Heap snapshots and JS memory growth (JS heap only).

Key panels:
- **Performance**: record a trace, inspect JS execution + React tracks + network events.
- **Memory**: take heap snapshots and allocation timelines.
- **React Profiler**: find components with expensive commits.

Expo tip:
- In Expo projects, DevTools can be opened from the Expo CLI terminal (commonly by pressing `j`).

Notes:
- DevTools features depend on your runtime/engine (Hermes is the assumed default).
- Some debugging is not available or is limited in true Release builds.

### Android: Android Studio Profiler + System Trace
Use for:
- UI jank attribution across threads.
- CPU, memory allocations, leaks, and system tracing.

Practical workflow:
1) Open the `android/` project in Android Studio (requires prebuild/CNG if you don’t have native folders).
2) Run as **profileable**.
3) Use the System Trace / “Capture System Activities” workflow.
4) Look at frame boundaries, main thread work, RenderThread, and JS thread.

Export traces to Perfetto if useful for sharing.

### iOS: Xcode Instruments
Use for:
- Time Profiler (CPU hot spots).
- Allocations and Leaks.
- Networking templates.

Workflow:
1) Build and run a production-like build.
2) Record a Time Profiler trace around the problematic interaction.
3) For memory: use Allocations/Leaks while repeating the suspect flow.

## Measuring in Release builds (real-world constraints)

- Many “debug conveniences” are missing in Release builds.
- Native profilers still work in Release builds.
- Expo offers intermediate build modes (for example “debugOptimized” in some workflows) that can be closer to production performance while retaining some debugging; use these when you need a middle ground.
- If you *must* capture JS/Hermes profiles in Release builds, consider an approach like:
  - Recording traces with platform profilers.
  - Using a release profiling helper library.

### Optional: react-native-release-profiler

If you need JS performance tooling closer to release builds, evaluate `react-native-release-profiler` (Margelo).

Caveats:
- It involves native integration (check installation steps and compatibility).
- In Expo managed projects you may need prebuild/CNG and the additional CLI dependency it mentions.

## Memory debugging workflow (practical)

1) Reproduce with a **stress loop**:
   - Navigate A → B → A, repeat 10×.
   - Or scroll an image grid 10×.
2) Watch if memory returns to baseline.
3) If JS heap grows:
   - Use RN DevTools Memory panel, take heap snapshots before/after.
4) If JS heap is stable but RSS keeps rising:
   - Use Instruments / Android Studio memory tooling to find native allocations.

## What to save in your perf report

Always attach:
- Build type (Release/Profile/debugOptimized) and exact commit hash.
- Device model + OS version.
- Raw trace artefacts where possible.
- A before/after KPI table.

## Links

See `references/resources.md` for the official React Native profiling guide, DevTools docs, and Expo debugging docs.
