---
name: jira-debug-download-and-organize
description: |
  Jira 티켓 첨부파일 다운로드 및 정리.
  사용: /jira-debug-download-and-organize <ISSUE_KEY>
  예: /jira-debug-download-and-organize QPD-4832
allowed-tools:
  - Bash
---

# Download and Organize Skill

Jira 티켓의 첨부파일을 다운로드하고 댓글 기준으로 정리합니다.

## 사용법

```
/jira-debug-download-and-organize QPD-4832
```

## 실행 방법

### 방법 1: MCP 툴 사용 (권장)

MCP `jira_download_attachments` 툴이 사용 가능하면 이 방법을 우선 사용합니다.

```
1. mcp__atlassian__jira_download_attachments 로 첨부파일 다운로드
   - issue_key: <ISSUE_KEY>
   - target_dir: .Codex/skills/jira-debug/download-and-organize/files/<ISSUE_KEY>

2. 압축 파일 해제
   - zip 파일: unzip -o <file>.zip -d <file>/
   - gz 파일: gunzip -k <file>.gz
```

### 방법 2: 스크립트 사용

MCP 툴을 사용할 수 없거나, README 자동 생성이 필요한 경우:

```bash
.Codex/skills/jira-debug/scripts/download_and_organize.sh <ISSUE_KEY>
```

## 기능

- 모든 첨부파일 자동 다운로드
- 디렉토리 구조 자동 생성
- README.md 자동 생성
- 압축 파일 자동 해제 (zip, gz)

## 의존성

- `jira` CLI
- `jq`
- `curl`
- `unzip` (선택)

## 출력 위치

`.Codex/skills/jira-debug/download-and-organize/files/<ISSUE_KEY>/`

> `files/` 디렉토리는 `.gitignore`로 관리되어 Git에 포함되지 않습니다.

## 환경변수

| 변수 | 필수 | 설명 |
|------|:----:|------|
| `JIRA_API_TOKEN` | O | Jira API 토큰 |
| `JIRA_USERNAME` | O | Jira 사용자 이메일 |
| `JIRA_URL` | - | Jira 서버 URL (기본값: https://querypie.atlassian.net) |

> `.Codex/.env.example`을 참고하여 `.Codex/.env` 파일을 생성하세요.

## 출력 구조 예시

```
.Codex/skills/jira-debug/download-and-organize/files/QPD-4832/
├── README.md
├── 00_unmatched/           # 댓글과 매핑되지 않은 파일
│   └── screenshot.png
├── 01_20240115_로그_파일/   # 첫 번째 댓글 첨부파일
│   ├── README.md
│   └── server_agent.log
└── 02_20240116_추가_자료/   # 두 번째 댓글 첨부파일
    ├── README.md
    └── SystemLog.evtx
```
