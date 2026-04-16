# Typography

## The Core Truth

> "Design is mostly just text."

Typography is arguably the most impactful design skill because nearly every interface is primarily composed of text.

---

## Font Selection

> "For picking a font, I can almost unilaterally say you'll never need more than one for any design. Find a nice sans-serif font and stick to it."

### The Rule: One Font

- Pick **one sans-serif font**
- Use **weight** and **size** to differentiate — not different typefaces
- Font selection should not be where you spend your time

### Recommended Sans-Serif Fonts (from the video)

These are broadly excellent choices used by professional designers:
- Inter
- Geist (Vercel's font)
- Plus Jakarta Sans
- DM Sans
- Manrope
- Outfit
- Figtree

> "Over the last 7 years of designing, I've rarely used any fonts other than what's on screen."

---

## Font Sizing Rules

### Landing Pages / Marketing Sites
- **Max 6 font sizes** across the entire design
- Range can be very wide (12px label → 72px+ hero headline)

| Role | Typical Size |
|------|-------------|
| Hero display | 56–80px |
| Section headline | 36–48px |
| Subheadline | 24–32px |
| Body text | 16–18px |
| Supporting text | 14px |
| Labels / captions | 12px |

### Dashboards & Data-Dense UIs
- **Tighter range** — typically nothing larger than 24px
- More text = more uniformity needed = narrower size spectrum

| Role | Typical Size |
|------|-------------|
| Page title | 20–24px |
| Section label | 16–18px |
| Body / data | 14px |
| Meta / caption | 12px |

> "For dashboards, that range shrinks dramatically to where you don't normally have text sizes larger than 24 pixels because of the increase in information density."

---

## The Pro Typography Trick (Letter Spacing + Line Height)

> "This one kind of is a hack... tighten up the letter spacing by about -2 to -3% and drop the line height to about 110 to 120%. It instantly makes any larger text look super pro real fast."

### For Large / Display Text

```css
/* Large headlines */
font-size: 56px;
letter-spacing: -0.02em;  /* -2% */
line-height: 1.1;          /* 110% */

/* Even tighter for very large text */
font-size: 72px;
letter-spacing: -0.03em;  /* -3% */
line-height: 1.05;         /* 105% */
```

### For Body Text
```css
font-size: 16px;
letter-spacing: 0;         /* no adjustment needed */
line-height: 1.5;          /* 150% - comfortable reading */
```

---

## Font Weight as Hierarchy

Within one font family, weights create hierarchy:

| Weight | Use |
|--------|-----|
| 300 (Light) | Large display text where weight would feel heavy |
| 400 (Regular) | Body text, labels |
| 500 (Medium) | Emphasized labels, nav items |
| 600 (SemiBold) | Card titles, section headers |
| 700 (Bold) | Primary headlines, key data points |
| 800–900 (ExtraBold/Black) | Hero display text, marketing punches |

---

## Practical Rules

1. **One typeface, multiple weights** — never mix two sans-serif fonts
2. **Max 6 font sizes** on any given page/screen
3. **Tighten large headlines** — -2 to -3% letter-spacing, 110-120% line-height
4. **Body line height 150%** — comfortable and readable
5. **Dashboard text** stays small and dense — nothing over 24px
6. **Marketing text** can go wild — huge display text creates drama

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Typeface** | A type family (e.g., Inter); contains all weights and styles |
| **Font** | A specific weight/style within a typeface (e.g., Inter Bold 700) |
| **Sans-serif** | Font without decorative strokes at letter ends; cleaner for screens |
| **Serif** | Font with decorative strokes; traditional, editorial feel |
| **Font weight** | Thickness of letterforms (100 thin to 900 black) |
| **Letter-spacing (tracking)** | Horizontal space between characters; negative = tighter |
| **Line-height (leading)** | Vertical space between lines; expressed as ratio or px |
| **Display text** | Very large text (56px+) used for headlines and heroes |
| **Body text** | Paragraph-length reading text, typically 16-18px |
| **Type scale** | The defined set of font sizes used in a design system |
| **Optical size** | How text appears visually vs its raw pixel size |
