---
name: google-serper-search
description: Search the web, news, and images through the Serper API. Use when the user asks to search the web, find current information online, verify recent facts, search Google, find images, or gather search results with source links.
---

# Google Serper Search

Use `scripts/serper_search.py` to call the Serper API and return JSON search results.

## Check configuration

Confirm `SERPER_API_KEY` is available before searching.

Run:

```bash
printenv SERPER_API_KEY
```

If the variable is empty, read [references/configuration.md](references/configuration.md) and set it in the current shell or shell profile before continuing.

## Run searches

Use:

```bash
python3 scripts/serper_search.py "query"
```

Use filters when the request needs them:

```bash
python3 scripts/serper_search.py "query" --type news --gl us --hl en --tbs "past week"
```

Supported `--type` values:

- `search`
- `images`
- `videos`
- `places`
- `maps`
- `reviews`
- `news`
- `shopping`
- `lens`
- `scholar`
- `patents`
- `autocomplete`

Aliases:

- `web` -> `search`
- `image` -> `images`
- `img` -> `images`

Supported `--tbs` shortcuts:

- `past hour`
- `past 24 hours`
- `past week`
- `past month`
- `past year`

Use `--gl` for country and `--hl` for language when the request needs regional or language-specific results.

## Interpret results

Read [references/api_response.md](references/api_response.md) when you need the result schema.

For web and news results, prioritize:

- `knowledgeGraph`
- `organic`
- `peopleAlsoAsk`
- `relatedSearches`

For image results, prioritize:

- image title
- `imageUrl`
- `thumbnailUrl`
- dimensions
- source page

## Present the answer

Summarize the most relevant results instead of dumping raw JSON unless the user asks for the raw response.

Include source links in the final answer.

Call out missing configuration or API errors explicitly when the script returns an `error` field.
