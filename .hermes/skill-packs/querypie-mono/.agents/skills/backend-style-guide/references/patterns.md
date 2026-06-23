# Patterns

## Entity 패턴 - KAC 방식 (정석) ⭐⭐⭐

### Entity에서 도메인 로직 처리

```kotlin
// kac/domain/access/policy/KubeClusterPolicy.kt

// 1. create - 검증 + 저장 + 이벤트
companion object {
    fun createManaged(..., repository: KubeClusterPolicyRepository): KubeClusterPolicy {
        if (repository.existsByName(name)) {
            throw KubeClusterPolicyDuplicateException(name)  // 검증
        }
        val policy = KubeClusterPolicy(...)
        val saved = repository.save(policy)  // 저장
        EventPublisher.instance().publish(
            KubeClusterPolicyCreatedEvent(
                deltas = ModelUpdater.deltaForCreate(saved, Properties.all),
            )
        )
        return saved
    }
}

// 2. update - 검증 + ModelUpdater로 변경 추적 + 이벤트
fun update(..., repository: KubeClusterPolicyRepository) {
    if (this.name != name && repository.existsByName(name)) {
        throw KubeClusterPolicyDuplicateException(name)
    }
    val modelUpdater = ModelUpdater(this, Properties.updatables())
    modelUpdater.setIfChanged(Properties.NAME, name)
    modelUpdater.setIfChanged(Properties.DESCRIPTION, description)

    if (modelUpdater.hasChanged()) {
        repository.save(this)
        EventPublisher.instance().publish(
            KubeClusterPolicyUpdatedEvent(deltas = modelUpdater.delta)
        )
    }
}

// 3. delete - 삭제 + 이벤트
fun delete(deletedBy: UserIdAndUuid, repository: KubeClusterPolicyRepository) {
    repository.delete(this)
    EventPublisher.instance().publish(
        KubeClusterPolicyDeletedEvent(
            deltas = ModelUpdater.deltaForDelete(this, Properties.all),
        )
    )
}
```

### Properties (ModelProperty) - Activity Log용

```kotlin
object Properties : ModelPropertyListable<KubeClusterPolicy> {
    val NAME = ModelProperty.of<KubeClusterPolicy, String>(
        name = "name",       // 로그 key
        label = "Name",      // 로그 label
        getValue = { it.name },
        setValue = { m, v -> m.name = v },
    )
    // ...
    override val all = listOf(NAME, DESCRIPTION, CONTENT, VERSION)
    override fun updatables() = all - VERSION
}
```

### ModelUpdater - 변경 추적

```kotlin
val modelUpdater = ModelUpdater(this, Properties.updatables())
modelUpdater.setIfChanged(Properties.NAME, name)

if (modelUpdater.hasChanged()) {
    EventPublisher.instance().publish(
        WebAppUpdatedEvent(deltas = modelUpdater.delta)
    )
}
```

---

## Controller 패턴

### DTO만 사용

```kotlin
@PostMapping
@Authorization(action = ActionType.KUBE_CLUSTER_POLICY_CREATE)
fun addPolicy(
    @RequestBody request: AddRequest,  // DTO
    @AuthenticationPrincipal sessionUser: SessionUser,
): AddResponse {  // DTO
    val policy = kubeClusterPolicyApplicationService.add(...)
    return AddResponse(policy.uuid.toString())
}

// DTO는 Controller 내부에 정의
data class AddRequest(val name: String, val description: String?) : ApiModel
data class AddResponse(val uuid: String) : ApiModel
```

---

## ApplicationService 패턴

### Entity 메서드 호출 + Repository 전달

```kotlin
@Service
class KubeClusterPolicyApplicationService(
    private val kubeClusterPolicyRepository: KubeClusterPolicyRepository,
) {
    @Transactional  // CUD에만!
    fun add(name: String, description: String?, createdBy: UserIdAndUuid): KubeClusterPolicy {
        return KubeClusterPolicy.createManaged(
            name = name,
            description = description,
            createdBy = createdBy,
            repository = kubeClusterPolicyRepository,  // Repository 전달!
        )
    }

    @Transactional
    fun edit(uuid: UUID, name: String, description: String?, updatedBy: UserIdAndUuid) {
        val policy = kubeClusterPolicyRepository.findByUuidOrThrow(uuid)
        policy.update(
            name = name,
            description = description,
            updatedBy = updatedBy,
            repository = kubeClusterPolicyRepository,
        )
    }
}
```

---

## 트랜잭션 패턴

### CUD는 @Transactional, READ는 필요시만 readOnly=true

```kotlin
@Service
class SomeApplicationService {
    @Transactional  // CUD에만!
    fun create(...) { ... }

    @Transactional
    fun update(...) { ... }
}

@Service
class SomeQueryService {
    // 기본: 트랜잭션 없음
    fun findById(...) { ... }

    // 필요한 경우에만 readOnly=true
    @Transactional(readOnly = true)
    fun findWithDetails(...) { ... }
}
```

### READ에서 @Transactional(readOnly = true)가 필요한 경우

| 상황 | 설명 |
|------|------|
| **LAZY 로딩** | 연관 엔티티 접근 시 트랜잭션 필요 (없으면 LazyInitializationException) |
| **일관된 읽기** | 여러 조회가 같은 시점의 데이터를 봐야 할 때 (DB 스냅샷) |
| **DB Replica 라우팅** | readOnly 힌트로 읽기 전용 DB로 라우팅 가능 |

### readOnly=true의 장점 (vs 일반 @Transactional)

| 장점 | 설명 |
|------|------|
| **Hibernate snapshot 생략** | loaded state를 저장하지 않아 메모리 절약 |
| **dirty checking 비활성화** | flush 시 변경 감지 안 함 → 성능 향상 |

> 참고: [Vlad Mihalcea - Spring read-only transaction Hibernate optimization](https://vladmihalcea.com/spring-read-only-transaction-hibernate-optimization/)

### READ에 @Transactional 없이 가능한 경우

| 상황 | 설명 |
|------|------|
| **단순 조회** | fetchJoin으로 이미 로딩 완료, LAZY 접근 없음 |
| **DTO 직접 조회** | Projection으로 엔티티 없이 바로 DTO 반환 |
| **단일 조회** | 일관된 읽기가 불필요한 경우 |

---

## 권한 체계 (Permission, Role, @Authorization)

### 구조

```
@Authorization(action = ActionType.XXX)
         ↓ (checks)
    ActionType ──────────► ResourceType
         ↓ (requires)            ↓ (belongs to)
  Set<PermissionType>         Product
         ↓ (filters by)          ↑ (has)
       License ──────────────────┘
         ↑ (constrains)
    Role/PredefinedRole
         ↑ (assigned to)
       User
```

### 정의

| 타입 | 의미 | 파일 |
|------|------|------|
| **ActionType** | API 작업 단위. ResourceType + PermissionType 집합 | `common/.../ActionType.kt` |
| **ResourceType** | 접근 대상 리소스. Product 정보 포함 | `common/.../ResourceType.kt` |
| **PermissionType** | 세분화된 권한 단위. Product 정보 포함 | `common/.../PermissionType.kt` |
| **Product** | 제품 단위 (DAC, SAC, KAC, WAC) | `libs/api-common/.../License.kt` |
| **License** | 보유 Product 집합. 권한 필터링 기준 | `iam/.../License.kt` |
| **Role** | 권한(PermissionType) 집합 | `iam/.../Role.kt` |
| **@Authorization** | 권한 검증 어노테이션 | `iam/.../Authorization.kt` |

### 라이선스 기반 권한 필터링

사용자의 역할 권한은 **라이선스가 보유한 Product**에 따라 동적 필터링됨

```kotlin
// 예: DAC 라이선스가 없으면 DAC_ACL_WRITE 권한은 부여되지 않음
val permissions = Role.permissions(roles, license.products)
```

### @Authorization 사용법

```kotlin
@Authorization(action = ActionType.KUBE_CLUSTER_CREATE)
fun createCluster(request: CreateRequest): CreateResponse

// 옵션
@Authorization(
    action = ActionType.XXX,
    skipLicenseCheck = false,
    optionalAuthentication = false,
    skipIpBandsCheck = false,
    skipUserIpBandsCheck = false,
)
```

---

## 캐싱 패턴 (CachedRepository)

### 용도

- **필수 아님** - 성능 최적화 용도
- 태그 기반으로 사용자/서버 조회 등 자주 조회되는 데이터에 사용

### 구조

```kotlin
@Component
class UserCachedRepository(
    redisTemplate: RedisTemplate<String, String>,
    userRepository: UserRepository,
    refreshScheduler: CacheRefreshScheduler,
) : CachedRepository<EventType, UUID, UserCached>(
    redisTemplate = redisTemplate,
    name = "user",
    refreshPolicy = RefreshPolicy.FETCH_ALL,
    missingPolicy = MissingPolicy.FETCH,
    eventHandlePolicy = EventHandlePolicy(
        update = setOf(UserEventType.USER_CREATED, ...),
        remove = setOf(UserEventType.USER_DELETED),
    ),
    originalDataRepository = Provider(userRepository),
) {
    init {
        refreshScheduler.addEveryTenMinuteSchedule("user") {
            refreshAll()
        }
    }
}
```

### 핵심 포인트

1. **이벤트 기반 캐시 무효화** - 도메인 이벤트 발생 시 자동 갱신/삭제
2. **Redis 기반** - `RedisTemplate` 사용
3. **주기적 갱신** - `CacheRefreshScheduler`로 스케줄링

---

## Value Object vs Entity (DDD)

### Entity

- **식별자(UUID)** 있음
- **독립적인 생명주기**
- JPA `@Entity`

```kotlin
@Entity
class KubeCluster(
    @Id val uuid: UUID,
    var name: String,
)
```

### Value Object

- **식별자 없음**, **불변**
- JPA `@Embeddable` 또는 Kotlin `value class`

```kotlin
@Embeddable
data class PasswordSetting(
    val minLength: Int,
    val requireUppercase: Boolean,
)

@JvmInline
value class UserName(val value: String)
```

### 구분 기준

| 질문 | Entity | Value Object |
|------|--------|--------------|
| 고유 식별자 필요? | ✅ UUID | ❌ 없음 |
| 독립적으로 조회/수정? | ✅ 가능 | ❌ 불가 |
| 다른 객체로 대체 가능? | ❌ 불가 | ✅ 동일 값이면 가능 |

---

## 네이밍 컨벤션

| 용어 | 규칙 | 이유 |
|------|------|------|
| OAuth | `Oauth` | `OAuth`, `oAuth`, `OAUTH` 혼재 방지 |

```kotlin
// ❌ 혼란
class OAuthService
class oAuthClient

// ✅ 통일
class OauthService
class OauthClient
```

---

## 로깅

### Logger 선언 위치 및 방식

```kotlin
// ❌ top-level + 문자열 이름
private val logger = LoggerFactory.getLogger("MyService")

// ✅ 클래스 멤버 + 클래스 참조
class MyService {
    private val logger = LoggerFactory.getLogger(javaClass)
}

// ✅ 싱글턴/유틸 클래스의 경우 companion object
object MyUtils {
    private val logger = LoggerFactory.getLogger(MyUtils::class.java)
}
```

| 규칙 | 이유 |
|------|------|
| **top-level 금지** | 클래스와 분리되어 관리 어려움 |
| **문자열 이름 금지** | 클래스명 변경 시 불일치 발생 |
| **클래스 참조 사용** | 리팩토링 안전, IDE 지원 |

### 로그 메시지 포맷

```kotlin
// ❌ 금지 - 문자열 먼저 생성됨
logger.info("msg=$msg, count=${list.size}")

// ✅ 권장 - SLF4J placeholder
logger.info("msg={}, count={}", msg, list.size)
```

**이유**: 로그 레벨 비활성화 시에도 문자열이 먼저 생성됨 (성능 낭비)

### 로그 레벨 가이드 ⭐⭐⭐

**원칙**: ERROR는 시스템 장애 시에만 사용. 불필요한 ERROR가 많으면 알람 피로(alert fatigue)로 실제 장애를 놓침.

| 레벨 | 사용 시점 | 예시 |
|------|----------|------|
| **ERROR** | 즉각 대응 필요한 시스템 장애 | DB 연결 실패, 필수 외부 API 장애, 데이터 정합성 깨짐 |
| **WARN** | 잠재적 문제, 모니터링 필요 | 재시도 성공, 성능 저하 감지, deprecated API 호출 |
| **INFO** | 정상적인 비즈니스 흐름 | 사용자 로그인, 주문 생성, 배치 작업 완료 |
| **DEBUG** | 개발/디버깅용 상세 정보 | 메서드 진입/종료, 변수 값, 쿼리 파라미터 |

### 흔한 실수

```kotlin
// ❌ 예상된 비즈니스 예외를 ERROR로 로깅 → INFO 사용
catch (e: UserNotFoundException) {
    logger.error("User not found: {}", email)
}

// ❌ 클라이언트 입력 오류를 ERROR로 로깅 → WARN 사용
if (!isValidRequest(request)) {
    logger.error("Invalid request: {}", request)
}

// ❌ 모든 예외를 ERROR로 로깅 → 예외 유형별 분류 필요
catch (e: Exception) {
    logger.error("Something went wrong", e)
}
```

### 올바른 사용

```kotlin
// ✅ 비즈니스 예외 → INFO
catch (e: UserNotFoundException) {
    logger.info("User not found: {}", email)
}

// ✅ 클라이언트 오류 → WARN
if (!isValidRequest(request)) {
    logger.warn("Invalid request from client: {}", request.userId)
}

// ✅ 시스템 장애 → ERROR
catch (e: DatabaseConnectionException) {
    logger.error("Database connection failed", e)
}

// ✅ 재시도 성공 → WARN
catch (e: TimeoutException) {
    retry()
    logger.warn("Request timeout, retried successfully: {}", requestId)
}
```

### 레벨 선택 기준

| 질문 | 레벨 |
|------|------|
| 즉시 대응 필요한 장애인가? | ERROR |
| 시스템 정상이나 주의 필요한가? | WARN |
| 정상적인 비즈니스 흐름인가? | INFO |
| 개발/디버깅용 정보인가? | DEBUG |

### 알람과의 관계

```
ERROR 로그 → 알람 발생 → 담당자 호출
         ↓
   불필요한 ERROR 다수
         ↓
   알람 피로 (alert fatigue)
         ↓
   실제 장애 놓침
```

---

## Kotlin 코드 스타일

> **기본 원칙**: [Kotlin 공식 스타일 가이드](https://kotlinlang.org/docs/coding-conventions.html), [Spring 공식 가이드](https://docs.spring.io/spring-framework/reference/) 준수
>
> 명확한 이유 없이 표준을 벗어나는 코드는 지양

### import 규칙

```kotlin
// ❌ 와일드카드 import 금지
import com.querypie.kac.domain.*
import java.util.*

// ✅ 실제 사용하는 클래스만 명시
import com.querypie.kac.domain.KubeCluster
import com.querypie.kac.domain.KubeClusterPolicy
import java.util.UUID
```

| 규칙 | 이유 |
|------|------|
| `.*` 금지 | 불필요한 클래스까지 import됨, 사용 클래스 파악 어려움 |
| 명시적 import | 코드 의존성 명확, IDE 자동 정리 용이 |

### 프로퍼티 기본값

직관적으로 예상 가능한 경우만 기본값 사용. 그 외에는 명시적 전달 또는 주석 추가.

```kotlin
// ❌ 예상하기 어려운 기본값
class Policy(
    val retryCount: Int = 3,        // 왜 3인지 알 수 없음
    val timeout: Duration = 30.seconds,
)

// ✅ 명시적으로 전달
class Policy(
    val retryCount: Int,
    val timeout: Duration,
)

// ✅ 일반적으로 예상 가능한 경우는 OK
class Entity(
    val createdAt: LocalDateTime = LocalDateTime.now(),
    val enabled: Boolean = true,    // 활성화가 기본인 게 자연스러움
)
```

### var vs val 적절히 사용
```kotlin
// ❌ 불필요한 var
class User(
    var uuid: UUID,  // UUID는 변경되면 안 됨
)

// ✅ 불변 필드는 val
class User(
    val uuid: UUID,
    var name: String,  // 변경 가능한 필드만 var
)
```

### 무지성 nullable 금지

```kotlin
// ❌ 이유 없이 nullable
class Config(
    val url: String?,      // null이 될 이유가 없으면 안 됨
    val timeout: Int?,
)

// ✅ 실제로 null이 의미 있는 경우만
class Config(
    val url: String,
    val description: String?,  // 설명은 없을 수 있음
    val expiryAt: LocalDateTime?,  // 만료일 없으면 무기한
)
```

### Not-null assertion 사용 자제

not-null assertion 사용 시 NPE 발생하며 원인 파악 어려움. 명시적 예외 처리 권장.

```kotlin
// ❌ 무지성 단언 - 그냥 NPE 발생, 원인 파악 어려움
val user = userRepository.findByUuid(uuid)!!

// ✅ 명시적 예외 처리 - 무슨 문제인지 바로 알 수 있음
val user = userRepository.findByUuid(uuid)
    ?: throw UserNotFoundException(uuid)

// ✅ 스마트 캐스팅이 필요한 경우는 OK
if (value != null) {
    process(value)  // 스마트 캐스팅됨
}
// 또는 컴파일러가 null 체크를 인식 못하는 경우
val result = someMap[key]!!  // 직전에 containsKey 체크한 경우
```
### 파일 내 클래스 순서

```kotlin
// ❌ 보조 클래스가 먼저
data class ResultDto(...)
class MainService(...)

// ✅ 메인 클래스 먼저, 보조 클래스는 하단에
class MainService(...)
data class ResultDto(...)
```

| 순서 | 내용 |
|------|------|
| 1 | 메인 클래스 (파일명과 일치) |
| 2 | 보조 클래스 / data class |

### 클래스 멤버 순서
클래스 내부의 멤버는 다음 순서로 정의한다:
**공용(public) → 보호(protected) → 비공개(private)** 순서로 작성하여 자연스러운 정보 노출 구조를 보장한다.

```kotlin
@Service
class MyService {
    // 1. Public properties
    val publicProperty: String = ""

    // 2. Public methods
    fun publicMethod() {
    }

    // 3. Private methods
    private fun privateMethod() {
    }

    // 4. Nested classes / Data classes
    data class Result(val value: String)

    // 5. Companion object (최하단)
    companion object {
        const val CONSTANT = "value"
    }
}
```

### 체크 포인트

| 항목 | 질문 |
|------|------|
| 기본값 | 이 기본값이 일반적으로 예상 가능한가? |
| var/val | 이 필드가 런타임에 변경되어야 하는가? |
| nullable | null이 비즈니스적으로 의미 있는 값인가? |
| not-null assertion | 스마트 캐스팅이 필요한 경우인가? 아니면 명시적 예외처리가 나은가? |

---

## 안티패턴 모음

### Spring Boot Auto-Config 빈 충돌 ⭐⭐⭐

Spring Boot는 `@ConditionalOnMissingBean`으로 auto-configuration을 결정한다. **동일 타입의 `@Bean`을 등록하면 auto-config이 비활성화**되어 전역 사이드이펙트가 발생한다.

```kotlin
// ❌ ObjectMapper 타입 @Bean 등록 → Spring Boot JacksonAutoConfiguration 비활성화
@Configuration
class MacYamlMapperConfig {
    @Bean("macYamlMapper")
    fun macYamlMapper(): ObjectMapper =  // ← 빈 이름과 무관하게 타입만으로 충돌
        ObjectMapper(YAMLFactory())       // JavaTimeModule, KotlinModule 없음
}
// 결과: ObjectMapper를 주입받는 모든 곳에서 Instant 직렬화 실패 등 장애 발생

// ✅ 해결 1: 사용처에서 직접 생성 (유일한 사용처인 경우)
@Component
class McpServerPolicyYamlParser {
    private val yamlMapper = ObjectMapper(YAMLFactory())
        .registerModule(KotlinModule.Builder().build())
}

// ✅ 해결 2: Jackson2ObjectMapperBuilderCustomizer 사용 (전역 커스터마이즈)
@Bean
fun jacksonCustomizer() = Jackson2ObjectMapperBuilderCustomizer { builder ->
    builder.modulesToInstall(MyCustomModule())
}
```

| 위험한 타입 | Auto-Config 클래스 | 비활성화 조건 |
|------------|-------------------|-------------|
| `ObjectMapper` | `JacksonAutoConfiguration` | `@ConditionalOnMissingBean(ObjectMapper.class)` |
| `DataSource` | `DataSourceAutoConfiguration` | `@ConditionalOnMissingBean(DataSource.class)` |
| `RestTemplate` | `RestTemplateAutoConfiguration` | `@ConditionalOnMissingBean(RestTemplateBuilder.class)` |
| `WebClient` | `WebClientAutoConfiguration` | `@ConditionalOnMissingBean(WebClient.Builder.class)` |

> 실제 사례: [PR #15584](https://github.com/chequer-io/querypie-mono/pull/15584) — `ObjectMapper` `@Bean` 등록으로 supervisor 헬스체크 전면 장애

### 메모리/리소스 과사용

| 코드 패턴 | 문제 | 해결 |
|-----------|------|------|
| `inputStream.readAllBytes()` | 크기 제한 없이 전체 메모리 로드 | 크기 검증 또는 스트리밍 처리 |
| `request.body.readAllBytes()` | 대용량 요청 시 OOM | Content-Length 검증 + 제한 |
| `.collect(Collectors.toList())` | 대량 데이터 전체 수집 | 페이징 또는 스트리밍 |
| `StringBuilder.append()` 루프 | 크기 제한 없이 계속 축적 시 OOM | 최대 크기 제한 추가 |
| `BufferedReader(InputStreamReader(...))` | `.use {}` 없이 사용 시 누수 | `use {}` 블록 사용 |
| `FileInputStream(...)` / `FileOutputStream(...)` | 닫지 않으면 FD 누수 | `use {}` 블록 사용 |

### @Transactional 안티패턴

| 코드 패턴 | 문제 | 해결 |
|-----------|------|------|
| 같은 클래스 내 `@Transactional` 메서드 호출 | Self-invocation: 프록시 우회 | 별도 Bean으로 분리 |
| `private fun` + `@Transactional` | 어노테이션 무시됨 | public으로 변경 |
| `@Transactional` 내 외부 API 호출 | DB 커넥션 점유 시간 증가 | 트랜잭션 밖에서 호출 |
| `catch (e: Exception)` 후 삼킴 | 롤백 안 됨 | rethrow 또는 `rollbackFor` |
| checked exception 발생 | 기본적으로 롤백 안 됨 | `rollbackFor = [Exception::class]` |

### Kotlin 코루틴 안티패턴

| 코드 패턴 | 문제 | 해결 |
|-----------|------|------|
| `GlobalScope.launch` | 생명주기 무시, 메모리 누수 | structured concurrency 사용 |
| `runBlocking` in production | 스레드 블로킹, 데드락 위험 | `launch` 또는 `async` 사용 |
| 코루틴 내 `while(true)` 취소 미확인 | 취소 불가능 | `ensureActive()` 또는 `isActive` 체크 |

### Destructuring 파싱 안티패턴

```kotlin
// ❌ split 결과 검증 없이 destructuring
val (host, port) = config.endpoint.split(":")  // "host:port:extra" → IndexOutOfBoundsException

// ✅ split 결과 검증 후 사용
val parts = config.endpoint.split(":")
if (parts.size != 2) {
    logger.warn("Invalid endpoint format: {}", config.endpoint)
    return null
}
val host = parts[0]
val port = parts[1].toIntOrNull() ?: return null
```
```

### NotImplementedError 안티패턴

```kotlin
// ❌ 런타임에 NotImplementedError throw - 서비스 크래시 유발
fun exportToExcel(data: List<Item>): ByteArray {
    throw NotImplementedError("Excel export not implemented yet")
}

// ✅ 로그만 남기고 graceful 처리
fun exportToExcel(data: List<Item>): ByteArray? {
    logger.warn("Excel export is not implemented yet")
    return null
}

// ✅ 또는 명시적으로 지원하지 않음을 반환
sealed class ExportResult {
    data class Success(val data: ByteArray) : ExportResult()
    data class NotSupported(val message: String) : ExportResult()
}
```
