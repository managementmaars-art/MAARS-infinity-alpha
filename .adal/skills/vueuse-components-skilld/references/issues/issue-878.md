---
number: 878
title: Memoize results based on arguments in createSharedComposable 
type: other
state: closed
created: 2021-10-24
url: "https://github.com/vueuse/vueuse/issues/878"
reactions: 11
comments: 8
---

# Memoize results based on arguments in createSharedComposable 

Hi!

Firstly, thanks for maintaining such a great collection of utilities. It's always the first place I check before implementing a composable myself, and very often, I don't end up needing to because you guys already have :-) 

I'm wondering if it would make sense for `createSharedComposable` to memoize the result based on the arguments. This definitely makes sense in my use case, and I can't think of a situation where you wouldn't want this. The following, for example, seems incorrect to me, but that's the way it works currently:

```ts
// Loads product 42 and provides some methods on it
const { product42, updateProduct42, deleteProduct42 } = useProduct(42);
// Result is cached due to using createSharedComposable, so this will still be product 42
const { product43, updateProduct43, deleteProduct43 } = useProduct(43);
```

This is what I'm using right now to overcome this:

```ts
import { effectScope, EffectScope } from "vue-demi";
import { tryOnScopeDispose } from "@vueuse/core";
import { values } from "lodash/fp";


type AnyFn = (...args: any[]) => any;
type ResolverFn<Fn extends AnyFn> = (...args: Parameters<Fn>) => string;

const defaultArgumentResolver = (...args: any[]) => values(args).join("_");

/**
 * Make a composable function usable with multiple Vue instances.
 *
 * @see https://vueuse.org/createSharedComposable
 */
export default function createSharedComposable<Fn extends AnyFn>(
  composable: Fn,
  memoizeResolver: ResolverFn<Fn> = defaultArgumentResolver,
): Fn {
  let state: Record<string, { subscribers: number, scope: EffectScope, value: ReturnType<Fn> }> = {};

  return <Fn>((...args: Parameters<Fn>) => {
    const key = memoizeResolver(...args);
    if (!state[key]) {
      const scope = effectScope(true)
      const value = scope.run(() => composable(...args))
      state[key] = { subscribers: 1, scope, value};
    } else {
      state[key].subscribers += 1;
    }

    tryOnScopeDispose(() => {
      state[key].subscribers -= 1;

      const { scope, subscribers } = state[key];
      if (scope && subscribers <= 0) {
        scope.stop()
        delete state[key];
      }
    })

    return state[key].value;
  })
}
```...

---

## Top Comments

**@ilyaliao** [maintainer]:

Hi, I just found this. Is there a minimal reproduction that can trigger an error? I just tried it but didn’t see any errors.

If it’s confirmed to be a bug, I’d be happy to reopen it and investigate :)

**@OrbisK** [maintainer]:

@spaceemotion can you please open a new issue with a reproduction via https://playground.vueuse.org/?

**@spaceemotion**:

Was about to open an issue around this and saw this was an older issue. I frequently come across this pit-fall since the current version of `createSharedComposable` allows arguments. It doesn't error out and say "beware that if you do this, all instances will be shared, and arguments get ignored". The docs also don't have a warning for this.