# Debate Review: Persistent Agent + Append-Only Prompt Design

## Status: Proposed

## 문서 구성

- baseline architecture와 상태 전이 규칙은 [2026-03-30-debate-review-core-design.md](./2026-03-30-debate-review-core-design.md)를 따른다.
- CLI 경계와 subcommand 계약은 [2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)를 따른다.
- 이 문서는 persistent agent mode가 baseline 설계를 어떻게 확장하는지 정의한다.
- 실제 rollout 순서와 현재 completion backlog는 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.

## Current Implementation Checkpoint (2026-04-03)

이 문서는 원래 "persistent agent로 전환하는 설계"를 정의했지만, 현재 저장소의 구현 상태는 당시 가정과 완전히 같지 않다.

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

아직 completion 기준에 못 미치는 항목:

- 현재 가장 시급한 blocker는 `build-prompt` 출력이 invalid JSON이어서 persistent agent 초기화가 깨지는 `#161`이다.
- duplicate withdrawal 설계가 persistent mode step prompt와 state bookkeeping까지 일관되게 닫히지 않았다. `#164`는 state-side 기반 작업이고 prompt/routing parity는 아직 남아 있다.
- 나머지 active backlog는 repo-owned orchestration path, operational follow-through, E2E verification이며 canonical 목록은 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.

즉, 현재 debate-review는 "상태 전이용 CLI + prompt assets + 운영 절차 문서"는 갖췄지만, 설계 문서가 상정한 완성형 운영 시스템은 아직 아니다. canonical backlog와 우선순위는 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에 둔다.

## Background

현재 debate-review는 라운드당 3회, 최대 10라운드에서 **30회의 독립적 agent 호출**을 수행한다.

매 호출마다:

1. 새 agent instance 생성
2. `build-context`로 8개 placeholder 재구성 (이전 라운드를 요약 압축)
3. 3개 프롬프트 템플릿 중 하나를 선택하여 placeholder 치환
4. Agent가 PR diff, 소스 파일을 처음부터 다시 탐색

이로 인한 문제:

| 문제 | 설명 |
|------|------|
| 정보 손실 | `build_review_context`가 최근 2라운드만 요약. 후반 라운드에서 초기 논쟁 맥락 상실 |
| 반복 탐색 | 같은 PR diff, 같은 파일을 30회 다시 읽음 |
| Orchestrator 복잡도 | context.py 275줄, 프롬프트 템플릿 3개, placeholder 치환 로직 |
| 비용 | 매번 PR diff + 소스 파일 탐색으로 불필요한 토큰 소비 |

## Design Overview

### Core Idea

1. **Persistent Agent**: CC 1개, Codex 1개 agent instance를 세션 시작 시 생성하고, 전체 debate 동안 유지
2. **Append-Only Prompt**: Orchestrator가 매 step마다 새 instruction을 기존 agent에게 후속 메시지로 전달
3. **Context 자동 누적**: 이전 분석 결과, 파일 내용, 판단 근거가 agent의 conversation history에 보존
4. **Prompt Caching**: 이전 conversation이 exact prefix로 유지되어 자동 캐싱 (cached input 90% 할인)

### Architecture

```
CC Orchestrator
  │
  ├── CC Agent Instance (세션 시작 시 1회 생성, debate 종료까지 유지)
  │     ├─ Turn 1: R1 Step2 cross-verify
  │     ├─ Turn 2: R2 Step1 lead review
  │     ├─ Turn 3: R2 Step3 lead response + code apply
  │     └─ ... (최대 15 turns)
  │
  ├── Codex Agent Instance (세션 시작 시 1회 생성, debate 종료까지 유지)
  │     ├─ Turn 1: R1 Step1 lead review
  │     ├─ Turn 2: R1 Step3 lead response + code apply
  │     ├─ Turn 3: R2 Step2 cross-verify
  │     └─ ... (최대 15 turns)
  │
  └── CLI state management ($DEBATE_REVIEW_BIN — 변경 없음)
```

### Agent Dispatch Flow

```
[Session Start]
  ├─ Create CC Agent(initial_prompt)     ← 1회
  ├─ Create Codex Agent(initial_prompt)  ← 1회
  │
  [Round 1]
  │  Step 0: sync-head (Orchestrator → CLI)
  │  Step 1 (Lead: Codex)
  │    ├─ Orchestrator → SendMessage(Codex, lead_review_instruction)
  │    ├─ Codex output → Orchestrator parses → upsert-issue, record-verdict
  │  Step 2 (Cross: CC)
  │    ├─ Orchestrator → SendMessage(CC, cross_verify_instruction)
  │    ├─ CC output → Orchestrator parses → record-cross-verification, upsert-issue
  │  Step 3 (Lead: Codex)
  │    ├─ Orchestrator → SendMessage(Codex, lead_response_instruction)
  │    ├─ Codex output → Orchestrator parses → resolve-rebuttals, record-application
  │  Step 4: settle-round (Orchestrator → CLI)
  │
  [Round 2]
  │  Step 1 (Lead: CC)    ← SendMessage(CC, ...)
  │  Step 2 (Cross: Codex) ← SendMessage(Codex, ...)
  │  Step 3 (Lead: CC)    ← SendMessage(CC, ...)
  │  ...
  │
  [Terminal] → post-comment, worktree cleanup
```

### Prompt Caching Effect

Persistent agent의 conversation history는 exact prefix — 자동 캐싱 대상:

- 이전 turn 전체가 변하지 않는 prefix → cache hit (정가의 10%)
- 매 turn에서 새로 처리하는 것은 step instruction + agent output만 (~3k tokens)
- Agent가 탐색한 PR diff, 소스 파일도 context에 누적 → 재탐색 불필요

| Turn | 전체 context | Cached | Fresh | 실효 비용 |
|------|-------------|--------|-------|----------|
| 1 | ~3k | 0 | 3k | 100% |
| 5 | ~25k | ~22k | ~3k | ~14% |
| 10 | ~50k | ~47k | ~3k | ~8% |
| 15 | ~75k | ~72k | ~3k | ~6% |

30회 호출 총 실효 비용: 현재 방식(~120k tokens)과 거의 동일하면서, 정보 품질은 대폭 향상.

---

## Completion Gaps

Persistent agent 설계를 실제로 "완성"으로 간주하려면 아래 갭이 메워져야 한다.

### 1. Orchestrator must exist as code, not only prose

현재 저장소 구현은 CLI primitive와 prompt builder를 제공하지만, 다음 책임은 여전히 `SKILL.md` 안의 수동 절차다.

- round loop 실행
- CC / Codex agent 생성 및 resume
- agent JSON 파싱 및 retry
- Step 1/2/3 결과를 CLI subcommand로 routing
- terminal 처리와 cleanup

완성 기준:

- 저장소 안에 재실행 가능한 orchestrator entrypoint가 존재한다.
- `init -> sync-head -> init-round -> step dispatch -> settle-round -> terminal processing`이 자동으로 연결된다.

### 2. Persistent step prompts and state routing must match

현재 기본 모드는 `persistent`이므로, duplicate withdrawal 같은 새 계약은 persistent step prompt와 state mutation 경로에 먼저 반영되어야 한다.

특히 다음이 맞아야 한다.

- Step 1 lead review output schema
- Step 2 cross verification output schema
- CLI routing (`resolve-rebuttals`, `record-cross-verification`, `upsert-issue`, `record-verdict`)
- Step 4 settlement / ledger / stall detection

### 3. Restart and recovery need runtime verification

문서는 recovery prompt, persisted handle, `next_step`, `resume_context`를 정의하지만, 실제로 중요한 것은 "실패 후에도 다시 이어서 돈다"는 보장이다.

필수 검증 시나리오:

- Step 1 직후 중단 -> resume
- Step 3 phase1/phase2 사이 중단 -> resume
- persistent agent handle 유실 -> recovery prompt로 새 agent 생성
- PR 외부 push 발생 -> supersede -> 다음 round 재개

### 4. Terminal operations need to be code-backed

설계 문서의 terminal path는 상태 종료만으로 끝나지 않는다.

- final PR comment 게시
- bug report 생성
- PR metadata 갱신
- worktree cleanup

이 중 상태 변경은 일부 구현됐지만, GitHub issue 생성 / PR edit / cleanup은 아직 운영자 절차다.

---

## Implementation Plan

### Task 1: context.py 제거 + build-context CLI 제거

`build-context` subcommand와 `context.py`를 제거한다. Orchestrator가 이전 agent output에서 직접 데이터를 추출하여 step message를 구성하므로, state-derived placeholder 생성이 불필요해진다.

#### 변경 파일

| 파일 | 작업 |
|------|------|
| `lib/debate_review/context.py` (275줄) | **삭제** |
| `tests/test_context.py` (263줄) | **삭제** |
| `cli.py` | `build-context` subcommand 제거 |
| `tests/test_cli.py` | `build-context` 관련 테스트 제거 |

#### cli.py 구체적 변경

```python
# 제거할 import
from debate_review.context import build_context

# 제거할 parser 등록 (build_parser 내, 4줄)
p_ctx = subparsers.add_parser("build-context", help="Build review context from state")
p_ctx.add_argument("--state-file", required=True)
p_ctx.add_argument("--round", type=int, required=True)

# 제거할 함수 (5줄)
def cmd_build_context(args):
    state = load_state(args.state_file)
    if state is None:
        _error_exit(f"No state file found at {args.state_file}")
    result = build_context(state, round_num=args.round)
    print(json.dumps(result))

# 제거할 commands dict entry (1줄)
"build-context": cmd_build_context,
```

#### applicable_issues 로직 처리

`build_applicable_issues` (context.py 내)는 Step 3 message 구성 시 필요하다. Orchestrator가 `show --json` 결과에서 직접 필터링한다:

```
issues에서 consensus_status=accepted AND application_status in (pending, failed) 필터링
```

Persistent mode 재시작을 위해 agent 식별자도 state file에 저장해야 한다. 따라서 다음 상태 관리 entry를 추가한다:

- `state["persistent_agents"]["cc_agent_id"]`
- `state["persistent_agents"]["codex_session_id"]`
- CLI subcommand: `record-agent-sessions --state-file ... --cc-agent-id ... --codex-session-id ...`

---

### Task 2: 프롬프트 템플릿 3개 → Initial Prompt 1개로 교체

3개의 독립된 프롬프트 템플릿을 제거하고, agent 생성 시 전달하는 initial prompt 1개로 교체한다. Step별 instruction은 SKILL.md에 format을 명시한다.

#### 변경 파일

| 파일 | 작업 |
|------|------|
| `agent-lead-review-prompt.md` (89줄) | **삭제** |
| `agent-cross-verify-prompt.md` (71줄) | **삭제** |
| `agent-lead-response-prompt.md` (95줄) | **삭제** |
| `agent-initial-prompt.md` (~40줄) | **신규** |
| `tests/test_prompt_docs.py` | 파일명 변경에 맞춰 수정 |

#### agent-initial-prompt.md

```markdown
# Debate Review Agent: {REPO} #{PR_NUMBER}

## Your Role

You are a code review agent participating in a multi-round structured debate.
You will receive a series of tasks as follow-up messages. Each message is one
step of one round. Execute ONLY the task in the latest message.

All previous messages and your previous responses are preserved as conversation
history. Use them as context for your decisions.

## Repository

- Repo: {REPO}
- PR: #{PR_NUMBER}
- Worktree: {WORKTREE_PATH}

## How to Explore

- `env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff {PR_NUMBER} --repo {REPO}`
- `env -u GITHUB_TOKEN -u GH_TOKEN gh pr view {PR_NUMBER} --repo {REPO}`
- Read files directly in {WORKTREE_PATH}
- `env -u GITHUB_TOKEN -u GH_TOKEN gh pr checks {PR_NUMBER} --repo {REPO}`

## Output Language

Use {OUTPUT_LANGUAGE} for all user-facing JSON string values (message, reason,
description). Keep JSON keys, enum values, file paths, anchors unchanged.

## Review Criteria

{REVIEW_CRITERIA}

## General Output Rules

- Output ONLY valid JSON as specified in each task message
- No markdown, explanations, or preamble outside the JSON
- Each task message specifies its own JSON schema — follow it exactly
```

Placeholder는 agent 생성 시 1회 치환: `{REPO}`, `{PR_NUMBER}`, `{WORKTREE_PATH}`, `{OUTPUT_LANGUAGE}`, `{REVIEW_CRITERIA}`.

---

### Task 3: SKILL.md 재작성

SKILL.md의 주요 섹션을 persistent agent 방식으로 재작성한다. 가장 큰 변경.

#### 섹션별 변경

**(A) "Agent Invocation" 섹션 — 전면 재작성**

현재 (매 step 새 agent):

```markdown
Codex: codex exec -s "$SANDBOX" - < "$PROMPT_FILE"
CC: Agent(prompt="$FILLED_PROMPT", description="debate-review step N")
```

변경 (persistent agent):

```markdown
### Agent Lifecycle

#### Agent Creation (세션 시작 시 1회)

CC:
  Agent(prompt=FILLED_INITIAL_PROMPT, description="debate-review CC agent")
  → CC_AGENT_ID 저장

Codex:
  codex exec -s danger-full-access - < initial_prompt_filled.md
  → CODEX_SESSION_ID 저장

#### Step Dispatch (매 step)

CC:   SendMessage(to=CC_AGENT_ID, message=step_instruction)
Codex: codex exec resume "$CODEX_SESSION_ID" -s danger-full-access - < step_message.md
```

**(B) "Review Context + Placeholder Construction" 섹션 — 제거**

현재:

```markdown
## Review Context + Placeholder Construction
Use `build-context` to generate all state-derived placeholder data...
```

전체 제거. "Step Message Construction" 섹션으로 교체.

**(C) Step 1/2/3 절차 — placeholder 참조 제거**

현재 각 step:

```
1. Build review context via `build-context`
2. Read prompt template
3. Substitute placeholders
4. Invoke sub-agent
```

변경:

```
1. Compose step message (format은 아래 참조)
2. SendMessage(agent_id, step_message) 또는 codex exec resume
3. Parse JSON response
4. Route to CLI subcommands
```

**(D) Step Message Format 추가**

SKILL.md에 각 step의 message format을 명시한다:

**Step 1 (Lead Review):**

```markdown
## Round {ROUND} — Lead Review

You are the LEAD reviewer this round.

### Pending Rebuttals (Step 1a)

{PENDING_REBUTTALS_JSON}

If empty, skip rebuttal resolution.
For each: `withdraw` (accept rebuttal) or `maintain` (keep finding).

### Task (Step 1b)

Review the PR diff. Report new findings by severity: critical, warning, suggestion.

Rules:
- Do NOT re-report withdrawn issues unless you have new evidence
- Do NOT report code added as a fix for a previously accepted issue
- If unsure, err on the side of not reporting

### Current Open Issues

{OPEN_ISSUES_JSON}

### Debate Ledger

{DEBATE_LEDGER_TEXT}

### Verdict

- 0 new findings + open issues is empty → `no_findings_mergeable`
- Otherwise → `has_findings`

### Output

{"rebuttal_responses": [...], "findings": [...], "verdict": "..."}
```

**Step 2 (Cross-Verify):**

```markdown
## Round {ROUND} — Cross-Verification

You are the CROSS-VERIFIER this round.

### Lead's Findings

{LEAD_FINDINGS_JSON}

For each: `accept` or `rebut` with reason.

### Task

Report your own additional findings not raised by the lead.

### Debate Ledger

{DEBATE_LEDGER_TEXT}

### Output

{"cross_verifications": [...], "findings": [...]}
```

**Step 3 (Lead Response + Code Apply):**

```markdown
## Round {ROUND} — Lead Response + Code Application

### Rebuttals Against Your Findings

{CROSS_REBUTTALS_JSON}

For each: `withdraw` or `maintain`.

### Cross-Verifier's New Findings

{CROSS_NEW_FINDINGS_JSON}

For each: `accept` or `maintain`.

### Issues to Fix

{APPLICABLE_ISSUES_JSON}

If empty, skip code application.

### Code Application

1. Edit files in {WORKTREE_PATH}
2. git add <files>
3. COMMIT_MSG=$("{DEBATE_REVIEW_BIN}" build-commit-message ...)
4. git commit -m "$COMMIT_MSG"
5. git push origin HEAD:{HEAD_BRANCH}

### Output

{"rebuttal_decisions": [...], "cross_finding_evaluations": [...], "application_result": {...}}
```

**(E) Step Message 데이터 소스 섹션 추가**

| Step message 데이터 | 출처 |
|---------------------|------|
| `PENDING_REBUTTALS_JSON` | Orchestrator가 이전 round Step 3 output에서 maintain된 rebuttals 추출 |
| `OPEN_ISSUES_JSON` | `show --json` → issues에서 open + (accepted, not applied) 필터링 |
| `LEAD_FINDINGS_JSON` | 현재 round Step 1 agent output의 `findings` 원문 |
| `CROSS_REBUTTALS_JSON` | 현재 round Step 2 agent output의 `cross_verifications`에서 rebut만 |
| `CROSS_NEW_FINDINGS_JSON` | 현재 round Step 2 agent output의 `findings` 원문 |
| `APPLICABLE_ISSUES_JSON` | `show --json` → consensus=accepted, app=pending/failed 필터링 |
| `DEBATE_LEDGER_TEXT` | `show --json` → debate_ledger 포맷팅 (Step 1, Step 2에 모두 포함) |

핵심: `build-context` CLI 호출 없음. Orchestrator가 (1) 직전 agent output 원문, (2) `show --json` 결과만으로 구성.

**(F) Restart Rules 수정**

Agent가 살아있는 경우: journal step → 해당 agent에 SendMessage로 재개.

Agent가 죽은 경우: 새 agent 생성 + recovery prompt:

```markdown
# Debate Review Agent (Recovered): {REPO} #{PR_NUMBER}

[initial prompt 내용]

## Recovery Context

이전 agent 실패 후 복구. 이전 debate 기록:

### Debate Ledger
{state.debate_ledger}

### Open Issues
{state.issues filtered}

Round {N} Step {M}부터 재개.
```

**(G) Supersede Handling 수정**

외부 push 감지 시, agent에게 다음 메시지 전달:

```markdown
## External Push Detected

PR HEAD changed externally (new SHA: {NEW_SHA}).
Previous line numbers and code references may be invalid.
Re-read the PR diff in your next task.
```

이어서 새 라운드 Step 1 instruction 전달.

---

### Task 4: REFERENCE.md 재작성

현재 (15줄): placeholder 소스 목록.

변경 후:

```markdown
# Debate Review Reference

## Agent Initial Prompt

File: `agent-initial-prompt.md`

Placeholders (agent 생성 시 1회 치환):
- {REPO}, {PR_NUMBER}: Orchestrator 변수
- {WORKTREE_PATH}: init-round output
- {OUTPUT_LANGUAGE}: init output의 language
- {REVIEW_CRITERIA}: $SKILL_ROOT/review-criteria.md 내용

## Step Message Data Sources

| 데이터 | 출처 |
|--------|------|
| Pending rebuttals | Orchestrator: 이전 round Step 3 output에서 추출 |
| Open issues | show --json → issues 필터링 |
| Lead findings | Orchestrator: 현재 round Step 1 output에서 추출 |
| Cross rebuttals | Orchestrator: 현재 round Step 2 output에서 추출 |
| Cross new findings | Orchestrator: 현재 round Step 2 output에서 추출 |
| Applicable issues | show --json → consensus=accepted, app=pending/failed |
| Debate ledger | show --json → debate_ledger 포맷팅 |

## Agent Invocation

CC Agent:
- Create: Agent(prompt=initial, description="debate-review CC agent")
- Resume: SendMessage(to=CC_AGENT_ID, message=step_instruction)
- Requires: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

Codex Agent:
- Create: codex exec -s danger-full-access - < initial_prompt.md
- Resume: codex exec resume "$SESSION_ID" -s danger-full-access - < step.md

모든 step에서 동일한 danger-full-access sandbox 사용.
```

---

### Task 5: 테스트 업데이트

| 파일 | 작업 |
|------|------|
| `tests/test_context.py` (263줄) | **삭제** |
| `tests/test_cli.py` | `build-context` subcommand 테스트 제거 |
| `tests/test_prompt_docs.py` | 3개 템플릿 → `agent-initial-prompt.md` 존재 검증 |

다른 테스트 파일 (test_state, test_round_ops, test_issue_ops, test_cross_verification, test_application, test_sync, test_comment, test_error_log)은 변경 없음.

---

## File Change Summary

### 삭제 (5파일, 793줄)

| 파일 | 줄 수 |
|------|------|
| `lib/debate_review/context.py` | 275 |
| `agent-lead-review-prompt.md` | 89 |
| `agent-cross-verify-prompt.md` | 71 |
| `agent-lead-response-prompt.md` | 95 |
| `tests/test_context.py` | 263 |

### 신규 (1파일, ~40줄)

| 파일 | 줄 수 |
|------|------|
| `agent-initial-prompt.md` | ~40 |

### 수정 (6파일)

| 파일 | 변경 | 줄 변화 |
|------|------|---------|
| `cli.py` | build-context subcommand 제거 | -15 |
| `config.yml` | `codex_sandbox`/`codex_apply_sandbox` → 단일 `codex_sandbox: danger-full-access` | -2 / +1 |
| `SKILL.md` | Procedure 재작성 | -200 / +180 |
| `REFERENCE.md` | Step message data sources로 교체 | -15 / +30 |
| `tests/test_cli.py` | build-context 테스트 제거 | -20 |
| `tests/test_prompt_docs.py` | 파일명 변경 | ~0 |

### 변경 없음 (11파일)

| 파일 | 이유 |
|------|------|
| `state.py` | `persistent_agents` state 필드 추가 |
| `round_ops.py` | consensus/stall 판정 변경 없음 |
| `cross_verification.py` | rebuttal/accept 로직 변경 없음 |
| `issue_ops.py` | issue upsert/dedup 변경 없음 |
| `application.py` | 3-phase checkpoint 변경 없음 |
| `sync.py` | git sync 변경 없음 |
| `comment.py` | PR comment 생성 변경 없음 |
| `gh.py` | GitHub CLI wrapper 변경 없음 |
| `config.py` | config loading 변경 없음 |
| `error_log.py` | error logging 변경 없음 |
| `review-criteria.md` | review criteria 변경 없음 |

### 순 변화: **~538줄 감소**

---

## Runtime Requirements

### CC Agent (SendMessage)

```
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Agent Teams 활성화 시 SendMessage tool로 기존 agent에 후속 메시지 전달 가능.

### Codex Agent (Session Resume)

```bash
codex exec -s danger-full-access - < initial_prompt_filled.md   # 최초
codex exec resume "$SESSION_ID" -s danger-full-access - < step.md   # 이후
```

모든 step에서 동일한 `danger-full-access` sandbox를 사용하므로, resume 시 sandbox 변경 문제가 없다.

### Fallback: Fresh Agent + Transcript

Agent Teams나 Codex resume이 불안정한 경우, 매 step마다 새 agent를 생성하되 누적 transcript 문서를 전달:

```
transcript = initial_prompt
           + "R1S1 instruction\n" + output_1
           + "R1S2 instruction\n" + output_2
           + "R2S1 instruction\n"              ← 현재 step
```

Text prefix match로 prompt caching 적용. Persistent agent 대비 agent의 파일 탐색 결과는 보존되지 않으나, debate context는 보존.

---

## Failure Recovery

| 상황 | 처리 |
|------|------|
| Agent 정상 | journal step → SendMessage로 재개 |
| CC Agent crash | 새 agent 생성 + recovery prompt |
| Codex crash | --resume 재시도, 실패 시 새 세션 + recovery prompt |
| Orchestrator crash | state file + journal + persisted agent IDs로 복구. Handle이 살아 있으면 재사용, 아니면 새 agent 생성 |

---

## Open Questions

1. **Agent Teams 안정성**: experimental flag. 장시간(30분+) SendMessage 안정성 확인 필요
2. **Codex session ID 캡처**: codex exec 실행 후 session ID를 stdout에서 파싱하는 방법
3. **Agent 간 정보 전달 크기**: 많은 findings가 있을 때 step message 크기 실용적 한계
