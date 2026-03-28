# PR 자동 리뷰 시스템 설계

**날짜:** 2026-03-26
**상태:** 부분 구현 완료 (config, skill 파일 완성 / cron·ralph-loop 운영 설정 미완)

---

## 개요

GitHub에서 지정한 repo 목록 및 리뷰 요청받은 PR을 5분마다 모니터링하고, 새 커밋이 감지되면 코드 리뷰를 수행한 뒤 GitHub PR에 직접 댓글을 게시하는 시스템.

이 설계는 **Claude Code**와 **Codex**가 같은 PR을 각각 독립적으로 리뷰하는 이중 시스템을 전제로 한다. 두 에이전트는 대상 PR 선정 규칙은 공유하지만, 상태 파일과 댓글 중복 판정은 에이전트별로 분리한다.

즉, 동일한 PR과 동일한 HEAD SHA에 대해:

- Claude Code 리뷰 1회
- Codex 리뷰 1회

는 모두 정상 동작으로 간주한다.

---

## 요구사항

| 항목 | 내용 |
|------|------|
| 실행 환경 | 로컬 macOS |
| 실행 주체 | Claude Code 세션, Codex cron |
| 모니터링 대상 | 지정 repo 목록 + 리뷰 요청받은 PR 전체 |
| 리뷰 출력 | GitHub PR에 자동 댓글 게시 |
| 실행 주기 | 5분마다 |
| 재리뷰 기준 | 새 HEAD SHA 감지 시 |
| 이중 시스템 | Claude / Codex가 같은 PR을 각각 따로 리뷰 |

---

## 아키텍처

```
                    공통 정책
        (PR 선정 / 상태 스키마 / 댓글 헤더 / 재시도 규칙)
                           |
         ---------------------------------------------
         |                                           |
         v                                           v
   [Claude Code]                               [Codex]
 /ralph-loop --interval 5m              cron: */5 * * * * codex ...
         |                                           |
         v                                           v
  skills/ops/pr-auto-review.md             skills/ops/pr-auto-review.md
         |                                           |
         v                                           v
 ~/.claude/pr-review-state.json             ~/.codex/pr-review-state.json
         |                                           |
         v                                           v
  gh pr diff → Claude 분석               gh pr diff → Codex 분석
  → 정규화 댓글 게시                       → 정규화 댓글 게시
  (/code-review는 분석 보조로만)
         |                                           |
         v                                           v
 gh comment verify/update                   gh comment verify/update
```

단일 skill 문서를 유지하되, 문서 안에서 공통 정책과 플랫폼별 실행 계약을 분리해 명시한다.

---

## 컴포넌트

### 신규 파일

| 파일 | 역할 |
|------|------|
| `skills-jk/skills/ops/pr-auto-review.md` | 양 플랫폼에서 호출되는 메인 skill |
| `skills-jk/config/pr-auto-review.yml` | 모니터링 repo 목록, 최대 처리 수 등 설정 |
| `~/.claude/pr-review-state.json` | Claude Code 상태 파일 |
| `~/.codex/pr-review-state.json` | Codex 상태 파일 |

### 재활용 컴포넌트

| 컴포넌트 | Claude Code | Codex |
|----------|-------------|-------|
| 반복 실행 | `/ralph-loop` | cron |
| 리뷰 엔진 | Claude 보조 리뷰 + 정규화 게시 | Codex 자체 리뷰 로직 |
| PR 조회/댓글 게시 | `gh` CLI | `gh` CLI |

---

## 설정 파일

### `skills-jk/config/pr-auto-review.yml`

```yaml
repos:
  - chequer-io/deck
  - querypie/querypie-docs

max_prs_per_run: 10
```

### 상태 파일 스키마

각 에이전트는 동일한 JSON 스키마를 사용하되, 파일은 분리한다.

```json
{
  "chequer-io/deck#123": {
    "head_sha": "abc1234",
    "reviewed_at": "2026-03-26T20:00:00+09:00",
    "outcome": "commented",
    "comment_tag": "[auto-review:claude][sha:abc1234]"
  }
}
```

`comment_tag`는 `outcome=commented`일 때만 채워질 수 있으며, clean review는 `outcome=no_findings`와 함께 저장한다.

- Claude Code: `~/.claude/pr-review-state.json`
- Codex: `~/.codex/pr-review-state.json`

---

## Claude 기능 -> Codex 대응

Claude Code 전용 개념을 Codex 구현으로 옮길 때는 아래 매핑을 기준으로 한다.

| Claude Code 개념 | Codex 대응 | 설계에서의 의미 |
|------------------|------------|-----------------|
| 플러그인 | MCP 서버, Skills | 외부 도구 연동은 MCP, 재사용 워크플로우는 Skills로 대체 |
| `/command` | Codex CLI 서브커맨드, Skills, 일부 내장 slash command | 범용 slash command 확장 대신 `codex exec`, `codex review`, Skills 조합으로 구현 |
| `/code-review` | `gh pr diff` + Codex 자체 리뷰 로직 | `codex review`는 local diff용 옵션이 있지만 PR URL 입력은 받지 않으므로, 이번 설계에서는 `gh pr diff` 기반 흐름을 사용 |
| `/ralph-loop` | Codex Automations 또는 cron + `codex exec` | 이번 설계에서는 로컬 macOS cron을 채택 |
| Claude 전용 custom skill | Codex skill | 공통 정책은 같은 skill 문서에 두고, 실행기는 플랫폼별로 다르게 연결 |
| `CLAUDE.md` 지침 로드 | `AGENTS.md` 및 Codex 작업 지침 로드 | Codex는 Claude 전용 지침에 직접 의존하지 않고 저장소 지침을 우선 참조 |

주의사항:

- Codex에는 Claude와 완전히 동일한 범용 `/command` 체계가 있다고 가정하지 않는다.
- Codex 구현은 Claude 플러그인을 흉내 내는 방식이 아니라, Codex의 네이티브 기능으로 동등한 결과를 만드는 방식으로 설계한다.

---

## 공통 정책

### 1. 대상 PR 선정

매 실행마다 아래 두 소스에서 열린 PR을 수집한다.

1. `review-requested=@me` PR
2. 설정 파일의 지정 repo에 존재하는 열린 PR

수집 후 처리 규칙:

- 중복 제거 기준: `repo + pr_number`
- 정렬 기준: `createdAt` 오름차순
- 처리 상한: `max_prs_per_run`

예시 명령:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh search prs --review-requested=@me --state open --json number,repository,createdAt,url,isDraft
env -u GITHUB_TOKEN -u GH_TOKEN gh pr list --repo <owner/repo> --state open --json number,createdAt,headRefOid,isDraft,url
```

`gh` 조회 결과만으로 `headRefOid`가 부족한 경우, 후속 `gh pr view`로 보강한다.

### 2. 재리뷰 기준

재리뷰 판정 키는 아래 4개 요소다.

- `repo`
- `pr_number`
- `head_sha`
- `agent`

판정 규칙:

- 같은 에이전트가 같은 `head_sha`에 대해 `outcome=commented` 또는 `outcome=no_findings`로 상태를 기록했다면 skip
- 다른 에이전트의 리뷰 존재는 skip 조건이 아님
- 댓글 게시가 실패한 경우에는 리뷰 완료로 간주하지 않음

### 3. 댓글 포맷

에이전트별 댓글은 아래 헤더를 반드시 포함한다.

- Claude Code: `[auto-review:claude][sha:<head_sha>]`
- Codex: `[auto-review:codex][sha:<head_sha>]`

댓글 본문은 기존 코드 리뷰 형식을 따르되, 최소한 아래 구조를 유지한다.

```text
[auto-review:codex][sha:abc1234]

## Warning
- path/to/file.ext:123 - finding summary

## Suggestion
- path/to/other.ext:45 - suggestion summary
```

중복 판정 기준:

- 같은 PR에서
- 같은 에이전트 헤더와
- 같은 SHA 헤더가

이미 존재하면 해당 SHA는 재게시하지 않는다.

### 4. 정상 완료 처리

- actionable finding이 없으면 댓글 없이 `outcome=no_findings`로 상태 기록
- 같은 SHA의 댓글이 이미 존재: skip, 상태는 최신화 가능

### 5. 실패 처리

- 리뷰 생성 실패: 상태 미기록
- 댓글 게시 실패: 상태 미기록
- 상태 파일 손상: 빈 상태로 복구 후 진행

---

## 단일 Skill 문서 구조

`skills/ops/pr-auto-review.md`는 단일 문서를 유지하되, 아래 순서로 구성한다.

1. 공통 정책 로드
2. 실행 환경 판별
3. PR 수집 및 상태 비교
4. 플랫폼별 리뷰 실행
5. 댓글 존재 재검증
6. 성공 시 상태 기록

환경 판별은 "어느 런타임에서 호출되었는가"를 기준으로 한다. 파일 시스템에 특정 디렉토리가 있는지만으로 판별하지 않는다.

---

## Claude Code 실행 계약

### 실행 방식

Claude Code 세션에서 아래와 같이 반복 실행한다.

```text
/ralph-loop --interval 5m "Review pending PRs (agent=claude): load ~/workspace/skills-jk/skills/ops/pr-auto-review.md and execute it"
```

세션이 종료되면 자동 리뷰도 중단된다.

### 리뷰 수행 방식

- 공통 정책으로 PR 선정 및 상태 비교 수행
- 리뷰 단계에서만 Claude 전용 기능 사용
- `/code-review <PR URL>`는 분석 보조로 사용할 수 있음
- 최종 게시 댓글은 skill이 공통 헤더 규칙에 맞게 정규화해 직접 검증함

### 성공 판정

아래 조건을 모두 만족해야 성공으로 본다.

1. Claude 리뷰 분석 단계가 실패하지 않음
2. 아래 둘 중 하나를 만족함
   - PR에 `[auto-review:claude][sha:<head_sha>]` 댓글이 실제로 존재함
   - actionable finding이 없어 `outcome=no_findings`로 상태 기록함
3. 그 이후에만 `~/.claude/pr-review-state.json` 기록

### 실패 판정

아래 중 하나라도 발생하면 실패다.

- Claude 리뷰 분석 실패
- 댓글 미게시
- 게시된 댓글에 Claude 헤더 또는 SHA 헤더 누락

실패 시 상태는 기록하지 않으며, 다음 주기에 동일 SHA를 재시도한다.

### 운영 한계

- Claude Code 세션이 살아 있어야만 동작
- 장시간 무인 운영에는 적합하지 않음
- Codex와 달리 세션 독립형 백그라운드 실행을 보장하지 않음

---

## Codex 실행 계약

### 실행 방식

Codex CLI를 cron으로 5분마다 실행한다.

```cron
*/5 * * * * HOME=/Users/jk PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin /opt/homebrew/bin/codex exec "Review pending PRs (agent=codex): load /Users/jk/workspace/skills-jk/skills/ops/pr-auto-review.md and execute it"
```

### 리뷰 수행 방식

- 공통 정책으로 PR 선정 및 상태 비교 수행
- `/code-review` 같은 Claude 전용 플러그인에는 의존하지 않음
- Codex가 직접 PR diff를 읽고 리뷰 코멘트를 생성
- `codex review`는 local diff(`--base`, `--commit`)용 옵션은 있지만 PR URL을 직접 입력받지 않으므로 이 흐름에서는 사용하지 않음
- 필요 시 내부적으로 병렬 에이전트 구조를 사용할 수 있으나, 외부 계약은 단일 댓글 게시로 고정

### GitHub 계약

모든 GitHub 조회와 댓글 게시에는 아래 형식을 사용한다.

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh ...
```

댓글 게시 직전과 직후에 `[auto-review:codex][sha:<head_sha>]` 존재 여부를 확인한다.

### 성공 판정

아래 조건을 모두 만족해야 성공으로 본다.

1. 리뷰 결과 생성 성공
2. 아래 둘 중 하나를 만족함
   - PR에 `[auto-review:codex][sha:<head_sha>]` 댓글이 실제로 게시됨
   - actionable finding이 없어 `outcome=no_findings`로 상태 기록함
3. 그 이후에만 `~/.codex/pr-review-state.json` 기록

### 실패 판정

아래 중 하나라도 발생하면 실패다.

- 리뷰 생성 실패
- `gh` 조회 실패
- `gh` 댓글 게시 실패
- 게시 후 Codex 헤더 또는 SHA 헤더 불일치

실패 시 상태는 기록하지 않으며, 다음 주기에 동일 SHA를 재시도한다.

### 리뷰 출력 규칙

Codex 자동 리뷰 댓글은 deterministic하게 제한한다.

- 허용 섹션: `Critical`, `Warning`, `Suggestion`
- 근거 없는 추정성 항목은 게시하지 않음
- 파일/라인 근거가 없는 항목은 게시하지 않음
- finding이 없으면 댓글은 생략하되, 같은 SHA 재처리를 막기 위해 `outcome=no_findings`로 상태 기록

---

## 재리뷰 범위

새 커밋 push 시 **전체 PR diff (base -> new HEAD)** 기준으로 다시 리뷰한다.

동일 SHA에 대해:

- Claude Code는 자기 댓글만 중복 판정한다.
- Codex는 자기 댓글만 중복 판정한다.
- 서로의 댓글은 중복으로 취급하지 않는다.

---

## 오류 처리

| 상황 | 처리 방법 |
|------|----------|
| `gh` 인증 실패 | 해당 실행 건너뜀, 상태 미변경 |
| 상태 파일 없음 | 빈 상태로 시작 |
| 상태 파일 손상 | 백업 후 빈 상태로 재초기화 |
| PR가 닫힘/드래프트 전환 | skip |
| 댓글은 있는데 상태 파일이 없음 | 댓글 기준으로 중복 판정 후 상태 복구 가능 |

---

## 구현 순서

1. ~~`config/pr-auto-review.yml` 추가~~ ✅
2. ~~`skills/ops/pr-auto-review.md` 초안 작성~~ ✅
3. 공통 PR 수집/정렬/중복 제거 로직 구현
4. 상태 파일 read/write 로직 구현
5. Codex 댓글 포맷과 중복 판정 구현
6. Claude 댓글 검증 로직 구현
7. cron 및 `/ralph-loop` 운영 설정

---

## 한계 및 주의사항

- 두 에이전트가 같은 PR에 각각 댓글을 남기는 것은 의도된 동작이다.
- 같은 SHA에 대해 최대 2개의 자동 리뷰 댓글이 생길 수 있다.
- Claude 전용 기능과 Codex 전용 기능은 구현이 다르더라도, 공통 정책은 반드시 유지해야 한다.
- 이 설계의 핵심은 "실행기는 분리, 정책은 공유"다.
