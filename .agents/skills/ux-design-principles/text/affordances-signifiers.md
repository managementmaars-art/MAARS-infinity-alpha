# Affordances & Signifiers

## What Is an Affordance?

An **affordance** is what a UI element *can do* — what action it enables.
A **signifier** is how the UI *communicates* that affordance to the user.

> "Good UI has many signifiers... the UI was signifying how things worked."

---

## The Core Insight

You should never need to write instructions explaining how your UI works.
The design itself should teach the user.

### Classic Example from the Video

Three items: "Drinks", "Food", "Dessert"

| Visual Cue | What It Signifies |
|-----------|-------------------|
| Container around Drinks + Food | They are related; Dessert is not in this group |
| Highlighted container on Drinks | It is currently selected; you can toggle to Food |
| Grayed-out text on Dessert | It is inactive; clicking it probably won't do anything |

The user *knows* all of this instantly — without reading any instructions.

---

## Common Signifiers in UI

| Signifier | What It Communicates |
|-----------|----------------------|
| **Button press/active state** | This element is clickable |
| **Highlighted nav item** | Current active section |
| **Hover state** | Element responds to interaction |
| **Tooltip** | Additional info available; element has hidden functionality |
| **Grayed-out / reduced opacity** | Disabled; not currently actionable |
| **Container / card border** | Items inside are grouped |
| **Filled vs outlined icon** | Selected vs unselected |
| **Underlined text** | Clickable link |
| **Input border highlight (focus)** | Field is active and accepting input |
| **Red border on input** | Error state; something is wrong |

---

## Design Rule

> If a user has to pause and wonder "can I click this?" or "what does this do?" — you have failed the affordance test.

### Checklist
- [ ] Does every clickable element look clickable (hover state, cursor change)?
- [ ] Can a user tell at a glance what is selected vs not selected?
- [ ] Are disabled states visually distinct from active states?
- [ ] Do groupings communicate relationships (containers, proximity, indentation)?
- [ ] Are icons accompanied by labels or tooltips when their meaning is ambiguous?

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Affordance** | The potential action an element supports |
| **Signifier** | The visual cue communicating that affordance |
| **Ghost button** | Button with no background fill — signals secondary/optional action |
| **Disabled state** | Reduced opacity + no pointer events; communicates non-interactivity |
| **Focus ring** | Visible outline on focused form element; critical for keyboard accessibility |
| **Hover state** | Visual change on cursor enter — confirms clickability |
| **Active / pressed state** | Visual feedback during the moment of click |
| **Toggle** | Binary control where selection visually switches between two states |
