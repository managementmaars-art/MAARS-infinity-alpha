---
number: 4293
title: How to use onClickOutside and useTemplateRefs() from Vue 3.5?
category: Q&A
created: 2024-10-22
url: "https://github.com/vueuse/vueuse/discussions/4293"
upvotes: 1
comments: 2
answered: false
---

# How to use onClickOutside and useTemplateRefs() from Vue 3.5?

Vue's new useTemplateRefs() i is great. It brings a long more typesafetly and explicitness to the code.

However, I am fighting a bit with the new Type-Inference.

Example:

I am using a templateRef and declared it here it here:

```js
const overlayPanel = useTemplateRef<OverlayPanel>('overlayPanel')`
```

It simply references a custom OverlayPanel-Component:

```vue
<template>
    <OverlayPanel ref="overlayPanel" :dismissable="false" class="w-32 p-2">
       ...
    </OverlayPanel>
</template>
```

Now I want to leverage the onClickOutside() function from vueUse:

```js
onClickOutside(overlayPanel, () => overlayPanel.value?.hide(), {
    ignore: ['.p-overlaypanel'],
})

```...

---

## Top Comments

**@ilyaliao** [maintainer]:

You can use it like this

```ts
const overlayPanel = useTemplateRef<InstanceType<typeof OverlayPanel>>('overlayPanel')

onClickOutside(overlayPanel, () => {
  console.log('clicked outside')
})
```

refrence: https://vuejs.org/guide/typescript/composition-api.html#typing-component-template-refs

**@dosubot** (+1):


Hey there, @areindl! I'm a bot here to help you with bug fixes, questions, and contributions. Let's tackle this challenge together! 


To handle the type inference issue with `onClickOutside` and `useTemplateRef` in Vue 3.5, you can use type assertions to ensure compatibility with the expected `MaybeElementRef` type. Here's a possible approach:

1. **Type Assertion**: You can assert the type of `overlayPanel` to match `MaybeElementRef`. This is a common workaround when dealing with type mismatches in TypeScript.

...