---
name: jira-debug-search-code
description: |
  identify-components와 analyze-issue-detail 결과를 바탕으로 문제가 발생했을 코드를 추적합니다.
  - 컴포넌트 내 관련 코드 검색
  - 호출 체인 추적
  - 잠재적 문제점 분석
allowed-tools:
  - Grep
  - Glob
  - Read
  - Task
---

# Search Code Skill

분석 결과를 바탕으로 querypie-mono-3 코드베이스에서 문제 코드를 추적합니다.

## 사용법

```
/jira-debug-search-code "QueryExecutionException"
```

또는 이전 스킬들의 분석 결과가 컨텍스트에 있으면:

```
/jira-debug-search-code
```

## 코드베이스 구조

querypie-mono-3 프로젝트의 주요 경로:

| 컴포넌트 | 경로 | 언어 | 주요 파일 패턴 |
|---------|------|-----|---------------|
| API 공통 | `apps/api/app/` | Kotlin | `*Controller.kt`, `*Service.kt` |
| DAC (DB) | `apps/api/dbam/` | Kotlin | `Dac*.kt`, `Dbam*.kt` |
| SAC (서버) | `apps/api/sam/` | Kotlin | `Sac*.kt`, `Sam*.kt` |
| KAC (K8s) | `apps/api/kac/` | Kotlin | `Kac*.kt`, `Kube*.kt` |
| IAM (인증) | `apps/api/iam/` | Kotlin | `Iam*.kt`, `Auth*.kt` |
| Engine | `apps/engine/` | Kotlin/Java | `*.kt`, `*.java` |
| CommandPie Engine | `apps/commandpie-engine/` | Kotlin/Java | `*.kt`, `*.java` |
| Arisa (Proxy) | `apps/arisa/` | Kotlin/Java | `*.kt`, `*.java` |
| Multi-Agent | `apps/multi-agent/` | Swift/Kotlin | `*.swift`, `*.kt` |
| Front | `apps/front/` | TypeScript | `*.tsx`, `*.ts` |
| Agent | `apps/agent/` | Go | `*.go` |

## 검색 전략

### Strategy 1: 컴포넌트 기반 검색

`jira-debug-identify-components`에서 식별된 컴포넌트를 우선 검색:

```
primary_components (높은 신뢰도) → 집중 검색
secondary_components (낮은 신뢰도) → 보조 검색
```

### Strategy 2: Entry Point 찾기

**API (Backend):**
1. Controller/Router에서 엔드포인트 검색
2. `@GetMapping`, `@PostMapping` 등 어노테이션으로 검색
3. URL 패턴으로 검색

**Front:**
1. 페이지 컴포넌트에서 API 호출 검색
2. `useQuery`, `useMutation` 등 훅 검색

### Strategy 3: 호출 체인 추적

```
1. Controller → Service 호출 따라가기
2. Service 내 비즈니스 로직 분석
3. Repository/DAO 레이어 추적
4. 외부 시스템 연동 코드 검색
```

### Strategy 4: 에러 발생 지점 추적

```
1. Exception 클래스 정의 찾기
2. throw 하는 위치 찾기
3. catch 하는 위치 찾기
4. 에러 조건 분석
```

### Strategy 5: 키워드 기반 검색

```
1. 에러 메시지 문자열 검색
2. 관련 설정값 검색 (timeout, retry, pool 등)
3. 로그 메시지 검색
```

## 검색 실행 예시

### Exception 클래스 검색
```
Grep: pattern="class QueryExecutionException"
      path="apps/api/"
```

### 에러 메시지 검색
```
Grep: pattern="Connection timeout"
      path="apps/"
      glob="*.kt"
```

### 설정값 검색
```
Grep: pattern="timeout|TIMEOUT"
      path="apps/api/dbam/"
```

### Controller 엔드포인트 검색
```
Grep: pattern="@.*Mapping.*query"
      path="apps/api/"
```

## 출력 형식

```json
{
  "findings": [
    {
      "file": "apps/api/dbam/src/main/kotlin/com/querypie/dbam/service/DbamQueryService.kt",
      "line": 142,
      "code_snippet": "fun execute(query: String, timeout: Long = 30000L) {\n    // ...\n}",
      "relevance": "high",
      "analysis": "timeout 값이 30초로 하드코딩되어 있음. 환경변수로 설정 가능하게 변경 권장"
    },
    {
      "file": "apps/api/app/src/main/kotlin/com/querypie/api/dac/DacController.kt",
      "line": 58,
      "code_snippet": "@PostMapping(\"/execute\")\nfun executeQuery(...)",
      "relevance": "medium",
      "analysis": "API 진입점. 에러 핸들링에서 원본 에러 메시지가 유실될 수 있음"
    }
  ],
  "call_chain": [
    "DacController.executeQuery() [apps/api/app/.../DacController.kt:58]",
    "DbamQueryService.execute() [apps/api/dbam/.../DbamQueryService.kt:142]",
    "QueryEngine.run() [apps/engine/.../QueryEngine.kt:89]"
  ],
  "potential_issues": [
    {
      "issue": "timeout 값이 30초로 고정",
      "location": "DbamQueryService.kt:142",
      "suggestion": "환경변수 또는 설정 파일로 변경 가능하게 수정"
    },
    {
      "issue": "connection pool exhausted 시 명확한 에러 메시지 없음",
      "location": "ConnectionPool.kt:89",
      "suggestion": "pool 상태를 로깅하고 명확한 에러 메시지 추가"
    }
  ],
  "related_files": [
    "apps/api/dbam/src/main/kotlin/com/querypie/dbam/config/DbamConfig.kt",
    "apps/api/dbam/src/main/resources/application.yml"
  ]
}
```

## 검색 팁

### 효율적인 검색 순서

1. 먼저 `Glob`으로 파일 존재 확인
2. `Grep`으로 패턴 검색
3. 관련 파일을 `Read`로 상세 확인
4. 복잡한 검색은 `Task` (Explore agent)로 위임

### 검색 범위 제한

- 항상 `jira-debug-identify-components`에서 식별된 경로로 범위 제한
- 불필요한 전체 검색 지양
- test 파일은 필요시에만 포함

## 다음 단계

이 스킬의 출력은 다음 스킬에서 사용됩니다:
- `/jira-debug-generate-report` - 검색 결과를 리포트로 생성
