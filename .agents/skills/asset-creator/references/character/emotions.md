# Character Emotions

<overview>
Characters can express **any emotion** the scene demands. Create new emotions as needed using these patterns.
</overview>

<changeable-components>

| Component | How It Changes |
|-----------|----------------|
| **Eyes** | Size (rx/ry), pupil position, squinting, half-closed |
| **Eyebrows** | Add paths - angled up/down/curved |
| **Mouth** | Smile, frown, O-shape, teeth, wavy |
| **Cheeks** | Color shifts (red=angry, pale=sad, pink=surprised) |
| **Extras** | Tears, zzz, eye shine, bags under eyes |

</changeable-components>

---

<eyebrows>
**Note:** All coordinates below assume a 250×250 viewBox with character centered.

```svg
<!-- Sad - angled down toward outside -->
<path d="M80 95 L110 105" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>
<path d="M170 95 L140 105" stroke="#1a1a1a" stroke-width="3" stroke-linecap="round"/>

<!-- Angry - V shape, angled down toward center -->
<path d="M75 100 L105 110" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/>
<path d="M175 100 L145 110" stroke="#1a1a1a" stroke-width="4" stroke-linecap="round"/>

<!-- Surprised - raised curved -->
<path d="M80 90 Q95 85 110 90" stroke="#1a1a1a" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M140 90 Q155 85 170 90" stroke="#1a1a1a" stroke-width="3" fill="none" stroke-linecap="round"/>
```

</eyebrows>

---

<eye-variations>

```svg
<!-- Normal -->
<ellipse cx="95" cy="115" rx="12" ry="14" fill="white"/>
<circle cx="98" cy="118" r="6" fill="#1a1a1a"/>

<!-- Wide (surprised) - larger, centered pupil, add shine -->
<ellipse cx="95" cy="115" rx="16" ry="20" fill="white"/>
<circle cx="95" cy="115" r="8" fill="#1a1a1a"/>
<circle cx="90" cy="110" r="3" fill="white"/>

<!-- Squinting (angry) - compressed vertically -->
<ellipse cx="95" cy="120" rx="12" ry="10" fill="white"/>
<circle cx="98" cy="120" r="5" fill="#1a1a1a"/>

<!-- Half-closed (sleepy) - with eyelid overlay -->
<ellipse cx="95" cy="120" rx="14" ry="8" fill="white"/>
<ellipse cx="95" cy="115" rx="16" ry="10" fill="[BODY_COLOR]"/>
<circle cx="95" cy="122" r="4" fill="#1a1a1a"/>

<!-- Looking down (sad) - pupil moved down -->
<ellipse cx="95" cy="120" rx="12" ry="14" fill="white"/>
<circle cx="95" cy="125" r="6" fill="#1a1a1a"/>
```

</eye-variations>

---

<mouth-variations>

```svg
<!-- Big smile (happy) -->
<path d="M95 150 Q125 180 155 150" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="round"/>

<!-- Frown (sad) -->
<path d="M100 165 Q125 145 150 165" stroke="#1a1a1a" stroke-width="3" fill="none" stroke-linecap="round"/>

<!-- O-mouth (surprised) -->
<ellipse cx="125" cy="160" rx="12" ry="16" fill="#1a1a1a"/>

<!-- Yawn (sleepy) -->
<ellipse cx="125" cy="160" rx="15" ry="12" fill="#1a1a1a"/>

<!-- Gritting teeth (angry) -->
<rect x="100" y="150" width="50" height="15" fill="#1a1a1a" rx="2"/>
<line x1="110" y1="150" x2="110" y2="165" stroke="white" stroke-width="2"/>
<line x1="125" y1="150" x2="125" y2="165" stroke="white" stroke-width="2"/>
<line x1="140" y1="150" x2="140" y2="165" stroke="white" stroke-width="2"/>
```

</mouth-variations>

<extra-elements>

```svg
<!-- Tear drop (sad) -->
<ellipse cx="78" cy="135" rx="4" ry="6" fill="#87CEEB"/>

<!-- Bags under eyes (sleepy) -->
<path d="M82 130 Q95 136 108 130" stroke="#1E5ECC" stroke-width="2" fill="none"/>

<!-- ZZZ floating (sleepy) -->
<text x="175" y="65" font-family="Arial" font-size="14" fill="#1a1a1a" font-weight="bold">Z</text>
<text x="185" y="55" font-family="Arial" font-size="12" fill="#1a1a1a" font-weight="bold">Z</text>
<text x="193" y="47" font-family="Arial" font-size="10" fill="#1a1a1a" font-weight="bold">Z</text>
```

</extra-elements>

---

<eye-blink-animation>

<blink-technique>
Use **clipPath** so pupils are clipped (not squished) and never overflow:

```svg
<defs>
  <clipPath id="leftEyeClip">
    <ellipse cx="95" cy="115" rx="14" ry="16">
      <animate attributeName="ry" values="16;16;0;0;16;16" keyTimes="0;0.47;0.49;0.51;0.53;1" dur="3s" repeatCount="indefinite"/>
    </ellipse>
  </clipPath>
  <clipPath id="rightEyeClip">
    <ellipse cx="155" cy="115" rx="14" ry="16">
      <animate attributeName="ry" values="16;16;0;0;16;16" keyTimes="0;0.47;0.49;0.51;0.53;1" dur="3s" repeatCount="indefinite"/>
    </ellipse>
  </clipPath>
</defs>

<!-- Left Eye -->
<ellipse cx="95" cy="115" rx="14" ry="16" fill="white">
  <animate attributeName="ry" values="16;16;0;0;16;16" keyTimes="0;0.47;0.49;0.51;0.53;1" dur="3s" repeatCount="indefinite"/>
</ellipse>
<circle cx="98" cy="115" r="7" fill="#1a1a1a" clip-path="url(#leftEyeClip)"/>

<!-- Right Eye -->
<ellipse cx="155" cy="115" rx="14" ry="16" fill="white">
  <animate attributeName="ry" values="16;16;0;0;16;16" keyTimes="0;0.47;0.49;0.51;0.53;1" dur="3s" repeatCount="indefinite"/>
</ellipse>
<circle cx="152" cy="115" r="7" fill="#1a1a1a" clip-path="url(#rightEyeClip)"/>
```
</blink-technique>

<blink-explanation>
**How it works:** Eye white animates `ry` from full → 0 → full. ClipPath contains same animated ellipse to clip the pupil. Pupil doesn't animate - it's masked by clipPath. Eyes close completely, pupil never overflows.
</blink-explanation>

<blink-timing>
**Timing** (`keyTimes`): 0→0.47 open | 0.47→0.49 closing | 0.49→0.51 closed | 0.51→0.53 opening | 0.53→1 open
</blink-timing>

<blink-duration>
**Duration by emotion:** Happy: 3s | Sad: 5s (slower) | Angry: 2s (intense) | Surprised: 6s (wide-eyed) | Sleepy: custom with heavy lids
</blink-duration>

</eye-blink-animation>
