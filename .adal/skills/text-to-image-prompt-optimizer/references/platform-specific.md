# Platform-Specific Guide

Detailed guidance for different AI image generation platforms.

## Table of Contents

1. [Midjourney](#midjourney)
2. [Stable Diffusion](#stable-diffusion)
3. [DALL-E](#dall-e)
4. [Leonardo.ai](#leonardoai)
5. [Google Gemini (Nano Banana)](#google-gemini-nano-banana)
6. [Platform Comparison](#platform-comparison)

---

## Midjourney

### Key Characteristics
- Best for artistic, stylized images
- Excellent at understanding natural language
- Strong default aesthetics
- Great for concept art and illustrations

### Parameters

#### Aspect Ratio (--ar)
```
--ar 16:9    # Widescreen landscape
--ar 1:1     # Square (default)
--ar 9:16    # Portrait/vertical
--ar 2:3     # Standard portrait
--ar 3:2     # Standard landscape
--ar 4:5     # Social media portrait
```

#### Stylization (--s)
Controls how artistic vs literal the output is
```
--s 0        # More literal, photographic
--s 50       # Balanced
--s 100      # Default, good balance
--s 250      # More artistic
--s 750      # Very artistic/stylized
--s 1000     # Maximum stylization
```

#### Quality (--q)
Affects rendering time and detail
```
--q 0.25     # Quarter quality, fastest
--q 0.5      # Half quality, faster
--q 1        # Default quality
--q 2        # Double quality, more details
```

#### Chaos (--c)
Controls variation/creativity
```
--c 0        # Very consistent
--c 25       # Slightly varied
--c 50       # Moderately varied
--c 100      # Maximum variation
```

#### Version (--v)
```
--v 6        # Latest version (default)
--v 5.2      # Previous version
--v 5        # Older version
```

#### Style Options
```
--style raw        # More photographic, less processed
--style 4a         # Midjourney v4 aesthetic
--style 4b         # Alternative v4 aesthetic
--style 4c         # Another v4 variation
```

#### Other Useful Parameters
```
--no [things]      # Negative prompt (exclude elements)
--no people, text, watermark

--tile             # Creates tileable patterns
--video            # Generates creation video
--repeat 4         # Generate 4 variations at once
--stop 50          # Stop generation at 50% (experimental looks)
```

### Weight Control
```
(element)::2       # Double weight
(element)::0.5     # Half weight
(red flower)::2 (blue flower)::1  # Red emphasized

{option1|option2}  # Random choice between options
{cat|dog|bird}     # Will pick one randomly
```

### Multi-Prompts
```
hot:: dog         # "hot" and "dog" separately
hot::2 dog::1     # "hot" weighted higher

ancient::1 city::1 ::0.5  # Ancient city with reduced overall weight
```

### Best Practices for Midjourney

1. **Start Simple**: Begin with clear, concise descriptions
2. **Use Artist References**: "in the style of [artist]" works very well
3. **Order Matters**: Most important elements first
4. **Balance Specificity**: Too specific can confuse, too vague gives random results
5. **Iterate with Variations**: Use V1-V4 buttons to refine
6. **Remix for Changes**: Use Remix mode for controlled variations

### Example Prompts
```
Epic fantasy castle on a floating island, dramatic sunset,
volumetric clouds, fantasy art style, highly detailed,
cinematic lighting, trending on ArtStation --ar 16:9 --s 150 --q 2

Minimalist product photography, modern smartphone,
clean white background, studio lighting, professional,
commercial quality, centered composition --ar 4:5 --style raw

Portrait of a cyberpunk street samurai, neon-lit rain,
dramatic lighting, Blade Runner atmosphere, highly detailed,
digital art, cinematic --ar 2:3 --s 100
```

---

## Stable Diffusion

### Key Characteristics
- Most customizable and flexible
- Runs locally (free, but needs GPU)
- Extensive model ecosystem
- Precise control through settings

### Core Settings

#### Sampling Steps
Number of iterations for image generation
```
20-30 steps:  Fast, good for testing
30-50 steps:  Balanced quality/speed
50-80 steps:  High quality
100+ steps:   Diminishing returns, very slow
```

#### CFG Scale (Classifier Free Guidance)
How closely to follow the prompt
```
1-5:    Ignores prompt, more creative
7-12:   Balanced, recommended range
15-20:  Very strict prompt adherence
20+:    Over-fitted, artifacts likely
```

#### Sampler Selection
Different algorithms for image generation
```
Popular choices:
- DPM++ 2M Karras     # Fast, high quality
- Euler a             # Good for artistic styles
- DPM++ SDE Karras    # Detailed, slower
- DDIM                # Consistent results
- UniPC               # Very fast
```

#### Denoising Strength (for img2img)
How much to change the source image
```
0.3-0.5:  Minor changes, keep original
0.5-0.7:  Balanced transformation
0.7-0.9:  Major changes
0.9-1.0:  Almost completely new image
```

### Negative Prompts

Essential for quality in Stable Diffusion

**Universal Negative Prompt:**
```
ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face,
out of frame, extra limbs, disfigured, deformed, body out of frame,
bad anatomy, watermark, signature, cut off, low contrast, underexposed,
overexposed, bad art, beginner, amateur, distorted face, blurry, draft,
grainy
```

**For Portraits:**
```
bad hands, bad anatomy, bad proportions, deformed, mutated hands,
fused fingers, too many fingers, bad face, asymmetric eyes,
crossed eyes, lazy eye, long neck
```

**For Photorealistic:**
```
painting, illustration, drawing, art, sketch, cartoon, anime,
render, 3d, unrealistic, fake, CG
```

**For Specific Issues:**
```
text, watermark, signature, logo, copyright, artist name
```

### Prompt Structure for SD

More structured than Midjourney, benefits from specificity

```
[Main subject], [detailed description], [setting/background],
[lighting], [style], [quality markers]

Negative: [things to avoid]
```

### Models & LoRAs

**Base Models:**
- SD 1.5: Original, wide compatibility
- SD 2.1: Improved quality
- SDXL: Latest, best quality
- Realistic Vision: Photorealistic
- DreamShaper: Artistic/fantasy

**Using LoRAs:**
LoRAs are add-ons that specialize in specific styles/subjects
```
<lora:style_name:0.7>  # Trigger LoRA at 0.7 strength
```

### Best Practices for Stable Diffusion

1. **Always Use Negative Prompts**: Critical for quality
2. **Test Settings**: CFG and steps significantly affect output
3. **Use Appropriate Models**: Match model to your goal
4. **Embeddings Help**: Use quality embeddings like EasyNegative
5. **Img2img for Refinement**: Generate, then refine with img2img

### Example Prompts

```
Positive:
masterpiece, best quality, highly detailed, 8k uhd, professional photography,
a young woman with long flowing hair, wearing an elegant red dress,
standing in a field of golden wheat, sunset lighting, warm colors,
shallow depth of field, bokeh, cinematic, photorealistic

Negative:
ugly, blurry, low quality, distorted, bad anatomy, watermark, signature,
text, bad hands, extra fingers, deformed

Settings: Steps: 30, CFG: 7, Sampler: DPM++ 2M Karras
```

---

## DALL-E

### Key Characteristics
- Best natural language understanding
- Strong safety filters
- No fine-grained control
- Consistent, reliable results

### Approach for DALL-E

**Natural Language Focus:**
DALL-E works best with descriptive, natural sentences rather than keyword lists.

```
Good for DALL-E:
"A photograph of a cozy coffee shop interior with vintage furniture,
warm lighting from Edison bulbs, customers reading books, plants on shelves,
shot in the style of lifestyle magazine photography"

Less optimal:
"coffee shop, vintage, warm lighting, customers, books, plants,
professional photography, 4k"
```

### Best Practices

1. **Write Natural Descriptions**: Full sentences work better
2. **Be Specific**: Detailed descriptions yield better results
3. **Avoid Technical Jargon**: No need for camera settings or CFG
4. **Safety Guidelines**: Avoid restricted content
5. **Iterations Matter**: Regenerate for variations

### Example Prompts

```
A serene landscape painting showing a mountain lake at sunrise,
with mist rolling over the water and pine trees in the foreground.
The style should be realistic with soft, warm colors and
peaceful atmosphere.

An isometric view of a tiny fantasy village built into a giant mushroom,
with wooden bridges connecting different levels, glowing windows,
and tiny people going about their daily activities. The art style
should be colorful and whimsical, like a children's book illustration.
```

---

## Leonardo.ai

### Key Characteristics
- Great web interface
- Good balance of control and ease
- Strong model selection
- Alchemy feature for quality boost

### Key Features

#### Alchemy Mode
Enhanced quality with additional processing
```
ON:  Better details, more refined
OFF: Faster, standard quality
```

#### PhotoReal Mode
Specialized for photorealistic images
```
Use when: Creating realistic photos, portraits, products
Skip when: Artistic, illustrated, or stylized images
```

#### Prompt Magic Strength
How much to enhance/interpret your prompt
```
Low:    Literal interpretation
Medium: Balanced enhancement
High:   Creative interpretation
```

### Best Practices

1. **Use Preset Models**: Platform optimized models work great
2. **Alchemy for Finals**: Test without, finalize with Alchemy
3. **Negative Prompts Help**: Like SD, they improve quality
4. **Guidance Scale**: 7-12 works well (similar to SD CFG)

---

## Platform Comparison

### Quick Reference Table

| Feature | Midjourney | Stable Diffusion | DALL-E | Leonardo.ai | Gemini |
|---------|-----------|-----------------|--------|-------------|---------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Artistic Style** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Photorealism** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Control** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Character Consistency** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Image Editing** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | Subscription | Free (local) | Pay-per-use | Freemium | Freemium |
| **Speed** | Fast | Varies | Fast | Fast | Fast |

### When to Use Each Platform

**Use Midjourney when:**
- Creating concept art or illustrations
- You want artistic, stylized results
- You prefer simple prompts
- You value community and inspiration

**Use Stable Diffusion when:**
- You need maximum control
- Running locally (privacy, unlimited use)
- You want specific styles (via models/LoRAs)
- You're technical and enjoy tweaking

**Use DALL-E when:**
- You want reliable, consistent results
- Natural language prompts are preferred
- You need safe, appropriate content
- Quick iterations are important

**Use Leonardo.ai when:**
- You want a balance of control and ease
- You need both artistic and photorealistic
- You prefer web-based tools
- You want curated model selection

**Use Google Gemini when:**
- You need character consistency across multiple images
- You want conversational, iterative editing
- You're working on multi-image composition projects
- You need precise text rendering in images (Pro model)
- You prefer natural language over technical parameters
- You want integrated generation and editing in one place

### Cross-Platform Prompt Adaptation

**Original Midjourney Prompt:**
```
a cyberpunk city street, neon signs, rain, dramatic lighting,
cinematic, highly detailed --ar 16:9 --s 150
```

**Adapted for Stable Diffusion:**
```
Positive: masterpiece, best quality, highly detailed, 8k,
a futuristic cyberpunk city street at night, numerous neon signs,
heavy rain falling, wet reflective pavement, dramatic volumetric lighting,
cinematic composition, photorealistic, moody atmosphere

Negative: ugly, blurry, low quality, distorted, bad composition,
overexposed, underexposed, amateur

Settings: CFG 7-9, Steps 30-40, Aspect 16:9
```

**Adapted for DALL-E:**
```
A dramatic photograph of a cyberpunk city street on a rainy night.
The scene features numerous glowing neon signs reflecting off the wet pavement,
with heavy rain visible in the volumetric lighting. The composition is cinematic
with high attention to detail and moody atmosphere. Shot in 16:9 aspect ratio.
```

**Adapted for Leonardo.ai:**
```
Cyberpunk city street at night, heavy rain, neon signs everywhere,
wet reflective ground, dramatic lighting, cinematic mood, highly detailed

Negative: blurry, low quality, amateur

Settings: Alchemy ON, Guidance 8, PhotoReal OFF, 16:9
```

**Adapted for Google Gemini:**
```
Create a cinematic photograph of a futuristic cyberpunk city street on a rainy night.
The scene should show numerous glowing neon signs and holographic advertisements
reflecting beautifully off the wet pavement. Heavy rain should be visible with
dramatic volumetric lighting creating atmospheric depth. Use a wide-angle street-level
perspective to capture the towering buildings and bustling atmosphere. The color
palette should emphasize vibrant neon blues, purples, and pinks contrasting with
dark shadows. The mood should be cinematic and moody with high attention to detail.
Render in 16:9 widescreen format.
```

---

## Google Gemini (Nano Banana)

### Key Characteristics
- Google's native AI image generation and editing
- Conversational interface integrated into Gemini app, AI Studio, and Vertex AI
- Strong at character consistency across multiple generations
- Excellent for photo editing and multi-image composition
- Two models: Nano Banana (fast) and Nano Banana Pro (professional)

### Models

#### Nano Banana
- Designed for speed and efficiency
- Optimized for high-volume, low-latency tasks
- Good for quick iterations and testing
- Best for simple to moderate complexity images

#### Nano Banana Pro
- Designed for professional asset production
- Utilizes advanced reasoning ("Thinking") capabilities
- Follows complex instructions more accurately
- Renders high-fidelity text in images
- Best for polished, final outputs

### Prompt Structure for Gemini

Gemini works best with **clear, conversational prompts** rather than keyword lists.

#### Basic Formula
```
Create/Generate an image of [subject] [action] [scene]
```

Then build from there with:
- Subject: What is the main focus
- Composition: How elements are arranged
- Action: What is happening
- Location: Where the scene takes place
- Style: Visual aesthetic
- Editing instructions: Specific modifications

#### Example Progression

**Simple:**
```
Create an image of a cat napping in a sunbeam on a windowsill.
```

**Detailed:**
```
Create an image of an orange tabby cat napping peacefully in a warm sunbeam
on a wooden windowsill. The scene is cozy and domestic, with soft natural
lighting streaming through lace curtains. The style should be photorealistic
with warm, gentle tones.
```

**Professional (for Nano Banana Pro):**
```
Generate a professional editorial photograph of an orange tabby cat sleeping
on a rustic wooden windowsill bathed in golden afternoon sunlight. Use an
85mm portrait lens perspective with shallow depth of field to blur the
background. The composition should follow the rule of thirds, with soft,
diffused natural lighting. Render in warm, inviting tones suitable for a
lifestyle magazine spread.
```

### Key Prompting Techniques

#### Use Photographic/Cinematic Language
Gemini responds very well to photography and cinematography terms:

```
Composition Terms:
- wide-angle shot
- macro shot / close-up
- low-angle perspective / high-angle shot
- 85mm portrait lens / 24mm wide lens
- Dutch angle (tilted)
- bird's eye view
- over the shoulder

Lighting Terms:
- golden hour lighting
- studio lighting / soft box
- rim lighting / backlighting
- dramatic shadows
- natural window light
```

#### Clear Intent Over Long Instructions
**Better:** "A deserted street at dawn with no people or vehicles"
**Not:** "A street, no cars, no people, empty, quiet"

The key is to describe what you WANT, not what you don't want.

#### Semantic Negative Prompts
Instead of listing what to avoid, describe the positive alternative:

**Instead of:** "no cars, no traffic"
**Use:** "an empty, peaceful street with no signs of activity"

**Instead of:** "not blurry, not low quality"
**Use:** "sharp focus, crystal clear, professional quality"

### Unique Capabilities

#### 1. Character Consistency
Gemini excels at maintaining the same character across multiple images:

```
First image:
"Generate a character: a young woman with short purple hair,
wearing round glasses and a green jacket"

Follow-up images:
"Show the same character now sitting in a coffee shop"
"Show the same character walking in the rain with an umbrella"
"Show the same character in anime style"
```

Gemini will maintain the character's likeness across different poses, lighting, and even styles.

#### 2. Conversational Editing
You can iterate on images conversationally:

```
Initial: "Create a product photo of a coffee mug on a wooden table"

Edits:
"Make the background darker"
"Add steam rising from the mug"
"Change the mug color to blue"
"Add morning sunlight from the left"
```

Each edit builds on the previous image.

#### 3. Multi-Image Composition
Use multiple images as references:

```
"Combine the character from Image A with the background from Image B"
"Apply the art style from this reference image to my photo"
"Place the object from this image into that environment"
```

### Best Practices for Gemini

1. **Be Conversational**: Write naturally, like you're describing to a person
2. **Be Specific About Details**: Mention lighting, clothing, background, pose
3. **Use Visual References**: Specify styles (editorial, cinematic, Polaroid, fantasy, 3D)
4. **Iterate Naturally**: Make incremental changes through conversation
5. **Leverage Photography Terms**: Control composition with camera/lens language
6. **Choose the Right Model**:
   - Use Nano Banana for quick iterations
   - Use Nano Banana Pro for final, polished work

### Example Prompts for Gemini

#### Portrait Photography
```
Generate a professional headshot of a business executive in their 40s.
Use natural window lighting from the left side creating soft shadows.
The background should be a modern office setting, slightly out of focus.
Shot with an 85mm portrait lens at f/1.8 for shallow depth of field.
The mood should be confident and approachable.
```

#### Product Photography
```
Create a commercial product photo of a luxury watch on a marble surface.
Use studio lighting with a key light from the upper right and a subtle
fill light to reduce shadows. The watch should be positioned at a
45-degree angle showing the face and band. Include a subtle reflection
on the polished surface. Style should be clean, modern, and elegant.
```

#### Concept Art
```
Generate a concept art illustration of a futuristic city at sunset.
The scene should show towering skyscrapers with holographic billboards,
flying vehicles in the air, and pedestrians on elevated walkways.
Use a wide-angle perspective from street level looking up.
The lighting should be dramatic with warm sunset colors mixing with
cool blue artificial lights. Style should be cinematic and highly detailed.
```

#### Character Design
```
Create a fantasy character: an elven archer with long silver hair
braided with small flowers. She wears forest-green leather armor
with intricate leaf patterns. Her bow is made of living wood with
glowing runes. The background is an ancient forest with dappled sunlight.
Style should be detailed fantasy art suitable for a game character.
```

### When to Use Gemini

**Best for:**
- Character consistency across multiple images
- Iterative photo editing and refinement
- Multi-image composition and style transfer
- Conversational image creation workflow
- Projects requiring precise text rendering (Pro model)
- Professional asset production (Pro model)

**Consider alternatives when:**
- You need very specific artistic styles (Midjourney often better)
- You want maximum parameter control (Stable Diffusion better)
- You need completely uncensored generation (local SD better)
- You prefer simple, single-shot generation (DALL-E simpler)

### Tips for Best Results

1. **Start Simple, Add Detail**: Begin with basic description, then add specifics
2. **Mention Everything Important**: Don't assume - state lighting, clothing, pose, etc.
3. **Use Style References**: "editorial style", "cinematic", "Polaroid aesthetic"
4. **Leverage Conversation**: Use follow-up prompts to refine
5. **Photography Language**: Use technical terms for precise control
6. **Positive Descriptions**: Describe what you want, not what you don't

---

## Common Issues & Solutions

### Midjourney
**Issue:** Too artistic/stylized
**Solution:** Use `--style raw` and reduce `--s` value

**Issue:** Wrong aspect ratio
**Solution:** Specify `--ar` explicitly

### Stable Diffusion
**Issue:** Poor anatomy (hands, faces)
**Solution:** Use strong negative prompts, lower CFG, try different sampler

**Issue:** Blurry or low detail
**Solution:** Increase steps, use "highly detailed" in prompt, try SDXL

### DALL-E
**Issue:** Not following prompt precisely
**Solution:** Be more specific in natural language, break into multiple requests

**Issue:** Content policy rejection
**Solution:** Rephrase to focus on artistic/creative aspects

### Leonardo.ai
**Issue:** Inconsistent quality
**Solution:** Enable Alchemy mode, adjust Prompt Magic strength

**Issue:** Wrong style
**Solution:** Change the base model to match desired output type

### Google Gemini
**Issue:** Character not consistent across generations
**Solution:** Be very specific in initial character description, reference "the same character" in follow-ups

**Issue:** Not following complex instructions
**Solution:** Use Nano Banana Pro model, break complex requests into steps, use photography/cinematic terms

**Issue:** Image not detailed enough
**Solution:** Add more specific descriptors, use "highly detailed", specify lighting and composition, try Pro model
