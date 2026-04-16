---
number: 4139
title: useChangeCase is broken in beta
type: other
state: closed
created: 2024-08-08
url: "https://github.com/vueuse/vueuse/issues/4139"
reactions: 7
comments: 1
---

# useChangeCase is broken in beta

### Describe the bug

When running the newest beta version of `useChangeCase` it fails. It works fine when running in development(Nuxt), but it fails after build(Nuxt). The demo page for useChangeCase is also broken when selecting the beta version.



The code in question(`packages/integrations/useChangeCase/index.ts`):


When logging out `changeCase` imported in module it becomes clear that doing `Object.values` won't work as it would have to check the keys in order to match the `endsWith("Case")`:


### Reproduction

https://github.com/vueuse/vueuse/blob/main/packages/integrations/useChangeCase/demo.vue

### System Info

```Shell
System:
    OS: macOS 14.5
    CPU: (10) arm64 Apple M1 Pro
    Memory: 84.19 MB / 32.00 GB
    Shell: 5.9 - /bin/zsh
  Binaries:
    Node: 20.14.0 - /usr/local/bin/node
    Yarn: 1.22.19 - /opt/homebrew/bin/yarn
    npm: 10.8.2 - /opt/homebrew/bin/npm
    pnpm: 8.6.12 - /opt/homebrew/bin/pnpm
    bun: 1.0.3 - /opt/homebrew/bin/bun
  Browsers:
    Chrome: 127.0.6533.90
    Safari: 17.5
  npmPackages:
    @vueuse/core: ^11.0.0-beta.2 => 11.0.0-beta.2 
    @vueuse/integrations: ^11.0.0-beta.2 => 11.0.0-beta.2
```...

---

## Top Comments

**@ilyaliao** [maintainer]:

Closed via #4140 #4130