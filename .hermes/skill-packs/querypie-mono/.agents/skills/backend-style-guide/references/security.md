# Security & Infrastructure

## HA(High Availability) 환경 고려 ⭐⭐⭐

**원칙**: 서버가 여러 대 실행되는 환경 가정. Stateless 설계 필수.

### Redis 분산 락 TTL 패턴

```kotlin
// ❌ 고정 TTL - 실제 작업 시간보다 짧으면 중복 실행 발생
redisLockProvider.withLock(name = lockKey, ttlSeconds = 30) {
    // 실제 작업이 30초 이상 걸리면 락 만료 → 다른 인스턴스가 동일 작업 시작
    longRunningTask()
}

// ✅ 동적 TTL - 예상 작업 시간 + 여유분
val estimatedSeconds = config.timeoutSeconds + BUFFER_SECONDS + 10  // 여유 확보
redisLockProvider.withLock(name = lockKey, ttlSeconds = estimatedSeconds) {
    longRunningTask()
}
```

### Redis 캐시 즉시 삭제 패턴

```kotlin
// ❌ TTL 만료 대기 - 불필요한 메모리 점유
redisTemplate.opsForValue().set(resultKey, result, 5, TimeUnit.MINUTES)
// ... 사용 완료 후 삭제 안 함 → 5분간 메모리 점유

// ✅ 사용 완료 후 즉시 삭제
try {
    val result = redisTemplate.opsForValue().get(resultKey)
    // 처리 로직
} finally {
    redisTemplate.delete(resultKey)  // 즉시 삭제
}
```

| 항목 | 금지 | 권장 |
|------|------|------|
| 세션/상태 | 로컬 메모리 저장 | Redis 등 공유 저장소 |
| 파일 저장 | 로컬 파일시스템 | S3, 공유 스토리지 |
| 스케줄러/배치 | 단순 실행 | 분산 락으로 중복 실행 방지 |
| 캐시 | 로컬 캐시만 | Redis 등 분산 캐시 |

```kotlin
// ❌ 로컬 메모리에 상태 저장 - 다른 서버와 공유 안 됨
class SomeService {
    private val cache = mutableMapOf<String, Any>()
}

// ✅ Redis 등 공유 저장소 사용
class SomeService(
    private val redisTemplate: RedisTemplate<String, String>
)
```

---

## SecurityContext + ThreadLocal 주의 ⭐⭐⭐

### 현재 구조

- Spring Security의 SecurityContext **사용 안 함**
- **자체 SecurityContext 구현** (이름은 동일)
- **ThreadLocal 기반** - 요청 스레드에 사용자 정보 저장
- **WebMVC** 사용 (동기, Thread per Request)

### Filter Chain 구조 (전부 ThreadLocal 의존)

```
ExceptionHandlerFilter
    ↓
TraceLogFilter
    ↓
AuthenticationFilter ──► SecurityContextHolder.context = ... (ThreadLocal에 SET)
    ↓
ActivityLogFilter ──► securityContextHolder.context (ThreadLocal에서 GET)
    ↓
Controller
```

### 핵심 코드

```kotlin
@Component
class ThreadLocalSecurityContextHolder : SecurityContextHolder, SessionUserProvider {
    private val threadLocal = ThreadLocal<SecurityContext>()  // 👈 핵심!

    override var context: SecurityContext
        get() = contextOrNull ?: throw IllegalStateException("SecurityContext is null")
        set(context) { threadLocal.set(context) }
}
```

### 비동기 패턴 주의

| 패턴 | 왜 주의 |
|------|----------|
| WebFlux (Mono, Flux) | ThreadLocal 유실 |
| Reactive Streams | ThreadLocal 유실 |
| Kotlin Coroutines | ThreadLocal 유실 |
| @Async | ThreadLocal 유실 |
| CompletableFuture | ThreadLocal 유실 |

### 왜 문제인가?

```
Thread-1 (요청 스레드)
    ↓
SecurityContext 설정 (ThreadLocal)
    ↓
비동기 전환 (suspend, Mono, @Async 등)
    ↓
Thread-2 (다른 스레드)
    ↓
SecurityContext = null 💀
ActivityLog = null 💀
```

### 우리 상황

1. **DB가 JPA/JDBC** → blocking → 비동기 효용 없음
2. **ThreadLocal 의존** → SecurityContext, ActivityLog 깨짐
3. **Spring Boot가 알아서 WebMVC 선택** → 그냥 놔두면 됨

> 비동기 쓰고 싶으면 R2DBC + SecurityContext 재설계 필요 = 전체 리팩토링

### 왜 자체 SecurityContext를 만들었나?

HTTP Filter와 gRPC Interceptor 모두 지원하기 위해!

- HTTP: `AuthenticationFilter`에서 ThreadLocal에 SET
- gRPC: `GrpcAuthenticationInterceptor`에서 ThreadLocal에 SET

### 참조 파일

| 역할 | 파일 |
|------|------|
| SecurityContext | `iam/.../SecurityContext.kt` |
| ThreadLocal 구현 | `iam/.../ThreadLocalSecurityContextHolder.kt` |
| HTTP Filter | `app/.../ApiSecurityConfiguration.kt` |
| gRPC Interceptor | `app/.../GrpcAuthenticationInterceptor.kt` |

---

## Critical 코드 예시 🚨

### ThreadLocal + 비동기 = 컨텍스트 유실

```kotlin
// ❌ ThreadLocal + Flux = 컨텍스트 유실
Flux.create { sink -> ... }
    .doOnSubscribe { securityContext.get() }  // 다른 스레드에서 null!

// ❌ @Async + ThreadLocal
@Async
fun processAsync() {
    val user = securityContext.get()  // null!
}
```

### 타임아웃 미설정 = 무한 대기

```kotlin
// ❌ 타임아웃 없음 = 무한 대기 가능
val response = webClient.get().retrieve().bodyToMono()

// ✅ 타임아웃 설정
val response = webClient.get()
    .retrieve()
    .bodyToMono()
    .timeout(Duration.ofSeconds(30))
```

### 트랜잭션 내 외부 API = 커넥션 점유

```kotlin
// ❌ 트랜잭션 내 외부 API = DB 커넥션 점유 시간 증가
@Transactional
fun process() {
    save(entity)
    externalApi.call()  // 외부 API 응답 대기 동안 커넥션 점유
}

// ✅ 트랜잭션 분리
fun process() {
    saveEntity()  // @Transactional
    externalApi.call()  // 트랜잭션 밖
}
```

### Fail-Open 보안 (에러 시 원본 노출)

```kotlin
// ❌ Fail-Open: 에러 발생 시 필터링 안 된 원본 반환
fun filter(content: String): String {
    return try {
        doFilter(content)
    } catch (e: Exception) {
        content  // 💀 원본 그대로 노출!
    }
}

// ✅ Fail-Closed: 에러 시 안전한 기본값 또는 예외
fun filter(content: String): String {
    return try {
        doFilter(content)
    } catch (e: Exception) {
        logger.error("Filter failed", e)
        throw FilterException("필터링 실패", e)
    }
}
```

---

## WebClient/RestClient 리소스 누수 주의 ⭐⭐⭐

### 문제

WebClient/RestClient를 매번 새로 생성하면:
- **PooledConnectionProvider의 channelPools 계속 증가**
- **메모리 누수**
- **커넥션 고갈**

실제 코드베이스 주석:
```kotlin
// NOTE: sslContext를 WebClient 생성시에 계속 생성하면
// PooledConnectionProvider의 channelPools가 계속 증가하게 되어
// 메모리 누수가 발생할 수 있음
```

### ❌ 나쁜 패턴 - 매번 새로 생성

```kotlin
class SomeService {
    fun doSomething() {
        val client = WebClient.builder().build()  // 💀 매번 새로 생성
        client.get()...
    }
}
```

### ✅ 좋은 패턴 - Bean으로 재사용

```kotlin
@Configuration
class ApiConfiguration {
    @Bean
    fun restClient(): RestClient = RestClient.builder().build()

    @Bean
    fun webClient(): WebClient = WebClient.builder().build()
}

@Service
class SomeService(
    private val restClient: RestClient,  // 주입받음
) {
    fun doSomething() {
        restClient.get()...  // 재사용
    }
}
```

### ⚠️ 특수한 경우 (SSL/프록시 설정이 다를 때)

```kotlin
@Bean
@Qualifier("proxyWebClient")
fun proxyWebClient(httpProxySetting: HttpProxySetting): WebClient {
    val httpClient = HttpClient.create()
        .proxy { it.type(ProxyProvider.Proxy.HTTP).host(httpProxySetting.host) }
    return WebClient.builder()
        .clientConnector(ReactorClientHttpConnector(httpClient))
        .build()
}
```

### 규칙

1. **기본은 Bean으로 한 번만 생성** → DI로 재사용
2. **특수 설정 필요 시** → `@Qualifier`로 별도 Bean
3. **매번 새로 생성 금지** → 리소스 누수 원인

### 🚨 현재 문제 있는 파일들 (리팩토링 필요)

| 파일 | 문제점 |
|------|--------|
| `app/.../SplunkHecSender.kt:144` | `createWebClient()` 매번 새로 생성 |
| `app/.../AzureClient.kt:175` | 매번 새로 생성 |
| `app/.../CloudSyncAzureClientService.kt:20` | 매번 새로 생성 |
| `app/.../EventSubscriptionSender.kt:15` | 필드 초기화 (Bean 아님) |
| `kac/.../KubeProxyAdapter.kt:17` | 필드 초기화 (Bean 아님) |

---

## 민감정보 로깅 금지 ⭐⭐⭐

### 절대 로그에 남기면 안 되는 것

| 항목 | 예시 |
|------|------|
| **인증 정보** | 비밀번호, API Key, Access Token, Secret Key |
| **개인정보** | 주민번호, 카드번호, 계좌번호 |
| **암호화 키** | KEK, DEK, Private Key |
| **세션 정보** | Session ID, JWT 전체 |

### ❌ 나쁜 패턴

```kotlin
// 💀 비밀번호 로깅
logger.info("Login attempt: user={}, password={}", username, password)

// 💀 토큰 로깅
logger.debug("API call with token: {}", accessToken)

// 💀 전체 요청 로깅 (민감정보 포함 가능)
logger.info("Request body: {}", request)
```

### ✅ 좋은 패턴

```kotlin
// ✅ 민감정보 제외
logger.info("Login attempt: user={}", username)

// ✅ 마스킹 처리
logger.debug("API call with token: {}...{}", token.take(4), token.takeLast(4))

// ✅ 필요한 필드만 선택적 로깅
logger.info("Request: action={}, userId={}", request.action, request.userId)
```

### 예외 로깅 주의

```kotlin
// 💀 스택 트레이스에 민감정보 포함 가능
try {
    authenticate(password)
} catch (e: Exception) {
    logger.error("Auth failed", e)  // e.message에 password 포함될 수 있음
}

// ✅ 안전한 예외 로깅
catch (e: Exception) {
    logger.error("Auth failed for user: {}", username)
}
```

### 로그 레벨별 주의

| 레벨 | 프로덕션 노출 | 주의 |
|------|-------------|------|
| ERROR | ✅ | 민감정보 절대 금지 |
| WARN | ✅ | 민감정보 절대 금지 |
| INFO | ✅ | 민감정보 절대 금지 |
| DEBUG | 설정에 따라 | 주의 필요 |
| TRACE | 설정에 따라 | 주의 필요 |

---

## KEK/DEK 암호화 (AESConverter)

### 구조

```
KEK (Key Encryption Key)
  ↓ 환경변수에서 로드
DEK (Data Encryption Key)
  ↓ DB에 저장 (KEK로 암호화됨)
AESConverter
  ↓ Entity 필드 암호화/복호화
```

### 암호화 대상 (필수)

- 토큰 (access token, refresh token)
- 비밀번호
- 인증서/키
- API 시크릿

### 사용법

```kotlin
@Entity
class SomeEntity {
    @Convert(converter = AESConverter::class)
    @Column(name = "secret_key")
    var secretKey: String  // 자동 암호화/복호화
}
```

### 참조 파일

- `iam/.../AESConverter.kt`
- `common/.../DekProviderInitializer.kt`

---

## API 프로토콜

### Front ↔ Back 통신

- **정석: OAS(OpenAPI Spec) 기반 REST**
- OAS 스펙 위치: `libs/oas/specs/api/`
- Front에서 OAS 기반 클라이언트 자동 생성
- **포맷 검증**: `libs/oas`에 검증 도구 있음

### gRPC

- **레거시** - 특수한 경우 아니면 사용 안 함
- 새로운 API는 REST로 작성

---

## 예외 처리

- **애매한 상황** - Advice와 Error handling filter 혼재
- 일관된 패턴 정립 필요
