# Tone.js Skill

Expert knowledge package for building interactive music applications with Tone.js in browser environments.

## Overview

Tone.js Skill provides comprehensive guidance for AI agents to build professional audio applications using the Tone.js Web Audio framework. It encapsulates best practices, common patterns, and critical gotchas for synthesizers, samplers, effects processing, and audio scheduling in browsers.

## Features

- **Complete API Coverage**: Instruments, effects, scheduling, Transport system, and audio routing
- **Step-by-Step Workflows**: Seven common tasks with detailed implementation steps
- **Timing Precision**: Emphasis on sample-accurate scheduling vs imprecise JavaScript timing
- **Edge Case Handling**: Browser autoplay policies, memory management, loading states
- **Pattern Library**: Step sequencers, probabilistic playback, dynamic parameters
- **Architecture Overview**: Class hierarchy and audio graph structure
- **Quick Reference**: Instrument types, effects, time notation lookup tables

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tonejs-skill.git
cd tonejs-skill

# Add to your agent's skill directory
cp SKILL.md ~/.config/your-agent/skills/tonejs.md
```

## Usage

This skill is designed to be loaded by AI agents that support skill-based knowledge systems. When loaded, the agent gains expertise in:

```
- Creating synthesizers and polyphonic instruments
- Loading and playing audio samples
- Building step sequencers and drum machines
- Applying real-time audio effects
- Automating parameters over time
- Synchronizing visuals with audio playback
- Implementing complex audio routing graphs
```

The skill emphasizes critical concepts like:

- User interaction requirement: `Tone.start()` must be called from click/touch events
- Time parameter discipline: Always use callback `time` parameter for scheduling
- Memory management: Disposing of audio nodes to prevent leaks
- Loading patterns: Waiting for `Tone.loaded()` before sample playback

## Configuration

The skill file follows standard frontmatter format:

```yaml
name: tonejs
description: Web Audio framework for creating interactive music in browsers
license: MIT
metadata:
    author: Yotam Mann
    version: "15.4.0"
    repository: https://github.com/Tonejs/Tone.js
```

Agents detect usage scenarios automatically based on keywords: synthesizers, audio visualization, DAWs, step sequencers, effects processors, sample playback.

## Architecture

The skill is organized into functional sections:

- `Core Concepts`: AudioContext initialization, audio graph routing, time notation, Transport system
- `Step-by-Step Instructions`: Seven common implementation tasks with code examples
- `Common Patterns`: Reusable code patterns for sequencers, probabilistic playback, LFO modulation
- `Sound Design Principles`: Comprehensive guide for notification sounds, UI feedback, creative process, and technical considerations
- `Edge Cases and Gotchas`: Seven critical issues with correct vs incorrect examples
- `Architecture Overview`: Tone.js class hierarchy diagram
- `Quick Reference`: Lookup tables for instruments, effects, and time notation

Each section includes inline code examples with explanatory comments. Incorrect patterns are marked `WRONG` with corrected alternatives marked `CORRECT`.

## Development

The skill is maintained as a single Markdown file:

```
tonejs-skill/
├── SKILL.md              # Complete skill (626 lines)
└── README.md             # Documentation
```

Validation commands:

```bash
# Validate frontmatter syntax
grep -A 10 "^---" SKILL.md

# Test code examples (requires Tone.js environment)
# Extract and run code blocks for verification
```

The skill targets Tone.js version 15.4.0. Key dependencies documented: Web Audio API support, modern browser with ES6+ features.

## License

MIT License
