---
number: 4946
title: `toWritableComputed` | Destructure computed object properties
type: other
state: open
created: 2025-08-06
url: "https://github.com/vueuse/vueuse/issues/4946"
reactions: 1
comments: 2
---

# `toWritableComputed` | Destructure computed object properties

### Clear and concise description of the problem


In most cases `toRefs` can accomplish similar results. There are cases where `toWritableCompluted` can do things it cannot.

```ts
import { describe, expect, it } from 'vitest'
import { computed, ref as deepRef } from 'vue'
import { toWritableComputed } from './index'

describe('toWriteableComputed', async () => {
  it('references computed() -> deepRef() and keeps references to original target intact', async () => {
    const user = deepRef({ name: 'Bobby' })
    const comp = computed(() => user.value)

    // Note: the following would fail this test
    // const { name } = toRefs(comp.value)
    const { name } = toWritableComputeds(comp)

    expect(user.value).toEqual({ name: 'Bobby' })
    expect(comp.value).toEqual({ name: 'Bobby' })
    expect(name.value).toEqual('Bobby')

    user.value = {
      name: 'Allison',
    }

...