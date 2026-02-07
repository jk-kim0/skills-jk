# GSC 인덱싱 개선 프로젝트 진행 요약

- 최종 업데이트: 2026-02-07 (2차)

## 배경

www.querypie.com 외 3개 사이트의 Google Search Console 인덱싱 상태를 분석하고,
미인덱싱 URL을 체계적으로 해소하는 프로젝트입니다.

## 현황 (2026-02-06 기준)

| 사이트 | 미인덱싱 페이지 |
|--------|---------------|
| www.querypie.com | 2,566 |
| docs.querypie.com | 662 |
| aip-docs.app.querypie.com | 54 |
| app.querypie.com | 169 |
| **합계** | **3,451** |

### www.querypie.com 미인덱싱 원인 분류

| Reason | Pages |
|--------|------:|
| Page with redirect | 1,227 |
| Not found (404) | 822 |
| Alternate page with proper canonical tag | 197 |
| Discovered - currently not indexed | 144 |
| Crawled - currently not indexed | 96 |
| Duplicate, Google chose different canonical | 25 |
| Blocked by robots.txt | 18 |
| Redirect error | 18 |
| Duplicate without user-selected canonical | 18 |
| Soft 404 | 1 |

---

## 완료된 작업

### 분석 인프라 구축

| PR | 내용 |
|----|------|
| skills-jk #62 | GSC 인덱싱 주간 점검 자동화 설계 |
| skills-jk #63 | GSC 인덱싱 주간 리포트 자동화 구현 |
| skills-jk #64~#65 | GSC 스크래핑 도구 (`bin/gsc-index-report`) 구현 |
| skills-jk #67 | `--detail` / `--detail-reasons` 옵션 추가 (상세 URL 수집) |

### 분석 리포트

| PR | 내용 | 분석 대상 |
|----|------|----------|
| skills-jk #68 | www.querypie.com 404 URL 분석 | 822건 |
| skills-jk #69 | www.querypie.com 리다이렉트/미인덱싱 분석 | 1,341건 |
| skills-jk #70 | 4개 사이트 통합 분석 | 3,451건 |

### 개선 구현 (corp-web-app)

| PR | 내용 | 해소 건수 | 배포 |
|----|------|----------|------|
| corp-web-app #580 | `/docs/*` sitemap 기반 301/307 리다이렉트 | ~700건 | 2026-02-07 production 배포 완료 |
| corp-web-app #581 | `/wiki/*` Confluence 리다이렉트 URL 오류 수정 + 301 전환 | ~171건 | 2026-02-07 production 배포 완료 |
| corp-web-app #582 | `/docs/sitemap.xml` 빈 응답으로 변경 | — | 2026-02-07 production 배포 완료 |

#### PR #580 상세: `/docs/*` 리다이렉트

- `src/app/docs/[[...path]]/sitemap-paths.ts` 신규 생성
- aip-docs.app.querypie.com과 docs.querypie.com의 sitemap에서 URL 목록을 가져와 캐시 (1시간 TTL)
- sitemap에 존재하는 URL → 301 (영구 리다이렉트)
- sitemap에 존재하지 않는 URL → docs.querypie.com으로 307 (임시 리다이렉트)
- production 검증 완료: sitemap에 있는 URL은 올바른 대상으로 301, 없는 URL은 307 fallback

#### PR #581 상세: `/wiki/*` 리다이렉트 버그 수정

- **발견된 버그**: `/wiki` prefix를 제거하여 `querypie.atlassian.net/spaces/...`로 리다이렉트 → Confluence에서 404
- **수정**: `querypie.atlassian.net/wiki/spaces/...`로 올바르게 리다이렉트
- 307 (임시) → 301 (영구)로 변경하여 SEO link equity 전달 활성화
- production 검증 완료: 모든 wiki URL이 Confluence에서 200 응답

#### PR #582 상세: `/docs/sitemap.xml` 비우기

- docs 콘텐츠가 docs.querypie.com으로 완전 이전 완료
- docs.querypie.com 자체 GSC에 sitemap 등록되어 있으므로, www 측 sitemap 역할 종료
- `/docs/sitemap.xml` → 빈 `<sitemapindex>` 반환
- `/docs/{locale}/sitemap.xml` → 빈 `<urlset>` 반환
- URI 자체는 유지하여 200 응답, GSC가 점진적으로 크롤 대상에서 제거하도록 유도
- `/wiki/sitemap.xml`은 Confluence 콘텐츠를 Google에 노출시키는 유일한 경로이므로 유지

### 개선 효과 요약

| 항목 | 건수 |
|------|------|
| `/docs/*` 301 리다이렉트로 해소 | ~700 |
| `/wiki/*` 301 리다이렉트 정상화로 해소 | ~171 |
| `/docs/sitemap.xml` 비우기로 불필요 크롤 제거 | ~247 |
| **합계** | **~1,118건 (www 전체의 44%)** |

---

## 미완료 / 향후 계획

### P1 — 즉시 실행 가능

#### 1. robots.txt 정리 (corp-web-app)

현재 robots.txt에 누락된 Disallow 규칙을 추가합니다.

```
Disallow: /wiki/
Disallow: /_next/image
Disallow: /chat/
Disallow: /assets/api-docs.json
```

- 효과: 불필요 크롤 ~54건 차단 + 향후 크롤 방지
- 작업량: 1 파일 수정

#### 2. GSC sitemap 등록 정리 (GSC 콘솔 수동 작업)

www.querypie.com GSC에 등록된 14개 sitemap 중 `/docs/sitemap.xml`을 제거합니다.

| 대상 | 등록 URL 수 | 조치 | 사유 |
|------|------------|------|------|
| `/docs/sitemap.xml` | 247 | **제거** | docs.querypie.com으로 이전 완료, 빈 sitemap으로 변경됨 (PR #582) |
| `/wiki/sitemap.xml` | 305 | **유지** | Confluence 콘텐츠를 Google에 노출시키는 유일한 경로 |

- 효과: GSC에서 `/docs/sitemap.xml` 크롤 중단
- 작업: GSC 콘솔에서 수동 삭제

### P2 — 조사 후 실행

#### 3. `/resources/` 경로 리다이렉트 문제 (최대 잔여 카테고리)

| 문제 유형 | 건수 |
|-----------|------|
| 404 | 418 |
| Page with redirect | 342 |
| Redirect error | 18 |
| **소계** | **778** |

- corp-web-app의 resources 라우팅 분석 필요
- 리다이렉트 규칙 점검 및 사이트맵 정리

#### 4. `/sitemap.xml` 오류 조사

- GSC에서 www.querypie.com의 `/sitemap.xml`이 "1 error" 상태
- 사이트맵 구조 및 내용 점검 필요

#### 5. 프론트엔드 locale URL 버그 수정

- `/jahttps://...` 패턴의 비정상 URL 생성 (10건)
- locale prefix + 절대 URL 결합 로직 수정 필요

### P3 — 중장기

#### 6. docs.querypie.com 미인덱싱 해소 (662건)

| 주요 원인 | 건수 |
|-----------|------|
| Page with redirect | 219 |
| Not found (404) | 215 |
| Crawled - currently not indexed | 159 |

#### 7. app.querypie.com 중복 콘텐츠 정리 (169건)

- Duplicate without user-selected canonical: 145건
- canonical 태그 설정 필요

#### 8. 주간 모니터링 체계 운영

- `bin/gsc-index-report` 를 주간 실행하여 추이 추적
- 개선 조치 후 효과 측정

---

## 관련 파일

### 도구

| 파일 | 설명 |
|------|------|
| `bin/gsc-index-report` | GSC 인덱싱 상태 스크래핑 + 리포트 생성 |
| `bin/generate-docs-redirects` | docs 리다이렉트 맵 생성 (PR #71) |

### 데이터

| 파일 | 설명 |
|------|------|
| `reports/data/gsc-index-2026-02-06.json` | 4개 사이트 인덱싱 요약 데이터 |
| `reports/data/gsc-detail-2026-02-06.json` | www.querypie.com 상세 URL 목록 |
| `reports/data/gsc-detail-docs-2026-02-06.json` | docs.querypie.com 상세 URL 목록 |
| `reports/data/gsc-detail-aip-docs-2026-02-06.json` | aip-docs.app.querypie.com 상세 URL 목록 |
| `reports/data/gsc-detail-app-2026-02-06.json` | app.querypie.com 상세 URL 목록 |

### 분석 리포트

| 파일 | 설명 |
|------|------|
| `reports/gsc-index-report-2026-02-06.md` | 주간 인덱싱 상태 리포트 |
| `reports/gsc-404-analysis-2026-02-06.md` | www 404 URL 분석 |
| `reports/gsc-redirect-analysis-2026-02-06.md` | www 리다이렉트/미인덱싱 분석 |
| `reports/gsc-all-sites-analysis-2026-02-06.md` | 4개 사이트 통합 분석 |

### 배포 확인

production 배포 상태는 아래 엔드포인트로 확인합니다.

```bash
curl -s https://www.querypie.com/build-info.json | python3 -m json.tool
```

상세: `skills/ops/check-deployment.md`
