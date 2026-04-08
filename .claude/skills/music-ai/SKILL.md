---
name: music-ai
description: AI music generation, composition, lyrics, mastering, rights management, playlist curation — Suno, Udio, MusicGen, Soundraw for MAARS music agents
---

# Music AI — MAARS Reference

## Music Generation Platforms
```python
MUSIC_GEN_PLATFORMS = {
    "suno_v4": {
        "api": "https://studio-api.suno.ai",
        "strengths": "Full songs with vocals, any genre",
        "quality": "Highest vocal quality",
        "pricing": "$8/mo (500 songs) → Pro $24/mo",
        "use_cases": ["Jingles", "Background music", "Song demos", "Viral content"],
    },
    "udio": {
        "quality": "Excellent, rivals Suno",
        "strengths": "More control over structure, extensions",
        "use_cases": ["Longer compositions", "Iterative refinement"],
    },
    "musicgen": {
        "provider": "Meta (via replicate/huggingface)",
        "type": "Open source",
        "strengths": "Local deployment, no licensing issues for commercial",
        "use_cases": ["Background music", "Game/app soundtracks", "Loops"],
        "api": "https://api.replicate.com/v1/predictions",
    },
    "soundraw": {
        "focus": "Royalty-free music for content creators",
        "customization": "Tempo, energy, instruments, mood",
        "pricing": "$16.99/mo unlimited",
        "use_cases": ["YouTube", "Podcasts", "Social media"],
    },
    "stable_audio": {
        "provider": "Stability AI",
        "api": "https://api.stability.ai/v2beta/audio",
        "strengths": "Sound effects + music, precise duration control",
        "use_cases": ["Sound design", "Foley", "Short clips"],
    },
}
```

## Suno API Integration
```python
import requests, time

def generate_suno_song(prompt: str, style: str, title: str = ""):
    """Generate a full song with Suno API"""
    headers = {"Authorization": f"Bearer {SUNO_API_KEY}"}
    
    # Generate
    resp = requests.post("https://studio-api.suno.ai/api/generate/v2/",
        headers=headers,
        json={
            "prompt": f"[{style}] {prompt}",
            "title": title,
            "make_instrumental": False,
            "wait_audio": False,
        })
    clip_ids = [c["id"] for c in resp.json()["clips"]]
    
    # Poll for completion
    while True:
        feed = requests.get("https://studio-api.suno.ai/api/feed/",
            headers=headers, params={"ids": ",".join(clip_ids)}).json()
        if all(c["status"] == "complete" for c in feed):
            return [{"id": c["id"], "audio_url": c["audio_url"],
                     "title": c["title"], "duration": c["duration"]} 
                    for c in feed]
        time.sleep(5)
```

## Lyrics Generation
```python
LYRICS_PROMPT = """
Write lyrics for a {genre} song.
Theme: {theme}
Mood: {mood}
Structure: {structure} (verse-chorus-verse-chorus-bridge-chorus / AABA / through-composed)
Length: {length} minutes approx.
Style reference: Similar to {artist_reference}
Vocal style: {vocal_style} (male/female/duet/choir)
BPM feel: {tempo} (slow ballad / mid-tempo / upbeat / fast)

Requirements:
- Rhyme scheme: {rhyme_scheme} (ABAB/AABB/ABCB/free)
- Avoid clichés unless intentionally ironic
- Strong hook in chorus (memorable, singable)
- Bridge should pivot emotionally or thematically
- Include syllable count targets for each line

Output:
[VERSE 1]
...
[CHORUS]
...
[VERSE 2]
...
[CHORUS]
...
[BRIDGE]
...
[FINAL CHORUS]
...
"""
```

## Music Analysis & Theory
```python
MUSIC_ANALYSIS_PROMPT = """
Analyze this piece of music: {audio_description or lyrics}

Provide:
1. KEY & SCALE: Primary key, mode (major/minor/dorian/etc.)
2. CHORD PROGRESSION: Roman numeral analysis (I-IV-V-vi etc.)
3. TIME SIGNATURE: Meter and feel
4. TEMPO & ENERGY: BPM range, energy arc
5. GENRE CLASSIFICATION: Primary + secondary genres
6. INSTRUMENTATION: Key instruments and their roles
7. STRUCTURE: Label sections (intro/verse/chorus/bridge/outro)
8. PRODUCTION STYLE: Era, production techniques
9. EMOTIONAL ARC: How the music makes you feel and why
10. SIMILAR ARTISTS: Who this sounds like and why
"""

MUSIC_THEORY_TOOLS = {
    "chord_progressions": {
        "pop": ["I-V-vi-IV", "vi-IV-I-V", "I-IV-V-I"],
        "jazz": ["ii-V-I", "I-VI-II-V", "iii-VI-ii-V"],
        "blues": ["I7-IV7-I7-I7-IV7-IV7-I7-I7-V7-IV7-I7-V7"],
        "edm": ["i-VI-III-VII", "I-IV-vi-V"],
    },
    "modes": {
        "ionian": "Happy, bright (C D E F G A B)",
        "dorian": "Minor but hopeful (D E F G A B C)",
        "phrygian": "Dark, Spanish feel",
        "lydian": "Dreamy, floating",
        "mixolydian": "Rock, bluesy",
        "aeolian": "Natural minor, sad",
        "locrian": "Dissonant, unstable",
    },
}
```

## Audio Processing
```python
# Librosa — audio analysis
import librosa
import numpy as np

def analyze_audio(file_path: str) -> dict:
    y, sr = librosa.load(file_path)
    
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Key detection
    chroma_avg = np.mean(chroma, axis=1)
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    detected_key = key_names[np.argmax(chroma_avg)]
    
    return {
        "bpm": float(tempo),
        "duration": librosa.get_duration(y=y, sr=sr),
        "key": detected_key,
        "energy": float(np.mean(np.abs(y))),
        "spectral_centroid": float(np.mean(spectral_centroids)),
    }

# Audio mastering with PyDub
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

def master_audio(input_path: str, output_path: str, target_lufs: float = -14.0):
    audio = AudioSegment.from_file(input_path)
    audio = normalize(audio)
    audio = compress_dynamic_range(audio, threshold=-20, ratio=4)
    # Export with appropriate bitrate
    audio.export(output_path, format="mp3", bitrate="320k",
                tags={"album": "MAARS Generated"})
```

## Music Rights & Licensing
```python
MUSIC_LICENSING = {
    "sync_license": "Using music in video (ads, film, YouTube)",
    "master_license": "Using specific recording (covers need both)",
    "mechanical_license": "Reproducing/distributing a composition",
    "public_performance": "Playing music in public venues (ASCAP/BMI)",
    
    "royalty_free_sources": [
        "Soundraw.io", "Epidemic Sound", "Artlist",
        "YouTube Audio Library", "Free Music Archive",
        "Pixabay Music", "ccMixter (Creative Commons)",
    ],
    "ai_generated_music_rights": {
        "suno": "Commercial use with subscription (check current ToS)",
        "udio": "Check per-track license",
        "musicgen": "Meta Research License — check commercial terms",
        "soundraw": "Royalty-free with subscription",
    },
}
```

## Playlist Curation
```python
PLAYLIST_CURATION_PROMPT = """
Create a curated playlist for:
Occasion: {occasion}
Mood journey: {mood_arc} (e.g., "start energetic, build, peak, cool down")
Duration: {duration} minutes
Genre: {genres}
Audience: {audience}
Platform: {platform} (Spotify/Apple Music/YouTube)

For each track recommendation:
- Artist + Title
- BPM + Energy level (1-10)
- Why it fits at this point in the playlist
- Transition note (how to blend to next track)

Apply DJ principles:
- Key compatibility for smooth transitions
- Energy curve matching the occasion arc
- Avoid clustering similar sounds
"""
```

## Models to Use
- **Music generation**: `suno-v4` (vocals), `musicgen` (instrumental/commercial)
- **Lyrics writing**: `claude-opus-4-6` (poetic, structured)
- **Music analysis**: `claude-opus-4-6` (nuanced cultural + technical understanding)
- **Playlist curation**: `claude-sonnet-4-6` (taste + flow)
- **Audio description for prompts**: `gpt-4o` (fast, accurate)
- **Rights research**: `perplexity/sonar-pro` (current licensing info)
