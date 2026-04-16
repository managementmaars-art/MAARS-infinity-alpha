---
number: 5055
title: @vueuse/nuxt peerDependency should support Nuxt 4
category: Q&A
created: 2025-09-21
url: "https://github.com/vueuse/vueuse/discussions/5055"
upvotes: 1
comments: 1
answered: true
---

# @vueuse/nuxt peerDependency should support Nuxt 4

### Describe the bug

### Describe the bug

Installing `@vueuse/nuxt@10.11.1` in a project using **Nuxt 4.1.2** fails due to a peer dependency conflict.  
The package declares:

```json
"peerDependencies": {
  "nuxt": "^3.0.0"
}


### Reproduction

Initialize a fresh Nuxt 4 project (`nuxt@4.1.2`) and install `@vueuse/nuxt@10.11.1`. The install fails with a peer dependency conflict because `@vueuse/nuxt` requires `nuxt@^3.0.0`.

### System Info

```Shell
System:
    OS: Windows 11 10.0.26100
    CPU: (12) x64 11th Gen Intel(R) Core(TM) i5-11400F @ 2.60GHz
    Memory: 15.96 GB / 31.87 GB
  Binaries:
    Node: 22.12.0 - C:\nvm4w\nodejs\node.EXE
    npm: 10.9.0 - C:\nvm4w\nodejs\npm.CMD
    pnpm: 10.11.0 - ~\AppData\Local\pnpm\pnpm.CMD
    bun: 1.2.14 - ~\AppData\Roaming\npm\bun.CMD
  Browsers...

---

## Accepted Answer

**@9romise** [maintainer]:

The latest release already supports `Nuxt 4`. Is there a specific reason you‘re using version `v10.11.1`?