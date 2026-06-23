---
name: jira-debug-setup
description: |
  jira-debug 환경 설정을 도와줍니다.
  - 환경변수 검증
  - Self-service / Guided 모드 선택
  - .env 파일 자동 생성
  사용: /jira-debug-setup
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

# Jira Debug Setup Skill

jira-debug 사용을 위한 환경 설정을 도와주는 스킬입니다.

## 사용법

```
/jira-debug-setup
```

또는 `/jira-debug` 실행 시 환경이 미설정되어 있으면 자동으로 안내합니다.

## 워크플로우

### Step 1: 환경 상태 확인

다음을 순차적으로 확인합니다:

1. **파일 존재 확인**:
   ```bash
   test -f .Codex/.env && echo "exists" || echo "not_found"
   ```

2. **필수 환경변수 확인** (파일이 있는 경우):
   ```bash
   source .Codex/.env 2>/dev/null
   [ -z "$JIRA_API_TOKEN" ] && echo "JIRA_API_TOKEN 미설정"
   [ -z "$SLACK_BOT_TOKEN" ] && echo "SLACK_BOT_TOKEN 미설정"
   [ -z "$SLACK_USER_ID" ] && echo "SLACK_USER_ID 미설정"
   ```

### Step 2: 미설정 항목 발견 시 모드 선택

미설정 항목이 있으면 AskUserQuestion으로 설정 방식을 질문:

```
header: "설정 방식"
question: "jira-debug 환경 설정이 필요합니다. 어떤 방식으로 설정할까요?"
options:
  - label: "직접 설정할게요 (Self-service)"
    description: "가이드 문서 출력 후 직접 .env 파일을 편집합니다"
  - label: "단계별 안내 받을게요 (Guided)"
    description: "질문에 답하면 .env 파일이 자동으로 생성됩니다"
multiSelect: false
```

---

## Self-service 모드

가이드 문서를 출력하고 종료합니다:

```markdown
## 🔧 jira-debug 설정 가이드

### Step 1: 환경변수 파일 생성

```bash
cp .Codex/.env.example .Codex/.env
```

### Step 2: Jira API Token 발급

👉 https://id.atlassian.com/manage-profile/security/api-tokens

1. "Create API token" 클릭
2. 라벨 입력: `jira-debug`
3. 토큰 복사 (Jira API Token 형식)

### Step 3: Slack 설정

**Bot Token:**
- 1Password에서 "CS Debug Slack Bot" 검색
- 토큰 복사 (형식: `<slack-bot-token>`)

**User ID:**
- Slack 열기 → 본인 프로필 클릭
- ⋮ (더보기) → "멤버 ID 복사"
- 형식: `U0XXXXXXXXX`

### Step 4: .env 파일 편집

`.Codex/.env` 파일을 열고 다음 값들을 입력:

```bash
JIRA_URL=https://querypie.atlassian.net
JIRA_USERNAME=your-email@chequer.io
JIRA_API_TOKEN=<jira-api-token>

SLACK_BOT_TOKEN=<slack-bot-token>
SLACK_TEAM_ID=T03L6852Y
SLACK_USER_ID=U0XXXXXXXXX
```

### Step 5: 설정 완료

설정이 완료되면 다음 명령어로 테스트하세요:

```bash
/jira-debug QCP-XXXX
```
```

---

## Guided 모드

AskUserQuestion으로 값을 수집한 후 Write 도구로 .env 파일을 생성합니다.

### 질문 1: Jira 이메일

```
header: "Jira 이메일"
question: "📧 회사 이메일 주소를 입력해주세요. (예: yourname@chequer.io)"
options:
  - label: "@chequer.io 이메일"
    description: "예: yourname@chequer.io"
multiSelect: false
```
→ 사용자가 Other 선택 후 이메일 입력

### 질문 2: Jira API Token

```
header: "Jira Token"
question: "🔑 Jira API Token을 입력해주세요.\n\n👉 발급: https://id.atlassian.com/manage-profile/security/api-tokens\n\n형식: <jira-api-token>"
options:
  - label: "토큰 입력"
    description: "위 링크에서 토큰을 발급받아 입력하세요"
multiSelect: false
```
→ 사용자가 Other 선택 후 토큰 입력

### 질문 3: Slack Bot Token

```
header: "Slack Token"
question: "🤖 Slack Bot Token을 입력해주세요.\n\n1Password에서 'CS Debug Slack Bot' 검색\n형식: <slack-bot-token>"
options:
  - label: "토큰 입력"
    description: "1Password에서 복사한 토큰을 입력하세요"
multiSelect: false
```
→ 사용자가 Other 선택 후 토큰 입력

### 질문 4: Slack User ID

```
header: "Slack User ID"
question: "👤 본인의 Slack User ID를 입력해주세요.\n\nSlack 프로필 > ⋮ > '멤버 ID 복사'\n형식: U0XXXXXXXXX"
options:
  - label: "User ID 입력"
    description: "U로 시작하는 11자리 ID를 입력하세요"
multiSelect: false
```
→ 사용자가 Other 선택 후 User ID 입력

### .env 파일 생성

모든 값을 수집하면 Write 도구로 파일 생성:

```bash
# CS Debug 로컬 설정
# 자동 생성됨 - /jira-debug-setup

# ===== Jira 설정 =====
JIRA_URL=https://querypie.atlassian.net
JIRA_USERNAME={입력받은_이메일}
JIRA_API_TOKEN={입력받은_토큰}

# ===== Slack 설정 =====
SLACK_BOT_TOKEN={입력받은_봇토큰}
SLACK_TEAM_ID=T03L6852Y
SLACK_USER_ID={입력받은_유저ID}
```

### 완료 메시지

```markdown
✅ **설정 완료!**

다음 환경변수가 `.Codex/.env`에 저장되었습니다:
- JIRA_USERNAME: {이메일}
- JIRA_API_TOKEN: <jira-api-token> (설정됨)
- SLACK_BOT_TOKEN: <slack-bot-token> (설정됨)
- SLACK_USER_ID: {유저ID}

이제 `/jira-debug QCP-XXXX`를 실행할 수 있습니다!
```

---

## 모든 설정이 완료된 경우

환경변수가 모두 설정되어 있으면:

```markdown
✅ **환경 설정이 완료되어 있습니다!**

현재 설정:
- JIRA_USERNAME: {이메일}
- JIRA_API_TOKEN: ****xxxx (설정됨)
- SLACK_BOT_TOKEN: <slack-bot-token> (설정됨)
- SLACK_USER_ID: {유저ID}

재설정이 필요하면 `.Codex/.env` 파일을 직접 수정하거나,
파일을 삭제 후 `/jira-debug-setup`을 다시 실행하세요.
```

---

## 에러 처리

| 상황 | 대응 |
|------|------|
| .env.example 없음 | 템플릿 내용 직접 생성 |
| 잘못된 토큰 형식 | 형식 안내 후 재입력 요청 |
| Write 권한 없음 | 수동 설정 안내 |

---

## 참고

- 설정 가이드: [Jira Debug README](../README.md)
- .env.example: [../../.env.example](../../.env.example)
