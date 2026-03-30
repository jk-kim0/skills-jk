# CC-Codex Debate Review: State Management CLI 설계 문서

**작성일:** 2026-03-30
**상태:** 초안

---

## 선행 문서

이 문서는 [CC-Codex Debate Review 설계 문서](./2026-03-30-cc-codex-debate-review-design.md)를 전제로 한다.

- **상태 스키마**: 설계 문서 Section 2를 그대로 승계한다.
- **라운드 흐름**: 설계 문서 Section 3의 step 정의를 코드로 구현한다.
- **이 문서가 추가하는 것**: CC↔CLI 호출 경계, subcommand 계약, 안전 옵션, resume 규칙.

설계 문서가 정의한 상태 전이 규칙, journal checkpoint 순서, consensus 판정 조건은 이 문서에서 반복하지 않는다. 구현은 설계 문서의 해당 정의를 정확히 따라야 한다.

---

## 핵심 결정: CC↔CLI 역할 분담

### 문제

설계 문서의 오케스트레이션을 단일 Python CLI로 옮기면, **짝수 라운드에서 CC가 lead agent로 직접 리뷰할 때** CLI가 CC를 다시 subprocess로 호출하는 역전 구조가 된다. CC는 이미 오케스트레이터이고, Codex를 직접 호출할 수 있고, 자기가 리뷰하는 것도 자연스럽다.

### 결정

**CLI는 상태 관리 도구이다. CC가 오케스트레이터로 남는다.**

```
CC (오케스트레이터)
  ├─ debate-review init ...          → 상태 초기화
  ├─ debate-review sync-head ...     → PR HEAD sync
  ├─ debate-review upsert-issue ...  → issue 생성/갱신
  ├─ debate-review settle-round ...  → 정산
  ├─ debate-review post-comment ...  → 최종 코멘트
  │
  ├─ codex exec ...                  → Codex 호출 (홀수 라운드 lead, 짝수 라운드 cross)
  └─ CC 자체 리뷰                     → 짝수 라운드 lead, 홀수 라운드 cross
```

CC는 라운드 루프를 돌면서 각 step에서 CLI subcommand를 호출하여 상태를 조작한다. 리뷰 자체(finding 생성, rebuttal 판단)는 CC와 Codex가 직접 수행하고, CLI는 그 결과를 상태 파일에 반영하는 역할만 한다.

### 이 결정의 함의

| 책임 | 담당 |
|------|------|
| 라운드 루프, step 순서 결정 | CC (skill 문서가 안내) |
| Codex 호출, 프롬프트 조합 | CC |
| CC 자체 리뷰 (짝수 라운드 lead) | CC |
| 상태 파일 CRUD, 스키마 검증 | CLI |
| issue upsert, issue_key 생성, consensus 계산 | CLI |
| journal checkpoint 관리 | CLI |
| PR HEAD sync (fetch, ref update, worktree reset) | CLI |
| commit/push 실행 및 검증 | CLI |
| PR comment 게시 및 중복 확인 | CLI |

skill 문서 `skills/ops/cc-codex-debate-review.md`는 "어떤 순서로 어떤 subcommand를 호출하는가"를 기술하는 얇은 운영 문서가 된다. 상태 전이의 정확성은 CLI 코드가 보장한다.

---

## 대안 검토

### 대안 1: 기존 markdown skill 중심 구조 유지

- 장점: 새 실행 파일 불필요
- 단점: 상태 전이를 자연어 지시에 의존, 테스트 불가

### 대안 2: 단일 엔트리포인트 Python CLI (오케스트레이션 포함)

- 장점: 모든 로직이 코드 안에 있음
- 단점: CC가 lead일 때 CC를 다시 호출하는 역전 구조. CC의 기존 오케스트레이터 역할과 충돌

### 대안 3: subcommand 기반 상태 관리 도구 + CC 오케스트레이터

- 장점: CC의 역할을 유지하면서 상태 관리만 코드로 이동. 각 subcommand가 독립적으로 테스트 가능
- 단점: CC가 올바른 순서로 호출해야 하므로 skill 문서의 품질에 의존

### 선택: 대안 3

CC는 이미 Codex를 호출하고, 자체 리뷰를 수행하고, 사용자와 상호작용하는 오케스트레이터다. 이 역할을 Python CLI에 넘기면 오히려 복잡해진다. CLI는 CC가 "정확하게 하기 어려운 것"(상태 계산, 스키마 검증, atomic write)만 담당하는 게 낫다.

---

## CLI 엔트리포인트

```bash
bin/debate-review <subcommand> [options]
```

모든 subcommand는 `--state-file <path>` 를 공통 옵션으로 받는다. 상태 파일 경로는 `~/.claude/debate-state/<owner>-<repo>-<pr>.json` 규칙을 따른다.

---

## Subcommand 계약

### `init`

세션 상태를 초기화한다.

```bash
bin/debate-review init \
  --repo <owner/repo> \
  --pr <number> \
  [--repo-root <path>] \
  [--config <path>] \
  [--max-rounds <number>]
```

**동작:**
1. PR 메타데이터 수집 (`headRefName`, `headRefOid`, `headRepositoryOwner`)
2. is_fork 판별
3. 기존 상태 파일 확인:
   - 없음 → 설계 문서 Section 2 스키마로 초기화
   - terminal 상태 + 같은 HEAD → 에러: "세션 이미 완료"
   - terminal 상태 + 다른 HEAD → 재초기화
   - in_progress → 기존 상태 반환 (resume)
4. 상태 파일 저장

**stdout:** 초기화된 상태 파일 경로와 세션 상태 요약 (JSON)

```json
{
  "state_file": "~/.claude/debate-state/owner-repo-123.json",
  "status": "created|resumed|already_terminal",
  "current_round": 1,
  "is_fork": false
}
```

### `sync-head`

Step 0: PR HEAD를 로컬에 동기화한다.

```bash
bin/debate-review sync-head --state-file <path>
```

**동작:**
1. 현재 PR HEAD 조회
2. `journal.pre_sync_head_sha` 기록
3. `git fetch` → synthetic local ref 갱신
4. worktree hard reset
5. 외부 변경 감지 (supersede 판정)
6. `journal.post_sync_head_sha`, `head.synced_worktree_sha` 기록

**stdout:**

```json
{
  "pre_sync_sha": "abc1234",
  "post_sync_sha": "def5678",
  "external_change": true,
  "superseded_rounds": [1, 2]
}
```

### `upsert-issue`

리뷰 결과를 상태에 반영한다. 단일 issue를 생성하거나 기존 issue에 report를 추가한다.

```bash
bin/debate-review upsert-issue \
  --state-file <path> \
  --agent <cc|codex> \
  --round <number> \
  --severity <critical|warning|suggestion> \
  --criterion <number> \
  --file <path> \
  --line <number> \
  --message <text>
```

**동작:**
1. issue_key 생성 (설계 문서 규칙: canonical-kind 또는 fallback SHA1)
2. 기존 issue_key 탐색 → 있으면 report 추가, 없으면 새 issue 생성
3. `accepted_by` 초기화/갱신
4. 상태 파일 저장

**stdout:**

```json
{
  "issue_id": "isu_003",
  "report_id": "rpt_007",
  "action": "created|appended",
  "issue_key": "criterion:5|file:src/foo.ts|anchor:retry|kind:unbounded_loop"
}
```

### `record-verdict`

Step 1 리뷰의 최종 판정을 기록한다.

```bash
bin/debate-review record-verdict \
  --state-file <path> \
  --round <number> \
  --verdict <has_findings|no_findings_mergeable>
```

**동작:**
1. `rounds[round].step1.verdict` 기록
2. `no_findings_mergeable`이고 clean pass 조건 충족 시 `rounds[round].clean_pass = true`
3. 상태 파일 저장

**stdout:**

```json
{
  "round": 3,
  "verdict": "no_findings_mergeable",
  "clean_pass": true
}
```

### `record-cross-verification`

Step 2 교차 검증 결과를 기록한다.

```bash
bin/debate-review record-cross-verification \
  --state-file <path> \
  --round <number> \
  --verifications <json>
```

`--verifications` JSON 형식:

```json
[
  {"report_id": "rpt_001", "decision": "accept", "reason": "..."},
  {"report_id": "rpt_002", "decision": "rebut", "reason": "..."}
]
```

**동작:**
1. 각 verification의 accept/rebut를 issue에 반영
2. accept → `accepted_by`에 cross-verifier 추가, consensus_status 갱신
3. rebut → `rounds[round].step2.rebuttals`에 기록
4. 상태 파일 저장

### `resolve-rebuttals`

Step 3 또는 Step 1a에서 rebuttal에 대한 lead agent의 응답을 기록한다.

```bash
bin/debate-review resolve-rebuttals \
  --state-file <path> \
  --round <number> \
  --decisions <json>
```

`--decisions` JSON 형식:

```json
[
  {"report_id": "rpt_001", "decision": "withdraw", "reason": "..."},
  {"report_id": "rpt_002", "decision": "maintain", "reason": "..."}
]
```

**동작:**
1. withdraw → report status를 `withdrawn`으로, `accepted_by` 재계산, consensus_status 갱신
2. maintain → 재보고 대상으로 표시
3. 상태 파일 저장

### `record-application`

Step 3 코드 반영 결과를 기록한다.

```bash
bin/debate-review record-application \
  --state-file <path> \
  --round <number> \
  --applied-issues <json> \
  --failed-issues <json> \
  [--commit-sha <sha>] \
  [--push-verified]
```

**동작:**
1. 각 issue의 `application_status` 갱신 (`applied`/`failed`)
2. journal checkpoint 순서대로 기록 (설계 문서 Section 3의 checkpoint 0-6)
3. 상태 파일 저장

### `settle-round`

Step 4: 라운드 정산 및 consensus 판정.

```bash
bin/debate-review settle-round --state-file <path> --round <number>
```

**동작:**
1. 직전 2개 round가 연속 clean pass인지 확인 (설계 문서 합의 정의)
2. 조건 충족 시 → `status = consensus_reached`, `final_outcome = consensus`
3. `current_round >= max_rounds` 시 → `status = max_rounds_exceeded`
4. 그 외 → `current_round` 증가, 다음 라운드 준비
5. `rounds[round].status = completed`
6. 상태 파일 저장

**stdout:**

```json
{
  "round": 3,
  "result": "continue|consensus_reached|max_rounds_exceeded",
  "next_round": 4,
  "unresolved_issue_ids": ["isu_001"],
  "recommendation_issue_ids": ["isu_002"]
}
```

### `post-comment`

최종 PR 코멘트를 게시한다.

```bash
bin/debate-review post-comment \
  --state-file <path> \
  [--no-comment]
```

**동작:**
1. 세션 상태에 따라 코멘트 템플릿 선택 (설계 문서의 4개 템플릿)
2. 기존 코멘트 중복 확인 (`final_comment_tag`)
3. `--no-comment` 시 코멘트 본문만 stdout에 출력하고 게시하지 않음
4. 게시 후 `final_comment_id` 기록
5. 상태 파일 저장

### `show`

현재 상태를 사람이 읽을 수 있는 형태로 출력한다.

```bash
bin/debate-review show --state-file <path> [--json]
```

**동작:**
- 기본: 사람이 읽기 쉬운 요약 (현재 라운드, 상태, open issues 수, 최근 step)
- `--json`: 상태 파일 전체를 그대로 출력

---

## CC 오케스트레이션 흐름에서의 사용 예시

skill 문서가 CC에게 안내할 전형적 흐름:

```bash
# 1. 초기화
STATE=$(bin/debate-review init --repo owner/repo --pr 123)
STATE_FILE=$(echo "$STATE" | jq -r .state_file)

# 2. 라운드 루프 시작
# Step 0: sync
bin/debate-review sync-head --state-file "$STATE_FILE"

# Step 1: Lead 리뷰 (홀수 라운드 → Codex 호출, 짝수 → CC 자체 리뷰)
# CC가 Codex 호출 또는 자체 리뷰 후 결과를 파싱하여:
bin/debate-review upsert-issue --state-file "$STATE_FILE" \
  --agent codex --round 1 --severity warning --criterion 5 \
  --file src/foo.ts --line 42 --message "unbounded retry"

bin/debate-review record-verdict --state-file "$STATE_FILE" \
  --round 1 --verdict has_findings

# Step 2: Cross-verification (CC가 cross-verifier 결과를 파싱하여)
bin/debate-review record-cross-verification --state-file "$STATE_FILE" \
  --round 1 --verifications '[{"report_id":"rpt_001","decision":"accept","reason":"valid"}]'

# Step 3: Lead 응답 + 코드 반영
bin/debate-review resolve-rebuttals --state-file "$STATE_FILE" \
  --round 1 --decisions '[...]'

bin/debate-review record-application --state-file "$STATE_FILE" \
  --round 1 --applied-issues '["isu_001"]' --failed-issues '[]' \
  --commit-sha abc1234 --push-verified

# Step 4: 정산
bin/debate-review settle-round --state-file "$STATE_FILE" --round 1

# 3. 종료 후 코멘트
bin/debate-review post-comment --state-file "$STATE_FILE"
```

---

## 안전 옵션

### 플래그 정의

| 플래그 | 효과 |
|--------|------|
| `--dry-run` | 읽기 작업만 수행. 상태 파일, commit, push, comment 모두 변경 없음 |
| `--no-push` | 로컬 commit은 생성하되 원격 push 생략. 상태 파일에는 push_verified=false로 기록 |
| `--no-comment` | PR comment 게시 생략. 코멘트 본문은 stdout에 출력 |

### 조합표

| 조합 | 상태 파일 갱신 | 로컬 commit | push | PR comment |
|------|:-:|:-:|:-:|:-:|
| (기본) | O | O | O | O |
| `--no-push` | O | O | X | O |
| `--no-comment` | O | O | O | X |
| `--no-push --no-comment` | O | O | X | X |
| `--dry-run` | X | X | X | X |

`--dry-run`은 `--no-push`와 `--no-comment`를 함의한다. 명시적으로 함께 줘도 에러는 아니다.

fork PR에서는 `--no-push`가 자동 적용된다 (is_fork=true이면 push 불가).

### subcommand별 적용

안전 플래그는 해당 subcommand에 전달된 경우에만 적용된다. CC(오케스트레이터)가 "이번 세션은 dry-run"이라고 판단하면, 각 subcommand 호출 시 `--dry-run`을 전달하는 방식이다.

---

## 재실행(Resume) 계약

### 사용자에게 보이는 규칙

같은 `--repo`와 `--pr`로 `init`을 다시 호출하면:

| 기존 상태 | 동작 |
|-----------|------|
| 없음 | 새 세션 생성 |
| `in_progress` | 기존 상태 반환 (resume) |
| terminal + 같은 HEAD | 에러: "세션 이미 완료" |
| terminal + 다른 HEAD | 기존 상태 아카이브 후 새 세션 생성 |

### CC의 resume 책임

CC는 `init`의 응답에서 `status`와 `current_round`를 읽고, journal의 마지막 완료 step부터 이어간다. 구체적으로:

1. `init` 호출 → `resumed` 상태 확인
2. `show --json`으로 journal 확인 → 마지막 완료 step 파악
3. 해당 step 다음부터 subcommand 호출 재개

journal이 step 중간에 멈춰 있으면 (예: commit은 했지만 push 전) 해당 step의 subcommand를 다시 호출한다. subcommand는 idempotent하게 설계되어, 이미 완료된 부분은 skip한다.

---

## 사전조건

- 대상 repo의 로컬 clone 존재
- `gh` CLI 인증 완료
- `codex` CLI 사용 가능
- Python 3.10+

CLI는 `init` 시점에 사전조건을 검증하고, 미충족 시 구체적 에러 메시지와 함께 실패한다.

---

## GitHub CLI 인증 규칙

CLI 내부의 모든 `gh` 호출은 주입된 토큰 변수를 제거하고 keyring 인증을 사용한다:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

사용자는 이를 알 필요 없다. CLI가 내부적으로 처리한다.

---

## 비범위

다음은 이 문서에서 정의하지 않는다:

- exit code 체계 (구현 plan에서 정의)
- 상태 파일 필드별 상세 mutation 알고리즘 (설계 문서 Section 2-3이 정의)
- Codex 프롬프트 템플릿 내용 (기존 `codex-*.md` 파일이 정의)
- stderr 사용 규칙 (구현에서 결정)
- 로그 레벨/verbosity 옵션 (구현에서 결정)
