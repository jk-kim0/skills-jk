# Debate Review Agent Status Supervision Design

## Goal

`cc-codex-debate-review`의 persistent mode에서 실행 중인 `Claude Code` 및 `Codex` subprocess의 상태를 5~10초 주기로 관찰하고, 이를 이용자에게 실시간으로 표시하며, 정상적인 장기 추론과 비정상 stall/무응답을 구분할 수 있는 supervision layer를 추가한다.

이 설계의 목표는 응답 시간을 인위적으로 줄이는 것이 아니다. 리뷰 범위와 깊이는 유지한 채, 다음을 가능하게 만드는 것이 목표다.

- 실행 중인 agent의 현재 상태를 이용자에게 보여주기
- “오래 걸리지만 정상 진행 중”과 “오동작으로 멈춤”을 구분하기
- stall 발생 시 단계적 복구를 수행하기
- 사후 분석에 필요한 로그와 타이밍 데이터를 남기기

## Non-Goals

- `legacy` mode 최적화
- PR 리뷰 범위 축소를 통한 응답 시간 단축
- terminal UI의 기존 activity indicator를 그대로 복제하기
- `codex app-server` 기반 전면 재구현

## Current State

현재 persistent orchestration의 핵심 흐름은 [orchestrator.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/orchestrator.py) 에 있다.

- step dispatch는 `_dispatch_step()`에서 처리한다.
- prompt 생성은 `build_prompt()`를 통해 수행되고, 결과는 `prompt_file`과 `message_file`로 나뉜다.
- 실제 runtime dispatch는 `adapter.send_message()`가 수행한다.
- dispatch는 현재 `_run_command()` 기반 `subprocess.run()`으로 동기 대기한다.
- `ProgressReporter`는 [progress.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/progress.py) 에서 30초마다 단순 elapsed line만 출력한다.
- `step_traces`는 [timing.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/timing.py) 에 저장되지만, mid-flight heartbeat나 stall evidence는 저장하지 않는다.

이 구조의 한계는 명확하다.

1. `send_message()`가 반환될 때까지 orchestrator가 agent 내부 진행 상황을 모른다.
2. 이용자에게는 “30초 지남”만 보이고, 실제로 agent가 생각 중인지 멈췄는지 보이지 않는다.
3. `subagent_log_path`는 응답 이후에야 알 수 있으므로, live stall detector의 1차 신호로 쓰기 어렵다.
4. stall이 나면 현재는 `OrchestrationError` 경로에서만 recovery가 동작하므로, “무응답 hang”를 잡지 못한다.

## Runtime Signals Already Available

subprocess 레벨에서 읽을 수 있는 신호는 이미 존재한다.

### Codex

- `codex exec --json`
- `codex exec resume --json`

위 명령은 stdout에 JSONL event를 순차적으로 기록한다. 로컬 실험에서 다음 이벤트를 확인했다.

- `thread.started`
- `turn.started`
- `item.completed`
- `turn.completed`

OpenAI 문서도 `--json`을 “one per state change” 형식의 JSONL 이벤트 출력으로 설명한다.

### Claude Code

- `claude -p --verbose --output-format stream-json --include-partial-messages`
- resume 경로도 같은 형식 사용 가능

로컬 실험에서 다음 이벤트를 확인했다.

- `system/hook_started`
- `system/init`
- `stream_event.message_start`
- `stream_event.content_block_delta`
- `assistant`
- `rate_limit_event`
- `result`

Claude Code의 `status line`은 별도 API가 아니라 하단 UI 커스터마이즈 기능이다. subprocess supervision의 주 신호로는 `stream-json`이 더 적합하다.

## Chosen Approach: Hybrid Supervision

세 가지 대안 중 `stdout event streaming + fallback polling`의 hybrid 방식을 채택한다.

### Why not log polling only

- `subagent_log_path`는 dispatch가 끝난 뒤에만 확보된다.
- 따라서 “응답이 오지 않는 동안”의 상태 판정에는 부적합하다.

### Why not app-server rewrite first

- `codex app-server`는 더 구조화된 이벤트를 주지만, 현재 debate-review runtime은 CLI subprocess 호출을 전제로 설계되어 있다.
- app-server 전환은 기능 요구보다 migration scope가 크다.

### Why hybrid

- live 상태는 stdout streaming event가 가장 신뢰도가 높다.
- 사후 포렌식과 mismatch 확인은 state/log file polling이 유용하다.
- stall 복구의 false positive를 줄이려면 단일 신호보다 조합 판정이 필요하다.

## Proposed Architecture

### New Runtime Components

1. `StreamingProcessRunner`
- `subprocess.run()` 대신 `subprocess.Popen()`을 사용한다.
- stdout/stderr를 line-buffered로 소비한다.
- 5~10초 주기로 supervision tick을 발생시킨다.

2. `AgentEventNormalizer`
- Codex와 Claude Code의 raw event를 공통 event schema로 정규화한다.
- downstream은 vendor별 raw event shape를 몰라도 된다.

3. `StepSupervisor`
- 현재 step의 health, heartbeat, stall score, recovery state를 관리한다.
- `ProgressReporter`와 `record_step_trace()`에 중간 상태를 전달한다.

4. `ProgressReporter v2`
- 단순 elapsed timer 대신 “현재 상태 + 최근 heartbeat + 경과시간”을 stderr에 출력한다.

## Normalized Event Schema

vendor별 raw event를 다음 공통 schema로 매핑한다.

```json
{
  "ts": "2026-04-06T03:12:45.123Z",
  "agent": "cc",
  "phase": "stream",
  "kind": "message_delta",
  "status": "active",
  "summary": "partial assistant text",
  "raw_type": "stream_event.content_block_delta",
  "meta": {}
}
```

필수 필드:

- `ts`: observer timestamp
- `agent`: `cc` or `codex`
- `phase`: `spawn`, `resume`, `stream`, `result`, `recovery`
- `kind`: normalized semantic event
- `status`: `active`, `idle`, `warning`, `error`, `completed`
- `summary`: 이용자 표시에 쓸 짧은 문구
- `raw_type`: 원본 event type
- `meta`: vendor-specific detail

## Event Mapping

### Codex Mapping

| Raw event | Normalized kind | User-facing meaning |
| --- | --- | --- |
| `thread.started` | `session_started` | persistent session usable |
| `turn.started` | `turn_started` | 새 step 처리 시작 |
| `item.completed` + `agent_message` | `assistant_output` | agent 응답 생성 |
| `turn.completed` | `turn_completed` | step 종료, usage 확보 |

Codex는 이벤트 밀도가 낮을 수 있으므로, “event 없음”을 즉시 stall로 해석하면 안 된다.

### Claude Code Mapping

| Raw event | Normalized kind | User-facing meaning |
| --- | --- | --- |
| `system.init` | `session_started` | resume session metadata 확인 |
| `stream_event.message_start` | `turn_started` | 모델 추론 시작 |
| `stream_event.content_block_delta` | `assistant_delta` | partial assistant output 진행 |
| `assistant` | `assistant_output` | assistant message complete |
| `result` | `turn_completed` | step 종료, usage/cost 확보 |
| `system.hook_*` | `hook_activity` | startup or hook activity |
| `rate_limit_event` | `rate_limit` | rate limit 상태 정보 |

Claude Code는 partial event가 richer하므로 live feedback 품질이 더 좋다.

## Status Model

이용자에게 보여주는 상태는 raw event가 아니라 아래 공통 상태 집합으로 제한한다.

- `dispatching`
- `awaiting_first_event`
- `thinking`
- `streaming_output`
- `tool_activity`
- `idle_but_alive`
- `suspected_stall`
- `recovering`
- `completed`
- `failed`

예시 출력:

```text
[Step1] cc review... status=thinking elapsed=47s last_event=message_start 44s ago
[Step1] cc review... status=streaming_output elapsed=52s last_event=assistant_delta 1s ago
[Step3] codex apply... status=suspected_stall elapsed=2m 18s no heartbeat for 92s
[Step3] codex apply... status=recovering attempt=1 reason=hard stall on resume subprocess
```

## Heartbeat Model

stall detection의 핵심은 wall-clock timeout이 아니라 heartbeat 기반 판정이다.

### Heartbeat Sources

우선순위 순서:

1. stdout normalized event 수신
2. stderr line 수신
3. known output/log file의 mtime or size 증가
4. child process alive 상태

### Heartbeat Semantics

- `strong heartbeat`
  - assistant delta
  - tool/hook event
  - turn started/completed
  - output file/log file 증가

- `weak heartbeat`
  - process alive 확인만 됨
  - 새 event는 없지만 종료도 안 됨

### Thresholds

초기값 제안:

- UI tick: `5s`
- healthy active: 최근 `<= 10s` 내 strong heartbeat
- idle but alive: 최근 `<= 45s` 내 strong heartbeat 없음, process alive
- suspected stall: `> 45s` strong heartbeat 없음
- hard stall: `> 120s` strong heartbeat 없음 and recovery 조건 충족

이 수치는 구현 후 live data로 다시 조정한다.

## Recovery Policy

recovery는 한 번에 session recreate로 가지 않고 단계적으로 수행한다.

### Stage 0: Observe

- `suspected_stall`이면 종료하지 않고 관찰을 계속한다.
- 이 단계에서는 이용자에게 경고만 표시한다.

### Stage 1: Client Retry

조건:

- hard stall 진입
- child process는 살아 있으나 stdout/stderr/activity가 장시간 정지

동작:

- 현재 client subprocess를 종료한다.
- same session handle로 동일 step message를 한 번 더 `resume`한다.
- trace에 `recovery_attempt=client_retry`를 남긴다.

이 단계의 의도는 “session 자체는 정상인데 resume client만 hang”한 경우를 회복하는 것이다.

### Stage 2: Session Recreate

조건:

- same handle retry도 실패
- 즉시 `OrchestrationError`
- 반복 stall

동작:

- 기존 recovery prompt를 사용해 새 persistent session을 만든다.
- 현재 step message를 재전송한다.
- trace에 `recovery_attempt=session_recreate`를 남긴다.

### Stage 3: Terminal Failure

조건:

- session recreate 이후에도 동일 failure
- recover budget 초과

동작:

- `mark-failed`
- failure evidence 저장
- follow-through issue/comment 경로와 연결

## Persisted State Changes

현재 `step_traces`에 아래 필드를 추가한다.

```json
{
  "supervision": {
    "status": "thinking",
    "last_event_at": "2026-04-06T03:12:45.123Z",
    "last_event_kind": "turn_started",
    "last_heartbeat_at": "2026-04-06T03:12:45.123Z",
    "heartbeat_source": "stdout_event",
    "stall_level": "none",
    "recovery_attempts": [
      {
        "kind": "client_retry",
        "started_at": "...",
        "completed_at": "...",
        "result": "success"
      }
    ]
  }
}
```

또한 `runtime_artifacts`를 확장한다.

- `stdout_event_log`
- `stderr_log`
- `output_file`
- `subagent_log_path`
- `child_pid` if available

모든 raw event를 state JSON에 그대로 저장하면 파일이 과도하게 커지므로, state에는 summary만 둔다.

raw event 저장 전략:

- step별 `.jsonl` artifact 파일을 별도로 쓴다.
- state에는 그 파일 경로와 핵심 counters만 저장한다.

## User-Facing Progress Output

[progress.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/progress.py) 의 `TICK_INTERVAL=30`은 요구사항과 맞지 않는다. 새 설계에서는 다음을 적용한다.

- 기본 tick interval: `5s`
- 출력은 “elapsed only”가 아니라 normalized status 중심
- status가 바뀌었을 때는 즉시 출력
- heartbeat summary와 마지막 event age를 포함

예시:

```text
[Step1] cc review... status=awaiting_first_event elapsed=5s
[Step1] cc review... status=thinking elapsed=11s last_event=turn_started 6s ago
[Step1] cc review... status=streaming_output elapsed=1m 8s last_event=assistant_delta 0s ago
[Step1] cc review ✓ (1m 14s) 2 findings, verdict=issues_found
```

## Implementation Surface

주요 변경 파일:

- [orchestrator.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/orchestrator.py)
  - `_run_command()` 대체
  - `send_message()` supervision loop 도입
  - staged recovery 도입
- [progress.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/progress.py)
  - 5초 tick
  - status-aware progress rendering
- [timing.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/timing.py)
  - supervision summary schema 추가
- [reporting.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/reporting.py)
  - heartbeat/stall/recovery 분석 반영
- [cli.py](/Users/jk/workspace/skills-jk/skills/cc-codex-debate-review/lib/debate_review/cli.py)
  - 필요한 경우 artifact path/reporting exposure

신규 모듈 후보:

- `runtime_stream.py`
  - subprocess streaming reader
- `runtime_events.py`
  - vendor event normalization
- `runtime_supervision.py`
  - heartbeat/stall/recovery state machine

## Testing Strategy

### Unit Tests

- Codex raw event -> normalized event mapping
- Claude raw event -> normalized event mapping
- heartbeat classification
- stall threshold transitions
- recovery stage transitions

### Orchestrator Tests

- `send_message()`가 stdout streaming event를 소비하면서 status patch를 기록하는지
- `no heartbeat` 시 `suspected_stall` -> `hard_stall`로 전이하는지
- same session retry 후 성공하는지
- session recreate fallback이 동작하는지

### E2E-Style Tests

- fake streaming Codex subprocess
- fake streaming Claude subprocess
- long-thinking but healthy case
- silent hang case
- partial output 이후 completion case

### Live Verification

- 실제 `persistent` debate review를 최소 1회 이상 수행
- 5초 단위 progress line 출력 확인
- hard stall 재현이 어려우면 test harness에서 synthetic hang subprocess로 검증

## Metrics to Capture

향후 판단을 위해 최소 아래 수치를 남긴다.

- step별 first event latency
- heartbeat gap histogram
- strong/weak heartbeat counts
- suspected stall 횟수
- hard stall 횟수
- recovery success rate
- recovery type별 소요 시간
- false stall 후 natural recovery 횟수

## Risks

1. vendor event shape drift
- normalize layer는 tolerant parser여야 한다.

2. 지나친 false positive
- 긴 추론을 stall로 오인하면 리뷰 품질이 악화된다.
- 그래서 kill 기준은 weak heartbeat와 file polling을 함께 보아야 한다.

3. state size 증가
- raw event는 별도 artifact로 분리해야 한다.

4. recovery 중복 실행
- 같은 step message 재전송 시 idempotency와 checkpoint replay 충돌을 검토해야 한다.

## Rollout

1. streaming supervision infrastructure 추가
2. ProgressReporter v2 연결
3. trace/reporting schema 확장
4. synthetic hang tests 추가
5. live persistent run으로 threshold 검증

## Recommendation

이 설계는 “응답속도 최적화”보다 “runtime observability + safe recovery”를 우선한다. 이는 debate-review의 본래 목적과 일치한다. 여러 round와 step을 거치며 깊은 리뷰를 유지하되, stall과 무응답만 체계적으로 다루는 방향이기 때문이다.
