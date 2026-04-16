# AI Image Prompt Template Library

Comprehensive template library for AI image generation across Midjourney, Stable Diffusion, DALL-E, and other platforms.

## Table of Contents

1. [Basic Structure](#basic-structure)
2. [Universal Templates](#universal-templates)
3. [Category Templates](#category-templates)
4. [Real-World Examples](#real-world-examples)

---

## Basic Structure

### Standard Formula
```
[Subject] + [Environment] + [Style] + [Lighting] + [Composition] + [Quality]
```

### Example
```
an orange cat, sitting on a windowsill, watercolor style,
soft afternoon sunlight, side close-up, highly detailed, 8k
```

---

## Universal Templates

### Template 1: Basic Universal
```
[subject], [action/state], [environment], [style], [lighting], [composition], [quality]

Example:
a young woman, reading a book, in a cozy library, anime style,
warm lighting, medium shot, highly detailed, vibrant colors
```

### Template 2: Style-Focused
```
[subject] in the style of [artist/movement], [environment], [mood], [details]

Example:
a cyberpunk city in the style of Blade Runner, neon lights,
rainy night, dystopian atmosphere, cinematic, 8k
```

### Template 3: Photorealistic
```
[subject], [scene], shot on [camera model], [lens], [lighting], [post-processing]

Example:
a mountain landscape, golden hour, shot on Canon EOS R5,
24mm lens, natural lighting, HDR, professional photography
```

---

## Category Templates

### 🧑 Portrait Photography

#### Modern Portrait
```
a [age] [gender], [appearance features], [clothing], [expression], [background],
[style], [lighting], portrait photography, [quality]

Example:
a young Asian woman, long black hair, wearing casual white shirt,
gentle smile, urban background, natural style, soft lighting,
portrait photography, 4k, sharp focus
```

#### Fantasy Character
```
a [race/class] character, [features], [equipment], [pose], [environment],
fantasy art style, [atmosphere], detailed, concept art

Example:
an elven warrior, silver armor, holding a glowing sword,
standing pose, ancient forest, fantasy art style, mystical atmosphere,
highly detailed, concept art, trending on ArtStation
```

#### Cartoon/Anime Character
```
[character description], [style] style, [expression], [outfit], [background],
cute, colorful, [quality]

Example:
a cute robot character, Pixar style, happy expression,
wearing a red scarf, simple background, adorable, colorful,
3D render, high quality
```

---

### 🏞️ Landscape & Scenery

#### Natural Landscape
```
[location/feature], [time/season], [weather], [color mood],
landscape photography, [angle], [quality]

Example:
a serene mountain lake, sunrise, light fog, warm golden tones,
landscape photography, wide angle view, 8k, ultra realistic
```

#### Urban/Cityscape
```
[city/building], [time], [style], [atmosphere], [angle],
architectural photography, [quality]

Example:
Tokyo street at night, neon signs, cyberpunk style,
bustling atmosphere, street level view,
architectural photography, cinematic, 4k
```

#### Interior Scene
```
[room type], [design style], [lighting], [atmosphere], [details],
interior design, [quality]

Example:
a modern living room, Scandinavian style, natural daylight,
cozy atmosphere, plants and books, interior design,
photorealistic, high resolution
```

---

### 🎨 Concept Art & Illustration

#### Sci-Fi Scene
```
[subject], [tech elements], sci-fi, [atmosphere], [color palette],
concept art, [details], [quality]

Example:
a futuristic spaceship, advanced technology, sci-fi,
epic atmosphere, blue and purple tones, concept art,
highly detailed, trending on ArtStation, 8k
```

#### Fantasy World
```
[scene/creature], [magical elements], fantasy art, [atmosphere],
[art style], detailed, [quality]

Example:
a magical floating island, glowing crystals, fantasy art,
ethereal atmosphere, Studio Ghibli inspired, highly detailed,
beautiful colors, 4k
```

---

### 📦 Product & Objects

#### Product Photography
```
[product], [material], [background], product photography,
[lighting], [angle], commercial, [quality]

Example:
a luxury watch, stainless steel, white background,
product photography, studio lighting, 45-degree angle,
commercial quality, 8k, sharp focus
```

#### Food Photography
```
[food], [plating], [background], food photography,
[lighting], appetizing, [quality]

Example:
a gourmet burger, artistic plating, rustic wooden table,
food photography, natural lighting, mouth-watering,
professional, 4k, macro shot
```

---

### 🎭 Artistic Styles

#### Watercolor
```
[subject], watercolor painting, [color palette], soft edges,
paper texture, [mood], artistic

Example:
a field of flowers, watercolor painting, pastel colors,
soft edges, visible paper texture, peaceful mood, artistic
```

#### Oil Painting
```
[subject], oil painting, [artist style], thick brushstrokes,
[color palette], [era], museum quality

Example:
a portrait of an old man, oil painting, Rembrandt style,
thick brushstrokes, warm earth tones, Renaissance era,
museum quality
```

#### Pixel Art
```
[subject], pixel art, [colors], retro, 8-bit/16-bit style,
game art, clean pixels

Example:
a fantasy castle, pixel art, vibrant colors, retro,
16-bit style, game art, clean pixels, isometric view
```

---

## Real-World Examples

### Example 1: Mystical Forest
**Request:** Create a magical enchanted forest scene

**Prompt:**
```
A mystical enchanted forest, glowing mushrooms, fireflies,
ancient twisted trees, misty atmosphere, moonlight filtering through leaves,
fantasy art style, ethereal blue and purple tones,
highly detailed, magical ambiance, concept art,
trending on ArtStation, 8k --ar 16:9 --s 150
```

---

### Example 2: Cyberpunk Character
**Request:** Design a futuristic hacker character

**Prompt:**
```
A cyberpunk hacker, neon-lit face, wearing techwear jacket,
futuristic glasses with HUD display, standing in rainy Tokyo street,
neon signs reflection on wet ground, dramatic lighting,
cinematic portrait, Blade Runner atmosphere,
purple and cyan color palette, highly detailed,
digital art, 4k --ar 2:3
```

---

### Example 3: Product Showcase
**Request:** Coffee product marketing image

**Prompt:**
```
A premium coffee cup, steam rising, sitting on rustic wooden table,
coffee beans scattered around, morning sunlight from window,
shallow depth of field, warm color grading,
product photography, commercial quality,
soft shadows, cozy atmosphere, 4k, sharp focus --ar 4:5
```

---

## Advanced Techniques

### Weight Control (Midjourney)
```
(red flower)::2 (blue flower)::1
# Red flower weighted 2x more than blue

{cat|dog|bird}
# Random selection
```

### Multi-Concept Fusion
```
a fusion of [concept A] and [concept B]

Example:
a fusion of tiger and dragon, fantasy creature,
detailed scales and fur, majestic, concept art
```

### Artist References
```
in the style of [artist name]

Popular artists:
- Hayao Miyazaki - Whimsical fantasy
- Moebius - Sci-fi concepts
- Alphonse Mucha - Art Nouveau decorative
- Greg Rutkowski - Fantasy realism
- Artgerm - Modern illustration
```

### Negative Prompts
```
Common issues to avoid:
--no blurry, low quality, distorted, ugly, bad anatomy,
extra limbs, duplicate, watermark, text, signature

For portraits:
--no bad hands, bad face, asymmetric eyes, deformed fingers
```
