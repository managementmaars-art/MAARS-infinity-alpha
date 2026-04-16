---
category: Browser
---

# usePreferredContrast

Reactive prefers-contrast media query.

## Usage

```ts
import { usePreferredContrast } from '@vueuse/core'

const preferredContrast = usePreferredContrast()
```

## Component Usage

```vue
<template>
  <UsePreferredContrast v-slot="{ contrast }">
    Preferred Contrast: {{ contrast }}
  </UsePreferredContrast>
</template>
```

## Type Declarations

```ts
export type ContrastType = "more" | "less" | "custom" | "no-preference"
/**
 * Reactive prefers-contrast media query.
 *
 * @see https://vueuse.org/usePreferredContrast
 * @param [options]
 *
 * @__NO_SIDE_EFFECTS__
 */
export declare function usePreferredContrast(
  options?: ConfigurableWindow,
): ComputedRef<ContrastType>
```
