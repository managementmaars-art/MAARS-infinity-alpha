---
number: 2043
title: computedDebounced
type: feature
state: closed
created: 2022-08-04
url: "https://github.com/vueuse/vueuse/issues/2043"
reactions: 22
comments: 5
labels: "[enhancement]"
---

# computedDebounced

### Clear and concise description of the problem

There are `refDebounced` and `watchDebounced`, but why not `computedDebounced`?

A computed that depends on other reactive state, but only updates after that other state has stopped changing for a certain time.

Maybe there is some way to use the existing function to achieve this, but I have trouble seeing it.

Note: In my current use-case, I actually only need the computed to fire on the next update, like watch with the option `{ flush: 'post' }`.

### Suggested solution

```
const preview = computedDebounced(() => generatePreview(props.inputText), 1000);
```

Essentially the same as:

```
const preview = ref('');

watchDebounced(() => props.inputText, () => {
  preview.value = generatePreview(props.inputText);
}, { debounce: 1000 });
```


### Alternative

_No response_

### Additional context

_No response_

### Validations

- [X] Follow our Code of Conduct
- [X] Read the Contributing Guidelines.
- [X] Read the docs.
- [X] Check that there isn't already an issue that request the same feature to avoid creating a duplicate.

---

## Top Comments

**@tripflex** (+11):

I agree with this, not sure why it was closed as stale there's 6 others who thumbed up for this 

**@vad1ym**:

+1, it would be nice to have this

Edit: Just found out about `refDebounced` + `toRef` + getter. Not sure how good it is, but it's much shorter than `watchDebounced` approach

```ts
const preview = refDebounced(toRef(() => generatePreview(props.inputText)), 1000);
```

**@chriscdn**:

I think `refDebounced` can be used with computed properties.