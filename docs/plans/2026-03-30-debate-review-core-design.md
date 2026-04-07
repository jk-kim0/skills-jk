# Debate Review Final Design

**작성일:** 2026-03-30  
**상태:** Final, implemented

## Purpose

이 문서는 `cc-codex-debate-review`의 최종 구현 구조를 설명하는 canonical architecture 문서다.
구현 과정에서 사용했던 rollout/spec/plan/report 문서는 유지하지 않으며, 현재 참조 문서는 이 문서와
[2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)
두 개로 한정한다.

## Supported Scope

- same-repo PR만 지원
- fork PR은 `debate-review init` 단계에서 즉시 거부
- 기본 실행 모드는 persistent agent mode
- `DRY_RUN=true`일 때만 review-only 시뮬레이션을 허용

## System Overview

debate-review는 PR 하나에 대해 CC와 Codex가 교대로 lead reviewer가 되면서
리뷰, 반박, 수정, 정산을 반복하는 시스템이다.

최종 구성은 아래 세 층으로 나뉜다.

1. Orchestrator
   - 엔트리포인트: [`run-debate-review`](../../skills/cc-codex-debate-review/bin/run-debate-review)
   - 구현: [`orchestrator.py`](../../skills/cc-codex-debate-review/lib/debate_review/orchestrator.py)
   - 책임: round loop, persistent agent dispatch, checkpoint recovery, terminal 처리
2. State/CLI engine
   - 엔트리포인트: [`debate-review`](../../skills/cc-codex-debate-review/bin/debate-review)
   - 구현: [`cli.py`](../../skills/cc-codex-debate-review/lib/debate_review/cli.py)
   - 책임: 상태 저장, 라운드/이슈 전이, prompt/build helpers, comment/follow-through
3. Persistent agent assets
   - 문서/프롬프트: [`SKILL.md`](../../skills/cc-codex-debate-review/SKILL.md), [`REFERENCE.md`](../../skills/cc-codex-debate-review/REFERENCE.md), [`agent-initial-prompt.md`](../../skills/cc-codex-debate-review/agent-initial-prompt.md), [`prompt-step-1.md`](../../skills/cc-codex-debate-review/prompt-step-1.md), [`prompt-step-2.md`](../../skills/cc-codex-debate-review/prompt-step-2.md), [`prompt-step-3.md`](../../skills/cc-codex-debate-review/prompt-step-3.md)

## Execution Model

### Lifecycle

1. `init`
   - PR metadata 조회
   - same-repo scope 확인
   - state file 생성 또는 resume
2. `sync-head`
   - PR HEAD를 synthetic ref와 worktree로 동기화
   - 외부 push가 감지되면 supersede 처리
3. `init-round`
   - 현재 라운드 metadata 생성
4. Step loop
   - Step 1: lead review
   - Step 2: cross verification
   - Step 3: lead response + code apply
   - Step 4: settlement
5. Terminal
   - final comment
   - failure follow-through
   - worktree cleanup

### Agent Roles

- 홀수 라운드: `codex` lead, `cc` cross
- 짝수 라운드: `cc` lead, `codex` cross
- 두 agent 모두 persistent session으로 유지되고, step prompt만 append-only로 누적된다

### Consensus Rule

합의는 아래 둘 중 하나로 판정된다.

- 같은 round에서 lead clean pass + cross-verifier clean pass
- 연속된 두 completed round가 모두 clean pass이고 lead agent가 서로 다름

구현 기준은 [`round_ops.py`](../../skills/cc-codex-debate-review/lib/debate_review/round_ops.py) 에 있다.

## State Model

상태 파일 경로:

- `~/.claude/debate-state/<owner>-<repo>-<pr>.json`

핵심 top-level field:

- session identity: `repo`, `repo_root`, `pr_number`
- scope/control: `is_fork`, `dry_run`, `max_rounds`, `language`
- head tracking: `head.initial_sha`, `head.last_observed_pr_sha`, `head.target_ref`, `head.synced_worktree_sha`
- restart journal: `journal.round`, `journal.step`, `journal.commit_sha`, `journal.push_verified`
- persistent sessions: `persistent_agents.cc_agent_id`, `persistent_agents.codex_session_id`
- debate data: `issues`, `debate_ledger`, `rounds`
- terminal state: `status`, `final_outcome`, `finished_at`, `final_comment_id`

정확한 validation과 migration은 [`state.py`](../../skills/cc-codex-debate-review/lib/debate_review/state.py) 가 담당한다.

## Runtime Observability

persistent dispatch는 blocking subprocess가 아니라 streaming supervision을 사용한다.

- vendor event normalization: [`runtime_events.py`](../../skills/cc-codex-debate-review/lib/debate_review/runtime_events.py)
- streaming runner: [`runtime_stream.py`](../../skills/cc-codex-debate-review/lib/debate_review/runtime_stream.py)
- heartbeat/stall supervision: [`runtime_supervision.py`](../../skills/cc-codex-debate-review/lib/debate_review/runtime_supervision.py)
- live progress output: [`progress.py`](../../skills/cc-codex-debate-review/lib/debate_review/progress.py)
- timing/traces: [`timing.py`](../../skills/cc-codex-debate-review/lib/debate_review/timing.py)
- session report generation: [`reporting.py`](../../skills/cc-codex-debate-review/lib/debate_review/reporting.py)

## Durable Module Map

- config: [`config.py`](../../skills/cc-codex-debate-review/lib/debate_review/config.py), [`config.yml`](../../skills/cc-codex-debate-review/config.yml)
- prompt composition: [`prompt.py`](../../skills/cc-codex-debate-review/lib/debate_review/prompt.py), [`context.py`](../../skills/cc-codex-debate-review/lib/debate_review/context.py)
- issue transitions: [`issue_ops.py`](../../skills/cc-codex-debate-review/lib/debate_review/issue_ops.py), [`cross_verification.py`](../../skills/cc-codex-debate-review/lib/debate_review/cross_verification.py)
- round/application transitions: [`round_ops.py`](../../skills/cc-codex-debate-review/lib/debate_review/round_ops.py), [`application.py`](../../skills/cc-codex-debate-review/lib/debate_review/application.py)
- sync/comment/follow-through: [`sync.py`](../../skills/cc-codex-debate-review/lib/debate_review/sync.py), [`comment.py`](../../skills/cc-codex-debate-review/lib/debate_review/comment.py), [`follow_through.py`](../../skills/cc-codex-debate-review/lib/debate_review/follow_through.py), [`agent_cleanup.py`](../../skills/cc-codex-debate-review/lib/debate_review/agent_cleanup.py)

## Verification References

최종 구현 검증은 package test suite를 기준으로 한다.

- 전체 suite: `python3 -m pytest`
- 문서/프롬프트 정합성: [`test_prompt_docs.py`](../../skills/cc-codex-debate-review/tests/test_prompt_docs.py)
- CLI/state/orchestrator coverage: [`test_cli.py`](../../skills/cc-codex-debate-review/tests/test_cli.py), [`test_state.py`](../../skills/cc-codex-debate-review/tests/test_state.py), [`test_orchestrator.py`](../../skills/cc-codex-debate-review/tests/test_orchestrator.py)
- runtime/reporting coverage: [`test_runtime_events.py`](../../skills/cc-codex-debate-review/tests/test_runtime_events.py), [`test_runtime_supervision.py`](../../skills/cc-codex-debate-review/tests/test_runtime_supervision.py), [`test_reporting.py`](../../skills/cc-codex-debate-review/tests/test_reporting.py)

## Non-Canonical Material

구현 당시의 step-by-step plan, rollout checklist, generated report는 이 문서 집합의 일부가 아니다.
현재 저장소에서는 최종 구현을 설명하지 않는 debate-review process 문서를 유지하지 않는다.
