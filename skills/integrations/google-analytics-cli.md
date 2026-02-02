---
name: google-analytics-cli
description: Google Analytics (GA4) 및 Search Console 데이터 조회 시 사용
tags: [google, analytics, search-console, seo, cli, integration]
---

# Google Analytics & Search Console CLI

## 개요

Google Analytics Data API (GA4) 및 Search Console API에 접근하기 위한 CLI 도구입니다.

| 서비스 | CLI | 위치 |
|--------|-----|------|
| Google Analytics | `ga` | `bin/ga` |
| Search Console | `gsc` | `bin/gsc` |

## 초기 설정

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. APIs & Services > Library에서 API 활성화:
   - Google Analytics Data API
   - Google Analytics Admin API
   - Search Console API
4. APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID
   - Application type: Desktop app
   - 생성된 클라이언트 시크릿 JSON 파일 다운로드

### 2. 클라이언트 시크릿 설정

```bash
# 디렉토리 생성
mkdir -p ~/.config/google

# 다운로드한 JSON 파일 이동
mv ~/Downloads/client_secret_*.json ~/.config/google/client_secret.json

# 또는 환경변수로 경로 지정
export GOOGLE_CLIENT_SECRET=~/.config/google/client_secret.json
```

### 3. Python 패키지 설치

```bash
pip install google-auth google-auth-oauthlib google-api-python-client google-analytics-data google-analytics-admin
```

### 4. 첫 실행 (OAuth 인증)

```bash
# 첫 실행 시 브라우저에서 Google 계정 인증
ga accounts

# 인증 완료 후 토큰이 자동 저장됨
# - GA 토큰: ~/.config/ga/token.pickle
# - GSC 토큰: ~/.config/gsc/token.pickle
```

## Google Analytics CLI (`ga`)

### 명령어

```bash
ga <command> [args]
```

| 명령어 | 설명 |
|--------|------|
| `accounts` | 계정 및 속성 목록 |
| `report <property_id>` | 트래픽 리포트 (일별 세션, 사용자, 페이지뷰) |
| `pages <property_id>` | 페이지별 성과 |
| `sources <property_id>` | 트래픽 소스별 성과 |

### 사용 예시

```bash
# 계정 및 Property ID 확인
ga accounts

# 최근 7일 트래픽 리포트
ga report 451236681

# 최근 30일 트래픽 리포트
ga report 451236681 --days 30

# 페이지별 성과 (Top 50)
ga pages 451236681 --days 30

# 트래픽 소스별 성과
ga sources 451236681 --days 30
```

### 주요 Property ID

| 서비스 | Property ID | 설명 |
|--------|-------------|------|
| QueryPie Homepage | 451239708 | 홈페이지 |
| ACP Docs | 522469891 | 문서 사이트 |
| ACP Application | 451236681 | 웹 콘솔 |

### 출력 예시

```
================================================================================
  트래픽 리포트: Property 451236681
  기간: 2026-01-24 ~ 2026-01-31
================================================================================

날짜            세션       사용자     페이지뷰        이탈률       평균시간
--------------------------------------------------------------------------------
20260127        5210       1890      46302       10.9%     532.5s
20260128        4909       1812      43005       11.1%     545.7s
```

## Search Console CLI (`gsc`)

### 명령어

```bash
gsc <command> [args]
```

| 명령어 | 설명 |
|--------|------|
| `sites` | 등록된 사이트 목록 |
| `sitemaps <site_url>` | 사이트맵 목록 및 인덱싱 상태 |
| `inspect <site_url> <page_url>` | URL 인덱싱 상태 검사 |
| `query <site_url>` | 검색 성능 데이터 (검색어, 페이지별) |
| `query <site_url> --by-date` | 날짜별 검색 성능 |
| `query <site_url> --by-country` | 국가별 검색 성능 |
| `query <site_url> --by-device` | 디바이스별 검색 성능 |
| `query <site_url> --by-appearance` | 검색 형태별 검색 성능 |
| `pages <site_url>` | 페이지별 검색 성능 |

### 사용 예시

```bash
# 등록된 사이트 목록
gsc sites

# 사이트맵 목록 및 인덱싱 현황
gsc sitemaps "https://www.querypie.com/"

# URL 인덱싱 상태 검사 (SEO 진단용)
gsc inspect "https://www.querypie.com/" "https://www.querypie.com/pricing"

# 최근 7일 검색 성능 (검색어/페이지별)
gsc query "https://www.querypie.com/"

# 최근 30일 검색 성능
gsc query "https://www.querypie.com/" --days 30

# 날짜별 검색 성능
gsc query "https://www.querypie.com/" --by-date --days 30

# 국가별 검색 성능
gsc query "https://www.querypie.com/" --by-country --days 30

# 디바이스별 검색 성능
gsc query "https://www.querypie.com/" --by-device

# 페이지별 검색 성능 (상위 50개)
gsc pages "https://www.querypie.com/" --days 30 --limit 50
```

### 출력 예시

**검색 성능 (query)**
```
================================================================================
  검색 성능 데이터: https://www.querypie.com/
  기간: 2026-01-21 ~ 2026-01-28
================================================================================

    클릭         노출      CTR       순위  검색어 / 페이지
--------------------------------------------------------------------------------
      15        1234     1.2%       8.5  querypie
                                         https://www.querypie.com/
```

**사이트맵 (sitemaps)**
```
================================================================================
  사이트맵 목록: https://app.querypie.com/
================================================================================

상태           유형           제출일               URL 수  경로
--------------------------------------------------------------------------------
정상           sitemap      2026-01-14          156  https://app.querypie.com/sitemap/publication-1.xml
             └─ web: 제출 156, 인덱싱 0
```

**URL 검사 (inspect)**
```
======================================================================
  URL 검사 결과
======================================================================
  검사 URL: https://www.querypie.com/pricing
  사이트: https://www.querypie.com/
======================================================================

[ 인덱싱 상태 ]
  상태: ✅ 인덱싱됨
  커버리지: Submitted and indexed
  robots.txt: ALLOWED
  인덱싱 허용: INDEXING_ALLOWED
  마지막 크롤링: 2026-01-28 09:15:32
  Google 선택 Canonical: https://www.querypie.com/pricing

[ 모바일 사용성 ]
  상태: ✅ 모바일 친화적
```

## 주요 지표 정의

### Google Analytics

| 지표 | 정의 |
|------|------|
| Sessions (세션) | 사용자의 방문 단위 (30분 비활동 시 새 세션) |
| Active Users (사용자) | 고유 사용자 수 (쿠키 기반, 중복 제거) |
| DAU | Daily Active Users - 하루 고유 사용자 수 |
| Bounce Rate (이탈률) | 단일 페이지 세션 비율 |
| Avg. Session Duration | 평균 세션 시간 |

### Search Console

| 지표 | 정의 |
|------|------|
| Clicks (클릭) | 검색 결과에서 사이트로 이동한 클릭 수 |
| Impressions (노출) | 검색 결과에 표시된 횟수 |
| CTR | Click-Through Rate = 클릭 / 노출 |
| Position (순위) | 검색 결과 평균 게재 순위 |

### URL Inspection 상태값

| 상태 | 의미 |
|------|------|
| `PASS` | 인덱싱됨, 문제 없음 |
| `PARTIAL` | 부분적으로 인덱싱됨 |
| `FAIL` | 인덱싱 실패 |
| `NEUTRAL` | 인덱싱 상태 확인 불가 (URL이 Google에 알려지지 않음) |

| 커버리지 상태 | 의미 |
|---------------|------|
| `Submitted and indexed` | 제출되어 인덱싱됨 |
| `Crawled - currently not indexed` | 크롤링됐지만 인덱싱되지 않음 |
| `Discovered - currently not indexed` | 발견됐지만 크롤링/인덱싱 안됨 |
| `URL is unknown to Google` | Google에 알려지지 않은 URL |
| `Blocked by robots.txt` | robots.txt에 의해 차단됨 |

## 토큰 관리

인증 토큰은 다음 위치에 저장됩니다:

| 서비스 | 토큰 위치 |
|--------|----------|
| Google Analytics | `~/.config/ga/token.pickle` |
| Search Console | `~/.config/gsc/token.pickle` |

토큰 갱신이 필요한 경우 해당 파일을 삭제하고 다시 실행하면 됩니다:

```bash
rm ~/.config/ga/token.pickle
ga accounts  # 브라우저에서 재인증

rm ~/.config/gsc/token.pickle
gsc sites    # 브라우저에서 재인증
```

**참고**: URL Inspection API를 처음 사용하는 경우, 추가 권한이 필요하여 토큰 재인증이 필요할 수 있습니다.

## 참고 링크

- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Google Analytics Admin API](https://developers.google.com/analytics/devguides/config/admin/v1)
- [Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original)
