# RDP 케이스별 대응 방안

> **이 문서의 역할**: CS 대응 시 Claude가 참조하는 **케이스별 원인 분석 및 해결 방안**.

## 케이스 목록

| 케이스 | 유형 | 핵심 증상 | 해결 | 키워드 |
|:------:|:----:|-----------|------|--------|
| A | 버그 | Connection Failed + ALPN | 10.2.14+ | alpn, tls, 0x80090367 |
| B | 환경 | 통신 안됨 + 400 | hosts/DNS | dns, 400, resolve |
| C | 환경 | 재설치 후 Offline | 클린 설치 | listener, port, rdp-qp |
| D | 환경 | TLS Handshake 실패 | TLS 1.2 활성화 | tls, 2012, handshake |
| E | 버그 | 조기 세션 종료 | 11.5.1+ | timeout, 50일, overflow |
| F | 환경 | 세션 5~10분 후 끊김 + SSL 오류 | 공인 인증서 | fake certificate, ssl, webview |
| G | 환경 | 세션 시작 직후 종료 (2초 이내) | 보안정책 확인 | started, stopped, 2022, nla |
| H | 환경 | 로그온 UI Freeze (2025) | Windows 업데이트 | 2025, freeze, gfx, network detection |
| I | 환경 | Multi-Agent→ARiSA 연결 실패 | ARiSA/proxies 확인 | 0x904, 0x204, arisa, 9000, proxies |

---

## 케이스 A: TLS/ALPN 협상 실패 (버그)

### 증상

- Connection Failed 상태
- `SSLHandshakeException: Received fatal alert: protocol_version`
- `Win32Exception (0x80090367): 응용 프로그램 프로토콜 협상에 실패했습니다`

### 발생 환경

- Windows Server 2019 Standard (특정 빌드)
- IDC 물리 서버에서 주로 발생
- AWS 서버는 정상, IDC 서버만 실패

### 원인

Windows Schannel의 ALPN 확장 처리 버그. 서비스(SYSTEM 계정)로 동작 시에만 TLS 핸드셰이크 실패.

### 확인 절차

1. TCP 레벨 연결 정상인지 확인 (`Last Checked at` 갱신 여부)
2. Server Agent 로그에서 `Win32Exception (0x80090367)` 확인
3. 테스트 프로그램(사용자 권한)에서는 성공하고 서비스로 동작 시 실패하는지 확인

### 해결

**해결 버전**: Server Agent 10.2.14-0cc4415 이상 (Fallback 로직 구현)

### 고객 안내 예시

```
원인은 Windows Schannel 버그이며, 현재 고객사와 동일한 OS 버전으로 동일한 로그 발생까지 재현한 상태입니다.

Fallback 로직을 구현한 Server Agent 핫픽스를 공유드립니다.
* QueryPie Server에서 일부 Windows Server 2019에 TLS Handshake 요청 시 실패하지 않도록 개선
```

### 관련 티켓

- [QCP-3828](https://querypie.atlassian.net/browse/QCP-3828)

---

## 케이스 B: DNS/도메인 resolve 실패 (환경)

### 증상

- Server Agent 설치 완료되었으나 QueryPie와 통신 안됨
- QueryPie -> Windows Server 방향 통신은 정상
- 400 Bad Request 응답

### 확인 절차

1. Wireshark에서 통신이 도메인(ALB) vs Private IP 확인
2. Windows Server에서 도메인 resolve: `nslookup {querypie-domain}`
3. 400 Bad Request 응답 여부 확인

### 원인

QueryPie 도메인이 DNS(Route53 등)에 등록되지 않아 resolve 실패.

### 해결

**임시**: hosts 파일에 도메인-IP 매핑 추가
```
C:\Windows\System32\drivers\etc\hosts
{ALB IP} {querypie-domain}
```

**영구**: Route53 등 DNS에 도메인 등록

### 고객 안내 예시

```
해당 건 조치 완료되었습니다.

- 원인: 쿼리파이 도메인이 Route53에 등록되어 있지 않아서 ALB까지 연결되지 않음
- 조치: Windows Server hosts 파일에 쿼리파이 도메인과 ALB 수동 매핑
```

### 관련 티켓

- [QCP-3857](https://querypie.atlassian.net/browse/QCP-3857)

---

## 케이스 C: Custom Listener Port 누수 (환경)

### 증상

- 재설치 후 Online -> Offline 유지
- 헬스체크 실패
- `RDP-QP-X connectivity check failed` 반복

### 확인 절차

1. 레지스트리 확인: `HKLM:\...\Terminal Server\WinStations`에 RDP-QP-1~5 잔여 여부
2. `netstat -ano`로 4-5만번대 포트 LISTEN 상태 확인

### 원인

Agent 삭제 시 레지스트리/포트가 자동 정리되지 않음. RDP Services 재기동 없이는 Custom Listener Port 해제 안됨.

### 해결 (클린 설치 절차)

```
1. 제어판에서 QueryPie RDP Server Agent 삭제

2. 레지스트리 편집기 (regedit) 접속

3. 아래 경로 삭제 확인:
   - HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent Persistent
   - HKLM:\SYSTEM\CurrentControlSet\Services\QueryPie Server Agent

4. 아래 경로 이동:
   HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations

5. RDP-QP-1 ~ RDP-QP-5 삭제

6. Remote Desktop Service 재시작:
   Restart-Service -Name TermService -Force

7. 로그 디렉터리 삭제:
   C:\ProgramData\QueryPie\Server Agent\Logs

8. Server Agent 재설치
```

### 고객 안내 예시

```
RDP Services 재기동 절차가 누락되어 Custom Listener Port 누수가 발생하는 것으로 보입니다.

RDP-QP-1과 같은 Custom Listener들은 RDP Agent 삭제 후 RDP Services가 재기동되어야 초기화됩니다.
services.msc에서 Remote Desktop Service를 재시작하면 포트 할당이 초기화됩니다.
```

### 관련 티켓

- [QCP-4336](https://querypie.atlassian.net/browse/QCP-4336)

---

## 케이스 D: Windows Server 2012 TLS 호환성 (환경)

### 증상

- Offline 상태
- `Failed to HeartBeat`, `SecureConnectionError`
- `TLS alert: 'HandshakeFailure'`
- `Win32Exception (0x80090326)`

### 발생 환경

- Windows Server 2012 / 2012 R2 (구형 OS)
- TLS 1.2 기본 비활성화

### 배경

**QueryPie 보안 요구사항**:
- QueryPie는 보안을 위해 **TLS 1.2 이상**을 요구합니다
- TLS 1.0/1.1은 보안 취약점으로 인해 업계 전반에서 deprecated
- Microsoft, AWS, Azure 등 모든 주요 클라우드 서비스가 TLS 1.2 이상 요구

**Windows Server 2012 상황**:
- TLS 1.2를 **지원**하지만 기본적으로 **비활성화**
- 활성화하면 정상 동작

### 확인 절차

1. Windows Server 버전 확인 (2012/2012 R2 여부)

2. TLS 1.2 활성화 상태 확인:
   ```powershell
   Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client' -ErrorAction SilentlyContinue
   ```

3. QueryPie HTTPS 통신 테스트:
   ```powershell
   [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
   Invoke-WebRequest https://{querypie-domain}/api/health
   ```

4. 필요 시 Root CA 인증서 등록 여부: `certmgr.msc`

### 해결

**고객에게 TLS 1.2 요구사항 안내**:
- QueryPie는 보안을 위해 TLS 1.2 이상을 요구함을 전달
- TLS 1.2 활성화 방법은 Microsoft 공식 문서 참조 안내: [TLS 1.2 enforcement](https://learn.microsoft.com/en-us/mem/configmgr/core/plan-design/security/enable-tls-1-2)

**필요 시**: QueryPie 도메인의 Root CA 인증서가 Windows에 등록되어 있는지 확인

### 고객 안내 예시

```
안녕하세요,

로그 분석 결과 TLS 핸드셰이크 실패로 인해 Server Agent가 QueryPie와 통신하지 못하고 있습니다.

■ 원인
QueryPie는 보안을 위해 TLS 1.2 이상을 요구합니다.
Windows Server 2012/2012 R2는 TLS 1.2를 지원하지만 기본적으로 비활성화되어 있어,
Server Agent가 QueryPie API와 HTTPS 통신 시 핸드셰이크가 실패합니다.

■ 해결 방안
1. Windows Server에서 TLS 1.2 활성화
   - 참고: https://learn.microsoft.com/en-us/mem/configmgr/core/plan-design/security/enable-tls-1-2

2. QueryPie API 서버에서 HTTP 허용 (비권장)
   - Server Agent 설치 시 Hub URL을 http://로 설정
   - 보안상 권장되지 않음

추가 문의사항 있으시면 말씀해주세요.
```

### 관련 티켓

- [QCP-4556](https://querypie.atlassian.net/browse/QCP-4556)

---

## 케이스 F: QueryPie Fake Certificate (환경)

### 증상

- RDP 세션이 5~10분 후 끊김
- Multi-Agent 로그에 `Access token expired` 반복
- webView.log에 SSL 인증서 오류:
  ```
  CertVerifyProcBuiltin for {IP} failed:
  ----- Certificate i=0 (CN=QueryPie Fake Certificate,O=QueryPie,C=KR) -----
  ERROR: No matching issuer found
  ```

### 발생 환경

- QueryPie 서버에 자체 서명 인증서(Self-signed) 또는 사설 CA 인증서 사용
- Docker 기본 설정으로 NGINX 실행 시 발생
- 클라이언트(Windows/macOS)에 해당 CA가 신뢰되지 않음

### 원인

**QueryPie Fake Certificate 출처**:
- Docker 이미지의 NGINX 기본 설정 (`artifacts/nginx/nginx.conf`)에서 생성
- 1일 유효 자체 서명 인증서: `CN=QueryPie Fake Certificate,O=QueryPie,C=KR`

**토큰 갱신 실패 원인**:
- Multi-Agent는 WebView(CEF) 내부에서 JavaScript fetch/WebSocket으로 API 호출
- CEF의 `OnCertificateError` 콜백은 **Main Frame Navigation에만 적용**
- Sub-resource 요청(fetch, XMLHttpRequest, WebSocket)은 콜백 우회 불가
- 토큰 갱신 API 호출 시 SSL 검증 실패 → 세션 종료

### 확인 절차

1. Multi-Agent 로그 디렉터리에서 `webView.log` 확인:
   ```
   C:\Users\{사용자}\.querypie-multi-agent\logs\webView.log (Windows)
   ~/.querypie-multi-agent/logs/webView.log (macOS/Linux)
   ```

2. SSL 인증서 오류 키워드 검색:
   ```
   CertVerifyProcBuiltin.*failed
   QueryPie Fake Certificate
   No matching issuer found
   ```

3. Multi-Agent 로그에서 토큰 갱신 실패 확인:
   ```
   Access token expired
   QPS-13201.*Not found authentication result
   ```

### 해결

**권장 (영구)**: QueryPie 서버에 공인 SSL 인증서 적용

**대안 1**: 사설 CA 인증서를 클라이언트에 신뢰 등록
- Windows: `certmgr.msc` → 신뢰할 수 있는 루트 인증 기관에 CA 추가
- macOS: 키체인 접근 → 시스템 키체인에 CA 추가 후 "항상 신뢰"

**대안 2 (비권장)**: HTTP 사용 (보안상 권장하지 않음)

### 고객 안내 예시

```
안녕하세요,

로그 분석 결과 Multi-Agent가 QueryPie 서버와 HTTPS 통신 시
SSL 인증서 검증에 실패하여 세션이 종료되고 있습니다.

■ 원인
QueryPie 서버에서 사용 중인 SSL 인증서가 클라이언트 PC에서
신뢰되지 않아 토큰 갱신 API 호출이 실패합니다.

webView.log에서 다음 오류가 확인됩니다:
"CertVerifyProcBuiltin for {IP} failed: CN=QueryPie Fake Certificate"

■ 해결 방안
1. QueryPie 서버에 공인 SSL 인증서 적용 (권장)
2. 현재 사용 중인 CA 인증서를 클라이언트 PC에 신뢰 등록
   - Windows: certmgr.msc → 신뢰할 수 있는 루트 인증 기관
   - macOS: 키체인 접근 → 시스템 키체인

추가 문의사항 있으시면 말씀해주세요.
```

### 관련 티켓

- [QCP-4605](https://querypie.atlassian.net/browse/QCP-4605)

---

## 케이스 E: mouse->time 32비트 overflow (버그)

### 증상

- RDP 세션이 설정된 timeout보다 일찍 종료 (예: 10분 설정인데 5분에 종료)
- Server Access History에 `Idle timeout`으로 기록
- Command Audit에 마우스 클릭 기록 없음

### 발생 환경

- 부팅 후 **50일 이상** 경과된 Windows Server
- Server Agent 11.1.0 이하

### 확인 절차

1. Server Access History에서 세션 종료 사유 확인
2. Command Audit > MouseClick 필터로 클릭 기록 확인
3. 서버 가동 시간 확인:
   ```powershell
   (get-date) - (gcim Win32_OperatingSystem).LastBootUpTime
   ```
   50일 이상인지 확인

### 원인

Windows GetTickCount()는 32비트 unsigned integer로 약 49.7일(2^32 ms) 후 overflow. idle timeout 계산 오류 발생.

### 해결

**해결 버전**: Server Agent 11.5.1 이상 (QPD-4233 버그 수정)

### 고객 안내 예시

```
분석 결과 전달 드립니다.

1. 본 이슈는 서버에이전트에서 mouse click 발생 시각 계산 로직에 버그가 있어서,
   처음 부팅 후 50일 이상 된 윈도우 서버에서 발생하는 이슈입니다.

   - mouse click 이벤트 시각이 실제와 다르게 기록되며,
   - idle timeout 계산 시에도 실제와 다른 시간 기준 사용
   - 관리자페이지상 10분인데 5분만에 세션 종료되는 현상 발생

2. 서버에이전트 버전업(11.5.1+)이 필요합니다.
```

### 관련 티켓

- [QCP-4704](https://querypie.atlassian.net/browse/QCP-4704)

---

## 케이스 G: 세션 시작 직후 종료 (환경)

### 증상

- RDP 세션이 시작 직후 **2초 이내** 종료
- Server Agent 로그: `Client started` → `Client stopped` (1~2초 간격)
- HeartBeat 정상 (Offline/Connection Failed 아님)
- 스트림 복사 중 `Operation canceled` 에러

### 발생 환경

- Windows Server 2022 Datacenter (신규 설치)
- 기존 서버는 정상, 신규 설치 서버에서만 발생

### 의심 원인

1. **Windows 보안 정책**: NLA, CredSSP, SecurityLayer 설정 차이
2. **그룹 정책**: 신규 서버에 적용된 GPO가 RDP 연결 차단
3. **보안 패치**: Windows Server 2022 특정 보안 업데이트 영향

### 필요 자료

1. **Server Agent Verbose 로그**
   ```
   로그 레벨을 Verbose로 변경 후 재현
   ```

2. **그룹 정책 덤프**
   ```powershell
   gpresult /h C:\gp.html
   ```

3. **Windows 이벤트 로그**
   ```powershell
   md C:\temp -ea 0
   $logs="Microsoft-Windows-TerminalServices-LocalSessionManager/Operational","Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational","Microsoft-Windows-TerminalServices-RdpCoreTS/Operational","System","Security"
   $logs|%{wevtutil epl $_ "C:\temp\$($_ -replace '[\/]','_').evtx"}
   ```

4. **기존 정상 서버와 비교**
   - 기존 Windows 2022 서버 유무
   - 보안 패치 레벨 차이

### 관련 티켓

- [QCP-4648](https://querypie.atlassian.net/browse/QCP-4648)

---

## 케이스 H: Windows Server 2025 GFX Freeze (환경)

### 증상

- macOS/Windows App으로 **Multi Agent 경유** RDP 접속 시 로그온 UI에서 **Freeze**
- 3번 중 1~2번 꼴로 랜덤 발생
- 세션 로그에는 **정상 접속**으로 기록됨 (마우스 클릭 등도 녹화됨)
- **직접 연결(MSTSC, xfreerdp)은 정상** 동작

### 발생 환경

- **Windows Server 2025** (특히 초기 버전, 윈도우 업데이트 미적용)
- macOS Tahoe 26.1에서 주로 보고됨
- Server Agent gfx=true (기본값) 설정

### 원인

**FreeRDP의 gfx=true 옵션과 Windows Server 2025 조합 문제**:
- Server Agent는 내부적으로 [FreeRDP](https://github.com/FreeRDP/FreeRDP) 오픈소스를 사용
- Windows Server 2025 출시 직후 FreeRDP 커뮤니티에 다수 보고된 이슈
  - [FreeRDP#10864](https://github.com/FreeRDP/FreeRDP/issues/10864)
- **network detection** GP 설정과 **gfx** 옵션의 상호작용으로 인해 freeze 발생
- KB5052093 이후 Windows 패치에서 Microsoft 측 수정으로 해결

### 확인 절차

1. Windows Server 버전 확인: **2025** 여부
2. Windows 업데이트 상태 확인 (KB5052093 이후 패치 적용 여부)
3. 직접 연결(MSTSC) vs Multi Agent 경유 비교
4. GP 설정 확인:
   ```
   gpedit.msc → Computer Configuration → Administrative Templates
     → System → Group Policy
     → "Configure Automatic Updates" 관련 network detection 설정
   ```

### 해결

| 방법 | 효과 | 비고 |
|------|:----:|------|
| **Windows 업데이트 (권장)** | ✅ | KB5052093 이후 패치 적용 |
| GP network detection 설정 변경 | ✅ | 임시 workaround |
| Server Agent gfx=false | ✅ | 그래픽 성능 저하 (비권장) |

### 고객 안내 예시

```
안녕하세요,

분석 결과 공유 드립니다.

■ 원인
Windows Server 2025 초기 버전에서 FreeRDP의 GFX(Graphics Pipeline Extension)
옵션 사용 시 로그온 화면에서 freeze되는 이슈가 확인되었습니다.

이는 FreeRDP 커뮤니티에서 다수 보고된 이슈로, Windows 측 network detection
관련 로직과 GFX 옵션의 상호작용으로 발생합니다.
- https://github.com/FreeRDP/FreeRDP/issues/10864

■ 해결 방안
1. Windows Server 2025에 KB5052093 이후 최신 보안 패치 적용 (권장)
   - 해당 패치 이후 이슈가 해결됨을 확인했습니다.

2. (대안) Group Policy에서 network detection 관련 설정 변경
   - gpedit.msc → Computer Configuration → Administrative Templates
     → Windows Components → Remote Desktop Services
     → Remote Desktop Session Host → Connections
     → "Restrict Remote Desktop Services users to a single Remote Desktop Services session"
     → Disabled 변경 후 gpupdate /force 실행

추가 문의사항 있으시면 말씀해주세요.
```

### 관련 티켓

- [QCP-4630](https://querypie.atlassian.net/browse/QCP-4630)

### 외부 참고 자료

- [FreeRDP Issue #10864](https://github.com/FreeRDP/FreeRDP/issues/10864)
- [Reddit: Windows 11 24H2 RDP Session Hangs](https://www.reddit.com/r/sysadmin/comments/1gbq4y7/windows_11_24h2_rdp_session_hangs_on_logon)
- [Microsoft Tech Community: RDP Freeze on Reconnect](https://techcommunity.microsoft.com/discussions/windows11/windows-version-24h2-causes-remote-desktop-to-freeze-on-reconnect-/4383663)

---

## 케이스 I: Multi-Agent → ARiSA 연결 실패 (환경)

### 증상

- Server Agent는 **Online** 상태인데 RDP 접속 실패
- mstsc: `0x904` (확장오류 `0x7`)
- macOS/Windows App: `0x204`
- 접속 시도 시 타임아웃 또는 즉시 실패

### 발생 환경

- QueryPie 서버 측 문제
- ARiSA 프로세스 미실행 또는 9000번 포트 미점유
- `querypie.proxies` 테이블의 host 설정 오류

### 확인 절차

1. **Multi-Agent 로그 확인**: 요청 전송 흔적 있음
2. **ARiSA 로그 확인**: **요청 수신 흔적 없음** ← 핵심 단서
   - 이 불일치가 있으면 Multi-Agent → ARiSA 구간 문제 확정
3. **QueryPie 서버에서 확인**:
   ```bash
   # ARiSA 프로세스 실행 여부
   ps aux | grep arisa

   # ARiSA 9000번 포트 점유 여부
   netstat -tlnp | grep 9000
   ```
4. **Meta DB에서 proxies 설정 확인**:
   ```sql
   SELECT * FROM querypie.proxies;
   ```
   - `host` 값이 Multi-Agent가 접근 가능한 주소인지 확인

### 원인

**원인 1: ARiSA 프로세스 문제**
- ARiSA 프로세스가 실행되지 않음
- ARiSA가 실행 중이지만 9000번 포트를 리스닝하지 않음

**원인 2: Proxy 주소 설정 문제**
- Multi-Agent가 RDP 접속 시 API에 ARiSA 주소를 요청
- API는 `querypie.proxies` 테이블의 `host` 값을 응답
- 이 값이 잘못 설정되면 Multi-Agent가 ARiSA를 찾지 못함
  - 예: 내부 IP인데 외부에서 접속 시도
  - 예: 도메인이 resolve 안 됨

### 해결

| 원인 | 해결 방법 |
|------|----------|
| ARiSA 프로세스 미실행 | ARiSA 서비스 재시작 |
| 9000 포트 미점유 | ARiSA 설정 확인 후 재시작 |
| proxies.host 설정 오류 | Meta DB에서 올바른 주소로 수정 |

**proxies 테이블 수정 예시**:
```sql
UPDATE querypie.proxies
SET host = '{올바른_ARiSA_주소}'
WHERE id = {proxy_id};
```

### 고객 안내 예시

```
안녕하세요,

분석 결과 공유 드립니다.

■ 원인
Multi-Agent가 QueryPie 서버의 ARiSA 프록시에 연결하지 못해
RDP 접속이 실패하고 있습니다.

확인 결과:
- Multi-Agent 로그: 접속 요청 전송 흔적 있음
- ARiSA 로그: 요청 수신 흔적 없음
- → Multi-Agent → ARiSA 구간에서 연결 자체가 실패

■ 확인 필요 사항
1. ARiSA 프로세스가 정상 실행 중인지 확인
2. ARiSA가 9000번 포트를 리스닝하고 있는지 확인
3. querypie.proxies 테이블의 host 설정이 올바른지 확인

■ 조치
{확인 결과에 따른 조치 - ARiSA 재시작 또는 proxies 설정 수정}

추가 문의사항 있으시면 말씀해주세요.
```

### 진단 핵심 포인트

> **Multi-Agent 로그에는 요청 전송 흔적이 있는데, ARiSA 로그에는 수신 흔적이 없다면**
> → 100% Multi-Agent → ARiSA 구간 문제
> → QueryPie 서버 측 확인 필요 (ARiSA 프로세스, 포트, proxies 설정)

---

## 심층 분석이 필요할 때

케이스 대응으로 해결되지 않으면 아래 문서와 소스코드를 참조하세요.

### 아키텍처 문서

| 문서 | 언제 참조? |
|------|-----------|
| [arch-glossary.md](../../rdp-doc/common/arch-glossary.md) | TLS, ALPN, Heartbeat 등 용어 이해 |
| [arch-server-agent.md](../../rdp-doc/common/arch-server-agent.md) | Server Agent 내부 동작, 이벤트 수집 |
| [arch-network.md](../../rdp-doc/common/arch-network.md) | Gateway, Nova, 네트워크 구성 문제 |

### 소스코드

| 컴포넌트 | 경로 | 케이스별 확인 포인트 |
|----------|------|---------------------|
| Server Agent | `apps/winsac` | A: TLS/ALPN, D: Schannel, E: GetTickCount |
| Gateway | `apps/gateway` | A: Activate TLS, B: DNS resolve |
| Policy Server | `apps/api` | C: Agent 등록/삭제 로직 |

### 외부 문서

- [RDP Server Agent 설정 가이드](https://querypie.atlassian.net/wiki/spaces/QCP/pages/879362165)
- [RDP Windows Server 연결 Use Case](https://querypie.atlassian.net/wiki/spaces/QCP/pages/1105789042)
