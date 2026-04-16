---
number: 5276
title: Can't get pnpm dev working
category: Q&A
created: 2026-02-02
url: "https://github.com/vueuse/vueuse/discussions/5276"
upvotes: 1
comments: 3
answered: false
---

# Can't get pnpm dev working

Hello, I was trying to follow the 'Contributing' instructions. Such to make the change for this.

I have cloned the repo, I have pnpm installed. But running pnpm dev gives me this

...

---

## Top Comments

**@dosubot**:


Hi @imconfusednow! I'm Dosu and I’m helping the vueuse team.


The error about missing types means you need to run the build step before starting the dev server. On a fresh clone, the correct sequence is:  
1. `pnpm i`  
2. `pnpm build:packages`  
3. `pnpm dev`  
This builds all internal packages and generates the required type files. Skipping this step causes missing import errors and can break both the dev server and unit tests, so test failures are expected until you build first ([source](https://github.com/vueuse/vueuse/issues...

**@imconfusednow**:

Still the same after repeating those.

Current git sha: `fa483b4a79e9ca0fd34e94619f0f7dcb7ce4c0dc`

pnpm dev log

...

**@imconfusednow**:

Hello, I've done what the ai suggested, and tried starting from scratch to no avail.

Step 2, which I hadn't done before ran fine, but still exactly the same on step 3.