# Voice Catalog

Comprehensive listing of Kokoro TTS voices with quality grades, characteristics, and selection guidance.

## Grade Criteria

| Grade | Meaning               | Description                                                               |
| ----- | --------------------- | ------------------------------------------------------------------------- |
| A     | Excellent naturalness | Indistinguishable from a natural human reading; pleasant cadence and tone |
| A-    | Near-excellent        | Very natural with minor imperfections in stress or rhythm                 |
| B     | Good clarity          | Clear and listenable but noticeably synthetic in some passages            |
| B-    | Above average         | Mostly clear but with occasional unnatural phrasing or robotic artifacts  |
| C+    | Acceptable            | Serviceable for notifications; some robotic qualities noticeable          |
| C     | Baseline              | Clearly synthetic but intelligible                                        |
| D     | Below average         | Robotic delivery; uncomfortable for extended listening                    |
| F+    | Poor                  | Significant artifacts; suitable only for short phrases                    |
| F     | Unusable              | Severe quality issues; not recommended for any use                        |

## Female Voices

### af_heart (Heart) -- Grade A

The current default English voice. Excellent naturalness with warm, expressive delivery. Handles long passages well without listener fatigue. Best all-around female voice.

**Strengths**: Natural cadence, warm tone, good breath pacing, handles punctuation naturally.
**Weaknesses**: None significant at current Kokoro version.
**Recommended for**: Default TTS, long-form reading, notifications.

### af_bella (Bella) -- Grade A-

Near-excellent naturalness. Slightly more formal tone than Heart. Excellent for professional or narration contexts.

**Strengths**: Clear enunciation, professional tone, consistent quality across sentence lengths.
**Weaknesses**: Slightly less warm than Heart; minor rhythm variations on complex sentences.
**Recommended for**: Professional narration, formal notifications.

### af_nicole (Nicole) -- Grade B-

Above average clarity. Noticeable synthetic quality on certain vowel sounds but generally pleasant.

**Strengths**: Good clarity, distinctive timbre.
**Weaknesses**: Some vowel sounds feel synthetic; pacing can be uneven on long passages.
**Recommended for**: Short notifications, variety rotation.

### af_aoede (Aoede) -- Grade C+

Acceptable quality. Serviceable for notifications but has noticeable robotic artifacts on longer passages.

**Strengths**: Distinct voice character, handles short phrases well.
**Weaknesses**: Robotic pacing on complex sentences, inconsistent stress patterns.
**Recommended for**: Short alerts, variety when primary voices are unavailable.

### af_kore (Kore) -- Grade C+

Similar tier to Aoede. Acceptable for short-form use.

**Strengths**: Clear articulation on short phrases.
**Weaknesses**: Unnatural rhythm on long passages, occasional emphasis on wrong syllables.
**Recommended for**: Short alerts only.

### af_sarah (Sarah) -- Grade C+

Acceptable quality with a softer delivery style.

**Strengths**: Softer tone may suit certain content types.
**Weaknesses**: Tends to lose clarity on technical or complex words; rhythm inconsistencies.
**Recommended for**: Casual short notifications.

## Male Voices

### am_adam (Adam) -- Grade F+

Poor quality with significant artifacts. Not recommended for regular use.

**Strengths**: Recognizably male voice.
**Weaknesses**: Significant synthetic artifacts, unnatural pacing, poor handling of punctuation.
**Recommended for**: Testing only.

### am_michael (Michael) -- Unrated

Not yet formally evaluated. Needs audition assessment.

**Strengths**: TBD.
**Weaknesses**: TBD.
**Recommended for**: Audition candidate.

### am_echo (Echo) -- Grade D

Below average quality. Robotic delivery unsuitable for extended listening.

**Strengths**: Intelligible on short phrases.
**Weaknesses**: Robotic tone, poor prosody, unpleasant on long passages.
**Recommended for**: Testing only.

### am_puck (Puck) -- Unrated

Not yet formally evaluated. Needs audition assessment.

**Strengths**: TBD.
**Weaknesses**: TBD.
**Recommended for**: Audition candidate.

## Chinese Voice

### zf_xiaobei -- Default Chinese Voice

Configured via `TTS_VOICE_ZH`. Used when CJK character ratio exceeds 20% (detected by `detect_language` in `tts-common.sh`). Not included in the English audition rotation.

## Voice Selection Guidance

### For Default TTS (TTS_VOICE_EN)

Use **af_heart** (Grade A). It provides the best naturalness and listener comfort for the primary use case of reading Claude Code responses aloud via Telegram.

### For Variety or Rotation

If implementing voice rotation, limit to Grade B- and above: af_heart, af_bella, af_nicole.

### For Short Notifications Only

Any Grade C+ voice is acceptable for brief alerts: af_aoede, af_kore, af_sarah.

### Male Voices

The male voice catalog is currently weak. am_michael and am_puck are unrated and should be auditioned before use. am_adam (F+) and am_echo (D) are not recommended for production.

## Configuration

Voices are configured in `~/.claude/automation/claude-telegram-sync/mise.toml`:

```toml
[env]
TTS_VOICE_EN = "af_heart"      # Kokoro English voice ID
TTS_VOICE_ZH = "zf_xiaobei"    # Kokoro Chinese voice ID
TTS_VOICE_SAY_EN = "Samantha"  # macOS say fallback (English)
TTS_VOICE_SAY_ZH = "Ting-Ting" # macOS say fallback (Chinese)
```

The shell library `tts-common.sh` also reads `EN_VOICE` and `ZH_VOICE` environment variables, defaulting to af_heart and zf_xiaobei respectively.
