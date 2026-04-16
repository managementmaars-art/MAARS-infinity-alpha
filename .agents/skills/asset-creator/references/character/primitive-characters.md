# Primitive Shape Characters

<style-reference>
> **Style:** Hey Duggee, Dumb Ways to Die, cute emoji mascots. Simple, clean, geometric, friendly.
</style-reference>

<character-structure>

| Component | Description | Position |
|-----------|-------------|----------|
| **Body** | ONE geometric shape OR symbolic object (square, circle, triangle, hexagon, basketball, apple, brain, heart, etc.) = head+torso combined | Center of canvas |
| **Eyes** | White ellipses (rx: 0.09×B, ry: 0.1×B) with black pupils (r: 0.04×B, offset +2%) | Upper third of body |
| **Cheeks** | Colored circles (r: 0.04×B) | Below eyes, inside body bounds |
| **Mouth** | Curved line or shape (width: 0.2×B), color: `#1a1a1a` | Lower third of body |

<key-points>
**Key points:**
- Body IS the head (no separate head, no neck)
- Body color should be vibrant, not muted
- Eyes: `white` with `#1a1a1a` pupils
- Symmetrical around center
</key-points>

</character-structure>

---

<before-drawing>
1. **Orientation?** (forward, left, right, 3/4) → shift eyes/pupils
2. **Emotion?** → affects face only (see [emotions.md](./emotions.md))
3. **Non-human?** (robots, animals) → same style, adapt structure as needed

> **KEEP IT CLEAN:** Minimalistic, uncluttered. Simple shapes, few details, no visual noise.

</before-drawing>

---

<constraints>

| ✅ ALLOWED | ❌ NOT ALLOWED |
|-----------|----------------|
| Any geometric body shape | New body parts (tails, wings, arms, legs) |
| Any color combination | Breaking/detaching body parts |
| Any facial emotion/expression | - |
| Eye blink animation | - |

</constraints>

<objects-and-props>
When a character needs to interact with or "hold" an object:
- Place the object on the **right side** of the character
- The object does NOT need to touch the character's body
- Characters do not literally hold objects (no arms/legs to hold with)
- Simply position the object near the character to show association

</objects-and-props>

---

<non-human-characters>

<non-human-rules>
**Non-Human Characters** (robots, animals, creatures):
- Use simple geometric shapes as base, or simple shapes
- Keep the same cute, friendly aesthetic
- Apply same face style: white eyes, black pupils, colored cheeks
- Maintain similar proportions and simplicity
- Make sure the viewbox is big enough to show the character
</non-human-rules>

<personified-objects>
**Personified Objects** (objects given personality, not actual characters):
- Keep the object's original form/shape
- ONLY add eyes and expressions
- Add whatever facial expressions are needed (eyes, cheeks, mouth)
- Do NOT restructure the object into a character body
- The object itself IS the body
</personified-objects>

</non-human-characters>

---

<core-rules>

<emotion-eye-animation>
**Emotion & Eye Animation (Required)**
**Every character MUST have:**
1. **A relevant emotion** - Choose expression based on scene context (happy, sad, angry, surprised, sleepy, etc.)
2. **Eye blinking animation** - All characters must include the clipPath-based eye blink (see [emotions.md](./emotions.md))

</emotion-eye-animation>

<scaling>
**Scaling**
- **Proportions are fixed** - all component ratios remain constant
- **Scale is flexible** - characters can be rendered at any size
- Use CSS/SVG transforms to scale, never distort individual parts

</scaling>

<colors>
**Colors**
- **Body** = vibrant color
- **Cheeks** = different colors as needed
- Use **brilliant, vibrant, deep** colors - avoid dull/muted tones
- Eyes: `white` with `#1a1a1a` pupils
- Mouth: `#1a1a1a`

</colors>

<constraints-summary>
**ALLOWED:**
- Any geometric shape or a symbolic/relevent object for body
- Any color combination
- Any emotion/expression
- Any animation (that maintains body integrity)

</constraints-summary>

<positioning-rules>
**All facial features (eyes, cheeks, mouth) MUST be inside the body shape.**
- For non-rectangular bodies (triangle, hexagon), calculate the body bounds at each y-level
- Cheeks must fit within the body width at their y-position
- Do NOT copy absolute positions from other characters - calculate relative to YOUR body shape

</positioning-rules>

<body-shapes>
**Body Shapes Must Be Equilateral/Regular**
- **Square**: Equal width and height
- **Triangle**: Equilateral (all sides equal)
- **Hexagon**: Regular hexagon (all sides equal)
- **Circle**: Already symmetric
- **Pentagon/Octagon/etc.**: Must be regular polygons

</body-shapes>

<proportions>
**Proportions (Ratios to Body Size):** Use these ratios to maintain proportions at any scale. `B` = body width/height.

| Component | Size | Position |
|-----------|------|----------|
| **Body** | B × B | Center of canvas |
| **Eyes** | rx: 0.09×B, ry: 0.1×B | Upper third of body |
| **Pupils** | r: 0.04×B | Offset +2% from eye center |
| **Cheeks** | r: 0.04×B | Below eyes, inside body |
| **Mouth** | Width: 0.2×B | Center, lower third of body |

<proportions-example>
**Example at different scales:**
- B=100: Eyes rx=9px
- B=200: Eyes rx=18px
- B=50: Eyes rx=4.5px
</proportions-example>

</proportions>

</core-rules>

---

<standard-specifications>
**ViewBox:** `0 0 250 250` (minimum 250×250, character must be centered)

**Important:** All characters must use a viewBox of at least 250×250. The character should be centered within the canvas with appropriate padding on all sides.

**Layer Order (SVG render order):**
1. **Body**
2. Eyes → Cheeks → Mouth

</standard-specifications>

---

<examples>
**Example: Orange Square**

```svg
<svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg"><rect x="45" y="45" width="160" height="160" fill="#e85d3b" rx="8"/><ellipse cx="95" cy="105" rx="15" ry="17" fill="#fff"/><ellipse cx="155" cy="105" rx="15" ry="17" fill="#fff"/><circle cx="99" cy="109" r="7" fill="#1a1a1a"/><circle cx="159" cy="109" r="7" fill="#1a1a1a"/><circle cx="70" cy="135" r="8" fill="#f9a825"/><circle cx="180" cy="135" r="8" fill="#f9a825"/><path d="M105 160q20 20 40 0" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="round"/></svg>
```

---

<example-hexagon>
**Example 2: Blue Hexagon (Sleepy)**

```svg
<svg viewBox="0 0 250 250" xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="a"><ellipse cx="95" cy="100" rx="15" ry="7"><animate attributeName="ry" values="7;7;0;0;7;7" keyTimes="0;0.35;0.37;0.63;0.65;1" dur="2s" repeatCount="indefinite"/></ellipse></clipPath><clipPath id="b"><ellipse cx="155" cy="100" rx="15" ry="7"><animate attributeName="ry" values="7;7;0;0;7;7" keyTimes="0;0.35;0.37;0.63;0.65;1" dur="2s" repeatCount="indefinite"/></ellipse></clipPath></defs><path fill="#2979ff" d="m125 35 75 35v110l-75 35-75-35V70z"/><ellipse cx="95" cy="100" rx="15" ry="7" fill="#fff"><animate attributeName="ry" values="7;7;0;0;7;7" keyTimes="0;0.35;0.37;0.63;0.65;1" dur="2s" repeatCount="indefinite"/></ellipse><circle cx="95" cy="100" r="5" fill="#1a1a1a" clip-path="url(#a)"/><ellipse cx="155" cy="100" rx="15" ry="7" fill="#fff"><animate attributeName="ry" values="7;7;0;0;7;7" keyTimes="0;0.35;0.37;0.63;0.65;1" dur="2s" repeatCount="indefinite"/></ellipse><circle cx="155" cy="100" r="5" fill="#1a1a1a" clip-path="url(#b)"/><path d="M80 110q15 6 30 0m35 0q15 6 30 0" stroke="#1e5ecc" stroke-width="2.5" fill="none"/><circle cx="75" cy="125" r="8" fill="#5c9eff"/><circle cx="175" cy="125" r="8" fill="#5c9eff"/><ellipse cx="125" cy="155" rx="18" ry="14" fill="#1a1a1a"/></svg>
```

</example-hexagon>

</examples>

<emotions-reference>
For character emotions and expressions, see [emotions.md](./emotions.md).

</emotions-reference>
