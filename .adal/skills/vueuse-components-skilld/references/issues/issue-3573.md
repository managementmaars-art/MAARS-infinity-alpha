---
number: 3573
title: useDropZone not working on Mac OS
type: bug
state: open
created: 2023-11-20
url: "https://github.com/vueuse/vueuse/issues/3573"
reactions: 6
comments: 13
labels: "[bug]"
---

# useDropZone not working on Mac OS

### Describe the bug

On Mac OS you can only drop files from outside browser. My friend on Windows doesn't have any issues. I attach video of issue on Chrome. I tested that on all browsers (Chrome, Firefox), on Safari only SVG drag and drop works.

https://github.com/vueuse/vueuse/assets/27168276/129a8755-3ae4-4a8b-bbcf-9a7c063fbce8



### Reproduction

https://github.com/vueuse/vueuse/assets/27168276/129a8755-3ae4-4a8b-bbcf-9a7c063fbce8

### System Info

```Shell
System:
    OS: macOS 14.1.1
    CPU: (10) arm64 Apple M1 Max
    Memory: 3.90 GB / 32.00 GB
    Shell: 5.9 - /bin/zsh
  Binaries:
    Node: 18.17.1 - ~/.nvm/versions/node/v18.17.1/bin/node
    npm: 9.6.7 - ~/.nvm/versions/node/v18.17.1/bin/npm
  Browsers:
    Brave Browser: 116.1.57.64
    Chrome: 119.0.6045.159
    Safari: 17.1
    Firefox 119.0.1
```


### Used Package Manager

npm

### Validations

- [X] Follow our Code of Conduct
- [X] Read the Contributing Guidelines.
- [X] Read the docs.
- [X] Check that there isn't already an issue that reports the same bug to avoid creating a duplicate.
- [X] Make sure this is a VueUse issue and not a framework-specific issue. For example, if it's a Vue SFC related bug, it should likely be reported to https://github.com/vuejs/core instead.
- [X] Check that this is...