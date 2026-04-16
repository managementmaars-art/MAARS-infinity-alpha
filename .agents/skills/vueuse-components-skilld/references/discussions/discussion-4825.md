---
number: 4825
title: "Why is console.log(toReactive(ref([]))) returning {} instead of [] ?"
category: Q&A
created: 2025-06-17
url: "https://github.com/vueuse/vueuse/discussions/4825"
upvotes: 1
comments: 1
answered: true
---

# Why is console.log(toReactive(ref([]))) returning {} instead of [] ?

I am converting a ref to an empty array to a reactive, and noticed that if I try to do it with VueUse' toReactive(), I get an empty object {}, while if I explicitly pass the .value, I get an empty array []:

```
import { reactive, ref } from "vue";
import { toReactive } from "@vueuse/core";

console.log(toReactive(ref([]))); // {}
console.log(toReactive(ref([]).value)); // []
```

Is this expected? I am confused, as I would have expected an empty array in both cases.
If I try to use this object as an array, I get errors i.e.:

```
const refVec = ref([]);
const vec = toReactive(refVec);
vec.push(33);
```

on node (v24) gives me an error, i.e.:

```
[...]
getOwnPropertyDescriptor() {
RangeError: Maximum call stack size exceeded
[...]
```

---

## Accepted Answer


Hi @tricaric! I'm Dosu and I’m helping the vueuse team.


This is expected: `toReactive` is designed for refs containing plain objects, not arrays. Internally, it creates a proxy with an empty object as the target, which means when you pass `ref([])`, the result is an object (`{}`), not an array (`[]`). This breaks array methods and can cause errors like the stack overflow you saw. If you want a reactive array, use `reactive(ref([]).value)` or just `reactive([])` instead. The current API doesn't support array refs for `toReactive`—it's intended for objects only, as shown in the implementation and tests see source.



*To reply, just mention @dosu.*

...