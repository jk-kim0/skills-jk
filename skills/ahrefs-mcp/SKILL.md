---
name: ahrefs-mcp
description: Ahrefs SEO 데이터 (백링크, 키워드, 도메인 레이팅) 조회 시 사용
tags: [ahrefs, seo, mcp, keyword, backlink, integration]
---

# Ahrefs MCP

## 개요

Ahrefs MCP는 Claude Code에서 Ahrefs SEO 데이터에 직접 접근할 수 있게 해주는 Model Context Protocol 서버입니다.

| 항목 | 내용 |
|------|------|
| 프로토콜 | MCP (Model Context Protocol) |
| 인증 방식 | OAuth 2.0 (원격) / API v3 키 (로컬) |
| 요구사항 | Ahrefs 유료 구독 |

## 설정 방법

### 방법 1: 원격 MCP 서버 (권장)

로컬 설치 없이 Ahrefs 원격 서버에 직접 연결합니다.

```bash
# MCP 서버 등록
claude mcp add --transport http ahrefs https://api.ahrefs.com/mcp/mcp --scope user
```

**인증 프로세스:**
1. 새 Claude Code 세션 시작
2. Ahrefs 도구 사용 요청 시 브라우저에서 OAuth 인증 화면 표시
3. Ahrefs 계정으로 로그인 후 권한 승인

**요구사항:** Ahrefs 유료 구독 (Lite, Standard, Advanced, Enterprise)

### 방법 2: 로컬 MCP 서버

API v3 키를 사용하여 로컬에서 실행합니다.

```bash
# Node.js 필요
npm -v

# MCP 서버 설치
npm install --prefix=~/.global-node-modules @ahrefs/mcp -g

# 업그레이드
npm install --prefix=~/.global-node-modules @ahrefs/mcp@latest -g
```

`~/.claude.json`에 설정 추가:

```json
{
  "mcpServers": {
    "ahrefs": {
      "command": "npx",
      "args": ["--prefix=/Users/USERNAME/.global-node-modules", "@ahrefs/mcp"],
      "env": {
        "API_KEY": "YOUR_AHREFS_API_V3_KEY"
      }
    }
  }
}
```

**요구사항:** Ahrefs Enterprise 플랜 (API v3 접근용)

**API 키 발급:**
1. [Ahrefs](https://app.ahrefs.com) 로그인
2. 프로필 아이콘 > Account Settings > API 탭
3. Generate API Key > 키 복사 및 안전하게 보관

## 상태 확인

```bash
# MCP 서버 목록 확인
claude mcp list

# 특정 서버 상세 정보
claude mcp get ahrefs

# 서버 제거
claude mcp remove ahrefs --scope user
```

| 상태 | 의미 |
|------|------|
| `connected` | 정상 연결됨 |
| `Needs authentication` | OAuth 인증 필요 |
| `error` | 연결 실패 |

## 사용 가능한 기능

| 기능 | 설명 |
|------|------|
| Site Explorer | 백링크 분석, 도메인 레이팅, 트래픽 추정 |
| Keywords Explorer | 키워드 리서치, 검색량, 난이도 분석 |
| SERP Overview | 검색 결과 페이지 분석 |
| Rank Tracker | 키워드 순위 추적 |
| Site Audit | 사이트 기술 감사 |
| Brand Radar | 브랜드 언급 모니터링 |

## 사용 예시

Claude Code 세션에서:

```
"Ahrefs MCP를 사용해서 example.com의 백링크 프로필을 분석해줘"
"Ahrefs로 'seo tools' 키워드의 검색량과 난이도를 확인해줘"
"Ahrefs 데이터로 competitor.com의 도메인 레이팅을 조회해줘"
```

**팁:** "Ahrefs MCP를 사용해서" 또는 "Ahrefs로"를 명시적으로 언급하면 도구 선택이 더 정확합니다.

## 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| "Needs authentication" 지속 | 새 Claude Code 세션 시작 후 Ahrefs 도구 사용 요청 |
| npm 설치 실패 | Node.js 설치 확인: `npm -v` |
| API 키 오류 | API v3 키 사용 확인 (MCP 키는 지원하지 않음) |
| 권한 오류 (macOS/Linux) | `sudo chown -R $(whoami) ~/.global-node-modules` |
| 설정 미반영 (Claude Desktop) | Task Manager에서 Claude Desktop 종료 후 재시작 |

## 참고 자료

- [Ahrefs MCP Server (GitHub)](https://github.com/ahrefs/ahrefs-mcp-server)
- [Ahrefs API Documentation](https://docs.ahrefs.com/docs/api/reference/introduction)
- [Ahrefs MCP Claude Code Guide](https://docs.ahrefs.com/docs/mcp/reference/claude-code)
