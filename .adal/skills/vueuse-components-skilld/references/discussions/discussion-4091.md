---
number: 4091
title: How to override the `afterFetch` of custom `useFetch` by `createFetch`
category: Q&A
created: 2024-07-10
url: "https://github.com/vueuse/vueuse/discussions/4091"
upvotes: 2
comments: 2
answered: false
---

# How to override the `afterFetch` of custom `useFetch` by `createFetch`

I created a `fetcher` using `createFetch` to intercept some request errors in the app, but some special cases i need to override the `afterFetch` option of `fetcher`:
```typescript
// fetcher.ts
export default createFetch({
  options:{
    beforeFetch(ctx){
      ctx = setToken(ctx)
      return ctx
    },
    afterFetch(ctx){
      console.log(ctx)
      return ctx
    }
  }
})
```
```typescript
// foo.vue
import fetcher from './fetcher'

const {data} = fethcer('/bar',{ 
  afterFetch(ctx){  // i tried replacing the default `afterFetch` option here, but i didn't
    console.log('remove default log.') // in fact, two logs appear on the console, they've all been executed.
    return ctx
  }
}).post().json()
```

how can i do that?

---

## Top Comments

**@dosubot** (+1):


Hey @hequ9! I'm here to help you with your code questions and bugs. Let's see if we can solve this together!


To override the `afterFetch` option so that only the new `afterFetch` function is executed, you can use the `combination: 'overwrite'` option when creating the fetch instance. Here is an example:

```typescript
// fetcher.ts
export default createFetch({
  combination: 'overwrite', // Add this line
  options: {
    afterFetch(ctx) {
      console.log(ctx)
      return ctx
    },
  },
})
```

```typescript
// foo.vue
import fetcher from './fetcher'

...

**@thecodemill** (+1):

It seems you can "overwrite" **ALL** the fetch methods, or "chain" **ALL** the fetch methods, but you can't, for example, overwrite just `beforeFetch` and expect your default `afterFetch` to fire. Your defaults just get deleted and you essentially have to pass both your modified `beforeFetch` **and** the original (default) `afterFetch` all over again. I've wasted a long time testing different approaches and coming to this same conclusion. Pretty demotivating tbh...