# Server Agent (WinSAC) 상세

Windows Server에 설치되어 RDP 접근을 제어하고 감사하는 Server Agent(WinSAC)의 상세 구현을 설명합니다.

**위치**: `apps/winsac`
**언어**: C# (.NET)

---

## 1. 내부 아키텍처

Server Agent는 **두 개의 프로세스**로 구성됩니다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Windows Server                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WinSAC.Agent.Service.exe (Windows 서비스, SYSTEM 권한)              │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │  MainService    │  │ TlsRouterService│  │  WebHostService │     │   │
│  │  │  (Heartbeat)    │  │  (TLS+ALPN)     │  │  (HTTP Relay)   │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │ RDServerService │  │ GatewayService  │  │ProcessEventMon. │     │   │
│  │  │  (RDP 세션)      │  │  (Gateway)      │  │ (ETW/WMI/...)   │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │RDSessionMonitor │  │UserEventTransm. │  │   IpcService    │     │   │
│  │  │ (세션 상태 추적)  │  │  (이벤트 전송)   │  │  (Named Pipe)   │     │   │
│  │  └─────────────────┘  └─────────────────┘  └────────┬────────┘     │   │
│  │                                                      │ Named Pipe   │   │
│  └──────────────────────────────────────────────────────┼──────────────┘   │
│                                                         │                  │
│  ┌──────────────────────────────────────────────────────┼──────────────┐   │
│  │  WinSAC.Agent.Client.exe (사용자 세션, 사용자 권한)    │              │   │
│  │                                                      ▼              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │UserEventManager │  │ InputEventMon.  │  │   IpcClient     │     │   │
│  │  │  (이벤트 큐)     │  │ (키보드/마우스)  │  │  (Named Pipe)   │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 프로세스 분리 이유

| 이유 | 설명 |
|------|------|
| **권한 분리** | Service는 SYSTEM 권한 (TLS, RDP 중개), Client는 사용자 권한 (입력 캡처) |
| **보안** | 사용자가 Client 프로세스를 종료해도 Service는 계속 동작 |
| **입력 캡처** | 키보드/마우스 Hook은 사용자 세션에서만 가능 |

### Client 프로세스 생명주기

```csharp
// Service가 RDP 세션 활성화 시 Client 프로세스 생성
var startInfo = new UserProcessStartInfo {
    FileName = "WinSAC.Agent.Client.exe",
    ArgumentList = { clientId, processToken }  // 인증 토큰 전달
};
session.StartProcess(startInfo);
```

**Client 프로세스 보호 (DACL 설정)**:
- Local System: 모두 허용
- 세션 사용자: 종료/우선순위 변경 등 차단
- Everyone: 모두 차단

### IPC 통신 (Named Pipe over HTTP)

```
┌─────────────────┐                    ┌─────────────────┐
│  Client.exe     │                    │  Service.exe    │
│                 │                    │                 │
│  HttpClient     │───Named Pipe──────→│  IpcService     │
│  (IpcClient)    │  (querypie-xxx)    │  (Kestrel)      │
│                 │                    │                 │
│  - AuthorizeClient (인증)            │                 │
│  - NotifyKeyboardEvent               │                 │
│  - NotifyMouseEvent                  │                 │
└─────────────────┘                    └─────────────────┘
```

Pipe 이름: `UniqueUtility.Create(Environment.MachineName)` (머신별 고유)

**왜 Named Pipe에 HTTP를 얹었는가?**
- **Kestrel 재사용**: ASP.NET Core의 HTTP 파이프라인을 그대로 사용 (별도 IPC 프로토콜 구현 불필요)
- **개발 생산성**: 기존 HTTP 컨트롤러/미들웨어 패턴 활용
- **디버깅 용이**: HTTP 요청/응답 형식으로 로깅 가능

---

## 2. 주요 서비스

| 서비스 | 파일 | 역할 |
|--------|------|------|
| `MainService` | `Services/` | Heartbeat 송신 및 상태 관리 |
| `TlsRouterService` | `Services/TlsRouter/` | TLS + ALPN 라우팅 |
| `GatewayService` | `Services/QueryPie/` | Gateway 연결 관리 |
| `RDServerService` | `Services/RdServer/` | RDP 세션 처리 |
| `RDProxy` | `Services/RemoteDesktopServer/Proxy/` | FreeRDP 프록시 관리 |
| `WebHostService` | `Services/` | HTTP API 서버 |
| `ProcessEventMonitorService` | `Services/` | 프로세스 이벤트 수집 |
| `UserEventTransmissionService` | `Services/` | 이벤트 API 전송 |

---

## 3. TLS Router (포트 13389)

Server Agent는 **13389 포트** 하나로 여러 프로토콜을 처리합니다. TLS 핸드셰이크 시 **ALPN**으로 프로토콜을 구분합니다.

```
                           ┌─────────────────────────────────────────────────┐
                           │            Server Agent (WinSAC)                │
                           │                                                 │
[외부: API/ARiSA] ─────────┼─→ [13389 TLS Router]                            │
                           │        │                                        │
                           │        ├─ ALPN: TunnelProtocol → RDServerService│
                           │        │                                        │
                           │        ├─ ALPN: http/1.1 → WebHostService ──────┼─→ [13390 Kestrel]
                           │        │                     (내부 릴레이)        │   (localhost only)
                           │        │                                        │
                           │        └─ ALPN: qpgateway → GatewayService      │
                           │                                                 │
                           └─────────────────────────────────────────────────┘
```

| ALPN 값 | 처리 서비스 | 용도 |
|---------|------------|------|
| `TunnelProtocol` | RDServerService | RDP 세션 (User Agent 연결) |
| `http/1.1` | WebHostService | HTTP API 호출 |
| `qpgateway` | GatewayService | Gateway 연결 |

**이 구조의 장점**:
1. 방화벽 관리 용이: 외부에서 13389 포트 하나만 열면 됨
2. TLS 집중 관리: 인증서, 핸드셰이크를 TLS Router에서 일괄 처리
3. Kestrel 단순화: 순수 HTTP 서버로 동작

> **참고**: 13390 포트는 내부 구현 세부사항. localhost에서만 접근 가능하며, 인스톨러에서 변경 불가.

### TLS 인증서 생성

Windows 버전별 호환성 문제로 복잡한 fallback 체인을 사용합니다.

**문제 배경**: Windows Server 2019 1809에서 런타임 생성 ECDsa 인증서로 TLS 1.3 협상 시 `SEC_E_ALGORITHM_MISMATCH` 오류 발생

**인증서 선택 로직** (`TlsRouterService.CreateTlsHandlerAsync`):

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TLS Handler 선택 흐름                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ 사용자 지정 인증서   │
                   │ 있음?               │
                   └──────────┬──────────┘
                      Yes     │     No
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│ 지정된 인증서 사용     │           │ Self-signed 인증서 생성│
│ TLS 1.2/1.3          │           └───────────┬───────────┘
└───────────────────────┘                       │
                                                ▼
                              ┌─────────────────────────────────┐
                              │ 순차적으로 테스트 (실패 시 다음) │
                              └─────────────────────────────────┘
                                                │
            ┌───────────────────────────────────┼───────────────────────────────────┐
            │                                   │                                   │
            ▼                                   ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐           ┌───────────────────────┐
│ ① ECDsa + Native      │──실패──→  │ ② ECDsa + Native      │──실패──→  │ ③ RSA + Native        │
│    TLS 1.2/1.3        │           │    TLS 1.2 only       │           │    TLS 1.2/1.3        │
└───────────────────────┘           └───────────────────────┘           └───────────────────────┘
                                                                                   │
                                                                                실패
            ┌───────────────────────────────────┼───────────────────────────────────┐
            │                                   │                                   │
            ▼                                   ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐           ┌───────────────────────┐
│ ④ RSA + Native        │──실패──→  │ ⑤ ECDsa + BouncyCastle│──실패──→  │ ⑥ RSA + BouncyCastle  │
│    TLS 1.2 only       │           │    TLS 1.2            │           │    TLS 1.2            │
└───────────────────────┘           └───────────────────────┘           └───────────────────────┘
```

**테스트 방식**: 실제 loopback TLS 연결을 시도하여 핸드셰이크 성공 여부 확인

**인증서 선택 순서 요약**:

| 순서 | 알고리즘 | TLS 버전 | 구현 |
|------|---------|---------|------|
| ① | ECDsa | 1.2/1.3 | Native |
| ② | ECDsa | 1.2 only | Native |
| ③ | RSA | 1.2/1.3 | Native |
| ④ | RSA | 1.2 only | Native |
| ⑤ | ECDsa | 1.2 | BouncyCastle |
| ⑥ | RSA | 1.2 | BouncyCastle |

**BouncyCastle 사용 이유**: .NET 네이티브 TLS 구현이 특정 Windows 버전에서 실패할 때 대체 TLS 스택으로 사용 (TLS 1.2만 지원)

**Self-signed 인증서 스펙**:
```csharp
SubjectName: "CN=*.querypie"
ValidFrom: Now - 1년
ValidTo: Now + 1년
ECDsa: prime256v1 (nistP256) + SHA256
RSA: 2048비트 + SHA256 + PKCS1
```

---

## 4. FreeRDP Proxy

Server Agent는 **FreeRDP 기반의 RDP 프록시**를 사용하여 User Agent(Multi-Agent)로부터 받은 RDP 트래픽을 Windows RDP 서비스로 중계합니다.

### 왜 FreeRDP를 사용하는가?

| 이유 | 설명 |
|------|------|
| **프로토콜 복잡성** | RDP는 인증, 암호화, 가상 채널 등 복잡한 프로토콜. 직접 구현 대신 검증된 오픈소스 사용 |
| **인증 정보 주입** | 사용자가 서버 비밀번호를 모르는 상태에서 접속. FreeRDP Proxy가 자격증명을 자동 주입 |
| **채널 제어** | 클립보드, 오디오, 디바이스 리다이렉션 등 정책에 따라 활성화/비활성화 가능 |
| **보안 협상** | TLS, NLA, RDP Security 등 다양한 보안 모드 협상 처리 |

### RDP 연결 흐름

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              Server Agent (WinSAC)                                │
│                                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐            │
│  │ RDServerService │     │    RDProxy      │     │  freerdp-proxy  │            │
│  │ (TLS 연결 수신)  │     │  (프록시 관리)   │     │   .exe          │            │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘            │
│           │                       │                       │                      │
User Agent ─┼─ TLS(13389) ─────────→│                       │                      │
(Multi-Agent)                       │                       │                      │
│           │ ① Handshake           │                       │                      │
│           │ ② 인증정보 조회 (API)  │                       │                      │
│           │                       │                       │                      │
│           │ ③ 프록시 시작 ─────────────────────────────────→│ (ephemeral port)    │
│           │                       │                       │                      │
│           │ ④ localhost:port 연결 ─────────────────────────→│                      │
│           │                       │                       │                      │
│           │                       │                       │ ⑤ 127.0.0.1:3389 연결│
│           │                       │                       ├─────────────────────→│
│           │                       │                       │        Windows RDP   │
│           │←─────────── RDP 패킷 중계 ─────────────────────→│        Service       │
│           │                       │                       │                      │
└───────────┼───────────────────────┼───────────────────────┼──────────────────────┘
            │                       │                       │
```

### FreeRDP Proxy 설정 (RDProxyConfig)

Server Agent는 매 연결마다 임시 INI 설정 파일을 생성하여 `freerdp-proxy.exe`에 전달합니다.

```ini
[Server]
Host=127.0.0.1
Port={ephemeral}        # 동적 할당된 포트

[Target]
Host=127.0.0.1
Port=3389               # Windows RDP 기본 포트
FixedTarget=true
User={서버계정}
Domain={도메인}
Password={비밀번호}     # API에서 조회한 자격증명

[Channels]
GFX=true                # 그래픽 가속
DisplayControl=true     # 동적 해상도
Clipboard=true          # 클립보드 (정책으로 제어 가능)
AudioInput=true         # 마이크
AudioOutput=true        # 스피커
DeviceRedirection=true  # USB 등 장치
VideoRedirection=true
CameraRedirection=true
RemoteApp=true

[Input]
Keyboard=true           # 키보드 입력 (정책으로 제어 가능)
Mouse=true              # 마우스 입력

[Security]
ServerTlsSecurity=true
ServerNlaSecurity=true
ServerRdpSecurity=true
ClientTlsSecurity=true
ClientNlaSecurity=true
ClientRdpSecurity=true
ClientAllowFallbackToTls=true
```

### FreeRDP 호환성 이슈

특정 Windows RDP 설정에서 FreeRDP가 연결에 실패하는 알려진 이슈가 있습니다.

**문제 조합** (https://github.com/FreeRDP/FreeRDP/issues/11278):

| SecurityLayer | EncryptionLevel | NLA | 결과 |
|---------------|-----------------|-----|------|
| RDP | High | false | ❌ 실패 |
| RDP | Low | false | ❌ 실패 |
| RDP | ClientCompatible | false | ❌ 실패 |
| Negotiated | Low | false | ❌ 실패 |
| 그 외 조합 | - | - | ✅ 성공 |

**Server Agent 대응** (`QPClientForwardConnectionFactory.CheckSystemListenerCompatibility`):
- 연결 시작 전 Windows RDP 설정 확인
- 비호환 설정 감지 시 `NotSupportedException` 반환

### freerdp-proxy.exe 관리

```csharp
// RDProxy.cs
public async ValueTask<Result> StartAsync(CancellationToken cancellationToken)
{
    // 1. 설정 파일 생성
    var configFile = WriteTempProxyConfigFile(config);

    // 2. WinPty로 프로세스 시작 (콘솔 출력 캡처용)
    var process = WinPtyProcess.Start(
        "freerdp-proxy.exe",
        [configFile],
        AppContext.BaseDirectory
    );

    // 3. "Listening on ..." 로그 대기 → 준비 완료
    await WaitForListeningAsync(process);

    // 4. 설정 파일 삭제 (보안: 비밀번호 포함)
    File.Delete(configFile);
}
```

**생명주기**:
- 연결당 하나의 `freerdp-proxy.exe` 프로세스 생성
- 연결 종료 시 프로세스 종료
- ephemeral 포트 사용으로 포트 충돌 방지

---

## 5. HTTP API 서버

### 엔드포인트

| 엔드포인트 | 메서드 | 인증 | 설명 |
|-----------|--------|------|------|
| `/api/health` | GET | - | 에이전트 상태 조회 (Health Check) |
| `/api/health/rdp` | GET | - | RDP 연결 가능성 검증 (30초 타임아웃) |
| `/api/activate` | POST | - | 에이전트 활성화 (ServerId 설정) |
| `/api/clients/{clientId}` | DELETE | - | 클라이언트 세션 강제 종료 |
| `/api/maintenance/update` | POST | API Key | 원격 업데이트 |
| `/api/maintenance/uninstall` | POST | API Key | 원격 언인스톨 (예약됨) |

### Health Check 응답

```json
{
  "agentId": "머신 ID",
  "agentUuid": "서버 UUID",
  "status": "HEALTHY",
  "version": "11.5.1",
  "osVersion": "Windows Server 2019",
  "computerName": "WIN-SERVER",
  "unicastAddresses": ["192.168.1.100"],
  "requireGatewayTunnel": false
}
```

### API Key 인증 (Maintenance API)

```
Headers:
  Date: RFC 1123 형식 (예: "Mon, 20 Jan 2026 12:00:00 GMT")
  X-Api-Key: SHA256(Date + "/" + Secret) → HEX 문자열

Secret: "7ac5337f-f220-4acb-8b8b-c548418aabfb" (API와 Server Agent 공유)
```

---

## 6. 이벤트 수집 및 전송

### 이벤트 종류

| 이벤트 | 수집 위치 | 수집 방식 |
|--------|----------|----------|
| 키보드 입력 | Client | Raw Input API (`RawKeyboardEventMonitor`) |
| 마우스 클릭 | Client | Low-level Hook (`LowLevelMouseEventMonitor`) |
| 프로세스 시작/종료 | Service | ETW / WMI / EventLog / SnapshotDiff |

### 프로세스 이벤트 수집 엔진 (우선순위 순)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ETW           │────→│   WMI           │────→│   EventLog      │────→│  SnapshotDiff   │
│ (권장, 실시간)   │실패 │ (레거시)         │실패 │ (감사 정책 필요) │실패 │ (폴백, 폴링)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

| 엔진 | 설명 |
|------|------|
| **ETW** | 실시간, 가장 효율적. `KernelTraceEventParser.Keywords.Process` 이벤트 구독 |
| **WMI** | `Win32_ProcessStartTrace` / `Win32_ProcessStopTrace` 이벤트 구독 |
| **EventLog** | Security 이벤트 로그에서 프로세스 감사 이벤트 읽기 (감사 정책 활성화 필요) |
| **SnapshotDiff** | 주기적으로 프로세스 목록 스냅샷 비교 (마지막 폴백) |

**왜 이 순서인가?**
| 순서 | 이유 |
|------|------|
| ETW 1순위 | 커널 레벨 이벤트 → 가장 빠르고 누락 없음 |
| WMI 2순위 | 유저 모드지만 이벤트 기반 → ETW 다음으로 효율적 |
| EventLog 3순위 | 관리자가 감사 정책 설정해야 동작 → 환경 의존 |
| SnapshotDiff 4순위 | 폴링 방식(주기적 비교) → CPU 부하, 이벤트 누락 가능 |

**폴백 발생 조건**: 상위 엔진 초기화 실패 시 (권한 부족, API 미지원 등)

### 이벤트 흐름

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    Service.exe                                      │
│                                                                                     │
│  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐     │
│  │ ProcessEvent    │          │QPClientUserEvent│          │UserEventTransm. │     │
│  │ MonitorService  │─프로세스→│    Handler      │─Channel─→│    Context      │     │
│  │ (ETW/WMI/...)   │  이벤트  │                 │          │                 │     │
│  └─────────────────┘          └────────┬────────┘          └────────┬────────┘     │
│                                        │                            │              │
│                                        │ 키보드/마우스              │ 2초 주기     │
│  ┌─────────────────┐                   │ (IPC로 수신)               │ 배치 전송    │
│  │    IpcService   │───────────────────┘                            │              │
│  │  (Named Pipe)   │                                                ▼              │
│  └────────▲────────┘                                    ┌─────────────────┐        │
│           │                                             │  QPApiClient    │        │
│           │ Named Pipe                                  │ POST /api/      │        │
│           │                                             │ server-agent/   │────────│───→ API
│           │                                             │ event           │        │
└───────────┼─────────────────────────────────────────────┴─────────────────┴────────┘
            │
┌───────────┼─────────────────────────────────────────────────────────────────────────┐
│           │                         Client.exe                                      │
│           │                                                                         │
│  ┌────────┴────────┐          ┌─────────────────┐          ┌─────────────────┐     │
│  │    IpcClient    │←─────────│ UserEventManager│←─────────│InputEventMonitor│     │
│  │  (Named Pipe)   │   이벤트 │    (큐)         │   Hook   │ (키보드/마우스)  │     │
│  └─────────────────┘   전달   └─────────────────┘   이벤트 └─────────────────┘     │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 전송 로직 (`UserEventTransmissionService`)

```csharp
// 2초마다 실행
while (!stoppingToken.IsCancellationRequested)
{
    await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);

    // 채널에서 이벤트 읽기 (최대 100개)
    Event[] events = channel.ReadAll().Take(100).ToArray();

    // API로 전송
    await apiClient.AddEventAsync(credential, new AddEventRequest { EventList = events });

    // 실패 시 최대 10회 재시도, 초과 시 로그에 덤프 후 폐기
}
```

### 이벤트 데이터 포맷

```json
{
  "timestamp": 1705651200000,
  "type": "KEY_PRESS | MOUSE_CLICK | MOUSE_DOUBLE_CLICK | PROCESS_START | PROCESS_STOP",
  "data": "포맷된 이벤트 데이터"
}
```

---

## 7. Heartbeat

### Heartbeat 데이터

```csharp
HeartBeat {
    AgentId: 머신 ID (고유)
    AgentUuid: 서버 UUID (Registry 저장)
    Status: HEALTHY | DEGRADED | UNHEALTHY | STARTING
    Version: 에이전트 버전
    OSVersion: Windows OS 버전
    ComputerName: 컴퓨터명 (15자)
    UnicastAddresses: List<String>  // 모든 NIC의 IPv4 주소 배열
    RdpPort: 13389 (기본값)
    RequireGatewayTunnel: Gateway 터널 필요 여부
}
```

> **Note**: `UnicastAddresses`는 배열입니다. 여러 NIC가 있는 서버는 여러 IP를 전송합니다.
> API는 이 배열에서 **실제 접근 가능한 호스트를 검증**하여 `manualHost`로 저장합니다.
> 상세 내용은 [arch-flows-deep-dive.md#33-unicastaddresses](./arch-flows-deep-dive.md#33-unicastaddresses-배열과-접근-가능한-호스트-검증)를 참조하세요.

### Heartbeat 흐름

```
┌──────────────┐                 ┌──────────────┐
│ Server Agent │                 │     API      │
└──────┬───────┘                 └──────┬───────┘
       │                                │
       │ PUT /api/server-agent/heart-beat
       ├───────────────────────────────→│  (1분마다)
       │                                │
       │←── 응답 (정책 변경 여부 등) ────│
       │                                │
       │←── Health Check 요청 ──────────│  (API → Server Agent)
       │                                │
       │─── Health Check 응답 ─────────→│
       │                                │
```

---

## 8. 원격 유지보수 API (Maintenance)

Policy Server(API)가 Server Agent를 원격으로 업데이트/언인스톨하기 위한 API입니다.

### POST /api/maintenance/update

**요청 본문**:
```json
{
  "temporaryToken": "인스톨러 다운로드용 임시 토큰",
  "noticeMessage": "Server Agent will be updated after 5 seconds",
  "noticeDuration": 5,
  "installerDownloadURL": "https://querypie.example.com/api/server-agent/internal/download",
  "installerDownloadTimeout": 60,
  "installerFileName": "QueryPie_Server_Access_Control_Setup.exe",
  "installerArguments": ["/Url=...", "/HubUrl=...", "/Port=13389", "/UseHttpProxy=default"]
}
```

### 업데이트 흐름

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   QueryPie UI   │    │    Policy API   │    │  Server Agent   │
└───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘
        │                      │                      │
        │ ① 업데이트 요청       │                      │
        ├─────────────────────→│                      │
        │                      │ ② 상태 검증           │
        │                      │                      │
        │                      │ ③ POST /api/maintenance/update
        │                      ├─────────────────────→│
        │                      │                      │
        │                      │                      │ ④ 인바운드 차단
        │                      │                      │
        │                      │                      │ ⑤ 활성 세션 알림
        │                      │                      │
        │                      │                      │ ⑥ 세션 종료 (30초)
        │                      │                      │
        │                      │                      │ ⑦ 인스톨러 다운로드
        │                      │←─────────────────────│
        │                      │─────────────────────→│
        │                      │                      │
        │                      │                      │ ⑧ 서명 검증
        │                      │                      │
        │                      │                      │ ⑨ 인스톨러 실행
        │                      │                      │   (/VERYSILENT /DELAY=3000)
        │                      │                      │
        │                      │ ⑩ 200 OK             │
        │                      │←─────────────────────│
```

### Server Agent 내부 처리 (ApplicationUpdater)

```csharp
// 1. 작업 디렉토리 생성
_workingDir = Path.Combine(TempDirectory, Path.GetRandomFileName())

// 2. 인스톨러 다운로드
await apiClient.DownloadFileAsync(installerURL, _installerPath)

// 3. 서명 검증 (QueryPie 인증서만 허용)
if (pe.SigningAuthenticodeCertificate.Subject != "QueryPie")
    return Error

// 4. 인바운드 트래픽 차단
tlsRouter.AddInterceptor(DenyInbound)

// 5. 관리중인 세션 종료 + 파일 락 세션 종료
TerminateManagedSessions()
TerminateLockingSessions()

// 6. 인스톨러 실행
Process.Start(installerPath, "/VERYSILENT /SUPPRESSMSGBOXES /NOCANCEL /NORESTART /DELAY=3000")
```

**에러 처리**:
- 타임아웃: 3분 (다운로드 타임아웃 별도)
- 실패 시 자동 롤백: 인바운드 트래픽 다시 허용
- 상태 추적: `UPDATE_WAIT → UPDATING → UPDATE_COMPLETED/UPDATE_FAILED`

### POST /api/maintenance/uninstall

Server Agent를 원격으로 언인스톨합니다.

**요청 본문**:
```json
{
  "noticeMessage": "Server Agent가 5초 후 삭제됩니다",
  "noticeDuration": 5
}
```

**처리 흐름**:
1. `unins000.exe` 존재 확인
2. 인바운드 트래픽 차단
3. 관리중인 세션 종료 (메시지 알림 후)
4. 파일 락 세션 종료
5. 언인스톨러 실행: `unins000.exe /VERYSILENT /SUPPRESSMSGBOXES /DELAY=3000 /PASSWORD={DeletionKey}`

> **주의**: 현재 Policy Server(API)에서 이 endpoint를 호출하는 코드는 없습니다. Server Agent 측에서만 구현되어 있으며, 향후 원격 언인스톨 기능 추가 시 사용될 예정입니다.

---

## 9. 설치 옵션

### 인스톨러 옵션

| 옵션 | 레지스트리 키 | 설명 |
|------|-------------|------|
| `/Url=` | `ApiUrl` | QueryPie 웹 URL (**Deletion Key 계산에만 사용**) |
| `/HubUrl=` | `HubUrl` | QueryPie API URL (**모든 API 통신에 사용**) |
| `/Port=` | `Port` | TLS Router 포트 (기본값: 13389) |
| `/UseHttpProxy=` | `UseHttpProxy` | HTTP 프록시 사용 (`true`: 시스템 프록시 사용, `false`: 직접 연결, `default`: 시스템 설정 따름) |

> **주의**: `web_url`(ApiUrl)과 `hub_url`(HubUrl)은 다른 용도입니다. [GLOSSARY.md](GLOSSARY.md#url-설정)를 참조하세요.

**API URL 설정 (QPApiOptionsConfigurator.cs)**:
```csharp
public void Configure(QPApiOptions options)
{
    var apiUrl = ServerAgentConfig.HubUrl;  // ← HubUrl이 실제 API 통신에 사용
    options.Url = apiUrl;
}
```

### 레지스트리 저장 경로

```
HKLM\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent
```

### RequireGatewayTunnel 자동 설정

HubUrl이 `localhost` 또는 `127.0.0.1`을 포함하면 Gateway Relay를 강제로 사용합니다.

```csharp
public static bool RequireGatewayTunnel =>
    HubUrl.Contains("localhost") || HubUrl.Contains("127.0.0.1");
```

---

## 10. Deletion Key (삭제 키)

Server Agent 삭제 시 필요한 키입니다. 무단 삭제를 방지합니다.

### 생성 알고리즘

```csharp
var domain = ServerAgentConfig.ApiUrl;  // web_url 사용
var date = DateTimeOffset.UtcNow.ToString("yyyyMMdd");
var input = Encoding.Unicode.GetBytes(domain + '/' + date + '/' + secret);
var output = SHA256.HashData(input);
// 결과: "c44f-4439-afbf" 형식
```

**특징**:
- 매일 갱신됨 (날짜 기반)
- `web_url`(ApiUrl)이 포함되어 설치 환경별로 고유
- QueryPie 관리 콘솔에서 조회 가능

### 삭제 프로세스

```
1. 삭제 요청 → Deletion Key 입력 UI 표시
2. 입력된 키와 생성된 키 비교
3. 일치 → 서비스 중지, 방화벽 규칙 삭제, 언인스톨 진행
   불일치 → "Invalid Deletion Key" 에러, 삭제 취소
```

---

## 11. Test Connection

서버 연결 전 사전 테스트를 수행하는 기능입니다.

### 테스트 흐름

```
PreparingAsync
  ├─> CheckCanConnectAsync (10초 타임아웃)
  │   └─> 접속 권한 검사
  ├─> LoadCredentialAsync
  │   └─> 윈도우 계정 정보 로드
  ├─> CheckCredential
  │   └─> 계정 유효성 검사
  └─> LockConnectionAsync
      └─> 동시 접속 제어 (3초 Lock timeout)

ActiveAsync (연결 성공)
  └─> SendConnectedAsync

ErrorAsync (연결 실패)
  └─> SendConnectionFailedAsync
```

### 관련 API

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/server-agent/check-can-connect` | 연결 가능 여부 확인 |
| `GET /api/server-agent/credential-test-connection/{token}` | 테스트용 자격증명 조회 |
| `POST /api/server-agent/connection-failed` | 연결 실패 보고 |

---

## 12. 주요 클래스 참조

| 클래스 | 파일 | 역할 |
|--------|------|------|
| `MainService` | `Services/` | Heartbeat 송신 및 상태 관리 |
| `TlsRouterService` | `Services/TlsRouter/` | TLS + ALPN 라우팅 |
| `GatewayService` | `Services/QueryPie/` | Gateway 연결 관리 |
| `RDServerService` | `Services/RemoteDesktopServer/` | RDP 세션 처리 |
| `RDClient` | `Services/RemoteDesktopServer/Client/` | RDP 상태 머신 |
| `RDProxy` | `Services/RemoteDesktopServer/Proxy/` | FreeRDP 프록시 프로세스 관리 |
| `RDProxyConfig` | `Services/RemoteDesktopServer/Proxy/` | FreeRDP 설정 (INI 생성) |
| `QPClientForwardConnectionFactory` | `Services/QueryPie/RemoteDesktopClient/` | 프록시 연결 팩토리 |
| `QPApiClient` | `Services/QueryPie/Api/` | 정책 서버 API 클라이언트 |
| `QPClientHandler` | `Services/QueryPie/RemoteDesktopClient/` | RDP 연결 라이프사이클 |
| `ApplicationUpdater` | `Services/Maintenance/` | 원격 업데이트 처리 |
