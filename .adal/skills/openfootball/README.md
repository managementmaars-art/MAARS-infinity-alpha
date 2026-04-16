# openfootball Skill

Teaches AI agents how to fetch and analyze football (soccer) match data from [openfootball](https://github.com/openfootball) — a free, open, public domain collection of match fixtures and results in JSON format covering major leagues worldwide.

## What This Skill Provides

The `SKILL.md` file gives your agent full context on:

- **JSON Data Access** — How to fetch match data via raw GitHub URLs with zero authentication
- **League Coverage** — File naming conventions for 10+ leagues across England, Germany, Spain, Italy, and France
- **Season Navigation** — How to find and access data from 2010-11 through the current season
- **JSON Schema** — Complete documentation of the match data structure including scores, rounds, dates, and times
- **Common Patterns** — Ready-to-use code examples for building league tables, filtering by team, head-to-head comparisons, and multi-season aggregation

## When to Use This Skill

Use the openfootball skill when your agent needs to:

- Fetch match results and fixtures for major European football leagues
- Build league standings/tables from raw match data
- Analyze team performance, form, or head-to-head records
- Compare results across multiple leagues or seasons
- Access World Cup, Euro, or Champions League historical data
- Work with structured football data without needing API keys or paid subscriptions

## Getting Started

### 1. No Setup Required

All openfootball data is **fully public** — no API key, authentication, or account is needed. Your agent can start fetching data immediately.

### 2. Fetch a League

Use the raw GitHub URL pattern:

```
https://raw.githubusercontent.com/openfootball/football.json/master/{season}/{code}.json
```

**Examples:**

| League | URL |
|--------|-----|
| Premier League 2024/25 | `https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json` |
| Bundesliga 2024/25 | `https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/de.1.json` |
| La Liga 2024/25 | `https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json` |
| Serie A 2024/25 | `https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/it.1.json` |
| Ligue 1 2024/25 | `https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/fr.1.json` |

### 3. Parse the Response

Responses are standard JSON. Use any JSON parser — `jq` (CLI), `requests` + `json` (Python), `fetch` (JavaScript), etc.

## Key Concepts

| Concept | Description |
|---|---|
| **League Code** | A `{country}.{division}` identifier like `en.1` (Premier League), `de.1` (Bundesliga) |
| **Season Directory** | A year or year-range like `2024-25` (cross-year) or `2025` (calendar-year) |
| **Match Object** | A JSON object with `round`, `date`, `time`, `team1`, `team2`, and `score` fields |
| **Score Object** | Contains `ft` (full-time) as `[home, away]` and optionally `ht` (half-time) |
| **Football.TXT** | The plain-text source format from which the JSON files are auto-generated |
| **Public Domain (CC0)** | All data is free to use with no restrictions or attribution required |

## Available Leagues at a Glance

| Code | League | Country |
|---|---|---|
| `en.1` | Premier League | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England |
| `en.2` | Championship | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England |
| `en.3` | League One | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England |
| `en.4` | League Two | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England |
| `de.1` | Bundesliga | 🇩🇪 Germany |
| `de.2` | 2. Bundesliga | 🇩🇪 Germany |
| `de.3` | 3. Liga | 🇩🇪 Germany |
| `es.1` | La Liga | 🇪🇸 Spain |
| `es.2` | Segunda División | 🇪🇸 Spain |
| `it.1` | Serie A | 🇮🇹 Italy |
| `it.2` | Serie B | 🇮🇹 Italy |
| `fr.1` | Ligue 1 | 🇫🇷 France |
| `fr.2` | Ligue 2 | 🇫🇷 France |

## Tips

- **Zero setup** — no keys, no auth, no account. Just fetch the URL.
- **Use `jq` for quick CLI exploration** — `curl -s URL | jq '.matches[:5]'`
- **Check for `score` before accessing** — future matches won't have scores.
- **Team names include suffixes** — use exact strings like `"Arsenal FC"`, not `"Arsenal"`.
- **Team names vary by league** — German teams use German names (`"FC Bayern München"`), English teams use English names (`"Arsenal FC"`).
- **Cache completed seasons** — they never change. Only poll the current season.
- **Build your own standings** — the data provides raw results; you compute tables, form, stats.
- **Public domain (CC0)** — use it for anything with zero restrictions.

## Resources

| Resource | URL |
|---|---|
| football.json Repo | [github.com/openfootball/football.json](https://github.com/openfootball/football.json) |
| openfootball GitHub Org | [github.com/openfootball](https://github.com/openfootball) |
| GitHub Pages Mirror | [openfootball.github.io](https://openfootball.github.io) |
| Football.TXT Spec | [github.com/openfootball/spec](https://github.com/openfootball/spec) |
| League Quick Starter | [github.com/openfootball/league-starter](https://github.com/openfootball/league-starter) |