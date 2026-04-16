# 데이터 소스 설정

## Reddit 서브레딧

| 서브레딧 | 주제 | 우선순위 |
|---------|------|---------|
| r/Solopreneur | 솔로프리너 전반 | 높음 |
| r/indiehackers | 인디해커 | 높음 |
| r/SaaS | SaaS 빌딩 | 높음 |
| r/Entrepreneur | 창업 전반 | 중간 |
| r/ClaudeAI | Claude/Anthropic | 중간 |
| r/ChatGPT | ChatGPT/OpenAI | 중간 |
| r/nextjs | Next.js 개발 | 낮음 |
| r/GeminiAI | Gemini/Google AI | 낮음 |

### Reddit JSON API
```
https://www.reddit.com/r/{subreddit}/top.json?t=day&limit=10
https://www.reddit.com/r/{subreddit}/hot.json?limit=10
```
- User-Agent 필수: `TrendScout/1.0`
- Rate limit: 10회/분
- 인증 불필요

### 멀티 서브레딧 (한 번에 조회)
```
https://www.reddit.com/r/Solopreneur+indiehackers+SaaS/top.json?t=day&limit=20
```

## Hacker News

### Firebase API (공개, 무제한)
```
# Top stories IDs
https://hacker-news.firebaseio.com/v0/topstories.json

# Individual story
https://hacker-news.firebaseio.com/v0/item/{id}.json

# Best stories
https://hacker-news.firebaseio.com/v0/beststories.json

# New stories
https://hacker-news.firebaseio.com/v0/newstories.json
```

### 응답 예시
```json
{
  "id": 12345,
  "type": "story",
  "title": "Show HN: My solo SaaS hit $10k MRR",
  "url": "https://example.com",
  "score": 234,
  "by": "username",
  "descendants": 89
}
```

## Indie Hackers

공식 API 없음. 대안:
1. **Exa MCP**: `mcp__exa__web_search_exa` — `includeDomains: ["indiehackers.com"]`로 최신 글 검색
2. **미인증 JSON**: `https://www.indiehackers.com/feed.json` (가용 시)

### Exa 검색 예시
```
query: "indie hacker launched revenue milestone"
includeDomains: ["indiehackers.com"]
startPublishedDate: "2026-03-14"
numResults: 5
```

## 필터링 기준

### 포함 (score 기준)
- Reddit: upvote 10+ (소규모 서브레딧은 5+)
- HN: score 50+
- Indie Hackers: 관련성 기반 (Exa 시맨틱)

### 제외
- `[deleted]`, `[removed]` 포스트
- selftext에 URL만 있는 스팸
- "hiring", "looking for cofounder" 같은 구인글
