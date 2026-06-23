# 네트워크 컴포넌트 및 구성 시나리오

QueryPie RDP 접근제어에서 복잡한 네트워크 환경을 지원하는 Gateway와 Nova 컴포넌트를 설명합니다.

---

## 1. 개요

QueryPie는 다양한 네트워크 환경에 대응하기 위해 **Gateway**와 **Nova** 두 가지 컴포넌트를 제공합니다. 두 컴포넌트는 **개별 사용**하거나 **조합해서 사용**할 수 있습니다.

| 컴포넌트 | 용도 | 사용 환경 |
|---------|------|----------|
| **Gateway** | SSH 점프 호스트 또는 Direct 연결 | Server Agent에 직접 접근 불가 |
| **Nova** | Reverse SSH Tunnel | 인바운드 완전 차단 환경 |

```
┌─────────────────────────────────────────────────────────────────────┐
│                        네트워크 접근 방식                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [직접 연결]     ARiSA ─────────────────────→ Server Agent          │
│                                                                      │
│  [Gateway]       ARiSA → Gateway ──(SSH)──→ Server Agent            │
│                                                                      │
│  [Nova]          ARiSA → NOVAS ←──(SSH)── NOVAC → Server Agent      │
│                                                                      │
│  [Gateway+Nova]  ARiSA → Gateway → NOVAS ←─ NOVAC → Server Agent    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Gateway

**위치**: `apps/gateway` | **언어**: C# (.NET)

> **상세 문서**: Gateway 내부 구현 상세는 `apps/gateway/.claude/skills/gateway-doc/` 스킬 문서를 참조하세요.
> 환경변수 설정, 세션 관리, Protocol SDK 구조 등을 다룹니다.

SSH 점프 호스트 터널링 또는 Direct 연결을 통해 Server Agent에 접근합니다.

### 2.1 핵심 기능

- Direct Tunnel 지원 (점프 호스트 없이 직접 연결)
- SSH 다중 점프 호스트 터널 생성
- Control Channel / Relay Channel 관리
- SOCKS5 프록시 기반 동적 포워딩

### 2.2 Control Channel vs Relay Channel

| 구분 | Control Channel | Relay Channel |
|------|----------------|---------------|
| **역할** | 제어 메시지 전달 | 실제 데이터 전송 |
| **수명** | 장기 지속 (항상 연결 유지) | 단기 임시 (요청 시 생성) |
| **용도** | Ping/Pong, Relay 요청 | HTTP 요청, 데이터 포워딩 |
| **관리** | ControlChannelPool | 5초 타임아웃 후 정리 |

```
WinSAC                                    Gateway                        API Server
  |                                          |                               |
  | <------ Control Channel Established ----->|                               |
  | (항상 유지, Ping/Pong 30초마다)            |                               |
  |                                          |                               |
  |-- 1. RelayRequest via ControlChannel --> |                               |
  |                                          | <--- 2. TCP handshake ----->  |
  | <-- 3. RelayResponse + channelId ------- |                               |
  |                                          |                               |
  |-- 4. New TCP connection (RelayConn) --> |                               |
  |                                          |                               |
  | <== 5. HTTP Request/Response via RelayChannel ========================> |
```

**왜 채널을 분리하는가?**

각 채널을 통해 전송되는 트래픽 특성이 다릅니다:

| 채널 | 트래픽 예시 | 특성 |
|------|-----------|------|
| **Control** | Heartbeat, RelayRequest/Response | 작은 메시지, **즉시 응답 필요** |
| **Relay** | 이벤트 로그 bulk 전송, 커맨드 오딧 | 대용량, 지연 허용 |

단일 채널 사용 시 문제:
- 대용량 이벤트 로그 전송 중 Heartbeat가 블로킹됨
- Heartbeat 지연 → Server Agent 상태가 OFFLINE으로 오판될 수 있음
- 감사 로그 전송이 제어 메시지에 영향을 주면 안 됨

### 2.3 주기적 API 요청 (1분마다)

Gateway는 매 1분마다 API와 ARiSA에 요청하여 라우팅 정보를 갱신합니다.

| 데이터 | 엔드포인트 | 호스트 |
|--------|-----------|--------|
| 프록시 점프 경로 | `GET /_internal/gateway/proxy-jumps` | API |
| 직접 연결 서버 | `GET /api/features/winsac/connected-servers` | ARiSA |

**proxy-jumps 응답 예시**:
```json
{
  "proxyJumps": [{
    "jumpHosts": [
      { "host": "jump1.example.com", "port": 22, "auth": {...} }
    ],
    "servers": [
      { "host": "windows-server1.example.com", "port": 13389, "cookie": "..." }
    ]
  }]
}
```

**Gateway의 응답 처리**:
| 상황 | Gateway 동작 |
|------|-------------|
| **JumpHosts 있음** | SSH 다중 홉 연결 |
| **JumpHosts 없음** | Direct 연결 |
| **서버 추가** | ClientSession 추가 |
| **서버 제거** | ClientSession 정리 |

### 2.4 영구세션 vs 임시세션

Gateway가 `connected-servers` API를 호출하는 이유는 **ARiSA에 활성 RDP 세션이 있는 서버의 Gateway 세션을 영구 유지**하기 위함입니다.

```
[RDP 세션 진행 중]
Server Agent ──(세션 로그/커맨드 오딧)──→ Gateway ──(Relay)──→ API
                                            ↑
                                    영구세션 필요!
```

| 유형 | 만료 시간 | 설명 |
|------|----------|------|
| **Persistent** | 무제한 | ARiSA에 활성 세션 있음 |
| **Temporary** | 5분 후 | ARiSA 세션 종료됨 (재연결 대기) |

**왜 ARiSA 세션 상태가 Gateway 터널과 연관되는가?**

RDP 세션 흐름을 보면 이해할 수 있습니다:

```
RDP 트래픽:     Client Agent → ARiSA → Gateway → Server Agent → Windows RDP
API 트래픽:     Server Agent → Gateway → API  (RequireGatewayTunnel=true일 때)
```

- **ARiSA에 활성 RDP 세션이 있으면**: Server Agent가 이벤트 로그, 커맨드 오딧 등을 API에 전송해야 함 → 이 트래픽이 Gateway 경유 → **터널 필수**
- **ARiSA에 활성 RDP 세션이 없으면**: Server Agent는 Heartbeat 정도만 전송 → 터널 유지 불필요

즉, **ARiSA 세션 상태 = Gateway 터널 필요성**이라는 본질적인 의존 관계가 있습니다.

**왜 터널을 유지하는가? (On-demand가 아닌 이유)**

다중 SSH 점프호스트 환경에서 터널 생성 비용이 큽니다:

| 환경 | 터널 생성 시간 | 세션 중 API 호출 빈도 |
|------|--------------|---------------------|
| Direct (hop 없음) | ~1초 | - |
| 2 hop | ~4-6초 | - |
| 3-4 hop | **10초 이상** | - |

RDP 세션 중 Server Agent가 보내는 API 호출:
- 이벤트 로그 (키 입력, 마우스, 프로세스 실행 등): **수백~수천 건/세션**
- Connected/Disconnected
- 커맨드 오딧

다중 hop 환경에서 매 API 호출마다 터널을 생성하면 **UX 파탄** → 터널 유지가 필수입니다.

**5분 유예 기간의 목적 (Connection Pooling)**:
- 세션이 종료되었다가 곧바로 다시 연결될 경우 터널 재생성 오버헤드 방지
- 짧은 시간 내 재연결 시 기존 Gateway 세션 재사용 가능
- 불필요한 SSH 핸드셰이크/TLS 협상 반복 최소화
- 특히 3-4 hop 환경에서 **10초 이상의 재연결 지연**을 방지

### 2.5 다중 SSH 점프 호스트 터널링

```
설정: JumpHosts = [ssh1.com, ssh2.com, ssh3.com]
목표: api.internal:8080

1. Local → ssh1.com:22 (직접 SSH)
2. ssh1 → ssh2.com:22 (포트 포워딩)
3. ssh2 → ssh3.com:22 (포트 포워딩)
4. ssh3 → Dynamic SOCKS (SOCKS5 프록시)
5. SOCKS → api.internal:8080 (최종 목표)
```

### 2.6 Gateway Protocol

Gateway ↔ Server Agent 간 프로토콜입니다.

| 메시지 | 값 | 용도 |
|--------|---|------|
| ClientHello | 0xFE | 핸드셰이크 시작 |
| ServerHello | 0xFD | 핸드셰이크 응답 |
| Ping/Pong | 0xFA/0xF9 | 연결 유지 (30초) |
| RelayRequest | 0xF7 | 릴레이 요청 |
| RelayResponse | 0xF6 | 릴레이 응답 |
| Close | 0xF5 | 연결 종료 |

**ConversationID 기반 요청-응답 매칭**: 각 RelayRequest에 고유 ConversationID가 부여되어, RelayResponse와 1:1 매칭됩니다.

### 2.7 Gateway 주요 클래스

| 클래스 | 역할 |
|--------|------|
| `GatewayService` | 메인 서비스, API 폴링 및 워커 관리 |
| `GatewayWorker` | 점프 호스트 체인당 하나, SSH 연결 관리 |
| `ControlChannelPool` | Control Channel 풀 관리 |
| `RelayChannelFactory` | Relay Channel 생성 팩토리 |
| `DirectSessionManager` | 직접 연결 세션 관리 |
| `ProxyJumpConnection` | SSH 프록시 점프 연결 |
| `GatewaySsl` | TLS/ALPN 처리 |

---

## 3. Server Agent 측 Gateway 처리

Server Agent가 Gateway 연결을 수신하고 처리하는 방법입니다.

### 3.1 연결 방향

**Gateway가 Server Agent로 연결**합니다 (반대 방향이 아님):

```
Gateway ──(TLS)──→ Server Agent:13389 ──(ALPN: qpgateway)──→ GatewayService
```

### 3.2 GatewayService 구조

Server Agent의 TLS Router에서 `qpgateway` ALPN으로 Gateway 연결을 수신합니다.

```csharp
// TLS Router에 qpgateway ALPN 리스너 등록
var listener = tlsRouter.CreateListener(GatewaySsl.ApplicationProtocol);
while (!stoppingToken.IsCancellationRequested)
{
    var connection = await listener.AcceptAsync(stoppingToken);
    if (connection.Data.Type == ConnectionType.Control)
        await HandleControlChannelAsync(connection);  // 풀에 추가, 장기 유지
    else
        await HandleRelayChannelAsync(connection);    // 5초 내 소비 필요
}
```

### 3.3 Relay Channel 매칭

Server Agent가 API에 요청할 때 Gateway를 통해 연결하는 흐름:

```
Server Agent                                    Gateway                    API
    |                                              |                        |
    | -- 1. RelayRequest via Control Channel ----> |                        |
    |      (host="api.querypie.io", port=443)      |                        |
    |                                              | <== 2. TCP handshake ==>|
    | <-- 3. RelayResponse + channelId ----------- |                        |
    |                                              |                        |
    |                                              | -- 4. TLS (Relay) ---> |
    | <--- 5. TLS Router: qpgateway ALPN 수신 ---- |                        |
    |       _pendingRelayChannels[channelId] = ch  |                        |
    |                                              |                        |
    | -- 6. ConnectAsync에서 channelId로 매칭 --> |                        |
    |                                              |                        |
    | <======================== 7. HTTP Request/Response ================> |
```

### 3.4 QPApiClient의 Gateway 사용

```csharp
handler.ConnectCallback = async (context, cancellationToken) =>
{
    var factory = services.GetRequiredService<IRelayChannelFactory>();

    if (factory.CanConnect())
    {
        // Gateway 연결됨 → Relay Channel 사용
        var result = await factory.ConnectAsync(endPoint, cancellationToken);
        if (result.Success)
            return result.Value.Stream;
    }

    // Gateway 연결 안 됨 → 직접 TCP fallback
    var socket = new Socket(SocketType.Stream, ProtocolType.Tcp);
    await socket.ConnectAsync(endPoint, cancellationToken);
    return new NetworkStream(socket, ownsSocket: true);
};
```

### 3.5 타임아웃 및 장애 처리

| 항목 | 값 |
|------|-----|
| Gateway Handshake | 30초 |
| Relay Channel 대기 | 5초 |
| ConnectAsync 재시도 | 300ms |
| Ping/Pong | 30초 |

| 상황 | 동작 |
|------|------|
| Control Channel 없음 | 직접 TCP fallback |
| Relay Channel 미소비 | 5초 후 정리 |
| Relay Channel 매칭 실패 | 직접 TCP fallback |

---

## 4. Nova

**위치**: `apps/nova` | **언어**: Go

Reverse SSH Tunnel을 통해 인바운드 차단 환경에서 접근을 제공합니다.

> **상세 문서**: Nova 내부 구현 상세는 `/apps/nova/.claude/skills/nova-doc/` 스킬 문서를 참조하세요.
> 환경변수 설정, 배포 구성, 운영/트러블슈팅 가이드 등을 다룹니다.

### 4.1 컴포넌트

| 컴포넌트 | 위치 | 역할 |
|---------|------|------|
| **NOVAS** (Server) | 외부 | SSH 서버 + REST API |
| **NOVAC** (Client) | 내부 | SSH 아웃바운드 + SOCKS5 |

### 4.2 통신 시퀀스

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NOVAC (내부 네트워크)                        │
│                                                                      │
│  1. SSH 아웃바운드 연결 (password auth, Ed25519 검증)               │
│  2. Shell Session 열기 (NOVAC_NAME, NOVAC_TAGS 전송)               │
│  3. tcpip-forward 요청 (Remote Port Binding)                       │
│  4. SOCKS5 프록시 서버 시작                                         │
└────────────────────────────────────────────────┬────────────────────┘
                                                 │ SSH 아웃바운드
                                                 ↓
┌────────────────────────────────────────────────────────────────────┐
│                         NOVAS (외부 네트워크)                       │
│                                                                     │
│  SSH Server (포트 22)        REST API Server (포트 9090)           │
│  └─ tcpip-forward 수신        └─ /sessions: 세션 목록 조회         │
│  └─ forwarded-tcpip 채널       └─ HTTP CONNECT 프록시             │
│                                                                     │
│  Redis Registry                                                     │
│  └─ 활성 NOVAS 서버 등록 (TTL 10초, 5초마다 갱신)                  │
└────────────────────────────────────────────────────────────────────┘
```

### 4.3 데이터 흐름

```
External Client (ARiSA)
    │
    ├─ HTTP CONNECT to NOVAS:9090
    │  Header: X-NOVA-TAGS: env=prod;region=us
    │
    ↓
NOVAS API Server
    ├─ Tags 매칭으로 Session 선택 (Least Connection)
    ├─ forwarded-tcpip 채널 오픈
    ↓
NOVAC SOCKS5 Server
    ├─ SSH 채널을 통해 요청 수신
    ├─ SOCKS5 프로토콜 해석
    ↓
Target Server (내부 네트워크)
```

### 4.4 X-NOVA-TAGS

Nova의 Tags 기반 라우팅으로 적절한 NOVAC을 선택합니다.

**형식**: `key1=val1;key2=val2`

**NOVAC 설정**:
```bash
export NOVAC_TAGS="env=prod;region=us-west;tier=api"
export NOVAC_NAME="agent-1"
```

**매칭 예시**:
```
Client 요청:  env=prod;tier=api
NOVAC-1:      env=prod;region=us-west;tier=api    → 공통 2개 ✓
NOVAC-2:      env=dev;region=us-east;tier=api     → 공통 1개 ✓
NOVAC-3:      env=staging;region=eu               → 공통 0개 ✗
```

**사용**:
```bash
curl -x http://NOVAS:9090 https://internal-server.local \
  --proxy-header "X-NOVA-TAGS: env=prod;tier=api"
```

---

## 5. 네트워크 구성 시나리오

### 5.1 직접 연결

가장 기본적인 구성입니다.

```
Client Agent ──TLS──→ ARiSA ──TLS──→ Server Agent
```

**조건**: Server Agent 13389 포트 인바운드 허용

### 5.2 Gateway Direct Tunnel

점프 호스트 없이 Gateway 경유 연결입니다.

```
Client Agent → ARiSA → Gateway (Direct) → Server Agent
```

**조건**: Gateway에서 Server Agent로 직접 연결 가능

### 5.3 Gateway SSH Multi-hop

SSH 점프 호스트를 거쳐야 하는 환경입니다.

```
Client Agent → ARiSA → Gateway → JumpHost1 → JumpHost2 → Server Agent
```

**사용 환경**: 다중 보안 구역, Bastion 호스트 정책

### 5.4 Nova Reverse Tunnel

인바운드가 완전 차단된 환경입니다.

```
NOVAC (내부) ──SSH 아웃바운드──→ NOVAS (외부)
                                   ↑
Client Agent → ARiSA ──────────────┘
```

**사용 환경**: 인바운드 차단, 방화벽 정책 변경 불가

### 5.5 Gateway + Nova 조합

가장 복잡한 구성: SSH 점프 + Reverse Tunnel 조합입니다.

```
┌─────────────────────────────────────────────────────────────────────┐
│                           외부 (QueryPie 인프라)                     │
│                                                                      │
│  Client Agent → ARiSA → Gateway ──(SSH JumpHosts)──→ NOVAS          │
│                                                           │          │
└───────────────────────────────────────────────────────────│──────────┘
                                              HTTP CONNECT via SSH
                                                            │
┌───────────────────────────────────────────────────────────│──────────┐
│                           내부 (고객 네트워크)              │          │
│                                                           ↓          │
│                                         NOVAC ←──(SSH)────┘          │
│                                           │ SOCKS5                   │
│                                           ↓                          │
│                                     Server Agent                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**사용 환경**:
- NOVAS가 직접 노출되지 않고 SSH 점프 호스트 뒤에 있는 환경
- 다중 보안 구역 + 인바운드 차단이 동시에 적용된 환경
- 고도의 네트워크 격리가 필요한 금융/공공 환경

**장점**:
- 최대한의 네트워크 격리 보장
- 인바운드 포트 개방 불필요
- 다중 보안 구역 통과 가능

**주의사항**:
- 지연 시간 증가 (여러 홉 경유)
- 장애 포인트 증가 (JumpHost, NOVAS, NOVAC 모두 정상 동작 필요)

---

## 6. 주요 포트

| 컴포넌트 | 포트 | 용도 |
|---------|------|------|
| Gateway | 설정값 | 클라이언트 수신 |
| NOVAS | 22 | SSH 서버 |
| NOVAS | 9090 | REST API |
| SSH JumpHost | 22 | 점프 호스트 |

---

## 7. 보안 특성

| 구간 | 암호화 | 인증 |
|------|--------|------|
| Gateway ↔ Server Agent | TLS + Gateway Protocol | ALPN 기반 라우팅 |
| Gateway ↔ JumpHost | SSH | 패스워드/개인키 |
| NOVAC ↔ NOVAS | SSH | Ed25519 + 토큰 |
| ARiSA ↔ NOVAS | HTTP CONNECT | X-NOVA-TAGS |

---

## 8. 문제 해결

| 증상 | 확인 포인트 |
|------|------------|
| 느린 연결 | 터널 홉 수, 네트워크 지연 |
| Relay Channel 타임아웃 | 5초 내 연결 필요, 네트워크 상태 |
| Nova 세션 없음 | NOVAC 실행 상태, Redis 등록 |
| SSH 연결 실패 | JumpHost 인증정보, 네트워크 |
| Tags 매칭 실패 | X-NOVA-TAGS, NOVAC_TAGS 설정 |

상세 진단은 [diagnose/SKILL.md](../diagnose/SKILL.md)를 참조하세요.
