---
number: 5001
title: BUG | Directives aren't cleaned up when component unmounts
type: bug
state: open
created: 2025-08-29
url: "https://github.com/vueuse/vueuse/issues/5001"
reactions: 1
comments: 7
labels: "[bug]"
---

# BUG | Directives aren't cleaned up when component unmounts

### Describe the bug

**Reproduction steps:**
1. Go to minimal repro
2. Open Dev Tools to see console.log prints
3. Press "Toggle component". 
4. Move mouse and notice that mouse coordinates are printed.
5. Press "Toggle component" again to unmount component and move mouse.

**Expected:**
Mouse coordinate logs stop printing.

**Actual:**
Mouse coordinates continue to print after component is unmounted.

I was looking at how directives are implemented in VueUse and noticed that these aren't cleaned when component unmounts.

...