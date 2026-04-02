# Debate Review: Persistent Agent 구현 태스크

## 설계 문서

[2026-04-01-debate-review-persistent-agent-design.md](./2026-04-01-debate-review-persistent-agent-design.md)

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

---

## 선행 검증 (PR 작업 전)

PR 1 착수 전에 runtime 요구사항을 검증한다.

| 검증 항목 | 방법 | 통과 기준 |
|-----------|------|----------|
| Agent Teams (SendMessage) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경에서 Agent 생성 후 SendMessage로 후속 지시 전달 | 응답 수신, context 유지 확인 |
| Codex session resume | `codex exec` 후 session ID 캡처 → `codex exec --resume` 재개 | 이전 turn context 보존 확인 |
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
