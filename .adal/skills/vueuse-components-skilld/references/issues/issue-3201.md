---
number: 3201
title: useInfiniteScroll - broken on v10.2.1
type: other
state: open
created: 2023-07-01
url: "https://github.com/vueuse/vueuse/issues/3201"
reactions: 13
comments: 33
labels: "[needs reproduction]"
---

# useInfiniteScroll - broken on v10.2.1

### Describe the bug

I use this to scroll on the body:
```js
useInfiniteScroll(document, fetch, {
  distance: 10
})
```
However upgrading to `v10.2.1`, it doesn't seem to work anymore. Downgrading to `v10.2.0` fixes the issue.

I think this is the cause: https://github.com/vueuse/vueuse/pull/3143

### Reproduction

https://stackblitz.com/edit/vitejs-vite-zf9drc

### System Info

```Shell
System:
    OS: Linux 6.3 Alpine Linux
    CPU: (16) x64 AMD Ryzen 7 5700G with Radeon Graphics
    Memory: 19.14 GB / 30.70 GB
    Container: Yes
    Shell: 1.36.0 - /bin/ash
  Binaries:
    Node: 18.16.0 - /usr/bin/node
    npm: 9.6.6 - /usr/bin/npm
  npmPackages:
    @vueuse/components: ^10.2.1 => 10.2.1 
    @vueuse/core: ^10.2.1 => 10.2.1
    @vueuse/head: ^1.1.26 => 1.1.26 
    vue: ^3.3.4 => 3.3.4
```


### Used Package Manager

npm

### Validations

- [X] Follow our Code of Conduct
- [X] Read the Contributing Guidelines.
- [X] Read the docs.
- [X] Check that there isn't already an issue that reports the same bug to avoid creating a duplicate.
- [X] Make sure this is a VueUse issue and not a framework-specific issue. For example, if it's a Vue SFC related bug, it should likely be reported to https://github.com/vuejs/core instead.
- [X] Check that this is a concrete bug. For Q&A open a GitHub Discussion.
- [X] The provided reproduction is a minimal reproducible example of the bug.

---

## Top Comments

**@francoism90** (+5):

So I've moved to `useScroll` instead, I don't know what happend to `useInfiniteScroll`, but it just doesn't work anymore.

It's a bit ugly, but it also brings some new features:
```ts
const { arrivedState } = useScroll(document, {
  throttle: 100,
  behavior: 'smooth'
})

onMounted(() => initialize())
watch(arrivedState, (state) => (state.bottom ? fetch() : null))
```

**@francoism90** (+2):

So I did some more testing, and I believe it's completely broken now:



```
useInfiniteScroll(document, () => console.log('fetch'), {
  distance: 10
})
```
This happens when I just scroll to the end of the page, it keeps calling this over-and-over.. and never stops.

Weird thing, is when I call a method (`useInfiniteScroll(document, fetch, ..)`), it does call the method, but only one time after, and never again later. It also does call `fetch` 2x/3x on start, instead of the usual only when...

**@francoism90** (+1):

@erikkkwu It simply doesn't call anything. I tried Firefox and Brave, they don't call 'fetch' (or anything else) when reaching the button of the page.

It does work fine on `[v10.2.0](https://github.com/vueuse/vueuse/releases/tag/v10.2.0)` (and previous versions). so I don't think it's the observer.