# New Architecture and managed-workflow constraints

## Why it matters for performance work

React Native’s New Architecture changes core internals:
- How JS ↔ native communication works (JSI / TurboModules)
- Rendering pipeline (Fabric)
- Scheduling across threads

For performance, this can:
- Reduce overhead on hot paths
- Improve responsiveness
- Change the trade-offs of certain libraries

## Expo reality (modern SDKs)

In recent Expo SDK lines, the New Architecture becomes the default and (in newer SDKs) cannot be disabled.

Operational impact:
- Third-party native modules must be compatible.
- Some legacy debugging tools/workflows differ.

## How to manage compatibility

- Run `npx expo-doctor` to detect version mismatches and known issues.
- Validate native module compatibility (React Native Directory where applicable).
- Prefer Expo Modules API / config plugins for native integration.

## When to go native for performance

Stay managed if the bottleneck is:
- Re-renders, list configuration, images, bundle size, data fetching.

Consider native code (via Expo Modules API / prebuild) if you truly need:
- Heavy compute off the JS thread (image processing, codecs, crypto)
- Real-time audio/video pipelines
- High-frequency sensor processing

## Key caution

New Architecture upgrades can be high leverage but also high risk.
Treat them like a migration:
- Branch.
- Measure KPIs.
- Validate all critical flows.
- Keep a rollback plan.

## Links

See `references/resources.md` for:
- Expo New Architecture guide
- React Native New Architecture docs
