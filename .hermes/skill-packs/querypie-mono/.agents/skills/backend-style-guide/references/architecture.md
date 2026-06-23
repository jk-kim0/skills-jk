# Architecture

## 아키텍처 - "반쯤 헥사고널"

### 계층 구조

```
Controller/interfaces (Entity → DTO 변환)
    ↓ (Entity)
ApplicationService (Entity 사용)
    ↓ (Entity)
Service (조합 + 비즈니스 검증)
    ↓ (Entity)
Entity (도메인 로직)
    ↓
Repository
```

---

## 패키지 구조 (필수) ⭐⭐⭐

```
{module}/
├── interfaces/         # API 계층 (HTTP, gRPC, MCP)
│   ├── http/
│   │   ├── admin/      # 관리자 API
│   │   ├── user/       # 사용자 API
│   │   └── external/   # 외부 API
│   ├── grpc/
│   └── mcp/
│
├── application/        # 애플리케이션 계층 (유스케이스)
│   ├── *ApplicationService.kt   # Command (CUD) + 트랜잭션
│   └── *QueryService.kt         # Query (R)
│
├── domain/             # 도메인 계층 (비즈니스 규칙)
│   ├── Entity.kt       # 엔티티 + 도메인 로직
│   ├── *Repository.kt  # 리포지토리 인터페이스
│   └── *Event.kt       # 도메인 이벤트
│
└── infrastructure/     # 인프라 계층 (외부 연동)
    ├── persistence/    # JPA 리포지토리 구현
    └── external/       # 외부 API 클라이언트
```

### 계층별 역할

| 계층 | 역할 | 의존 방향 |
|------|------|----------|
| interfaces | HTTP/gRPC 요청 처리, DTO 정의 | → application |
| application | 유스케이스, 트랜잭션, Entity 사용 | → domain |
| domain | 비즈니스 규칙, Entity, Repository 인터페이스 | 의존 없음 |
| infrastructure | DB, 외부 API 연동, Repository 구현 | → domain |

---

## 핵심 포인트

### 1. Entity = 도메인 모델 + 로직 (DDD)

- Entity가 단순 데이터 홀더가 아니라 비즈니스 로직 포함
- Anemic Domain Model 피하기

### 2. Entity는 Bean이 아님 → DI 불가 → Repository를 파라미터로 전달

```kotlin
// Entity - Bean 아니라 DI 못 받음
class Policy {
    companion object {
        fun create(..., repository: PolicyRepository) {  // 파라미터로 받음
            if (repository.existsByName(name)) {
                throw DuplicateException()
            }
            // 도메인 로직 + repository 사용
        }
    }
}
```

### 3. DTO 변환 경계 = Controller

- 헥사고널 DTO 변환 지옥 회피
- **Controller**: Entity ↔ DTO 변환
- **ApplicationService 이하**: Entity 직접 사용

### 4. CQRS 패턴

- **ApplicationService**: Command (CUD) - `@Transactional`
- **QueryService**: Query (R) - Repository/QueryDSL 직접 접근, 트랜잭션 불필요

---

## 서비스 레이어 역할

| 레이어 | 역할 |
|--------|------|
| ApplicationService | 유스케이스 대응, 트랜잭션 |
| Service | 조합 + 비즈니스 로직 검증 |
| Entity | 단일 Entity 도메인 로직 |

---

## 모듈 의존 관계

```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│   DAC   │ │   SAC   │ │   KAC   │ │   WAC   │ │   AI    │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │  app 모듈 │           │           │           │
     └───────────┴─────┬─────┴───────────┴───────────┘
                       ↓
              ┌────────────────┐
              │      IAM       │
              └────────┬───────┘
                       ↓
              ┌────────────────┐
              │     common     │
              └────────────────┘
```

### 모듈별 위치

- **DAC**: `app/src/main/kotlin/com/querypie/dac/` (app 모듈 내부)
- **SAC**: `app/src/main/kotlin/com/querypie/sam/` (app 모듈 내부)
- **KAC**: `kac/` (독립 Gradle 모듈)
- **WAC**: `wac/` (독립 Gradle 모듈)
- **IAM**: `iam/` (독립 Gradle 모듈)

> **기술 부채**: app 모듈 내 DAC/SAC는 분리 필요

---

## 모듈간 통신 패턴

### 정석: Finder 인터페이스

```kotlin
// common 모듈에 인터페이스 정의
interface UserFinder {
    fun findByUuid(uuid: UUID): User?
}

// iam 모듈에서 구현
@Component
class UserFinderImpl(
    private val userRepository: UserRepository
) : UserFinder {
    override fun findByUuid(uuid: UUID) = userRepository.findByUuid(uuid)
}

// 다른 모듈에서 사용
class SomeService(private val userFinder: UserFinder) { ... }
```

### 정석: 이벤트 기반 통신

```kotlin
// 도메인 이벤트 발행
EventPublisher.instance().publish(WebAppCreatedEvent(webApp))

// 다른 모듈에서 구독
@EventListener
fun onWebAppCreated(event: WebAppCreatedEvent) { ... }
```

### 비정석: Client 클래스 (IAM 특수 케이스)

```kotlin
// iam 모듈의 UserClient - 비정석이지만 존재
@Component
class UserClient(private val userRepository: UserRepository) { ... }
```

---

## 정석 예시 파일 (KAC)

| 역할 | 파일 |
|------|------|
| Controller (DTO ↔ Entity 변환) | `kac/interfaces/http/admin/KubeClusterPolicyController.kt` |
| ApplicationService | `kac/application/access/KubeClusterPolicyApplicationService.kt` |
| QueryService | `kac/application/access/KubeClusterPolicyQueryService.kt` |
| Entity (정석) | `kac/domain/access/policy/KubeClusterPolicy.kt` |

### 전체 흐름

```
Controller → ApplicationService → Entity (repository 파라미터)
                ↓
            QueryService → Repository/QueryDSL 직접
```
