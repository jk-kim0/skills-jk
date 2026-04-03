# Debate Review: Persistent Agent + Append-Only Prompt Design

## Status: Proposed

## 문서 구성

- baseline architecture와 상태 전이 규칙은 [2026-03-30-debate-review-core-design.md](./2026-03-30-debate-review-core-design.md)를 따른다.
- CLI 경계와 subcommand 계약은 [2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)를 따른다.
- 이 문서는 persistent agent mode가 baseline 설계를 어떻게 확장하는지 설명한다.
- 현재 유효한 implementation backlog는 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.

## Current Implementation Checkpoint (2026-04-03)

이미 `main`에 반영된 항목:

- `agent_mode` / `persistent_agents` 상태 필드
- `record-agent-sessions` CLI
- `agent-initial-prompt.md`, `prompt-step-{1,2,3}.md`, `build-prompt`
- persistent mode 기본값 전환
- `settle-round`의 `debate_ledger` 정산 반영 (`#162`)
- 다중 플래그 시 application phase sequential 실행 보장 (`#163`)
- duplicate withdrawal의 state-side 1차 반영 (`#164`)
- Phase 2 commit SHA full-length 정규화 (`#165`)
- round / step timing instrumentation (`#166`)

현재 가장 시급한 blocker는 `#161`이다.

- `build-prompt` 출력이 invalid JSON이어서 persistent agent 초기화가 시작 단계에서 실패한다.
- duplicate withdrawal은 state-side 기반 반영까지는 들어왔지만, prompt/state parity는 아직 닫히지 않았다.
- 나머지 active backlog는 orchestration path, operational follow-through, E2E verification이며 canonical 목록은 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에 둔다.

## Background

기존 debate-review는 라운드당 3회, 최대 10라운드에서 독립 agent를 반복 생성했다. persistent mode는 이 비용과 맥락 손실을 줄이기 위해 세션 시작 시 CC/Codex agent를 한 번만 만들고, 이후 step instruction을 append-only 방식으로 이어 붙이는 설계다.

핵심 차이:

- agent instance를 매 step 새로 만들지 않는다.
- 이전 판단과 파일 탐색 결과를 conversation history에 유지한다.
- prompt caching이 자연스럽게 적용된다.
- 상태 전이와 정산은 기존 CLI primitive를 계속 사용한다.

## Design Overview

### Core Idea

1. CC와 Codex 각각 persistent agent instance를 유지한다.
2. Orchestrator는 매 step마다 새 instruction만 전달한다.
3. 상태 전이와 checkpoint는 `bin/debate-review`가 담당한다.
4. prompt asset은 initial prompt 1개와 step prompt 3개로 나뉜다.

### Architecture

```
CC Orchestrator
  ├── CC agent session
  ├── Codex agent session
  └── debate-review CLI/state engine
```

### Implemented Foundation

아래 항목은 이미 코드와 운영 문서로 존재한다.

- prompt 자산:
  [`agent-initial-prompt.md`](../../skills/cc-codex-debate-review/agent-initial-prompt.md),
  [`prompt-step-1.md`](../../skills/cc-codex-debate-review/prompt-step-1.md),
  [`prompt-step-2.md`](../../skills/cc-codex-debate-review/prompt-step-2.md),
  [`prompt-step-3.md`](../../skills/cc-codex-debate-review/prompt-step-3.md)
- prompt builder / session metadata:
  [`prompt.py`](../../skills/cc-codex-debate-review/lib/debate_review/prompt.py),
  [`cli.py`](../../skills/cc-codex-debate-review/lib/debate_review/cli.py),
  [`state.py`](../../skills/cc-codex-debate-review/lib/debate_review/state.py)
- runtime guide:
  [`SKILL.md`](../../skills/cc-codex-debate-review/SKILL.md),
  [`REFERENCE.md`](../../skills/cc-codex-debate-review/REFERENCE.md)
- verification:
  [`test_prompt.py`](../../skills/cc-codex-debate-review/tests/test_prompt.py),
  [`test_prompt_docs.py`](../../skills/cc-codex-debate-review/tests/test_prompt_docs.py),
  [`test_cli.py`](../../skills/cc-codex-debate-review/tests/test_cli.py)

## Current Design-Sensitive Gaps

이 문서는 더 이상 step-by-step implementation plan을 담지 않는다. 현재 유효한 설계 민감 이슈만 남긴다.

- `#161`: `build-prompt` output JSON 안정화
- persistent step prompt와 state routing의 schema 정합성
- restart / recovery / supersede의 실제 런타임 검증
- terminal follow-through의 재현 가능한 orchestration path

세부 backlog와 우선순위는 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.
