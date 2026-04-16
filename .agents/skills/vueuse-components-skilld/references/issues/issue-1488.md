---
number: 1488
title: Installing the nuxt3 version based on documentation fails due to 'Conflicting peer dependency'
type: other
state: closed
created: 2022-04-11
url: "https://github.com/vueuse/vueuse/issues/1488"
reactions: 12
comments: 23
---

# Installing the nuxt3 version based on documentation fails due to 'Conflicting peer dependency'

### Describe the bug

When Installing the Nuxt3 version based on documentation it fails due to a _'Conflicting peer dependency'._ This happens on a clean `npx nuxi init`


### logs
```
0 verbose cli [
0 verbose cli   '/Users/***/.nvm/versions/node/v16.13.0/bin/node',
0 verbose cli   '/Users/***/.nvm/versions/node/v16.13.0/bin/npm',
0 verbose cli   'i',
0 verbose cli   '-D',
0 verbose cli   '@vueuse/nuxt',
0 verbose cli   '@vueuse/core'
0 verbose cli ]
1 info using npm@8.5.2
2 info using node@v16.13.0
....
npm ERR! code ERESOLVE
npm ERR! ERESOLVE could not resolve
npm ERR!
npm ERR! While resolving: undefined@undefined
npm ERR! Found: vue@3.2.31
npm ERR! node_modules/vue
npm ERR!   peer vue@"3.2.31" from @nuxt/vite-builder@3.0.0-27494471.1091d45
npm ERR!   node_modules/@nuxt/vite-builder
npm ERR!     @nuxt/vite-builder@"npm:@nuxt/vite-builder-edge@3.0.0-27494471.1091d45" from nuxt3@3.0.0-27494471.1091d45
npm ERR!     node_modules/nuxt3
npm ERR!       dev nuxt3@"latest" from the root project
npm ERR!   peer vue@"^3.2.25" from @vitejs/plugin-vue@2.3.1
npm ERR!   node_modules/@vitejs/plugin-vue
npm ERR!     @vitejs/plugin-vue@"^2.3.1" from @nuxt/vite-builder@3.0.0-27494471.1091d45
npm ERR!     node_modules/@nuxt/vite-builder
npm ERR!       @nuxt/vite-builder@"npm:@nuxt/vite-builder-edge@3.0.0-27494471.1091d45" from nuxt3@3.0.0-27494471.1091d45
npm ERR!       node_modules/nuxt3
npm ERR!         dev nuxt3@"latest" from the root project
npm ERR!   4 more (@vue/server-renderer, @vueuse/head, nuxt3, vue-router)
npm ERR!
npm ERR! Could not resolve dependency:
npm ERR! dev @vueuse/core@"*" from the root project
npm ERR!
npm ERR! Conflicting peer dependency: vue@2.6.14
npm ERR! node_modules/vue
npm ERR!   peer vue@">= 2.5 < 3" from @vue/composition-api@1.4.9
npm ERR!   node_modules/@vue/composition-api
npm ERR!     peerOptional @vue/composition-api@"^1.1.0" from @vueuse/core@8.2.5
npm ERR!     node_modules/@vueuse/core
npm ERR!       dev @vueuse/core@"*" from the root project
npm ERR!
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --force, or --legacy-peer-deps
npm ERR! to accept an incorrect (and potentially broken) dependency resolution.
```...

---

## Top Comments

**@sidewinda** (+6):

Same issue here. Can't install it with Nuxt 3.

Node v18.1.0
NPM v8.10.0

...

**@vanling** (+3):

Update 2:
I installed an older npm version and now it seems to work
```
npm install npm@7.0 -g
rm -rf node_modules
npm install
```

Update 3:
Broken again: Created new folder, installed latest NPM again and did a fresh nuxt install etc
```
nvm install-latest-npm  
npx nuxi init testing
cd testing
npm install
npm i -D @vueuse/nuxt @vueuse/core
```

same errors
```
npm ERR! Could not resolve dependency:
npm ERR! dev @vueuse/core@"*" from the root project
npm ERR!
npm ERR! Conflicting peer dependency: vue@2.6.14
```

**@maxdzin** (+3):

The same for me.
I tried on a clean project of nuxt v3.0.0-rc1
The complete log:
...