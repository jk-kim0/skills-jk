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
| `query <site_url>` | 검색 성능 데이터 (검색어, 페이지별) |
| `query <site_url> --by-date` | 날짜별 검색 성능 |

### 사용 예시

```bash
# 등록된 사이트 목록
gsc sites

# 최근 7일 검색 성능 (검색어/페이지별)
gsc query "https://www.querypie.com/"

# 최근 30일 검색 성능
gsc query "https://www.querypie.com/" --days 30

# 날짜별 검색 성능
gsc query "https://www.querypie.com/" --by-date --days 30
```

### 출력 예시

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
```

## 참고 링크

- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Google Analytics Admin API](https://developers.google.com/analytics/devguides/config/admin/v1)
- [Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original)
