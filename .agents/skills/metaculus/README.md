# Metaculus Skill

Teaches AI agents how to interact with [Metaculus](https://www.metaculus.com) — a forecasting platform where users predict outcomes of real-world events across science, technology, politics, economics, and more.

## What This Skill Provides

The `SKILL.md` file gives your agent full context on:

- **Authentication** — Token-based auth via `Authorization: Token <token>` header
- **REST API** — Browse posts, retrieve community predictions, submit forecasts, manage comments, and download data
- **Data model** — Posts, questions, groups, conditionals, projects, tournaments, categories, and comments
- **Question types** — Binary, multiple choice, numeric, date, and discrete questions with type-specific forecast formats
- **CDF generation** — Complete Python functions for generating and standardizing continuous CDFs (the trickiest part of the API)
- **Aggregations** — How community predictions are computed (recency-weighted, unweighted, Metaculus prediction)
- **Rate limits and error handling**

## When to Use This Skill

Use the Metaculus skill when your agent needs to:

- Browse, search, and filter prediction questions (by status, type, category, tournament, etc.)
- Read community predictions and aggregation history
- Submit forecasts — binary probabilities, multiple choice distributions, or continuous CDFs
- Withdraw active forecasts
- Read and post comments on questions
- Download forecast data as CSVs for analysis
- Monitor trending questions or questions with large probability movement
- Participate in tournaments
- Paginate through large result sets

## Getting Started

### 1. Get API Access

**All endpoints require authentication.** There are no public/unauthenticated endpoints.

1. Create an account at [metaculus.com](https://www.metaculus.com).
2. Go to [Account Settings → API Access](https://www.metaculus.com/accounts/settings/account/#api-access).
3. Copy (or generate) your API token.

### 2. Environment Variables

Never hardcode tokens. Store credentials as environment variables or in a `.env` file:

```
METACULUS_API_TOKEN=your-token-here
```

### 3. Make Your First Request

```bash
curl -s "https://www.metaculus.com/api/posts/?limit=5&order_by=-published_at&with_cp=true" \
  -H "Authorization: Token $METACULUS_API_TOKEN" | jq '.results[] | {id, title, status}'
```

## Key Concepts

| Concept | Description |
|---|---|
| **Post** | The top-level feed entity. Wraps a question, group of questions, conditional pair, or notebook. |
| **Question** | A single forecastable item. Types: `binary`, `multiple_choice`, `numeric`, `discrete`, `date`. |
| **Group of Questions** | Multiple related sub-questions in a single post (e.g., yearly forecasts). |
| **Conditional** | A pair of questions: "If [condition], what is P(child)?" — with yes/no variants. |
| **Community Prediction** | Aggregated forecast from all users. Methods: `recency_weighted`, `unweighted`, `metaculus_prediction`. |
| **Project / Tournament** | Containers for posts. Tournaments have prize pools and leaderboards. |
| **CDF** | Cumulative Distribution Function — the format for continuous/numeric/date/discrete forecasts (typically 201 floats). |
| **Scaling** | Defines how a question's real-world range maps to the internal [0, 1] CDF space. Can be linear or logarithmic. |
| **Resolution** | The actual outcome once known: `yes`/`no` for binary, a number, date, or option name for others. |

## API at a Glance

All endpoints use a single base URL:

| Component | URL |
|---|---|
| **REST API** | `https://www.metaculus.com/api/` |

### Endpoint Categories

| Category | Endpoints | Description |
|---|---|---|
| **Feed** | `GET /api/posts/`, `GET /api/posts/{id}/` | Browse and retrieve posts with filters |
| **Forecasting** | `POST /api/questions/forecast/`, `POST /api/questions/withdraw/` | Submit or withdraw predictions |
| **Comments** | `GET /api/comments/`, `POST /api/comments/create/` | Read and post comments |
| **Data** | `GET /api/posts/{id}/download-data/`, `GET /api/projects/{id}/download-data/` | Download CSV data exports |

## Tips

- **All requests require auth** — include `Authorization: Token <token>` on every request
- **Question ID ≠ Post ID** — forecasts use `question.id`, not `post.id`. Always fetch the post first to get the question ID.
- **Pass `with_cp=true`** when listing posts if you need community predictions — aggregations are empty by default
- **CDF generation is the hardest part** — use the Python helper functions in `SKILL.md` and always run `standardize_cdf()` before submitting
- **Probabilities are 0–1** — a probability of 0.65 means 65% chance
- **All timestamps are ISO 8601** — e.g., `"2024-10-16T12:56:51.751385Z"`
- **Multiple choice probabilities must sum to 1.0** — the API will reject submissions that don't
- **Date questions use unix timestamps** in `scaling.range_min` / `scaling.range_max` — convert dates before mapping to CDF
- **For groups, use the detail endpoint** — the list endpoint with `with_cp=true` only returns CP for the top 3 sub-questions
- **Paginate with `limit` and `offset`** — don't try to fetch everything in one request
- **Respect rate limits** — implement exponential backoff on 429 responses
- **Use `order_by=-hotness`** to find trending questions, or `order_by=-weekly_movement` for questions with recent probability shifts

## Resources

| Resource | URL |
|---|---|
| Metaculus Platform | [metaculus.com](https://www.metaculus.com) |
| API Documentation | [metaculus.com/api](https://www.metaculus.com/api/) |
| Account Settings (API Token) | [metaculus.com/accounts/settings](https://www.metaculus.com/accounts/settings/account/#api-access) |
| GitHub (Source & Issues) | [github.com/Metaculus/metaculus](https://github.com/Metaculus/metaculus/issues) |
| Contact | [api-requests@metaculus.com](mailto:api-requests@metaculus.com) |