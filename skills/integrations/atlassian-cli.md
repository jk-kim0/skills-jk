---
name: atlassian-cli
description: Jira 이슈 조회/생성, Confluence 스페이스/페이지 관리 시 사용
tags: [jira, confluence, atlassian, cli, acli, integration]
---

# Atlassian CLI (ACLI)

## 개요

Atlassian 공식 CLI 도구로 Jira, Confluence에 접근합니다.

| 항목 | 값 |
|------|-----|
| 명령어 | `acli` |
| 위치 | `/usr/local/bin/acli` |
| 버전 | 1.3.13-stable |

## 인증

```bash
# 로그인 (OAuth 브라우저 인증)
acli auth login

# 상태 확인
acli auth status

# 계정 전환
acli auth switch

# 로그아웃
acli auth logout
```

## Jira 명령어

### 프로젝트

```bash
# 프로젝트 목록
acli jira project list

# 프로젝트 상세
acli jira project view <PROJECT_KEY>
```

### 이슈 (Work Item)

```bash
# 이슈 검색 (JQL)
acli jira workitem search --jql "project = PROJ AND status = 'In Progress'"

# 이슈 상세 조회
acli jira workitem view <ISSUE_KEY>

# 이슈 생성
acli jira workitem create --project PROJ --type Task --summary "제목"

# 이슈 수정
acli jira workitem edit <ISSUE_KEY> --summary "새 제목"

# 이슈 상태 전환
acli jira workitem transition <ISSUE_KEY> --status "Done"

# 이슈 담당자 지정
acli jira workitem assign <ISSUE_KEY> --assignee "user@example.com"

# 이슈 복제
acli jira workitem clone <ISSUE_KEY>

# 이슈 삭제
acli jira workitem delete <ISSUE_KEY>
```

### 댓글

```bash
# 댓글 목록
acli jira workitem comment list <ISSUE_KEY>

# 댓글 추가
acli jira workitem comment add <ISSUE_KEY> --body "댓글 내용"
```

### 첨부파일

```bash
# 첨부파일 목록
acli jira workitem attachment list <ISSUE_KEY>

# 첨부파일 추가
acli jira workitem attachment add <ISSUE_KEY> --file /path/to/file
```

### 스프린트

```bash
# 스프린트 목록
acli jira sprint list --board <BOARD_ID>

# 스프린트 상세
acli jira sprint view <SPRINT_ID>
```

### 보드

```bash
# 보드 목록
acli jira board list

# 보드 상세
acli jira board view <BOARD_ID>
```

## Confluence 명령어

### 스페이스

```bash
# 스페이스 목록
acli confluence space list

# 스페이스 상세
acli confluence space view <SPACE_KEY>
```

## 설치 방법

### Homebrew (macOS)

```bash
brew tap atlassian/homebrew-acli
brew install acli
```

### 직접 다운로드 (macOS)

```bash
# Apple Silicon
curl -LO "https://acli.atlassian.com/darwin/latest/acli_darwin_arm64/acli"

# Intel
curl -LO "https://acli.atlassian.com/darwin/latest/acli_darwin_amd64/acli"

chmod +x ./acli
sudo mv ./acli /usr/local/bin/acli
```

## 주의사항

- OAuth 인증 필요 (`acli auth login`)
- 버전은 릴리스 후 6개월간만 지원됨
- Atlassian Government Cloud는 미지원

## 참고 링크

- [ACLI 공식 문서](https://developer.atlassian.com/cloud/acli/guides/introduction/)
- [ACLI 설치 가이드](https://developer.atlassian.com/cloud/acli/guides/install-acli/)
