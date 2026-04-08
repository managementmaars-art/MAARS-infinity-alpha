
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Creative arts and music technology
    ('music-production', 'Music production - DAW, mixing, mastering, sound design, synthesis, sampling, arrangement'),
    ('ableton-live', 'Ableton Live - clips, devices, Max for Live, Push, MIDI, audio effects, warping, exporting'),
    ('fl-studio', 'FL Studio - patterns, mixer, automation, plugins, zipped loops, performance, scripting'),
    ('logic-pro-advanced', 'Logic Pro advanced - smart tempo, Flex Time, Space Designer, Alchemy, drummer, production'),
    ('pro-tools-advanced', 'Pro Tools advanced - HD, session management, elastic audio, AAX plugins, post workflows'),
    ('audio-programming', 'Audio programming - JUCE, PortAudio, RtAudio, DSP, plugin development, VST/AU/AAX'),
    ('max-msp', 'Max/MSP - patching, objects, gen~, codebox, MIDI, CV, Jitter, Node for Max, RNBO'),
    ('supercollider', 'SuperCollider - SynthDef, patterns, buses, server control, OSC, JITLib, SCLang'),
    ('pd-puredata', 'Pure Data - patches, abstractions, externals, GEM, Pd-Lua, embedded, Android, iOS'),
    ('spatial-audio', 'Spatial audio - ambisonics, binaural, HRTF, Dolby Atmos, Sony 360, spatialization algorithms'),
    ('sound-design', 'Sound design - synthesis, sampling, Foley, field recording, spectral editing, convolution'),
    ('music-theory-tech', 'Music theory technology - notation software, Sibelius, Finale, MuseScore, XML, LilyPond'),
    ('generative-music', 'Generative music - algorithmic composition, Markov chains, ML, rule systems, live coding'),
    # Film and video technology
    ('cinematography-tech', 'Cinematography technology - camera systems, RAW, LUT, grading workflow, lens metadata'),
    ('video-production-workflow', 'Video production workflow - pre-production, shooting, editing, finishing, delivery, archiving'),
    ('color-grading', 'Color grading - DaVinci, color science, node workflows, LUTs, HDR, deliverables, creative'),
    ('vfx-compositing', 'VFX compositing - Nuke, After Effects, keying, roto, tracking, color, integration'),
    ('motion-graphics-advanced', 'Motion graphics advanced - After Effects, Cinema 4D, expressions, Lottie, web animation'),
    ('3d-rendering-advanced', '3D rendering advanced - path tracing, shading models, HDRI, render farms, denoising'),
    ('real-time-rendering', 'Real-time rendering - Unreal Engine, Lumen, Nanite, ray tracing, materials, blueprints'),
    ('virtual-production', 'Virtual production - LED volumes, in-camera VFX, Unreal, tracking, Mo-Sys, Ncam, nDisplay'),
    ('game-narrative-design', 'Game narrative design - branching, world building, dialogue systems, Ink, Twine, Articy'),
    ('interactive-fiction', 'Interactive fiction - Inform 7, Twine, ink, parser, choice, CYOA, Bitsy, narrative design'),
    ('game-audio', 'Game audio - middleware, Wwise, FMOD, adaptive audio, mixing, implementation, SFX, voice'),
    # Language learning technology
    ('language-learning-apps', 'Language learning apps - spaced repetition, SRS algorithms, Anki, Duolingo, pedagogy'),
    ('nlp-language-teaching', 'NLP for language teaching - grammar checking, pronunciation, feedback, adaptive difficulty'),
    ('corpus-linguistics', 'Corpus linguistics - concordancing, frequency analysis, NLTK, Sketch Engine, learner corpora'),
    ('speech-recognition-teaching', 'Speech recognition for teaching - pronunciation assessment, ASR, phoneme, feedback'),
    ('translation-technology', 'Translation technology - CAT tools, TM, glossaries, SDL Trados, memoQ, MT post-editing'),
    ('localization-advanced', 'Localization advanced - i18n, l10n, pseudo-localization, LQA, TMS, workflow automation'),
    # Mental health technology
    ('mental-health-platforms', 'Mental health platforms - teletherapy, EHR, scheduling, billing, HIPAA, PHR, outcomes'),
    ('digital-therapeutics', 'Digital therapeutics - FDA DTx, CBT apps, PTSD, anxiety, depression, evidence, compliance'),
    ('crisis-intervention-tech', 'Crisis intervention technology - hotline systems, chatbots, risk assessment, escalation'),
    ('addiction-recovery-tech', 'Addiction recovery technology - tracking, peer support, medication reminders, MBC, PHQ'),
    # Smart home and consumer IoT
    ('home-assistant-advanced', 'Home Assistant advanced - automations, blueprints, custom components, lovelace, integrations'),
    ('homekit-development', 'HomeKit development - HAP protocol, accessories, services, characteristics, Homebridge'),
    ('smart-home-protocols', 'Smart home protocols - Matter, Thread, Zigbee, Z-Wave, KNX, Lutron, interoperability'),
    ('alexa-skills-advanced', 'Alexa Skills advanced - APL, ISP, account linking, custom slot types, SSML, proactive events'),
    ('google-home-actions', 'Google Home Actions - Smart Home API, intents, device traits, local SDK, Account Linking'),
    ('iot-security-advanced', 'IoT security advanced - secure boot, TLS, certificate management, firmware signing, OTA'),
    ('edge-computing-iot', 'Edge computing IoT - AWS Greengrass, Azure IoT Edge, balena, ML inference, stream processing'),
    # Game development deep
    ('unity-advanced', 'Unity advanced - ECS, DOTS, Burst, URP, HDRP, shader graph, UI Toolkit, Netcode'),
    ('unreal-advanced', 'Unreal Engine advanced - Blueprints, C++, Gameplay Framework, AI, networking, animation'),
    ('godot-advanced', 'Godot advanced - GDScript, C#, signals, physics, networking, shaders, editor plugins'),
    ('game-physics', 'Game physics - rigid body, collision, joints, PhysX, Bullet, Jolt, character controllers'),
    ('game-ai-advanced', 'Game AI advanced - behavior trees, GOAP, utility theory, nav mesh, pathfinding, perception'),
    ('game-networking-advanced', 'Game networking advanced - rollback, lag compensation, interest management, prediction'),
    ('game-analytics', 'Game analytics - events, funnels, retention, LTV, A/B testing, LiveOps, data pipeline'),
    ('game-monetization', 'Game monetization - IAP, battle pass, ad mediation, pricing, balance, ethical design'),
    ('procedural-generation', 'Procedural generation - terrain, dungeon, grammar, noise, WFC, cellular automata, fractals'),
    ('shader-programming', 'Shader programming - GLSL, HLSL, vertex, fragment, compute, raymarching, GPGPU, debugging'),
    # Creative coding
    ('openframeworks', 'openFrameworks - addons, computer vision, 3D, audio, network, threading, events, ofxGui'),
    ('processing-advanced', 'Processing/p5.js advanced - libraries, 3D, shaders, generative art, live coding, export'),
    ('three-js-advanced', 'Three.js advanced - custom shaders, post-processing, physics, AR/VR, instancing, GPGPU'),
    ('touchdesigner-advanced', 'TouchDesigner advanced - CHOP, TOP, DAT, SOP, operators, Python, live performance'),
    ('vvvv-programming', 'vvvv gamma - dataflow, patches, reactive, spread, VL, GPU, real-time, installation'),
    ('resolume-vjing', 'Resolume Avenue/Arena - clips, effects, composition, mapping, FFGL plugins, DMX, Ableton sync'),
    ('notch-realtime', 'Notch - real-time 3D, particles, ACES, camera, LDAP, generative, post-production'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
