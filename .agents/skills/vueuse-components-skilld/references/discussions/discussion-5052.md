---
number: 5052
title: BUG | `useMagicKeys` | Releasing held keys during a drag still show as being held during and after a drag
category: Q&A
created: 2025-09-04
url: "https://github.com/vueuse/vueuse/discussions/5052"
upvotes: 1
comments: 2
answered: true
---

# BUG | `useMagicKeys` | Releasing held keys during a drag still show as being held during and after a drag

I have modified the useMagicKeys example from the documentation by adding a div with `draggable="true"`. See replication link below

1. Hold Shift (any key)
2. Press Mouse down on "Drag Me" element
3. Release Shift
4. Release Mouse down
5. Notice that useMagicKeys still shows Shift as being pressed.
6. Notice other keys pressed after this work as expected
7. Pressing Shift again and releasing "resets" this bug and shows it as unpressed once again

https://github.com/user-attachments/assets/0951ae48-dd7e-4674-8045-8f461c1de996

...

---

## Accepted Answer

**@9romise** [maintainer]:

According to the WHATWG HTML Standard, input events are suppressed during drag-and-drop:

> From the moment that the user agent is to **initiate the drag-and-drop operation**, until the end of the drag-and-drop operation, device input events (e.g. mouse and keyboard events) must be suppressed.

So it seems there isn’t much we can do here.