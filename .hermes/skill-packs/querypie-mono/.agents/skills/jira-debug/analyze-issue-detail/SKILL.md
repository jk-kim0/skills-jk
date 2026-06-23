---
name: jira-debug-analyze-issue-detail
description: |
  티켓의 에러 로그/스택 트레이스를 상세 분석합니다.
  - Exception 클래스명, 에러 메시지 추출
  - 스택 트레이스에서 호출 체인 파악
  - 재현 단계 추출
allowed-tools: []
---

# Analyze Issue Detail Skill

티켓에 포함된 에러 로그, 스택 트레이스, 재현 단계를 상세 분석합니다.

## 사용법

```
/jira-debug-analyze-issue-detail
```

이전에 `/jira-debug-fetch-ticket`으로 조회한 티켓 정보가 컨텍스트에 있어야 합니다.

## 분석 항목

### 1. Exception 분석

티켓 설명과 댓글에서 다음을 추출:

- **Exception 클래스명**: `NullPointerException`, `QueryExecutionException` 등
- **패키지 경로**: `com.querypie.dbam.service.DbamQueryService`
- **에러 메시지**: 전체 에러 텍스트

### 2. 스택 트레이스 분석

스택 트레이스가 있는 경우:

- 호출 체인 순서 파악 (어디서 시작해서 어디서 실패했는지)
- QueryPie 코드와 외부 라이브러리 구분
- 가장 관련 있는 메서드 3-5개 추출

### 3. HTTP 상태 코드 분석

- **4xx**: 클라이언트/API 레이어 문제
  - 400: 잘못된 요청 파라미터
  - 401/403: 인증/권한 문제
  - 404: 리소스 없음
- **5xx**: 서버 내부 문제
  - 500: 서버 에러
  - 502/503: 게이트웨이/서비스 불가
  - 504: 타임아웃

### 4. 재현 단계 추출

티켓에서 재현 단계(Steps to Reproduce)를 추출하여 구조화:

1. 어떤 화면/기능에서 시작했는지
2. 어떤 동작을 수행했는지
3. 어떤 결과가 발생했는지

### 5. 환경 정보 추출

- 브라우저/OS 정보
- QueryPie 버전
- 데이터소스 유형 (MySQL, PostgreSQL 등)

## 출력 형식

```json
{
  "error_type": "QueryExecutionException",
  "error_message": "Connection timeout after 30s",
  "package_path": "com.querypie.dbam.service.DbamQueryService",
  "stack_trace_summary": [
    "DbamQueryService.execute(DbamQueryService.kt:142)",
    "QueryEngine.run(QueryEngine.kt:58)",
    "ConnectionPool.getConnection(ConnectionPool.kt:89)"
  ],
  "http_status": 500,
  "http_analysis": "서버 내부 에러 - 백엔드 로직 또는 외부 연동 문제",
  "reproduction_steps": [
    "1. 대시보드에서 쿼리 실행 클릭",
    "2. 대용량 테이블에 SELECT * 실행",
    "3. 약 30초 후 timeout 에러 발생"
  ],
  "environment": {
    "browser": "Chrome 120",
    "os": "macOS",
    "querypie_version": "10.2.1",
    "datasource_type": "MySQL 8.0"
  },
  "suspected_cause": "Connection pool exhaustion 또는 slow query로 인한 timeout",
  "keywords_extracted": ["timeout", "쿼리 실행", "30초", "connection"]
}
```

## 분석 팁

### 에러 패턴 인식

| 패턴 | 가능한 원인 |
|------|------------|
| `NullPointerException` | 데이터 누락, 초기화 실패 |
| `TimeoutException` | 네트워크 지연, 쿼리 성능 |
| `ConnectionException` | 데이터소스 연결 문제 |
| `AuthenticationException` | 인증 토큰 만료, 권한 부족 |
| `ValidationException` | 입력값 검증 실패 |

### 로그 레벨 분석

- `ERROR`: 실제 문제 발생 지점
- `WARN`: 잠재적 문제 또는 예상 가능한 실패
- `INFO`: 동작 흐름 파악용

## 다음 단계

이 스킬의 출력은 다음 스킬들에서 사용됩니다:
- `/jira-debug-search-code` - 에러 발생 지점 코드 검색
- `/jira-debug-generate-report` - 분석 결과 리포트 생성
