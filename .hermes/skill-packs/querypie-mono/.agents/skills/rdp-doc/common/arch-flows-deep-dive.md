# RDP 흐름 Deep Dive

이 문서는 RDP 접근제어 시스템의 **주요 흐름**에 대한 상세 설명을 제공합니다.
Activate, 상태 전이, Heartbeat, 업데이트, RDP 접속 등의 시퀀스 다이어그램과 상세 단계를 다룹니다.

간소화된 개요는 [ARCHITECTURE.md](./ARCHITECTURE.md), 네트워크 관련 상세는 [DEEP-DIVE.md](./DEEP-DIVE.md)를 참조하세요.

---

## 1. Activate 흐름

### 1.1 왜 필요한가?

Server Agent가 설치되었다고 해서 바로 사용할 수 있는 것이 아닙니다. API 서버가 Server Agent를 인식하고 **AgentUuid를 할당**해야 합니다. 이 과정이 Activate입니다.

### 1.2 Activate 상세 흐름

```
┌──────────────┐                ┌──────────────┐                ┌──────────────┐
│ Server Agent │                │     API      │                │    Admin     │
│  (신규 설치)  │                │              │                │   Console    │
└──────┬───────┘                └──────┬───────┘                └──────┬───────┘
       │                               │                               │
       │ ① Heartbeat 전송              │                               │
       │   (AgentUuid=null)           │                               │
       ├──────────────────────────────→│                               │
       │                               │                               │
       │                               │ ② 신규 Server Agent 등록      │
       │                               │   상태: WAITING_FOR_ACTIVATION│
       │                               │                               │
       │                               │ ③ 관리자가 확인               │
       │                               │←──────────────────────────────┤
       │                               │                               │
       │                               │ ④ AgentUuid 생성              │
       │                               │                               │
       │   ⑤ POST /api/activate       │                               │
       │←──────────────────────────────┤                               │
       │   (AgentUuid 전달)            │                               │
       │                               │                               │
       │ ⑥ AgentUuid 레지스트리 저장   │                               │
       │                               │                               │
       │ ⑦ 다음 Heartbeat              │                               │
       │   (AgentUuid=할당된값)        │                               │
       ├──────────────────────────────→│                               │
       │                               │                               │
       │                               │ ⑧ 상태 변경: HEALTHY          │
       │                               │                               │
```

### 1.3 Activate 조건

- Server Agent가 Heartbeat 또는 Heartbeat Scan으로 발견됨
- 상태가 `WAITING_FOR_ACTIVATION`
- API가 Server Agent의 `/api/activate` 엔드포인트에 접근 가능

### 1.4 Activate 실패 원인

| 원인 | 설명 |
|------|------|
| 방화벽 차단 | Server Agent (13389 포트) 인바운드 차단 |
| 터널 미수립 | Gateway/Nova 터널이 아직 수립되지 않음 |
| 서비스 중지 | Server Agent 서비스가 시작되지 않음 |

---

## 2. Server Agent 상태 전이

### 2.1 상태 정의

| 상태 | 설명 |
|------|------|
| **WAITING_FOR_ACTIVATION** | 신규 설치, AgentUuid 미할당 |
| **HEALTHY** | Heartbeat 정상 수신 중 |
| **OFFLINE** | Heartbeat 5분 이상 미수신 |
| **DEGRADED** | 일부 기능 제한 (정책 미적용 등) |

### 2.2 상태 전이 다이어그램 (상세)

```
                                       ┌────────────────────────────┐
                                       │                            │
┌───────────────────┐     Activate     │  ┌───────────────────┐     │
│ WAITING_FOR_      │ ────────────────→│  │     HEALTHY       │←────┘
│ ACTIVATION        │                  │  │                   │  Heartbeat
└───────────────────┘                  │  └─────────┬─────────┘  재수신
   (최초 설치 시에만)                   │            │
                                       │  5분 이상  │
                                       │  미수신    ▼
                                       │  ┌───────────────────┐
                                       │  │     OFFLINE       │
                                       │  │                   │
                                       │  └───────────────────┘
                                       │
                                       └─ OFFLINE에서 Heartbeat 재수신 시
                                          HEALTHY로 복귀 (WAITING_FOR_ACTIVATION 아님)
```

### 2.3 주의사항

- `WAITING_FOR_ACTIVATION`은 **최초 설치 시에만** 나타나는 상태입니다.
- OFFLINE 상태에서 Heartbeat를 다시 수신하면 이미 AgentUuid가 할당되어 있으므로 **바로 HEALTHY로 복귀**합니다.

---

## 3. Heartbeat 흐름

### 3.1 Heartbeat 페이로드

```json
{
  "AgentId": "고유 ID",
  "AgentUuid": "UUID (최초에는 null)",
  "Status": "HEALTHY",
  "Version": "에이전트 버전",
  "OSVersion": "Windows OS 버전",
  "ComputerName": "컴퓨터명 (15자)",
  "UnicastAddresses": ["192.168.1.10", "10.0.0.5"],  // 모든 NIC의 IPv4 주소 배열
  "RdpPort": 13389,
  "RequireGatewayTunnel": false
}
```

### 3.2 Heartbeat 흐름 다이어그램

```
┌──────────────┐                 ┌──────────────┐
│ Server Agent │                 │     API      │
└──────┬───────┘                 └──────┬───────┘
       │                                │
       │ PUT /api/server-agent/heart-beat
       ├───────────────────────────────→│  (Heartbeat 송신)
       │                                │
       │←── 응답 (정책 변경 여부 등) ────│
       │                                │
       │←── Health Check 요청 ──────────│  (Health Check 수신)
       │                                │
       │─── Health Check 응답 ─────────→│
       │                                │
       │ (1분 후 반복)                   │
       │                                │
```

### 3.3 UnicastAddresses 배열과 접근 가능한 호스트 검증

#### 왜 필요한가?

Server Agent는 `UnicastAddresses` 필드에 **모든 NIC의 IPv4 주소를 배열로** 전송합니다.

```json
{
  "UnicastAddresses": ["192.168.1.10", "10.0.0.5", "172.16.0.100"],
  ...
}
```

**문제 상황:**
- Windows 서버에 여러 NIC가 있을 수 있음 (HA 구성, 관리 네트워크, iSCSI 등)
- 첫 번째 IP가 항상 API에서 접근 가능한 주소라는 보장이 없음
- 특정 IP가 다른 Server Agent(예: Standby 노드)의 IP와 동일할 수 있음

#### API 측 검증 로직

신규 Server Agent 등록 시 또는 `WAITING_FOR_ACTIVATION` 상태에서 API는 **접근 가능한 호스트를 검증**합니다.

```
┌──────────────┐                           ┌──────────────┐
│     API      │                           │ Server Agent │
└──────┬───────┘                           └──────┬───────┘
       │                                          │
       │ ① Heartbeat 수신                         │
       │   UnicastAddresses: [IP1, IP2, IP3]      │
       │←─────────────────────────────────────────│
       │                                          │
       │ ② 모든 IP에 병렬로 /api/health 요청       │
       │   (타임아웃: 60초)                        │
       ├─────────────────────────────────────────→│ (또는 다른 Agent)
       │                                          │
       │ ③ 응답의 AgentId 검증                    │
       │   (요청한 AgentId와 일치하는지)            │
       │                                          │
       │   └─ 불일치 시: 해당 IP 무시              │
       │   └─ 일치 시: 해당 IP를 manualHost로 저장 │
       │   └─ 첫 번째 성공한 호스트 반환           │
       │                                          │
```

> **Note**: 검증은 `Flux.flatMap`을 사용하여 **병렬로** 수행됩니다. 모든 호스트를 동시에 체크하고 첫 번째로 성공하는 호스트를 반환합니다.

#### 타임아웃 설정

Server Agent의 TlsRouterService 시작에 약 15초가 소요될 수 있어, 충분한 타임아웃이 필요합니다.

| 설정 | 값 | 용도 |
|------|-----|------|
| `CONNECT_TIMEOUT_MILLIS` | 60초 | TCP 연결 타임아웃 |
| `responseTimeout` | 60초 | HTTP 응답 타임아웃 |
| SSH 터널 생성 | 60초 | ProxyJump 경유 시 터널 생성 |

#### AgentId 검증이 중요한 이유

```
[시나리오: HA 클러스터에서 IP 충돌]

Windows Server A (Active)
├─ AgentId: "AGENT-A-XXXX"
├─ NIC1: 192.168.1.10 (서비스 IP, Active가 사용)
└─ NIC2: 10.0.0.5 (관리 IP)

Windows Server B (Standby)
├─ AgentId: "AGENT-B-YYYY"
├─ NIC1: 192.168.1.10 (서비스 IP, 현재 미사용)
└─ NIC2: 10.0.0.6 (관리 IP)

Server B가 Heartbeat 전송 시:
  UnicastAddresses: ["192.168.1.10", "10.0.0.6"]

API가 192.168.1.10으로 /api/health 호출:
  → Server A가 응답 (AgentId: "AGENT-A-XXXX")
  → 요청한 AgentId("AGENT-B-YYYY")와 불일치!
  → 건너뛰고 10.0.0.6으로 재시도
  → Server B가 응답 (AgentId: "AGENT-B-YYYY") ✓
  → 10.0.0.6을 manualHost로 저장
```

#### 10.x 하위호환성

10.x 버전의 Server Agent는 `/api/health` 응답에 `agentId`를 포함하지 않습니다. 이 경우 AgentId 검증을 생략합니다.

```kotlin
// 11.x 이후: agentId 포함 → 검증 수행
// 10.x: agentId 미포함 (body == null) → 검증 생략
if (body != null && agentId != body.agentId) {
    return@flatMap Mono.empty()  // 불일치 시 건너뜀
}
```

#### 호출 시점

| 시점 | 함수 | 동작 |
|------|------|------|
| **신규 등록** | `findAccessibleHost()` | 병렬로 접근 가능한 호스트 찾기, `createOrFindServerAndLink` 전에 호출 |
| **WAITING_FOR_ACTIVATION** | `activateServerAgent()` | 검증 후 `/api/activate` 호출 |
| **Heartbeat Scan 신규 발견** | `findAccessibleHost()` | Heartbeat Scan으로 신규 발견 시에도 동일하게 검증 |

#### 관리자 페이지에서 수동 수정

자동 검증이 실패하거나 네트워크 환경이 변경된 경우, **관리자 페이지에서 직접 IP를 수정**할 수 있습니다.

```
Settings > Servers > Server Agents > [Server Agent 선택] > Edit
  └─ Host 필드에서 IP 주소 직접 입력/수정 가능
```

수동으로 설정한 IP는 `manualHost`로 저장되며, 이후 자동 검증 결과보다 우선합니다.

#### 관련 코드

- `ServerAgentClient.kt`: `findAccessibleHost()`, `activateServerAgent()`
- `ServerAgentApplicationService.kt`: `receiveHeartbeat()`

---

## 4. 단일 포트 아키텍처

### 4.1 왜 단일 포트인가?

Server Agent는 **TLS Router(13389)**를 통해 여러 프로토콜을 단일 포트에서 처리합니다. TLS 핸드셰이크 시 **ALPN(Application-Layer Protocol Negotiation)**으로 프로토콜을 구분합니다.

### 4.2 ALPN 기반 라우팅

| ALPN 값 | 처리 서비스 | 용도 |
|---------|------------|------|
| `TunnelProtocol` | RDServerService | RDP 세션 (User Agent 연결) |
| `http/1.1` | WebHostService | HTTP API 호출 |
| `qpgateway` | GatewayService | Gateway 프로토콜 |

### 4.3 TLS Router 구조

```
                           ┌─────────────────────────────────────────────────┐
                           │               TLS Router (13389)                │
                           │                                                 │
                           │  ┌─────────────────────────────────────────┐    │
   외부 연결 ─────────────→│  │ TLS Handshake + ALPN Negotiation        │    │
                           │  └─────────────────────────────────────────┘    │
                           │                    │                            │
                           │      ┌─────────────┼─────────────┐              │
                           │      ▼             ▼             ▼              │
                           │ ┌─────────┐  ┌─────────┐  ┌─────────────┐       │
                           │ │qpgateway│  │http/1.1 │  │TunnelProtocol│      │
                           │ └────┬────┘  └────┬────┘  └──────┬──────┘       │
                           │      │            │              │              │
                           │      ▼            ▼              ▼              │
                           │ GatewayService WebHost    RDServerService       │
                           │                                                 │
                           └─────────────────────────────────────────────────┘
```

---

## 5. 업데이트 흐름

### 5.1 업데이트 시퀀스 (상세)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   QueryPie UI   │    │    Policy API   │    │  Server Agent   │
│   (관리자)       │    │                 │    │                 │
└───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘
        │                      │                      │
        │ ① 업데이트 요청       │                      │
        ├─────────────────────→│                      │
        │                      │                      │
        │                      │ ② 상태 검증           │
        │                      │ (ONLINE, 업데이트 중 아님)
        │                      │                      │
        │                      │ ③ 큐에 태스크 등록    │
        │                      │                      │
        │ ④ 응답               │                      │
        │←─────────────────────│                      │
        │                      │                      │
        │                      │ ⑤ 임시 토큰 생성      │
        │                      │                      │
        │                      │ ⑥ POST /api/maintenance/update
        │                      ├─────────────────────→│
        │                      │  (API Key 인증)       │
        │                      │                      │
        │                      │                      │ ⑦ 인바운드 차단
        │                      │                      │
        │                      │                      │ ⑧ 활성 세션 알림
        │                      │                      │  (메시지박스 표시)
        │                      │                      │
        │                      │                      │ ⑨ 모든 RDP 세션 종료
        │                      │                      │  (30초 타임아웃)
        │                      │                      │
        │                      │                      │ ⑩ 인스톨러 다운로드
        │                      │←─────────────────────│
        │                      │  (temporaryToken 사용) │
        │                      │─────────────────────→│
        │                      │                      │
        │                      │                      │ ⑪ 서명 검증
        │                      │                      │  (QueryPie 인증서)
        │                      │                      │
        │                      │                      │ ⑫ 파일 락 확인
        │                      │                      │
        │                      │                      │ ⑬ 인스톨러 실행
        │                      │                      │  (/VERYSILENT /DELAY=3000)
        │                      │                      │
        │                      │ ⑭ 200 OK             │
        │                      │←─────────────────────│
        │                      │                      │
        │                      │ ⑮ 상태 업데이트       │
        │                      │  (UPDATE_COMPLETED)   │
        │                      │                      │
```

### 5.2 Server Agent 내부 처리 (ApplicationUpdater)

```csharp
// 1. 작업 디렉토리 생성
_workingDir = Path.Combine(TempDirectory, Path.GetRandomFileName())

// 2. 인스톨러 다운로드
await apiClient.DownloadFileAsync(installerURL, _installerPath)

// 3. 서명 검증 (QueryPie 인증서만 허용)
if (pe.SigningAuthenticodeCertificate.Subject != "QueryPie")
    return Error

// 4. 파일 락 확인
if (IsFileLocked(_installerPath))
    return Error

// 5. 인스톨러 실행 (/VERYSILENT로 무음 설치)
Process.Start(_installerPath, "/VERYSILENT /DELAY=3000")
```

---

## 6. RDP 접속 흐름

### 6.1 Server Agent 설치 시 (상세)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│Chrome WebView│   │ Multi-Agent  │   │    ARiSA     │   │ Server Agent │   │ Windows RDP  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │                  │                  │
       │ ① RDP 요청       │                  │                  │                  │
       ├─────────────────→│                  │                  │                  │
       │                  │                  │                  │                  │
       │                  │ ② 토큰 발급 요청  │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │                  │                  │                  │
       │                  │ ③ JWT 토큰 응답   │                  │                  │
       │                  │←─────────────────┤                  │                  │
       │                  │                  │                  │                  │
       │                  │ ④ 포워더 생성    │                  │                  │
       │                  │ (localhost:포트)  │                  │                  │
       │                  │                  │                  │                  │
       │                  │ ⑤ mstsc/WinApp   │                  │                  │
       │                  │    실행          │                  │                  │
       │                  │                  │                  │                  │
       │                  │ ⑥ TLS 연결 + JWT │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │                  │                  │                  │
       │                  │                  │ ⑦ Agent Protocol│                  │
       │                  │                  ├─────────────────────────────────────→│
       │                  │                  │ (중계만, API 미호출)                 │
       │                  │                  │                  │                  │
       │                  │                  │                  │ ⑧ Connected()   │
       │                  │                  │                  │←─────────────────┤
       │                  │                  │                  │   (Server Agent가│
       │                  │                  │                  │    직접 호출)    │
       │                  │                  │                  │                  │
       │                  │                  │ ⑨ RDP 패킷 중계 │                  │
       │                  │←───────────────→ │ ←──────────────────────────────────→│
       │                  │                  │                  │                  │
       │                  │ ⑩ RDP 화면       │                  │                  │
       │                  │                  │                  │                  │
```

### 6.2 Server Agent 미설치 시 (상세)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│Chrome WebView│   │ Multi-Agent  │   │    ARiSA     │   │    API       │   │ Windows RDP  │
│              │   │              │   │              │   │              │   │ (3389 직접)  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │                  │                  │
       │ ① RDP 요청       │                  │                  │                  │
       ├─────────────────→│                  │                  │                  │
       │                  │                  │                  │                  │
       │                  │ ② 토큰 발급      │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │←─────────────────┤                  │                  │
       │                  │                  │                  │                  │
       │                  │ ③ TLS 연결 + JWT │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │                  │                  │                  │
       │                  │                  │ ④ Connected()   │                  │
       │                  │                  ├─────────────────→│                  │
       │                  │                  │  (ARiSA가        │                  │
       │                  │                  │   직접 호출)     │                  │
       │                  │                  │                  │                  │
       │                  │                  │ ⑤ 3389 직접 연결│                  │
       │                  │                  ├─────────────────────────────────────→│
       │                  │                  │                  │                  │
       │                  │                  │ ⑥ RDP 패킷 중계 │                  │
       │                  │←───────────────→ │ ←──────────────────────────────────→│
       │                  │                  │                  │                  │
```

### 6.3 설치 vs 미설치 차이점

| 항목 | Server Agent 설치 | Server Agent 미설치 |
|------|------------------|---------------------|
| 연결 대상 포트 | 13389 (Server Agent) | 3389 (Windows RDP) |
| Connected() 호출 | Server Agent | ARiSA |
| 중계 주체 | Server Agent (Agent Protocol) | ARiSA (직접 연결) |
| 세션 기록 | Server Agent 측 | ARiSA 측 |

---

## 7. 세션 종료 흐름

### 7.1 Server Agent 설치 시

```
1. 사용자가 RDP 세션 종료 (로그오프 또는 연결 끊기)
2. Server Agent → API: Disconnected() 호출
3. API: 세션 종료 로그 저장, 녹화 파일 완료 처리
4. ARiSA: 스트림 종료 (API 호출 없음)
5. Multi-Agent: TunnelForwarder 종료
```

### 7.2 Server Agent 미설치 시

```
1. 사용자가 RDP 세션 종료
2. ARiSA → API: Disconnected() 호출
3. API: 세션 종료 로그 저장
4. Multi-Agent: TunnelForwarder 종료
```

---

## 8. 포트 및 보안

### 8.1 주요 포트 (상세)

| 컴포넌트 | 포트 | 프로토콜 | 용도 |
|---------|------|---------|------|
| Server Agent | 13389 | TLS | RDP + API + Gateway (단일 포트) |
| Windows RDP | 3389 | TCP | 네이티브 RDP (Server Agent 미설치 시) |
| Gateway | 설정값 | TCP | 클라이언트 수신 |
| NOVAS | 22 | SSH | Nova SSH 서버 |
| NOVAS | 9090 | HTTP | Nova REST API |
| SSH JumpHost | 22 | SSH | 점프 호스트 |

### 8.2 보안 특성 (상세)

| 구간 | 암호화 | 인증 |
|------|--------|------|
| Multi-Agent ↔ ARiSA | TLS | JWT 토큰 |
| ARiSA ↔ Server Agent | TLS + Agent Protocol | JWT 토큰 |
| Gateway ↔ Server Agent | TLS + Gateway Protocol | ALPN 기반 라우팅 |
| Gateway ↔ JumpHost | SSH | 패스워드/개인키 |
| NOVAC ↔ NOVAS | SSH | Ed25519 키 검증 + 토큰 |
| ARiSA ↔ NOVAS | HTTP CONNECT | X-NOVA-TAGS 헤더 |

---

## 9. 문제 해결 참조

### 9.1 증상별 확인 포인트 (상세)

| 증상 | 관련 컴포넌트 | 확인 포인트 |
|------|-------------|------------|
| Activate 실패 | API, Server Agent | 13389 인바운드 허용 여부, 터널 상태 |
| Heartbeat 미수신 | Server Agent, API | 서비스 상태, 네트워크 연결, HubUrl 설정 |
| 업데이트 실패 | Server Agent | 인증서 검증, 파일 락, 임시 폴더 권한 |
| RDP 연결 실패 | ARiSA, Server Agent | 토큰 유효성, TLS 핸드셰이크, ALPN |
| 느린 연결 | Gateway, Nova | 터널 경로 수, 지연 시간 |
| Relay Channel 타임아웃 | Gateway | 5초 내 Relay TCP 연결 필요 |
| Nova 세션 없음 | NOVAC, NOVAS | NOVAC 실행 상태, Redis 등록 |
| SSH 연결 실패 | Gateway | JumpHost 인증정보, 네트워크 |
| Tags 매칭 실패 | Nova | X-NOVA-TAGS 헤더, NOVAC_TAGS 설정 |

상세한 증상별 진단은 [diagnose/SKILL.md](../diagnose/SKILL.md)를 참조하세요.

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2025-01-21 | 3.3 UnicastAddresses 배열과 접근 가능한 호스트 검증 섹션 추가 |
| 2025-01-19 | 초기 문서 생성 - DELETED_CONTENT.md에서 흐름 상세 내용 복원 |
