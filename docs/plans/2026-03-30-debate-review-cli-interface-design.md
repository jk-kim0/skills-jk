# Debate Review CLI Reference

**작성일:** 2026-03-30  
**상태:** Final, implemented

## Purpose

이 문서는 `run-debate-review` 오케스트레이터와 `debate-review` CLI 사이의 최종 계약을 정리한 reference 문서다.
process plan이나 rollout checklist는 포함하지 않는다.

## Scope Rules

- 모든 mutating 명령은 `--state-file` 기반으로 동작한다
- `init`만 `--repo`, `--pr`를 받는다
- same-repo PR만 허용한다
- `gh` 호출은 keyring 인증 기준으로 수행한다

## Entrypoints

- orchestrator: [`run-debate-review`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/bin/run-debate-review)
- state CLI: [`debate-review`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/bin/debate-review)

## Command Groups

### Session Bootstrap

#### `init`

입력:

- `--repo <owner/repo>`
- `--pr <number>`
- optional: `--repo-root`, `--config`, `--max-rounds`, `--dry-run`

동작:

- PR metadata 조회
- same-repo 여부 확인
- fork PR이면 즉시 에러 반환
- state file 생성 또는 resume

구현: [`cli.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/cli.py)

#### `show`

- state 요약 또는 `--json` 출력

#### `record-agent-sessions`

- persistent agent handle 저장

#### `report-sessions`

- debate-state와 runtime artifacts를 스캔해 full-session report 생성

### Round / Debate Flow

#### `sync-head`

- PR HEAD 조회
- synthetic ref fetch
- worktree reset
- supersede 감지

구현: [`sync.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/sync.py)

#### `init-round`

- current round metadata 생성
- `journal.round`, `journal.step` 초기화

#### `upsert-issue`

- finding을 stable issue로 생성/갱신

#### `record-verdict`

- step1 verdict 기록
- clean pass 판정

#### `record-cross-verification`

- step2 accept/rebut 기록

#### `resolve-rebuttals`

- step1a 또는 step3 decision 반영

#### `withdraw-issue`

- agent가 자신이 연 issue를 철회

#### `record-application`

3-phase 기록 API:

1. applied/failed issue 기록
2. commit SHA 기록
3. push verification

구현: [`application.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/application.py)

#### `mark-cross-verifier-clean-pass`

- same-round consensus용 step2 clean pass flag 기록

#### `settle-round`

- settled/unresolved issue 계산
- consensus / stalled / max rounds 판정

구현: [`round_ops.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/round_ops.py)

### Prompt / Message Helpers

#### `build-prompt`

- init 또는 step message 생성
- persistent prompt file에 append

구현: [`prompt.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/prompt.py)

#### `build-commit-message`

- applied issue를 바탕으로 commit subject/body 생성

### Terminal / Ops

#### `post-comment`

- 최종 PR comment 생성/게시/중복 방지

#### `mark-failed`

- terminal failed state 기록

#### `create-failure-issue`

- error/stalled outcome일 때 GitHub issue 생성

#### `cleanup-worktree`

- debate worktree 제거

#### `terminate-agents`

- persistent agent process cleanup

## Output Contract

CLI는 stdout으로 JSON object를 반환한다.

- success: subcommand별 result object
- error: `{"error": "..."}`
- dry-run mutation: `{"action":"dry_run", ...}`

## State Expectations

핵심 상태 규칙:

- `init` 이전에는 다른 명령을 호출하지 않는다
- `record-application`은 3-phase 순서를 유지한다
- terminal state 이후 같은 HEAD면 resume가 아니라 completion으로 본다
- agent handle은 `persistent_agents` block에 저장한다

정확한 validation/migration은 [`state.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/state.py) 를 따른다.

## Orchestrator Boundary

CLI가 담당하는 것:

- 상태 전이
- validation
- deterministic bookkeeping
- prompt file/build helpers
- final comment / failure follow-through helper

오케스트레이터가 담당하는 것:

- step 순서
- persistent agent subprocess lifecycle
- runtime supervision/recovery
- live progress output

구현 참조:

- orchestrator: [`orchestrator.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/orchestrator.py)
- runtime supervision: [`runtime_supervision.py`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/runtime_supervision.py)

## Retained References

- architecture: [2026-03-30-debate-review-core-design.md](./2026-03-30-debate-review-core-design.md)
- runtime procedure: [`SKILL.md`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/SKILL.md)
- placeholder/prompt mapping: [`REFERENCE.md`](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/REFERENCE.md)
