# www.querypie.com 리다이렉트/미인덱싱 URL 분석 리포트

- 생성: 2026-02-06
- 데이터 소스: GSC 상세 URL — Page with redirect (1,227건), Redirect error (18건), Crawled - currently not indexed (96건)

## 요약

www.querypie.com의 리다이렉트 관련 미인덱싱 URL 1,341건을 분석했습니다. 404 분석(822건)과 합치면 **총 2,163건으로 전체 미인덱싱 2,566건의 84%**에 해당합니다.

핵심 문제는 두 가지입니다:
1. **docs 이전**: `/docs/*` URL이 리다이렉트 되지만 사이트맵에 원본 URL이 남아있음 (516건)
2. **resources URL 구조 변경**: 리소스 페이지가 리다이렉트 되지만 원본 URL이 사이트맵에 잔존 (342건)

| 카테고리 | Redirect | Redirect Error | Crawled-Not-Indexed | 합계 |
|----------|----------|---------------|---------------------|------|
| `/docs/` (문서 이전) | 516 | 0 | 6 | 522 |
| `/resources/` (다국어) | 342 | 18 | 38 | 398 |
| `/features/` | 50 | 0 | 5 | 55 |
| `/wiki/` (Confluence) | 22 | 0 | 36 | 58 |
| `/platform/`, `/products/` 등 | 70 | 0 | 11 | 81 |
| **합계** | **1,000** | **18** | **96** | **1,114** |

> GSC UI 제한으로 Page with redirect는 1,227건 중 1,000건만 수집됨.

---

## 1. Page with redirect (1,227건)

리다이렉트가 설정되어 있으나, **사이트맵에 리다이렉트 원본 URL이 남아있어** Google이 계속 크롤링하고 "redirect" 상태로 기록하는 URL입니다.

### 크롤링 시점 분포

| 시기 | 건수 |
|------|------|
| 2026년 2월 | 16 |
| 2026년 1월 | 292 |
| 2025년 12월 | 133 |
| 2025년 11월 | 374 |
| 2025년 10월 | 157 |
| 2025년 9월 이전 | 28 |

### 1-1. `/docs/` 리다이렉트 (516건) — 최대 카테고리

docs.querypie.com으로 이전된 문서의 원본 URL입니다.

| 경로 | 건수 |
|------|------|
| `/docs/en/administrator-manual/...` | 134 |
| `/docs/ko/administrator-manual/...` | 116 |
| `/docs/ja/administrator-manual/...` | 75 |
| `/docs/ko/user-guide/...` | 26 |
| `/docs/en/user-manual/...` | 26 |
| `/docs/ko/user-manual/...` | 22 |
| `/docs/ko/release-notes/...` | 21 |
| `/docs/en/user-guide/...` | 20 |
| `/docs/ja/user-guide/...` | 19 |
| `/docs/ja/user-manual/...` | 17 |
| 기타 | 40 |

**조치:** 사이트맵에서 `/docs/` URL 일괄 제거. 리다이렉트 자체는 정상 동작 중이므로 리다이렉트 규칙은 유지.

### 1-2. `/resources/` 리다이렉트 (342건)

리소스 페이지 URL 구조가 변경된 것으로 추정됩니다.

| 세부 경로 | 건수 |
|-----------|------|
| `discover/blog` | 111 |
| `discover/white-paper` | 82 |
| `discover/webinars` | 64 |
| `learn/tutorials` | 47 |
| `learn/documentation` | 11 |
| `discover/integrations` | 10 |
| 기타 | 17 |

**조치:** 사이트맵에서 리다이렉트 되는 원본 `/resources/` URL 제거. 최종 리다이렉트 대상 URL만 사이트맵에 포함.

### 1-3. `/features/` 리다이렉트 (50건)

| 세부 경로 | 건수 |
|-----------|------|
| `/features/documentation/...` | 35 |
| `/features/demo/...` | 15 |

**조치:** 사이트맵에서 제거.

### 1-4. `/wiki/` 리다이렉트 (22건)

Confluence 위키 페이지 중 일부는 리다이렉트가 설정되어 있음 (404 분석의 113건과 별개).

**조치:** 사이트맵에서 제거.

### 1-5. 기타 (70건)

| 경로 | 건수 |
|------|------|
| `/ko/platform/...`, `/ja/platform/...` | 16 |
| `/platform/...` | 9 |
| `/ko/products/...`, `/ja/products/...`, `/en/products/...` | 12 |
| `/ko/customers/...`, `/ja/customers/...` | 5 |
| 기타 | 28 |

---

## 2. Redirect Error (18건)

리다이렉트 체인이 깨져있거나 무한 루프에 빠지는 URL입니다. **모두 `/resources/` 경로**입니다.

| URL | Last Crawled |
|-----|-------------|
| `/ja/resources/discover/blog/1/agentless-philosophy` | Jan 15, 2026 |
| `/en/resources/discover/blog/2` | Jan 6, 2026 |
| `/resources/discover/white-paper/1` | Jan 4, 2026 |
| `/ko/resources/discover/white-paper/1` | Jan 4, 2026 |
| `/ko/resources/discover/blog/2` | Dec 22, 2025 |
| `/ja/resources/discover/blog/2/querypie-cracking-global-markets` | Dec 17, 2025 |
| `/en/resources/discover/blog/1` | Dec 16, 2025 |
| `/resources/discover/blog/2` | Dec 2, 2025 |
| `/ko/resources/discover/blog/1` | Nov 25, 2025 |
| `/ko/resources/discover/webinars/1` | Nov 21, 2025 |
| `/resources/discover/blog/1` | Nov 16, 2025 |
| `/resources/discover/webinars/2` | Nov 12, 2025 |
| `/resources/discover/webinars/1` | Nov 12, 2025 |
| `/ko/resources/discover/webinars/2` | Nov 11, 2025 |
| `/en/resources/discover/webinars/1` | Nov 10, 2025 |
| `/ja/resources/discover/webinars/1` | Nov 10, 2025 |
| `/ko/resources/discover/white-paper/2` | Oct 27, 2025 |
| `/resources/discover/white-paper/2` | Oct 24, 2025 |

**공통 패턴:** 모두 ID가 1 또는 2인 초기 리소스 — 콘텐츠 이동/삭제 시 리다이렉트가 불완전하게 설정된 것으로 추정.

**조치:** 이 18개 URL의 리다이렉트 대상을 개별 확인하여 수정. 콘텐츠가 없으면 410 응답 또는 카테고리 목록 페이지로 리다이렉트.

---

## 3. Crawled - currently not indexed (96건)

Google이 크롤링했으나 인덱싱할 가치가 없다고 판단한 URL입니다.

### Wiki (36건)

Confluence 위키 페이지가 크롤링되지만 인덱싱되지 않음. 대부분 기술 문서(Installation Guide, Environment Variables 등).

**조치:** `robots.txt`에 `/wiki/` Disallow 추가하여 크롤 자체를 차단.

### Resources (33건)

다국어 리소스 페이지가 크롤링되지만 인덱싱되지 않음. 콘텐츠 품질 문제이거나 중복 콘텐츠로 판단된 것일 수 있음.

**조치:** 해당 페이지의 콘텐츠 품질 확인. thin content면 보강 또는 noindex 처리.

### 주목할 URL

| URL | 비고 |
|-----|------|
| `/_next/image?url=...` | Next.js 이미지 최적화 URL이 크롤됨 |
| `/chat/publication/...` | 채팅/AI 생성 콘텐츠로 추정되는 URL |
| `/assets/api-docs.json` | API 문서 JSON 노출 |
| `/?NaPm=ct%3D...` | 네이버 광고 추적 파라미터가 포함된 URL |

**조치:**
- `/_next/image` → robots.txt Disallow
- `/chat/` → robots.txt Disallow (AI 생성 콘텐츠 차단)
- `/assets/api-docs.json` → robots.txt Disallow
- 추적 파라미터 URL → canonical 태그로 정규화

---

## 통합 액션 플랜 (404 분석 + 리다이렉트 분석)

### 사이트맵 정리 (가장 높은 효과)

| 액션 | 대상 건수 | 해소되는 문제 |
|------|----------|-------------|
| 사이트맵에서 `/docs/` URL 제거 | ~700건 | 404 180건 + Redirect 516건 |
| 사이트맵에서 `/resources/` 리다이렉트 URL 제거 | ~340건 | Redirect 342건 |
| 사이트맵에서 `/wiki/` URL 제거 | ~135건 | 404 113건 + Redirect 22건 |
| 사이트맵에서 `/features/` 리다이렉트 URL 제거 | ~50건 | Redirect 50건 |

> 사이트맵 정리만으로 약 **1,225건 (전체의 48%)** 해소 가능

### robots.txt 추가 규칙

```
Disallow: /wiki/
Disallow: /_next/image
Disallow: /chat/
Disallow: /assets/api-docs.json
```

### 프론트엔드 수정 (404 분석 리포트에서 이관)

- locale prefix + 절대 URL 결합 버그 수정 (`/jahttps://...` 패턴)

### Redirect Error 개별 수정 (18건)

- `/resources/discover/blog/1`, `/2` 등 초기 리소스 URL의 리다이렉트 대상 확인 및 수정
