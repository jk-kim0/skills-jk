---
name: jira-debug-fetch-ticket
description: |
  Jira 티켓 정보를 조회합니다.
  사용: /jira-debug-fetch-ticket QCP-4832
allowed-tools:
  - mcp__atlassian__jira_get_issue
  - mcp__atlassian__jira_search
  - Bash
---

# Fetch Ticket Skill

Jira 티켓의 상세 정보를 조회합니다. MCP와 CLI 두 가지 방법을 지원합니다.

## 사용법

```
/jira-debug-fetch-ticket QCP-4832
```

## 환경변수 설정 (최초 1회)

`.Codex/.env` 또는 `~/.zshrc`에 추가:

```bash
export JIRA_URL="https://querypie.atlassian.net"
export JIRA_USERNAME="your-email@chequer.io"
export JIRA_API_TOKEN="<jira-api-token>"
```

토큰 발급: https://id.atlassian.com/manage-profile/security/api-tokens

## 실행 방법

### 방법 1: MCP 사용 (MCP가 설정된 경우)

MCP `atlassian` 서버가 연결되어 있으면 이 방법을 우선 사용합니다:

```
mcp__atlassian__jira_get_issue(issue_key="QCP-4832", fields="*all", comment_limit=50)
```

### 방법 2: Jira CLI 사용 (MCP가 없는 경우)

MCP가 설정되지 않은 경우 `jira` CLI를 사용합니다:

```bash
# 기본 정보 조회
jira issue view QCP-4832

# JSON 형식으로 상세 조회
jira issue view QCP-4832 --raw | jq '.'

# 특정 필드만 조회
jira issue view QCP-4832 --raw | jq '{
  key: .key,
  summary: .fields.summary,
  status: .fields.status.name,
  priority: .fields.priority.name,
  reporter: .fields.reporter.displayName,
  assignee: .fields.assignee.displayName,
  created: .fields.created,
  updated: .fields.updated,
  description: .fields.description,
  comments: [.fields.comment.comments[] | {author: .author.displayName, body: .body, created: .created}]
}'
```

**Jira CLI 설치:**
```bash
brew install jira-cli
jira init  # 최초 설정
```

## 조회 정보

- 제목, 설명, 상태, 우선순위
- 보고자, 담당자
- 생성일/수정일
- 댓글, 첨부파일

## 도구 선택 로직

1. MCP `mcp__atlassian__jira_get_issue` 도구가 사용 가능한지 확인
2. 사용 가능하면 MCP 사용
3. 사용 불가능하면 `jira` CLI 사용

## 에러 처리

| 에러 | 원인 | 해결 |
|------|------|------|
| `Invalid URL` | 환경변수 미설정 | `.Codex/.env` 또는 `~/.zshrc`에 환경변수 추가 |
| `401 Unauthorized` | 토큰 문제 | `JIRA_API_TOKEN` 확인/재발급 |
| `404 Not Found` | 티켓 없음 | 티켓 번호 확인 |
| `jira: command not found` | CLI 미설치 | `brew install jira-cli` |

## 다음 단계

이 스킬의 출력은 다음 스킬들에서 사용됩니다:
- `/jira-debug-identify-components` - 컴포넌트 식별
- `/jira-debug-analyze-issue-detail` - 에러 상세 분석
