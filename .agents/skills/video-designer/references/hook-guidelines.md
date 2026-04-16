# HOOK GUIDELINES - SCENE 0 ONLY

You have 1 second. ONE. The thumb is already moving to scroll. Stop it.

## SCENE 0 PURPOSE

**This is THE scroll-stopper. The make-or-break moment.**

- Scene 0 exists for ONE reason: grab attention and make them stay
- Every element placement must serve the message—if it doesn't convey meaning, cut it
- **VISUALS DO THE TALKING.** The image/icon/animation should explain the hook on its own
- Text is a last resort. If you need words to make the hook work, your visual isn't strong enough
- Ask yourself: "Does a viewer instantly GET IT from the visual alone?" If no, redesign.

---

## THE ONLY RULE THAT MATTERS

**THE MAIN VISUAL MUST EXPLODE ONTO THE SCREEN AND OWN IT.**

Not appear. Not fade in. EXPLODE.

---

## SCREEN DOMINATION

The hero element is NOT a part of the scene. It IS the scene.

- **Fill 70-80% of the screen** with your main visual. If it feels "too big", it's probably right.
- **Center of attention = Center of screen.** No subtlety. No "tasteful positioning off to the side."
- **Everything else is decoration.** Supporting elements exist only to make the hero look more powerful.
- If someone glances for 0.5 seconds, they MUST see your hero element. Nothing else matters.

---

## ANIMATION: VIOLENCE, NOT ELEGANCE

Forget smooth. Forget gentle. This is visual assault.

- **Frame 1: Something is already moving.** Not frame 30. Not after a pause. FRAME ONE.
- **Pop, slam, burst, punch.** These are your verbs. "Fade" and "ease" are banned.
- **Overshoot everything.** Scale to 120% then snap back to 100%. Every. Single. Time.
- **Stack animations.** While one thing lands, another launches. Zero dead frames.
- **Speed: 200-400ms max** for any entrance. If it takes longer, it's boring.

---

## TYPOGRAPHY THAT PUNCHES

If there's text, it better hit hard.

- **Massive font size.** If you can fit more than 5-6 words on screen, your text is too small.
- **CAPS LOCK IS YOUR FRIEND.** Key words scream, they don't whisper.
- **Thick stroke outlines.** Text must pop against ANY background.
- **Stagger word entrances.** Each word is its own event. Boom. Boom. Boom.
- **Weight: 800-900.** Anything lighter is invisible.

---

## TIMING: RELENTLESS MOTION

The first 2 seconds must feel like controlled chaos.

- **0-50ms:** First element HITS the screen
- **50-500ms:** 2-3 more elements join with overlapping animations
- **500-2000ms:** Continuous motion, pulses, settles, secondary animations
- **NEVER a static frame** in the first 2 seconds. If nothing's moving, you've failed.

---

## WHAT THIS IS NOT

This is NOT:
- Subtle
- Tasteful
- Balanced
- Minimalist
- "Letting the content breathe"

This IS:
- Aggressive
- Impossible to ignore
- Visually overwhelming (in a good way)
- The reason someone watches the next 58 seconds

---

## SPATIAL LAYOUT

**Visual groups get their own space. No group enters another's territory.**

**Step 1: Identify visual groups from Direction**
- A visual group = one visual concept (icon + its label + its effects)
- Elements that are described together = ONE group
- Elements that are described separately = SEPARATE groups

**Step 2: Position HERO GROUP first (70-80% of screen)**
- Hero is the largest/most important element
- Place it at or near screen center
- Calculate its bounds using element-bounds-calculation formulas

**Step 3: Position SECONDARY GROUPS in remaining space**
- Secondary groups go in the 20-30% NOT occupied by hero
- Calculate secondary group bounds
- Run collision check against hero bounds
- If overlap → move secondary group OUTSIDE hero bounds

**Step 4: Position STAT/LABEL elements**
- Stats/labels that describe an element should be ADJACENT to it, not ON it
- "Next to" means OUTSIDE the element's bounds, not inside
- Run collision check before finalizing

**COLLISION = FAIL: If any group overlaps another, reposition until no overlap.**

---

**Remember: You're not making art. You're stopping a scroll. Act like it.**
