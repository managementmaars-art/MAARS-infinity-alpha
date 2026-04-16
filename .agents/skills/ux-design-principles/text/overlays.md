# Overlays

## What Is an Overlay?

An overlay is any translucent or opaque layer placed on top of an image (or content) to:
1. Make text readable over a complex background
2. Create depth and visual separation
3. Add aesthetic polish

> "Overlays are really important because if you screw them up, you're going to ruin the image and the text, too."

---

## The Three Approaches (Worst to Best)

### Approach 1: No Overlay (Worst)
Text directly on a complex/busy image.

**Problem:** Text is illegible — too much visual competition from the image.

### Approach 2: Full Opaque Overlay
A semi-transparent dark layer covering the entire image.

> "We could add in a full screen overlay, but it doesn't do the image justice."

**Problem:** Kills the image. The whole reason you used the image was its visual richness — a full overlay destroys that.

### Approach 3: Linear Gradient (Good)
A gradient from transparent at the top to a solid color at the bottom.

> "Instead, add in a linear gradient that'll display the image then smoothly convert into a text-readable background."

**Result:** Image shows fully at the top, fades gracefully to readable background at the bottom where text lives.

### Approach 4: Gradient + Progressive Blur (Best — "Extra Fancy")

> "If we're going for extra fancy, we can add in a progressive blur on top of the gradient for an even more modern look."

This combines:
1. **Linear gradient** (transparency control)
2. **Progressive blur** (increases as you go down — frosted glass effect)

The image transitions from crisp at top → blurry + dark at bottom → clear readable text.

---

## CSS Implementations

### Linear Gradient Overlay
```css
.card {
  position: relative;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    transparent 40%,
    rgba(0, 0, 0, 0.6) 70%,
    rgba(0, 0, 0, 0.85) 100%
  );
}

.card-text {
  position: absolute;
  bottom: 16px;
  left: 16px;
  color: white;
}
```

### Progressive Blur + Gradient (Modern)
```css
/* Using backdrop-filter with a mask */
.card-blur-overlay {
  position: absolute;
  inset: 0;
  /* Gradient mask to make blur apply only to bottom portion */
  -webkit-mask-image: linear-gradient(to bottom, transparent 40%, black 75%);
  mask-image: linear-gradient(to bottom, transparent 40%, black 75%);
  backdrop-filter: blur(12px);
}

/* Stack the gradient on top for color control */
.card-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 50%,
    rgba(0, 0, 0, 0.5) 100%
  );
}
```

---

## Other Overlay Contexts

Overlays appear in many contexts beyond image cards:

| Context | Treatment |
|---------|-----------|
| **Modal backdrop** | Solid or blurred overlay covering page content; `rgba(0,0,0,0.5)` or `backdrop-filter: blur(4px)` |
| **Sidebar overlay** | Semi-transparent on mobile to show page behind |
| **Tooltip** | No overlay; appears above content with shadow |
| **Drawer** | Backdrop overlay to focus attention on drawer |
| **Command palette (K-bar)** | Dark backdrop with strong blur or deep opacity |
| **Hero image** | Linear gradient from image to solid background color |
| **Video background** | Overlay to ensure UI text/buttons are legible |

---

## Gradient Direction Guide

| Text position | Gradient direction |
|--------------|-------------------|
| Text at bottom | `to bottom` (transparent top → dark bottom) |
| Text at top | `to top` (dark top → transparent bottom) |
| Text on left | `to left` (transparent right → dark left) |
| Text on right | `to right` |
| Full coverage (soft) | Radial gradient from center → edge |

---

## Practical Rules

1. **Never place text directly on a busy image** without an overlay
2. **Full opaque overlay kills the image** — avoid unless the image doesn't matter
3. **Linear gradient = best default** — lets the image show while making text readable
4. **Progressive blur = premium feel** — modern, editorial, worth the complexity
5. **Start gradient at 40-50%** — let the image breathe before darkening
6. **White text on gradient works universally** — no need to pick a text color
7. **Modal backdrops** use blur OR darkness, not both — pick one

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Overlay** | A layer positioned on top of content to modify its appearance |
| **Linear gradient** | A gradient that transitions along a straight line (top to bottom, etc.) |
| **Radial gradient** | A gradient that radiates outward from a center point |
| **Progressive blur** | Blur that increases in intensity across a gradient mask |
| **backdrop-filter** | CSS filter applied to content *behind* an element (blur, brightness) |
| **Frosted glass** | UI effect: blurred, semi-transparent surface; achieved with backdrop-filter |
| **mask-image** | CSS property that clips visibility using a gradient or image as a mask |
| **Modal backdrop** | Dark overlay behind a modal dialog that dims the background |
| **Scrim** | Design term for a translucent overlay that makes content more readable |
| **Vignette** | Darkening toward the edges of an image (radial gradient overlay) |
