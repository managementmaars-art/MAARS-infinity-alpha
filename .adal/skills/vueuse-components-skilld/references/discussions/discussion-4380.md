---
number: 4380
title: useGeolocation() coords available on useAsyncData() composable
category: Q&A
created: 2024-12-04
url: "https://github.com/vueuse/vueuse/discussions/4380"
upvotes: 1
comments: 2
answered: true
---

# useGeolocation() coords available on useAsyncData() composable

Hello, everyone,
I need the coordinates taken via the composable useGeolocation() in an API call I make via useAsyncData(). The problem is that they are still undefined at that point.
reproduction link: https://stackblitz.com/edit/nuxt-starter-zb6l89?file=app.vue
Does anyone have any idea how I could do this?
Thanks.

---

## Accepted Answer

In case anyone needs it, I found this solution that seems to work well:

```javascript
<template>
  <div>
    <NuxtRouteAnnouncer />
    <div>
      <h1>{{ data }}</h1>
      <span>error: {{ error }}</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useGeolocation } from '@vueuse/core';

const { coords, locatedAt, resume, error } = useGeolocation({
  enableHighAccuracy: false,
  maximumAge: Number.POSITIVE_INFINITY,
  immediate: true,
});

const { data } = useAsyncData(
  'test',
  () => {
    return `Hello World - ${coords.value.latitude} - ${coords.value.longitude}`;
  },
  {
    immediate: !error.value ? false : true,
    watch: () => (!error.value ? [locatedAt.value] : []),
  }
);
</script>
```