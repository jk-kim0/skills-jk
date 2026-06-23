# RDP 자료 수집 요청 템플릿

> **이 문서의 역할**: CS 대응 시 Claude가 참조하는 **자료 수집 요청 템플릿**.

## 템플릿 목록

| 번호 | 템플릿 | 사용 시점 | 키워드 |
|:----:|--------|----------|--------|
| 3.1 | 기본 정보 수집 | 모든 이슈 첫 요청 | basic, 기본 |
| 3.2 | Server Agent 로그 (Verbose) | 상세 로그 필요 | verbose, log |
| 3.3 | 네트워크 패킷 캡처 | 네트워크 문제 의심 | packet, capture |
| 3.4 | TLS/SSL 설정 확인 | TLS 실패 의심 | tls, ssl |
| 3.5 | 네트워크 연결 상태 | HeartBeat 실패 | network, heartbeat |
| 3.6 | SCHANNEL 상세 로깅 | TLS 심층 분석 | schannel |
| 3.7 | GPO 및 보안 정책 | RDP 보안 정책 문제 | gpo, policy |
| 3.8 | Windows 이벤트 로그 | 로그인/세션 분석 | event, 이벤트 |
| 3.9 | 즉시 로그 수집 (올인원) | CS 긴급 대응 | all, 전체, 긴급 |

---

## 3.1 기본 정보 수집

> **사용 시점**: 모든 이슈의 첫 번째 요청

```
안녕하세요, 이슈 분석을 위해 다음 정보 확인 부탁드립니다.



1. Windows Server OS 버전 (UBR 포함)
   PowerShell 관리자 권한으로 실행:

Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" | Select-Object ProductName, ReleaseId, DisplayVersion, CurrentBuild, UBR

   실행 결과를 캡처하여 공유 부탁드립니다.



2. QueryPie Server Agent 버전
   - 시스템 트레이 아이콘 우클릭 -> About
   - 또는 제어판 -> 프로그램 추가/제거
   - 또는 레지스트리: HKLM:\SOFTWARE\QueryPie\Server Agent



3. QueryPie 버전
   관리자페이지 -> Settings -> About



4. 문제 발생 정보
   - 최초 발생 시점:
   - 재현 빈도 (항상/간헐적/특정 조건):
   - 영향 범위 (특정 서버만/전체):

감사합니다.
```

---

## 3.2 Server Agent 로그 (Verbose)

> **사용 시점**: 상세 로그 분석 필요 시

```
안녕하세요, 상세 분석을 위해 Server Agent 로그를 Verbose 레벨로 수집 요청드립니다.

참고: https://querypie.atlassian.net/wiki/spaces/QCP/pages/879362165



1. 로그 레벨 변경
   PowerShell 관리자 권한으로 실행:

# 현재 로그 레벨 확인
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent" | Select-Object LogLevel

# Verbose로 변경
Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent" -Name "LogLevel" -Value "Verbose"

# 서비스 재시작
Restart-Service "QueryPie Server Agent" -Force



2. 문제 재현
   로그 레벨 변경 후 문제 증상을 재현해주세요.



3. 로그 파일 수집
   아래 경로의 Logs 폴더를 ZIP으로 압축:

C:\ProgramData\QueryPie\Server Agent\Logs\



4. 로그 레벨 원복 (분석 완료 후)

Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent" -Name "LogLevel" -Value "Information"
Restart-Service "QueryPie Server Agent" -Force

감사합니다.
```

---

## 3.3 네트워크 패킷 캡처

> **사용 시점**: 네트워크 구간 문제 의심 시

```
안녕하세요, QueryPie <-> Server Agent 구간 네트워크 분석이 필요합니다.
양쪽에서 동시에 패킷 캡처를 진행해주세요.



1. Windows Server에서 캡처 (netsh)
   PowerShell 관리자 권한으로:

# 캡처 시작
netsh trace start capture=yes tracefile="C:\rdp_capture.etl" maxsize=500

# 문제 재현 후 중지 (약 2-3분)
netsh trace stop

   생성 파일: C:\rdp_capture.etl, C:\rdp_capture.cab



2. QueryPie 서버에서 캡처 (tcpdump)
   SSH 접속 후:

sudo tcpdump -i any port 13389 -w /tmp/rdp_traffic.pcap

# 문제 재현 후 Ctrl+C

   생성 파일: /tmp/rdp_traffic.pcap



캡처 시간 동기화
양쪽 캡처를 동시에 시작/종료하고, 문제 재현 시점을 알려주세요.

감사합니다.
```

---

## 3.4 TLS/SSL 설정 확인

> **사용 시점**: TLS 핸드셰이크 실패 의심 시

```
안녕하세요, TLS 설정 확인이 필요합니다.
아래 명령어들의 실행 결과를 캡처하여 공유 부탁드립니다.



1. TLS Cipher Suite 목록

Get-TlsCipherSuite | Format-Table Name, Exchange, Cipher, Hash -AutoSize



2. SCHANNEL 프로토콜 설정

Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols" -Recurse | Get-ItemProperty



3. TLS 1.2 활성화 여부 (Windows 2012는 특히 중요)

# TLS 1.2 Client
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client" -ErrorAction SilentlyContinue

# TLS 1.2 Server
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server" -ErrorAction SilentlyContinue

"경로를 찾을 수 없습니다" 오류 -> TLS 1.2 명시적 미설정 상태

감사합니다.
```

---

## 3.5 네트워크 연결 상태

> **사용 시점**: HeartBeat 실패 시

```
안녕하세요, 네트워크 연결 상태 확인 부탁드립니다.



1. DNS 확인 (Windows -> QueryPie)

nslookup {querypie-domain}
Test-NetConnection -ComputerName {querypie-domain} -Port 443



2. HTTPS 통신 테스트

Invoke-WebRequest -Uri "https://{querypie-domain}" -UseBasicParsing | Select-Object StatusCode, StatusDescription



3. 포트 리슨 상태 (Windows)

netstat -ano | findstr "13389"
netstat -ano | findstr "LISTEN"



4. 역방향 연결 테스트 (QueryPie -> Windows)
   QueryPie 서버에서:

nc -zv {Windows서버IP} 13389

연결 실패 -> Windows 방화벽 13389 인바운드 확인

감사합니다.
```

---

## 3.6 SCHANNEL 상세 로깅

> **사용 시점**: TLS 심층 분석 필요 시
> **주의**: 시스템 부하 있음, 분석 후 반드시 원복

```
안녕하세요, TLS 심층 분석을 위해 SCHANNEL 상세 로깅이 필요합니다.

주의: 상세 로깅은 시스템 부하를 줄 수 있습니다. 분석 후 반드시 원복해주세요.



1. SCHANNEL 상세 로깅 활성화

Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" -Name "EventLogging" -Value 7 -Type DWord



2. 문제 재현



3. 이벤트 로그 추출

wevtutil epl System "C:\SystemLog.evtx"



4. 로깅 원복 (필수!)

Set-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" -Name "EventLogging" -Value 1 -Type DWord

감사합니다.
```

---

## 3.7 GPO 및 보안 정책

> **사용 시점**: RDP 보안 정책 문제 의심 시

```
안녕하세요, GPO 설정 확인이 필요합니다.



1. GPO 보고서 생성

# 컴퓨터 정책
gpresult /SCOPE COMPUTER /H C:\GPO_Computer.html

# 사용자 정책
gpresult /H C:\GPO_User.html

생성된 HTML 파일 2개 전달 부탁드립니다.



2. RDP 보안 설정 확인

Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" | Select-Object SecurityLayer, UserAuthentication, MinEncryptionLevel

결과 해석:
- SecurityLayer: 0=RDP, 1=Negotiate, 2=TLS (SSL)
- UserAuthentication: 0=비활성화, 1=NLA 활성화

감사합니다.
```

---

## 3.8 Windows 이벤트 로그

> **사용 시점**: 로그인 실패/세션 이벤트 분석 시

```
안녕하세요, Windows 이벤트 로그 분석이 필요합니다.



1. Security 이벤트 로그 (로그인 실패 분석)

wevtutil epl Security "C:\Security_Event.evtx" /q:"*[System[TimeCreated[timediff(@SystemTime) <= 86400000]]]"



2. Terminal Services 이벤트 로그 (RDP 세션 분석)

wevtutil epl Microsoft-Windows-TerminalServices-LocalSessionManager/Operational "C:\TS_LocalSession.evtx"
wevtutil epl Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational "C:\TS_RemoteConnection.evtx"



3. Application 이벤트 로그 (Server Agent 오류)

wevtutil epl Application "C:\Application_Event.evtx" /q:"*[System[TimeCreated[timediff(@SystemTime) <= 86400000]]]"

생성된 .evtx 파일들을 압축하여 전달 부탁드립니다.

감사합니다.
```

---

## 3.9 즉시 로그 수집 (올인원)

> **사용 시점**: CS 긴급 대응, 한 번에 모든 로그 수집

```
안녕하세요, 즉시 분석을 위해 아래 정보들을 한 번에 수집 부탁드립니다.

PowerShell 관리자 권한으로 아래 스크립트를 실행해주세요:


# 1. Server Agent 로그 압축
Compress-Archive -Path "C:\ProgramData\QueryPie\ServerAgent\logs\*" -DestinationPath "C:\ServerAgentLogs.zip" -Force

# 2. Windows 이벤트 로그 (최근 1일)
Get-WinEvent -LogName System -MaxEvents 1000 |
  Where-Object { $_.TimeCreated -gt (Get-Date).AddDays(-1) } |
  Export-Csv "C:\SystemEvents.csv" -NoTypeInformation

Get-WinEvent -LogName Application -MaxEvents 1000 |
  Where-Object { $_.TimeCreated -gt (Get-Date).AddDays(-1) } |
  Export-Csv "C:\ApplicationEvents.csv" -NoTypeInformation

# 3. 네트워크 상태
Get-NetTCPConnection | Where-Object { $_.LocalPort -eq 13389 -or $_.RemotePort -eq 13389 } | Out-File "C:\NetworkStatus.txt"
Get-NetFirewallRule -DisplayName "*QueryPie*" | Format-List | Out-File "C:\FirewallRules.txt" -Append

# 4. 레지스트리 설정
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent" | Out-File "C:\RegistrySettings.txt"

# 5. 전체 압축
Compress-Archive -Path "C:\ServerAgentLogs.zip", "C:\SystemEvents.csv", "C:\ApplicationEvents.csv", "C:\NetworkStatus.txt", "C:\FirewallRules.txt", "C:\RegistrySettings.txt" -DestinationPath "C:\QueryPie_AllLogs.zip" -Force


생성된 C:\QueryPie_AllLogs.zip 파일을 첨부 부탁드립니다.

감사합니다.
```

---

## 메시지 작성 가이드

### Jira/Slack 공통 원칙

| 원칙 | 이유 |
|------|------|
| **접힘 문서(collapsible) 사용하지 않음** | 가독성 저하, 핵심 정보가 숨겨짐 |
| **italic 사용하지 않음** | 가독성 저하 (bold, 코드블록은 허용) |
| **이모지 사용하지 않음** | 전문적인 CS 응대에 부적절 |
| **PowerShell 명령어는 상세히 안내** | 고객이 복사-붙여넣기로 바로 실행 가능해야 함 |
| **구간 분석 결과 먼저 설명** | 어디서 문제인지 알려야 고객이 납득함 |
| **추정 원인과 확정 원인 구분** | "~로 보입니다" vs "~입니다" 명확히 |

### PowerShell 명령어 안내 형식

**나쁜 예:**
```
서버 가동 시간을 확인해주세요.
```

**좋은 예:**
```
Windows Server에서 PowerShell을 *관리자 권한*으로 열고 아래 명령어를 실행해주세요:

(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime

실행 결과에서 Days 값이 50일 이상이면 알려진 버그에 해당합니다.
```

### 로그 수집 요청 형식

**나쁜 예:**
```
Server Agent 로그를 보내주세요.
```

**좋은 예:**
```
Windows Server에서 아래 경로의 폴더를 ZIP으로 압축하여 전달 부탁드립니다:

C:\ProgramData\QueryPie\ServerAgent\logs\

해당 폴더가 없으면 아래 경로를 확인해주세요:
C:\ProgramData\QueryPie\Server Agent\Logs\
```

### 구간 분석 결과 설명 형식

**나쁜 예:**
```
로그 분석 결과 세션이 끊기고 있습니다.
```

**좋은 예:**
```
proxy.log 분석 결과, *Server Agent가 Proxy에게 RST를 던지고 있습니다.*

- 10.232.22.31:13389 = Server Agent
- 10.20.201.206:52822 = QueryPie Proxy

Server Agent 내부에서 무슨 일이 있었는지 확인하려면 Server Agent 로그가 필요합니다.
```

### Slack 메시지 특이사항

| 항목 | 가이드 |
|------|--------|
| **코드 블록** | 단일 백틱(\`) 또는 삼중 백틱(\`\`\`) 사용 |
| **강조** | `*bold*` 사용 가능, `_italic_` 사용 금지 |
| **멘션** | 필요 시 담당자 멘션 |

---

## Jira 코멘트 등록

자료 수집 요청 작성 후 Jira 티켓에 등록:
- MCP: `mcp__atlassian__jira_add_comment` 도구
- CLI: `jira issue comment add <issue-key> -b "내용"`
