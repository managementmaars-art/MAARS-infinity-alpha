# Startup, bundle size, and OTA update performance

## Startup anatomy (what usually dominates)

Cold start is typically a combination of:
1) Native bootstrap
2) JS bundle I/O + parse/execute
3) Synchronous module initialisation
4) First screen render (and any blocking async work you made “sync” via gating)

Your goal is not “zero work”, it’s:
- **minimum work before first paint**, and
- **minimum JS evaluation before the first interactive screen**.

## Measure startup correctly

- Separate **cold start** vs **warm start**.
- Measure in **Release** (or closest available) builds.
- Use a simple scenario: launch → first meaningful screen.

If you can’t get a release build quickly, an intermediate step is to run production-mode bundling in a dev client (still not identical to Release):

```bash
npx expo start --no-dev --minify
```

## High-ROI fixes

### 1) Splash screen gating (do less, not more)

Pattern:
- Keep splash visible while loading only truly critical resources (fonts, tiny config).
- Hide it as soon as those complete.

Example (fonts + splash gating):

```ts
import { useEffect } from 'react';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';

SplashScreen.preventAutoHideAsync();

export function Root() {
  const [loaded, error] = useFonts({
    InterBlack: require('../assets/fonts/Inter-Black.otf'),
  });

  useEffect(() => {
    if (loaded || error) SplashScreen.hideAsync();
  }, [loaded, error]);

  if (!loaded && !error) return null;
  return null; // your app tree
}
```

Anti-pattern:
- Keeping splash up while you fetch non-critical data that can load after first paint.

### 2) Confirm Hermes + treat engine upgrades as a perf lever

Hermes is the default JS engine in modern Expo/RN for good reasons:
- Often faster startup
- Lower memory usage
- Sometimes smaller app size

Make the choice explicit if you’re unsure:

```json
{
  "expo": {
    "jsEngine": "hermes"
  }
}
```

Note:
- Changing the JS engine is not supported in Expo Go in modern SDKs; use a development build if you need to switch engines.

#### OTA updates + Hermes bytecode compatibility

If you ship OTA updates (`expo-updates` / EAS Update):
- Hermes compiles JS into bytecode.
- **Bytecode format depends on Hermes version.**

Operational rule:
- When you change Hermes/RN/Expo runtime such that bytecode compatibility can change, also manage `runtimeVersion` so incompatible updates won’t load on old binaries.

### 3) Shrink JS evaluation (bundle size + module init)

#### Tree shaking hygiene

- Prefer ESM `import`/`export` everywhere you control.
- Avoid patterns that break tree shaking (notably: converting ESM to CommonJS).
  - Watch out for Babel configs that apply `@babel/plugin-transform-modules-commonjs` (or similar) to app code.
- Guard dev-only code paths with `__DEV__` / `process.env.NODE_ENV` so production bundles can drop them.

Optional (advanced): Expo unstable tree shaking flags

Some Expo setups support production-only tree shaking via environment flags during bundling/export. If you opt in:

```bash
EXPO_UNSTABLE_METRO_OPTIMIZE_GRAPH=1 EXPO_UNSTABLE_TREE_SHAKING=1 npx expo export
```

Treat these flags as an experiment:
- Validate behaviour in real release builds.
- Confirm correctness (no missing side effects).

#### Metro: inline requires (measure it)

`inlineRequires` can reduce startup cost by deferring module evaluation.

Metro config example:

```js
const { getDefaultConfig } = require('expo/metro-config');
const config = getDefaultConfig(__dirname);

config.transformer.getTransformOptions = async () => ({
  transform: {
    inlineRequires: true,
  },
});

module.exports = config;
```

Caveat:
- Inline requires can change execution order of side effects.
- Validate with production bundling and smoke tests.

#### Expo’s experimental tree shaking

Expo supports production-only tree shaking features that require:
- ESM modules
- Production bundling (e.g. via `npx expo export`)

If you opt into unstable flags, do it on a branch and verify with real builds.

### 4) Android binary size knobs (don’t trade startup blindly)

With `expo-build-properties`, you can enable:
- R8 minification (`enableMinifyInReleaseBuilds`)
- Resource shrinking (`enableShrinkResourcesInReleaseBuilds`)
- JS bundle compression (`enableBundleCompression`) — **smaller APK, potentially slower startup**

Example:

```json
{
  "expo": {
    "plugins": [
      [
        "expo-build-properties",
        {
          "android": {
            "enableMinifyInReleaseBuilds": true,
            "enableShrinkResourcesInReleaseBuilds": true,
            "enableBundleCompression": false
          }
        }
      ]
    ]
  }
}
```

Recommendation:
- Turn on minify + shrink first.
- Treat bundle compression as an experiment with a startup KPI before/after.

### 5) OTA update size: control assets and verify

If you ship OTA updates, large assets can dominate update size.

Key control:
- `updates.assetPatternsToBeBundled` (or legacy `extra.updates.assetPatternsToBeBundled`) to include only certain assets in updates.

Example:

```json
{
  "expo": {
    "updates": {
      "assetPatternsToBeBundled": ["app/images/**/*.png"]
    }
  }
}
```

Critical step:
- Run `npx expo-updates assets:verify <dir>` to ensure all required assets are available for an update.

Optional (newer stacks): Hermes bytecode diffing for smaller OTA updates

On newer Expo SDK lines, Expo may support distributing OTA updates as binary patches (Hermes bytecode diffing). If OTA payload size is a major KPI for you, evaluate this feature via the Expo changelog/docs for your SDK.

## Hermes V1 notes (2026-era stacks)

- React Native 0.84 makes Hermes V1 the default engine.
- Expo SDK 55 supports opting into Hermes V1 via `expo-build-properties` (`useHermesV1`), but it can require building React Native from source (increasing build times) and may have known regressions.

Treat Hermes V1 as:
- A potentially high-impact performance lever, and
- A controlled rollout (branch, perf test, rollback plan).

## Suggested deliverables for this domain

- A table of startup timings (cold/warm) before/after.
- A list of “startup blockers” removed or deferred.
- Bundle/OTA size report (JS bundle bytes + asset bytes).

## Links

See `references/resources.md` for:
- Expo Hermes guide
- Expo tree shaking guide
- Metro config docs
- expo-build-properties
- EAS Update asset selection + runtimeVersion docs
