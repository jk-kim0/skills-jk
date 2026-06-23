# RDP 접근제어 시스템 아키텍처

QueryPie의 RDP 기반 Windows Server 접근제어 시스템의 전체 아키텍처와 핵심 개념을 설명합니다.

> **상세 참조**
> - Server Agent 구현 상세: [SERVER-AGENT.md](SERVER-AGENT.md)
> - 네트워크 컴포넌트: [NETWORK.md](NETWORK.md)
> - 용어 정의: [GLOSSARY.md](GLOSSARY.md)

---

## 1. 시스템 개요

QueryPie의 RDP 접근제어는 사용자 PC와 Windows Server 사이에 여러 컴포넌트를 배치하여 **인증, 권한 검사, 세션 감사, 명령어 로깅**을 수행합니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              사용자 환경                                     │
│  ┌────────────────────┐    ┌─────────────────────┐                          │
│  │  RDP 클라이언트     │ ←→ │  Client Agent       │                          │
│  │ (mstsc/Windows App)│    │  (Multi-Agent)      │                          │
│  └────────────────────┘    │  + Chrome WebView   │                          │
│                            └──────────┬──────────┘                          │
└───────────────────────────────────────│─────────────────────────────────────┘
                                        │ TLS + Agent Protocol
                                        ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QueryPie 인프라                                    │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       ARiSA Proxy Server                              │  │
│  │  ┌────────────────┐  ┌──────────────┐  ┌─────────────────────┐       │  │
│  │  │ Agent Listener │→ │ WinSACProxy  │→ │ gRPC API Client     │       │  │
│  │  └────────────────┘  └──────────────┘  │ (서버에이전트 미설치 시)│       │  │
│  │                                        └──────────┬──────────┘       │  │
│  └───────────────────────────────────────────────────│───────────────────┘  │
│                                                      │                       │
│  ┌───────────────────────────────────────────────────↓───────────────────┐  │
│  │                     Policy Server (API)                               │  │
│  │  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐           │  │
│  │  │ 정책 관리    │  │ 세션 관리        │  │ 감사 로그      │           │  │
│  │  └─────────────┘  └──────────────────┘  └────────────────┘           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────────────────┐    │
│  │        Gateway             │  │           Nova                     │    │
│  │ (Direct/SSH Multi-hop)     │  │  (Reverse Tunnel)                  │    │
│  └────────────────────────────┘  └────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │ TLS + Agent Protocol
                                        ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Windows Server 환경                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Server Agent (WinSAC)                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐              │  │
│  │  │ TLS Router   │→ │ RD Server    │→ │ RDP Forwarder  │              │  │
│  │  └──────────────┘  └──────────────┘  └───────┬────────┘              │  │
│  │                                              │                        │  │
│  │  - Heartbeat 송신 (1분 주기)                                          │  │
│  │  - Connected/Disconnected 호출 (서버에이전트 설치 시)                   │  │
│  └──────────────────────────────────────────────│────────────────────────┘  │
│                                                 │                           │
│  ┌──────────────────────────────────────────────↓────────────────────────┐  │
│  │              Windows RDP Service (포트 3389)                           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 핵심 개념

### 2.1 AgentId vs AgentUuid

Server Agent는 두 가지 식별자를 사용합니다. 상세 설명은 [GLOSSARY.md](GLOSSARY.md#식별자)를 참조하세요.

| 식별자 | 생성 주체 | 특징 | 용도 |
|--------|----------|------|------|
| **AgentId** | Server Agent | 하드웨어 기반, 불변 | Heartbeat 수신 시 조회 |
| **AgentUuid** | API 서버 | Activate 시 할당 | Server 매핑, 정책 적용 |

```
설치 직후:  AgentId="a1b2c3d4...", AgentUuid=null, 상태=WAITING_FOR_ACTIVATION
Activate 후: AgentId="a1b2c3d4...", AgentUuid="550e8400-...", 상태=HEALTHY
```

### 2.2 Activate (활성화)

**Server Agent를 QueryPie 시스템에 등록하는 과정**입니다. API가 Server Agent에 AgentUuid를 할당합니다.

**왜 필요한가?** Server Agent가 설치되었다고 해서 바로 사용할 수 있는 것이 아닙니다. API 서버가 Server Agent를 인식하고 AgentUuid를 할당해야 정책 적용, Server 매핑 등이 가능합니다.

```
┌──────────────┐                ┌──────────────┐                ┌──────────────┐
│ Server Agent │                │     API      │                │    Admin     │
└──────┬───────┘                └──────┬───────┘                └──────┬───────┘
       │                               │                               │
       │ ① Heartbeat (AgentUuid=null) │                               │
       ├──────────────────────────────→│                               │
       │                               │ ② 신규 등록                   │
       │                               │   (WAITING_FOR_ACTIVATION)   │
       │                               │                               │
       │                               │ ③ 관리자가 Activate 클릭     │
       │                               │←──────────────────────────────┤
       │                               │                               │
       │   ④ POST /api/activate       │                               │
       │←──────────────────────────────┤ (AgentUuid 전달)              │
       │                               │                               │
       │ ⑤ AgentUuid 레지스트리 저장   │                               │
       │                               │                               │
       │ ⑥ 다음 Heartbeat (AgentUuid=값)                              │
       ├──────────────────────────────→│ ⑦ 상태: HEALTHY               │
```

**Activate 실패 원인**:
- 방화벽에서 Server Agent (13389 포트) 인바운드 차단
- Gateway/Nova 터널이 아직 수립되지 않음
- Server Agent 서비스가 시작되지 않음

### 2.3 Heartbeat vs Heartbeat Scan

| 구분 | Heartbeat | Heartbeat Scan |
|------|-----------|----------------|
| **방향** | Server Agent → API (아웃바운드) | API → Server Agent (인바운드) |
| **주체** | Server Agent가 전송 | API가 요청 |
| **주기** | 1분 | Quartz Job 스케줄 |
| **용도** | 정상 상태 보고 | 상태 확인, 신규 발견 |

**두 가지가 필요한 이유**: 아웃바운드가 차단된 환경에서는 Heartbeat Scan으로 Server Agent를 발견합니다.

### 2.4 Server Agent 상태

| 상태 | 의미 |
|------|------|
| **HEALTHY** | Heartbeat 정상 수신 |
| **OFFLINE** | Heartbeat 5분 이상 미수신 |
| **WAITING_FOR_ACTIVATION** | 신규 설치, AgentUuid 미할당 |

```
WAITING_FOR_ACTIVATION ──(Activate)──→ HEALTHY ←──(Heartbeat)──→ OFFLINE
```

**주의**: OFFLINE에서 Heartbeat 재수신 시 바로 HEALTHY로 복귀합니다.

---

## 3. 핵심 컴포넌트

### 3.1 Client Agent (Multi-Agent)

**위치**: `apps/multi-agent` | **언어**: C# (.NET)

사용자 PC에서 실행되어 로컬 RDP 클라이언트와 ARiSA 프록시 사이를 중개합니다.

**핵심 기능**:
- Chrome WebView로 UI 렌더링
- 로컬 포트 포워딩 (localhost:임의포트 → ARiSA)
- JWT 토큰 발급 요청 및 인증 처리
- RDP 파일(.rdp) 생성 및 RDP 클라이언트 실행

**플랫폼별 RDP 클라이언트**:
| 플랫폼 | 클라이언트 | 비고 |
|--------|-----------|------|
| Windows | `mstsc.exe` | 기본 원격 데스크톱 연결 |
| macOS | `Windows App` | 구 Microsoft Remote Desktop |

**연결 흐름**:
```
1. Chrome WebView에서 RDP 연결 요청
2. TunnelForwarder 생성 (localhost:랜덤포트 수신)
3. RDP 파일 생성 (full address:s:localhost:포트)
4. mstsc.exe 또는 Windows App 자동 실행
5. RDP 클라이언트 → TunnelForwarder → ARiSA
```

**주요 클래스**:
| 클래스 | 파일 | 역할 |
|--------|------|------|
| `ThirdPartyController` | `Api/WebToApp/V3/Controllers/` | RDP 요청 API 엔드포인트 |
| `RDPService` | `Core/Services/Sac/ThirdParty/RDP/` | 터널 생성 및 클라이언트 실행 |
| `TunnelForwarder` | `Core/Tunnel/Forwarder/` | 로컬 포트 → 원격 포워딩 |
| `TunnelConnection` | `Core/Tunnel/Connection/` | TLS + 핸드셰이크 처리 |

### 3.2 ARiSA Proxy Server

**위치**: `apps/arisa` | **언어**: C# (.NET)

Client Agent와 Server Agent 사이의 RDP 프록시입니다.

**핵심 기능**:
- Agent Protocol을 통한 클라이언트 연결 수락 및 인증
- TLS 터널링 또는 Plain TCP 중계
- 정책 서버(API)와 gRPC 통신

**주요 클래스**:
| 클래스 | 파일 | 역할 |
|--------|------|------|
| `AgentConnectionListener` | `ARiSA.Framework/Agent/` | Agent 연결 수신 |
| `AgentProxyConnection` | `ARiSA.Framework/Agent/` | 연결 정보 래핑 |
| `WinSACProxy` | `Modules/ARiSA.WinSAC/` | RDP 프록시 팩토리 |
| `WinSACProxySession` | `Modules/ARiSA.WinSAC/` | RDP 세션 관리 |
| `GrpcApiClient` | `Modules/ARiSA.WinSAC/Api/Grpc/` | 정책 서버 통신 |

#### UseServerAgent 플래그

| 조건 | 호출 주체 | 동작 |
|------|----------|------|
| **서버에이전트 설치** (`UseServerAgent=true`) | Server Agent | ARiSA는 중계만, Server Agent가 API 호출 |
| **서버에이전트 미설치** (`UseServerAgent=false`) | ARiSA | ARiSA가 3389 직접 연결 + API 호출 |

**서버에이전트 미설치 시 (Protocol-less 모드)**:
```csharp
// WinSACProxySession.cs
if (Forward is StreamingProxyConnection forward)
{
    var response = SendConnected();  // ← ARiSA가 직접 Connected API 호출
    _serverCredentials = new GrpcServerCredentials(response.ServerToken, ...);

    // 직접 스트림 복사로 RDP 프로토콜 핸들링
    await localStream.CopyToAsync(forwardStream, cancellationToken);
}
```

**서버에이전트 설치 시 (Agent Protocol 모드)**:
```csharp
// WinSACProxySession.cs
// ARiSA는 Connected/Disconnected 호출 없이 중계만 수행
// Server Agent의 TunnelConnection.LinkAsync()로 위임
await agentProtocolForward.Inner.LinkAsync(...);
```

**Agent Protocol 핸드셰이크**:
```
Client Agent                      ARiSA
    │                               │
    ├─── TCP + TLS 연결 ───────────→│
    │                               │
    ├─── Agent Protocol Frame ─────→│
    │    (User, Auth, Route, Sac)   │
    │                               │
    │←──── JWT 검증 완료 ────────────│
    │                               │
    │←─── RDP 패킷 중계 시작 ────────→│
```

### 3.3 Server Agent (WinSAC)

**위치**: `apps/winsac` | **언어**: C# (.NET)

Windows Server에 설치되어 RDP 접근을 제어하고 감사합니다.

**핵심 기능**:
- Heartbeat 송신 (1분 주기)
- ARiSA 또는 Gateway와 TLS/Agent Protocol 통신
- RDP 세션 중개 (로컬 RDP 서비스 ↔ ARiSA)
- 사용자 이벤트 모니터링 (키 입력, 마우스, 프로세스)
- Connected/Disconnected 호출

> **상세**: [SERVER-AGENT.md](SERVER-AGENT.md)

### 3.4 Policy Server (API)

**위치**: `apps/api` | **언어**: Kotlin (Spring Boot)

중앙 정책 관리 및 세션/감사 로그 저장을 담당합니다.

**세션 정보 수집 아키텍처**:
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │ ←──→ │    ARiSA    │ ←──→ │ Server Agent│
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            │ 세션 이벤트
                            ▼
                     ┌─────────────┐
                     │    Redis    │ ← 실시간 세션 상태 저장
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │     API     │ ← Redis에서 세션 목록 조회
                     └─────────────┘
```

**주요 API 엔드포인트**:
| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/server-agent/heart-beat` | PUT | Heartbeat 수신 |
| `/api/server-agent/check-can-connect` | GET | 접근 가능 여부 확인 |
| `/api/server-agent/credential` | GET | 계정 자격증명 조회 |
| `/api/server-agent/credential-test-connection/{token}` | GET | 테스트 연결용 자격증명 조회 |
| `/api/server-agent/connected` | POST | 세션 시작 리포팅 |
| `/api/server-agent/connection-failed` | POST | 연결 실패 리포팅 |
| `/api/server-agent/disconnected` | POST | 세션 종료 리포팅 |
| `/api/server-agent/event` | POST | 이벤트 로그 (명령어 등) |

**정책 검증 항목**:
1. 역할 할당 여부
2. IP 제한
3. 프로토콜 허용 (RDP, VNC 등)
4. 시간대/요일 제한
5. OTP(MFA) 필요 여부
6. 계정 잠금 상태

#### Server Agent 데이터 모델

API 서버는 AgentId와 AgentUuid를 다음과 같이 관리합니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  server_agents 테이블                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  uuid (PK)      │ AgentUuid - API가 생성한 UUID                             │
│  agent_id       │ AgentId - 하드웨어 기반 해시 (CHAR(64), UNIQUE)           │
│  computer_name  │ Windows 컴퓨터 이름                                       │
│  system_ip      │ IP 주소 목록                                              │
│  version        │ Server Agent 버전                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:1 매핑
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  server_agent_server_mappings 테이블                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  server_uuid       │ QueryPie Server의 UUID (FK)                            │
│  server_agent_uuid │ AgentUuid (FK)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:1 매핑
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  servers 테이블                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  uuid (PK)      │ Server UUID                                               │
│  name           │ 서버 이름                                                  │
│  host           │ 호스트 주소                                                │
│  os_type        │ WINDOWS / LINUX / ...                                     │
│  rdp_port       │ RDP 포트 (기본 13389)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### AgentId vs AgentUuid 사용 시나리오

**AgentId 사용**:

| 시나리오 | 사용 방식 |
|---------|----------|
| **Heartbeat 수신** | `findByAgentId(agentId)` → 기존 Server Agent 엔티티 조회 |
| **신규 등록 확인** | `existsByAgentId(agentId)` → 중복 여부 확인 |
| **Activate 요청 검증** | `agentId` 비교 → 올바른 머신에 Activate하는지 확인 |

**AgentUuid 사용**:

| 시나리오 | 사용 방식 |
|---------|----------|
| **Server 연결** | `serverAgentServerMappingService.create(serverUuid, agentUuid)` |
| **Server 조회** | `getLinkedServer(agentUuid)` → 연결된 Server 찾기 |
| **정책 적용** | AgentUuid → Server → ServerGroup → 정책 |
| **원격 업데이트** | AgentUuid로 대상 Server Agent 특정 |

**정리**:

| 식별자 | API 서버에서의 역할 | 주요 용도 |
|--------|-------------------|----------|
| **AgentId** | Server Agent **검색 키** | Heartbeat 수신 시 기존 엔티티 조회 |
| **AgentUuid** | Server Agent **참조 키** | Server 매핑, 정책 적용, 원격 관리 |

### 3.5 Gateway & Nova

복잡한 네트워크 환경을 지원하는 컴포넌트들입니다.

| 컴포넌트 | 역할 | 사용 환경 |
|---------|------|----------|
| **Gateway** | SSH 점프 호스트 또는 Direct 연결 | Server Agent에 직접 접근 불가 |
| **Nova** | Reverse SSH Tunnel | 인바운드 완전 차단 |

> **상세**: [NETWORK.md](NETWORK.md)

---

## 4. 통신 프로토콜

### 4.1 Agent Protocol

Client Agent ↔ ARiSA ↔ Server Agent 간 사용됩니다.

- TLS 1.3 암호화
- JWT 토큰 기반 인증
- ConnectionData 구조체로 메타데이터 전달

**ConnectionData 필드**:
```
User: 사용자명, 도메인, OS 정보
Auth: AccessToken, 세션 타임아웃, MFA(OTP)
Route: 대상 UUID, 객체 타입, 소스
Sac: ServerGroupUuid, AccountUuid, ChannelType(RDP), UseServerAgent
```

### 4.2 gRPC (ARiSA ↔ API)

ARiSA가 정책 서버와 통신할 때 사용합니다 (서버에이전트 미설치 시).

**인증 헤더**:
```
Authorization: QueryPie {JWT_ACCESS_TOKEN}
X-QueryPie-Server-Token: {SERVER_TOKEN}
X-Forwarded-For: {CLIENT_IP}
tracekey: {TRACE_KEY}
```

---

## 5. 전체 요청-응답 흐름

### 5.1 RDP 접속 (Server Agent 설치 시)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Chrome WebView│   │ Multi-Agent  │   │    ARiSA     │   │    API       │   │ Server Agent │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │                  │                  │
       │ ① RDP 요청       │                  │                  │                  │
       ├─────────────────→│                  │                  │                  │
       │                  │ ② JWT 토큰 발급  │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │←─────────────────┤                  │                  │
       │                  │                  │                  │                  │
       │                  │ ③ 포워더 생성 + mstsc 실행          │                  │
       │                  │                  │                  │                  │
       │                  │ ④ TLS 연결 + JWT │                  │                  │
       │                  ├─────────────────→│                  │                  │
       │                  │                  │ ⑤ Agent Protocol│                  │
       │                  │                  ├─────────────────────────────────────→│
       │                  │                  │                  │                  │
       │                  │                  │                  │ ⑥ Connected()   │
       │                  │                  │                  │←─────────────────┤
       │                  │                  │                  │                  │
       │                  │                  │ ⑦ RDP 패킷 중계 │                  │
       │                  │←───────────────→ │ ←──────────────────────────────────→│
```

### 5.2 RDP 접속 (Server Agent 미설치 시)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Chrome WebView│   │ Multi-Agent  │   │    ARiSA     │   │    API       │   │ Windows RDP  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │                  │                  │
       │ ①~④ 동일        │                  │                  │                  │
       │                  │                  │                  │                  │
       │                  │                  │ ⑤ Connected()   │                  │
       │                  │                  ├─────────────────→│  (ARiSA가 호출)  │
       │                  │                  │                  │                  │
       │                  │                  │ ⑥ 3389 직접 연결│                  │
       │                  │                  ├─────────────────────────────────────→│
       │                  │                  │                  │                  │
       │                  │                  │ ⑦ RDP 패킷 중계 │                  │
       │                  │←───────────────→ │ ←──────────────────────────────────→│
```

### 5.3 세션 종료 흐름

| 환경 | 흐름 |
|------|------|
| Server Agent 설치 | 사용자 종료 → Server Agent → API: Disconnected() |
| Server Agent 미설치 | 사용자 종료 → ARiSA → API: Disconnected() |

---

## 6. 보안 특성

| 구간 | 암호화 | 인증 |
|------|--------|------|
| Client ↔ ARiSA | TLS 1.3 | JWT AccessToken |
| ARiSA ↔ API | gRPC/TLS | JWT + ServerToken |
| ARiSA ↔ Server Agent | TLS 1.3 | Agent Protocol |

---

## 7. 주요 포트

| 컴포넌트 | 포트 | 프로토콜 | 용도 |
|---------|------|---------|------|
| Server Agent | 13389 | TLS + Agent Protocol | RDP 프록시 수신 |
| Server Agent | 13390 | HTTP | 로컬 관리 API |
| Windows RDP | 3389 | RDP | 실제 RDP 서비스 |
| ARiSA | 설정값 | TLS | Agent 연결 수신 |
| API | 8090 | gRPC/HTTPS | 정책 서버 |

> Gateway, Nova 관련 포트는 [NETWORK.md](NETWORK.md) 참조

---

## 8. 소스코드 위치 요약

| 컴포넌트 | 경로 | 언어 |
|---------|------|------|
| Client Agent | `apps/multi-agent` | C# |
| ARiSA Proxy | `apps/arisa` | C# |
| Server Agent | `apps/winsac` | C# |
| Policy Server | `apps/api` | Kotlin |
| Gateway | `apps/gateway` | C# |
| Nova | `apps/nova` | Go |

---

## 9. 관련 문서

| 문서 | 내용 |
|------|------|
| [SERVER-AGENT.md](SERVER-AGENT.md) | Server Agent 내부 아키텍처, 이벤트 수집, API, 유지보수 |
| [NETWORK.md](NETWORK.md) | Gateway, Nova, 네트워크 구성 시나리오 |
| [GLOSSARY.md](GLOSSARY.md) | 용어집 |
