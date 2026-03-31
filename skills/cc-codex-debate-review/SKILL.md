---
name: cc-codex-debate-review
description: CC와 Codex가 교대 lead agent로 반복 리뷰하며 토론 합의에 도달하는 PR 리뷰 오케스트레이션
---

# CC-Codex Debate Review

## 개요

Open PR에 대해 Claude Code(CC)와 Codex 두 AI Agent가 반복적으로 리뷰, 반박, 수정을 수행하고, 두 Agent가 모든 issue에 대해 동일한 결론에 도달할 때까지 토론을 반복하는 시스템.

CC는 오케스트레이터이자 짝수 라운드 lead agent. Codex는 `codex exec`로 호출되는 서브프로세스이자 홀수 라운드 lead agent.

**상태 관리는 CLI가 담당한다.** CC는 `$DEBATE_REVIEW_BIN` subcommand를 호출하여 상태를 조작하고, 리뷰 자체(finding 생성, rebuttal 판단)만 직접 수행한다.

```
CC (오케스트레이터)
  ├─ $DEBATE_REVIEW_BIN <subcommand> → 상태 관리 (CLI)
  ├─ codex exec ...                  → Codex 호출 (홀수 lead, 짝수 cross)
  └─ CC 자체 리뷰                     → 짝수 lead, 홀수 cross
```

## 사용 시점

- PR에 대해 두 Agent의 합의 기반 리뷰가 필요할 때
- 호출 예시: `debate-review를 실행해줘 (repo=owner/repo, pr=123)`

## 입력

아래 경로는 모두 `cc-codex-debate-review/` 디렉토리 기준이다.

| 입력 | 경로 |
|------|------|
| CLI | `./bin/debate-review` |
| 설정 파일 | `./config.yml` |
| 리뷰 기준 | `./review-criteria.md` |
| Codex 프롬프트 | `./codex-*.md` |

### 사전조건

- 대상 repo의 로컬 클론 필수
- `gh auth` 인증 완료
- `codex` CLI 사용 가능
- `$DEBATE_REVIEW_BIN` 실행 가능

## GitHub CLI 규칙

CLI 내부의 모든 `gh` 호출은 주입된 토큰 변수를 제거하고 keyring 인증을 사용한다. CC가 직접 `gh`를 호출할 때도 동일 규칙:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

---

## 절차

### 1. 초기화

#### 설정 로드

```bash
SKILL_ROOT="<path-to-cc-codex-debate-review>"
DEBATE_REVIEW_BIN="$SKILL_ROOT/bin/debate-review"
CONFIG_FILE="$SKILL_ROOT/config.yml"
```

설정 파일에서 값을 읽는다:
```bash
MAX_ROUNDS=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['max_rounds'])")
CODEX_SANDBOX=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('codex_sandbox', 'read-only'))")
```

#### 인자 확인

호출 시 `REPO` (예: `owner/repo`)와 `PR_NUMBER`를 인자로 받는다. 둘 중 하나라도 없으면 즉시 중단.

#### 세션 초기화

```bash
RESULT=$("$DEBATE_REVIEW_BIN" init --repo "$REPO" --pr "$PR_NUMBER" \
  --config "$CONFIG_FILE")
```

`RESULT` JSON에서 추출:
```bash
STATE_FILE=$(echo "$RESULT" | jq -r '.state_file')
STATUS=$(echo "$RESULT" | jq -r '.status')           # "created" | "resumed"
CURRENT_ROUND=$(echo "$RESULT" | jq -r '.current_round')
IS_FORK=$(echo "$RESULT" | jq -r '.is_fork')
DRY_RUN=$(echo "$RESULT" | jq -r '.dry_run')
```

`STATUS`가 `resumed`이면 → **재시작 절차** (아래 참조)로 분기.

#### 상태 확인 (필요 시)

```bash
"$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json
```

현재 상태 전체를 JSON으로 출력. `journal.step`으로 재시작 위치를 파악할 때 사용.

---

### 2. 라운드 루프

초기화 완료 후 `CURRENT_ROUND`부터 루프 시작. 각 라운드:

1. Step 0: PR HEAD 동기화
2. Lead agent 결정 + 라운드 초기화
3. Step 1: Lead agent 리뷰 (1a: 미결 rebuttal 처리 → 1b: 새 리뷰 + verdict)
4. Step 2: Cross-verifier 교차 검증 (clean pass 시 생략)
5. Step 3: Lead agent 응답 + 코드 반영 (clean pass 시 생략)
6. Step 4: 정산

---

### Step 0: PR HEAD 동기화

```bash
SYNC_RESULT=$("$DEBATE_REVIEW_BIN" sync-head --state-file "$STATE_FILE")
```

CLI가 git fetch, worktree 관리, supersede 감지를 모두 처리한다.

`SYNC_RESULT`에서 `external_change: true`이면 supersede 발생. CLI가 이미 issue 상태 재설정과 `current_round` 증가를 처리했으므로, CC는 `show --json`으로 최신 상태를 다시 읽고 `CURRENT_ROUND`를 갱신한 뒤 새 라운드로 진행한다.

```bash
if [ "$(echo "$SYNC_RESULT" | jq -r '.external_change')" = "true" ]; then
  STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
  CURRENT_ROUND=$(echo "$STATE_JSON" | jq -r '.current_round')
fi
```

---

### Lead Agent 결정 + 라운드 초기화

| 라운드 | Lead Agent | Cross-Verifier |
|--------|-----------|----------------|
| 홀수 (1, 3, 5, ...) | Codex | CC |
| 짝수 (2, 4, 6, ...) | CC | Codex |

```bash
if [ $((CURRENT_ROUND % 2)) -eq 1 ]; then
  LEAD_AGENT="codex"
  CROSS_VERIFIER="cc"
else
  LEAD_AGENT="cc"
  CROSS_VERIFIER="codex"
fi

STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
REPO_ROOT=$(echo "$STATE_JSON" | jq -r '.repo_root')
WORKTREE_PATH="$REPO_ROOT/.worktrees/debate-pr-$PR_NUMBER"
HEAD_BRANCH=$(echo "$STATE_JSON" | jq -r '.head.pr_branch_name')
SYNCED_SHA=$(echo "$SYNC_RESULT" | jq -r '.post_sync_sha')

"$DEBATE_REVIEW_BIN" init-round \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --lead-agent "$LEAD_AGENT" \
  --synced-head-sha "$SYNCED_SHA"
```

---

### Step 1: Lead Agent 리뷰

#### Step 1a: 미결 rebuttal 처리

이전 라운드에서 상대 agent가 보낸 rebuttal이 있으면, lead agent가 각각에 대해 `withdraw` 또는 `maintain`을 결정한다.

이전 라운드의 rebuttal은 `show --json` 출력의 `rounds[N-1].step3.rebuttals`에서 확인.

Lead agent (CC 또는 Codex)가 결정을 내리면:

```bash
"$DEBATE_REVIEW_BIN" resolve-rebuttals \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --step "1a" \
  --decisions '[{"report_id": "rpt_003", "decision": "withdraw", "reason": "반박 수용"}]'
```

`maintain`으로 결정한 finding은 Step 1b에서 반드시 재보고해야 한다.

CLI 응답의 `re_report_ids` 배열에 `maintain`으로 결정된 report ID들이 포함된다. 이 ID들에 해당하는 issue를 Step 1b findings에 포함시켜야 한다.

이전 라운드가 없거나 rebuttal이 없으면 건너뛴다.

#### Step 1b: 새 리뷰

**Codex가 lead일 때 (홀수 라운드):**

> **중요:** `codex-lead-review-prompt.md`는 Step 1a(rebuttal 처리)와 Step 1b(새 리뷰)를 **하나의 호출**로 처리한다. Codex 응답에서 `rebuttal_responses`는 `resolve-rebuttals --step "1a"`로, `findings`는 `upsert-issue`로, `verdict`는 `record-verdict`로 각각 전달한다.

1. 리뷰 컨텍스트 구성 (CC가 상태 데이터로 생성)
2. 프롬프트 템플릿 읽기: `./codex-lead-review-prompt.md` (`$SKILL_ROOT/codex-lead-review-prompt.md`)
3. 플레이스홀더 치환: `{REPO}`, `{PR_NUMBER}`, `{PR_TITLE}`, `{PR_BODY}`, `{ROUND}`, `{REVIEW_CONTEXT}`, `{DEBATE_LEDGER}`, `{OPEN_ISSUES}`, `{PENDING_REBUTTALS}`, `{REVIEW_CRITERIA}`, `{DIFF}`
4. PR diff 획득:
   ```bash
   DIFF=$(env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff "$PR_NUMBER" --repo "$REPO")
   ```
5. Codex 실행:
   ```bash
   cd "$WORKTREE_PATH"
   # 프롬프트를 임시 파일로 저장하고 stdin으로 전달 (ARG_MAX 초과 방지)
   PROMPT_FILE=$(mktemp /tmp/debate-prompt-XXXXXX.txt)
   printf '%s' "$FILLED_PROMPT" > "$PROMPT_FILE"
   codex exec -s "$CODEX_SANDBOX" - < "$PROMPT_FILE"
   rm -f "$PROMPT_FILE"
   ```
6. JSON 응답 파싱 (실패 시 최대 3회 재시도)
7. 응답 분배:
   - `rebuttal_responses` → `resolve-rebuttals --step "1a"` (비어 있지 않으면)
   - `findings` → 각 항목을 `upsert-issue`로 기록
   - `verdict` → `record-verdict`로 기록

**CC가 lead일 때 (짝수 라운드):**

CC가 직접 diff, 리뷰 컨텍스트, 리뷰 기준을 읽고 리뷰를 수행. 출력 형식은 Codex와 동일한 JSON 구조.

#### Finding을 상태에 기록

Lead agent의 각 finding에 대해 `upsert-issue` 호출:

```bash
"$DEBATE_REVIEW_BIN" upsert-issue \
  --state-file "$STATE_FILE" \
  --agent "$LEAD_AGENT" \
  --round "$CURRENT_ROUND" \
  --severity "critical" \
  --criterion 1 \
  --file "src/foo.ts" \
  --line 42 \
  --anchor "validate_input" \
  --message "입력값 검증 누락"
```

`anchor`는 심볼명, 함수명 등 라인 이동에 덜 민감한 식별자를 우선 사용. 없으면 `line<N>`.

#### Verdict 기록

```bash
"$DEBATE_REVIEW_BIN" record-verdict \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verdict "has_findings"
```

**Clean pass 판정:** finding이 0건이고, 모든 기존 issue가 해결되었으면:
- `--verdict "no_findings_mergeable"`
- Step 2, 3을 건너뛰고 Step 4로 진행

---

### Step 2: Cross-Verifier 교차 검증

**전제:** clean pass가 아닌 경우에만 실행.

Cross-verifier가 두 가지를 수행:
1. Lead의 각 report에 대해 `accept` 또는 `rebut`
2. 자체 새 findings 보고

**Codex가 cross-verifier일 때 (짝수 라운드):**

프롬프트 템플릿: `./codex-cross-verify-prompt.md` (`$SKILL_ROOT/codex-cross-verify-prompt.md`)
플레이스홀더: `{LEAD_AGENT_ID}`, `{LEAD_REPORTS}` 외 동일.

**CC가 cross-verifier일 때 (홀수 라운드):**

CC가 직접 lead의 report를 평가하고 자체 findings 생성.

#### 교차 검증 결과 기록

```bash
"$DEBATE_REVIEW_BIN" record-cross-verification \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verifications '[
    {"report_id": "rpt_001", "decision": "accept", "reason": "타당한 finding"},
    {"report_id": "rpt_002", "decision": "rebut", "reason": "의도적 중복"}
  ]'
```

#### Cross-verifier의 새 findings 기록

Cross-verifier의 각 새 finding도 `upsert-issue`로 기록:

```bash
"$DEBATE_REVIEW_BIN" upsert-issue \
  --state-file "$STATE_FILE" \
  --agent "$CROSS_VERIFIER" \
  --round "$CURRENT_ROUND" \
  --severity "warning" \
  --criterion 7 \
  --file "src/config.ts" \
  --line 15 \
  --anchor "TIMEOUT" \
  --message "하드코딩된 타임아웃 값"
```

CLI가 agent role에 따라 step1/step2 tracking을 자동 라우팅한다.

---

### Step 3: Lead Agent 응답 + 코드 반영

**전제:** clean pass가 아닌 경우에만 실행.

Lead agent가 세 가지를 처리:
1. Cross-verifier의 rebuttal에 대한 응답 (withdraw/maintain)
2. Cross-verifier의 새 findings 평가 (accept/maintain)
3. 합의된 issue에 대한 코드 반영 (동일 저장소 PR만)

**Codex가 lead일 때:**

프롬프트 템플릿: `./codex-lead-response-prompt.md` (`$SKILL_ROOT/codex-lead-response-prompt.md`)
플레이스홀더: `{CROSS_REBUTTALS}`, `{CROSS_FINDINGS}`, `{APPLICABLE_ISSUES}` 외 동일.

**CC가 lead일 때:**

CC가 직접 rebuttal 처리, cross findings 평가, 코드 수정 수행.

#### Rebuttal 응답 + Cross Findings 평가 기록

Lead agent가 두 가지를 처리:
1. Cross-verifier의 rebuttal에 대한 응답: `withdraw` (수용) 또는 `maintain` (거부, 다음 라운드 반박으로 전달)
2. Cross-verifier의 새 findings 평가: `accept` (수락) 또는 `maintain` (거부, 다음 라운드 반박으로 전달)

모든 결정을 하나의 `resolve-rebuttals --step "3"` 호출로 기록:

```bash
"$DEBATE_REVIEW_BIN" resolve-rebuttals \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --step "3" \
  --decisions '[
    {"report_id": "rpt_002", "decision": "withdraw", "reason": "반박 수용"},
    {"report_id": "rpt_005", "decision": "accept", "reason": "타당한 지적"},
    {"report_id": "rpt_006", "decision": "maintain", "reason": "이미 처리된 사항"}
  ]'
```

`--step "3"` 결정 값:
- `withdraw`: lead 자신의 finding 철회 (rebuttal 수용)
- `maintain`: 거부 — 다음 라운드에서 상대 agent의 rebuttal로 전달됨
- `accept`: cross-verifier의 finding 수락 (합의에 추가)

#### Codex code_fixes 적용

Codex가 lead이고 `code_fixes` 배열이 비어 있지 않으면, CC가 각 diff를 워크트리에 적용한다.

**Fork PR에서는 code_fixes 적용을 건너뛴다.** push가 불가능하므로 워크트리에 패치를 적용해도 의미가 없다. `IS_FORK`가 `true`이면 이 섹션 전체를 생략.

**`DRY_RUN=true`이면 실제 워크트리 변경도 금지한다.** 검토용 시뮬레이션이므로 `git apply`, `git commit`, `git push`는 실행하지 않고, agent가 제안한 `code_fixes`와 적용 대상 issue만 기록한 뒤 정산 단계로 진행한다.

각 `code_fixes` 항목의 `diff` 값을 파일에 저장하고 `git apply`로 적용:

```bash
STAGED_FILES=$(mktemp)

# 각 code_fix 항목에 대해 반복
PATCH_FILE=$(mktemp /tmp/debate-patch-XXXXXX.patch)
printf '%s\n' "$DIFF_CONTENT" > "$PATCH_FILE"
git -C "$WORKTREE_PATH" apply --check "$PATCH_FILE"  # 검증
git -C "$WORKTREE_PATH" apply "$PATCH_FILE"           # 적용
git -C "$WORKTREE_PATH" apply --numstat "$PATCH_FILE" | awk '{print $3}' >> "$STAGED_FILES"
rm -f "$PATCH_FILE"
```

- `--check` 실패 시 해당 issue_id를 `failed-issues`로 기록하고 다음 항목으로 진행
- 모든 적용이 끝난 후 Phase 1의 `--applied-issues`와 `--failed-issues`에 반영
- 성공한 patch가 실제로 수정한 파일 경로를 누적해 두고, Phase 2에서 중복 제거 후 스테이징한다
- CC가 lead일 때는 CC가 직접 코드를 수정한다 (code_fixes 불필요)

#### 코드 반영 (동일 저장소 PR, 3-phase)

`consensus_status=accepted`이고 `application_status=pending|failed`인 모든 issue를 lead agent가 수정.

`DRY_RUN=true`이면 아래 3개 phase를 모두 생략한다. dry-run에서는 상태 검증만 수행하고 commit/push를 만들지 않는다.

**Phase 1: 반영 결과 기록**

```bash
"$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --applied-issues '["isu_001", "isu_003"]' \
  --failed-issues '["isu_002"]'
```

**Phase 2: commit SHA 기록**

코드 수정 후 commit (수정된 파일만 스테이징). 성공한 patch가 없으면 commit을 건너뛴다:
```bash
sort -u "$STAGED_FILES" | while IFS= read -r path; do
  [ -n "$path" ] && git -C "$WORKTREE_PATH" add -- "$path"
done
rm -f "$STAGED_FILES"
if git -C "$WORKTREE_PATH" diff --cached --quiet; then
  # 실제 반영된 변경사항 없음 → commit/push 건너뜀
  COMMIT_SHA=""
else
  git -C "$WORKTREE_PATH" commit -m "fix: apply debate review findings (round $CURRENT_ROUND)"
  COMMIT_SHA=$(git -C "$WORKTREE_PATH" rev-parse HEAD)
fi
```

스테이징 대상은 각 성공한 patch의 diff에서 추출한 실제 변경 파일 경로(중복 제거 후) 또는 CC가 직접 수정한 파일 경로다. `code_fixes`의 `file` 필드는 대표 경로 힌트로만 취급하고, `git add -A`는 사용하지 않는다.

`COMMIT_SHA`가 비어 있으면 (`applied-issues`가 없거나 모든 patch가 실패한 경우) `--commit-sha`와 Phase 3를 건너뛴다.

```bash
[ -n "$COMMIT_SHA" ] && "$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --commit-sha "$COMMIT_SHA"
```

**Phase 3: push 검증**

`DRY_RUN=true`이면 이 단계도 실행하지 않는다. `COMMIT_SHA`가 비어 있으면 push 및 검증을 건너뛴다.

```bash
[ -n "$COMMIT_SHA" ] && git -C "$WORKTREE_PATH" push origin "HEAD:$HEAD_BRANCH"
```

```bash
[ -n "$COMMIT_SHA" ] && "$DEBATE_REVIEW_BIN" record-application \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND" \
  --verify-push
```

CLI가 실제 PR HEAD를 조회하여 commit SHA와 일치하는지 검증한다.

**Fork PR에서는 3-phase를 모두 건너뛴다.** (push 불가, `application_status=recommended`로 설정됨)

---

### Step 4: 정산

```bash
SETTLE_RESULT=$("$DEBATE_REVIEW_BIN" settle-round \
  --state-file "$STATE_FILE" \
  --round "$CURRENT_ROUND")
```

`SETTLE_RESULT.result` 값에 따른 분기:

| 결과 | 의미 | 다음 행동 |
|------|------|----------|
| `continue` | 합의 미달 | `next_round`로 라운드 루프 반복 |
| `consensus_reached` | 합의 도달 | Terminal 처리 → 코멘트 게시 |
| `max_rounds_exceeded` | 최대 라운드 초과 | Terminal 처리 → 코멘트 게시 |

`continue`면:
```
CURRENT_ROUND=$(echo "$SETTLE_RESULT" | jq -r '.next_round')
# 라운드 루프 처음(Step 0)으로
```

---

### Terminal 처리 + 최종 코멘트

`consensus_reached` 또는 `max_rounds_exceeded` 도달 시:

```bash
"$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE"
```

CLI가 상태에 따라 적절한 템플릿으로 코멘트를 생성하고 PR에 게시한다. 중복 게시 방지도 CLI가 처리.

dry-run 모드이거나 코멘트 게시를 생략하려면:

```bash
"$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE" --no-comment
```

코멘트 본문이 stdout에 출력되고 실제 게시는 생략.

#### PR Title / Description 업데이트

코드 수정이 반영된 경우, PR title과 description이 최종 변경 내역을 정확히 반영하도록 업데이트한다.

1. 현재 PR title/body 확인:
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr view "$PR_NUMBER" --repo "$REPO" --json title,body
   ```
2. 최종 diff 기준으로 변경 내역 재분석:
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr diff "$PR_NUMBER" --repo "$REPO"
   ```
3. PR title/body가 최신 코드와 불일치하면 업데이트 (`DRY_RUN=true`이면 이 단계를 건너뛴다):
   ```bash
   env -u GITHUB_TOKEN -u GH_TOKEN gh pr edit "$PR_NUMBER" --repo "$REPO" \
     --title "$UPDATED_TITLE" \
     --body "$UPDATED_BODY"
   ```

**업데이트 기준:**
- Debate review에서 적용된 수정사항이 반영되었는지
- 파일 줄 수, 구조, 설정 항목 등 구체적 수치가 정확한지
- 코드 예시(명령어, 변수명 등)가 실제 코드와 일치하는지
- `debate_ledger`가 비어 있지 않으면, `## Debate Review Summary` 섹션을 PR description 하단에 추가하여 주요 토론 결과를 기록

코드 수정이 없었으면 (모든 라운드가 clean pass였으면) 이 단계를 건너뛴다.

#### 워크트리 정리

Terminal 상태 후:

```bash
git -C "$REPO_ROOT" worktree remove "$WORKTREE_PATH" --force
```

---

## 리뷰 컨텍스트 구성

Step 1과 Step 2에서 agent에게 리뷰를 요청할 때, 직전 2개 라운드의 경과를 컨텍스트로 전달한다.

**범위:** `max(1, current_round - 2)` ~ `current_round - 1`의 completed/superseded 라운드. Round 1에서는 `{REVIEW_CONTEXT}`에 `(첫 라운드 — 이전 리뷰 없음)`을 전달한다.

직전 2개 라운드 요약만으로는 더 오래된 미해결 issue가 빠질 수 있으므로, Codex lead Step 1 프롬프트에는 현재 unresolved issue 전체를 `{OPEN_ISSUES}`로 별도 전달한다.

**구성 항목:**
1. 라운드 메타데이터: 번호, lead agent, status, clean_pass
2. Step 1 결과: findings 요약 (issue ID, severity, file, message)
3. Step 2 결과: accept/rebut 판정 + 새 findings
4. Step 3 결과: rebuttal 응답 + 코드 반영 결과
5. 미해결 issue 현황

**생성 방법:** `show --json` 출력의 `rounds[]`와 `issues`로부터 CC가 구성한다.

**형식:**

```text
## 리뷰 컨텍스트 (라운드 <N-2> ~ <N-1>)

### 라운드 <N-2> [lead: <agent>, status: <status>, clean_pass: <bool>]

**Step 1 (<agent> 리뷰):**
- isu_001 (warning) src/foo.ts:42 — 무한 재시도 루프

**Step 2 (<agent> 교차 검증):**
- rpt_001 (isu_001): accepted
- rpt_002 (isu_002): rebutted — "사유"

**Step 3 (<agent> 응답 + 반영):**
- rpt_002 rebuttal: accepted → isu_002 withdrawn
- 반영 완료: isu_001, isu_003

**미해결 issue:** (없음)
```

---

## Debate Ledger 관리

토론이 길어질 때(5+ 라운드) agent가 이전 라운드의 결정을 참조할 수 있도록, 전 라운드에 걸친 issue별 결론을 누적 기록한다.

### Ledger 작성 시점

Step 4 (`settle-round`) 실행 후, 오케스트레이터(CC)가 반환값의 `settled_issues`를 확인한다. 각 settled issue에 대해 1줄 요약을 작성하여 state file의 `debate_ledger` 배열에 append한다.

### Ledger 항목 형식

```json
{
  "issue_id": "isu_001",
  "status": "accepted",
  "reason": null,
  "summary": "batch exit code 누락 — R1 Codex 제기, R1 CC accept, R3 반영",
  "round": 3
}
```

- `status`: `accepted` 또는 `withdrawn`
- `reason`: `consensus_reason` 값. withdrawn 시 철회 사유, accepted 시 `null`. 재제기 시 이전 사유와의 차별점 판단에 사용
- `summary`: issue 내용, 제기/합의/철회 경과를 1줄로 요약 (오케스트레이터가 자연어로 작성)
- `round`: 해당 결론이 확정된 라운드 번호

### Ledger 기록 방법

`settle-round` 결과에 `settled_issues`가 있으면, 오케스트레이터가 state file을 읽어 `debate_ledger` 배열에 항목을 추가하고 저장한다:

```bash
# settle-round 후, settled_issues가 있으면:
STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json)
# CC가 settled_issues 각 항목에 대해 summary를 작성
# state file의 debate_ledger에 append 후 저장
python3 - "$STATE_FILE" "$LEDGER_JSON" <<'PY'
import json, sys
path, ledger_json = sys.argv[1], sys.argv[2]
with open(path) as f:
    state = json.load(f)
entries = json.loads(ledger_json)
state.setdefault("debate_ledger", []).extend(entries)
import tempfile, os
dir_ = os.path.dirname(path)
with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
    json.dump(state, f, indent=2)
    tmp = f.name
os.replace(tmp, path)
PY
```

### 이미 ledger에 있는 issue의 재등장

withdrawn 후 재제기되어 다시 settled되면, 새 항목을 append한다 (이전 항목은 유지). 이력이 누적되므로 agent가 해당 issue의 전체 논의 흐름을 파악할 수 있다.

### {DEBATE_LEDGER} placeholder

프롬프트에 전달할 때, `debate_ledger` 배열을 아래 텍스트 형식으로 변환한다:

```text
## Debate Ledger (전체 라운드 결론 요약)

- isu_001 [accepted] batch exit code 누락 — R1 Codex 제기, R1 CC accept, R3 반영
- isu_003 [withdrawn] (reason: 의도적 설계 선택) KeyboardInterrupt 처리 — R1 Codex 제기, R2 CC rebut, R5 Codex withdraw

이전에 withdrawn된 issue를 재제기하려면, 위 기록의 reason과 다른 새로운 근거를 제시해야 합니다.
```

배열이 비어 있으면 `(첫 라운드 — 이전 결론 없음)`을 전달한다.

---

## 재시작 규칙

재시작은 항상 `init`부터:

```bash
RESULT=$("$DEBATE_REVIEW_BIN" init --repo "$REPO" --pr "$PR_NUMBER" \
  --config "$CONFIG_FILE")
# STATUS = "resumed"
```

`show --json`으로 `journal.step`을 확인하여 재개 위치 결정:

| journal.step | 다음 행동 |
|--------------|----------|
| `init` | Step 0 (sync-head)부터 |
| `step0_sync` | Step 1 (리뷰)부터 |
| `step1_lead_review` | clean_pass=true면 Step 4, 아니면 Step 2 |
| `step2_cross_review` | Step 3 |
| `step3_lead_apply` | journal 체크포인트 확인 후 미완료 phase부터 |
| `step4_settle` | 다음 라운드 Step 0 |

### Step 3 재시작 상세

`journal.step = step3_lead_apply`일 때 체크포인트 확인:

1. `journal.push_verified = true` → Step 3 완료, Step 4로
2. `journal.commit_sha`가 있고 PR HEAD와 일치 → push 성공으로 간주, Phase 3 재실행 (`--verify-push`)
3. `journal.commit_sha`가 있고 PR HEAD와 불일치 → push 미완, CC가 push 재시도 후 Phase 3
4. `journal.commit_sha = null` → Phase 2부터 (commit 재생성)
5. `journal.applied_issue_ids`가 비어 있음 → Phase 1부터

---

## 실패 처리

| 실패 유형 | 처리 방식 |
|-----------|----------|
| sync 실패 | 즉시 중단, 다음 실행 시 sync부터 재시도 |
| 리뷰 분석 실패 | 해당 step 재시도 |
| Codex JSON 파싱 실패 | 동일 step 최대 3회 재시도, 초과 시 에러 종료 |
| commit 실패 | Phase 1까지 기록된 상태에서 재시도 |
| push 실패 | Phase 2까지 기록된 상태에서 push 재시도 |
| CLI exit code 1 | JSON 에러 메시지 파싱, 원인 파악 후 조치 |

에러 종료 시 stale 세션이 resume되지 않도록 먼저 state file을 terminal failed 상태로 기록한다. `debate-review init`은 `status=in_progress` 세션을 그대로 재개하므로, fatal error 경로에서는 이 단계가 필수다. 현재 CLI에 전용 subcommand가 없으므로 이 경로만 예외적으로 state file을 직접 갱신한 뒤 (`DRY_RUN=true`이면 `--no-comment` 추가) 최종 코멘트를 게시하고 워크트리를 정리한다.

```bash
ERROR_MESSAGE=${ERROR_MESSAGE:-"Unknown error"}
python3 - "$STATE_FILE" "$ERROR_MESSAGE" <<'PY'
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

path, error_message = sys.argv[1], sys.argv[2]
with open(path) as f:
    state = json.load(f)

state["status"] = "failed"
state["final_outcome"] = "error"
state["finished_at"] = datetime.now(timezone.utc).isoformat()
state["error_message"] = error_message
state["head"]["terminal_sha"] = state["head"]["last_observed_pr_sha"]
state["journal"]["state_persisted"] = True

dir_ = os.path.dirname(path)
with tempfile.NamedTemporaryFile("w", dir=dir_, delete=False, suffix=".tmp") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
    tmp_path = f.name
os.replace(tmp_path, path)
PY

if [ "$DRY_RUN" = "true" ]; then
  "$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE" --no-comment
else
  "$DEBATE_REVIEW_BIN" post-comment --state-file "$STATE_FILE"
fi

if [ -z "${WORKTREE_PATH:-}" ]; then
  STATE_JSON=$("$DEBATE_REVIEW_BIN" show --state-file "$STATE_FILE" --json 2>/dev/null || true)
  REPO_ROOT=$(printf '%s' "$STATE_JSON" | jq -r '.repo_root // empty')
  [ -n "$REPO_ROOT" ] && WORKTREE_PATH="$REPO_ROOT/.worktrees/debate-pr-$PR_NUMBER"
fi

if [ -n "${WORKTREE_PATH:-}" ] && [ -d "$WORKTREE_PATH" ]; then
  git -C "$REPO_ROOT" worktree remove "$WORKTREE_PATH" --force || true
fi
```

CLI가 에러 템플릿으로 코멘트를 생성하고, cleanup 가능할 때 stale worktree를 제거한다.

---

## Codex 호출 참고

| Step | 템플릿 | 용도 |
|------|--------|------|
| Step 1 (Codex lead) | `codex-lead-review-prompt.md` | 리뷰 + rebuttal 처리 |
| Step 2 (Codex cross) | `codex-cross-verify-prompt.md` | 교차 검증 + 자체 findings |
| Step 3 (Codex lead) | `codex-lead-response-prompt.md` | 응답 + 코드 수정 |

호출 패턴:
1. 프롬프트 템플릿 읽기
2. 플레이스홀더 치환 (아래 도출 방법 참조)
3. 프롬프트 파일을 stdin으로 전달하며 `codex exec -s "$CODEX_SANDBOX" - < "$PROMPT_FILE"` 실행
4. JSON 출력 파싱 (실패 시 최대 3회 재시도)

#### 플레이스홀더 도출 방법

공통 플레이스홀더:
- `{REPO}`, `{PR_NUMBER}`, `{ROUND}`: 오케스트레이터 변수에서 직접
- `{PR_TITLE}`, `{PR_BODY}`: `gh pr view --json title,body`에서 추출
- `{DIFF}`: `gh pr diff "$PR_NUMBER" --repo "$REPO"`
- `{REVIEW_CRITERIA}`: `./review-criteria.md` (`$SKILL_ROOT/review-criteria.md`) 파일 내용
- `{REVIEW_CONTEXT}`: "리뷰 컨텍스트 구성" 섹션의 형식으로 CC가 생성
- `{DEBATE_LEDGER}`: "Debate Ledger 관리" 섹션의 형식으로 CC가 `state.debate_ledger`에서 생성

Step별 플레이스홀더 (`show --json` 출력에서 도출):

| 플레이스홀더 | 데이터 경로 | 설명 |
|---|---|---|
| `{OPEN_ISSUES}` | `issues` 중 현재 unresolved 상태인 항목 | 현재 라운드 시작 시점의 open issue 전체 목록. 직전 2개 라운드 컨텍스트 밖의 오래된 issue도 포함한다. same-repo는 `consensus_status=open` 또는 `consensus_status=accepted`이고 `application_status!=applied`, fork는 `consensus_status=open` 또는 `consensus_status=accepted`이고 `application_status!=recommended`인 항목을 포함한다. `issue_id`, `consensus_status`, `application_status`, `severity`, `file`, `line`, `anchor`, `message`를 조합한 JSON 배열로 전달 |
| `{PENDING_REBUTTALS}` | `rounds[N-1].step3.rebuttals` + `issues[*].reports[*]` | 이전 라운드 step3의 rebuttals에 원 finding의 `issue_id`, `severity`, `file`, `line`, `anchor`, `message`를 조합한 JSON 배열. Lead agent가 반박 사유와 원문 맥락을 함께 보고 판단할 수 있게 전달 |
| `{LEAD_AGENT_ID}` | `rounds[N].lead_agent` | 현재 라운드의 lead agent ID |
| `{LEAD_REPORTS}` | `rounds[N].step1.report_ids` → `issues[*].reports[*]` | report_id로 issues에서 `report_id`, `severity`, `file`, `line`, `anchor`, `message`를 조합. `report_id`를 반드시 포함하여 JSON 배열로 전달 (cross-verifier가 결정을 report_id로 반환해야 하므로) |
| `{CROSS_REBUTTALS}` | `rounds[N].step2.rebuttals` + `issues[*].reports[*]` | 현재 라운드 step2의 rebuttals에 원 finding의 `report_id`, `issue_id`, `severity`, `file`, `line`, `anchor`, `message`를 조합한 JSON 배열. Lead agent가 어떤 finding에 대한 반박인지 파악할 수 있게 전달 |
| `{CROSS_FINDINGS}` | `rounds[N].step2.report_ids` → `issues[*].reports[*]` | cross-verifier의 report_id들로 issues에서 `report_id`, `severity`, `file`, `line`, `anchor`, `message`를 조합. `report_id`를 포함하여 JSON 배열로 전달 |
| `{APPLICABLE_ISSUES}` | `issues` 중 `consensus_status=accepted` AND `application_status=pending\|failed` | 반영 대상 issue 목록. issue_id, file, line, message 포함 JSON 배열로 전달 |

---

## 빠른 참조

| 항목 | 규칙 |
|------|------|
| Lead agent | 홀수 라운드=Codex, 짝수=CC |
| 합의 조건 | 연속 2개 clean pass (서로 다른 lead agent) |
| 상태 파일 | `~/.claude/debate-state/<owner>-<repo>-<pr>.json` |
| CLI | `$DEBATE_REVIEW_BIN <subcommand>` |
| 코멘트 태그 | `[debate-review][sha:<initial_sha>]` |
| 최대 라운드 | 10 (설정 `max_rounds`) |
| Codex 샌드박스 | `read-only` (필요 시 `danger-full-access` 명시 opt-in) |
| 워크트리 | `<repo_root>/.worktrees/debate-pr-<N>` |
| GitHub CLI | `env -u GITHUB_TOKEN -u GH_TOKEN gh ...` |

## 흔한 실수

- **CLI 없이 상태 직접 조작**: 반드시 `$DEBATE_REVIEW_BIN` subcommand를 통해 상태 변경
- **Step 0 건너뛰기**: 재시작 시에도 반드시 `sync-head` 실행
- **코멘트 태그에 `post_sync_head_sha` 사용**: `initial_sha`를 써야 Step 3 commit 이후에도 안정
- **`opened_by` 기반 변경**: lead agent가 모든 합의된 issue를 수정 (opened_by 무관)
- **Codex 출력을 그대로 코멘트에 사용**: 오케스트레이터가 정규화된 형식으로 변환 필수
- **Phase 순서 무시**: Phase 1 → commit → Phase 2 → push → Phase 3 순서 엄수
- **Fork PR에서 push 시도**: fork PR은 코드 반영/commit/push 모두 건너뜀
