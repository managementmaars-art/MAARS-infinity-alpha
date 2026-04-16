---
name: trend-scout
description: "Reddit, Hacker News, Indie Hackers에서 어제~오늘 1인 개발자/인디해커/솔로프리너 관련 인기글을 수집하고 Threads 포스트용으로 큐레이션. 트리거: '트렌드', '인기글', 'trend scout', '쓰레드 리서치', 'threads 소재', '오늘 뭐 올리지', '콘텐츠 소재', 'reddit 인기글', 'HN 인기글', '해커뉴스', '트렌드 스카우트'. /trend-scout로 실행."
---

# Trend Scout

Reddit + Hacker News + Indie Hackers에서 어제~오늘 인기글을 수집하고 Threads 포스트로 큐레이션.

## Workflow

### 1. 데이터 수집

스크립트 실행으로 Reddit 8개 서브레딧 + Hacker News top stories 수집:

```bash
bash {SKILL_DIR}/scripts/fetch-trends.sh day 10
```

결과: `/tmp/trend-scout/` JSON 파일들. 스크립트가 통합 JSON을 stdout으로 출력.

### 2. Exa MCP 보강

Indie Hackers 등 JSON API 없는 소스는 Exa로 보강. 어제 날짜를 `startPublishedDate`로 지정:

```
mcp__exa__web_search_advanced_exa({
  query: "indie hacker launched revenue solopreneur",
  includeDomains: ["indiehackers.com"],
  startPublishedDate: "{어제 YYYY-MM-DD}",
  numResults: 5
})
```

### 3. 필터링

수집 결과에서 선별. 기준 ([references/sources.md](references/sources.md) 참고):

- Reddit upvote 10+ (소규모 서브레딧 5+), HN score 50+
- 제외: 스팸, 구인글, 구체성 없는 동기부여

큐레이션 우선순위:
1. 실제 숫자 (MRR, 유저 수, 매출)
2. 반직관적 인사이트
3. 실행 가능한 전략
4. 실패/교훈 사례

### 4. Threads 포스트 작성

포맷: [references/threads-format.md](references/threads-format.md)

핵심: 500자 이내, 한국어 대화체, 핵심부터, 숫자 포함, 원문 링크 1개.

### 5. 출력

추천 포스트 3-5개:

```
## 추천 #1: {주제}
- 소스: {Reddit/HN/IH} | {서브레딧} | score {점수}
- 링크: {URL}

### Threads 초안
{500자 이내 한국어 포스트}

### 큐레이션 이유
{1줄}
```

## 날짜 범위

기본 어제~오늘. Reddit `t=day`, HN은 실시간 top, Exa는 어제 날짜 `startPublishedDate`.
