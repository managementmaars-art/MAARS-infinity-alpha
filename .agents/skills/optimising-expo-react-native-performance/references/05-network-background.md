# Network, caching, and background work

## Network performance: what actually matters

Users feel:
- “Screen is empty / spinner” time.
- Stalls when navigating between data-backed screens.

Your goal is usually:
- Fewer requests.
- Smaller payloads.
- Better caching and deduping.
- Predictable retries/backoff.

## Measure first

- Use React Native DevTools Network tab where available (Expo tooling can enable network inspection).
- Capture p95 latency and “screen data-ready time”.

## High-ROI implementation patterns

### 1) Avoid refetch storms

Common causes:
- Multiple components triggering the same request.
- Navigation focus effects refetching too aggressively.

Fixes:
- Deduplicate in-flight requests.
- Cache server-state data (stale-while-revalidate patterns).

### 2) Use HTTP caching where possible

- ETags, Cache-Control, CDN caching.
- Treat “static-ish” resources differently from dynamic ones.

### 3) Consider Expo’s `expo/fetch` when you need consistency

Expo provides a WinterCG-compliant Fetch API with streaming support. Useful when you want consistent behaviour across environments.

```ts
import { fetch } from 'expo/fetch';

const resp = await fetch(url, { headers: { Accept: 'application/json' } });
const json = await resp.json();
```

## Background work (best effort, not guaranteed)

Mobile OS schedulers are aggressive about battery and background limits.

### Prefer `expo-background-task`

- Android: WorkManager
- iOS: BGTaskScheduler

Expect:
- Deferrable execution.
- Not immediate.
- Platform conditions (power/network) can gate execution.

Skeleton:

```ts
import * as TaskManager from 'expo-task-manager';
import * as BackgroundTask from 'expo-background-task';

const TASK_NAME = 'sync-task';

TaskManager.defineTask(TASK_NAME, async () => {
  // keep it short; handle failures
  return BackgroundTask.BackgroundTaskResult.Success;
});

await BackgroundTask.registerTaskAsync(TASK_NAME, {
  minimumInterval: 30, // minutes
});
```

### Avoid deprecated background APIs

If you still use `expo-background-fetch`, treat migration as part of modernising and improving reliability.

## Links

See `references/resources.md` for:
- Expo `expo/fetch` docs
- Expo background task docs
