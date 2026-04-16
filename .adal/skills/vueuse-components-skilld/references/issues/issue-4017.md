---
number: 4017
title: useWebNotification emitting notification when mounted
type: docs
state: closed
created: 2024-06-04
url: "https://github.com/vueuse/vueuse/issues/4017"
reactions: 8
comments: 5
labels: "[documentation]"
---

# useWebNotification emitting notification when mounted

### Describe the bug

When the user already has notifications enabled, it emits two notifications (without body) when the component is mounted.

_Including that the error apparently occurs in the documentation itself_

### Reproduction

https://vueuse.org/core/useWebNotification

### System Info

```Shell
System:
    OS: Windows 11 10.0.22621
    CPU: (8) x64 Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz
    Memory: 1.94 GB / 15.84 GB
  Binaries:
    Node: 20.10.0 - C:\Program Files\nodejs\node.EXE
    npm: 10.2.3 - C:\Program Files\nodejs\npm.CMD
  Browsers:
    Edge: Chromium (123.0.2420.97)
    Internet Explorer: 11.0.22621.3527
  npmPackages:
    @vueuse/nuxt: ^10.10.0 => 10.10.0
    vue: ^3.4.21 => 3.4.27
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
- [X] Th...

---

## Top Comments

**@bblanchon** (+5):

I'm having the same issue, too.
Is anything preventing the PR from being merged?

**@9romise** [maintainer]:

Sorry, this was my mistake. This PR fixes the issue: #4019 . You can patch it in your registry to temporarily fix it.

**@oligety** (+1):

Hi @9romise , 
Is there any update on this pull request? This is holding us back from upgrading from 10.9.0 to newer versions. And we prefer not to patch this.