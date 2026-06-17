# GA4 UTM-like 유입 집계 리포트: www.querypie.com

## 개요

| 항목 | 내용 |
|------|------|
| 보고서 작성일 | 2026-06-16 |
| 데이터 소스 | Google Analytics 4 Data API |
| GA4 Property | `querypie.com for global` (`451239708`) |
| 분석 Host | `www.querypie.com` |
| 전체 분석 기간 | 2026-03-09 ~ 2026-06-15 |
| 최근 기간 | 2026-05-16 ~ 2026-06-15 |

GA4의 당일 데이터는 지연될 수 있어, 2026-06-16 당일은 제외하고 2026-06-15까지 집계했다.

## 집계 기준

이 리포트의 UTM-like 유입은 GA4의 manual traffic source 계열 차원 중 아래 조건 중 하나라도 만족하는 세션으로 정의했다.

- `sessionManualCampaignName`에 명시적인 캠페인 값이 있음
- `sessionManualCampaignId`에 명시적인 캠페인 ID 값이 있음
- `sessionManualAdContent`에 `utm_content`성 값이 있음
- `sessionManualTerm`에 `utm_term`성 값이 있음
- `sessionManualSourceMedium`의 medium이 기본값(`organic`, `referral`, `(none)`, `ai-assistant`)이 아닌 커스텀 medium임

지표 해석:

| 리포트 표현 | GA4 지표 | 의미 |
|-------------|----------|------|
| 방문 | `sessions` | 세션 수 |
| 방문자 | `activeUsers` | 활성 사용자 수 |
| 참여 세션 | `engagedSessions` | 참여 조건을 만족한 세션 수 |
| 조회 | `screenPageViews` | 페이지뷰 수 |
| 이벤트 | `eventCount` | 전체 이벤트 수 |
| 클릭 | `eventCount` where `eventName` is `click` or `select_promotion` | 클릭/선택 성격 이벤트 수 |
| 전환 | `keyEvents` | GA4 key event 수 |

주의: 현재 GA4 Admin에는 `generate_lead`, `select_plan`, `form_type`, `plan_name` 기반 전환 집계가 등록되어 있지 않다. 따라서 이 리포트의 클릭은 GA4에 실제로 들어온 클릭/선택 이벤트 기준이며, 리드/플랜 전환 클릭률은 아직 산출할 수 없다.

## 1. Executive Summary

### 1.1 전체 기간 핵심 지표

| 기간 | 방문 | 방문자 | 참여 세션 | 조회 | 이벤트 | 클릭 | 전환 |
|------|-----:|-------:|----------:|-----:|-------:|-----:|-----:|
| 2026-03-09 ~ 2026-06-15 | 56 | 52 | 25 | 120 | 320 | 5 | 0 |
| 2026-05-16 ~ 2026-06-15 | 19 | 16 | 5 | 53 | 122 | 2 | 0 |

### 1.2 비율 지표

| 기간 | 조회/방문 | 클릭/방문 | 참여율 |
|------|----------:|----------:|-------:|
| 2026-03-09 ~ 2026-06-15 | 2.14 | 0.09 | 44.6% |
| 2026-05-16 ~ 2026-06-15 | 2.79 | 0.11 | 26.3% |

### 1.3 핵심 해석

1. UTM-like 유입 규모는 아직 작다. 전체 기간 기준 방문 56, 조회 120, 클릭 5다.
2. 최근 30일에는 방문 19, 조회 53, 클릭 2로, 전체 대비 방문은 34%, 조회는 44%, 클릭은 40%가 최근 30일에 발생했다.
3. 명시적인 key event 전환은 0건이다. 현재 데이터로는 캠페인별 lead/plan 전환 성과를 판단할 수 없다.
4. 최근 유입은 `qp / notice`의 `iso-42001-certification`, `lingo-release`, `notepie-release` 캠페인이 중심이다.
5. 실제 클릭 이벤트는 `note / social`의 `blog`에서 `click` 3건, `qp / notice`의 `iso-42001-certification`에서 `select_promotion` 2건만 확인된다.

## 2. Source / Campaign별 성과

### 2.1 전체 기간

| Source / Medium | Campaign | 방문 | 방문자 | 참여 세션 | 조회 | 이벤트 | 전환 |
|-----------------|----------|-----:|-------:|----------:|-----:|-------:|-----:|
| `daum / organic` | `(organic)` | 27 | 27 | 15 | 53 | 150 | 0 |
| `qp / notice` | `iso-42001-certification` | 4 | 3 | 1 | 11 | 30 | 0 |
| `qp / notice` | `lingo-release` | 4 | 2 | 2 | 11 | 33 | 0 |
| `ig / social` | `(referral)` | 4 | 3 | 1 | 5 | 13 | 0 |
| `qp / notice` | `notepie-release` | 2 | 2 | 1 | 21 | 29 | 0 |
| `note / social` | `blog` | 2 | 2 | 1 | 4 | 17 | 0 |
| `Knowgenerativeai.com / marketplace` | `Knowgenerativeai.com` | 2 | 2 | 0 | 2 | 6 | 0 |
| `linkedin / social` | `(not set)` | 2 | 2 | 0 | 2 | 6 | 0 |
| `returnonsecurity.com / newsletter` | `security-funded-133-don-t-call-it-a-economic-comeback/` | 2 | 2 | 0 | 2 | 6 | 0 |
| `returnonsecurity.com / newsletter` | `security-funded-146-ai-s-got-99-problems-but-crm-ain-t-one` | 2 | 2 | 1 | 2 | 7 | 0 |
| `newsletter / email` | `webinar_20260319` | 1 | 1 | 1 | 3 | 8 | 0 |
| `cybersectools.com / comparison-page` | `tool-comparison` | 1 | 1 | 0 | 1 | 3 | 0 |
| `naver / organic` | `(organic)` | 1 | 1 | 1 | 1 | 5 | 0 |
| `opentools_web / opentools_medium` | `(referral)` | 1 | 1 | 1 | 1 | 4 | 0 |
| `returnonsecurity.com / newsletter` | `security-funded-146-ai-s-got-99-problems-but-crm-ain-t-one/` | 1 | 1 | 0 | 1 | 3 | 0 |

### 2.2 최근 30일

| Source / Medium | Campaign | 방문 | 방문자 | 참여 세션 | 조회 | 이벤트 | 전환 |
|-----------------|----------|-----:|-------:|----------:|-----:|-------:|-----:|
| `qp / notice` | `iso-42001-certification` | 4 | 3 | 1 | 11 | 30 | 0 |
| `qp / notice` | `lingo-release` | 4 | 2 | 2 | 11 | 33 | 0 |
| `daum / organic` | `(organic)` | 3 | 3 | 1 | 4 | 12 | 0 |
| `qp / notice` | `notepie-release` | 2 | 2 | 1 | 21 | 29 | 0 |
| `Knowgenerativeai.com / marketplace` | `Knowgenerativeai.com` | 2 | 2 | 0 | 2 | 6 | 0 |
| `linkedin / social` | `(not set)` | 2 | 2 | 0 | 2 | 6 | 0 |
| `returnonsecurity.com / newsletter` | `security-funded-133-don-t-call-it-a-economic-comeback/` | 2 | 2 | 0 | 2 | 6 | 0 |

## 3. Campaign / Content 조합별 성과

### 3.1 전체 기간

| Source / Medium | Campaign | Content | 방문 | 방문자 | 참여 세션 | 조회 | 이벤트 |
|-----------------|----------|---------|-----:|-------:|----------:|-----:|-------:|
| `daum / organic` | `(organic)` | `(not set)` | 27 | 27 | 15 | 53 | 150 |
| `ig / social` | `(referral)` | `link_in_bio` | 4 | 3 | 1 | 5 | 13 |
| `qp / notice` | `iso-42001-certification` | `card` | 3 | 2 | 1 | 10 | 27 |
| `qp / notice` | `lingo-release` | `card` | 3 | 1 | 2 | 10 | 30 |
| `note / social` | `blog` | `(not set)` | 2 | 2 | 1 | 4 | 17 |
| `Knowgenerativeai.com / marketplace` | `Knowgenerativeai.com` | `(not set)` | 2 | 2 | 0 | 2 | 6 |
| `linkedin / social` | `(not set)` | `304525597` | 2 | 2 | 0 | 2 | 6 |
| `returnonsecurity.com / newsletter` | `security-funded-133-don-t-call-it-a-economic-comeback/` | `(not set)` | 2 | 2 | 0 | 2 | 6 |
| `returnonsecurity.com / newsletter` | `security-funded-146-ai-s-got-99-problems-but-crm-ain-t-one` | `(not set)` | 2 | 2 | 1 | 2 | 7 |
| `qp / notice` | `notepie-release` | `bar` | 1 | 1 | 1 | 20 | 26 |
| `newsletter / email` | `webinar_20260319` | `(not set)` | 1 | 1 | 1 | 3 | 8 |
| `cybersectools.com / comparison-page` | `tool-comparison` | `(not set)` | 1 | 1 | 0 | 1 | 3 |
| `naver / organic` | `(organic)` | `(not set)` | 1 | 1 | 1 | 1 | 5 |
| `opentools_web / opentools_medium` | `(referral)` | `(not set)` | 1 | 1 | 1 | 1 | 4 |
| `qp / notice` | `iso-42001-certification` | `bar` | 1 | 1 | 0 | 1 | 3 |
| `qp / notice` | `lingo-release` | `bar` | 1 | 1 | 0 | 1 | 3 |
| `qp / notice` | `notepie-release` | `card` | 1 | 1 | 0 | 1 | 3 |
| `returnonsecurity.com / newsletter` | `security-funded-146-ai-s-got-99-problems-but-crm-ain-t-one/` | `(not set)` | 1 | 1 | 0 | 1 | 3 |

### 3.2 최근 30일

| Source / Medium | Campaign | Content | 방문 | 방문자 | 참여 세션 | 조회 | 이벤트 |
|-----------------|----------|---------|-----:|-------:|----------:|-----:|-------:|
| `qp / notice` | `iso-42001-certification` | `card` | 3 | 2 | 1 | 10 | 27 |
| `qp / notice` | `lingo-release` | `card` | 3 | 1 | 2 | 10 | 30 |
| `daum / organic` | `(organic)` | `(not set)` | 3 | 3 | 1 | 4 | 12 |
| `Knowgenerativeai.com / marketplace` | `Knowgenerativeai.com` | `(not set)` | 2 | 2 | 0 | 2 | 6 |
| `linkedin / social` | `(not set)` | `304525597` | 2 | 2 | 0 | 2 | 6 |
| `returnonsecurity.com / newsletter` | `security-funded-133-don-t-call-it-a-economic-comeback/` | `(not set)` | 2 | 2 | 0 | 2 | 6 |
| `qp / notice` | `notepie-release` | `bar` | 1 | 1 | 1 | 20 | 26 |
| `qp / notice` | `iso-42001-certification` | `bar` | 1 | 1 | 0 | 1 | 3 |
| `qp / notice` | `lingo-release` | `bar` | 1 | 1 | 0 | 1 | 3 |
| `qp / notice` | `notepie-release` | `card` | 1 | 1 | 0 | 1 | 3 |

## 4. Content / Term별 성과

### 4.1 `utm_content`성 값

| Content | 방문 | 방문자 | 조회 | 이벤트 |
|---------|-----:|-------:|-----:|-------:|
| `card` | 7 | 4 | 21 | 60 |
| `link_in_bio` | 4 | 3 | 5 | 13 |
| `bar` | 3 | 3 | 22 | 32 |
| `304525597` | 2 | 2 | 2 | 6 |

최근 30일에는 `card` 7방문/21조회, `bar` 3방문/22조회, `304525597` 2방문/2조회만 확인된다.

### 4.2 `utm_term`성 값

| Term | 방문 | 방문자 | 조회 | 이벤트 |
|------|-----:|-------:|-----:|-------:|
| `쿼리파이` | 25 | 25 | 51 | 143 |
| `주식회사 쿼리파이` | 1 | 1 | 1 | 4 |
| `쿼리파이 채용` | 1 | 1 | 1 | 5 |
| `파이` | 1 | 1 | 1 | 3 |

`utm_term`성 값은 대부분 `daum / organic`의 브랜드 검색어로 보인다. 엄밀한 광고 UTM이라기보다는 GA4 manual 계열에 잡힌 검색어성 값으로 분리해서 해석하는 것이 안전하다.

## 5. 조회 페이지

전체 기간 UTM-like 유입에서 조회가 가장 많이 발생한 페이지:

| Page path | 조회 | 방문자 | 이벤트 |
|-----------|-----:|-------:|-------:|
| `/ko` | 41 | 32 | 160 |
| `/` | 11 | 11 | 35 |
| `/ko/company/about-us` | 9 | 6 | 18 |
| `/en/news/24/iso-42001-certification-announcement` | 5 | 3 | 9 |
| `/ko/company/contact-us` | 5 | 4 | 6 |
| `/en/news/26/lingo-launch` | 4 | 2 | 6 |
| `/ja/features/documentation/blog/29/ai-attack-tool-firewall-breach-data-protection` | 4 | 2 | 17 |
| `/ko/news/24/iso-42001-certification-announcement` | 4 | 1 | 10 |
| `/en/news/27/notepie-launch` | 3 | 2 | 7 |
| `/ko/company/certifications` | 2 | 1 | 2 |

## 6. 클릭 이벤트

### 6.1 클릭 이벤트 요약

| 기간 | `click` | `select_promotion` | 클릭 합계 |
|------|--------:|-------------------:|----------:|
| 2026-03-09 ~ 2026-06-15 | 3 | 2 | 5 |
| 2026-05-16 ~ 2026-06-15 | 0 | 2 | 2 |

### 6.2 클릭 발생 위치

| Source / Medium | Campaign | Content | Event | Page path | 클릭 | 사용자 |
|-----------------|----------|---------|-------|-----------|-----:|-------:|
| `note / social` | `blog` | `(not set)` | `click` | `/ja/features/documentation/blog/29/ai-attack-tool-firewall-breach-data-protection` | 3 | 1 |
| `qp / notice` | `iso-42001-certification` | `card` | `select_promotion` | `/ko` | 2 | 1 |

### 6.3 UTM-like 유입 전체 이벤트 구성

| Event name | 전체 기간 이벤트 | 해석 |
|------------|----------------:|------|
| `page_view` | 120 | 페이지 조회 |
| `session_start` | 56 | 세션 시작 |
| `user_engagement` | 51 | 사용자 참여 |
| `first_visit` | 50 | 신규 방문 |
| `view_promotion` | 17 | 프로모션/공지 노출 |
| `scroll` | 14 | 스크롤 |
| `video_progress` | 4 | 영상 진행 |
| `click` | 3 | 클릭 |
| `video_start` | 2 | 영상 시작 |
| `select_promotion` | 2 | 프로모션/공지 선택 |
| `form_start` | 1 | 폼 시작 |

최근 30일에는 `page_view` 53, `session_start` 19, `view_promotion` 17, `user_engagement` 14, `first_visit` 14, `select_promotion` 2, `scroll` 2, `form_start` 1이 확인된다.

## 7. 결론

UTM-like 유입은 아직 운영 판단을 내릴 만큼 크지 않다. 전체 기간 방문 56, 조회 120, 클릭 5 수준이며, 최근 30일에도 방문 19, 조회 53, 클릭 2에 그친다.

현재 성과가 가장 뚜렷한 축은 `qp / notice` 캠페인이다. `iso-42001-certification`, `lingo-release`, `notepie-release`가 최근 30일 UTM-like 조회의 대부분을 만들고 있으며, 실제 클릭도 `iso-42001-certification`의 `card`에서 `select_promotion` 2건이 발생했다.

반면 `generate_lead`, `select_plan`, `form_type`, `plan_name` 기반 전환 집계가 아직 없기 때문에 “방문 → 조회 → 리드/플랜 선택” 퍼널은 완성되어 있지 않다. 지금 확인 가능한 것은 유입, 조회, 클릭/선택 이벤트까지이며, 전환 성과는 GA4 key event 설정 후 별도로 집계해야 한다.
