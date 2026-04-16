# JS thread, UI thread, rendering, and animations

## Diagnosing the difference: JS vs UI thread

Think in two “FPS counters”:
- **JS thread**: React reconciliation, state updates, JS-driven animations, event handlers.
- **UI thread**: native layout/drawing, compositing, native animations.

Typical symptoms:
- **JS thread stall** → taps lag, JS-driven animations freeze, transitions feel slow.
- **UI thread overload** → scroll stutters even if JS is quiet; visual stutter under motion.

## JS thread: highest-leverage fixes

### 1) Remove production logging

`console.*` can become a meaningful bottleneck in bundled apps (including logs from dependencies). Remove them in production builds.

Example Babel config:

```json
{
  "env": {
    "production": {
      "plugins": ["transform-remove-console"]
    }
  }
}
```

### 2) Defer non-urgent work

Use `InteractionManager` to schedule heavy work after animations/interactions:

```ts
import { InteractionManager } from 'react-native';

InteractionManager.runAfterInteractions(() => {
  // heavy work: parsing, expensive state derivations, etc.
});
```

For tap handlers where visual feedback must appear first:

```ts
function onPress() {
  requestAnimationFrame(() => {
    doExpensiveAction();
  });
}
```

### 3) Reduce re-renders

Common causes:
- Parent state changes re-render entire lists.
- Context updates are too broad.
- Inline object/array props defeat memoisation.

Tactics:
- Split context providers.
- Stabilise props: memoise computed props, avoid inline functions in hot paths.
- Memoise row components (`React.memo`) where it matters.

#### React Compiler (modern option)

React Compiler can automatically memoise many components and reduce manual `useMemo`/`useCallback` burden.

Expo flow (practical):
1) Run the compiler healthcheck (rule violations are common in older code):

```bash
npx react-compiler-healthcheck@latest
```

2) Enable the Expo compiler experiment (exact packages/flags vary by Expo SDK; follow the Expo guide):

```bash
# often (SDK-dependent):
npx expo install babel-plugin-react-compiler@beta
```

```json
{
  "expo": {
    "experiments": {
      "reactCompiler": true
    }
  }
}
```

3) Profile key flows and keep a fast rollback path (feature flag / branch).

Use incremental adoption if needed (compile only certain files). For problematic files, use the opt-out directive (for example `"use no memo"`). Verify the compiler is active by looking for the compiler/memoisation indicators in DevTools (for example “Memo ✨” tags).

## UI thread: highest-leverage fixes

### 1) Prefer native-driven navigation transitions

Using native stack / native screens generally yields smoother transitions because animations run on native/UI runtime rather than the JS thread.

Practical toggles (depending on your nav stack):
- Use `react-native-screens` and ensure screens are enabled.
- Consider `detachInactiveScreens` and `freezeOnBlur` where appropriate.

### 2) Avoid expensive compositing on animated frames

Classic offenders:
- Transparent text over images (alpha compositing).
- Heavy shadows, blur views, large overdraw.

Platform knobs (use carefully, profile memory):
- Android: `renderToHardwareTextureAndroid`
- iOS: `shouldRasterizeIOS` (often enabled by default)

### 3) Don’t animate layout if you can animate transforms

Animating width/height of images can cause expensive recropping/resizing.
Prefer transform scale:

```ts
style={{ transform: [{ scale }] }}
```

## Animations: choose the right mechanism

### Animated API
- By default, keyframes are calculated on the JS thread.
- `useNativeDriver: true` pushes animation execution to native, resilient to JS stalls.

```ts
Animated.timing(value, {
  toValue: 1,
  duration: 250,
  useNativeDriver: true,
}).start();
```

### LayoutAnimation
- “Fire and forget” layout transitions.
- Typically less sensitive to JS thread drops.
- Not suitable for interruptible/gesture-driven animations.

### Reanimated
- Runs animations on the UI runtime via worklets.
- Great for gesture-driven and high-frequency animations.

Performance gotcha:
- Avoid reading shared values on the JS thread in tight loops; it can force synchronisation.

## Suggested debugging order for jank

1) Record a performance trace.
2) If JS is busy at the moment of jank → reduce JS work (re-renders/computation).
3) If JS is idle but UI stutters → reduce view cost (layout/compositing), and check animations.
4) If still unclear → system trace (Android) / Instruments (iOS).

## Links

See `references/resources.md` for:
- React Native performance overview
- Animated / LayoutAnimation docs
- Reanimated performance guidance
- react-native-screens documentation
- React Compiler docs + Expo guide
