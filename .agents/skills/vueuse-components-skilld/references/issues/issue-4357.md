---
number: 4357
title: BUG | `useAxios` | Issue with useAxios when Calling execute Multiple Times
type: other
state: open
created: 2024-11-22
url: "https://github.com/vueuse/vueuse/issues/4357"
reactions: 3
comments: 4
labels: "[has pr]"
---

# BUG | `useAxios` | Issue with useAxios when Calling execute Multiple Times

### Describe the bug

When using useAxios from the VueUse library to make multiple HTTP requests, a common issue occurs when the execute method is called repeatedly in quick succession. The useAxios hook prioritizes the last request, but instead of returning a success response, it returns a cancel error for the last executed request.

This is problematic when you expect the final request to complete successfully, but it incorrectly throws an error due to cancellation, even though the request was actually executed and processed correctly.

<img width="559" alt="Screenshot 2024-11-23 at 03 21 00" src="https://github.com/user-attachments/assets/de5c2179-0bb0-431c-a058-986a1193bd17">
<img width="559" alt="Screenshot 2024-11-23 at 03 21 47" src="https://github.com/user-attachments/assets...