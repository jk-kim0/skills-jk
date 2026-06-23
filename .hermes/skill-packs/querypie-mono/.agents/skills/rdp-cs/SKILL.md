---
name: rdp-cs
description: Use when classifying QueryPie RDP customer support symptoms, collecting diagnostics, drafting Jira or Slack responses, and closing RDP support cases.
---

# RDP 증상 진단 체크리스트

> **이 문서의 역할**: CS 대응 시 Codex가 참조하는 **증상 분류** 및 **구간 분석 가이드**.

---

## 1. 증상별 분류 및 체크리스트

> **사용 시점**: 티켓 정보 수집 후 가장 먼저 증상을 분류하고, 해당 체크리스트를 확인합니다.

---

### 1.1 서버에이전트 설치/실행 실패

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "Server Agent 설치가 안 돼요", "서비스가 시작 안 돼요", "설치 후 바로 꺼져요" |
| **화면에서 보이는 것** | services.msc에서 서비스 상태가 "중지됨" 또는 시작 직후 종료 |
| **구분 기준** | Server Agent 서비스 자체가 실행되지 않음 |
| **헷갈리는 케이스** | 1.2(Offline)와 다름: Offline은 서비스는 실행 중이나 통신 실패 |

#### 배경 이해

Server Agent는 Windows 서비스로 동작하며, 시작 시 다음 과정을 거칩니다:
1. 레지스트리에서 Hub URL 등 설정값 로드
2. .NET Runtime 초기화 및 WMI 서비스 연결
3. QueryPie API로 HeartBeat 전송 시작

이 중 하나라도 실패하면 서비스가 시작되지 않거나 즉시 종료됩니다.

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 서비스 상태 | `services.msc` -> QueryPie Server Agent | 미실행/오류 -> 아래 항목 순차 확인 |
| 2 | Hub URL 설정 | 레지스트리: `HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent` | URL 형식 오류 -> 재설치 또는 레지스트리 수정 |
| 3 | 런타임 에러 | PowerShell(관리자)에서 `.\WinSAC.Agent.exe` 직접 실행 | 에러 메시지 확인 -> 로그 수집 |
| 4 | WMI 서비스 | PowerShell: `Get-Service winmgmt` | Stopped -> WINMGMT 서비스 시작 |
| 5 | .NET Framework | 이벤트 뷰어 -> 응용 프로그램 로그 | .NET 에러 -> Framework 재설치 |

#### 관련 티켓

| 티켓 | 원인 | 해결 |
|------|------|------|
| [QCP-3983](https://querypie.atlassian.net/browse/QCP-3983) | WINMGMT 서비스 비정상 | 10.2.14+ 업그레이드 |

---

### 1.2 Offline / Not Found

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "서버가 Offline으로 떠요", "Not Found라고 나와요" |
| **화면에서 보이는 것** | QueryPie 관리자페이지 → Server 목록에서 상태가 **Offline** 또는 **Not Found** |
| **구분 기준** | HeartBeat 미수신 (최근 5분 내 HeartBeat 없음) |
| **헷갈리는 케이스** | 1.3(Connection Failed)과 다름: Connection Failed는 HeartBeat는 성공, Activate만 실패 |

#### 배경 이해

**HeartBeat 메커니즘**:
- Server Agent: **1분 간격** HeartBeat 전송
- QueryPie API: HeartBeat 수신 후 **5분간** Online 유지
- **Offline** = 최근 5분 내 HeartBeat 미수신

**원인 분류**:
| 원인 | 상세 |
|------|------|
| 서비스 미실행 | Server Agent 서비스가 중지됨 |
| 네트워크 문제 | 방화벽, DNS, 라우팅 문제 |
| TLS 실패 | TLS 버전/프로토콜 불일치 |
| Hub URL 오류 | 설치 시 잘못된 URL 입력 |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 서비스 실행 | `services.msc` | 미실행 -> 서비스 시작 |
| 2 | Hub URL | 레지스트리 확인 | URL 오류 -> 재설치 |
| 3 | HeartBeat 로그 | `Failed to HeartBeat` 검색 | 실패 -> 네트워크 체크 |
| 4 | DNS | `nslookup {querypie-domain}` | 실패 -> DNS/hosts 설정 |
| 5 | HTTPS 통신 | `Invoke-WebRequest https://{domain}` | 실패 -> 방화벽/TLS |
| 6 | TLS 에러 | 로그에서 `TLS alert` 검색 | 있음 -> 케이스 D 참조 |

#### 관련 티켓

| 티켓 | 원인 | 해결 | 분류 |
|------|------|------|:----:|
| [QCP-3857](https://querypie.atlassian.net/browse/QCP-3857) | Route53 미등록 | hosts 파일 수정 | 환경 |
| [QCP-4556](https://querypie.atlassian.net/browse/QCP-4556) | TLS 1.2 미활성화 | 케이스 D (TLS 1.2 요구사항 안내) | 환경 |
| [QCP-4336](https://querypie.atlassian.net/browse/QCP-4336) | Custom Listener 누수 | 레지스트리 정리 | 환경 |
| [QCP-4783](https://querypie.atlassian.net/browse/QCP-4783) | HeartBeat 실패 (ResponseEnded) | 환경 문제 | 환경 |

---

### 1.3 Connection Failed

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "Connection Failed라고 떠요", "연결 실패라고 나와요" |
| **화면에서 보이는 것** | QueryPie 관리자페이지 → Server 목록에서 상태가 **Connection Failed** |
| **구분 기준** | HeartBeat 성공 (Server Agent → QueryPie), Activate 실패 (QueryPie → Server Agent) |
| **헷갈리는 케이스** | 1.2(Offline)와 다름: Offline은 HeartBeat 자체가 실패 |
| **추가 확인** | `Last Checked at` 시간이 갱신되는지 확인 → 갱신 O면 TLS 문제, 갱신 X면 방화벽 |

#### 배경 이해

**Connection Failed 의미**:
- Server Agent -> QueryPie: **정상** (HeartBeat 성공)
- QueryPie -> Server Agent: **실패** (Activate 실패)

**역방향 통신** 문제입니다.

**주요 원인**:
| 원인 | 설명 |
|------|------|
| 방화벽 (인바운드) | Windows Server 13389 포트 차단 |
| TLS 실패 | QueryPie -> Server Agent TLS 연결 실패 |
| NAT/라우팅 | QueryPie가 실제 IP에 도달 불가 |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 포트 리슨 | `netstat -ano \| findstr 13389` | LISTEN 없음 -> 서비스 재시작 |
| 2 | TCP 연결 | `Last Checked at` 갱신 여부 | 갱신 O -> TLS, 갱신 X -> 방화벽 |
| 3 | 방화벽 | `telnet {WindowsIP} 13389` | 실패 -> 인바운드 오픈 |
| 4 | TLS | 로그에서 `SSLHandshakeException` | 있음 -> 케이스 A 참조 |

#### 관련 티켓

| 티켓 | 원인 | 해결 | 분류 |
|------|------|------|:----:|
| [QCP-3828](https://querypie.atlassian.net/browse/QCP-3828) | Schannel ALPN 버그 | 10.2.14 핫픽스 | 버그 |
| [QCP-3640](https://querypie.atlassian.net/browse/QCP-3640) | SG 13389 미오픈 | 포트 오픈 | 환경 |

---

### 1.4 RDP 세션 접속 실패

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "접속하면 에러가 나요", "연결이 안 돼요", "접속 시도하면 끊겨요" |
| **화면에서 보이는 것** | 서버 상태는 **Online**인데, 접속 시도 시 에러 모달 또는 즉시 종료 |
| **구분 기준** | Server Agent는 정상, RDP 세션 수립 단계에서 실패 |
| **헷갈리는 케이스** | 1.6(세션 끊김)과 다름: 세션 끊김은 접속 성공 후 사용 중 끊김 |
| **추가 확인** | 에러 코드 확인 (QPS-xxxxx), mstsc 직접 접속 테스트 |

#### 원인 분류

| 분류 | 원인 예시 |
|------|-----------|
| Windows 보안 정책 | CredSSP, NLA, SecurityLayer 설정 |
| 네트워크/보안장비 | IPS 위협탐지, 방화벽 차단 |
| QueryPie 설정 | Security 설정 누락 |
| 클라이언트 문제 | Multi Agent/User Agent 버그 |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 에러 메시지 | 에러 코드 확인 | `QPS-12393` -> Security 설정 |
| 2 | 직접 RDP | mstsc로 직접 접속 | 성공 -> 서버에이전트 문제 |
| 3 | 보안 설정 | gpedit.msc 확인 | NLA/SSL 강제 -> 11.0.0+ 필요 |
| 4 | 세션 로그 | `Client started`->`stopped` 패턴 | 2초 이내 -> 버그 가능성 |
| 5 | Windows 버전 | Windows Server 2025 여부 | 2025 + freeze -> 케이스 H |

### QueryPie 서버 측 확인 (구간 C 문제 의심 시)

> **중요**: 클라이언트/Windows 서버 문제가 아닐 때, QueryPie 서버 측 상태를 반드시 확인

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | ARiSA 프로세스 | QueryPie 서버에서 `ps aux \| grep arisa` | 미실행 -> ARiSA 재시작 |
| 2 | ARiSA 포트 점유 | `netstat -tlnp \| grep 9000` | LISTEN 없음 -> ARiSA 재시작/설정 확인 |
| 3 | Proxy 주소 설정 | Meta DB에서 `SELECT * FROM querypie.proxies` | host 값이 Multi-Agent가 접근 가능한 주소인지 확인 |

**Proxy 주소 설정 / ARiSA 미실행 문제 상세**:
- Multi-Agent가 RDP 접속 시 API에 요청하여 ARiSA 주소를 받아옴
- API는 `querypie.proxies` 테이블의 `host` 값을 응답
- 이 값이 잘못 설정되어 있거나, ARiSA가 9000번 포트를 리스닝하지 않으면 연결 실패

**증상**:
- Server Agent는 Online인데 접속 실패
- mstsc: `0x904` (확장오류 `0x7`)
- macOS/Windows App: `0x204`

**진단 핵심**:
- Multi-Agent 로그: 요청 전송한 흔적 있음
- ARiSA 로그: **요청 수신 흔적 없음** ← 이 불일치가 핵심 단서
- → Multi-Agent → ARiSA 구간에서 연결 자체가 실패했음을 의미

### Server Agent 미설치 환경 (UseServerAgent=false)

> **증상**: mstsc 직접 접속은 성공, QueryPie 경유 시 실패 + Audit log에는 Connection 성공으로 기록

**배경**:
- `Allow RDP Connection without Server Agent` 옵션 Enable 시
- ARiSA가 단순 TCP 프록시 역할 (바이트 포워딩만 수행)
- TLS/NLA/CredSSP 협상은 mstsc와 Windows Server가 직접 수행
- **이론상 mstsc 직접 접속과 동일하게 동작해야 함**

**조사 필요 사항**:

| 순서 | 확인 항목 | 수집 방법 | 목적 |
|:----:|-----------|-----------|------|
| 1 | 에러 모달 상세 | 스크린샷 + 에러 코드 | 실패 원인 특정 |
| 2 | PCAP 비교 | mstsc 직접 vs QueryPie 경유 | TLS 협상 차이 분석 |
| 3 | ARiSA 로그 | Verbose 로그 수집 | 프록시 동작 확인 |
| 4 | RDP 파일 설정 | 생성된 .rdp 파일 내용 | 보안 옵션 확인 |

**관련 티켓**: [QCP-3761](https://querypie.atlassian.net/browse/QCP-3761) (미해결 종료)

---

### 1.5 로그인 실패 (ID/PW)

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "비밀번호가 틀렸다고 나와요", "로그인이 안 돼요" |
| **화면에서 보이는 것** | RDP 화면까지 진입 후 "사용자 이름 또는 암호가 올바르지 않습니다" |
| **구분 기준** | RDP 세션은 수립됨, 인증 단계에서 실패 |
| **헷갈리는 케이스** | 1.4(접속 실패)와 다름: 접속 실패는 로그인 화면 전에 끊김 |
| **추가 확인** | AD 계정 형식 (`user@domain.fqdn` vs `DOMAIN\user`) |

#### AD 계정 형식 주의

| 형식 | 예시 | 지원 |
|------|------|:----:|
| UPN (권장) | `user@domain.local` | O |
| Down-Level | `DOMAIN\user` | X |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 계정 형식 | 입력 형식 확인 | `DOMAIN\user` -> `user@domain.fqdn` |
| 2 | Test Connection | 관리자페이지에서 테스트 | 실패 -> ID/PW 오류 |
| 3 | Agent 버전 | AD 환경이면 버전 확인 | 10.2.4 이하 -> 업그레이드 |

---

### 1.6 세션 끊김/조기 종료

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "사용하다가 갑자기 끊겨요", "5분마다 끊겨요", "Idle timeout 전에 끊겨요" |
| **화면에서 보이는 것** | 접속 성공 후 작업 중 갑자기 연결 종료 |
| **구분 기준** | 세션 수립 성공 후 비정상 종료 (설정된 timeout 이전) |
| **헷갈리는 케이스** | 1.4(접속 실패)와 다름: 접속 실패는 처음부터 연결 안 됨 |
| **추가 확인** | Server Access History에서 종료 사유 확인, 끊기는 시점 패턴 (5분 간격? 랜덤?) |

#### 원인 분류

| 원인 | 특징 |
|------|------|
| Idle Timeout | 정상 동작 |
| mouse->time overflow | 부팅 50일+ 서버 |
| 토큰 갱신 실패 | 5-10분 간격 끊김 |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | 종료 사유 | Server Access History | `Idle timeout` 확인 |
| 2 | 서버 가동 시간 | `(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime` | 50일+ -> overflow 버그 |
| 3 | 마우스 클릭 | Command Audit - MouseClick | 기록 없음 -> overflow 확정 |

#### 관련 티켓

| 티켓 | 원인 | 해결 |
|------|------|------|
| [QCP-4704](https://querypie.atlassian.net/browse/QCP-4704) | mouse->time overflow | 11.5.1+ 업그레이드 |

---

### 1.7 로그/녹화 미저장

#### 증상 판단

| 항목 | 내용 |
|------|------|
| **고객 설명** | "로그가 안 남아요", "녹화가 안 돼요", "Audit에 기록이 없어요" |
| **화면에서 보이는 것** | 세션 종료 후 Audit 페이지에서 로그/녹화 없음 또는 불완전 |
| **구분 기준** | 세션 자체는 정상, 로그/녹화 저장만 실패 |
| **헷갈리는 케이스** | 1.6(세션 끊김)과 다름: 세션 끊김은 세션 자체가 비정상 종료 |

#### 체크리스트

| 순서 | 체크 항목 | 확인 방법 | 판단 기준 |
|:----:|-----------|-----------|-----------|
| 1 | Agent 통신 | `Failed to HeartBeat` 검색 | 실패 -> 네트워크 문제 |
| 2 | API 연결 | 80 포트 통신 테스트 | 실패 -> 포트 오픈 |
| 3 | S3 권한 | S3 연동 상태 확인 | 오류 -> IAM 확인 |

---

### 1.8 기타 증상

위 카테고리에 해당하지 않는 증상:
- **Server Agent 삭제 불가**: apiURL 변경 후 삭제
- **세션 종료 시 로그오프**: 10.2.x 의도된 동작, 11.0.0+ 업그레이드
- **타 솔루션 RDP 불가**: 11.2.0+ 핫픽스
- **Okta MFA 미적용**: 구조적 한계

---

## 2. 구간 분석 가이드

> **핵심 원칙**: 원인을 분석하기 전에 **어떤 구간에서 발생한 문제인지 가장 먼저 파악**한다.

### 2.1 RDP 연결 구간 이해

RDP 세션은 다음 구간을 거칩니다:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Multi-Agent  │ ──→ │    Proxy     │ ──→ │ Server Agent │ ──→ │ freerdp-     │ ──→ │ TermService  │
│   (MA)       │     │   (ARiSA)    │     │    (SA)      │     │ proxy.exe    │     │  (RDP 3389)  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
   클라이언트 PC         QueryPie 서버        Windows Server        Windows Server       Windows Server
```

| 구간 | 설명 | 포트 |
|------|------|------|
| MA → Proxy | Multi-Agent가 ARiSA Proxy에 TLS 연결 | Proxy 리슨 포트 |
| Proxy → SA | Proxy가 Server Agent에 TLS 연결 | **13389** (기본값, 설정에 따라 다름) |
| SA → freerdp-proxy | Server Agent 내부에서 freerdp-proxy.exe 호출 | 내부 통신 |
| freerdp-proxy → TermService | freerdp-proxy가 Windows RDP 서비스에 연결 | **3389** |

**문제 발생 시 어느 구간에서 RST/FIN이 발생했는지 파악해야 원인을 특정할 수 있습니다.**

#### 네트워크 구성별 시나리오

고객 환경에 따라 Gateway, Nova가 추가될 수 있습니다:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        네트워크 접근 방식                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [직접 연결]     MA → Proxy ─────────────────────→ Server Agent     │
│                                                                      │
│  [Gateway]       MA → Proxy → Gateway ──────────→ Server Agent      │
│                                                                      │
│  [Nova]          MA → Proxy → NOVAS ←──(SSH)── NOVAC → Server Agent │
│                                                                      │
│  [Gateway+Nova]  MA → Proxy → Gateway → NOVAS ←─ NOVAC → SA         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| 시나리오 | 사용 환경 | 추가 장애 포인트 |
|---------|----------|-----------------|
| **직접 연결** | Server Agent 인바운드 허용 | - |
| **Gateway** | SSH 점프 호스트 필요 | Gateway, JumpHost |
| **Nova** | 인바운드 완전 차단 | NOVAS, NOVAC |
| **Gateway + Nova** | 다중 보안 구역 + 인바운드 차단 | Gateway, JumpHost, NOVAS, NOVAC |

**Nova 사용 시 주의**: NOVAC은 내부에서 NOVAS로 SSH **아웃바운드** 연결을 맺습니다 (화살표 방향 주의).

> 상세 아키텍처: `rdp-doc` 스킬의 `common/arch-network.md` 참조

### 2.2 로그 존재 여부 체크 (필수)

**분석 전에 반드시 어떤 로그가 있는지 확인합니다.**

| 로그 | 위치 | 확인 가능한 구간 |
|------|------|------------------|
| **Multi-Agent 로그** | `C:\Users\{사용자}\.querypie-multi-agent\logs\` (Windows) / `~/.querypie-multi-agent/logs/` (macOS/Linux) | 클라이언트 측 연결 상태, WebView 에러 |
| **Proxy 로그** | QueryPie 서버: `/var/log/querypie/proxy/proxy.log` | MA → Proxy → SA 구간, RST/FIN 방향 |
| **Server Agent 로그** | Windows Server: `C:\ProgramData\QueryPie\ServerAgent\logs\` | SA → freerdp-proxy → TermService 구간 |

**체크리스트:**

| 순서 | 체크 항목 | 없으면 |
|:----:|-----------|--------|
| 1 | Server Agent 로그 있는가? | 고객에게 요청 (경로: `C:\ProgramData\QueryPie\ServerAgent\logs\`) |
| 2 | Proxy 로그 있는가? | QueryPie 서버에서 수집 |
| 3 | Multi-Agent 로그 있는가? | 클라이언트 PC에서 수집 |

**주의**: 티켓에 첨부된 `log.zip`이 어디서 수집된 로그인지 먼저 확인하세요.
- `api/`, `proxy/`, `engine/`, `nginx/` 폴더가 있으면 → **QueryPie 서버 로그** (Server Agent 로그 아님)
- `novas/` 폴더의 `novas.log`는 **QueryPie 서버의 novas 컴포넌트 로그**이며, Windows Server의 Server Agent 로그가 아닙니다.

### 2.3 Proxy 로그 분석법

Proxy 로그에서 **어느 방향에서 RST/FIN이 발생했는지** 확인합니다.

#### 용어 정의

| 용어 | 의미 | IP 예시 |
|------|------|---------|
| **Local** | Multi-Agent 방향 (클라이언트) | `10.20.201.206:52822` (클라이언트 IP, 임시 포트) |
| **Forward** | Server Agent 방향 | `10.232.22.31:13389` (서버 IP, **13389 포트**) |

**Server Agent 포트(기본값 13389, 설정에 따라 다름)가 있으면 Server Agent 방향입니다.**

#### 에러 메시지 해석

```
[ERR] <WinSac> An error occurred while copying the stream (A to B)
System.IO.IOException: Connection reset by peer.
 SocketException (104): Connection reset by peer
```

- `(A to B)`: A에서 읽어서 B로 쓰는 중 에러 발생
- `Connection reset by peer`: **A가 RST를 던짐**

#### 예시 분석

**예시 1: Server Agent가 RST를 던진 경우**
```
[ERR] <WinSac> An error occurred while copying the stream (10.232.22.31:13389 to 10.20.201.206:52822)
SocketException (104): Connection reset by peer
```
- `10.232.22.31:13389` = Forward = **Server Agent**
- `10.20.201.206:52822` = Local = Multi-Agent
- **해석: Server Agent(13389)에서 읽는 중 RST 발생 → Server Agent가 연결을 끊음**

**예시 2: Multi-Agent가 RST를 던진 경우**
```
[ERR] <WinSac> An error occurred while copying the stream (10.20.201.206:52822 to 10.232.22.31:13389)
SocketException (104): Connection reset by peer
```
- **해석: Multi-Agent에서 읽는 중 RST 발생 → Multi-Agent가 연결을 끊음**

#### 정상 종료 vs 비정상 종료

| 로그 패턴 | 의미 |
|-----------|------|
| `Streaming gracefully completed.` → `Local ... was closed.` → `Forward ... was closed.` | **정상 종료** |
| `[ERR] ... Connection reset by peer` | **비정상 종료** (RST) |
| `[ERR] ... Operation canceled` | **취소됨** (상대방이 먼저 끊은 후 전파) |

#### Proxy 로그로 알 수 없는 것

Proxy 로그만으로는 **Server Agent 내부에서 무슨 일이 있었는지** 알 수 없습니다:
- Server Agent 자체 문제인지?
- freerdp-proxy.exe 문제인지?
- TermService(Windows RDP)가 끊은 건지?

→ **Server Agent 로그가 필요합니다.**

### 2.4 Server Agent 로그 분석법

Server Agent 로그에서 **내부 구간별 상태**를 확인합니다.

#### 구간별 로그 키워드

| 구간 | 정상 로그 | 에러 로그 |
|------|----------|----------|
| MA → SA 수신 | `Client connected`, `TLS handshake completed` | `TLS alert`, `Connection refused` |
| SA → freerdp-proxy | `Starting freerdp-proxy`, `freerdp-proxy started` | `freerdp-proxy failed`, `freerdp-proxy crashed` |
| freerdp-proxy → TermService | `RDP connection established` | `RDP connection failed`, `CredSSP error` |

#### Verbose 로그 필요 여부

| 정보 | Information 레벨 | Verbose 레벨 |
|------|:----------------:|:------------:|
| 세션 시작/종료 | O | O |
| TLS 핸드셰이크 상세 | X | O |
| freerdp-proxy 상세 동작 | X | O |
| RDP 패킷 레벨 | X | O |

**Verbose 로그 수집 방법**은 [collect-data/README.md](../collect-data/README.md#32-server-agent-로그-verbose)를 참조하세요.

#### Server Agent 로그 경로

```
C:\ProgramData\QueryPie\ServerAgent\logs\
├── WinSAC.Agent.log          # 메인 로그
├── WinSAC.Agent.*.log        # 롤링된 이전 로그
└── freerdp-proxy.log         # freerdp-proxy 로그 (있는 경우)
```

### 2.5 구간 분석 체크리스트

**세션 끊김/연결 실패 이슈 분석 시 다음 순서로 진행합니다:**

| 순서 | 체크 항목 | 확인 방법 | 결과에 따른 행동 |
|:----:|-----------|-----------|------------------|
| 1 | 어떤 로그가 있는가? | 첨부파일 확인 | 없는 로그 요청 |
| 2 | Proxy 로그에서 RST/FIN 방향 확인 | `copying the stream (A to B)` 에러 | A가 RST 던진 주체 |
| 3 | RST가 Server Agent 방향(13389)이면 | Server Agent 로그 확인 | SA 내부 구간 분석 |
| 4 | RST가 Multi-Agent 방향이면 | Multi-Agent 로그 확인 | 클라이언트 측 문제 분석 |
| 5 | Server Agent 로그에서 freerdp-proxy 에러 확인 | `freerdp-proxy failed` 등 | TermService 문제 가능성 |
| 6 | TermService 문제 의심 시 | Windows 이벤트 로그 요청 | GPO, 보안 정책 확인 |

### 2.6 구간별 원인 예시

| RST 발생 구간 | 가능한 원인 | 추가 확인 필요 |
|---------------|-------------|---------------|
| **Proxy → SA** | 방화벽, Server Agent 미실행, TLS 실패 | Server Agent 서비스 상태, 13389 포트 |
| **SA 내부 (freerdp-proxy)** | freerdp-proxy 크래시, 라이선스 문제 | Server Agent verbose 로그 |
| **SA → TermService** | Windows RDP 서비스 문제, GPO 정책, NLA 설정 | Windows 이벤트 로그, GPO 덤프 |
| **MA → Proxy** | 클라이언트 네트워크 문제, WebView 크래시 | Multi-Agent 로그, webView.log |

---

## TLS Fallback 에러 (정상 동작)

> **핵심**: `Failed to create TLS handler` 에러가 있어도 최종 **Healthy면 정상**

### 판단 기준

| 로그 흐름 | 판단 |
|-----------|:----:|
| `ERR Failed to create TLS handler` → `INF TLS=native (1.2)` → `Healthy` | **정상** |
| `ERR Failed to create TLS handler` → fallback 없음 → Offline | 문제 |

Fallback 상세: [arch-server-agent.md](../../rdp-doc/common/arch-server-agent.md#tls-인증서-생성)

### 관련 티켓

- [QCP-4323](https://querypie.atlassian.net/browse/QCP-4323) - TLS fallback 에러 문의 (정상 동작)

---

## 로그 분석 키워드

| 키워드 | 의미 | 조치 |
|--------|------|------|
| `Failed to HeartBeat` | QueryPie 통신 실패 | 네트워크/TLS 확인 |
| `Win32Exception (0x80090367)` | ALPN 협상 실패 | 핫픽스 적용 |
| `TLS alert: 'HandshakeFailure'` | TLS 실패 | 케이스 D 참조 (TLS 1.2 요구사항 안내) |
| `RDP-QP-X connectivity check failed` | Listener 실패 | 레지스트리 정리 |
| `Client started` -> `stopped` (2초) | 세션 즉시 종료 | 버그 가능성 |
| Windows Server 2025 + freeze | 로그온 UI Freeze | 케이스 H 참조 (Windows 업데이트 필요) |
| `0x904` (mstsc) / `0x204` (App) | Multi-Agent→ARiSA 연결 실패 | QueryPie 서버 측 확인 (ARiSA 프로세스, 9000 포트, proxies 테이블) |

---

## 심층 분석이 필요할 때

체크리스트로 해결되지 않으면 아래 문서와 소스코드를 참조하세요.

### 아키텍처 문서

| 문서 | 언제 참조? |
|------|-----------|
| [arch-glossary.md](../../rdp-doc/common/arch-glossary.md) | AgentId, AgentUuid, Heartbeat 등 용어 |
| [arch-server-agent.md](../../rdp-doc/common/arch-server-agent.md) | Server Agent 내부 동작 이해 |
| [arch-overview.md](../../rdp-doc/common/arch-overview.md) | 전체 시스템 구조 파악 |

### 소스코드

| 컴포넌트 | 경로 | 주요 확인 포인트 |
|----------|------|-----------------|
| Server Agent | `apps/winsac` | HeartBeat, Listener, TLS 처리 |
| Gateway | `apps/gateway` | Activate, 연결 상태 관리 |
| Policy Server | `apps/api` | Agent 상태 판정 로직 |
