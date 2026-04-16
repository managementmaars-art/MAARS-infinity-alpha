---
number: 5200
title: BUG | `refManualReset` | Does not track deep mutations
type: docs
state: open
created: 2025-12-08
url: "https://github.com/vueuse/vueuse/issues/5200"
reactions: 5
comments: 4
labels: "[documentation, pr welcome, has pr]"
---

# BUG | `refManualReset` | Does not track deep mutations

### Describe the bug

`refManualReset()` is implemented using `customRef`.
Because `customRef` only tracks access through its `get()` and triggers updates only when `set()` is called, deep mutations inside the stored object are never tracked.

### Reproduction

https://playground.vueuse.org/#eNp9U01v2zAM/SuELknQxMawHYbMLZoNPXTA2mHLbrpoMu0olSVDH0mGwP99lO2kQVHkYkvkI/X49HRkq7bNdhHZkhVeOtUG8BhiC1qY+paz4Dm740Y1rXUBjuCw+iFMFPoXEg46qJxtYHJPLaLHXFqHE264kdb4AJV1Ddy+KZoeuQEgtFtCvwQwosElcLa2DWfzIdY6WylN4SOImn4fPkOXMvTpZl/SGXkO643y4KLxc/gbA/x5hL3SGp6e1xDbUgSE/QZNagByQxOh56aKRgZlDSgjHQqPqxqns4FKIpzthI6YJYLZSCKjBjc3CZDmshTQtp5OXtuWy8n8WvGMSHNT5IPEJChtAjatJoq0AyhKtQOphfckeqXxAOmzkFaDIqBfSDQBHWyjD6r6d9ruF9QRacLNuOhvK8mXGt7RZKTfsSf2llLXFXnCjHCSL5Am91Ir+UIcLsShnquyTCIW+QAbKI/lRX4xCZuTZUikStXZ1ltDvuqF5UzapqWj3XObxCdbnW+fM6G13X/vY8FFHB1ANRuUL+/Et/6QYpz9dOQotyOK51wQrsYwpB9+P+GB1udkY8uoCX0lSR61OiaOA+xrNCXRvsD1bB/7F6FMvfYPh4DGn4ZKRHuf9njO6GV8uzL6K92P2aeTv1n3HyhOOGg=

###  Expected behavior

In fact, I'm not asking for a change to the implementation, since user can solve this simply by add `reactive` to the `defaultValue`.

Instead, I propose adding a clear documentation note: 

- `refManualReset()` is shallow.
- Deep mutations inside the object will not trigger reactive updates unless the object itself is wrapped with `reactive()`.
- Only calling `set()` triggers updates — internal mutations do not.

...

---

## Top Comments

**@ilyaliao** [maintainer] (+1):

We use `customRef` in many places, and they all have the same issue. I suggest mentioning it in the Guide rather than in individual function documentation.

**@9romise** [maintainer] (+2):

PR welcome.
Some discussion before:
- https://github.com/vueuse/vueuse/issues/5112
- https://github.com/vueuse/vueuse/pull/5115#issuecomment-3583872497

**@xiaoland** (+2):

> We use `customRef` in many places, and they all have the same issue. I suggest mentioning it in the Guide rather than in individual function documentation.

Good idea! I have searched across the code base for all usages of `customRef`:

...