---
number: 5074
title: How does useStorageAsync work without a serializer? chrome.storage can store complex objects without a serializer.
category: Q&A
created: 2025-09-30
url: "https://github.com/vueuse/vueuse/discussions/5074"
upvotes: 1
comments: 1
answered: true
---

# How does useStorageAsync work without a serializer? chrome.storage can store complex objects without a serializer.

[Chrome extension related]
I have a Pinia store that I'm trying to connect to chrome.storage using useStorageAsync and using chrome.storage.local as the persistence source.

However, I found that after implementing StorageLike, all data stored in chrome.storage became strings, even though chrome.storage can store objects and doesn't require a serializer.

I'm not exclusively reading from chrome.storage in my Vue app, and this serialization process prevents me from easily reading from chrome.storage in the background (because I need to handle the serialization).

I want to find a way to remove the serialization process

---

## Accepted Answer

> > Hi @aiktb! I'm Dosu and I’m helping the vueuse team.
> > useStorageAsync always applies serialization when reading from or writing to storage, even if the backend (like chrome.storage.local) can natively store objects. By default, it stringifies objects before storing them. To avoid this, you can provide a custom serializer via the serializer option that simply passes objects through without stringifying. For example:
> > ```js
> > useStorageAsync('key', initialValue, chromeStorageLike, {
> >   serializer: {
> >     read: v => v,      // pass-through: no deserialization
> >     write: v => v      // pass-through: no serialization
> >   }
> > })
> > ```
> > 
> > 
> >     
> >       
> >     
> > 
> >       
> >     
> > 
> >     
> >   
> > This way, your objects will be stored in chrome.storage.local as native objects, and you won't need to handle deserialization elsewhere. The serialization process is integral to useStorageAsync'...