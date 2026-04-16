---
number: 4105
title: "A snippet of code in \"useEventListener\" that confuses me"
category: Q&A
created: 2024-07-18
url: "https://github.com/vueuse/vueuse/discussions/4105"
upvotes: 1
comments: 2
answered: false
---

# A snippet of code in "useEventListener" that confuses me




I guess the target may change and it wants to cleanup the last event and register again. 
But what makes me confusing is that after excuted "unrefElement(target)" and it returns the result is not a reactive value, how can make the "watch" function trigger again?
Can anyone tell me the reason. thanks.


---

## Top Comments

**@ilyaliao** [maintainer]:

However, when you need to access an element in Vue, you would use `ref` or `useTemplateRef`. Therefore, when passing it to `useEventListener`, the target will be reactive.

**@dosubot**:


@YuinS316 Hello there! I'm here to help you with any issues or questions you have. Let's dive into the problem you're facing!


The `watch` function can trigger again after executing `unrefElement(target)` because it is set up to observe changes in the value returned by `unrefElement(target)`. If the result of `unrefElement(target)` changes, the `watch` function will re-execute.

...