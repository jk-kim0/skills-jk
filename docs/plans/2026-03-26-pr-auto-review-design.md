# PR 자동 리뷰 시스템 설계

**날짜:** 2026-03-26
**상태:** 설계 완료, 구현 예정

---

## 개요

GitHub에서 지정한 repo 목록 및 리뷰 요청받은 PR을 5분마다 모니터링하고, 새 커밋이 감지되면 코드 리뷰를 수행한 뒤 GitHub PR에 직접 댓글을 게시하는 시스템.

**Claude Code**와 **Codex** 두 플랫폼에서 독립적으로 동작하며, 각자 별도의 상태 파일을 관리한다. 두 에이전트가 동일 PR을 중복 리뷰하는 것은 의도된 동작이다.

---

## 요구사항

| 항목 | 내용 |
|------|------|
| 실행 환경 | 로컬 macOS — Claude Code 세션 또는 Codex cron |
| 모니터링 대상 | 지정 repo 목록 + 리뷰 요청받은 PR 전체 |
| 리뷰 출력 | GitHub PR에 자동 댓글 게시 |
| 실행 주기 | 5분마다 |
| 재리뷰 | 새 커밋 push 시 전체 PR diff 기준 재리뷰 |
| 다중 에이전트 | Claude Code / Codex 독립 실행, 상태 별도 관리, 중복 리뷰 허용 |

---

## 아키텍처

```
[Claude Code]                          [Codex]
/ralph-loop --interval 5m              cron: */5 * * * * codex ...
       ↓                                      ↓
  pr-auto-review skill              pr-auto-review skill (동일 파일)
       ↓                                      ↓
  gh CLI → PR 목록 수집              gh CLI → PR 목록 수집
       ↓                                      ↓
  ~/.claude/pr-review-state.json    ~/.codex/pr-review-state.json
  와 비교                            와 비교
       ↓                                      ↓
  /code-review <PR URL> 호출        spawn_agent로 code-review 수행
  (공식 플러그인)                    (인라인 로직)
       ↓                                      ↓
  상태 파일 업데이트                  상태 파일 업데이트
```

두 에이전트는 서로의 상태를 공유하지 않으며, 같은 PR에 각자의 리뷰를 독립적으로 게시한다.

---

## 컴포넌트

### 신규 파일

| 파일 | 역할 |
|------|------|
| `skills-jk/skills/ops/pr-auto-review.md` | 양 플랫폼에서 호출되는 메인 skill |
| `skills-jk/config/pr-auto-review.yml` | 모니터링 repo 목록, 설정 |
| `~/.claude/pr-review-state.json` | Claude Code 리뷰 상태 (자동 관리) |
| `~/.codex/pr-review-state.json` | Codex 리뷰 상태 (자동 관리) |

### 재활용 컴포넌트

| 컴포넌트 | Claude Code | Codex |
|----------|-------------|-------|
| 반복 실행 | `/ralph-loop` 플러그인 | cron (`*/5 * * * *`) |
| 코드 리뷰 | `/code-review` 공식 플러그인 | `spawn_agent` 인라인 구현 |
| PR 목록 조회 | `gh` CLI | `gh` CLI (동일) |

---

## 설정 파일

### `skills-jk/config/pr-auto-review.yml`

```yaml
# github_username은 자동 감지 (gh api user --jq .login)
repos:
  - querypie-tech/querypie-mono
  - querypie-tech/corp-web-app
  # 추가 repo...

max_prs_per_run: 10  # 1회 실행당 처리할 최대 PR 수
```

### 상태 파일 (자동 관리, 플랫폼별 독립)

```json
{
  "querypie-tech/querypie-mono": {
    "123": "abc1234",
    "124": "def5678"
  }
}
```

- Claude Code: `~/.claude/pr-review-state.json`
- Codex: `~/.codex/pr-review-state.json`

---

## pr-auto-review Skill 실행 흐름

skill 파일은 단일 파일(`skills/ops/pr-auto-review.md`)이며, 실행 환경(Claude Code / Codex)을 감지해 플랫폼별 동작을 분기한다.

### 공통 흐름 (양 플랫폼)

1. **설정 로드**: `config/pr-auto-review.yml` 읽기 (사용자명은 `gh api user --jq .login` 자동 감지, PR 조회에는 `@me` 사용)
2. **PR 목록 수집**:
   - `gh search prs --review-requested=@me --state=open`
   - 각 지정 repo: `gh pr list --repo <repo> --state open`
   - 중복 제거 후 최대 `max_prs_per_run`개 (PR 생성일 오름차순)
3. **변경 감지**: 플랫폼별 상태 파일과 비교 — `PR번호 + HEAD commit SHA`가 변경된 것만 선별
4. **각 PR 리뷰** — 플랫폼별 방식으로 수행 (아래 참조)
5. **상태 파일 저장** — 성공한 PR만 기록

### Claude Code: 리뷰 수행

```
/code-review <PR URL>
```

공식 플러그인이 CLAUDE.md 로드, 5 parallel Sonnet agents, 신뢰도 필터링(80점 이상만), 기존 댓글 중복 체크를 모두 처리한다.

### Codex: 리뷰 수행

`/code-review` 플러그인이 없으므로 `spawn_agent`로 동등한 로직을 인라인 수행:

1. Haiku agent: PR 기본 정보 조회 (closed/draft/자동화 PR 여부, 기존 Codex 리뷰 댓글 존재 여부 확인)
2. Haiku agent: 관련 CLAUDE.md / AGENTS.md 파일 목록 조회
3. Haiku agent: PR 변경사항 요약
4. 5개 parallel worker agents: 독립 코드 리뷰 수행
   - Agent 1: CLAUDE.md / AGENTS.md 준수 여부
   - Agent 2: 명백한 버그 탐지
   - Agent 3: git blame/history 기반 맥락 검토
   - Agent 4: 이전 PR 코멘트 참조
   - Agent 5: 코드 내 주석 지침 준수 여부
5. 각 이슈에 대해 Haiku agent로 신뢰도 점수 산정 (80점 미만 필터링)
6. `gh pr comment`로 리뷰 결과 게시

---

## 환경 감지

`pr-auto-review` skill은 실행 환경을 다음 기준으로 판별한다:

- `~/.claude/` 디렉토리 존재 → Claude Code
- `~/.codex/` 디렉토리 존재 → Codex
- 상태 파일 경로 및 리뷰 수행 방식 분기

---

## 오류 처리

| 상황 | 처리 방법 |
|------|----------|
| `gh` CLI 실패 (네트워크, 토큰 만료) | 해당 실행 건너뜀, 상태 파일 변경 없음 |
| 리뷰 수행 실패 | 해당 PR 상태 변경 없음 (다음 실행에서 재시도) |
| 상태 파일 없음 / 손상 | 빈 상태로 초기화 후 진행 |
| PR diff 너무 큼 | 파일별 분할 처리 (Claude Code: 플러그인 자체 처리 / Codex: agent가 파일 범위 제한) |

---

## 재리뷰 범위

새 커밋 push 시 **전체 PR diff (base → new HEAD)** 기준으로 리뷰 수행.
각 플랫폼이 독립적으로 기존 자신의 댓글 존재 여부를 확인하므로, 동일 SHA에 대한 중복 게시는 발생하지 않는다.

---

## 실행 방법

### Claude Code

```
/ralph-loop --interval 5m "Review pending PRs: load skills-jk/skills/ops/pr-auto-review.md and execute it"
```

Claude Code 세션이 열려 있는 동안 5분마다 자동 실행된다.

### Codex

crontab에 등록:

```cron
*/5 * * * * /opt/homebrew/bin/codex --yolo "Review pending PRs: load skills-jk/skills/ops/pr-auto-review.md and execute it"
```

macOS에서 백그라운드로 상시 실행된다. 세션 독립적.

- Codex 바이너리: `/opt/homebrew/bin/codex` (v0.116.0)
- `--yolo` 플래그: 확인 프롬프트 없이 자동 실행 (cron 환경에서 필수)

---

## 한계 및 주의사항

- **Claude Code 세션 의존성**: Claude Code는 세션이 활성 상태여야 동작. Codex cron은 세션 무관하게 동작.
- **중복 리뷰 의도**: 두 에이전트가 동일 PR에 각각 댓글을 남기는 것은 설계상 의도된 동작.
- **rate limit**: 두 에이전트가 동시에 실행될 경우 GitHub API 호출이 2배가 되나, 5분 주기 + max 10 PR 기준으로 rate limit(시간당 5,000 요청) 내 안전한 범위.
