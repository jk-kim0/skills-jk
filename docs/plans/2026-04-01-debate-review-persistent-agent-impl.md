# Debate Review: Persistent Agent 구현 태스크

## 문서 구성

- baseline architecture는 [2026-03-30-debate-review-core-design.md](./2026-03-30-debate-review-core-design.md)에 있다.
- CLI 경계와 상태 관리 계약은 [2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)에 있다.
- 이 문서는 [2026-04-01-debate-review-persistent-agent-design.md](./2026-04-01-debate-review-persistent-agent-design.md)를 실제 작업 단위와 completion backlog로 풀어낸다.
- 즉, debate-review 문서 묶음 안에서 이 문서는 rollout and completion tracker 역할을 맡는다.

## 현재 체크포인트 (2026-04-03)

이 문서는 원래 persistent mode를 단계적으로 rollout하기 위한 계획이었지만, 현재 `main`은 이미 다음 상태까지 와 있다.

- `agent_mode` 도입 완료
- persistent prompt 자산 및 `build-prompt` 추가 완료
- `record-agent-sessions` / resume metadata 추가 완료
- 기본값이 이미 `persistent`
- legacy 경로는 아직 남아 있음
- duplicate withdrawal의 state-side 1차 반영이 `#164`로 병합됨
- Step 3 Phase 2의 short SHA 정규화가 `#165`로 병합됨

따라서 아래의 PR 1~4 계획은 역사적 맥락으로는 유효하지만, 앞으로의 작업은 "persistent 도입"보다 "debate-review 완성"에 초점을 맞춰 재정렬해야 한다.

## 현재 핵심 블로커

가장 시급한 문제는 `#161`이다.

- `build-prompt` 출력이 invalid JSON이어서 persistent agent 초기화가 시작 단계에서 실패한다.
- 이 문제는 Codex lead 구성에서 persistent debate를 실제로 시작할 수 없게 만들므로, 다른 completion 작업보다 우선한다.
- 따라서 아래 backlog의 우선순위는 `#161` 해소를 선행 조건으로 읽어야 한다.

## 핵심 제약: 증분 배포 + 병행 운영

**각 PR이 병합될 때마다 debate-review가 정상 작동해야 한다.**

기존 방식(독립 agent 호출)과 새 방식(persistent agent)을 **동시에 사용할 수 있는 상태**를 유지한다. `config.yml`의 `agent_mode` 값으로 모드를 선택한다.

```yaml
# config.yml
agent_mode: legacy      # legacy | persistent
```

### 전환 흐름

```
[현재] legacy만 존재
  ↓ PR 1: 새 파일 추가 + agent_mode 플래그 도입
[병행] legacy(기본) + persistent 선택 가능
  ↓ PR 2: SKILL.md에 persistent 절차 추가 (legacy 절차 유지)
[병행] legacy / persistent 모두 사용 가능
  ↓ PR 3: 기본값을 persistent로 변경
[병행] persistent(기본) + legacy 선택 가능 (롤백 가능)
  ↓ PR 4: legacy 코드 삭제 + 문서/테스트 정리
[완료] persistent만 존재
```

각 단계 후 debate-review 실행 가능 여부:
- PR 1 후: ✅ `agent_mode: legacy` (기본값) — 기존과 동일하게 동작
- PR 2 후: ✅ `legacy` / `persistent` 모두 선택 가능
- PR 3 후: ✅ `persistent` 기본, 문제 시 `legacy`로 롤백
- PR 4 후: ✅ `persistent`만 동작 (legacy 코드 완전 제거)

### Completion 관점에서 다시 정의한 목표

앞으로 남은 작업의 완료 기준은 아래다.

1. debate-review를 end-to-end로 실행하는 repo-owned orchestration path가 존재한다. 구현 형태는 Python runner일 수도 있고, 검증 가능한 scripted orchestration일 수도 있지만 ad-hoc 수동 세션 절차에 의존하면 안 된다.
2. 기본 모드인 `persistent` 경로가 최신 schema와 완전히 일치하고, 초기화 경로가 실제로 동작한다.
3. resume / recovery / supersede / terminal processing이 자동화되어 있다.
4. 문서에만 있는 운영 절차(버그 리포트, PR metadata update, cleanup)가 코드 또는 검증 가능한 helper로 내려온다.
5. 핵심 시나리오를 덮는 end-to-end 테스트가 있다.

---

## 선행 검증 (PR 작업 전)

PR 1 착수 전에 runtime 요구사항을 검증한다.

| 검증 항목 | 방법 | 통과 기준 |
|-----------|------|----------|
| Agent Teams (SendMessage) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경에서 Agent 생성 후 SendMessage로 후속 지시 전달 | 응답 수신, context 유지 확인 |
| Codex session resume | `codex exec` 후 session ID 캡처 → `codex exec resume` 재개 | 이전 turn context 보존 확인 |
| 장시간 안정성 | 3+ turns 연속 SendMessage / resume | crash 없이 동작 |

검증 결과에 따라:
- **모두 통과**: persistent agent 방식으로 진행
- **CC만 통과**: CC는 SendMessage, Codex는 매 step fresh agent + transcript fallback
- **모두 실패**: 양쪽 모두 transcript fallback 방식

검증 실패해도 PR 1~2는 진행 가능 (기본값이 legacy이므로 기존 동작에 영향 없음).

---

## PR 1: agent-initial-prompt.md 추가 + agent_mode 플래그 도입

### 목적

Persistent agent에 필요한 파일을 추가하고, 모드 선택 플래그를 도입한다. 기본값은 `legacy`이므로 기존 동작에 영향 없음.

### 변경 파일

| 파일 | 작업 |
|------|------|
| `agent-initial-prompt.md` (~40줄) | **신규** — 설계 문서 Task 2의 initial prompt |
| `config.yml` | `agent_mode: legacy` 추가 |
| `lib/debate_review/config.py` | `agent_mode` 필드 파싱 추가 |
| `cli.py` | `init` 출력에 `agent_mode` 포함, `record-agent-sessions` 추가 |
| `lib/debate_review/state.py` | `persistent_agents` state 필드 추가 |

### agent-initial-prompt.md

설계 문서의 `agent-initial-prompt.md` 섹션 그대로 작성:
- `{REPO}`, `{PR_NUMBER}`, `{WORKTREE_PATH}`, `{OUTPUT_LANGUAGE}`, `{REVIEW_CRITERIA}` placeholder
- agent 역할 설명, 탐색 방법, 출력 규칙

### config.yml 변경

```yaml
# 추가
agent_mode: legacy      # legacy | persistent
```

### cli.py init 출력 변경

```json
{
  "agent_mode": "legacy",
  ...
}
```

Orchestrator는 `AGENT_MODE` 변수를 저장하고, 이후 절차 분기에 사용한다.

### persistent agent handle 저장

Persistent mode에서 agent 생성 직후 다음 state 필드를 저장한다:

- `persistent_agents.cc_agent_id`
- `persistent_agents.codex_session_id`

CLI subcommand:

```bash
"$DEBATE_REVIEW_BIN" record-agent-sessions \
  --state-file "$STATE_FILE" \
  --cc-agent-id "$CC_AGENT_ID" \
  --codex-session-id "$CODEX_SESSION_ID"
```

### 검증

- [ ] `agent_mode: legacy`일 때 기존 debate-review 정상 동작
- [ ] `agent-initial-prompt.md` placeholder 형식이 일관적
- [ ] `init` 출력에 `agent_mode` 포함

### debate-review 동작 영향: 없음 (기본값 legacy)

---

## PR 2: SKILL.md에 persistent agent 절차 추가

### 목적

SKILL.md에 persistent agent 절차를 **추가**한다. 기존 legacy 절차는 그대로 유지한다. Orchestrator는 `AGENT_MODE`에 따라 분기한다.

### 전제 조건

- PR 1 병합 완료 (`agent-initial-prompt.md` 존재, `agent_mode` 플래그 존재)

### 변경 파일

| 파일 | 작업 |
|------|------|
| `SKILL.md` | persistent agent 절차 추가 (legacy 절차 유지) |

### SKILL.md 구조

```markdown
## Agent Mode

init에서 받은 `AGENT_MODE` 값에 따라 절차를 분기한다.

| Mode | Agent 생성 | Step 실행 | 파일 참조 |
|------|-----------|----------|----------|
| `legacy` | 매 step 새 agent | build-context → template 치환 → agent 호출 | agent-*-prompt.md 3개 |
| `persistent` | 세션 시작 시 1회 | SendMessage / codex resume | agent-initial-prompt.md 1개 |

### legacy 모드

(기존 절차 — 변경 없음)

### persistent 모드

(설계 문서 Task 3의 전체 내용)
```

### persistent 모드 절차 (설계 문서 Task 3 참조)

| 섹션 | 내용 |
|------|------|
| Agent Lifecycle | Create (세션 시작 1회) + Resume (SendMessage / codex resume) |
| Step Message Format | Step 1 (Lead Review), Step 2 (Cross-Verify), Step 3 (Lead Response + Code Apply) |
| Step Message 데이터 소스 | 직전 agent output + `show --json` 결과로 구성 (build-context 미사용) |
| Restart Rules | persisted handle 생존 → SendMessage/resume 재개, handle 없음/agent 사망 → recovery prompt로 새 agent 생성 |
| Supersede Handling | agent에게 external push 메시지 전달 |

### 모드 분기 위치

Orchestrator가 분기하는 지점은 3곳:

1. **Initialization 직후**: persistent면 CC/Codex agent 생성
2. **각 Step 실행**: persistent면 SendMessage/resume, legacy면 build-context → template
3. **Restart**: persistent면 agent 생존 확인 후 분기

나머지 절차(Step 0 sync-head, Step 4 settle, Terminal processing, CLI 호출)는 모드와 무관하게 동일.

### 검증

- [ ] `agent_mode: legacy` — 기존과 동일하게 동작 (회귀 없음)
- [ ] `agent_mode: persistent` — persistent agent 흐름으로 동작
- [ ] 실제 PR에서 양쪽 모드 각각 debate-review 실행

### debate-review 동작 영향: legacy 무영향, persistent 추가

---

## PR 3: 기본값을 persistent로 변경

### 목적

충분한 검증 후, `agent_mode` 기본값을 `persistent`로 변경한다. 문제 발생 시 `legacy`로 즉시 롤백 가능.

### 전제 조건

- PR 2 병합 완료
- persistent 모드로 **최소 3회 이상** 실제 PR debate-review 성공

### 변경 파일

| 파일 | 작업 |
|------|------|
| `config.yml` | `agent_mode: persistent` (기본값 변경) |

### 검증

- [ ] 기본값 persistent로 debate-review 정상 동작
- [ ] `agent_mode: legacy`로 변경 시 롤백 정상

### debate-review 동작 영향: 기본 모드 변경 (롤백 가능)

---

## PR 4: legacy 코드 삭제 + 문서/테스트 정리

### 목적

Legacy 모드 코드를 제거하고 문서/테스트를 정리한다. 이 PR 이후 persistent 모드만 남는다.

### 전제 조건

- PR 3 병합 후 persistent 기본값으로 **충분한 기간** 운영 완료
- Legacy로 롤백할 필요가 없다고 판단

### 변경 파일

| 파일 | 작업 |
|------|------|
| `lib/debate_review/context.py` (275줄) | **삭제** |
| `tests/test_context.py` (263줄) | **삭제** |
| `agent-lead-review-prompt.md` (89줄) | **삭제** |
| `agent-cross-verify-prompt.md` (71줄) | **삭제** |
| `agent-lead-response-prompt.md` (95줄) | **삭제** |
| `cli.py` | `build-context` subcommand 제거 |
| `tests/test_cli.py` | `build-context` 관련 테스트 제거 |
| `SKILL.md` | legacy 모드 절차 제거, 모드 분기 제거 |
| `REFERENCE.md` | 재작성 — 설계 문서 Task 4 |
| `tests/test_prompt_docs.py` | 3개 템플릿 → `agent-initial-prompt.md` 존재 검증 |
| `config.yml` | `agent_mode` 필드 제거 (persistent만 남으므로 불필요) |
| `lib/debate_review/config.py` | `agent_mode` 필드 파싱 제거 |

### 검증

- [ ] `grep -r "build.context" skills/cc-codex-debate-review/` — 참조 없음
- [ ] `grep -r "agent-lead-review-prompt\|agent-cross-verify-prompt\|agent-lead-response-prompt" skills/cc-codex-debate-review/` — 참조 없음
- [ ] `grep -r "agent_mode\|legacy" skills/cc-codex-debate-review/` — 참조 없음
- [ ] `python -m pytest tests/` 전체 통과
- [ ] debate-review 실행 정상

### debate-review 동작 영향: legacy 제거 (롤백 불가)

---

## Updated Remaining Work

기존 rollout 계획을 현재 상태에 맞춰 재해석하면, 남은 일은 아래 다섯 묶음이다. 이 목록이 debate-review completion의 canonical backlog다.

### Workstream A: Persistent prompt / routing parity

기본값이 `persistent`이므로, 새 기능 계약은 먼저 persistent 경로에 반영되어야 한다.

- `#161`: `build-prompt` output JSON을 안정화해 persistent agent 초기화를 복구
- Step 1 / Step 2 prompt-step 템플릿이 최신 output schema를 반영
- duplicate withdrawal 같은 새 state transition이 step prompt, CLI, Step 4 정산까지 일관되게 연결
- `#164`가 state-side 기반은 병합했으므로, 남은 범위는 prompt/state parity와 stall-safe bookkeeping 정리다
- legacy / persistent 간 출력 schema 불일치 제거

### Workstream B: Application path hardening

Step 3 code application은 실제로 same-repo PR을 바꾸는 mutation 경로다.

- push verification 실패 후 resume 경로 검증
- phase1 / phase2 / phase3 중간 재시작 검증

참고:

- short SHA 정규화는 `#165`로 이미 병합되었다.
- 따라서 이 workstream의 남은 범위는 resume / verification robustness다.

### Workstream C: Repo-owned orchestration path

현재 가장 큰 구조적 공백이다. 저장소에는 state CLI는 있지만 round loop를 재현 가능하게 실행하는 repo-owned 경로가 없다.

- round loop 실행 경로 추가
- agent 생성 / resume / retry / recovery 구현
- CLI subcommand routing 자동화
- terminal 시 comment / cleanup 호출까지 연결
- 구현 형태는 Python runner로 고정하지 않는다. 다만 저장소 안에서 재현 가능하고 검증 가능해야 한다.

### Workstream D: Operational follow-through automation

현재 `SKILL.md`에만 있는 절차를 코드 또는 helper script로 내려야 한다.

- `mark-failed` 후 GitHub issue 생성
- final state 후 PR title/body 갱신
- worktree cleanup
- CI / runtime status 추적

### Workstream E: E2E verification

지금 테스트는 unit / contract 수준은 강하지만 운영 플로우 증명은 약하다.

- clean pass consensus
- same-repo code apply
- fork recommendation path
- supersede by external push
- persistent resume / recovery
- terminal comment dedupe

---

## 요약

| PR | 내용 | 위험도 | 롤백 |
|----|------|--------|------|
| 1 | `agent-initial-prompt.md` + `agent_mode` 플래그 | 낮음 | 불필요 (기본 legacy) |
| 2 | SKILL.md에 persistent 절차 추가 | **중간** | `agent_mode: legacy`로 즉시 롤백 |
| 3 | 기본값 `persistent`로 변경 | 낮음 | `agent_mode: legacy`로 즉시 롤백 |
| 4 | legacy 코드 삭제 + 문서 정리 | 낮음 | git revert |

### 의존 관계

```
선행 검증 ─→ PR 1 ─→ PR 2 ──→ PR 3 ──→ PR 4
                       │         │
                       │         └─ persistent 충분히 검증 후
                       └─ 양쪽 모드 실행 검증 후
```

### 병행 운영 기간

PR 2 병합 ~ PR 4 병합 사이에 양쪽 모드를 모두 사용할 수 있다.

- 평상시: `agent_mode: persistent` (PR 3 이후)
- 문제 발생 시: `agent_mode: legacy`로 config 변경 → 즉시 기존 방식으로 동작
- Legacy가 더 이상 불필요: PR 4 병합으로 코드 제거

### 현재 우선순위

현재 시점에서는 원래 문서의 "PR 1부터 다시 진행"보다 아래 우선순위가 더 정확하다.

1. `#161` 해소로 persistent initialization 복구
2. persistent prompt / state routing parity 복구
3. application path hardening
4. repo-owned orchestration path 정리
5. failure / cleanup / PR update 자동화
6. legacy 제거와 문서 정리
