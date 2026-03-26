# PR 자동 리뷰 시스템 설계

**날짜:** 2026-03-26
**상태:** 설계 완료, 구현 예정

---

## 개요

GitHub에서 지정한 repo 목록 및 리뷰 요청받은 PR을 5분마다 모니터링하고, 새 커밋이 감지되면 공식 `code-review` 플러그인을 호출해 코드 리뷰를 수행한 뒤 GitHub PR에 직접 댓글을 게시하는 시스템.

Claude Code의 `/ralph-loop` 명령을 활용해 로컬 머신에서 실행되며, 세션이 활성 상태인 동안 지속 동작한다.

---

## 요구사항

| 항목 | 내용 |
|------|------|
| 실행 환경 | 로컬 macOS, Claude Code 세션 내 |
| 모니터링 대상 | 지정 repo 목록 + 리뷰 요청받은 PR 전체 |
| 리뷰 출력 | GitHub PR에 자동 댓글 게시 |
| 리뷰 수행 | 공식 `code-review` 플러그인 위임 (중복 체크 내장) |
| 실행 주기 | 5분마다 |
| 재리뷰 | 새 커밋 push 시 전체 PR diff 기준 재리뷰 |

---

## 아키텍처

```
/ralph-loop --interval 5m "Run /pr-auto-review skill"
       ↓ (5분마다)
  pr-auto-review skill
       ↓
  gh CLI → PR 목록 수집
  (설정 repo 목록 + review-requested, 최대 max_prs_per_run개)
       ↓
  상태 파일 비교 (PR번호 + HEAD SHA)
       ↓ (변경 있는 경우만)
  /code-review <PR URL> 호출
  (중복 댓글 체크, CLAUDE.md 로드, 5 parallel agents, 신뢰도 필터링 내장)
       ↓
  상태 파일 업데이트 (성공한 PR만)
```

---

## 컴포넌트

### 신규 파일

| 파일 | 역할 |
|------|------|
| `skills-jk/skills/ops/pr-auto-review.md` | 루프에서 호출되는 메인 skill |
| `skills-jk/config/pr-auto-review.yml` | 모니터링 repo 목록, 설정 |
| `~/.claude/pr-review-state.json` | 리뷰 완료된 PR + SHA 추적 (로컬 상태) |

### 재활용 컴포넌트

| 컴포넌트 | 용도 |
|----------|------|
| `/ralph-loop` 플러그인 | 5분 주기 반복 실행 |
| `/code-review` 공식 플러그인 | 실제 코드 리뷰 수행 (5 parallel agents, 중복 체크, CLAUDE.md 반영) |
| `gh` CLI | PR 목록 조회 |

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

### `~/.claude/pr-review-state.json` (자동 관리)

```json
{
  "querypie-tech/querypie-mono": {
    "123": "abc1234",
    "124": "def5678"
  }
}
```

---

## pr-auto-review Skill 실행 흐름

매 5분마다 실행 시:

1. **설정 로드**: `config/pr-auto-review.yml` 읽기 (PR 조회에는 `@me` 사용, 사용자명은 로그 출력 목적으로만 `gh api user --jq .login`으로 감지)
2. **PR 목록 수집**:
   - `gh search prs --review-requested=@me --state=open` (`@me`는 gh CLI가 인증된 사용자로 자동 해석하므로 별도 치환 불필요)
   - 각 지정 repo: `gh pr list --repo <repo> --state open`
   - 중복 제거 후 최대 `max_prs_per_run`개로 제한 (PR 생성일 오름차순 — 오래 기다린 PR 우선)
3. **변경 감지**: `~/.claude/pr-review-state.json`과 비교 — `PR번호 + HEAD commit SHA`가 변경된 것만 선별
4. **각 PR 리뷰** (per PR):
   - `/code-review <PR URL>` 호출 (공식 플러그인이 중복 댓글 체크, CLAUDE.md 로드, 신뢰도 필터링 모두 처리)
   - 성공 시에만 상태 파일에 새 SHA 기록
   - 실패 시 상태 유지 (다음 실행 때 재시도)
5. **상태 파일 저장**

---

## 오류 처리

| 상황 | 처리 방법 |
|------|----------|
| `gh` CLI 실패 (네트워크, 토큰 만료) | 해당 실행 건너뜀, 상태 파일 변경 없음 |
| `code-review` 플러그인 실패 | 해당 PR 상태 변경 없음 (다음 실행에서 재시도) |
| 상태 파일 없음 / 손상 | 빈 상태로 초기화 후 진행 (공식 플러그인의 내장 중복 체크가 실제 중복 게시 방지) |
| PR diff 너무 큼 | `code-review` 플러그인이 자체 처리 (파일 범위 제한) |

---

## 재리뷰 범위

새 커밋 push 시 **전체 PR diff (base → new HEAD)** 기준으로 리뷰 수행.
공식 `code-review` 플러그인이 이전 리뷰 댓글 존재 여부를 확인하므로, 중복 게시 없이 업데이트된 상태를 반영한 완전한 리뷰가 이루어진다.

---

## 실행 방법

```
/ralph-loop --interval 5m "Review pending PRs: load skills-jk/skills/ops/pr-auto-review.md and execute it"
```

Claude Code 세션이 열려 있는 동안 5분마다 자동 실행된다.

---

## 한계 및 주의사항

- **세션 의존성**: Claude Code 세션이 활성 상태여야 동작한다. 세션 종료 시 중단되며, 재시작 시 명령어 재입력 필요. 장시간 자리를 비우는 경우 모니터링이 중단되는 것은 설계상 허용된 동작임.
- **rate limit**: 5분 주기 + max 10 PR은 GitHub API rate limit(시간당 5,000 요청) 내 안전한 범위.
- **cron 기반 대안**: 항상 켜진 모니터링이 필요할 경우 macOS LaunchAgent 방식으로 전환 가능하나, 현재 범위 밖.
