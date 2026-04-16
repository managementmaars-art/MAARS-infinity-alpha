---
number: 4085
title: Make API's of `useDropZone` and `useFileDialog` consistent
type: feature
state: open
created: 2024-07-08
url: "https://github.com/vueuse/vueuse/issues/4085"
reactions: 10
comments: 5
labels: "[enhancement, has workaround]"
---

# Make API's of `useDropZone` and `useFileDialog` consistent

### Clear and concise description of the problem

At the moment, there are two handy composables for dealing with file uploads:

* useFileDialog
* useDropZone

These come in handy when building a custom file upload component/dropzone, but often when you build such a component, you'll want to offer both "drag and drop" support, as well as "click to upload", to support different devices and user preferences.

So you end up having to use both of these composables in your component.

The challenge is however, that their API's are currently vastly different and incompatible, which results in a somewhat hacky solution requiring unnecessary computed refs and helper functions.

Some of the most notable discrepancies are:

1. `useDropZone` takes an `onDrop` handler as _input_ in the options, while `useFileDialog` _returns_ an `onChange` function in the return value. Moreover, the `files` passed to both of these are different. An array of `File` for `onDrop`, and `FileList` for `onChange`. The `onChange` handler also triggers immediately when the dialog is opened, with a `null` value, which is unexpected as no files have been selected yet.
2. `useDropZone` takes an array or function of `dataTypes`, whereas `useFileDialog` takes an `accept` string which allows wildcards. Moreover, the `dataTypes` option can be a Ref for `useDropZone`, but the `accept` option must be a string
3. `useFileDialog` accepts the `multiple` option to allow or disallow multiple file uploads, but `useDropZone` does not support this and it has to be implemented by the user.

### Suggested solution

I would propose the following changes to unify these API's:

1. Allow the `accept` option in `useFileDialog` to take a Ref
2. Allow the `accept` option in `useFileDialog` to take an array of data types, which can then be joined into a comma separated string for the `accept` property for the file input elemen...

---

## Top Comments

**@adamreisnz** (+13):

For anyone interested, here's a single custom composable that uses both `useFileDialog` and `useDropZone` together to handle file selection, and normalizes the output somewhat:

...

**@galexrt** (+3):

> I have one doubt about the type `UseFileSelectionOptions`. Is it defined in any existing package or should I define it by myself?

Ups, seems that I forgot to copy that in as well. I have updated my code snippet with the type.

**@galexrt** (+1):

> Thanks <img alt="" width="16" height="16" src="https://avatars.githubusercontent.com/u/3718398?s=64&amp;u=5825eda2f272031bcf5979b3c53cad5c5ebbfdbf&amp;v=4">@galexrt for the Typescript version

That reminds me that I wanted to post the code of the typescript version here instead of just the commit linking to the code.

So here's the typescript version of @adamreisnz code with some slight code style changes, ready to be copy'n'pasted (use/modify as you need):

...