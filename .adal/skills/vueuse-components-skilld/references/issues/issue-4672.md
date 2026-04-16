---
number: 4672
title: BUG | `useDevicesList` | Doesn't list devices after reload in Firefox
type: bug
state: open
created: 2025-03-21
url: "https://github.com/vueuse/vueuse/issues/4672"
reactions: 2
comments: 0
labels: "[bug, has pr]"
---

# BUG | `useDevicesList` | Doesn't list devices after reload in Firefox

### Describe the bug

Currently, the `useDevicesList` function doesn't load the devices correctly after the page is reloaded. This only happens in Firefox.

Can be reproduced by going to the docs page in Firefox, granting access to the devices (devices should now be listed correctly) and then refreshing the page. We now get only 1 available, but empty, device and not the actual available devices.

The problem seems to lie in the fact that Firefox needs an active mediastream to enumerate the devices (described here). A fix for this seems to have been put in previously, but this will only work when the user hasn't given perm...