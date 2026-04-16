---
number: 3536
title: useRouteParams doesn't allow removing the parameter by setting it to empty string / null / undefined
type: other
state: open
created: 2023-11-09
url: "https://github.com/vueuse/vueuse/issues/3536"
reactions: 5
comments: 8
labels: "[needs reproduction, has workaround]"
---

# useRouteParams doesn't allow removing the parameter by setting it to empty string / null / undefined

### Describe the bug

I'm using @vueuse/router and @vueuse/nuxt. I have a page that has one required route param and one optional route param. When trying to remove the optional param using the ref from `useRouteParams`, the url doesn't change correctly. I've tried setting the ref to an empty string, null and undefined. Tried with and without a default value for the route param. Doesn't work.

### Reproduction

https://github.com/mtdvlpr/reproduction

### System Info

```Shell
System:
    OS: Windows 11 10.0.22621
    CPU: (16) x64 Intel(R) Core(TM) i9-9980HK CPU @ 2.40GHz
    Memory: 20.55 GB / 31.70 GB
  Binaries:
    Node: 18.18.2 - C:\Program Files\nodejs\node.EXE
    Yarn: 3.6.4 - C:\Program Files\nodejs\yarn.CMD
    npm: 9.8.1 - C:\Program Files\nodejs\npm.CMD
  Browsers:
    Edge: Chromium (119.0.2151.44)
    Internet Explorer: 11.0.22621.1
  npmPackages:
    @vueuse/nuxt: ^10.5.0 => 10.5.0
    @vueuse/router: ^10.5.0 => 10.5.0
    nuxt: ^3.8.1 => 3.8.1
    vue: ^3.3.8 => 3.3.8
```


### Used Package Manager

yarn

### Validations

...