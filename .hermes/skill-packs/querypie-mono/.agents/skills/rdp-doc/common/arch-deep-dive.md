# RDP 아키텍처 Deep Dive

이 문서는 RDP 접근제어 시스템의 **상세 동작 원리**를 설명합니다. 개념 이해를 위한 다이어그램, 코드 레벨 구현, 시퀀스 흐름 등 심층적인 내용을 다룹니다.

간소화된 아키텍처 개요는 [ARCHITECTURE.md](./ARCHITECTURE.md), 용어 정의는 [GLOSSARY.md](./GLOSSARY.md)를 참조하세요.

---

## 1. Heartbeat 동작 원리

### 1.1 Heartbeat vs Heartbeat Scan

Server Agent의 상태 확인은 **두 가지 방향**의 통신으로 이루어집니다.

**Heartbeat (Server Agent → API)**:
```
Server Agent ──(PUT /api/server-agent/heart-beat)──→ API
```

- Server Agent가 **1분마다** API로 상태 전송
- **아웃바운드** 통신 (Server Agent가 API 호출)
- 포함 정보: AgentId, AgentUuid, Status, Version, OS, IP 등

**Heartbeat Scan (API → Server Agent)**:
```
API ──(GET /api/health)──→ Server Agent
     (모든 Windows 서버 대상)
```

- API가 **모든 Windows 서버를 스캔**하여 상태 확인
- **인바운드** 통신 (API가 Server Agent 호출)
- 용도:
  - 아웃바운드 통신이 안 되는 환경에서 Server Agent 발견
  - Activate 대상 확인
  - 상태 동기화

### 1.2 왜 두 가지가 필요한가?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 시나리오 1: 정상 환경 (Heartbeat 사용)                                        │
│                                                                              │
│  Server Agent ──────(아웃바운드 OK)──────→ API                               │
│       │                                     │                                │
│       └──── Heartbeat로 1분마다 상태 전송 ───┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 시나리오 2: 아웃바운드 차단 환경 (Heartbeat Scan 필요)                         │
│                                                                              │
│  Server Agent ──X── (아웃바운드 차단) ──X──→ API                              │
│       │                                      │                               │
│       │                                      │                               │
│       └←──── Heartbeat Scan으로 인바운드 확인 ┘                               │
│              (Gateway/Nova 경유 가능)                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Bootstrap 문제 (닭과 달걀)

**API 인바운드가 제한된 환경**에서 신규 Server Agent를 발견하는 데 Heartbeat Scan이 필수입니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 문제 상황: Gateway 연결 전 신규 Server Agent 발견                              │
│                                                                              │
│  1. Server Agent 설치됨                                                      │
│  2. Server Agent → API로 Heartbeat 보내려 함                                 │
│  3. API 인바운드 차단 (Server Agent 관점에서 아웃바운드 불가)                   │
│  4. Heartbeat 실패                                                           │
│  5. API는 이 Server Agent 존재를 모름                                        │
│  6. Gateway proxy-jumps에 이 서버가 포함 안 됨                               │
│  7. Gateway 연결도 안 됨                                                     │
│  8. → Deadlock!                                                              │
│                                                                              │
│  Server Agent가 Gateway를 쓰려면 API가 먼저 알아야 하는데,                     │
│  API에 알리려면 Gateway가 필요한 상황                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Heartbeat Scan이 이 Deadlock을 해결합니다:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 해결: Heartbeat Scan으로 Bootstrap                                           │
│                                                                              │
│  1. API ──(Heartbeat Scan)──→ Server Agent 발견                             │
│  2. API가 Server Agent 등록                                                  │
│  3. Gateway proxy-jumps에 포함                                               │
│  4. Gateway → Server Agent 연결 수립                                         │
│  5. 이후 Server Agent → Gateway → API로 Heartbeat 정상 동작                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 정상 운영 시 Heartbeat Scan은 중복인가?

Gateway 연결이 수립된 후에는 **기술적으로 Heartbeat Scan이 중복**입니다.

| 시점 | Heartbeat | Heartbeat Scan | 필요? |
|------|-----------|----------------|-------|
| **Bootstrap** (신규 발견) | ✗ (Gateway 없음) | ✓ | **Scan 필수** |
| **정상 운영** (Gateway 연결됨) | ✓ (Gateway 경유) | ✓ | 기술적 중복 |
| **Gateway 장애** | ✗ | ✓ | 진단용으로 유용 |

**그럼에도 Heartbeat Scan을 유지하는 이유:**

1. **장애 원인 구분**: Heartbeat가 안 오는 게 Server Agent 문제인지, Gateway 문제인지 직접 확인 가능
2. **같은 환경에 신규 Server Agent 추가 시**: 또 Bootstrap 문제 발생, 주기적 Scan으로 자동 발견
3. **구현 단순화**: "이 서버는 Scan, 저 서버는 안 함" 로직보다 일괄 Scan이 단순

**결론**: 정상 운영 시 중복이지만, **단순함을 위한 트레이드오프**로 유지합니다.

### 1.5 반대로, Heartbeat를 제거하고 Scan만 남기면?

Heartbeat Scan이 중복이라는 관점과 **반대로**, Heartbeat가 불필요한 것 아닌가?라는 관점도 있습니다.

**Heartbeat 방식의 문제점 (엔터프라이즈 현장 경험 기반):**

| 문제 | 설명 |
|------|------|
| **API 인바운드 화이트리스트 관리** | Server Agent IP를 전부 등록해야 함, Windows 서버가 수시로 추가/제거되면 관리 부담 |
| **API 서버 부하** | 수천 대의 Server Agent가 1분마다 API에 TCP/TLS 핸드셰이크 |
| **동적 IP 환경** | Server Agent IP가 바뀌면 화이트리스트 갱신 필요 |

**Scan만 남기면?**

```
현재:  Server Agent ──(1분마다 Heartbeat)──→ API  (수천 대가 API로 연결)
대안:  API ──(Scan)──→ Server Agent  (API가 필요할 때 연결)
```

| 항목 | Heartbeat 방식 | Scan Only 방식 |
|------|---------------|----------------|
| API 인바운드 화이트리스트 | Server Agent IP 전부 등록 | **불필요** |
| API 서버 부하 | 수천 대 동시 연결 | **API가 제어** |
| 실시간성 | 1분 주기 | Scan 주기에 의존 |

**하지만 완전한 해결은 아님:**

Heartbeat를 제거해도 **RDP 세션 중 트래픽은 여전히 Server Agent → API 방향**:
- 이벤트 로그 (키 입력, 마우스, 프로세스)
- 커맨드 오딧
- Connected/Disconnected

**결론: RequireGatewayTunnel=true가 더 나은 해결책**

Heartbeat를 제거하는 대신, **Gateway 경유로 해결하는 것이 현재 아키텍처의 방향**:

```
문제: Server Agent → API 직접 연결 시 화이트리스트 관리 부담
해결: HubUrl=localhost 설정 → RequireGatewayTunnel=true
      → 모든 트래픽이 Gateway 경유
      → API 화이트리스트에 Gateway IP만 등록
```

이 방식은:
- Heartbeat/이벤트 로그 모두 Gateway 경유
- API 인바운드 화이트리스트 단순화
- 기존 아키텍처 유지하면서 문제 해결

상세 설정은 [섹션 2.6 API 인바운드 제한 환경 설정 가이드](#26-api-인바운드-제한-환경-설정-가이드)를 참조하세요.

### 1.6 Heartbeat Scan Job 로직

**위치**: `apps/api/.../ServerAgentHeartbeatScanJob.kt`

```kotlin
// 1. 모든 Windows 서버 조회
val windowsServers = serverRepository.findAllByOsTypeWithTags(ServerOsType.WINDOWS)

// 2. 병렬로 각 서버에 GET /api/health 요청
windowsServers.forEach { server ->
    executor.submit {
        val response = serverAgentClient.sendHeartbeat(
            host = server.host,
            port = server.rdpPort,
            serverUuid = server.uuid,
            ...
        )
        // 3. 응답 처리
        serverAgentApplicationService.heartbeatScanReceived(...)
    }
}

// 4. 링크되지 않은 Server Agent도 스캔
unlinkedServerAgents.forEach { ... }
```

---

## 2. Gateway 동작 원리

### 2.1 API 응답 생성 로직

Gateway가 `proxy-jumps` API를 호출하면 API는 다음 로직으로 응답을 생성합니다:

**API 응답 생성 로직** (apps/api):
```
1. 모든 Windows 서버 필터링 (osType == WINDOWS)
2. 각 서버의 서버 그룹에서 NORMAL 상태의 ProxyJump 조회
3. 동일한 JumpHost 체인(hash)을 가진 서버들을 그룹화
4. 각 그룹별로 JumpHosts + Servers 응답 생성
```

**Gateway의 응답 처리**:
| 상황 | Gateway 동작 |
|------|-------------|
| **JumpHosts 있음** | `GatewayWorker` 생성 → `SharedJumpHostTunnel`로 SSH 다중 홉 연결 |
| **JumpHosts 없음** | Direct 연결 (점프 호스트 없이 직접 연결) |
| **JumpHosts 동일** | 같은 `GatewayWorker`가 터널 재사용 |
| **서버 추가** | 기존 Worker에 `ClientSession` 추가 |
| **서버 제거** | `ClientSession` 정리 (터널은 유지) |

**JumpHost 체인 비교 기준**:
- host, port
- auth.username, auth.password, auth.sshPrivateKey, auth.sshPassphrase, auth.authType
- 모든 값이 동일해야 같은 체인으로 인식 → 터널 재사용

### 2.2 Direct Tunnel 지원

Gateway는 점프 호스트 없이 **Direct Tunnel**도 지원합니다:

```csharp
// GatewayConnector.cs
if (_tunnel is not null)
{
    // JumpHost를 통한 연결
    transport = await _tunnel.ConnectAsync(server.Host, server.Port, cts.Token);
}
else
{
    // Direct TCP 연결 (점프호스트 없음)
    transport = await ConnectDirectAsync(server.Host, server.Port, ...);
}
```

**Direct 연결 방식**:
1. **Direct TCP**: 방화벽이 열린 환경에서 직접 TCP 연결
2. **Nova Proxy 경유 Direct**: Nova 프록시를 통한 제어된 Direct 연결

### 2.3 다중 SSH 점프 호스트 터널링 상세

```
설정: JumpHosts = [ssh1.com, ssh2.com, ssh3.com]
목표: api.internal:8080 (프라이빗 네트워크)

1. Local → ssh1.com:22
   (직접 SSH 연결)

2. ssh1.com → Local:12345 ↔ ssh2.com:22
   (ssh1에서 포트 포워딩)

3. ssh2.com → ssh1:LocalPort ↔ ssh3.com:22
   (ssh2는 ssh1을 통해 ssh3에 접근)

4. ssh3.com → Dynamic SOCKS
   (ssh3에서 SOCKS 프록시: 127.0.0.1:54321)

5. Local → SOCKS(127.0.0.1:54321) → ssh3 → api.internal:8080
   (최종적으로 3개 SSH 호스트를 통과)
```

### 2.4 Gateway Protocol 상세

Gateway ↔ Server Agent 간 사용되는 프로토콜:

**ConversationID 기반 요청-응답 매칭**:
```
1. WinSAC이 RelayRequest 전송
   Message(ConversationID=1, RelayRequest(host, port))

2. RequestProcessor._requestSenders[1] = 대기 컨텍스트

3. Gateway가 같은 ConversationID로 응답
   Message(ConversationID=1, RelayResponse(connectionId))

4. 대기 중인 SendRequestAsync<>가 깨어남
   → RelayResponse 반환
```

### 2.5 RequireGatewayTunnel 동작 원리

Server Agent의 `HubUrl` 설정이 `localhost` 또는 `127.0.0.1`을 포함하면 **Gateway를 필수로 사용**하도록 강제됩니다.

**설정 위치**: `apps/winsac/Agent/WinSAC.Agent.Service/Config/ServerAgentConfig.cs`

```csharp
public static string HubUrl => GetString();
public static bool RequireGatewayTunnel =>
    HubUrl.Contains("localhost") || HubUrl.Contains("127.0.0.1");
```

**동작 원리**:
```
HubUrl = "http://localhost:xxxx"
           ↓
RequireGatewayTunnel = true
           ↓
Heartbeat에 RequireGatewayTunnel=true 포함
           ↓
API 요청 시 RelayChannelFactory 우선 사용
           ↓
Gateway를 통한 Relay 연결 (Direct TCP 대신)
```

| 상황 | HubUrl | RequireGatewayTunnel | 동작 |
|------|--------|---------------------|------|
| 프로덕션 (직접 연결) | `https://api.querypie.com` | `false` | TCP 직접 연결 |
| **API 인바운드 제한** | `http://localhost:xxxx` | `true` | **Gateway Relay 강제** |

**핵심: "localhost"가 Server Agent의 localhost가 아닌 이유**

이 설계의 핵심은 **네트워크 터널링 특성**을 활용한 것입니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Gateway 터널이 없을 때                                                        │
│                                                                              │
│  Server Agent의 http://localhost 요청                                        │
│       ↓                                                                      │
│  Server Agent가 설치된 Windows Server의 localhost                            │
│       ↓                                                                      │
│  아무것도 없음 (이 포트를 수신하는 서비스 없음)                                 │
│       ↓                                                                      │
│  연결 실패 ✗                                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Gateway 터널이 있을 때                                                        │
│                                                                              │
│  Server Agent의 http://localhost 요청                                        │
│       ↓                                                                      │
│  Gateway Relay Channel을 통해 터널링                                         │
│       ↓                                                                      │
│  Gateway 호스트의 localhost (= API 서버가 배포된 호스트)                      │
│       ↓                                                                      │
│  API 서버 응답 ✓                                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Gateway는 API 서버와 같은 호스트에 배포**되므로:
- Server Agent의 `http://localhost` 요청이
- Gateway 터널을 통해
- **API 서버 호스트의 localhost**로 도달

따라서 URL에 "localhost"가 포함되어 있으면:
1. Server Agent 자체의 localhost로는 의미 없음 (받아줄 서비스 없음)
2. **Gateway 터널이 있어야만 의미 있음**
3. → `RequireGatewayTunnel=true`가 **물리적으로 필수**

**이것이 URL 문자열로 RequireGatewayTunnel을 판단하는 이유입니다.**

> **설계 노트**: 명시적인 `/RequireGatewayTunnel=true` 옵션이 더 명확할 수 있으나, 현재 설계는 "localhost URL이면 Gateway 없이는 동작 불가"라는 물리적 제약을 코드에 반영한 것입니다. 향후 설치 마법사 개선 시 명시적 옵션 추가를 고려할 수 있습니다.

### 2.6 API 인바운드 제한 환경 설정 가이드

**엔터프라이즈 환경의 일반적인 요구사항:**
- API 서버 인바운드를 엄격한 화이트리스트로 관리
- Windows 서버가 수시로 추가/제거되어 화이트리스트 관리 부담
- Server Agent IP를 일일이 등록하기 어려움

**해결책: HubUrl을 localhost로 설정하여 모든 트래픽을 Gateway 경유**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 기존 방식 (직접 연결)                                                         │
│                                                                              │
│  Server Agent 1 ──→ API   (화이트리스트에 IP 등록 필요)                       │
│  Server Agent 2 ──→ API   (화이트리스트에 IP 등록 필요)                       │
│  Server Agent 3 ──→ API   (화이트리스트에 IP 등록 필요)                       │
│  ...                                                                         │
│  Server Agent N ──→ API   (N개의 IP 관리 필요!)                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Gateway 경유 방식 (RequireGatewayTunnel=true)                                │
│                                                                              │
│  Server Agent 1 ──┐                                                          │
│  Server Agent 2 ──┼──→ Gateway ──→ API  (Gateway IP만 화이트리스트!)         │
│  Server Agent 3 ──┤                                                          │
│  ...              │                                                          │
│  Server Agent N ──┘                                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**설정 방법:**

Server Agent 설치 시 HubUrl을 localhost로 지정:

```powershell
# 설치 명령 예시
QueryPie_Server_Access_Control_Setup.exe /Url=https://querypie.example.com /HubUrl=http://localhost /Port=13389 /VERYSILENT
```

> 설치 옵션 상세는 [SERVER-AGENT.md 섹션 8. 설치 옵션](SERVER-AGENT.md#8-설치-옵션)을 참조하세요.

**장점:**
1. **화이트리스트 단순화**: API 인바운드에 Gateway IP만 등록하면 됨
2. **동적 IP 환경 대응**: Server Agent IP가 바뀌어도 화이트리스트 변경 불필요
3. **API 서버 부하 분산**: 수많은 Server Agent가 직접 연결하는 대신 Gateway가 연결 집중점 역할
4. **보안 강화**: API 서버 노출 최소화

**주의사항:**
- Gateway가 정상 동작해야 모든 통신 가능
- Gateway 장애 시 Server Agent → API 통신 불가
- 초기 Bootstrap은 Heartbeat Scan으로 수행 (섹션 1.3 참조)

---

## 3. Server Agent 측 Gateway 처리

### 3.1 GatewayService 구조

**위치**: `apps/winsac/Agent/WinSAC.Agent.Service/Services/QueryPie/Gateway/GatewayService.cs`

```csharp
public sealed class GatewayService : BackgroundService, IRelayChannelFactory
{
    private readonly ControlChannelPool _controlChannelPool = new();
    private readonly ConcurrentDictionary<Guid, RelayChannel> _pendingRelayChannels = new();

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // TLS Router에 qpgateway ALPN 리스너 등록
        var listener = tlsRouter.CreateListener(GatewaySsl.ApplicationProtocol);

        while (!stoppingToken.IsCancellationRequested)
        {
            var connection = await listener.AcceptAsync(stoppingToken);
            _ = HandleClientAsync(connection, stoppingToken);
        }
    }
}
```

**주요 컴포넌트**:

| 컴포넌트 | 역할 |
|---------|------|
| `ControlChannelPool` | Control Channel 풀 관리 (Round-Robin 선택) |
| `_pendingRelayChannels` | 대기 중인 Relay Channel (5초 타임아웃) |
| `IRelayChannelFactory` | HTTP 클라이언트가 Gateway를 통해 연결할 때 사용하는 인터페이스 |

### 3.2 Control Channel vs Relay Channel 처리

Gateway 연결 수신 후 **Connection Type**에 따라 분기합니다:

```csharp
private async Task HandleClientAsync(TlsConnection connection, CancellationToken cancellationToken)
{
    var gwConnection = await HandshakeGatewayConnectionAsync(connection, cancellationToken);

    if (gwConnection.Data.Type is ConnectionType.Control)
    {
        // Control Channel: 풀에 추가하고 장기 유지
        await HandleControlChannelAsync(gwConnection, cancellationToken);
    }
    else
    {
        // Relay Channel: 5초 내 소비되어야 함
        await HandleRelayChannelAsync(gwConnection, cancellationToken);
    }
}
```

**Control Channel 처리**:
```csharp
private async Task HandleControlChannelAsync(GatewayConnection connection, CancellationToken cancellationToken)
{
    var controlChannel = new ControlChannel(connection, new ControlChannelServerHandler());
    _controlChannelPool.Add(controlChannel);  // 풀에 추가

    try
    {
        await controlChannel.RunAsync(cancellationToken);  // 종료까지 유지
    }
    finally
    {
        _controlChannelPool.Remove(controlChannel);  // 종료 시 풀에서 제거
    }
}
```

**Relay Channel 처리 (5초 타임아웃)**:
```csharp
private async ValueTask<bool> HandleRelayChannelAsync(GatewayConnection connection, CancellationToken cancellationToken)
{
    var relayChannel = new RelayChannel(connection);

    // 대기 목록에 추가
    _pendingRelayChannels[relayChannel.Id] = relayChannel;

    // 5초 대기
    await Task.Delay(TimeSpan.FromSeconds(5), cancellationToken);

    // 5초 내 소비되었으면 true (목록에서 이미 제거됨)
    // 5초 내 소비 안 됐으면 false (목록에서 직접 제거)
    return !_pendingRelayChannels.TryRemove(relayChannel.Id, out _);
}
```

### 3.3 Relay Channel 매칭 흐름

Server Agent가 API 요청을 보낼 때 Gateway를 통해 연결하는 전체 흐름:

```
Server Agent                                    Gateway                                     API
    |                                              |                                          |
    | -- 1. RelayRequest via Control Channel ----> |                                          |
    |      (host="api.querypie.io", port=443)      |                                          |
    |                                              | <========= 2. TCP handshake ==========>  |
    |                                              |                                          |
    | <-- 3. RelayResponse + channelId ----------- |                                          |
    |                                              |                                          |
    |                                              | --- 4. New TLS connection (Relay) --->   |
    |                                              |      (ConnectionType.Relay, channelId)   |
    |                                              |                                          |
    | <--- 5. TLS Router: qpgateway ALPN 수신 ---- |                                          |
    |       GatewayService.HandleRelayChannelAsync |                                          |
    |       _pendingRelayChannels[channelId] = ch  |                                          |
    |                                              |                                          |
    | -- 6. ConnectAsync에서 channelId로 매칭 ---> |                                          |
    |       _pendingRelayChannels.TryRemove(id)    |                                          |
    |                                              |                                          |
    | <======================== 7. HTTP Request/Response ===============================>    |
```

### 3.4 IRelayChannelFactory 구현

GatewayService는 `IRelayChannelFactory` 인터페이스를 구현하여 HTTP 클라이언트가 Gateway를 통해 연결할 수 있게 합니다:

```csharp
public interface IRelayChannelFactory
{
    bool CanConnect();  // Control Channel 연결 여부
    ValueTask<Result<RelayChannel>> ConnectAsync(DnsEndPoint endPoint, CancellationToken cancellationToken);
}
```

**ConnectAsync 구현**:
```csharp
public async ValueTask<Result<RelayChannel>> ConnectAsync(DnsEndPoint endPoint, CancellationToken cancellationToken)
{
    // 1. Control Channel 풀에서 하나 선택 (Round-Robin)
    if (!_controlChannelPool.TryNext(out var channel))
        return new ControlChannelNotConnectedException();

    // 2. Control Channel을 통해 Relay 요청
    var channelId = await channel.OpenRelayChannelAsync(endPoint.Host, (ushort)endPoint.Port, cancellationToken);

    // 3. 대기 목록에서 해당 Relay Channel 찾기 (최대 300ms 재시도)
    if (_pendingRelayChannels.TryRemove(channelId, out var relayChannel))
        return relayChannel;

    await Task.Delay(300, CancellationToken.None);

    if (_pendingRelayChannels.TryRemove(channelId, out relayChannel))
        return relayChannel;

    return new RelayChannelNotFoundException(channelId);
}
```

### 3.5 Client 프로세스의 Gateway 사용

Service 프로세스뿐 아니라 **Client 프로세스**도 Gateway를 통해 API에 접근해야 합니다. 이를 위해 `RelayChannelLocalPortForwarder`가 로컬 프록시를 제공합니다:

**위치**: `apps/winsac/Agent/WinSAC.Agent.Service/Services/QueryPie/Gateway/RelayChannelLocalPortForwarder.cs`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WinSAC.Agent.Client.exe (사용자 세션)                                       │
│                                                                              │
│    HTTP 요청 → localhost:dynamicPort                                        │
│                       │                                                      │
└───────────────────────│──────────────────────────────────────────────────────┘
                        │ TCP
                        ↓
┌───────────────────────────────────────────────────────────────────────────────┐
│  WinSAC.Agent.Service.exe (SYSTEM)                                            │
│                                                                               │
│    RelayChannelLocalPortForwarder                                            │
│    └─ TCP Accept → IRelayChannelFactory.ConnectAsync()                       │
│                    └─ Gateway 연결 가능: Relay Channel 사용                   │
│                    └─ Gateway 연결 불가: 직접 TCP 연결 fallback               │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 3.6 타임아웃 및 재시도 정책

| 항목 | 값 | 설명 |
|------|-----|------|
| Gateway Handshake 타임아웃 | 30초 | 핸드셰이크 완료까지 대기 |
| Relay Channel 대기 | 5초 | `_pendingRelayChannels`에서 소비 대기 |
| ConnectAsync 매칭 재시도 | 300ms | 첫 시도 실패 시 300ms 후 재시도 |
| Control Channel Ping/Pong | 30초 | 연결 유지 확인 |

### 3.7 장애 상황 처리

| 상황 | Server Agent 동작 |
|------|------------------|
| Control Channel 없음 | `ControlChannelNotConnectedException` → 직접 TCP fallback |
| Relay Channel 미소비 (5초) | 연결 자동 정리, 로그 경고 |
| Relay Channel 매칭 실패 | `RelayChannelNotFoundException` → 직접 TCP fallback |
| Gateway Handshake 실패 | 연결 종료, 에러 로그 |

---

## 4. Nova 동작 원리

> **상세 문서**: Nova 내부 구현 상세 (환경변수 설정, 배포, 운영 가이드 등)는
> `/apps/nova/.claude/skills/nova-doc/` 스킬 문서를 참조하세요.

### 4.1 컴포넌트 상세

- **NOVAS** (Nova Server): 터널 서버 (외부에서 SSH 수신 + REST API)
- **NOVAC** (Nova Client): 터널 에이전트 (내부에서 SSH 아웃바운드)

### 4.2 핵심 기능

- 인바운드 포트 개방 없이 외부 접근 가능
- SOCKS5 프록시 기반 동적 포워딩
- Redis 레지스트리를 통한 서버 발견 (분산 환경)
- Tags 기반 라우팅 (환경, 리전 등으로 필터링)

### 4.3 Nova 데이터 흐름 상세

```
External Client (ARiSA)
    │
    ├─ HTTP CONNECT server:13389
    ├─ Header: X-NOVA-TAGS: env=prod;region=asia
    │
    ↓
NOVAS API Server
    │
    ├─ Tags 매칭으로 Session 선택
    │  (Least Connection 알고리즘)
    │
    ├─ Forwarder 선택 (Round-Robin)
    │
    ├─ forwarder.Dial(ctx, "target-server:443")
    │
    ↓
ReverseDynamicForwarder
    │
    ├─ SSH "forwarded-tcpip" 채널 오픈
    │  - DestAddr: 127.0.0.1 (NOVAC 바인딩 주소)
    │  - DestPort: 동적 할당 포트
    │
    ↓
NOVAC SOCKS5 Server
    │
    ├─ SSH 채널을 통해 요청 수신
    ├─ SOCKS5 프로토콜 해석
    ├─ 최종 타겟으로 연결
    │
    ↓
Target Server (내부 네트워크)
```

### 4.4 X-NOVA-TAGS 상세

Nova의 **Tags 기반 라우팅**은 여러 NOVAC 중 적절한 에이전트를 선택하기 위한 메커니즘입니다.

#### 형식

```
X-NOVA-TAGS: key1=val1;key2=val2;key3=val3
```

- 세미콜론(`;`)으로 구분
- 각 항목은 `key=value` 형식
- 공백은 trim됨
- 중복 키 불가

#### NOVAC 설정

NOVAC이 NOVAS에 연결할 때 자신의 태그를 등록합니다:

```bash
# 환경변수로 설정
export NOVAC_TAGS="env=prod;region=us-west;tier=api"
export NOVAC_NAME="agent-1"
```

**전달 흐름**:
```
1. NOVAC 시작 → NOVAC_TAGS 환경변수 파싱
2. SSH 연결 → session.Setenv("NOVAC_TAGS", tagString)
3. NOVAS가 SSH 환경변수로 수신 → Session.Tags에 저장
```

#### 매칭 로직

클라이언트(ARiSA)가 `X-NOVA-TAGS` 헤더로 요청하면:

```go
// 1. 요청 태그 파싱
clientTags := ParseTagMap("env=prod;tier=api")

// 2. 모든 NOVAC 세션과 교집합 계산
for each session:
    commonTags := session.Tags.GetIntersection(clientTags)
    if len(commonTags) == 0:
        skip  // 일치하는 태그 없음

// 3. Least Connection 선택
// 공통 태그가 있는 세션 중 활성 터널 개수가 가장 적은 세션 선택
```

**매칭 예시**:
```
Client 요청:  env=prod;tier=api
NOVAC-1:      env=prod;region=us-west;tier=api    → 공통: env=prod, tier=api (2개) ✓
NOVAC-2:      env=dev;region=us-east;tier=api     → 공통: tier=api (1개) ✓
NOVAC-3:      env=staging;region=eu               → 공통: 없음 ✗
```

#### 응답 헤더

선택된 세션의 정보를 응답 헤더로 반환:
```
X-NOVA-TAGS: env=prod;tier=api    // 공통 태그
X-NOVA-NAME: agent-1              // 선택된 NOVAC 이름
```

---

## 5. 네트워크 구성 시나리오 상세

### 5.1 Gateway SSH Multi-hop 상세 시퀀스

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ ARiSA    │   │ Gateway  │   │JumpHost1 │   │JumpHost2 │   │Server Agt│
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │              │
     │ Relay 요청   │              │              │              │
     ├─────────────→│              │              │              │
     │              │ SSH 연결     │              │              │
     │              ├─────────────→│              │              │
     │              │              │ Port Forward │              │
     │              │              ├─────────────→│              │
     │              │              │              │ SOCKS5       │
     │              │              │              ├─────────────→│
     │              │              │              │              │
     │←════════════════════════════════════════════════════════→│
     │              TLS Tunnel (양방향 데이터 전송)               │
```

### 5.2 Nova Reverse Tunnel 상세 시퀀스

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ ARiSA    │   │  NOVAS   │   │  Redis   │   │  NOVAC   │   │Server Agt│
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │              │
     │              │              │ ← 서버등록   │              │
     │              │              │←─────────────┤              │
     │              │←─ SSH 연결 ─────────────────┤              │
     │              │  (아웃바운드)│              │              │
     │              │              │              │              │
     │ GET /sessions│              │              │              │
     ├─────────────→│              │              │              │
     │              │─ Redis 조회 →│              │              │
     │              │←─────────────┤              │              │
     │←─────────────┤              │              │              │
     │              │              │              │              │
     │ HTTP CONNECT │              │              │              │
     │ X-NOVA-TAGS  │              │              │              │
     ├─────────────→│              │              │              │
     │              │─ forwarded-tcpip ──────────→│              │
     │              │              │              │─ SOCKS5 ────→│
     │              │              │              │              │
     │←════════════════════════════════════════════════════════→│
     │              양방향 데이터 전송 (SSH 터널 경유)             │
```

### 5.3 Gateway + Nova 조합 상세 흐름

가장 복잡한 구성: Gateway의 SSH 점프와 Nova의 Reverse Tunnel을 함께 사용하는 환경.

**상세 흐름**:
```
1. Gateway가 SSH JumpHost들을 거쳐 NOVAS에 연결
2. NOVAS는 이미 NOVAC과 Reverse SSH Tunnel이 수립된 상태
3. Gateway → NOVAS: HTTP CONNECT 요청 (X-NOVA-TAGS 포함)
4. NOVAS → NOVAC: forwarded-tcpip 채널을 통해 연결 전달
5. NOVAC → Server Agent: SOCKS5로 최종 연결
6. 양방향 데이터 전송
```

**사용 환경**:
- NOVAS가 직접 노출되지 않고 SSH 점프 호스트 뒤에 있는 환경
- 다중 보안 구역 + 인바운드 차단이 동시에 적용된 환경
- 고도의 네트워크 격리가 필요한 금융/공공 환경

**장점**:
- 최대한의 네트워크 격리 보장
- 기존 SSH 인프라 활용 가능
- 인바운드 포트 개방 최소화

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2025-01-19 | 초기 문서 생성 - DELETED_CONTENT.md에서 상세 내용 복원 |
