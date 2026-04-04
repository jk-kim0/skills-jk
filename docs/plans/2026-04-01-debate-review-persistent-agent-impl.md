# Debate Review: Persistent Agent Completion Backlog

## 문서 구성

- baseline architecture는 [2026-03-30-debate-review-core-design.md](./2026-03-30-debate-review-core-design.md)에 있다.
- CLI 경계와 상태 관리 계약은 [2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)에 있다.
- persistent mode 설계 설명은 [2026-04-01-debate-review-persistent-agent-design.md](./2026-04-01-debate-review-persistent-agent-design.md)에 있다.
- 이 문서는 현재 시점의 debate-review completion backlog만 관리한다.

## 현재 체크포인트 (2026-04-04)

현재 `main`에는 아래 기반이 이미 구현돼 있다.

- `agent_mode` / `persistent_agents` 상태 필드
- persistent prompt 자산 및 `build-prompt`
- `record-agent-sessions` / resume metadata
- 기본값 `persistent`
- `settle-round`의 `debate_ledger` 정산 반영 (`#162`)
- 다중 플래그 시 application phase sequential 실행 보장 (`#163`)
- duplicate withdrawal의 state-side 1차 반영 (`#164`)
- Step 3 Phase 2의 short SHA 정규화 (`#165`)
- round / step timing instrumentation (`#166`)
- `build-prompt` JSON 출력 zsh echo 손상 수정 (`#168`) — persistent 초기화 blocker 해소
- `build-prompt` init 경로 temp file 누수 수정 + CLI-level 테스트 추가 (`#168` debate-review 결과)
- Step 3 prompt/routing에 `withdrawals` 필드 추가 (`#169`)
- operational follow-through CLI 명령 추가: `create-failure-issue`, `update-pr-status`, `cleanup-worktree` (`#170`)
- orchestration runner: round loop, agent dispatch, checkpoint/recovery, terminal processing (`#171`, merged)

## Implemented Foundation

과거 rollout 계획에서 실제로 구현된 기반은 아래 코드와 문서에서 확인할 수 있다.

- persistent mode 설정과 상태 필드:
  [`config.yml`](../../skills/cc-codex-debate-review/config.yml),
  [`config.py`](../../skills/cc-codex-debate-review/lib/debate_review/config.py),
  [`state.py`](../../skills/cc-codex-debate-review/lib/debate_review/state.py)
- prompt 생성과 세션 메타데이터:
  [`prompt.py`](../../skills/cc-codex-debate-review/lib/debate_review/prompt.py),
  [`cli.py`](../../skills/cc-codex-debate-review/lib/debate_review/cli.py),
  [`agent-initial-prompt.md`](../../skills/cc-codex-debate-review/agent-initial-prompt.md),
  [`prompt-step-1.md`](../../skills/cc-codex-debate-review/prompt-step-1.md),
  [`prompt-step-2.md`](../../skills/cc-codex-debate-review/prompt-step-2.md),
  [`prompt-step-3.md`](../../skills/cc-codex-debate-review/prompt-step-3.md)
- 운영 절차와 런타임 가이드:
  [`SKILL.md`](../../skills/cc-codex-debate-review/SKILL.md),
  [`REFERENCE.md`](../../skills/cc-codex-debate-review/REFERENCE.md)
- operational follow-through:
  [`follow_through.py`](../../skills/cc-codex-debate-review/lib/debate_review/follow_through.py)
- 검증:
  [`test_cli.py`](../../skills/cc-codex-debate-review/tests/test_cli.py),
  [`test_prompt.py`](../../skills/cc-codex-debate-review/tests/test_prompt.py),
  [`test_prompt_docs.py`](../../skills/cc-codex-debate-review/tests/test_prompt_docs.py),
  [`test_state.py`](../../skills/cc-codex-debate-review/tests/test_state.py),
  [`test_timing.py`](../../skills/cc-codex-debate-review/tests/test_timing.py),
  [`test_follow_through.py`](../../skills/cc-codex-debate-review/tests/test_follow_through.py)

## Completion Criteria

완료 기준은 아래 다섯 가지다.

1. debate-review를 end-to-end로 실행하는 repo-owned orchestration path가 존재한다.
2. 기본 모드인 `persistent` 경로가 최신 schema와 완전히 일치하고, 초기화 경로가 실제로 동작한다.
3. resume / recovery / supersede / terminal processing이 자동화되어 있다.
4. 문서에만 있는 운영 절차가 코드 또는 검증 가능한 helper로 내려온다.
5. 핵심 시나리오를 덮는 end-to-end 테스트가 있다.

## Current Remaining Work

### Workstream A: Persistent prompt / routing parity ✅

- ~~`#161`: `build-prompt` output JSON 안정화~~ → `#168`에서 해결
- ~~Step prompt 템플릿의 최신 output schema 반영~~ → Step 3에 `withdrawals` 필드 추가 완료
- ~~duplicate withdrawal state transition을 step prompt, CLI, Step 4 정산까지 일관되게 연결~~ → `#164` + Step 3 prompt/routing 보완으로 완료
- ~~legacy / persistent 간 출력 schema 불일치 제거~~ → legacy `agent-lead-response-prompt.md`에도 `withdrawals` 추가

### Workstream B: Repo-owned orchestration path ✅

`#171` (merged) — Python orchestration runner 구현.

- ~~round loop 실행 경로 추가~~ ✅
- ~~agent 생성 / resume / retry / recovery 구현~~ ✅
- ~~CLI subcommand routing 자동화~~ ✅
- ~~terminal 시 comment / cleanup 호출까지 연결~~ ✅

### Workstream C: Operational follow-through automation ⏳

`#170` (merged) — CLI 명령 구현, `#172` (open) — orchestrator 통합.

- ~~`mark-failed` 후 GitHub issue 생성용 CLI 추가~~ → `create-failure-issue` ✅
- ~~final state 후 PR title 갱신용 CLI 추가~~ → `update-pr-status` ✅
- ~~worktree cleanup CLI 추가~~ → `cleanup-worktree` ✅
- ⏳ orchestrator `_terminal()` / `_mark_failed()` / `_cleanup_worktree()` 연동 → `#172` (open)
- CI / runtime status 추적 → orchestrator의 checkpoint 시스템으로 대체

### Workstream D: E2E verification

- clean pass consensus
- same-repo code apply
- fork recommendation path
- supersede by external push
- persistent resume / recovery
- terminal comment dedupe

## 현재 우선순위

1. ~~`#161` 해소로 persistent initialization 복구~~ ✅
2. ~~persistent prompt / state routing parity 복구~~ ✅
3. ~~repo-owned orchestration path 정리~~ ✅
4. failure / cleanup / PR update 자동화 마무리 (`#172` open)
5. end-to-end verification 보강
6. legacy 제거와 문서 정리
