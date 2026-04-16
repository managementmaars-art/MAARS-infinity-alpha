# 📣 OpenClaw 하이브리드 마케팅 전략

> 작성일: 2026-02-18  
> 대상 레포: `openclaw-self-healing` + `openclaw-self-evolving`  
> 목표: 6개월 내 GitHub Stars 100+

---

## 1. 크로스 프로모션 전략

### 1.1 두 레포 상호 링크 구조

#### `openclaw-self-healing` README에 추가할 섹션

README 하단 "Related Projects" 섹션에 다음 문구 삽입:

```markdown
## 🔗 Related Projects

> **[openclaw-self-evolving](https://github.com/Ramsbaby/openclaw-self-evolving)** — 
> Self-Healing이 시스템을 *보호*한다면, Self-Evolving은 시스템을 *진화*시킵니다.  
> OpenClaw 스킬이 스스로 업그레이드되는 AI 진화 엔진.
```

위치: "Contributing" 섹션 바로 위 (README 하단 20% 영역)

#### `openclaw-self-evolving` README에 추가할 섹션

```markdown
## 🔗 Related Projects

> **[openclaw-self-healing](https://github.com/Ramsbaby/openclaw-self-healing)** — 
> Self-Evolving이 스킬을 *업그레이드*한다면, Self-Healing은 시스템을 *복구*합니다.  
> 4단계 자동 장애복구 시스템 — 새벽 3시에 깨어나지 마세요.
```

### 1.2 GitHub Topics 태그 최적화

두 레포가 **서로 다른 키워드**로 다양한 검색 유입을 커버한다:

| 레포 | 권장 Topics 태그 (10개 이내) |
|------|------|
| **self-healing** | `self-healing`, `crash-recovery`, `watchdog`, `launchagent`, `automation`, `claude-code`, `openclaw`, `devops`, `macos`, `reliability` |
| **self-evolving** | `self-evolving`, `ai-agent`, `skill-upgrade`, `autonomous`, `openclaw`, `claude`, `meta-programming`, `ai-tools`, `llm`, `workflow-automation` |

> **전략**: self-healing은 DevOps/인프라 키워드로 SRE/개발자 유입  
> self-evolving은 AI Agent/LLM 커뮤니티 키워드로 AI 연구자 유입

### 1.3 "Awesome OpenClaw Skills" 리스트 기여

**단기 액션:**
1. `awesome-claude-code` 또는 `awesome-ai-agents` 레포에 두 프로젝트 PR 제출
2. 형식: `[OpenClaw Self-Healing](링크) — 4-tier crash recovery for OpenClaw Gateway`
3. GitHub에서 "awesome-openclaw" 검색 → 없으면 직접 `awesome-openclaw-skills` 레포 생성

**"Awesome" 레포 직접 생성 전략:**
```
awesome-openclaw-skills/
├── README.md  ← 큐레이션 리스트 (self-healing, self-evolving 모두 등재)
├── CONTRIBUTING.md
└── categories/
    ├── reliability.md
    └── ai-agents.md
```
이 레포 자체가 세 번째 마케팅 채널이 됨.

---

## 2. ClawHub 스킬 SEO 전략

> ⚠️ ClawHub 공개 검색 알고리즘 문서 부재 — 일반 마켓플레이스 SEO 원칙 + OpenClaw 커뮤니티 관찰 기반

### 2.1 self-healing 스킬 등록 최적화

**스킬명:** `OpenClaw Self-Healing — 4-Tier Crash Recovery`

**추천 태그 (5~8개):**
```
self-healing, crash-recovery, watchdog, auto-restart, gateway-recovery, 
reliability, launchagent, systemd
```

**Description 최적화 (영어 + 핵심 키워드 선배치):**
```
Automatically detects and recovers from OpenClaw Gateway crashes using 
4 escalating tiers: instant restart → root-cause diagnosis → AI-powered fix → 
human escalation. No more 3 AM pager alerts.

Features:
- LaunchAgent/systemd KeepAlive (0-30s recovery)
- doctor --fix auto-remediation
- Claude Code autonomous diagnosis
- macOS & Linux support
```

**SEO 원칙:**
- 첫 두 문장에 핵심 키워드 집중 ("self-healing", "crash recovery", "auto-restart")
- 숫자와 구체적 지표 포함 ("0-30s", "4 tiers")
- 문제-해결 프레이밍 (Pain → Solution)

### 2.2 self-evolving 스킬 등록 최적화

**스킬명:** `OpenClaw Self-Evolving — Autonomous Skill Upgrader`

**추천 태그 (5~8개):**
```
self-evolving, ai-agent, autonomous, skill-upgrade, meta-ai, 
claude-code, workflow-automation, llm-tools
```

**Description 최적화:**
```
Your OpenClaw skills evolve themselves. Self-Evolving monitors skill 
performance, identifies improvement opportunities, and autonomously 
upgrades skill logic using Claude Code.

Features:
- Autonomous skill performance monitoring
- AI-driven code improvement suggestions
- Safe staging + rollback mechanism
- Compatible with any OpenClaw skill
```

**SEO 원칙:**
- "autonomous", "self-evolving", "AI agent" — 현재 AI 트렌드 키워드 선점
- 차별화 포인트 명시: "evolves themselves" (의인화로 기억에 남음)
- 호환성 언급으로 광범위 적용 가능성 어필

### 2.3 ClawHub 공통 최적화 원칙

1. **스킬 아이콘/썸네일**: 고대비, 텍스트 최소화, 컨셉 직관적 표현
2. **버전 업데이트 주기**: 월 1회 이상 업데이트 → "활성 프로젝트" 신호
3. **사용 예제**: README에 ClawHub 설치 원클릭 배지 추가
4. **리뷰 유도**: 설치 후 README에 "⭐ ClawHub에서 리뷰 남기기" CTA 포함

---

## 3. Reddit / Hacker News 런칭 타임라인

### 3.1 서브레딧별 전략

#### r/selfhosted (구독자 ~580K)
- **AI 관련 규칙**: 2025년 7월 업데이트 기준 — AI 관련 포스팅 **전면 허용** (단, flair 필수)
  - "AI-Slop" 신고는 실제로 규칙 위반 아님
  - `[Self-Promotion]` flair 선택 또는 `[AI-Assisted]` flair 사용
- **톤**: 기술적, 문제 해결 중심. "저 이거 만들었어요" → "새벽 3시 장애로 고통받다가 만들었습니다"
- **포스팅 형식**: 스크린샷 + 짧은 데모 GIF 필수. 텍스트만이면 묻힘
- **최적 시간**: 화~목 오전 9-11시 (UTC), 금요일 피크타임 노리기

#### r/AI_Agents (구독자 성장중)
- **자기홍보 주의**: 커뮤니티 사이드바에 "promote personal projects" 제한 명시
- **전략**: 직접 홍보보다 "AI가 스스로 진화하는 시스템을 만드는 방법" 교육 포스트
- **허용 형식**: 기술 설명 + GitHub 링크 자연스럽게 포함
- **톤**: 학술적, 아키텍처 토론 유도

#### r/MachineLearning / r/LocalLLaMA
- self-evolving 프로젝트 적합
- "autonomous skill improvement using LLMs" 관점으로 어프로치

#### r/devops / r/sysadmin
- self-healing 프로젝트 적합
- "watchdog beyond simple restart" 관점

#### Hacker News (Show HN)
- **형식**: `Show HN: OpenClaw Self-Healing – 4-tier autonomous crash recovery`
- **규칙**: 첫 댓글에 프로젝트 배경과 기술적 결정 이유 상세 설명 필수
- **최적 시간**: 월~화 오전 9-11시 (ET) = 한국시간 화~수 밤 11시-새벽 1시
- **주의**: HN은 AI wrapper에 피로감 → "autonomous"보단 "fault isolation architecture" 기술 프레이밍

### 3.2 두 프로젝트 시차 런칭 전략

**동시 런칭 금지** — 이유:
- 하나의 PR 사이클이 완료되기 전에 또 다른 프로젝트가 노출되면 attention split
- 커뮤니티가 첫 번째 프로젝트에 기여/피드백 줄 시간 부족

**권장: 4주 시차**

```
Week 1-2: openclaw-self-healing 런칭
  └─ r/selfhosted, r/devops, r/sysadmin
  └─ HN Show HN
  └─ 피드백 수렴, 이슈 대응, README 개선

Week 3-4: openclaw-self-evolving 런칭
  └─ r/AI_Agents, r/LocalLLaMA
  └─ self-healing README에 self-evolving 링크 추가 (크로스 프로모션 활성화)
  └─ HN Show HN (두 번째)
```

### 3.3 포스팅 템플릿

**r/selfhosted용 (self-healing):**
```
Title: I got tired of being paged at 3 AM for OpenClaw crashes, so I built a self-healing system

OpenClaw Gateway는 가끔 특이한 이유로 죽습니다 — corrupted config, 
DB 연결 stale, API rate limit... 단순 restart watchdog은 이 케이스를 못 잡습니다.

그래서 4단계 자동복구 시스템을 만들었습니다:
1. LaunchAgent KeepAlive (0-30초 즉시 재시작)
2. doctor --fix 자동 진단/수정
3. Claude Code 자율 AI 진단
4. 그래도 안 되면 → 사람 호출

GitHub: [링크]

영어권 커뮤니티는 영어로, 로컬 커뮤니티는 한국어로 포스팅.
```

---

## 4. 6개월 성장 로드맵

### Month 1-2: 기반 다지기 (목표: ⭐ 30)

**핵심 원칙**: "친구 100명 먼저, 낯선 이 나중에"

#### 주요 액션
- [ ] README 완성도 극대화 (30초 데모 GIF, 명확한 설치 가이드)
- [ ] GitHub Topics 10개 최적화 (위 목록 적용)
- [ ] 지인 네트워크 활용 (개발자 친구, 커뮤니티 지인에게 직접 DM)
- [ ] Dev.to / Hashnode 첫 블로그 포스트: "OpenClaw 게이트웨이가 새벽 3시에 죽었을 때"
- [ ] self-healing 레포 1차 런칭: r/selfhosted + HN Show HN
- [ ] ClawHub에 self-healing 스킬 등록 (SEO 최적화 적용)
- [ ] CONTRIBUTING.md 정비 (첫 기여자 진입장벽 낮추기)
- [ ] 이슈 응답 시간: 24시간 이내 유지

**Stars 예측**: 개인 네트워크 15-20 + 커뮤니티 유입 10-15 = **30+**

---

### Month 3-4: 커뮤니티 빌딩 (목표: ⭐ 60)

**핵심 원칙**: "도움 먼저, 홍보 나중 (70:30 법칙)"

#### 주요 액션
- [ ] self-evolving 레포 런칭: r/AI_Agents, r/LocalLLaMA + HN
- [ ] 크로스 프로모션 활성화: 두 README 상호 링크 완성
- [ ] `awesome-openclaw-skills` 레포 생성 및 홍보
- [ ] Stack Overflow / GitHub Discussions에서 관련 질문에 helpful 답변 (프로젝트 자연스럽게 언급)
- [ ] ClawHub self-evolving 스킬 등록
- [ ] 첫 외부 기여자 온보딩 (Good First Issue 라벨 5개 이상)
- [ ] 블로그 포스트 2편 추가:
  - "AI 에이전트가 스스로를 업그레이드하는 방법"
  - "OpenClaw 시스템 아키텍처 딥다이브"
- [ ] Twitter/X 개발 업데이트 주 2회 (기술적 insight 중심)

**Stars 예측**: Month 2 기반 30 + 신규 유입 30 = **60+**

---

### Month 5-6: 바이럴 시도 (목표: ⭐ 100)

**핵심 원칙**: "하나의 바이럴 콘텐츠가 6개월 노력을 앞지른다"

#### 주요 액션
- [ ] **데모 비디오 제작**: "AI가 스스로 고치는 시스템" 5분 YouTube 데모
  - OpenClaw crash 시뮬레이션 → 자동복구 → 스킬 자가 업그레이드 흐름
- [ ] **HN Front Page 재도전**: "Ask HN: How do you handle AI agent self-improvement safely?"
- [ ] **Product Hunt 런칭**: 두 프로젝트 묶어서 "OpenClaw AI Suite" 포지셔닝
- [ ] **기술 블로그 외부 기고**:
  - LogRocket, Better Programming, Towards AI
  - 제목: "Building Self-Healing AI Systems with Claude Code"
- [ ] **GitHub Trending 진입 시도**:
  - 특정 주에 커뮤니티 집중 활성화로 trending 진입
  - 한국 개발자 커뮤니티 (okky.kr, velog.io) 동시 공략
- [ ] **Milestone 축하 포스트**: ⭐50 달성 시 "50 stars 회고" 포스트 → 추가 바이럴

**Stars 예측**: Month 4 기반 60 + 바이럴 효과 40 = **100+**

---

## 5. 성과 측정 지표 (KPI)

| 지표 | Month 2 | Month 4 | Month 6 |
|------|---------|---------|---------|
| GitHub Stars (합계) | 30 | 60 | 100 |
| ClawHub 스킬 설치수 | 10 | 30 | 80 |
| README 방문자 (월간) | 500 | 1,500 | 5,000 |
| 이슈/PR 외부 기여 | 2 | 8 | 20 |
| 블로그 포스트 | 1 | 3 | 6 |

---

## 6. 리스크 & 대응책

| 리스크 | 대응책 |
|--------|--------|
| Reddit 자기홍보 제거 | 교육 콘텐츠 포지셔닝, 직접 홍보 최소화 |
| HN 저조한 반응 | 포스팅 시간 최적화 재시도, 다른 앵글로 접근 |
| AI 프로젝트 포화 상태 | 기술 차별화 포인트 강조 (단순 wrapper ❌, 아키텍처 ✅) |
| Stars 정체 | Product Hunt 런칭으로 새로운 유입 채널 개척 |
| 기여자 부재 | Good First Issue 적극 생성, mentoring 제공 |

---

## 7. 즉시 실행 액션 (이번 주)

1. **두 레포 GitHub Topics 즉시 업데이트** (15분)
2. **README에 "Related Projects" 섹션 추가** (30분)
3. **ClawHub self-healing 스킬 등록** (1시간)
4. **Dev.to 계정 생성 + 첫 포스트 초안 작성** (2시간)
5. **r/selfhosted 포스팅 준비** (GIF 제작 포함, 3시간)

---

*이 문서는 실제 웹 검색 데이터 (2025-2026 기준) + 오픈소스 마케팅 best practice를 기반으로 작성되었습니다.*  
*r/selfhosted AI 규칙: 2025년 7월 업데이트 확인 완료 — AI 포스팅 전면 허용, flair 필수.*
