# Google Search Console 분석 리포트: app.querypie.com

## 개요

| 항목 | 내용 |
|------|------|
| 분석 대상 | https://app.querypie.com/ |
| 분석 기간 | 2025-11-01 ~ 2026-01-30 (90일) |
| 분석 일자 | 2026-02-02 |
| 분석 도구 | `gsc` CLI (bin/gsc) |

---

## 1. 요약 (Executive Summary)

| 지표 | 현황 | 상태 |
|------|------|------|
| 제출된 URL | 156개 | - |
| 인덱싱된 URL | **0개** | 심각 |
| 검색 노출 (90일) | **0회** | 심각 |
| 검색 클릭 (90일) | **0회** | 심각 |
| 메인 페이지 상태 | Redirect Error | 조사 필요 |

**결론**: 사이트가 Google 검색에 전혀 노출되지 않고 있습니다.

---

## 2. Googlebot 응답 분석

### 2.1 HTTP 응답 비교

| 요청 유형 | User-Agent | HTTP 상태 | 리다이렉트 |
|-----------|------------|-----------|-----------|
| HEAD | 일반 브라우저 | **405** | - |
| HEAD | Googlebot | **405** | - |
| GET | Googlebot Desktop | **200** | 0회 |
| GET | Googlebot Mobile | **200** | 0회 |

**발견사항**: GET 요청은 정상이지만, HEAD 요청에 405 에러 발생

### 2.2 SSR 렌더링 확인

Googlebot으로 받은 HTML 분석 결과:

```html
<!-- 메인 페이지 -->
<title>QueryPie AIP | Secure MCP Provider Management</title>
<meta name="description" content="QueryPie is a secure MCP provider management tool..."/>
<meta property="og:title" content="QueryPie AIP | Secure MCP Provider Management"/>

<!-- Publication 페이지 예시 -->
<title>QueryPie AIP | 클린 아키텍쳐 설계 원칙</title>
<meta name="description" content="&quot;클린 아키텍쳐&quot;는 로버트 C. 마틴(Uncle Bob)이..."/>
```

**긍정적 요소**:
- SSR(Server-Side Rendering) 정상 작동
- 메타 태그 (title, description, og tags) 포함
- Schema.org 마크업 적용 (`itemType="https://schema.org/Conversation"`)
- 실제 콘텐츠가 HTML에 포함됨 (JS 렌더링 불필요)

---

## 3. "Redirect Error" 원인 분석

Google Search Console이 보고하는 "Redirect error"의 가능한 원인:

| 가능성 | 설명 | 확률 |
|--------|------|------|
| HTTP HEAD 405 | Googlebot이 HEAD 요청 시 405를 리다이렉트 에러로 해석 | 높음 |
| JavaScript 리다이렉트 | 클라이언트 측 JS 리다이렉트 발생 | 낮음 |
| 간헐적 서버 리다이렉트 | 특정 조건에서 서버가 리다이렉트 | 낮음 |

### URL 검사 결과

```
메인 페이지 (https://app.querypie.com/)
----------------------------------------
상태: 중립
커버리지: Redirect error
페이지 가져오기: REDIRECT_ERROR
마지막 크롤링: 2026-01-25 13:17:05
크롤링 에이전트: MOBILE

Publication 페이지
----------------------------------------
상태: 중립
커버리지: URL is unknown to Google
→ Google이 아직 크롤링하지 않음
```

---

## 4. 사이트맵 현황

```
총 158개 URL 제출, 0개 인덱싱 (0%)

sitemap.xml
└── publication-1.xml (158 URLs)
    └─ web: 제출 156, 인덱싱 0
```

### 사이트맵 URL 구조

모든 URL이 `/chat/publication/` 경로:
```
https://app.querypie.com/chat/publication/{uuid}/{slug}
```

robots.txt에서 `Allow: /chat/publication/`으로 허용됨

---

## 5. 콘텐츠 품질 분석

사이트맵의 158개 URL 샘플 분석:

| 콘텐츠 유형 | 예시 | SEO 가치 |
|-------------|------|----------|
| 기술 분석 | `clean-architecture-book-summary-korean` | 높음 |
| 데이터 분석 | `korean-poll-survey-data-analysis-support-rates` | 높음 |
| PR 분석 | `querypie-mono-september-pr-analysis` | 중간 |
| 날씨 메모 | `san-francisco-weather-today-61f` | 없음 |
| 일정 메모 | `schedule-meeting-with-jane-tuesday` | 없음 |

**문제점**: Thin content (날씨, 개인 일정 등)가 사이트맵에 포함됨

---

## 6. 근본 원인 분석

### 원인 1: 메인 페이지 크롤링 실패
- Google이 `/`에서 "Redirect error" 감지
- 이로 인해 사이트 전체의 크롤링 우선순위 하락

### 원인 2: 크롤링 진입점 부재
- 메인 페이지가 인덱싱되지 않아 내부 링크 발견 불가
- 외부 백링크 부족 (www.querypie.com에서 링크 필요)

### 원인 3: 사이트맵 URL 미발견
- 사이트맵 제출됨 (156개)
- 하지만 Google이 실제 크롤링하지 않음 → "URL is unknown to Google"

### 원인 4: HTTP HEAD 요청 미지원
- 서버가 HEAD 요청에 405 반환
- 일부 크롤러가 HEAD로 먼저 확인 후 GET 수행

---

## 7. 권장 조치사항

### 긴급 (1주 이내)

| 우선순위 | 조치사항 | 담당 | 상세 |
|----------|----------|------|------|
| 1 | HTTP HEAD 요청 지원 추가 | Backend | 405 → 200 응답 |
| 2 | Search Console에서 메인 페이지 수동 인덱싱 요청 | Marketing | URL 검사 → 인덱싱 요청 |
| 3 | robots.txt에 `Allow: /` 추가 | DevOps | 메인 페이지 명시적 허용 |

### 중요 (2-4주 이내)

| 우선순위 | 조치사항 | 담당 | 상세 |
|----------|----------|------|------|
| 4 | Thin content 사이트맵에서 제외 | Product | 날씨/일정 등 필터링 |
| 5 | www.querypie.com에서 백링크 추가 | Marketing | 홈페이지에서 app 링크 |
| 6 | canonical URL 검토 | Frontend | `og:url`이 고정값으로 설정됨 |

### 개선 (1-3개월)

| 우선순위 | 조치사항 | 담당 |
|----------|----------|------|
| 7 | Publication 공개 기준 정립 (최소 콘텐츠 길이) | Product |
| 8 | Internal linking 강화 | Frontend |
| 9 | Google에 직접 문의 (Redirect error 상세 원인) | Marketing |

---

## 8. 기술적 세부사항

### og:url 이슈

현재 모든 페이지의 og:url이 동일:
```html
<meta property="og:url" content="https://app.querypie.com"/>
```

이는 각 페이지의 실제 URL로 변경되어야 함:
```html
<!-- 올바른 예 -->
<meta property="og:url" content="https://app.querypie.com/chat/publication/{uuid}/{slug}"/>
```

### Schema.org 마크업

현재 `Conversation` 타입 사용 중:
```html
<article itemType="https://schema.org/Conversation">
```

SEO 최적화를 위해 `Article` 또는 `BlogPosting` 타입 검토 권장

---

## 9. 모니터링 계획

```bash
# 주간 체크 스크립트

# 1. 사이트맵 인덱싱 현황
gsc sitemaps "https://app.querypie.com/"

# 2. 메인 페이지 인덱싱 상태
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"

# 3. 검색 성능 추이
gsc query "https://app.querypie.com/" --by-date --days 7

# 4. HTTP HEAD 응답 확인
curl -sI "https://app.querypie.com/" | head -1
```

---

## 10. 결론

### 현재 상태
- SSR 및 메타 태그는 정상 구현됨
- 그러나 "Redirect error"로 인해 메인 페이지 인덱싱 실패
- 결과적으로 사이트 전체가 Google 검색에서 누락됨

### 핵심 액션
1. **HTTP HEAD 요청 지원** - 가장 의심되는 원인
2. **수동 인덱싱 요청** - 즉시 실행 가능
3. **백링크 구축** - www.querypie.com에서 연결

### 예상 결과
위 조치 후 2-4주 내 인덱싱 시작 예상

---

## 부록: 분석에 사용된 명령어

```bash
# 사이트 목록 확인
gsc sites

# 사이트맵 현황
gsc sitemaps "https://app.querypie.com/"

# 검색 성능 (90일)
gsc query "https://app.querypie.com/" --by-date --days 90

# URL 인덱싱 상태 검사
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"

# Googlebot 응답 확인
curl -sL -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "https://app.querypie.com/"
```
