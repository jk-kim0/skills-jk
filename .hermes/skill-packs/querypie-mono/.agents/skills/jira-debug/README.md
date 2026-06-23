# Jira Debug

Jira 티켓을 분석하고 querypie-mono-3 코드베이스에서 원인을 찾아 Slack DM으로 결과를 전송하는 Claude Code 플러그인입니다.

## MCP vs CLI

이 플러그인은 **MCP**와 **CLI** 두 가지 방식을 모두 지원합니다:

| 방식 | 장점 | 단점 |
|------|------|------|
| **MCP** | 더 빠르고 편리 | 추가 설정 필요 |
| **CLI** | 별도 설정 없이 사용 | `jira-cli` 설치 필요 |

MCP를 사용하려면 개인 설정 파일(`~/.claude/.mcp.json`)에 설정을 추가하세요 (아래 "MCP 설정 (선택)" 참고).

## 3분 퀵스타트

> **모든 설정은 `.claude/.env` 파일 하나에서 관리됩니다.**

### 1. 환경 설정

```bash
cd querypie-mono-3
claude

# Claude 내에서
/jira-debug-setup
```

또는 수동으로:

```bash
cd querypie-mono-3/.claude
cp .env.example .env
# .env 파일 편집
```

### 2. 실행

```bash
/jira-debug QCP-4832
```

---

## 토큰 발급

| 항목 | 발급 방법 | 저장 위치 |
|------|----------|----------|
| **Jira API Token** | https://id.atlassian.com/manage-profile/security/api-tokens | `.claude/.env` |
| **Slack Bot Token** | 1Password "CS Debug Slack Bot" | `.claude/.env` |
| **Slack User ID** | Slack 프로필 > ⋮ > 멤버 ID 복사 | `.claude/.env` |

### Jira API Token 발급 (개인별)

1. https://id.atlassian.com/manage-profile/security/api-tokens 접속
2. **"Create API token"** 클릭
3. 라벨 입력 (예: "CS Debug")
4. 생성된 토큰 복사

### Slack 설정

Bot Token은 팀 공용으로 1Password에서 가져오고, User ID만 개인별로 설정합니다.

**Bot Token 가져오기 (팀 공용)**:
1. **1Password** 접속
2. **"CS Debug Slack Bot"** 검색
3. `SLACK_BOT_TOKEN` 값 복사 (Slack Bot Token 형식)

**본인 Slack User ID 확인 (개인별)**:
1. **Slack** 열기
2. 좌측 상단 본인 이름 클릭 → **"프로필 보기"**
3. **⋮ (더보기)** 클릭 → **"멤버 ID 복사"**
4. `U0XXXXXXXXX` 형식의 ID가 복사됩니다

### .env 파일 설정

`.claude/.env` 파일을 열고 다음과 같이 입력:

```bash
# Jira
JIRA_URL=https://querypie.atlassian.net
JIRA_USERNAME=your-email@chequer.io
JIRA_API_TOKEN=생성된-토큰

# Slack - Bot Token (1Password에서 복사)
SLACK_BOT_TOKEN=<slack-bot-token>

# Slack - 본인 User ID (Slack에서 복사)
SLACK_USER_ID=U0XXXXXXXXX
```

> **Note**: Bot Token은 팀 공용이므로 모두 같은 값을 사용합니다. User ID만 각자 다르게 설정하면 됩니다.

---

## 워크플로우

```
/jira-debug QCP-4832
    │
    ├─▶ 0. 환경 설정 확인 (미설정 시 /jira-debug-setup 안내)
    ├─▶ 1. Jira 티켓 조회 (MCP atlassian)
    ├─▶ 2. 컴포넌트 식별 (신뢰도 기반)
    ├─▶ 3. 에러 상세 분석
    ├─▶ 4. 코드 검색
    ├─▶ 5. 리포트 생성
    └─▶ 6. Slack DM 전송 (MCP slack)
```

---

## 개별 스킬

```bash
/jira-debug-setup                      # 환경 설정 (Self-service / Guided)
/jira-debug-fetch-ticket QCP-4832      # Jira 티켓 조회
/jira-debug-identify-components        # 컴포넌트 식별
/jira-debug-analyze-issue-detail       # 에러 상세 분석
/jira-debug-search-code "keyword"      # 코드 검색
/jira-debug-generate-report            # 리포트 생성
/jira-debug-send-slack "message"       # Slack 전송
```

---

## 설정 체크리스트

- [ ] `.claude/.env` 파일 생성 완료
- [ ] `JIRA_USERNAME` 설정 (본인 이메일)
- [ ] `JIRA_API_TOKEN` 설정 (개인 발급)
- [ ] `SLACK_BOT_TOKEN` 설정 (1Password에서 복사, Slack Bot Token 형식)
- [ ] `SLACK_USER_ID` 설정 (본인 User ID, `U0`로 시작)
- [ ] Claude Code 재시작 후 `/jira-debug` 명령어 실행 가능

### 테스트 실행

```bash
cd querypie-mono-3
claude

# Claude 내에서
/jira-debug-send-slack "테스트 메시지"
```

자신의 Slack DM으로 메시지가 도착하면 성공입니다!

---

## 문제 해결

### 환경변수 확인

```bash
# 모든 설정은 .claude/.env에서 관리
cat .claude/.env
source .claude/.env

# 각 환경변수 확인
echo $JIRA_API_TOKEN
echo $SLACK_BOT_TOKEN
echo $SLACK_USER_ID
```

### 환경 재설정

```bash
# Claude 내에서
/jira-debug-setup
```

### Slack MCP 연결 오류

**증상**: "Slack MCP server not connected" 또는 "invalid_auth" 에러

**해결 방법**:

1. `.claude/.env` 파일 확인:
   ```bash
   cat .claude/.env
   ```

2. 환경변수 로드 확인:
   ```bash
   source .claude/.env
   echo $SLACK_BOT_TOKEN
   echo $SLACK_USER_ID
   ```

3. 토큰 형식 확인:
   - `SLACK_BOT_TOKEN`: Slack Bot Token 형식해야 함
   - `SLACK_USER_ID`: `U0`로 시작해야 함

4. Bot Token 테스트:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     https://slack.com/api/auth.test | jq
   ```
   - `"ok": true`가 표시되면 정상

5. 토큰이 만료되었거나 잘못된 경우:
   - 1Password에서 최신 `SLACK_BOT_TOKEN` 확인
   - 팀 리드에게 문의

### Jira 조회 실패

**증상**: "Failed to fetch Jira issue" 에러

**해결 방법**:

1. 환경변수 확인:
   ```bash
   echo $JIRA_URL
   echo $JIRA_USERNAME
   echo $JIRA_API_TOKEN
   ```

2. Jira API Token 유효성 확인:
   - https://id.atlassian.com/manage-profile/security/api-tokens
   - 토큰이 만료되었으면 재발급

### MCP 서버 재시작

Claude Code를 완전히 종료하고 다시 시작:

```bash
# Claude Code 종료 (Ctrl+D 또는 /exit)
# 터미널에서
claude
```

---

## 고급 설정

### 환경변수 자동 로드 (direnv 사용)

프로젝트 디렉토리로 이동할 때 자동으로 `.env`를 로드하려면:

```bash
# direnv 설치
brew install direnv

# .envrc 파일 생성
echo 'dotenv .claude/.env' > .envrc

# 승인
direnv allow
```

이제 `cd querypie-mono-3`만 해도 자동으로 환경변수가 로드됩니다.

---

## 파일 구조

```
.claude/
├── commands/
│   └── jira-debug.md           # /jira-debug 커맨드
├── skills/
│   └── jira-debug/             # 그룹화된 스킬들
│       ├── README.md           # 이 문서
│       ├── setup/SKILL.md      # 환경 설정
│       ├── fetch-ticket/SKILL.md
│       ├── identify-components/SKILL.md
│       ├── analyze-issue-detail/SKILL.md
│       ├── search-code/SKILL.md
│       ├── generate-report/SKILL.md
│       └── send-slack/SKILL.md
├── memories/                   # 라벨링 데이터
├── reports/                    # 생성된 리포트
├── .env                        # 환경변수 (gitignore)
└── .env.example                # 환경변수 템플릿
```

---

---

## MCP 설정 (선택)

MCP를 사용하면 더 빠르고 편리하게 Jira/Slack 연동을 할 수 있습니다.

### 개인 MCP 설정 파일 생성

`~/.claude/.mcp.json` 파일을 생성합니다:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://querypie.atlassian.net",
        "JIRA_USERNAME": "your-email@chequer.io",
        "JIRA_API_TOKEN": "your-jira-token"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "<slack-bot-token>",
        "SLACK_TEAM_ID": "T03L6852Y"
      }
    }
  }
}
```

### MCP 없이 CLI만 사용

MCP 설정 없이도 모든 기능을 사용할 수 있습니다:

- **Jira**: `jira-cli` 사용 (`brew install jira-cli`)
- **Slack**: `curl`로 Slack API 직접 호출

---

## 추가 도움

- 설정 중 문제가 발생하면 `/jira-debug-setup`을 다시 실행하세요.
- 팀 리드에게 문의하거나 GitHub Issues에 등록해주세요.
