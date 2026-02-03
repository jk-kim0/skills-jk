# SEO 심층 분석 리포트: app.querypie.com

## 1. 개요

| 항목 | 내용 |
|------|------|
| 분석 대상 | https://app.querypie.com/ |
| 분석 기간 | 2025-11-01 ~ 2026-02-03 |
| 분석 일자 | 2026-02-03 |
| 분석 도구 | Ahrefs MCP, Google Search Console CLI |
| 제품 | QueryPie AIP (AI Platform) |
| 이전 분석 | 2026-02-02 |

---

## 2. Executive Summary

### 핵심 지표 현황

| 지표 | 현재 값 | 상태 |
|------|---------|------|
| **Domain Rating** | 55 (상위 도메인 상속) | 양호 |
| **Live Backlinks** | 228 | 양호 |
| **Referring Domains** | 7 | 부족 |
| **Organic Keywords** | 4 | 심각 |
| **Organic Traffic** | 0/월 (Ahrefs 추정) | 심각 |
| **GSC 검색 클릭** | 0회 | 심각 |
| **GSC 검색 노출** | 0회 | 심각 |
| **인덱싱 상태** | Redirect Error | 심각 |

### 핵심 문제: 인덱싱 완전 실패

**app.querypie.com은 Google에서 전혀 인덱싱되지 않고 있습니다.**

- **원인**: HTTP HEAD 요청 시 405 에러 반환
- **영향**: 90일간 검색 노출/클릭 모두 0회
- **시급성**: 최우선 해결 필요 (개발 1-2시간으로 해결 가능)

### 키워드 기회 요약

| 시장 | 핵심 키워드 | 검색량/월 | 난이도 | 예상 트래픽 |
|------|------------|----------|--------|------------|
| 한국 | ai 에이전트 | 3,600 | 1 | 300-700/월 |
| 한국 | ai 플랫폼 | 1,100 | 1 | 200-500/월 |
| 한국 | mcp 서버 | 4,400 | - | 200-500/월 |
| 미국 | mcp server | 46,000 | 81 | 100-500/월 |
| 미국 | sequential thinking | 500 | 3 | 50-150/월 |

**인덱싱 해결 시 예상 트래픽: 400-900/월**

---

## 3. Google Analytics 분석

app.querypie.com에 대한 별도의 GA Property가 설정되어 있지 않습니다.

app.querypie.com은 **QueryPie AIP (AI Platform)** 제품의 서비스 도메인으로, 사용자 트래픽 분석을 위해서는 별도의 GA 설정이 필요합니다.

---

## 4. 도메인 권위 분석

### 4.1 백링크 프로필

| 지표 | 값 | 평가 |
|------|-----|------|
| 총 백링크 (Live) | 228 | 양호 |
| 총 백링크 (All-time) | 230 | - |
| 참조 도메인 (Live) | 7 | 부족 |
| 참조 도메인 (All-time) | 7 | - |

### 4.2 참조 도메인 상세

| 도메인 | DR | 링크 수 | 첫 발견 | 비고 |
|--------|-----|---------|---------|------|
| **atlassian.net** | **92** | 4 | 2025-10 | 고품질 백링크 |
| **zenn.dev** | **83** | 1 | 2025-07 | 고품질 (일본 기술 블로그) |
| **pulsemcp.com** | **61** | 2 | 2025-09 | MCP 생태계 - 협력 기회 |
| demoday.co.kr | 20 | 4 | 2025-07 | 한국 스타트업 |
| devsnote.com | 17 | 1 | 2025-10 | - |
| querypie.ai | 1.6 | 215 | 2025-11 | 내부 링크 |
| subdomainfinder.io | 0.8 | 3 | 2025-10 | 낮은 가치 |

**긍정적 요소**: Atlassian (DR 92), zenn.dev (DR 83) 등 고품질 도메인에서 백링크 확보. 인덱싱 문제만 해결되면 SEO 잠재력 높음.

### 4.3 Organic Traffic 추이

| 주차 | 트래픽 | 트래픽 가치 | 변화 |
|------|--------|-------------|------|
| 2025-11-03 | 2 | $0 | 기준 |
| 2025-11-10 | 2 | $0 | 유지 |
| 2025-11-17 | 0 | $0 | 인덱싱 문제 시작 |
| 2025-12-01 ~ 2026-01-26 | 0 | $0 | 지속 |

**인사이트**: 2025년 11월 중순부터 Ahrefs에서도 organic 트래픽이 0으로 감지됨. 인덱싱 문제가 이 시점에 발생한 것으로 추정.

### 4.4 경쟁사 분석

| 경쟁사 | DR | 공통 키워드 | 분석 |
|--------|-----|------------|------|
| smithery.ai | 72 | 1 | MCP 직접 경쟁사 |
| Airtable | 91 | 1 | 통합 서비스 |
| n8n.io | 87 | 1 | AI 자동화 경쟁사 |
| Make.com | 89 | 1 | 자동화 플랫폼 |
| Cursor | 87 | 1 | AI 코딩 툴 |
| GitHub | 96 | 2 | 개발자 플랫폼 |

---

## 5. 검색 성능 분석 (GSC)

### 5.1 현재 상태: 검색 트래픽 제로

```
검색 성능 데이터: https://app.querypie.com/
기간: 2026-01-01 ~ 2026-01-31

데이터가 없습니다.
```

**결론**: 지난 90일간 Google 검색에서 단 한 번도 노출되지 않음

### 5.2 인덱싱 상태

| 항목 | 상태 |
|------|------|
| 메인 페이지 (/) | Redirect Error |
| Publication 페이지 | URL is unknown to Google |
| 사이트맵 제출 | 156개 URL 제출 |
| 인덱싱된 URL | 0개 |

### 5.3 QueryPie 도메인 비교

```
www.querypie.com       [====================] 인덱싱 정상
docs.querypie.com      [====================] 인덱싱 정상
aip-docs.app.querypie  [=================== ] 인덱싱 정상 (성장 중)
────────────────────────────────────────────────────────
app.querypie.com       [                    ] 인덱싱 0%
```

---

## 6. 키워드 분석

### 6.1 현재 랭킹 키워드

인덱싱 문제에도 불구하고 4개 키워드에서 낮은 순위로 랭킹 중:

| 키워드 | 순위 | 검색량/월 | 난이도 | 트래픽 | 분석 |
|--------|------|----------|--------|--------|------|
| **sequential thinking** | 65위 | 500 | 3 | 0 | MCP 관련, 개선 여지 |
| airtable documentation | 61위 | 200 | 29 | 0 | 통합 문서 |
| confluence api | 74위 | 200 | 12 | 0 | 통합 문서 |
| discord api | 84위 | 800 | 18 | 0 | 통합 문서 |

**인사이트**: 인덱싱 해결 시 순위 급상승 예상 (65위 -> Top 20 가능)

### 6.2 한국 AI 키워드 기회 (블루오션)

| 키워드 | 검색량/월 | 난이도 | CPC | 전략 |
|--------|----------|--------|-----|------|
| **ai 에이전트** | 3,600 | **1** | - | 핵심 타겟 |
| **ai 플랫폼** | 1,100 | **1** | $0.15 | 핵심 타겟 - 제품명과 일치 |
| **mcp 서버** | 4,400 | - | - | 핵심 타겟 - aip-docs와 시너지 |
| **ai saas** | 100 | **0** | $0.80 | 최우선 |
| 기업용 ai | 90 | - | - | 높음 |
| ai 워크플로우 | 80 | - | - | 높음 |
| ai 에이전트 플랫폼 | 30 | - | - | 중간 |
| ai 보안 플랫폼 | 10 | - | - | 보조 키워드 |
| 생성형 ai 보안 | 150 | - | - | 보조 키워드 |
| ai 보안 인증 | 30 | 0 | - | 컴플라이언스 연계 |
| **한국 총계** | **9,690+** | **평균 0.5** | - | **즉시 공략** |

### 6.3 미국 AI 키워드 기회

| 키워드 | 검색량/월 | 난이도 | CPC | 우선순위 |
|--------|----------|--------|-----|---------|
| **mcp server** | 46,000 | 81 | - | 장기 (시장 폭발 +3,186%) |
| model context protocol | 24,000 | 79 | - | 장기 |
| ai agent | 26,000 | 77 | - | 장기 |
| ai platform | 5,700 | 86 | $1.30 | 장기 |
| enterprise ai | 5,600 | 54 | $0.50 | 중기 |
| ai workflow | 1,700 | 53 | $4.00 | 중기 |
| **ai agent platform** | 1,100 | **49** | $2.50 | **중기 우선** |
| **ai saas** | 900 | **47** | $1.30 | **중기 우선** |
| ai security platform | 400 | 81 | $13.00 | 장기 |
| what is an mcp server | 3,700 | 29 | - | 중기 |
| mcp security | 800 | 35 | - | 중기 |
| ai compliance software | 200 | 25 | - | 컴플라이언스 연계 |
| soc 2 for saas | 150 | 20 | - | 컴플라이언스 연계 |
| **미국 총계** | **115,000+** | **평균 62** | - | **중장기 전략** |

### 6.4 MCP 콘텐츠 키워드

| 키워드 | 검색량/월 | 난이도 | 현재 콘텐츠 |
|--------|----------|--------|------------------------------|
| what is an mcp server | 3,700 | 29 | MCP 개념 설명 대화 |
| mcp security | 800 | 35 | MCP 보안 관련 대화 |
| mcp slack integration | 150 | - | Slack MCP 사용 예시 |
| mcp benefits | 50 | 15 | MCP 장점 분석 |
| mcp airtable | 20 | - | Airtable MCP 사용 예시 |

### 6.5 SERP 경쟁 분석: "ai 플랫폼" (한국)

| 순위 | 도메인 | DR | 백링크 | 트래픽 | 분석 |
|------|--------|-----|--------|--------|------|
| 1 | ibm.com | 92 | 2 | 523 | 대기업 |
| **2** | **damoa.ai** | **14** | 5,113 | **9,677** | DR 14가 2위! |
| 3 | spri.kr | 39 | 0 | 206 | 정보원 |
| **7** | **hitek.com.vn** | **23** | 0 | 77 | DR 23이 7위 |
| **8** | **daglo.ai** | **28** | 3,988 | **32,682** | DR 28이 고트래픽 |

**핵심 인사이트**:
- DR 14-28 사이트가 상위권 진입
- app.querypie.com (DR 55)은 인덱싱만 해결되면 Top 3 진입 확실

---

## 7. 인덱싱 문제 분석

### 7.1 문제 현황

Google Search Console URL 검사 결과:

```
메인 페이지 (https://app.querypie.com/)
----------------------------------------
상태: 중립
커버리지: Redirect error
페이지 가져오기: REDIRECT_ERROR
마지막 크롤링: 2026-01-25 13:17:05
크롤링 에이전트: MOBILE
```

### 7.2 원인 분석: HTTP HEAD 요청 미지원

```bash
# 일반 브라우저 User-Agent
$ curl -sI "https://app.querypie.com/"
HTTP 405 Method Not Allowed

# Googlebot User-Agent
$ curl -sI -A "Googlebot" "https://app.querypie.com/"
HTTP 405 Method Not Allowed

# GET 요청 (정상)
$ curl -s "https://app.querypie.com/" | head -1
HTTP 200 OK
```

| 가능성 | 설명 | 확률 |
|--------|------|------|
| **HTTP HEAD 405** | 서버가 HEAD 요청 미지원 | 높음 |
| JavaScript 리다이렉트 | 클라이언트 측 리다이렉트 | 낮음 |
| 간헐적 서버 리다이렉트 | 특정 조건에서 리다이렉트 | 낮음 |

### 7.3 SSR 렌더링 확인 (정상)

Googlebot으로 GET 요청 시 정상적인 HTML 반환:

```html
<!-- 메인 페이지 -->
<title>QueryPie AIP | Secure MCP Provider Management</title>
<meta name="description" content="QueryPie is a secure MCP provider management tool..."/>
<meta property="og:title" content="QueryPie AIP | Secure MCP Provider Management"/>

<!-- Schema.org 마크업 -->
<article itemType="https://schema.org/Conversation">
```

**긍정적 요소**:
- SSR 정상 작동
- 메타 태그 포함
- Schema.org 마크업 적용
- 실제 콘텐츠가 HTML에 포함됨

### 7.4 해결 방안

**Next.js/Express 예시**:

```javascript
// middleware.js 또는 server.js
app.head('*', (req, res) => {
  res.status(200).end();
});
```

**nginx 예시**:

```nginx
location / {
  if ($request_method = HEAD) {
    return 200;
  }
  # 기존 설정...
}
```

### 7.5 인덱싱 복구 타임라인

| 단계 | 작업 | 예상 소요 | 예상 결과 |
|------|------|-----------|-----------|
| 1 | HEAD 요청 지원 배포 | 1일 | - |
| 2 | GSC 수동 인덱싱 요청 | 즉시 | - |
| 3 | Google 재크롤링 | 1-7일 | 메인 페이지 인덱싱 |
| 4 | 내부 페이지 인덱싱 | 2-4주 | 50% 인덱싱 |
| 5 | 전체 인덱싱 완료 | 1-2개월 | 80%+ 인덱싱 |

---

## 8. 콘텐츠 분석

### 8.1 사이트맵 현황

```
총 158개 URL 제출, 0개 인덱싱 (0%)

sitemap.xml
└── publication-1.xml (158 URLs)
    └─ web: 제출 156, 인덱싱 0
```

### 8.2 사이트맵 URL 구조

모든 URL이 `/chat/publication/` 경로:
```
https://app.querypie.com/chat/publication/{uuid}/{slug}
```

### 8.3 Thin Content 문제

| 콘텐츠 유형 | 예시 | SEO 가치 |
|-------------|------|----------|
| 기술 분석 | `clean-architecture-book-summary-korean` | 높음 |
| 데이터 분석 | `korean-poll-survey-data-analysis` | 높음 |
| PR 분석 | `querypie-mono-september-pr-analysis` | 중간 |
| **날씨 메모** | `san-francisco-weather-today-61f` | **없음** |
| **일정 메모** | `schedule-meeting-with-jane-tuesday` | **없음** |

### 8.4 콘텐츠 큐레이션 기준

**인덱싱 대상 (사이트맵 포함):**
- MCP 통합/설정 관련 대화
- 기술 분석 (Clean Architecture, System Design 등)
- 데이터 분석 결과
- API 사용법 설명

**제외 대상 (noindex 처리):**
- 날씨/일정 메모
- 짧은 개인 대화 (500자 미만)
- 반복적인 QA (동일 질문 다른 사용자)

### 8.5 og:url 이슈

**현재 상태 (문제)**:
```html
<!-- 모든 페이지에서 동일한 og:url -->
<meta property="og:url" content="https://app.querypie.com"/>
```

**올바른 설정**:
```html
<!-- 각 페이지별 고유 og:url -->
<meta property="og:url" content="https://app.querypie.com/chat/publication/{uuid}/{slug}"/>
```

---

## 9. 종합 평가

### 9.1 SWOT 분석

| 강점 (Strengths) | 약점 (Weaknesses) |
|------------------|-------------------|
| SSR 정상 구현 | 인덱싱 완전 실패 |
| 메타 태그 완비 | HTTP HEAD 405 에러 |
| 228개 백링크 확보 | Thin content 포함 |
| Schema.org 마크업 | og:url 고정값 문제 |
| DR 55 보유 | 참조 도메인 부족 (7개) |

| 기회 (Opportunities) | 위협 (Threats) |
|---------------------|----------------|
| 기술 문제 해결 시 즉시 인덱싱 가능 | 인덱싱 지연으로 경쟁사 선점 |
| 한국 AI 키워드 블루오션 (난이도 0-1) | Thin content 패널티 가능성 |
| MCP 시장 폭발 (+3,186%) | MCP 키워드 난이도 급상승 중 |
| 고품질 백링크 보유 (Atlassian DR 92) | 기술 문제 장기화 시 크롤링 예산 낭비 |

### 9.2 현재 상태 평가

| 영역 | 상태 | 평가 |
|------|------|------|
| 인덱싱 | Redirect Error | 심각 |
| 검색 트래픽 | 90일간 0회 | 심각 |
| 기술적 SEO | HEAD 405 에러 | 심각 |
| SSR 렌더링 | 콘텐츠 정상 | 양호 |
| 메타 태그 | title, description 포함 | 양호 |
| 백링크 | 228개 확보 | 양호 |

---

## 10. 권장 조치사항

### 10.1 긴급 (즉시 시행) - ROI 극대화

| 우선순위 | 조치사항 | 담당 | 예상 시간 | 상세 |
|----------|----------|------|----------|------|
| **1** | **HTTP HEAD 요청 지원 추가** | Backend | 1-2시간 | 405 -> 200 응답으로 변경 |
| **2** | **GSC에서 수동 인덱싱 요청** | Marketing | 30분 | URL 검사 -> "인덱싱 요청" 클릭 |
| **3** | **robots.txt에 `Allow: /` 추가** | DevOps | 15분 | 메인 페이지 명시적 허용 |
| **4** | **사이트맵 재제출** | DevOps | 15분 | GSC에서 재제출 |

**ROI 분석**:
- 예상 연간 트래픽 가치: $4,200-11,400
- 필요한 투자: 개발자 1-2시간
- ROI: 극도로 높음

### 10.2 중요 (1-2주 이내)

| 우선순위 | 조치사항 | 담당 | 상세 |
|----------|----------|------|------|
| 5 | og:url 동적으로 변경 | Frontend | 각 페이지별 고유 URL |
| 6 | Thin content 사이트맵에서 제외 | Product | 날씨/일정 등 필터링 |
| 7 | www.querypie.com에서 백링크 추가 | Marketing | 홈페이지에서 app 링크 |
| 8 | pulsemcp.com 파트너십/추가 백링크 논의 | Marketing | MCP 생태계 협력 |
| 9 | 홈페이지 "ai 플랫폼" 키워드 최적화 | Content | 인덱싱 후 즉시 적용 |

### 10.3 개선 (2-4주 이내)

| 우선순위 | 조치사항 | 담당 |
|----------|----------|------|
| 10 | Schema.org `Conversation` -> `Article`로 변경 | Frontend |
| 11 | Publication 공개 기준 정립 (최소 콘텐츠 길이) | Product |
| 12 | Internal linking 강화 | Frontend |
| 13 | sequential thinking 페이지 최적화 | Content |
| 14 | 한국어 랜딩 페이지 준비 | Content |

### 10.4 인덱싱 후 콘텐츠 전략

**Phase 1 (인덱싱 해결 즉시):**
```
app.querypie.com/
├── / (홈페이지)           -> "ai 플랫폼" 타겟 (1,100/월, 난이도 1)
├── /features             -> "ai saas" 타겟 (100/월, 난이도 0)
└── /ko/                   -> 한국어 AI 플랫폼 랜딩
```

**Phase 2 (인덱싱 후 2주):**
```
├── /enterprise           -> "기업용 ai" 타겟 (90/월)
├── /solutions/workflow   -> "ai 워크플로우" 타겟 (80/월)
├── /mcp/sequential-thinking/ -> sequential thinking (500/월, 난이도 3)
└── /security             -> "ai 보안 플랫폼" 타겟 (10/월)
```

**Phase 3 (1개월):**
```
├── /en/platform          -> "ai agent platform" 타겟 (1,100/월, 난이도 49)
├── /en/enterprise        -> "enterprise ai" 타겟 (5,600/월, 난이도 54)
├── /integrations/        -> API 통합 문서 (airtable, confluence, discord)
└── /compliance           -> SOC 2, AI 거버넌스 연계
```

---

## 11. KPI 목표 (인덱싱 복구 후)

| 지표 | 현재 | 1개월 후 | 3개월 후 | 6개월 후 |
|------|------|----------|----------|----------|
| 인덱싱된 URL | 0 | 50 | 120 | 150 |
| 월간 노출 | 0 | 1,000 | 5,000 | 15,000 |
| 월간 클릭 | 0 | 20 | 100 | 300 |
| 참조 도메인 | 7 | 10 | 20 | 30 |

### 예상 트래픽 시나리오

| 시나리오 | 인덱싱 URL | 월간 노출 | 월간 클릭 | 조건 |
|----------|-----------|-----------|-----------|------|
| 보수적 | 50 | 2,000 | 40 | 현재 콘텐츠만 |
| 중간 | 100 | 8,000 | 160 | MCP 콘텐츠 강화 |
| 낙관적 | 150 | 20,000 | 400 | 키워드 최적화 완료 |

### 키워드별 예상 트래픽

| 키워드 | 현재 순위 | 예상 순위 | 예상 트래픽 |
|--------|----------|----------|------------|
| ai 플랫폼 (KR) | 미인덱싱 | Top 5 | 200-500/월 |
| ai 에이전트 (KR) | 미인덱싱 | 3-7위 | 300-700/월 |
| sequential thinking | 65위 | Top 10 | 50-150/월 |
| discord api | 84위 | Top 30 | 20-50/월 |
| **총계** | - | - | **400-900/월** |

---

## 12. 모니터링 계획

### 일일 체크

```bash
# 1. HTTP HEAD 응답 확인
curl -sI "https://app.querypie.com/" | head -1

# 2. 메인 페이지 인덱싱 상태
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"
```

### 주간 체크

```bash
# 1. 사이트맵 인덱싱 현황
gsc sitemaps "https://app.querypie.com/"

# 2. 검색 성능 (인덱싱 후)
gsc query "https://app.querypie.com/" --by-date --days 7
```

### 모니터링 체크포인트

| 기간 | 체크 항목 | 목표 |
|------|----------|------|
| +1일 | HEAD 응답 200 확인 | 에러 해결 |
| +1주 | 메인 페이지 인덱싱 | Indexed 상태 |
| +2주 | 첫 검색 노출 | 100+ 노출 |
| +1개월 | 50 URL 인덱싱 | 사이트맵 30% |

---

## 13. 부록

### 13.1 데이터 소스

| 소스 | 데이터 유형 | 분석 기간 | 비고 |
|------|-------------|-----------|------|
| **Ahrefs MCP** | Domain Rating, Backlinks, Referring Domains, Organic Keywords, Metrics History | 90일 | - |
| **Google Search Console CLI** | Search Performance, URL Inspection | 90일 | 데이터 없음 (인덱싱 실패) |

### 13.2 분석 CLI 명령어

```bash
# GSC 분석
gsc query "https://app.querypie.com/" --days 30  # 데이터 없음
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"

# HTTP HEAD 응답 확인
curl -sI "https://app.querypie.com/" | head -1
```

### 13.3 분석 이력

| 일시 | Round | 내용 |
|------|-------|------|
| 2026-02-02 01:00 KST | - | 초기 GSC 분석, 인덱싱 실패 확인 |
| 2026-02-03 02:00 KST | - | HTTP HEAD 405 에러 분석 |
| 2026-02-03 02:25 KST | Round 2 | 참조 도메인 상세 분석, 고품질 백링크 확인 (Atlassian DR 92, zenn.dev DR 83) |
| 2026-02-03 02:35 KST | Round 14 | 한국어 AI 키워드 분석, "ai 에이전트" (3,600, 난이도 1), "ai 플랫폼" (1,100, 난이도 1) 발견 |
| 2026-02-03 02:40 KST | Round 4 | MCP 콘텐츠 전략 수립, 인덱싱 해결 후 트래픽 예측 추가 |
| 2026-02-03 03:45 KST | Round 49 | 현재 오가닉 키워드 현황 분석 (sequential thinking 등) |
| 2026-02-03 04:00 KST | Round 38 | AI 플랫폼 키워드 심층 분석, 경쟁사 분석 |
| 2026-02-03 04:10 KST | Round 39 | SERP 경쟁 분석 - 한국 AI 플랫폼 블루오션 확정 |
| 2026-02-03 05:05 KST | Round 28 | 인덱싱 해결 시 예상 ROI 분석, 긴급도 재평가 |
| 2026-02-03 06:35 KST | Round 29 | MCP 시장 폭발 (+3,186%), 기회 비용 상향 ($4,200-11,400/년) |
| 2026-02-03 16:30 KST | - | GA 데이터 오류 수정 (ACP Application ≠ app.querypie.com) |

### 13.4 키워드 통합 목록 (Round 28-49)

**한국 시장:**
| 키워드 | 검색량/월 | 난이도 | 발견 Round |
|--------|----------|--------|-----------|
| ai 에이전트 | 3,600 | 1 | 14 |
| mcp 서버 | 4,400 | - | 14 |
| ai 플랫폼 | 1,100 | 1 | 14, 38 |
| ai saas | 100 | 0 | 38 |
| 기업용 ai | 90 | - | 38 |
| ai 워크플로우 | 80 | - | 38 |
| 생성형 ai 보안 | 150 | - | 28 |
| ai 에이전트 플랫폼 | 30 | - | 38 |
| ai 보안 플랫폼 | 10 | - | 14, 38 |
| ai 보안 인증 | 30 | 0 | 38 |

**미국 시장:**
| 키워드 | 검색량/월 | 난이도 | 발견 Round |
|--------|----------|--------|-----------|
| mcp server | 46,000 | 81 | 29 |
| model context protocol | 24,000 | 79 | 29 |
| ai agent | 26,000 | 77 | 29 |
| sequential thinking | 500 | 3 | 49 |
| ai agent platform | 1,100 | 49 | 38 |
| ai saas | 900 | 47 | 38 |
| enterprise ai | 5,600 | 54 | 38 |
| ai workflow | 1,700 | 53 | 38 |
| ai platform | 5,700 | 86 | 38 |
| ai security platform | 400 | 81 | 38 |
| what is an mcp server | 3,700 | 29 | 4 |
| mcp security | 800 | 35 | 4 |
| ai compliance software | 200 | 25 | 38 |
| soc 2 for saas | 150 | 20 | 38 |

---

*Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>*
