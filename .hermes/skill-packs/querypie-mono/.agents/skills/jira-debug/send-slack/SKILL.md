---
name: jira-debug-send-slack
description: |
  Slack DM으로 메시지를 전송합니다.
  사용: /jira-debug-send-slack "메시지"
allowed-tools:
  - mcp__slack__slack_post_message
  - mcp__slack__slack_get_users
  - Bash
---

# Send Slack Skill

Slack DM으로 메시지를 전송합니다. MCP와 CLI 두 가지 방법을 지원합니다.

## 사용법

```
/jira-debug-send-slack "메시지 내용"
```

발신자: Jira Debug Bot (Bot Token 사용)

## 환경변수 설정

`.Codex/.env` 파일에 추가:

```bash
# Bot Token (1Password "CS Debug Slack Bot"에서 복사)
SLACK_BOT_TOKEN=<slack-bot-token>

# 본인 User ID (Slack 프로필에서 복사)
SLACK_USER_ID=U0XXXXXXXXX
```

설정 가이드: [Jira Debug README](../README.md)

## 실행 방법

### 방법 1: MCP 사용 (MCP가 설정된 경우)

MCP `slack` 서버가 연결되어 있으면 이 방법을 우선 사용합니다:

```
1. 환경변수에서 User ID 읽기
   source .Codex/.env && echo $SLACK_USER_ID

2. MCP slack으로 DM 전송
   mcp__slack__slack_post_message(channel_id="$SLACK_USER_ID", text="메시지")
```

### 방법 2: curl 사용 (MCP가 없는 경우)

MCP가 설정되지 않은 경우 Slack API를 직접 호출합니다:

```bash
# 환경변수 로드
source .Codex/.env

# DM 채널 열기 (최초 1회)
CHANNEL_ID=$(curl -s -X POST "https://slack.com/api/conversations.open" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"users\": \"$SLACK_USER_ID\"}" | jq -r '.channel.id')

# 메시지 전송
curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"$CHANNEL_ID\",
    \"text\": \"메시지 내용\"
  }" | jq '.ok'
```

**간단한 형태 (User ID로 직접 전송):**

```bash
source .Codex/.env

curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"$SLACK_USER_ID\",
    \"text\": \"$MESSAGE\"
  }"
```

## 도구 선택 로직

1. MCP `mcp__slack__slack_post_message` 도구가 사용 가능한지 확인
2. 사용 가능하면 MCP 사용
3. 사용 불가능하면 `curl` 로 Slack API 직접 호출

## 메시지 포맷팅

Slack 마크다운 형식:

| 형식 | Slack 문법 | 예시 |
|------|-----------|------|
| 굵게 | `*text*` | *굵은 텍스트* |
| 기울임 | `_text_` | _기울임 텍스트_ |
| 코드 | `` `code` `` | `코드` |
| 코드 블록 | ` ```code``` ` | 코드 블록 |
| 링크 | `<URL\|표시텍스트>` | 클릭 가능한 링크 |
| 이모지 | `:emoji_name:` | :memo: |

## 분석 리포트 메시지 작성 가이드

**중요**: jira-debug 워크플로우에서 분석 결과를 Slack으로 전송할 때:

- `.Codex/reports/{TICKET_KEY}-analysis.md` 리포트의 **대부분의 내용을 포함**하여 전송
- 너무 요약하지 말고, 티켓 정보 / 관련 컴포넌트 / 데이터 흐름 / 원인 분석 / 권장 대응 등 주요 섹션을 모두 포함
- 섹션 구분은 이모지와 구분선(`---`)을 활용하여 가독성 확보
- Slack 메시지 최대 길이(약 4,000자) 초과 시에만 일부 축소

## 에러 처리

| 에러 | 원인 | 해결 |
|------|------|------|
| `invalid_auth` | 토큰 문제 | `.Codex/.env`에서 `SLACK_BOT_TOKEN` 확인 (1Password에서 최신 토큰) |
| `channel_not_found` | User ID 오류 | `SLACK_USER_ID` 확인 (Slack 프로필에서 재복사) |
| `not_authed` | MCP 연결 실패 | curl 방식으로 fallback |
| `missing_scope` | Bot 권한 부족 | Bot에 `chat:write`, `im:write` 권한 필요 |

## 토큰 유효성 테스트

```bash
source .Codex/.env

# Bot Token 테스트
curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test | jq '{ok, user, team}'
```

- `"ok": true`가 표시되면 정상

## 이전 단계

이 스킬은 다음 스킬들의 결과를 받아 실행합니다:
- `/jira-debug-generate-report` - 전송할 리포트 내용
