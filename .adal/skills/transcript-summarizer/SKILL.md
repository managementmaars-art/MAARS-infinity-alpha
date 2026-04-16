---
name: transcript-summarizer
description: Summarize meeting transcripts into structured notes with decisions, action items, and key topics.
---

# Transcript Summarizer Skill

## Purpose

Convert meeting transcripts into structured, actionable summaries. Supports multiple transcript formats and LLM backends.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REFLEX_TRANSCRIPT_SRC_DIR` | Default directory to look for transcript files | `.` |
| `REFLEX_TRANSCRIPT_DST_DIR` | Root output directory for processed transcripts | `./meetings` |
| `REFLEX_TRANSCRIPT_LLM` | LLM provider: `ollama`, `openai`, `anthropic` | `ollama` |
| `REFLEX_TRANSCRIPT_MODEL` | Model name override | Provider default |

## When to Use

- After a meeting recording has been transcribed
- Processing VTT/SRT captions from video calls
- Summarizing pasted meeting notes
- Extracting action items and decisions from long discussions

## Output Structure

Each meeting produces a directory with three files:

```
${REFLEX_TRANSCRIPT_DST_DIR:-./meetings}/
└── <YYYY-MM-DD>/
    └── <HH-MM>/
        ├── original.txt    # Raw transcript (unmodified source)
        ├── readable.md     # Cleaned, formatted transcript
        └── summary.md      # Structured summary (stored in Qdrant)
```

### File Descriptions

**original.txt**
- Exact copy of the input transcript
- Preserves VTT/SRT timestamps, formatting artifacts, etc.
- Useful for debugging or re-processing with different settings

**readable.md**
- Cleaned transcript with preprocessing applied (see Transcript Format Preprocessing)
- Speaker labels normalized
- Timestamps and artifacts removed
- Consecutive same-speaker lines merged
- Human-readable format for reviewing what was actually said

**summary.md**
- Structured summary following the Summary Template
- This is the file stored in Qdrant for RAG retrieval
- Contains executive summary, decisions, action items, etc.

### Directory Naming

- Date: ISO format `YYYY-MM-DD` (e.g., `2024-01-15`)
- Time: 24-hour format `HH-MM` (e.g., `14-30` for 2:30 PM)
- If meeting time is unknown, use `00-00` or prompt user

### Workflow

1. **Copy** original transcript to `original.txt`
2. **Clean** transcript using format-specific preprocessing → `readable.md`
3. **Summarize** cleaned transcript → `summary.md`
4. **Store** summary.md content in Qdrant with metadata pointing to directory

## Summary Template

The summarizer produces this structured output:

```markdown
# Meeting Summary: <title>

**Date:** <YYYY-MM-DD>
**Attendees:** <comma-separated names>
**Duration:** <if detectable from timestamps>

## Executive Summary

<2-4 sentence overview of the meeting's purpose and outcomes>

## Key Topics

1. **<Topic>** - <1-sentence description>
2. **<Topic>** - <1-sentence description>
   (3-7 topics)

## Decisions Made

- **<Decision>**: <reasoning or context>
- **<Decision>**: <reasoning or context>

## Action Items

| Action | Owner | Deadline |
|--------|-------|----------|
| <task> | <person> | <date or TBD> |

## Open Questions

- <Question or unresolved item>
- <Question or unresolved item>
```

## Extraction Cues

### Decisions
Look for phrases indicating agreement or resolution:
- "let's go with", "we decided", "agreed", "the plan is"
- "we'll use", "going forward", "the approach will be"
- Unanimous or majority agreement markers

### Action Items
Look for commitment language:
- "I'll do", "I will", "I can take that"
- "can you", "please handle", "your task is"
- "@name" followed by a task
- "by Friday", "next week", "before the release"

### Open Questions
Look for unresolved items:
- "TBD", "to be determined", "parking lot"
- "we need to figure out", "open question"
- "let's revisit", "follow up on"
- Questions without clear answers in the transcript

### Attendees
- Speaker labels (e.g., "John:", "Sarah Smith:")
- "attendees:", "participants:", "present:"
- Names mentioned in greetings ("hi John", "thanks Sarah")

## Transcript Format Preprocessing

### VTT (WebVTT)
- Strip `WEBVTT` header and metadata lines
- Remove timestamp lines (`00:00:00.000 --> 00:00:05.000`)
- Remove position/alignment tags (`<c>`, `align:`, `position:`)
- Deduplicate rolling captions (many VTT files repeat lines with slight timestamp shifts)
- Merge consecutive lines from same speaker

### SRT (SubRip)
- Strip sequence numbers (standalone integers)
- Remove timestamp lines (`00:00:00,000 --> 00:00:05,000`)
- Remove blank separator lines
- Merge consecutive same-speaker lines

### Plain Text
- Use as-is
- Detect speaker labels: `Name:`, `[Name]`, `SPEAKER_01:`
- Normalize speaker label formats for consistency

### DOCX
- Extract paragraph text via python-docx
- Preserve heading structure
- Strip formatting artifacts

### Google Doc
- Fetched via Google Workspace MCP as plain text
- Treat same as plain text after retrieval

## Long Transcript Strategy

**Threshold:** 30,000 words

### Single Pass (<30K words)
Send entire cleaned transcript to LLM with the system prompt and template.

### Two-Pass Chunked (>30K words)
1. **Chunk**: Split at ~20,000 word boundaries, preferring natural breaks (speaker changes, topic shifts, timestamp gaps)
2. **Extract**: Summarize each chunk independently, extracting topics, decisions, action items, and questions
3. **Synthesize**: Combine chunk summaries into a single coherent summary, deduplicating items and merging topics

## Qdrant Storage Schema

Always store summaries in Qdrant for RAG retrieval. The **full summary content** must be stored in the `information` field to enable semantic search across meeting contents.

**Information Field (embedded content):**
Store the complete generated summary markdown, including:
- Executive summary
- Key topics with descriptions
- Decisions with reasoning
- Action items (as formatted text)
- Open questions

This enables queries like "what did we decide about X?" or "who is responsible for Y?" to find relevant meetings.

**Metadata Fields:**
```yaml
source: "meeting_transcript"
content_type: "meeting_summary"
harvested_at: "<ISO 8601 timestamp>"

# Meeting context
meeting_title: "<title>"
meeting_date: "<YYYY-MM-DD>"
meeting_time: "<HH-MM>"
attendees: "<comma-separated names>"
output_dir: "<path to YYYY-MM-DD/HH-MM directory>"
source_format: "<vtt|srt|txt|docx|gdoc|pasted>"

# Extracted counts (for filtering)
action_item_count: <integer>
decision_count: <integer>
topics: "<comma-separated key topics>"

# Classification
category: "business"
type: "meeting_summary"
confidence: "high"
```

## LLM System Prompt

The summarize.py script uses this system prompt:

```
You are a meeting transcript summarizer. Your job is to extract structured
information from meeting transcripts.

Given a transcript, produce a summary with these sections:
- Executive Summary (2-4 sentences)
- Key Topics (3-7 bullet points)
- Decisions Made (with reasoning)
- Action Items (action, owner, deadline as table rows)
- Open Questions (unresolved items)

Rules:
- Only include information explicitly stated in the transcript
- If attendees are not clear, note "Attendees not identified"
- If no decisions were made, state "No explicit decisions recorded"
- Mark deadlines as "TBD" when not specified
- Keep the executive summary factual, not interpretive
```
