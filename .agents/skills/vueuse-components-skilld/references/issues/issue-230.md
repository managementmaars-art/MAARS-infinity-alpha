---
number: 230
title: useIndexedDb / useIDB
type: question
state: closed
created: 2020-11-21
url: "https://github.com/vueuse/vueuse/issues/230"
reactions: 13
comments: 4
labels: "[enhancement, help wanted, pr welcome]"
---

# useIndexedDb / useIDB

Any plans for adding a IndexedDb utility ? 

---

## Top Comments

**@antfu** [maintainer] (+3):

This is definitely good to have. However, I am not that familiar with IndexedDB, PR welcome. Another option is that we could have a wrapper for https://dexie.org/

**@jssullivan** (+1):

I am working to make a composition wrapper around idb-keyval. Which is a key value store api on top of Indexed DB. It will have a similar type signature to useStorageAsync 

This won't add full support for Indexed DB. However it will give you typed keys and values without the need of a serializer, adds web worker support, and lets you use more storage space when compared to using the local storage variant.

The caveat being it won't reactively update if another source updates the KV store. There isn't a...

**@brokolosov** (+1):

I found a local DB comparison (localStorage, localForage, indexDB, Dexie, LokiJS etc.)  Based on this comparison, a better choice would be LokiJS. Dexie is to slowly... IMHO
P.S. video