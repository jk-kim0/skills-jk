---
name: atlassian-mcp
description: Jira 이슈 조회/생성, Confluence 페이지 조회/편집 시 사용
tags: [jira, confluence, atlassian, mcp, integration]
---

# Atlassian MCP Integration

## 개요

MCP(Model Context Protocol) 서버를 통해 Jira와 Confluence에 접근합니다.

| 서비스 | MCP 서버 | 도구 접두사 |
|--------|----------|-------------|
| Jira | `@aashari/mcp-server-atlassian-jira` | `jira_*` |
| Confluence | `@aashari/mcp-server-atlassian-confluence` | `conf_*` |

## 사용 가능한 도구

### Jira

| 도구 | 용도 |
|------|------|
| `jira_get` | 데이터 조회 (프로젝트, 이슈, 댓글 등) |
| `jira_post` | 리소스 생성 (이슈, 댓글 등) |
| `jira_put` | 리소스 전체 교체 |
| `jira_patch` | 리소스 부분 수정 |
| `jira_delete` | 리소스 삭제 |

### Confluence

| 도구 | 용도 |
|------|------|
| `conf_get` | 데이터 조회 (스페이스, 페이지 등) |
| `conf_post` | 리소스 생성 (페이지, 댓글 등) |
| `conf_put` | 리소스 전체 교체 |
| `conf_patch` | 리소스 부분 수정 |
| `conf_delete` | 리소스 삭제 |

## 공통 파라미터

```
path        (필수) API 엔드포인트 경로
queryParams (선택) 쿼리 파라미터 객체
body        (선택) 요청 본문 (POST/PUT/PATCH)
jq          (선택) JMESPath 필터링 표현식
outputFormat (선택) "toon" (기본값) 또는 "json"
```

## Jira 사용 예시

### 프로젝트 목록 조회

```
도구: jira_get
path: /rest/api/3/project
```

### 이슈 검색 (JQL)

```
도구: jira_get
path: /rest/api/3/search
queryParams: { "jql": "project = MYPROJ AND status = 'In Progress'" }
```

### 특정 이슈 조회

```
도구: jira_get
path: /rest/api/3/issue/MYPROJ-123
```

### 이슈 생성

```
도구: jira_post
path: /rest/api/3/issue
body: {
  "fields": {
    "project": { "key": "MYPROJ" },
    "summary": "이슈 제목",
    "issuetype": { "name": "Task" },
    "description": {
      "type": "doc",
      "version": 1,
      "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "설명" }] }]
    }
  }
}
```

### 이슈 상태 변경

```
도구: jira_post
path: /rest/api/3/issue/MYPROJ-123/transitions
body: { "transition": { "id": "31" } }
```

## Confluence 사용 예시

### 스페이스 목록 조회

```
도구: conf_get
path: /wiki/api/v2/spaces
```

### 페이지 검색 (CQL)

```
도구: conf_get
path: /wiki/rest/api/search
queryParams: { "cql": "space = MYSPACE AND type = page" }
```

### 특정 페이지 조회

```
도구: conf_get
path: /wiki/api/v2/pages/{pageId}
queryParams: { "body-format": "storage" }
```

### 페이지 생성

```
도구: conf_post
path: /wiki/api/v2/pages
body: {
  "spaceId": "123456",
  "title": "페이지 제목",
  "body": {
    "representation": "storage",
    "value": "<p>페이지 내용</p>"
  }
}
```

## 설정 방법

`~/.claude/mcp.json`에 추가:

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-jira"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-site",
        "ATLASSIAN_USER_EMAIL": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    },
    "confluence": {
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-confluence"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-site",
        "ATLASSIAN_USER_EMAIL": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**API 토큰 생성:** https://id.atlassian.com/manage-profile/security/api-tokens

## 주의사항

- API 토큰은 절대 코드에 하드코딩하지 않음
- `outputFormat: "toon"`이 기본값으로 토큰 효율적
- JMESPath(`jq`)로 필요한 필드만 추출하면 응답 크기 감소

## 참고 링크

- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [MCP Server Jira](https://github.com/aashari/mcp-server-atlassian-jira)
- [MCP Server Confluence](https://github.com/aashari/mcp-server-atlassian-confluence)
