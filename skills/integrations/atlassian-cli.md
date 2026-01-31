---
name: atlassian-cli
description: Jira 이슈 조회/검색, Confluence 페이지 조회/검색 시 사용
tags: [jira, confluence, atlassian, cli, integration]
---

# Atlassian CLI

## 개요

Atlassian 서비스에 접근하기 위한 CLI 도구입니다.

| 서비스 | CLI | 위치 |
|--------|-----|------|
| Jira | `jira` | `/usr/local/bin/jira` |
| Confluence | `confluence` | `/usr/local/bin/confluence` |

## Jira CLI

### 명령어

```bash
jira <command> [args]
```

| 명령어 | 설명 |
|--------|------|
| `projects` | 전체 프로젝트 목록 |
| `search <JQL>` | JQL로 이슈 검색 |
| `issue <KEY>` | 이슈 상세 조회 |
| `boards` | 보드 목록 |
| `sprints <BOARD_ID>` | 스프린트 목록 |

### 사용 예시

```bash
# 프로젝트 목록
jira projects

# 이슈 검색
jira search "project = QPD AND status = 'In Progress'"

# 이슈 상세
jira issue QPD-4385

# 보드 목록
jira boards

# 스프린트 목록
jira sprints 42
```

## Confluence CLI

### 명령어

```bash
confluence <command> [args]
```

| 명령어 | 설명 |
|--------|------|
| `spaces` | 전체 글로벌 스페이스 목록 |
| `search <query>` | 페이지 검색 |
| `page <pageId>` | 페이지 내용 조회 |

### 사용 예시

```bash
# 스페이스 목록
confluence spaces

# 페이지 검색
confluence search "API 가이드"

# 페이지 조회
confluence page 12345678
```

## 설정

### 사이트 정보

| 항목 | 값 |
|------|-----|
| Site | querypie.atlassian.net |
| Email | jk@chequer.io |

### API 토큰 생성

https://id.atlassian.com/manage-profile/security/api-tokens

## 참고 링크

- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/)
