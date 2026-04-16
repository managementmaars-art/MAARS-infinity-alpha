---
number: 3240
title: Argument of type 'Ref<null>' is not assignable to parameter of type 'MaybeElementRef<MaybeElement>'.
type: other
state: closed
created: 2023-07-19
url: "https://github.com/vueuse/vueuse/issues/3240"
reactions: 10
comments: 22
labels: "[need more info, vue: upstream]"
---

# Argument of type 'Ref<null>' is not assignable to parameter of type 'MaybeElementRef<MaybeElement>'.

### Describe the bug

What is the cause of this problem? How to solve it?

```
Argument of type 'Ref<null>' is not assignable to parameter of type 'MaybeElementRef<MaybeElement>'.
  Property '[RefSymbol]' is missing in type 'Ref<null>' but required in type 'Ref<MaybeElement>'.ts(2345)
reactivity.d.ts(458, 5): '[RefSymbol]' is declared here.
```



code

```tsx
import { onClickOutside } from '@vueuse/core';

const target = ref(null);
onClickOutside(target, () => {
  isShowCandidate.value = false;
});

return () => (
  <div ref={target}></div>
);
```

package.json

```json
  "dependencies": {
    "@vueuse/components": "^10.2.1",
    "@vueuse/core": "^9.13.0",
    "vue": "3.2.47",
  },
```

Ref

Solved without doing anything? https://github.com/vueuse/vueuse/issues/405 

### Reproduction

https://stackblitz.com/

### System Info

```Shell
System:
    OS: macOS 13.4.1
    CPU: (8) arm64 Apple M1
    Memory: 106.36 MB / 8.00 GB
    Shell: 5.9 - /bin/zsh
  Binaries:
    Node: 16.20.0 - ~/.nvm/versions/node/v16.20.0/bin/node
    Yarn: 1.22.19 - ~/.nvm/versions/node/v16.20.0/bin/yarn
    npm: 8.19.4 - ~/.nvm/versions/node/v16.20.0/bin/npm
  Browsers:
    Chrome: 114.0.5735.198
    Firefox: 114.0.1
    Safari: 16.5.2
  npmPackages:
    @vueuse/core: ^9.13.0 => 9.13.0
```


### Used Package Manager

pnpm

### Validations

...

---

## Top Comments

**@roydukkey** (+3):

> The problem is solved

@rich1e How?

I don't count this much has a solution.

```
onClickOutside(target as unknown as MaybeElementRef<MaybeElement>, () => {
```

**@roydukkey** (+3):

I'm seeing this issue too when trying to upgrade my library to vue 3.3.

...

**@rich1e** (+6):

I think it should be necessary to clarify this question, because I am not the only one who has questions.