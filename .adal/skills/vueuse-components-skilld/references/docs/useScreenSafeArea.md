---
category: Browser
---

# useScreenSafeArea

Reactive `env(safe-area-inset-*)`



## Usage

In order to make the page to be fully rendered in the screen, the additional attribute `viewport-fit=cover` within `viewport` meta tag must be set firstly, the viewport meta tag may look like this:

```html
<meta name="viewport" content="initial-scale=1, viewport-fit=cover" />
```

Then we could use `useScreenSafeArea` in the component as shown below:

```ts
import { useScreenSafeArea } from '@vueuse/core'

const {
  top,
  right,
  bottom,
  left,
} = useScreenSafeArea()
```

For further details, you may refer to this documentation: Designing Websites for iPhone X

## Component Usage

```vue
<template>
  <UseScreenSafeArea top right bottom left>
    content
  </UseScreenSafeArea>
</template>
```

## Type Declarations

```ts
/**
 * Reactive `env(safe-area-inset-*)`
 *
 * @see https://vueuse.org/useScreenSafeArea
 */
export declare function useScreenSafeArea(): {
  top: ShallowRef<string, string>
  right: ShallowRef<string, string>
  bottom: ShallowRef<string, string>
  left: ShallowRef<string, string>
  update: () => void
}
export type UseScreenSafeAreaReturn = ReturnType<typeof useScreenSafeArea>
```
