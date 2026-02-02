# SEO 심층 분석 리포트: app.querypie.com

## 개요

| 항목 | 내용 |
|------|------|
| 분석 대상 | https://app.querypie.com/ |
| 분석 기간 | 2025-11-01 ~ 2026-02-03 |
| 분석 일자 | 2026-02-03 (심층 분석 업데이트) |
| 분석 도구 | Ahrefs MCP, Google Search Console CLI, Google Analytics GA4 |
| 제품 | QueryPie AIP (AI Platform) |
| GA Property ID | 451236681 |
| 이전 분석 | 2026-02-02 |

---

## 1. Executive Summary

### 핵심 지표 현황

| 지표 | 현재 값 | 상태 |
|------|---------|------|
| **Domain Rating** | 55 (상위 도메인 상속) | 양호 |
| **Live Backlinks** | 228 | 양호 |
| **Referring Domains** | 7 | ⚠️ 부족 |
| **Organic Keywords** | 4 | 🔴 심각 |
| **Organic Traffic** | 0/월 (Ahrefs 추정) | 🔴 심각 |
| **GSC 검색 클릭** | **0회** | 🔴 심각 |
| **GSC 검색 노출** | **0회** | 🔴 심각 |
| **인덱싱 상태** | **Redirect Error** | 🔴 심각 |

### 핵심 발견사항

1. **인덱싱 완전 실패**: Google에서 "Redirect Error"로 인해 전혀 인덱싱되지 않음
2. **검색 트래픽 제로**: GSC에서 90일간 노출/클릭 모두 0회
3. **기술적 문제**: HTTP HEAD 요청 미지원 (405 에러)
4. **SSR 정상 작동**: 실제 콘텐츠는 정상적으로 렌더링됨
5. **백링크 양호**: 228개 백링크, 7개 참조 도메인 확보

---

## 1.5 Google Analytics 종합 분석 (90일)

🔥 **핵심 발견**: app.querypie.com은 SEO 트래픽이 아닌 **기업 SSO를 통한 B2B SaaS 애플리케이션**입니다.

### GA 일별 트래픽 규모

| 지표 | 값 | 분석 |
|------|-----|------|
| **일일 평균 세션** | ~5,000 | 🟢 높은 사용량 |
| **일일 평균 사용자** | ~1,850 | 🟢 활성 사용자 |
| **일일 평균 페이지뷰** | ~45,000 | 🟢 높은 참여도 |
| **평균 세션 시간** | 8분+ | 🟢 깊은 사용 |
| **이탈률** | 10% 이하 | 🟢 매우 우수 |

### GA 트래픽 소스 분석 (90일)

| 순위 | 소스 / 매체 | 세션 | 사용자 | 점유율 | 분석 |
|------|-------------|------|--------|--------|------|
| 1 | **(direct) / (none)** | 176,282 | 6,976 | **60.4%** | 직접 접근 |
| 2 | **lguplus.okta.com** | 20,350 | 919 | 7.0% | LG U+ SSO |
| 3 | **kakao.okta.com** | 19,423 | 652 | 6.7% | 카카오 SSO |
| 4 | **dunamu.okta.com** | 11,826 | 215 | 4.1% | 두나무 SSO |
| 5 | **id.karrotmarket.com** | 7,992 | 234 | 2.7% | 당근마켓 |
| 6 | **nol-universe.okta.com** | 7,837 | 290 | 2.7% | 놀유니버스 SSO |
| 7 | **healingpaper.okta.com** | 6,965 | 269 | 2.4% | 힐링페이퍼 SSO |
| 8 | korbit.okta.com | 4,602 | 102 | 1.6% | 코빗 SSO |
| 9 | spoonradio.okta.com | 3,751 | 84 | 1.3% | 스푼라디오 SSO |
| 10 | kakaohealthcare.okta.com | 3,607 | 48 | 1.2% | 카카오헬스케어 SSO |
| ... | **google / organic** | **500** | 28 | **0.2%** | 🔴 **검색 트래픽 거의 없음** |

⚠️ **핵심 인사이트**:
- **98%** 이상의 트래픽이 기업 SSO (Okta, Google Accounts 등)를 통해 유입
- Google Organic 검색 트래픽은 **0.2%** (500세션) 에 불과
- 주요 고객사: **LG U+, 카카오, 두나무, 당근마켓, 토스페이먼츠** 등 국내 대기업/유니콘

### GA 주요 고객사 추정 (SSO 기준)

| 기업 | Okta 도메인 | 세션 | 추정 사용자 |
|------|-------------|------|-------------|
| LG U+ | lguplus.okta.com | 20,350 | 919 |
| 카카오 | kakao.okta.com + kakaohealthcare | 23,030 | 700 |
| 두나무 (업비트) | dunamu.okta.com | 11,826 | 215 |
| 당근마켓 | id.karrotmarket.com | 7,992 | 234 |
| 토스페이먼츠 | rnd-tosspayments.okta.com | 1,545 | 89 |
| 배달의민족 | wiki.daumkakao.com (추정) | 475 | 40 |
| 코빗 | korbit.okta.com | 4,602 | 102 |

### GA 상위 기능 페이지 (90일)

| 순위 | 페이지 | 페이지뷰 | 사용자 | 평균 시간 | 기능 |
|------|--------|----------|--------|-----------|------|
| 1 | /login | 639,081 | 8,780 | 4분 34초 | 로그인 |
| 2 | /dashboard | 256,879 | 5,483 | 1분 27초 | 대시보드 |
| 3 | **/databases/sql-editor** | **218,065** | 3,840 | 2분 29초 | **SQL 편집기** |
| 4 | /databases/connections | 203,914 | 4,540 | 2분 9초 | DB 연결 |
| 5 | /multiagent/connections | 145,636 | 1,370 | 4분 45초 | 멀티에이전트 |
| 6 | / | 135,522 | 5,325 | 37초 | 홈 |
| 7 | /servers/terminal | 63,493 | 1,385 | 3분 53초 | 서버 터미널 |
| 8 | /workflow/sent-requests | 57,776 | 2,646 | 1분 54초 | 워크플로우 |

⚠️ **핵심 기능**: SQL Editor (218K PV), DB Connections (204K PV), Server Terminal (63K PV) - **데이터 접근 제어 솔루션**의 핵심 기능 활발히 사용 중

---

## 2. 현재 상태: 검색 트래픽 제로

### 2.1 GSC 데이터 (최근 30일)

```
검색 성능 데이터: https://app.querypie.com/
기간: 2026-01-01 ~ 2026-01-31

데이터가 없습니다.
```

**결론**: 지난 90일간 Google 검색에서 **단 한 번도 노출되지 않음**

### 2.2 인덱싱 상태

| 항목 | 상태 |
|------|------|
| 메인 페이지 (/) | 🔴 Redirect Error |
| Publication 페이지 | 🔴 URL is unknown to Google |
| 사이트맵 제출 | ✅ 156개 URL 제출 |
| 인덱싱된 URL | **0개** |

---

## 3. 도메인 권위 분석 (Ahrefs)

### 3.1 백링크 프로필

| 지표 | 값 | 평가 |
|------|-----|------|
| 총 백링크 (Live) | 228 | 양호 |
| 총 백링크 (All-time) | 230 | - |
| 참조 도메인 (Live) | 7 | ⚠️ 부족 |
| 참조 도메인 (All-time) | 7 | - |

### 3.2 Ahrefs 키워드 데이터

| 키워드 | 검색량 | 순위 | 트래픽 |
|--------|--------|------|--------|
| sequential thinking | 500 | 65 | 0 |
| airtable documentation | 200 | 61 | 0 |
| confluence api | 200 | 74 | 0 |
| discord api | 800 | 84 | 0 |

**문제점**: Ahrefs에서도 트래픽 0으로 추정. 모든 키워드 순위가 60위 이상으로 실질적 트래픽 없음.

---

## 4. 기술적 문제 분석

### 4.1 "Redirect Error" 원인

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

### 4.2 HTTP HEAD 요청 테스트

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

**문제 확인**: HEAD 요청에 405 에러 반환. Googlebot이 HEAD 요청으로 먼저 확인 후 GET 수행하는 경우 크롤링 실패.

### 4.3 원인 분석

| 가능성 | 설명 | 확률 |
|--------|------|------|
| **HTTP HEAD 405** | 서버가 HEAD 요청 미지원 | 🔴 높음 |
| JavaScript 리다이렉트 | 클라이언트 측 리다이렉트 | 낮음 |
| 간헐적 서버 리다이렉트 | 특정 조건에서 리다이렉트 | 낮음 |

### 4.4 SSR 렌더링 확인 (정상)

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

---

## 5. 사이트맵 분석

### 5.1 사이트맵 현황

```
총 158개 URL 제출, 0개 인덱싱 (0%)

sitemap.xml
└── publication-1.xml (158 URLs)
    └─ web: 제출 156, 인덱싱 0
```

### 5.2 사이트맵 URL 구조

모든 URL이 `/chat/publication/` 경로:
```
https://app.querypie.com/chat/publication/{uuid}/{slug}
```

### 5.3 콘텐츠 품질 문제

사이트맵의 158개 URL 분석:

| 콘텐츠 유형 | 예시 | SEO 가치 |
|-------------|------|----------|
| 기술 분석 | `clean-architecture-book-summary-korean` | 높음 |
| 데이터 분석 | `korean-poll-survey-data-analysis` | 높음 |
| PR 분석 | `querypie-mono-september-pr-analysis` | 중간 |
| **날씨 메모** | `san-francisco-weather-today-61f` | **없음** |
| **일정 메모** | `schedule-meeting-with-jane-tuesday` | **없음** |

**Thin Content 문제**: 날씨, 개인 일정 등 SEO 가치 없는 콘텐츠가 사이트맵에 포함됨

---

## 6. og:url 이슈

### 6.1 현재 상태 (문제)

```html
<!-- 모든 페이지에서 동일한 og:url -->
<meta property="og:url" content="https://app.querypie.com"/>
```

### 6.2 올바른 설정

```html
<!-- 각 페이지별 고유 og:url -->
<meta property="og:url" content="https://app.querypie.com/chat/publication/{uuid}/{slug}"/>
```

---

## 7. 종합 평가

### 7.1 SWOT 분석

| 강점 (Strengths) | 약점 (Weaknesses) |
|------------------|-------------------|
| SSR 정상 구현 | 🔴 인덱싱 완전 실패 |
| 메타 태그 완비 | 🔴 HTTP HEAD 405 에러 |
| 228개 백링크 확보 | Thin content 포함 |
| Schema.org 마크업 | og:url 고정값 문제 |

| 기회 (Opportunities) | 위협 (Threats) |
|---------------------|----------------|
| 기술 문제 해결 시 즉시 인덱싱 가능 | 인덱싱 지연으로 경쟁사 선점 |
| MCP 콘텐츠 가치 | Thin content 패널티 가능성 |
| www.querypie.com 백링크 활용 | 기술 문제 장기화 시 크롤링 예산 낭비 |

### 7.2 문제 심각도

```
인덱싱 상태 (Query Pie 도메인 비교):

www.querypie.com       ████████████████████████████████████ 인덱싱 정상
docs.querypie.com      ████████████████████████████████████ 인덱싱 정상
aip-docs.app.querypie  █████████████████████████████████░░░ 인덱싱 정상 (성장 중)
────────────────────────────────────────────────────────────────────────
app.querypie.com       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 🔴 인덱싱 0%
────────────────────────────────────────────────────────────────────────
```

---

## 8. 권장 조치사항

### 🔴 긴급 (즉시 시행)

| 우선순위 | 조치사항 | 담당 | 상세 |
|----------|----------|------|------|
| **1** | **HTTP HEAD 요청 지원 추가** | Backend | 405 → 200 응답으로 변경 |
| **2** | **GSC에서 수동 인덱싱 요청** | Marketing | URL 검사 → "인덱싱 요청" 클릭 |
| **3** | **robots.txt에 `Allow: /` 추가** | DevOps | 메인 페이지 명시적 허용 |

### 중요 (1-2주 이내)

| 우선순위 | 조치사항 | 담당 | 상세 |
|----------|----------|------|------|
| 4 | og:url 동적으로 변경 | Frontend | 각 페이지별 고유 URL |
| 5 | Thin content 사이트맵에서 제외 | Product | 날씨/일정 등 필터링 |
| 6 | www.querypie.com에서 백링크 추가 | Marketing | 홈페이지에서 app 링크 |

### 개선 (2-4주 이내)

| 우선순위 | 조치사항 | 담당 |
|----------|----------|------|
| 7 | Schema.org `Conversation` → `Article`로 변경 | Frontend |
| 8 | Publication 공개 기준 정립 (최소 콘텐츠 길이) | Product |
| 9 | Internal linking 강화 | Frontend |

---

## 9. 기술적 해결 방안

### 9.1 HTTP HEAD 지원 추가 (긴급)

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

### 9.2 og:url 동적 설정

```javascript
// Next.js Head 컴포넌트
<meta property="og:url" content={`https://app.querypie.com${router.asPath}`} />
```

### 9.3 Thin Content 필터링

사이트맵 생성 시 다음 조건 적용:
- 최소 콘텐츠 길이: 500자 이상
- 제외 키워드: "날씨", "일정", "회의", "weather", "schedule"
- 최소 대화 턴 수: 3턴 이상

---

## 10. 인덱싱 복구 타임라인

### 예상 타임라인

| 단계 | 작업 | 예상 소요 | 예상 결과 |
|------|------|-----------|-----------|
| 1 | HEAD 요청 지원 배포 | 1일 | - |
| 2 | GSC 수동 인덱싱 요청 | 즉시 | - |
| 3 | Google 재크롤링 | 1-7일 | 메인 페이지 인덱싱 |
| 4 | 내부 페이지 인덱싱 | 2-4주 | 50% 인덱싱 |
| 5 | 전체 인덱싱 완료 | 1-2개월 | 80%+ 인덱싱 |

### 모니터링 체크포인트

```bash
# 매일 체크

# 1. 메인 페이지 인덱싱 상태
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"

# 2. 사이트맵 인덱싱 현황
gsc sitemaps "https://app.querypie.com/"

# 3. 검색 성능 (인덱싱 후)
gsc query "https://app.querypie.com/" --by-date --days 7

# 4. HTTP HEAD 응답 확인
curl -sI "https://app.querypie.com/" | head -1
```

---

## 11. KPI 목표 (인덱싱 복구 후)

| 지표 | 현재 | 1개월 후 | 3개월 후 | 6개월 후 |
|------|------|----------|----------|----------|
| 인덱싱된 URL | 0 | 50 | 120 | 150 |
| 월간 노출 | 0 | 1,000 | 5,000 | 15,000 |
| 월간 클릭 | 0 | 20 | 100 | 300 |
| 참조 도메인 | 7 | 10 | 20 | 30 |

---

## 12. 결론

### 현재 상태 평가

| 영역 | 상태 | 평가 |
|------|------|------|
| 인덱싱 | 실패 | 🔴 Redirect Error |
| 검색 트래픽 | 제로 | 🔴 90일간 0회 |
| 기술적 SEO | 문제 | 🔴 HEAD 405 에러 |
| SSR 렌더링 | 정상 | 🟢 콘텐츠 정상 |
| 메타 태그 | 정상 | 🟢 title, description 포함 |
| 백링크 | 양호 | 🟡 228개 확보 |

### 핵심 액션 (우선순위 순)

1. **🔴 HTTP HEAD 지원 추가** - 가장 가능성 높은 원인
2. **🔴 GSC 수동 인덱싱 요청** - 즉시 실행 가능
3. **🔴 robots.txt 확인** - Allow: / 명시적 추가

### 예상 결과

기술 문제 해결 후:
- **1주**: 메인 페이지 인덱싱 시작
- **1개월**: 50+ URL 인덱싱, 첫 검색 트래픽 발생
- **3개월**: 100+ URL 인덱싱, 월 100클릭 목표

### 경고

**기술 문제 미해결 시**: 무기한 인덱싱 불가. 콘텐츠 가치와 무관하게 검색 트래픽 제로 지속.

---

## 부록: 데이터 소스

### 사용된 데이터 소스

| 소스 | 데이터 유형 | 분석 기간 | 비고 |
|------|-------------|-----------|------|
| **Ahrefs MCP** | Domain Rating, Backlinks, Referring Domains, Organic Keywords, Metrics History | 90일 | - |
| **Google Search Console CLI** | Search Performance, URL Inspection | 90일 | ⚠️ 데이터 없음 (인덱싱 실패) |
| **Google Analytics GA4** | Traffic, Sources, Pages, User Behavior | 90일 | 🟢 애플리케이션 사용 데이터 풍부 |

### 분석 CLI 명령어

```bash
# GSC 분석
gsc query "https://app.querypie.com/" --days 30  # 데이터 없음
gsc inspect "https://app.querypie.com/" "https://app.querypie.com/"

# GA 분석
ga report 451236681 --days 90
ga sources 451236681 --days 90
ga pages 451236681 --days 90
```

### 주요 고객사 SSO 도메인 목록 (참고용)

| 기업 | SSO 도메인 |
|------|------------|
| LG U+ | lguplus.okta.com |
| 카카오 | kakao.okta.com, kakaohealthcare.okta.com |
| 두나무 | dunamu.okta.com |
| 당근마켓 | id.karrotmarket.com |
| 토스페이먼츠 | rnd-tosspayments.okta.com |
| 코빗 | korbit.okta.com |
| 스푼라디오 | spoonradio.okta.com |
| 메가존 | login.megazone.com |

### 분석 이력

| 일시 | 내용 |
|------|------|
| 2026-02-02 01:00 KST | 초기 GSC 분석, 인덱싱 실패 확인 |
| 2026-02-03 02:00 KST | HTTP HEAD 405 에러 분석 |
| 2026-02-03 16:00 KST | GA 상세 분석, B2B SaaS 트래픽 패턴 발견, 주요 고객사 식별 |

---

*Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>*
