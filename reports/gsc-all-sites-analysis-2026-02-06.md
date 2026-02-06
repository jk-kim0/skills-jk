# GSC 4개 사이트 통합 인덱싱 분석 리포트

- 생성: 2026-02-06
- 대상: www.querypie.com, docs.querypie.com, aip-docs.app.querypie.com, app.querypie.com

## 전체 요약

| 사이트 | 미인덱싱 | 상세 수집 | 주요 문제 |
|--------|---------|----------|----------|
| www.querypie.com | 2,566 | 별도 리포트 참조 | 404 (822), Redirect (1,227) |
| docs.querypie.com | 662 | 662 | 404 (215), Redirect (219), Crawled-not-indexed (159) |
| aip-docs.app.querypie.com | 54 | 54 | Crawled-not-indexed (25), Duplicate (22) |
| app.querypie.com | 169 | 169 | Duplicate (145), Crawled-not-indexed (13) |
| **합계** | **3,451** | | |

> www.querypie.com은 [404 분석](gsc-404-analysis-2026-02-06.md), [리다이렉트 분석](gsc-redirect-analysis-2026-02-06.md) 참조.

---

## docs.querypie.com (662건)

### 현황

| Reason | 건수 | 긴급도 |
|--------|------|--------|
| Page with redirect | 219 | 중 |
| Not found (404) | 215 | 높 |
| Crawled - currently not indexed | 159 | 중 |
| Blocked by robots.txt | 24 | 낮 |
| Duplicate, Google chose different canonical | 23 | 중 |
| Duplicate without user-selected canonical | 19 | 중 |
| Alternate page with proper canonical tag | 1 | - |
| Discovered - currently not indexed | 2 | - |

### 404 URL 분석 (215건)

| 패턴 | 건수 | 설명 |
|------|------|------|
| `/ko/querypie/*` | 79 | 구 URL 경로 (querypie → 현재 구조로 변경됨) |
| `/api/external/*` | 20 | API 엔드포인트가 크롤됨 |
| `/ko/administrator-manual/*` | 18 | 문서 구조 변경으로 404 |
| `/en/administrator-manual/*` | 9 | 위와 동일 |
| `/ko/user-manual/*` | 7 | 위와 동일 |
| `/ko/installation-and-customer-support/*` | 6 | 설치 문서 경로 변경 |
| `/en/release-notes/*` | 6 | 릴리즈 노트 경로 변경 |
| 기타 | 70 | |

**조치:**
1. `/ko/querypie/*` → 현재 문서 경로로 301 리다이렉트 매핑
2. `/api/external/*` → robots.txt Disallow 추가
3. 관리자/사용자 매뉴얼 경로 변경분 → 301 리다이렉트

### Page with redirect (219건)

| 패턴 | 건수 | 설명 |
|------|------|------|
| `/administrator-manual/general/*` | 39 | 언어 prefix 없는 구 경로 |
| `/administrator-manual/audit/*` | 29 | 위와 동일 |
| `/administrator-manual/databases/*` | 27 | 위와 동일 |
| `/administrator-manual/servers/*` | 22 | 위와 동일 |
| `/administrator-manual/kubernetes/*` | 14 | 위와 동일 |
| `/administrator-manual/web-apps/*` | 12 | 위와 동일 |
| `/en/querypie-manual/*` | 9 | 구 querypie-manual 경로 |
| `/user-manual/workflow/*` | 8 | 언어 prefix 없는 구 경로 |
| 기타 | 59 | |

**분석:** 대부분 **언어 prefix가 없는 구 URL**(`/administrator-manual/...`)이 언어별 경로(`/ko/administrator-manual/...`)로 리다이렉트됨. 사이트맵에서 원본 URL 제거 필요.

### Crawled - currently not indexed (159건)

| 패턴 | 건수 | 설명 |
|------|------|------|
| `/ko/querypie/*` | 44 | 구 URL (404도 발생하는 패턴) |
| `/_next/static/*` | 29 | Next.js 정적 자산 (JS/CSS) |
| `/ja/administrator-manual/*` | 24 | 일본어 문서 (thin content 가능) |
| `/ko/querypie-manual/*` | 24 | 구 querypie-manual 경로 |
| `/en/querypie-manual/*` | 19 | 위와 동일 |
| `favicon.ico` | 2 | |
| 기타 | 17 | |

**조치:**
1. `/_next/static/*` → robots.txt Disallow 추가 (이미 일부 차단 중이나 불완전)
2. `/ko/querypie/*`, `querypie-manual/*` → 현재 경로로 301 리다이렉트
3. `/ja/administrator-manual/*` → 콘텐츠 품질 확인 (번역 미완료 또는 thin content)

### Duplicate (42건)

- **user-selected canonical 없음 (19건):** 대부분 `/ja/` 일본어 페이지. canonical 태그 추가 필요.
- **Google이 다른 canonical 선택 (23건):** `/ko/installation-and-customer-support/*` (13건), `/ja/` 페이지 (10건). canonical 태그 설정과 Google 판단이 불일치.

**조치:**
1. 다국어 페이지의 hreflang 태그 점검
2. `/ko/installation-and-customer-support/*` canonical 설정 확인

### Blocked by robots.txt (24건)

23건이 `/_next/static/chunks/*.js` 또는 `*.css` — Next.js 빌드 자산. robots.txt가 이미 차단 중. **정상 동작이므로 조치 불필요.**

---

## aip-docs.app.querypie.com (54건)

### 현황

| Reason | 건수 |
|--------|------|
| Crawled - currently not indexed | 25 |
| Duplicate without user-selected canonical | 22 |
| Discovered - currently not indexed | 5 |
| Page with redirect | 1 |
| Not found (404) | 1 |

### 분석

**전반적으로 양호.** 주요 이슈:

1. **Crawled - not indexed (25건):**
   - `/en/user-guide/mcps/*` (20건) — MCP 플러그인 문서 페이지. 콘텐츠가 존재하나 인덱싱되지 않음.
   - `/_next/static/*` (3건), `favicon.ico` (1건) — 무시 가능.
   - **조치:** MCP 문서 페이지의 콘텐츠 충실도 확인. 내부 링크 보강 또는 사이트맵 제출로 인덱싱 유도.

2. **Duplicate without canonical (22건):**
   - `/en/user-guide/*` (19건) — 영어 사용자 가이드 페이지.
   - `/en/admin-guide/*` (3건)
   - **조치:** canonical 태그 및 hreflang 태그 점검. 한국어/일본어 버전과 중복 판정 가능성.

3. **Discovered - not indexed (5건):**
   - `/en`, `/ja`, `/ko` 루트 + `/ja/user-guide/*` 2건.
   - **조치:** 사이트맵에 포함 확인. 자연스럽게 인덱싱될 가능성 높음.

4. **404 (1건):** `/user-guide/special-features` — 언어 prefix 누락. 301 리다이렉트 추가.

---

## app.querypie.com (169건)

### 현황

| Reason | 건수 |
|--------|------|
| Duplicate without user-selected canonical | 145 |
| Crawled - currently not indexed | 13 |
| Blocked by robots.txt | 9 |
| Duplicate, Google chose different canonical | 1 |
| Discovered - currently not indexed | 1 |

### 분석

**145건이 모두 `/chat/publication/*` 경로** — AI 챗봇 대화 공개 페이지.

1. **Duplicate without canonical (145건):**
   - 전부 `/chat/publication/{uuid}/{slug}` 형태.
   - 사용자 채팅 대화를 공개한 페이지로, 콘텐츠가 유사하거나 canonical 미설정.
   - **조치:**
     - SEO 가치가 있는 publication만 인덱싱 하려면: 선별적 canonical + noindex 태그
     - 전부 인덱싱 하지 않으려면: `/chat/publication/` 경로에 noindex 메타태그 또는 robots.txt Disallow

2. **Crawled - not indexed (13건):**
   - `/chat/publication/*` (11건) + `/login` (1건) + `/` (1건)
   - 채팅 publication 콘텐츠 품질이 인덱싱 기준 미달.
   - `/login`, `/` → 앱 페이지라 인덱싱 어려움. 정상.

3. **Blocked by robots.txt (9건):**
   - `/chat/publication/*` (7건) + `/api/data` + `/__manifest`
   - **정상 동작**. API와 매니페스트 차단은 적절.

---

## 전체 사이트 통합 액션 플랜

### P1 — 높은 효과 (사이트맵/리다이렉트)

| # | 사이트 | 액션 | 예상 해소 |
|---|--------|------|----------|
| 1 | docs | `/ko/querypie/*` 301 리다이렉트 매핑 | ~123건 |
| 2 | docs | 언어 prefix 없는 구 URL 사이트맵 제거 | ~219건 |
| 3 | docs | `/api/external/*` robots.txt Disallow | ~20건 |
| 4 | app | `/chat/publication/*` noindex 또는 Disallow 결정 | ~145건 |

### P2 — 중간 (콘텐츠/태그 개선)

| # | 사이트 | 액션 | 예상 해소 |
|---|--------|------|----------|
| 5 | docs | 다국어 hreflang/canonical 태그 점검 | ~42건 |
| 6 | docs | `/ja/` 일본어 문서 콘텐츠 충실도 확인 | ~24건 |
| 7 | aip-docs | `/en/` canonical 태그 추가 | ~22건 |
| 8 | aip-docs | MCP 문서 페이지 내부 링크 보강 | ~20건 |

### P3 — 낮음 (정리)

| # | 사이트 | 액션 |
|---|--------|------|
| 9 | docs | `/_next/static/*` robots.txt 일관성 확인 |
| 10 | aip-docs | `/user-guide/special-features` 301 리다이렉트 |
| 11 | 전체 | 사이트맵에서 404/리다이렉트 URL 일괄 제거 |

---

## robots.txt 권장 추가 규칙

### docs.querypie.com

```
Disallow: /api/
Disallow: /_next/static/
```

### app.querypie.com (선택)

```
# 채팅 publication 인덱싱을 원하지 않는 경우
Disallow: /chat/publication/
```

---

## 참고: www.querypie.com 통합 현황

| 사이트 | 미인덱싱 | 분석 완료 | 주요 원인 |
|--------|---------|----------|----------|
| www.querypie.com | 2,566 | 2,163건 (84%) | 사이트 리뉴얼 후 리다이렉트/사이트맵 미정리 |
| docs.querypie.com | 662 | 662건 (100%) | 문서 구조 변경 + 구 URL 잔존 |
| aip-docs.app.querypie.com | 54 | 54건 (100%) | canonical 미설정 + 신규 사이트 |
| app.querypie.com | 169 | 169건 (100%) | AI 챗봇 publication 중복 |
| **합계** | **3,451** | **3,048건 (88%)** | |
