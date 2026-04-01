# Debate Review: Persistent Agent 구현 태스크

## 설계 문서

[2026-04-01-debate-review-persistent-agent-design.md](./2026-04-01-debate-review-persistent-agent-design.md)

## 핵심 제약: 증분 배포

**각 PR이 병합될 때마다 debate-review가 정상 작동해야 한다.**

현재 시스템은 `build-context` → 프롬프트 템플릿 치환 → 독립 agent 호출 흐름으로 동작한다. 새 시스템(persistent agent + append-only prompt)으로 전환할 때, 기존 코드를 먼저 삭제하면 시스템이 깨진다.

안전한 전환 순서:

```
[현재] build-context + 3 templates + SKILL.md(old)
  ↓ PR 1: 새 파일 추가 (기존 파일 유지)
[중간] build-context + 3 templates + agent-initial-prompt + SKILL.md(old)
  ↓ PR 2: SKILL.md 재작성 (새 흐름으로 전환)
[중간] build-context + 3 templates + agent-initial-prompt + SKILL.md(new)
  ↓ PR 3: 미사용 코드 삭제
[중간] agent-initial-prompt + SKILL.md(new)
  ↓ PR 4: REFERENCE.md + 테스트 정리
[완료] agent-initial-prompt + SKILL.md(new) + REFERENCE.md(new)
```

각 단계 후 debate-review 실행 가능 여부:
- PR 1 후: ✅ 기존 흐름 그대로 동작. 새 파일은 미사용 상태로 존재
- PR 2 후: ✅ 새 흐름으로 동작. 기존 파일은 미사용 상태로 존재
- PR 3 후: ✅ 미사용 코드 제거. 새 흐름 동작
- PR 4 후: ✅ 문서 + 테스트 정리 완료

---

## 선행 검증 (PR 작업 전)

PR 1 착수 전에 runtime 요구사항을 검증한다. 검증 실패 시 Fallback 전략(설계 문서 "Fallback: Fresh Agent + Transcript" 참조)으로 전환한다.

| 검증 항목 | 방법 | 통과 기준 |
|-----------|------|----------|
| Agent Teams (SendMessage) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경에서 Agent 생성 후 SendMessage로 후속 지시 전달 | 응답 수신, context 유지 확인 |
| Codex session resume | `codex exec` 후 session ID 캡처 → `codex exec --resume` 재개 | 이전 turn context 보존 확인 |
| 장시간 안정성 | 3+ turns 연속 SendMessage / resume | crash 없이 동작 |

검증 결과에 따라:
- **모두 통과**: persistent agent 방식으로 진행
- **CC만 통과**: CC는 SendMessage, Codex는 매 step fresh agent + transcript fallback
- **모두 실패**: 양쪽 모두 transcript fallback 방식

---

## PR 1: agent-initial-prompt.md 추가

### 목적

Persistent agent 생성 시 사용할 initial prompt 파일을 추가한다. 기존 시스템에는 영향 없음.

### 변경 파일

| 파일 | 작업 |
|------|------|
| `agent-initial-prompt.md` (~40줄) | **신규** — 설계 문서 Task 2의 initial prompt |

### 내용

설계 문서의 `agent-initial-prompt.md` 섹션 그대로 작성:
- `{REPO}`, `{PR_NUMBER}`, `{WORKTREE_PATH}`, `{OUTPUT_LANGUAGE}`, `{REVIEW_CRITERIA}` placeholder
- agent 역할 설명, 탐색 방법, 출력 규칙

### 검증

- [ ] 파일 문법 오류 없음 (placeholder 형식 일관성)
- [ ] 기존 debate-review 실행 시 영향 없음 (이 파일을 참조하는 코드 없음)

### debate-review 동작 영향: 없음

---

## PR 2: SKILL.md 재작성 — persistent agent 전환

### 목적

Orchestrator 절차를 persistent agent 방식으로 전환한다. 이 PR이 핵심 변경이며, 병합 후 debate-review는 새 흐름으로 동작한다.

### 전제 조건

- PR 1 병합 완료 (`agent-initial-prompt.md` 존재)
- 선행 검증 완료 (runtime 요구사항 확인)

### 변경 파일

| 파일 | 작업 |
|------|------|
| `SKILL.md` | 재작성 — 설계 문서 Task 3 전체 |

### 섹션별 변경 (설계 문서 Task 3 참조)

| 섹션 | 변경 |
|------|------|
| Agent Invocation | 전면 재작성 → Agent Lifecycle (Create + Resume) |
| Review Context + Placeholder Construction | **제거** → Step Message Construction으로 교체 |
| Step 1/2/3 절차 | placeholder 참조 제거 → SendMessage/resume 방식 |
| Step Message Format | **추가** — 각 step의 message format 명시 |
| Step Message 데이터 소스 | **추가** — 각 데이터의 출처 명시 |
| Restart Rules | 수정 → agent 생존/사망 분기 |
| Supersede Handling | 수정 → agent에게 메시지 전달 |

### 검증

- [ ] SKILL.md가 `build-context`를 호출하지 않음
- [ ] SKILL.md가 `agent-lead-review-prompt.md`, `agent-cross-verify-prompt.md`, `agent-lead-response-prompt.md`를 참조하지 않음
- [ ] SKILL.md가 `agent-initial-prompt.md`를 참조함
- [ ] 실제 PR에서 debate-review 실행하여 전체 라운드 동작 확인

### debate-review 동작 영향: 전환 — 기존 흐름 → 새 흐름

---

## PR 3: 미사용 코드 삭제

### 목적

PR 2에서 더 이상 참조하지 않는 파일과 코드를 삭제한다.

### 전제 조건

- PR 2 병합 완료 (SKILL.md가 더 이상 이 파일들을 참조하지 않음)

### 변경 파일

| 파일 | 작업 |
|------|------|
| `lib/debate_review/context.py` (275줄) | **삭제** |
| `tests/test_context.py` (263줄) | **삭제** |
| `agent-lead-review-prompt.md` (89줄) | **삭제** |
| `agent-cross-verify-prompt.md` (71줄) | **삭제** |
| `agent-lead-response-prompt.md` (95줄) | **삭제** |
| `cli.py` | `build-context` subcommand 제거 (import, parser, handler, commands entry) |
| `tests/test_cli.py` | `build-context` 관련 테스트 제거 |

### cli.py 구체적 변경

설계 문서 Task 1의 "cli.py 구체적 변경" 섹션 참조:
- `from debate_review.context import build_context` 제거
- `build-context` parser 등록 제거
- `cmd_build_context` 함수 제거
- commands dict entry 제거

### 검증

- [ ] `grep -r "build.context" skills/cc-codex-debate-review/` — SKILL.md, cli.py, tests에 참조 없음
- [ ] `grep -r "agent-lead-review-prompt\|agent-cross-verify-prompt\|agent-lead-response-prompt" skills/cc-codex-debate-review/` — 참조 없음
- [ ] `python -m pytest tests/` 전체 통과
- [ ] debate-review 실행 정상

### debate-review 동작 영향: 없음 (미사용 코드 삭제)

---

## PR 4: REFERENCE.md 재작성 + 테스트 정리

### 목적

문서와 테스트를 새 아키텍처에 맞게 정리한다.

### 전제 조건

- PR 3 병합 완료

### 변경 파일

| 파일 | 작업 |
|------|------|
| `REFERENCE.md` | 재작성 — 설계 문서 Task 4 |
| `tests/test_prompt_docs.py` | 3개 템플릿 검증 → `agent-initial-prompt.md` 존재 검증 |

### 검증

- [ ] REFERENCE.md가 새 아키텍처(initial prompt, step message data sources, agent invocation)를 반영
- [ ] `python -m pytest tests/test_prompt_docs.py` 통과
- [ ] debate-review 실행 정상

### debate-review 동작 영향: 없음 (문서 + 테스트만 변경)

---

## 요약

| PR | 내용 | 줄 변화 | 위험도 |
|----|------|---------|--------|
| 1 | `agent-initial-prompt.md` 추가 | +40 | 낮음 (기존 시스템 무영향) |
| 2 | SKILL.md 재작성 | -200 / +180 | **높음** (핵심 전환) |
| 3 | 미사용 코드 삭제 | -793 | 낮음 (dead code 제거) |
| 4 | REFERENCE.md + 테스트 정리 | -15 / +30 | 낮음 (문서 + 테스트) |
| **합계** | | **~538줄 감소** | |

### 의존 관계

```
선행 검증 ─→ PR 1 ─→ PR 2 ─→ PR 3 ─→ PR 4
```

각 PR은 직전 PR 병합 후에만 착수한다. 모든 PR 병합 후 debate-review는 persistent agent 방식으로 동작한다.
