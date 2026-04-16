---
number: 5056
title: Multiple favicons with useFavicon?
category: Q&A
created: 2025-09-22
url: "https://github.com/vueuse/vueuse/discussions/5056"
upvotes: 1
comments: 2
answered: true
---

# Multiple favicons with useFavicon?

I'd like to provide multiple favicon sizes to support different display resolutions. With useFavicon, I've attempted to provide an array of strings as a value and to define multiple instances of useFavicon. The former simply doesn't work while the latter appears to create the last one to have its value declared. Is there an official way to do this or would this be an enhancement request?

---

## Accepted Answer

Looks like this is a case where https://unhead.unjs.io/ is taking over. Started looking at useHead and was directed there. From there it was easy to do this:
```
useHead({
  link: [
    { rel: 'icon', href: `/favicon-16x16.png` },
    { rel: 'icon', href: `/favicon-32x32.png` }
  ]
})
```