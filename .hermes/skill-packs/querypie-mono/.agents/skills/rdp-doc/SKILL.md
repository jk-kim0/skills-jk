---
name: rdp-doc
description: |
  RDP/Windows Server 접근제어 시스템 아키텍처 문서 조회.
  트리거: RDP 아키텍처, Server Agent 구조, 네트워크 흐름, 용어 설명 요청.
  시스템 구조 이해, 컴포넌트 동작 원리, 용어 정의가 필요할 때 사용.
---

# RDP 아키텍처 문서

QueryPie RDP 접근제어 시스템의 아키텍처 문서를 조회합니다.

## 문서 목록

| 문서 | 내용 | 언제 참조? |
|------|------|-----------|
| `common/arch-index.md` | Quick Start, 문서 구조, 시나리오 | 처음 시작할 때 |
| `common/arch-overview.md` | 전체 아키텍처, 핵심 개념 | 시스템 구조 파악 |
| `common/arch-glossary.md` | 용어집 (AgentId, AgentUuid 등) | 용어가 헷갈릴 때 |
| `common/arch-server-agent.md` | Server Agent 상세 구현 | Server Agent 동작 이해 |
| `common/arch-network.md` | Gateway, Nova, 네트워크 구성 | 네트워크 흐름 파악 |
| `common/arch-deep-dive.md` | 컴포넌트별 심화 분석 | 상세 구현 확인 |
| `common/arch-flows-deep-dive.md` | 연결 흐름 상세 분석 | 흐름 추적 시 |

## 사용 방법

### 질문 유형별 참조 문서

| 질문 유형 | 참조 문서 |
|----------|----------|
| "RDP 시스템 전체 구조가 뭐야?" | arch-index.md → arch-overview.md |
| "AgentId랑 AgentUuid 차이가 뭐야?" | arch-glossary.md |
| "Server Agent가 어떻게 동작해?" | arch-server-agent.md |
| "Gateway랑 Nova 차이가 뭐야?" | arch-network.md |
| "RDP 연결 흐름 설명해줘" | arch-flows-deep-dive.md |
| "ARiSA가 뭐야?" | arch-overview.md → arch-deep-dive.md |

### 문서 조회 순서

1. **개요 파악**: arch-index.md (5분 요약)
2. **구조 이해**: arch-overview.md (전체 아키텍처)
3. **상세 확인**: 필요한 문서 선택

## 핵심 컴포넌트 요약

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Multi-Agent │ ──→ │   ARiSA     │ ──→ │Server Agent │ ──→ │ Windows RDP │
│ (사용자 PC)  │     │  (프록시)    │     │(Windows서버)│     │  (3389)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

| 컴포넌트 | 역할 | 소스 경로 |
|---------|------|----------|
| Multi-Agent | 사용자 PC에서 RDP 클라이언트와 ARiSA 중개 | `apps/multi-agent` |
| ARiSA | RDP 트래픽 프록시, JWT 인증 | `apps/arisa` |
| Server Agent | Windows Server에서 RDP 접근제어 | `apps/winsac` |
| Policy API | 정책 관리, 세션 저장 | `apps/api` |
