---
number: 4547
title: completely stop active dragging (useDraggable)
category: Q&A
created: 2025-01-28
url: "https://github.com/vueuse/vueuse/discussions/4547"
upvotes: 1
comments: 2
answered: false
---

# completely stop active dragging (useDraggable)

Have a project where I'm using useDraggable to be allow to drag and drop items in a list to reorder. I wanted to be able to cancel any active dragging by clicking `esc`. So far the only think I could think of is to add some sort of control variable and check in the callbacks, like

```vue
let escPressed = false

// or useKeystroke, or wtv
window.addEventListener("keydown", () => escPressed=true)


userDraggable((
   ...
   onEnter() { 
       // reset escPressed
      escPressed = false
       ....
   },
   onMove(){
      if (escPressed){ 
         return
      }
   }
   onEnd(){
      if (escPressed){ 
         return
      }
   }
```
but I _really_ dislike this option, as it doesn't really stop any dragging, just pretends it's not doing it. Anyone has better i...

---

## Top Comments

**@ilyaliao** [maintainer]:

Maybe you can stop it by using`disabled`.

```
const disabled = ref(false);
const { x, y, style } = useDraggable(el, {
  initialValue: { x: innerWidth / 4.2, y: 80 },
  preventDefault: true,
  disabled,
});

onKeyStroke('Escape', (e) => {
  e.preventDefault();
  disabled.value = true;
})
```

https://stackblitz.com/edit/vitejs-vite-ukacrkjy?file=src%2FApp.vue

**@dosubot**:


Hey @Ribeiro-Tiago! I'm Dosu, a bot here to help you with bug fixes, questions, and contributions. Let me know how I can assist you today!


The `useDraggable` function in vueuse does not provide a built-in method to programmatically cancel or stop an active drag operation. However, you can achieve the desired behavior by manually triggering the `onEnd` callback when the `Esc` key is pressed. Here's a refined approach:

1. Use an event listener to detect the `Esc` key press.
2. Manually call the `onEnd` function to stop the drag operation.

...