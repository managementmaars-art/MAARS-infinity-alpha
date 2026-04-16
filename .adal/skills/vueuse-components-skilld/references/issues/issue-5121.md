---
number: 5121
title: BUG | `useMediaQuery` | v14 breaks nuxt build (with nitropack@2.12.8)
type: other
state: closed
created: 2025-10-25
url: "https://github.com/vueuse/vueuse/issues/5121"
reactions: 9
comments: 3
---

# BUG | `useMediaQuery` | v14 breaks nuxt build (with nitropack@2.12.8)

### Describe the bug

After upgrading to VueUse v14, the Nuxt build fails, even when using Nitro 2.18.2, which was expected to fix the related issue.

...

---

## Top Comments

**@43081j** [maintainer] (+8):

the fix is here FYI

https://github.com/nitrojs/nitro/pull/3689

once nitro v2 ships this, it should be fixed

**@alimozdemir**:

I faced the same issue. For a workaround, I stopped using the `useWindowSize` composable from the code and directly used `window.innerWidth`.

**@erwanjugand** (+1):

Build works with nitro@2.12.9 