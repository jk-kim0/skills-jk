# RDP 접근제어 시스템 문서

QueryPie RDP 기반 Windows Server 접근제어 시스템의 아키텍처 문서입니다.

---

## Quick Start (5분 요약)

### 시스템이 하는 일

사용자가 Windows Server에 RDP 접속할 때, QueryPie가 중간에서 **인증, 권한 검사, 세션 감사, 명령어 로깅**을 수행합니다.

### 핵심 컴포넌트 4개

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Multi-Agent │ ──→ │   ARiSA     │ ──→ │Server Agent │ ──→ │ Windows RDP │
│ (사용자 PC)  │     │  (프록시)    │     │(Windows서버)│     │  (3389)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Policy API │
                    │ (정책/감사)  │
                    └─────────────┘
```

| 컴포넌트 | 역할 | 위치 |
|---------|------|------|
| **Multi-Agent** | 사용자 PC에서 RDP 클라이언트와 ARiSA 중개 | `apps/multi-agent` |
| **ARiSA** | RDP 트래픽 프록시, JWT 인증 | `apps/arisa` |
| **Server Agent** | Windows Server에서 RDP 접근제어, 이벤트 수집 | `apps/winsac` |
| **Policy API** | 정책 관리, 세션 저장, 감사 로그 | `apps/api` |

### 연결 흐름 한 줄 요약

```
사용자 → Multi-Agent → ARiSA → (Gateway/Nova) → Server Agent → Windows RDP
```

- **Gateway**: SSH 점프 호스트 경유 시 사용
- **Nova**: 인바운드 차단 환경에서 Reverse Tunnel로 사용

### Server Agent 상태

| 상태 | 의미 |
|------|------|
| **HEALTHY** | 정상 (Heartbeat 수신 중) |
| **OFFLINE** | Heartbeat 5분 이상 미수신 |
| **WAITING_FOR_ACTIVATION** | 신규 설치, 활성화 대기 |

---

## 문서 구조

| 문서 | 내용 | 언제 읽나? |
|------|------|----------|
| **[GLOSSARY.md](GLOSSARY.md)** | 용어집 | 용어가 헷갈릴 때 |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 전체 아키텍처, 핵심 개념 | 시스템 이해가 필요할 때 |
| **[SERVER-AGENT.md](SERVER-AGENT.md)** | Server Agent 상세 구현 | Server Agent 문제 분석 시 |
| **[NETWORK.md](NETWORK.md)** | Gateway, Nova, 네트워크 구성 | 네트워크 관련 문제 시 |

---

## CS 대응 빠른 참조

### 증상별 바로가기

| 증상 | 참조 문서 |
|------|----------|
| Server Agent **Offline** | [diagnose/SKILL.md#1.2](../diagnose/SKILL.md#12-offline--not-found) |
| **Connection Failed** | [diagnose/SKILL.md#1.3](../diagnose/SKILL.md#13-connection-failed) |
| **세션 끊김** | [diagnose/SKILL.md#1.6](../diagnose/SKILL.md#16-세션-끊김조기-종료) |

### 자주 찾는 개념

| 개념 | 참조 |
|------|------|
| AgentId vs AgentUuid | [GLOSSARY.md#agentid](GLOSSARY.md#agentid--machineid) |
| Heartbeat vs Heartbeat Scan | [ARCHITECTURE.md#heartbeat](ARCHITECTURE.md#23-heartbeat-vs-heartbeat-scan) |
| UseServerAgent 플래그 | [ARCHITECTURE.md#use-server-agent](ARCHITECTURE.md#32-arisa-proxy-server) |
| Gateway vs Nova | [NETWORK.md#overview](NETWORK.md#1-개요) |

---

## End-to-End 시나리오

### 시나리오 1: RDP 접속 (Server Agent 설치됨)

```
1. 사용자가 QueryPie UI에서 서버 선택 → "Connect" 클릭
2. Multi-Agent가 ARiSA에 JWT 토큰 발급 요청
3. Multi-Agent가 localhost:임의포트 → ARiSA 터널 생성
4. Multi-Agent가 .rdp 파일 생성 후 mstsc.exe 실행
5. RDP 클라이언트 → Multi-Agent → ARiSA → Server Agent
6. Server Agent가 API에 Connected() 호출
7. Server Agent가 로컬 RDP 서비스(3389)에 연결
8. 사용자에게 Windows 바탕화면 표시
```

### 시나리오 2: RDP 접속 (Server Agent 미설치)

```
1~5. 동일
6. ARiSA가 API에 Connected() 호출 (Server Agent 대신)
7. ARiSA가 직접 Windows RDP 서비스(3389)에 연결
8. 사용자에게 Windows 바탕화면 표시
```

**차이점**: Server Agent 없으면 ARiSA가 직접 API 호출 + 3389 연결

### 시나리오 3: Server Agent 신규 설치

```
1. Windows Server에 Server Agent 설치
2. Server Agent가 Heartbeat 전송 시작 (AgentUuid=null)
3. API가 신규 Server Agent 등록 (WAITING_FOR_ACTIVATION)
4. 관리자가 QueryPie 콘솔에서 Activate 버튼 클릭
5. API가 Server Agent의 /api/activate 호출
6. Server Agent가 AgentUuid를 레지스트리에 저장
7. 다음 Heartbeat부터 AgentUuid 포함
8. 상태가 HEALTHY로 변경
```

---

## 소스코드 위치

| 컴포넌트 | 경로 | 언어 |
|---------|------|------|
| Multi-Agent (Client Agent) | `apps/multi-agent` | C# |
| ARiSA Proxy | `apps/arisa` | C# |
| Server Agent (WinSAC) | `apps/winsac` | C# |
| Policy Server (API) | `apps/api` | Kotlin |
| Gateway | `apps/gateway` | C# |
| Nova | `apps/nova` | Go |

---

## 주요 포트

| 포트 | 컴포넌트 | 용도 |
|------|---------|------|
| **13389** | Server Agent | TLS + Agent Protocol (외부 노출) |
| **13390** | Server Agent | 내부 HTTP API (localhost only) |
| **3389** | Windows RDP | 실제 RDP 서비스 |
| **8090** | Policy API | gRPC/HTTPS |
| **22** | NOVAS | SSH 터널 |
| **9090** | NOVAS | REST API |
