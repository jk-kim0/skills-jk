# Debate Review Startup Latency 분석

> 분석일: 2026-04-07
> 분석 대상: PR #237, PR #236 실행 기록
> 데이터 소스: state JSON, CC 세션 로그 (JSONL), Codex 세션 로그 (JSONL)

## 요약

사용자가 debate-review 스킬을 호출한 후, 실제 Round 1 Step 1 (Lead Agent Review) 프롬프트가 에이전트에 도달하기까지 **약 69초** (PR #237 기준)가 소요됩니다.

> **주의: 초기 분석의 오류 정정**
>
> 초기 분석에서 "3분 25초"로 보고한 수치는 `step_timings.step1_lead_review` 타임스탬프를 Step 1 시작 시점으로 해석한 데서 비롯된 오류입니다. 실제로 이 타임스탬프는 Step 1의 첫 번째 `upsert-issue` 호출 시점 (= 에이전트가 리뷰를 완료한 후)을 기록합니다. 에이전트의 리뷰 수행 시간 (148.7초)이 오버헤드로 잘못 포함되었습니다.
>
> **근본 원인**: `step_timings` 기록 위치가 step dispatch가 아닌 첫 mutation (cli.py:521)에 있어, step timing이 "시작 시각"이 아닌 "첫 결과 기록 시각"을 나타냅니다. 이는 `step_timings` 시스템의 결함입니다. (#242에서 수정)

## 실제 타임라인 (PR #237 Round 1)

CC 세션 로그와 Codex 세션 로그의 타임스탬프를 교차 검증하여 재구성한 타임라인입니다.

```
07:22:46.093  orchestrator: init 완료 (state created)
07:22:58.446  CLI: sync_head + init_round
07:23:13.165  CC agent: claude -p 프로세스 시작
07:23:13.521  CC agent: 초기 프롬프트 수신
07:23:15.951  CC agent: {"status": "ready"} 응답
07:23:20.759  Codex agent: codex exec 세션 시작
07:23:20.760  Codex agent: 초기 프롬프트 수신 (5957 chars)
07:23:29.058  Codex agent: {"status": "ready"} 응답
07:23:29.072  Codex agent: task_complete
07:23:52.492  Codex agent: Step 1 task_started (codex exec resume)
07:23:55.210  Codex agent: Step 1 프롬프트 수신 ← 실제 Step 1 시작
  ... Codex가 코드 리뷰 수행 (2분 28초) ...
07:26:23.923  CLI: upsert-issue 호출 ← step_timings에 기록된 시점 (오해의 원인)
```

### 구간별 소요 시간 (실측)

| 구간 | 소요 시간 | 비고 |
| --- | ---: | --- |
| init CLI 실행 | 12.4s | `debate-review init` (state 생성 + PR 메타데이터 조회) |
| sync_head + init_round | 14.7s | git fetch + worktree checkout + round 초기화 |
| CC agent init (inference) | 2.4s | `claude -p` → `{"status": "ready"}` |
| CC 완료 → Codex 시작 | 4.8s | subprocess.run 리턴 + codex exec 시작 |
| Codex agent init (inference) | 8.3s | `codex exec` → `{"status": "ready"}` |
| **Codex init 완료 → Step 1 dispatch** | **23.4s** | **★ 의심 구간** |
| Step 1 dispatch → 프롬프트 수신 | 2.7s | codex exec resume 프로세스 시작 |
| **총 오버헤드 (init → Step 1 프롬프트 도달)** | **68.8s** | |
| Step 1 리뷰 수행 (Codex) | 148.7s | 실제 리뷰 작업 (오버헤드 아님) |

### 에이전트 init inference는 빠르다

| 에이전트 | init 프롬프트 크기 | inference 시간 | 응답 |
| --- | ---: | ---: | --- |
| CC (`claude -p`) | ~6KB | **2.4s** | `{"status": "ready"}` |
| Codex (`codex exec`) | ~6KB | **8.3s** | `{"status": "ready"}` |

초기 분석에서 "각 40-80초"로 추정했던 것은 완전히 잘못된 것으로, 실제로는 2-9초 수준입니다.

## 23.4초 의심 구간 분석

Codex init 완료 (07:23:29) → Step 1 dispatch (07:23:52) 사이의 23.4초를 분해합니다.

### 이 구간에서 수행되는 작업

```
_ensure_persistent_agents() 후반:
  1. record_agent_sessions (CLI subprocess)        ~0.1s

_dispatch_step() 내부:
  2. build_prompt (CLI subprocess)                 ~0.1s
  3. _read_file + os.remove                        <0.1s
  4. show --json (_load_state, CLI subprocess)      ~0.1s
  5. record_step_trace (인라인 Python)               ~0.1s
  6. build_runtime + StepSupervisor 초기화           <0.1s
  7. codex exec resume 프로세스 시작                  ~2-3s
  8. Codex task_started                            ~2-3s

  CLI subprocess 오버헤드 합계:                    ~5-7s
```

CLI subprocess 오버헤드는 개당 ~0.12초로 측정되었습니다 (`debate-review show` 기준). 총 4회 호출해도 ~0.5초입니다.

### 미설명 시간: ~16-18초

`codex exec` 프로세스 종료 → `subprocess.run()` 리턴 사이의 지연이 의심됩니다. `codex exec`는 `task_complete` 이벤트 후에도 cleanup/flush 작업을 수행할 수 있으며, 이 시간이 측정에 잡히지 않습니다. `codex exec resume` 시작 시에도 유사한 초기화 오버헤드가 있을 수 있습니다.

## 오버헤드 비교: Round 1 vs Round 2+

| PR | Round | 오버헤드 구간 | 소요 시간 | 비고 |
| --- | ---: | --- | ---: | --- |
| #237 | 1 | init → Step 1 프롬프트 | 68.8s | 에이전트 생성 포함 |
| #237 | 2 | step0 → Step 1 프롬프트 | ~10s (추정) | resume만, 생성 없음 |
| #236 | 3 | step0 → Step 1 프롬프트 | ~10s (추정) | 안정 상태 |

Round 2+ 에서의 오버헤드는 sync_head (~5s) + build_prompt + dispatch (~5s) ≈ **10초** 수준으로, 합리적입니다.

## step_timings 기록 결함

### 현재 동작 (결함)

| step_timing 키 | 기록 시점 | 기록 위치 |
| --- | --- | --- |
| `step0_sync` | sync 시작 시 | `sync_head()` ✅ |
| `step1_lead_review` | 첫 `upsert-issue` 또는 `record-verdict` 호출 시 | `cmd_upsert_issue()` ❌ |
| `step2_cross_review` | 첫 `record-cross-verification` 호출 시 | `cmd_record_cross_verification()` ❌ |
| `step3_lead_apply` | `record-application` 호출 시 | `record_application_phase1()` ❌ |
| `step4_settle` | `settle-round` 호출 시 | `cmd_settle_round()` ✅ |

`step1`, `step2`, `step3`의 timing은 **에이전트의 전체 수행 시간을 포함**하여, step 간 오버헤드를 정확히 측정할 수 없습니다.

### 올바른 동작 (step_traces)

orchestrator의 `_dispatch_step()`에서 `record_step_trace(started_at=...)` 호출은 올바르게 dispatch 시작 시점을 기록합니다. 그러나 현재 state file에 `step_traces: {}`로 비어 있어, 이 데이터가 활용되지 못하고 있습니다.

## 개선 제안

### 1순위: step_timings 기록 시점 수정

`step1_lead_review`, `step2_cross_review` 등의 timing을 `build-prompt` 호출 시점 또는 `record_step_trace(started_at)` 시점으로 이동합니다. 이를 통해 step 간 오버헤드를 정확히 측정할 수 있습니다. (#242에서 수정)

### 2순위: 에이전트 병렬 생성 (예상 효과: -10~15초)

현재 순차 생성을 병렬화합니다. 에이전트 init inference 자체는 2-9초로 빠르지만, 순차 실행으로 ~13초가 소요됩니다. 병렬화하면 ~9초로 단축됩니다.

실제 init inference 시간이 짧으므로, 초기 분석에서 제안한 "-40~80초" 효과는 과대 추정이었습니다. 실제 효과는 **~5-10초** 수준입니다.

### 3순위: Lazy Agent 생성

Round 1에서 lead agent(Codex)만 먼저 생성하고, cross-verifier(CC)는 Step 2 직전에 생성합니다. 이를 통해 Step 1 시작까지의 오버헤드를 추가로 ~10초 단축할 수 있습니다.

### 4순위: 23.4초 의심 구간 심층 조사

`codex exec` / `codex exec resume` 프로세스의 시작/종료 시간을 더 정밀하게 측정하여 미설명 시간의 원인을 파악합니다. orchestrator에 command_span 타이밍을 추가하면 각 subprocess 호출의 실제 소요 시간을 추적할 수 있습니다.

## 결론

| 구간 | 현재 소요 | 개선 후 (추정) |
| --- | ---: | ---: |
| init + sync + init_round | 27s | 27s (네트워크 바운드) |
| 에이전트 생성 (순차) | 16s | 9s (병렬) |
| dispatch 오버헤드 | 26s | 10s (의심 구간 해소 시) |
| **총 오버헤드** | **~69s** | **~46s** |

핵심 takeaway:
1. 실제 오버헤드는 **69초**이지, 3분 37초가 아닙니다
2. `step_timings`의 기록 결함으로 인해 에이전트 리뷰 수행 시간이 오버헤드에 포함되어 보였습니다
3. 에이전트 init inference는 예상보다 훨씬 빨랐습니다 (2-9초)
4. 가장 큰 단일 구간은 `init + sync` (27초)이며 네트워크 바운드입니다
