# Shadows

## What Shadows Do

Shadows create the illusion of depth on a flat screen — they communicate that one element is *above* another.

> "Shadows are a fantastic tool to use on light mode."

**Important:** Shadows are primarily a **light mode** technique. In dark mode, use surface lightness instead (see [dark-mode.md](dark-mode.md)).

---

## The Most Common Mistake

> "This shadow, along with most, is too strong."

Most designers make shadows too strong by:
- Too much opacity
- Too little blur
- Too large a spread

**The fix:** Lower the opacity AND increase the blur radius.

---

## Shadow Strength by Elevation

Different elements need different shadow strengths:

| Element | Shadow Strength | Why |
|---------|----------------|-----|
| Cards on page | Very subtle | They barely lift off the background |
| Dropdowns / popovers | Medium | They float above page content |
| Modals | Stronger | They sit above everything else |
| Tooltips | Medium-strong | High elevation, small surface |
| Sticky nav | Subtle | Just a hint of separation |

> "Cards require less, while content that sits above other content — like popovers — will need stronger shadows."

---

## CSS Shadow Recipes

### Subtle Card Shadow (light mode)
```css
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
```

### Medium (dropdown/popover)
```css
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
```

### Strong (modal/dialog)
```css
box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15), 0 8px 16px rgba(0, 0, 0, 0.08);
```

### Inner Shadow (inset / pressed effect)
```css
box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.08);
```

---

## The Tactile / Raised Button Effect

> "We can even use these techniques with inner and outer shadows to create effects like raised tactile buttons."

Combine outer and inner shadows to simulate a physical button:

```css
/* Raised button */
box-shadow:
  0 2px 0px rgba(0, 0, 0, 0.25),        /* bottom shadow — simulates height */
  inset 0 1px 0 rgba(255, 255, 255, 0.1); /* top inner highlight — simulates light */
```

This creates a "pressed" version on :active by moving the outer shadow:
```css
/* Pressed state */
box-shadow:
  0 1px 0px rgba(0, 0, 0, 0.25),
  inset 0 1px 0 rgba(0, 0, 0, 0.1);
transform: translateY(1px);
```

---

## The Golden Rule of Shadows

> "If the shadow is the first thing you notice on a design, you're not using it right."

A good shadow is invisible in the sense that you notice the *depth*, not the shadow itself. It should be a background effect, not a design feature.

---

## Practical Rules

1. **Start with very low opacity** (4-12%) and increase only if needed
2. **More blur = softer, more realistic** — aim for 8-24px blur on cards
3. **Shadow color is almost always black** with low opacity, not a colored shadow
4. **Multiple layered shadows** look more natural than a single shadow
5. **Cards need the least shadow; modals need the most**
6. **Never use shadows in dark mode** — use surface elevation instead
7. **If a shadow looks strong in your design editor, it will look even stronger in browser** — err toward subtle

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **box-shadow** | CSS property for outer shadows on elements |
| **drop-shadow** | CSS filter alternative; follows element shape including transparency |
| **inset shadow** | box-shadow with `inset` keyword; shadow appears inside the element |
| **Shadow offset** | X and Y distance the shadow is shifted from the element |
| **Shadow blur** | How diffuse/soft the shadow edges are |
| **Shadow spread** | How much the shadow expands beyond the element's bounds |
| **Shadow opacity** | How transparent the shadow is; lower = more subtle |
| **Elevation** | The perceived z-height of an element; higher = stronger shadow |
| **Layered shadow** | Multiple box-shadow values stacked for realism |
| **Tactile button** | Button that uses shadows to simulate physical depth (raised/pressed) |
