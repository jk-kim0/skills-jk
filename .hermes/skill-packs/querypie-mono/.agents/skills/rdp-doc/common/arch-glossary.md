# 용어집 (Glossary)

RDP 접근제어 시스템에서 사용되는 용어를 정리합니다.

---

## 식별자

### AgentId = MachineId

| 항목 | 설명 |
|------|------|
| **정의** | Windows 머신을 고유하게 식별하는 해시값 |
| **생성 주체** | Server Agent (런타임 계산) |
| **생성 방식** | `SHA256("{MachineName}/{MotherboardSerialNumber}/{PrimaryMacAddress}")` |
| **특징** | 하드웨어 기반, **재설치해도 동일** |
| **용도** | Heartbeat 수신 시 기존 Server Agent 조회 |
| **코드에서** | `agentId`, `machineId` |

### AgentUuid = ServerId

| 항목 | 설명 |
|------|------|
| **정의** | API 서버가 Server Agent에 할당하는 UUID |
| **생성 주체** | Policy API 서버 |
| **저장 위치** | 레지스트리 `HKLM\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent\ServerId` |
| **특징** | Activate 과정에서 할당, 레지스트리에 영구 저장 |
| **용도** | Server 매핑, 정책 적용, 원격 관리 |
| **코드에서** | `agentUuid`, `serverId`, `serverAgentUuid` |

### 두 식별자의 관계

```
┌─────────────────────────────────────────────────────┐
│  설치 직후                                           │
│  AgentId: "a1b2c3d4..." (즉시 생성)                 │
│  AgentUuid: null (미할당)                           │
│  상태: WAITING_FOR_ACTIVATION                        │
└─────────────────────────────────────────────────────┘
                    │ Activate
                    ▼
┌─────────────────────────────────────────────────────┐
│  Activate 후                                         │
│  AgentId: "a1b2c3d4..." (변경 없음)                  │
│  AgentUuid: "550e8400-..." (API가 할당)             │
│  상태: HEALTHY                                       │
└─────────────────────────────────────────────────────┘
```

---

## URL 설정

### web_url = ApiUrl (레지스트리)

| 항목 | 설명 |
|------|------|
| **정의** | QueryPie 웹 URL |
| **용도** | **Deletion Key 계산에만 사용** |
| **주의** | 과거에는 API 통신용이었으나 현재는 미사용 |
| **설치 옵션** | `/Url=...` |

### hub_url = HubUrl (레지스트리)

| 항목 | 설명 |
|------|------|
| **정의** | QueryPie API URL |
| **용도** | **Heartbeat, 정책 조회 등 모든 API 통신** |
| **특이사항** | `localhost` 포함 시 Gateway 강제 사용 |
| **설치 옵션** | `/HubUrl=...` |

### 왜 두 개로 나뉘어 있는가?

**레거시 호환성** 때문입니다.

1. **초기 버전**: `web_url` 하나로 모든 API 통신 수행
2. **아키텍처 변경**: API 엔드포인트가 웹 URL과 분리됨 → `hub_url` 추가
3. **Deletion Key 문제**: 이미 설치된 Agent들의 Deletion Key가 `web_url` 기반으로 계산됨
4. **하위 호환성 유지**: `web_url`을 삭제하면 기존 Agent 삭제 불가 → 유지

결과적으로 `web_url`은 Deletion Key 계산에만 사용되고, 실제 통신은 모두 `hub_url`로 수행합니다.

---

## 컴포넌트 이름

### Client Agent = Multi-Agent

사용자 PC에 설치되는 에이전트. Chrome WebView로 UI를 렌더링하고, 로컬 RDP 클라이언트와 ARiSA 사이를 중개합니다.

- **위치**: `apps/multi-agent`
- **언어**: C# (.NET)

### Server Agent = WinSAC

Windows Server에 설치되는 에이전트. RDP 접근제어, 이벤트 수집을 담당합니다.

- **위치**: `apps/winsac`
- **언어**: C# (.NET)
- **프로세스**: `WinSAC.Agent.Service.exe` (서비스), `WinSAC.Agent.Client.exe` (사용자 세션)

### Policy Server = API

중앙 정책 관리 서버. 세션 관리, 감사 로그 저장을 담당합니다.

- **위치**: `apps/api`
- **언어**: Kotlin (Spring Boot)

---

## 상태 (Status)

### Server Agent 상태

| 상태 | 의미 | 원인 |
|------|------|------|
| **HEALTHY** | 정상 | Heartbeat 정상 수신 |
| **DEGRADED** | 부분 이상 | 일부 기능 제한 |
| **UNHEALTHY** | 비정상 | 오류 발생 |
| **WAITING_FOR_ACTIVATION** | 활성화 대기 | 신규 설치, AgentUuid 미할당 |
| **STARTING** | 시작 중 | 서비스 시작 중 |
| **STOPPING** | 중지 중 | 서비스 종료 중 |
| **OFFLINE** | 오프라인 | Heartbeat 5분 이상 미수신 |
| **NOT_FOUND** | 미발견 | Heartbeat Scan에서 응답 없음 |

### 상태 전이

```
WAITING_FOR_ACTIVATION ──(Activate)──→ HEALTHY
                                          ↑↓ (Heartbeat)
                                       OFFLINE
```

**주의**: OFFLINE에서 Heartbeat 재수신 시 바로 HEALTHY로 복귀 (WAITING_FOR_ACTIVATION 아님)

---

## 통신 관련

### Heartbeat

| 항목 | 설명 |
|------|------|
| **방향** | Server Agent → API (아웃바운드) |
| **주기** | 1분 |
| **엔드포인트** | `PUT /api/server-agent/heart-beat` |
| **용도** | 상태 보고, 정책 변경 확인 |

### Heartbeat Scan

| 항목 | 설명 |
|------|------|
| **방향** | API → Server Agent (인바운드) |
| **주기** | Quartz Job 스케줄 (설정 가능) |
| **엔드포인트** | `GET /api/health` (Server Agent) |
| **용도** | 상태 확인, 신규 Server Agent 발견 |

### Activate

Server Agent를 QueryPie 시스템에 등록하는 과정. API가 Server Agent에 AgentUuid를 할당합니다.

1. Server Agent가 Heartbeat 전송 (AgentUuid=null)
2. API가 신규 Server Agent 등록 (WAITING_FOR_ACTIVATION)
3. 관리자가 콘솔에서 Activate 버튼 클릭
4. API가 Server Agent의 `/api/activate` 호출
5. Server Agent가 AgentUuid 저장
6. 상태가 HEALTHY로 변경

### Connected / Disconnected

RDP 세션 시작/종료를 API에 알리는 호출.

| 조건 | 호출 주체 |
|------|----------|
| Server Agent **설치됨** | Server Agent가 호출 |
| Server Agent **미설치** | ARiSA가 호출 |

---

## 플래그

### UseServerAgent

| 값 | 의미 |
|----|------|
| `true` | Server Agent 설치됨. ARiSA는 중계만, Server Agent가 API 호출 |
| `false` | Server Agent 미설치. ARiSA가 직접 RDP 연결 + API 호출 |

### RequireGatewayTunnel

| 조건 | 값 | 동작 |
|------|----|----|
| HubUrl에 `localhost` 또는 `127.0.0.1` 포함 | `true` | Gateway Relay 강제 |
| 그 외 | `false` | TCP 직접 연결 |

**설계 이유**: 로컬 개발 환경에서도 프로덕션과 동일한 Gateway 연결 경로를 테스트할 수 있도록 보장하기 위함

---

## 네트워크 컴포넌트

### Gateway

SSH 점프 호스트 터널링 또는 Direct 연결을 제공하는 컴포넌트.

- **위치**: `apps/gateway`
- **언어**: C# (.NET)
- **용도**: Server Agent에 직접 접근 불가능한 환경

### Nova

Reverse SSH Tunnel을 통해 인바운드 차단 환경에서 접근을 제공하는 컴포넌트.

- **NOVAS** (Server): 외부에서 SSH 수신 + REST API
- **NOVAC** (Client): 내부에서 SSH 아웃바운드
- **위치**: `apps/nova`
- **언어**: Go

### Control Channel vs Relay Channel

| 구분 | Control Channel | Relay Channel |
|------|----------------|---------------|
| **역할** | 제어 메시지 전달 | 실제 데이터 전송 |
| **수명** | 장기 지속 | 단기 임시 (5초 타임아웃) |
| **용도** | Ping/Pong, Relay 요청 | HTTP 요청, 데이터 포워딩 |

**분리 이유**:
1. **대역폭 효율**: 제어 메시지(작음)와 데이터 전송(큼)을 분리하여 Control Channel이 데이터 트래픽에 막히지 않음
2. **연결 관리 단순화**: Control Channel은 상시 유지, Relay Channel은 필요 시에만 생성/소멸
3. **타임아웃 독립성**: Relay Channel의 짧은 타임아웃(5초)이 Control Channel에 영향 주지 않음
4. **장애 격리**: Relay Channel 실패가 Control Channel에 영향 없음

---

## 프로토콜

### Agent Protocol

Client Agent ↔ ARiSA ↔ Server Agent 간 사용되는 프로토콜.

- TLS 1.3 암호화
- JWT 토큰 기반 인증
- ConnectionData 구조체로 메타데이터 전달

### Gateway Protocol

Gateway ↔ Server Agent 간 사용되는 프로토콜.

| 메시지 | 값 | 용도 |
|--------|---|------|
| ClientHello | 0xFE | 핸드셰이크 시작 |
| ServerHello | 0xFD | 핸드셰이크 응답 |
| Ping/Pong | 0xFA/0xF9 | 연결 유지 (30초) |
| RelayRequest | 0xF7 | 릴레이 채널 요청 |
| RelayResponse | 0xF6 | 릴레이 채널 응답 |

### ALPN (Application-Layer Protocol Negotiation)

TLS 핸드셰이크 시 프로토콜을 구분하는 방식. Server Agent의 TLS Router(13389)에서 사용.

| ALPN 값 | 처리 서비스 | 용도 |
|---------|------------|------|
| `TunnelProtocol` | RDServerService | RDP 세션 |
| `http/1.1` | WebHostService | HTTP API |
| `qpgateway` | GatewayService | Gateway 연결 |

---

## 보안 관련

### Deletion Key

Server Agent 삭제 시 필요한 키. 무단 삭제 방지 목적.

```
생성: SHA256(web_url + '/' + 날짜(yyyyMMdd) + '/' + secret)
결과: "c44f-4439-afbf" 형식
```

- 매일 갱신됨 (날짜 기반)
- QueryPie 관리 콘솔에서 조회 가능

---

## 약어

| 약어 | 풀네임 | 의미 |
|------|--------|------|
| **RDP** | Remote Desktop Protocol | 원격 데스크톱 프로토콜 |
| **SAC** | Server Access Control | 서버 접근 제어 |
| **WinSAC** | Windows Server Access Control | Windows 서버 접근 제어 (Server Agent) |
| **ARiSA** | - | RDP 프록시 서버 |
| **ETW** | Event Tracing for Windows | Windows 이벤트 추적 |
| **WMI** | Windows Management Instrumentation | Windows 관리 도구 |
| **ALPN** | Application-Layer Protocol Negotiation | TLS 프로토콜 협상 확장 |
| **IPC** | Inter-Process Communication | 프로세스 간 통신 |
