---
name: hn-to-x-poster
description: Use this when the user wants to review Hacker News top 30 stories, select software or AI related items, and automatically publish a Chinese thread of at least 3 posts to x.com or Twitter from an already logged-in browser session.
---

# HN to X Poster

## Overview

Use this skill for a browser-driven workflow that reads the current Hacker News front page, filters the top 30 stories for software or AI relevance, compresses the signal into a Chinese thread, and publishes it to `x.com`.

This skill is for direct execution, not just drafting. Default behavior is to post automatically if `x.com` is already logged in. If posting is blocked, fall back to a ready-to-send Chinese draft or thread and explain the blocker briefly.

## When To Use

Use this skill when the user asks for any combination of:

- Hacker News or HN top stories
- HN top 30, front page, or current HN software or AI items
- posting, tweeting, sending, or publishing the result to `x.com` or Twitter
- a Chinese summary of current HN software or AI topics that should be posted automatically

Do not use this skill when:

- the user only wants HN analysis without posting
- the user wants deep article research instead of front-page signal extraction

## Required Tooling

Use `chrome-devtools` MCP for the browser workflow.

Do not rely on API access to Hacker News or X unless the user explicitly changes the method.

## Workflow

### 1. Open The Two Sites

- Open or switch to `https://news.ycombinator.com/`
- Open or switch to `https://x.com/`
- Confirm that X is logged in before attempting to post

If X is not logged in, stop automatic posting and return a Chinese draft the user can publish manually.

### 2. Read HN Top 30

- Read the current HN front page
- Capture the first 30 ranked stories only
- Use the front-page title and visible context as the default source of truth

Do not open every article by default. This skill is meant to summarize the HN front-page signal, not to perform full article research.

### 3. Filter For Software Or AI Relevance

Keep items that are clearly about:

- software engineering
- programming languages
- developer tools
- operating systems
- networking, infrastructure, databases, compilers, security, or systems work
- AI, LLMs, agents, model tooling, MCP, inference workflows, or AI product/platform shifts

Usually drop items that are mainly:

- general politics
- culture or biography
- pure science without a software or AI angle
- consumer oddities with no developer or AI relevance

If an item is borderline, prefer keeping it only when a technical audience would plausibly care.

### 4. Plan Post Structure

Decide the thread structure before writing.

If the user explicitly specifies the number of posts in the thread:

- follow the user's specified count
- organize the content to fit that count as cleanly as possible
- do not override the count just because a different number seems better

If the user does not specify the number of posts:

- default to a thread of at least `3` posts
- treat HN front-page signal as high-density by default; do not assume one post is enough
- use a `total -> points -> takeaway` structure as the baseline shape
- allow `4+` posts whenever that makes the thread clearer
- do not optimize for the fewest posts; optimize for explaining the signal cleanly
- split by natural content blocks instead of arbitrary equal lengths
- prefer adding another post over over-compressing one crowded post

Default thread planning heuristics:

- `3` posts: the default minimum when the user did not specify a count
- `4` posts: use when signals naturally separate into multiple clusters, such as AI, security/systems, languages/tools, and conclusion
- `5+` posts: acceptable when needed to keep each post readable and specific
- `1` or `2` posts: only use when the user explicitly asks for that count

When writing a thread, give each post a distinct job. Typical default structure:

- post 1: overall read on today's HN board, set the tone
- post 2: first major cluster of signals
- post 3: second major cluster plus closing takeaway

If using more than 3 posts, keep the same principle:

- opening post sets the frame
- middle posts each cover one clear cluster
- final post lands the synthesis, verdict, or forward-looking take

### 5. Build The Post

Write the final Chinese content as a thread that:

- sounds natural on X
- highlights only the strongest 4 to 8 software or AI signals
- compresses repeated themes instead of listing everything
- ends with a clear conclusion about the pattern

Default style:

- concise
- readable by Chinese tech audiences
- opinionated and human, not robotic
- may use slang, idioms, colloquial turns of phrase, or other distinctive personal expressions when they improve voice
- keep the voice vivid but still grounded in what was actually visible on HN
- no hashtags unless the user asks
- no links unless the user asks

If writing a thread:

- keep each post readable on its own
- maintain flow across posts instead of making each one feel like a separate unrelated update
- use simple numbering such as `1/`, `2/`, `3/` when that improves clarity
- avoid stuffing every retained HN item into the thread; keep only the strongest signals
- prefer sharp summaries over flat inventory lists
- let the wording have some personality, but do not let jokes or slang blur the actual point

### 6. Enforce Length Before Posting

Before posting, make sure each post is short enough for a standard X post.

Length rules to enforce:

- standard X posts are limited to `280` characters for normal users
- a Chinese character usually consumes about `1-2` characters of the counter
- a link usually consumes about `23` characters even when it looks shorter
- always trust the visible X counter over any rough manual estimate

If it is too long:

- first consider splitting the content into more thread posts
- compress only after the thread structure is already reasonable
- remove low-signal items first
- collapse repeated categories into one phrase
- keep the main pattern, not the full inventory

For threads:

- shorten each post independently
- keep the thread balanced, but do not force equal lengths
- if one post is doing too much, split it before flattening it
- if the thread is getting too long overall, remove lower-signal details before sacrificing the total-summary-total structure

### 7. Post On X

Use the homepage composer with keyboard-first actions.

For a single post:

- go to `https://x.com/home`
- prefer pressing `n` first to open the new post composer
- if `n` does not open the composer, fall back to clicking the homepage `Post` button
- confirm the composer is visible before typing
- **NEVER use fill** - must use type_text to input the complete text in one go
- Do not input in steps or modify mid-way - input the full Chinese text at once
- verify both of these before posting:
  - the post button is enabled
  - the character counter looks normal
- prefer pressing `Ctrl + Enter` to publish
- if `Ctrl + Enter` does not publish, fall back to clicking `Post`

For a thread:

- go to `https://x.com/home`
- prefer pressing `n` first to open the new post composer
- if `n` does not open the composer, fall back to clicking the homepage `Post` button
- confirm the composer is visible before typing
- **NEVER use fill** - every post in the thread must be entered with `type_text`
- type the full text of post 1 in one go
- find and click the `Add post` button to create the next composer cell
- type the full text of each later post in one go with `type_text`
- keep repeating until all planned posts are present
- verify the final publish control is enabled and the visible counters look normal
- prefer pressing `Ctrl + Enter` once to publish the entire thread
- if `Ctrl + Enter` does not publish, fall back to clicking the final `Post all` or equivalent publish button

### 8. Verify Completion

After posting:

- go to the account profile or resulting post view
- for a single post, confirm the new post appears as the latest visible post
- for a thread, confirm the newly published posts appear as the latest visible posts in the expected order
- capture the first post URL if available
- when possible, verify at least one reply-linked or sequential thread post is also visible, not just the first post

Do not claim success unless the post or thread is visibly present in the browser.

## Failure Handling

### X Not Logged In

Do not attempt login on the user's behalf unless they explicitly ask.

Return:

- a brief note that automatic posting is blocked because X is not logged in
- the final Chinese draft or thread draft

### Composer Does Not Recognize Input

If text appears in the textbox but the post button stays disabled:

- **NEVER use fill** - must use type_text
- treat this as an input-recognition failure, not a writing failure
- Press Ctrl+A to select all, then use type_text to input the complete text again in one go
- re-check both the post button and the character counter before posting

### Composer Counter Looks Wrong

If the text length is obviously short enough but X claims it is over limit or otherwise shows a broken counter:

- assume the composer state is corrupted
- refresh or reopen `https://x.com/home`
- press `n` again to reopen a fresh composer when possible
- re-enter the final text in the homepage modal composer
- do not keep retrying in the broken composer state

### Post Or Thread Is Too Long

Restructure, shorten, and retry. Do not stop at the first over-limit failure.

If using a thread:

- first split overloaded posts into additional thread posts when that improves readability
- first shorten the affected post
- then remove lower-signal details
- increasing thread length is acceptable when it makes the post sequence clearer and the user did not specify the count

### Posting Still Fails

Return:

- the final Chinese text or thread
- the exact blocker, such as disabled post button or missing login state

## Output Expectations

When successful, give a short result that includes:

- that HN top 30 was reviewed
- that software or AI items were selected
- whether the result was a single post or a thread
- that the Chinese post or thread was published to X
- the first X post URL

When blocked, give:

- a brief reason
- the final Chinese draft or thread draft

## Operating Notes

- Treat HN as a front-page signal source, not a complete market map
- Prefer a small set of strong signals over exhaustive coverage
- Favor execution reliability over perfect prose
- If the user asks for a draft only, do not auto-post
- On X, use the homepage modal composer as the standard posting path, with `n` as the preferred way to open it
- Do not trust visible text alone; the post button state and counter state are the real readiness checks
- Prefer `Ctrl + Enter` as the standard publish action, with button click only as fallback
- When the user specifies the number of thread posts up front, follow that instruction exactly
- When the user does not specify a count, default to at least `3` posts and expand further when needed to explain the signal properly
- HN usually contains enough density that a single-post summary is an exception, not the default
- After publishing, verify on profile that the new post or thread is actually published before reporting success
