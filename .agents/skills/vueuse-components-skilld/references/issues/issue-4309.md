---
number: 4309
title: Algolia search brings me to 404 half the time
type: docs
state: closed
created: 2024-10-29
url: "https://github.com/vueuse/vueuse/issues/4309"
reactions: 9
comments: 14
labels: "[documentation, has pr]"
---

# Algolia search brings me to 404 half the time

### Describe the bug

When I search for `usesc...` to find `useScrollLock`, i'm brought to a 404 page the first time I click the algolia result.
If I navigate home, and do the exact same search and click the exact same link, I am now brought to the correct documentation page without a 404.
First time:
<img width="1896" alt="Screenshot 2024-10-29 at 12 55 38 AM" src="https://github.com/user-attachments/assets/18e7f099-fdac-4f33-8286-50e7e3b4f277">
Second time:
<img width="1896" alt="Screenshot 2024-10-29 at 12 58 27 AM" src="https://github.com/user-attachments/assets/9d38bec9-91a6-4906-a49d-ed17025e9b44">


### Reproduction

.

### System Info

```Shell
System:
    OS: macOS 15.1
    CPU: (8) arm64 Apple M1 Pro
    Memory: 369.72 MB / 32.00 GB
    Shell: 5.9 - /bin/zsh
  Binaries:
    Node: 20.18.0 - ~/.nvm/versions/node/v20.18.0/bin/node
    Yarn: 1.22.19 - ~/.nvm/versions/node/v20.18.0/bin/yarn
    npm: 10.8.2 - ~/.nvm/versions/node/v20.18.0/bin/npm
    pnpm: 9.12.2 - ~/.nvm/versions/node/v20.18.0/bin/pnpm
  Browsers:
    Chrome: 130.0.6723.70
```


### Used Package Manager

npm

### Validations

- [X] Follow our Code of Conduct
- [X] Read the Contributing Guidelines.
- [X] Read the docs.
- [X] Check that there isn't already an issue that r...

---

## Top Comments

**@ilyaliao** [maintainer]:

> <img alt="" width="16" height="16" src="https://avatars.githubusercontent.com/u/93901409?u=2bbbdc5294449782b6acd9d57455863d56c7a174&amp;v=4&amp;size=80">@ilyaliao Idk if it's deployed, but I got the error just now with `useFocusWithin`
> 
> 

Maybe wait until v12.6.0 is released


**@mrleblanc101** (+1):

Might be related to the capitalization, the source link are in lowercase `https://vueuse.org/core/usescrolllock/#usescrolllock` but when you click it, you are redirected with uppercase in the URL like so`https://vueuse.org/core/useScrollLock/#usescrolllock`

**@ilyaliao** [maintainer]:

Hope this was resolved via #4526. If not, please reopen the issue.