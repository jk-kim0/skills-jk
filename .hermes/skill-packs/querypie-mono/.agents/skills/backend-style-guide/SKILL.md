---
name: backend-style-guide
description: |
  apps/api 백엔드 코드 작성, 수정, PR 리뷰, PR 리뷰 피드백 반영 시 사용.

  [필수] DDD 계층 분리, @Authorization, 이벤트 발행, HA(Stateless), Collation, COMMENT
  [권장] CQRS, CachedRepository, fetchJoin, 트랜잭션 최소화
  [금지] FK, N+1, 계층 역방향 참조, wildcard import, WebClient 매번 생성, 민감정보 로깅

  트리거: 백엔드 코드 작성, Kotlin/Spring 코드 리뷰, PR 리뷰, API 구현, JPA/QueryDSL 작업, gRPC 개발
---

# Backend Style Guide

## 사용 지침

1. 이 문서의 체크리스트로 빠르게 검토
2. 필요시 상세 문서 참조 (`references/` 폴더)
3. 체크리스트에 없는 문제도 발견하면 지적

## 심각도 분류

| 심각도 | 설명 | 예시 |
|--------|------|------|
| **Critical** | 서비스 장애/보안 사고 유발 | 리소스 누수, 보안 취약점, 데이터 손실 |
| **Major** | 필수 규칙 위반 | 아키텍처 위반, FK 사용, N+1 |
| **Minor** | 권장 규칙 위반 | 로깅 포맷, 네이밍 |
| **Suggestion** | 개선 제안 | 리팩토링, 가독성 |

---

## 체크리스트

### 1. Critical 🚨

코드를 읽으며 스스로 질문:

| 관점 | 질문 |
|------|------|
| 에러 발생 시 | 예외 시 원본 데이터 노출되는가? (Fail-Open) |
| 대용량 입력 시 | 메모리에 전체 로드하는가? OOM 위험? |
| 외부 호출 실패 시 | 타임아웃 설정 있는가? 무한 대기? |
| 리소스 정리 | Stream/Connection이 `.use {}` 블록 안에 있는가? |
| 트랜잭션 범위 | 트랜잭션 내 외부 API 호출하는가? |
| 비동기 전환 시 | ThreadLocal 값이 유실되는가? |
| 동시 요청 시 | 동시 수정 시 레이스 컨디션 있는가? |
| 권한 검증 | `@Authorization` 있는가? |
| `@Bean` 등록 시 | Spring Boot auto-config 타입(`ObjectMapper`, `DataSource` 등)과 충돌하는가? |

상세: [`references/security.md`](references/security.md)

### 2. 필수 규칙 (Major)

#### 아키텍처

| 규칙 | 확인 |
|------|------|
| 계층 분리 | interfaces → application → domain ← infrastructure |
| 패키지 구조 | `interfaces/`, `application/`, `domain/`, `infrastructure/` |
| 의존 방향 | 상위 → 하위만. 역방향 금지 |
| Entity | 비즈니스 로직 포함 (Anemic Domain 금지) |

상세: [`references/architecture.md`](references/architecture.md)

#### 패턴

| 규칙 | 확인 |
|------|------|
| @Authorization | API 엔드포인트에 권한 검증 필수 |
| 이벤트 발행 | CUD 후 `EventPublisher.instance().publish()` |
| import | wildcard (`.*`) 금지 |
| 로깅 | `logger.info("msg={}", msg)` (템플릿 금지) |
| ERROR 레벨 | 시스템 장애만. 비즈니스 예외는 INFO/WARN |

상세: [`references/patterns.md`](references/patterns.md)

#### DB

| 규칙 | 확인 |
|------|------|
| Collation | `utf8mb4_general_ci` 명시 |
| COMMENT | 테이블/컬럼 COMMENT 필수 |
| FK 금지 | UUID 참조만 사용 |
| 롤백 스크립트 | enum 추가 시 `db/log/rollback/{version}.sql` |

상세: [`references/database.md`](references/database.md)

#### 보안

| 규칙 | 확인 |
|------|------|
| HA/Stateless | 로컬 메모리 저장 금지 → Redis |
| 민감정보 | 비밀번호, 토큰, API Key 로깅 금지 |
| 암호화 | `@Convert(converter = AESConverter::class)` |
| Redis 락 TTL | 예상 작업 시간 + 여유분으로 동적 계산 |
| Redis 캐시 | 사용 완료 후 즉시 삭제 (TTL 대기 금지) |

상세: [`references/security.md`](references/security.md)

### 3. 권장 규칙 (Minor)

| 항목 | 권장 |
|------|------|
| CQRS | ApplicationService(CUD) / QueryService(R) 분리 |
| QueryService | 기본 트랜잭션 없음. LAZY 필요시만 `readOnly=true` |
| N+1 방지 | `fetchJoin()` 또는 `@EntityGraph` |
| LAZY 기본 | `@ManyToOne(fetch = FetchType.LAZY)` |
| WebClient | Bean으로 DI, 매번 생성 금지 |
| CachedRepository | 자주 조회 데이터에 Redis 캐싱 |

### 4. Kotlin/Spring 특화

| 항목 | 확인 |
|------|------|
| null 안전성 | `!!` 남용 금지. `?: throw` 또는 `requireNotNull` |
| scope function | `let`/`run`/`apply`/`also` 적절히 선택 |
| 불변성 | 변경 불필요 필드는 `val` |
| @Transactional | CUD에만. READ는 필요시만 `readOnly=true` |
| @Async | 예외 처리 확인 (기본 무시됨) |
| Destructuring | `split()` 결과 크기 검증 후 사용 |
| NotImplementedError | throw 대신 warn 로그 (런타임 크래시 방지) |

### 5. JPA/QueryDSL 특화

| 항목 | 확인 |
|------|------|
| N+1 | 연관 객체 접근 시 추가 쿼리 발생 여부 |
| 페이징 | 대량 조회 시 페이징 처리 |
| 반복 쿼리 | 루프 내 DB 호출 금지 → `IN` 또는 `saveAll` |
| LAZY 접근 | 트랜잭션 밖에서 LAZY 프록시 접근 금지 |

### 6. gRPC 특화

| 항목 | 확인 |
|------|------|
| protobuf 호환성 | 필드 번호 변경 금지, 삭제 시 reserved |
| 스트림 에러 | `onErrorResume` / `doOnError` 처리 |
| deadline | gRPC 호출에 deadline 설정 |

---

## 빠른 참조

### 패키지 구조

```
{module}/
├── interfaces/     # HTTP/gRPC/MCP 컨트롤러
├── application/    # ApplicationService, QueryService
├── domain/         # Entity, Repository 인터페이스, Event
└── infrastructure/ # JPA 구현, 외부 연동
```

### 코드 예시

```kotlin
// 권한 검증
@Authorization(action = ActionType.WEB_APP_CREATE)
fun createWebApp(request: CreateRequest): WebApp

// 이벤트 발행
EventPublisher.instance().publish(WebAppCreatedEvent(webApp))

// 로깅 (O)
logger.info("msg={}, count={}", msg, list.size)

// 로깅 (X)
logger.info("msg=$msg, count=${list.size}")
```

---

## 리뷰 출력 형식

```markdown
## 리뷰 요약

| 심각도 | 개수 |
|--------|------|
| Critical | N개 |
| Major | N개 |
| Minor | N개 |

---

## Critical 🚨

### [1] 이슈 제목
**파일**: `경로:라인`
**문제**: 설명
**수정안**: 제안 코드

---

## Major

### [1] 이슈 제목
**파일**: `경로:라인`
**문제**: 설명
**수정안**: 제안

---

## Minor

- `파일:라인` - 설명
```

---

## 상세 문서

| 문서 | 내용 |
|------|------|
| [`references/architecture.md`](references/architecture.md) | 패키지 구조, 계층 분리, CQRS, 모듈 의존 |
| [`references/patterns.md`](references/patterns.md) | Entity 패턴, 로깅, 트랜잭션, 권한, Kotlin 스타일 |
| [`references/database.md`](references/database.md) | Collation, FK, N+1, 롤백 스크립트 |
| [`references/security.md`](references/security.md) | HA, ThreadLocal, WebClient, 암호화 |

## 도메인 지식 참조

프로토콜/스펙 관련 코드는 공식 문서 검색:

| 도메인 | 참조 |
|--------|------|
| HTTP | MDN, RFC 7231 |
| gRPC | grpc.io |
| OAuth/OIDC | RFC 6749, RFC 7519 |
| Kubernetes | kubernetes.io |

### 모듈별 AGENTS.md

| 도메인 | 위치 |
|--------|------|
| DAC/SAC | `app/AGENTS.md` |
| KAC | `kac/AGENTS.md` |
| WAC | `wac/AGENTS.md` |
| IAM | `iam/AGENTS.md` |
