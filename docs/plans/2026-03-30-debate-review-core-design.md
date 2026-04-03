# Debate Review Core Design

**작성일:** 2026-03-30
**상태:** 구조 수정 반영

---

## 문서 구성

- 이 문서는 debate-review의 canonical architecture와 상태 전이 규칙을 정의한다.
- CLI 경계와 subcommand 계약은 [2026-03-30-debate-review-cli-interface-design.md](./2026-03-30-debate-review-cli-interface-design.md)에서 다룬다.
- CLI 구현 순서는 [2026-03-30-debate-review-cli-impl.md](./2026-03-30-debate-review-cli-impl.md)에서 관리한다.
- persistent agent 확장 설계는 [2026-04-01-debate-review-persistent-agent-design.md](./2026-04-01-debate-review-persistent-agent-design.md)에서 다룬다.
- persistent rollout 및 completion workstream은 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.

## 개요

Open PR에 대해 Claude Code(CC)와 Codex 두 AI Agent가 반복적으로 리뷰, 반박, 수정 제안을 수행하고, 두 Agent가 모든 issue에 대해 동일한 결론에 도달할 때까지 토론을 반복하는 시스템.

이 문서의 핵심 설계 결정은 다음 다섯 가지입니다:

1. 라운드별 배열 인덱스 대신 **stable issue ID** 와 agent별 report instance를 사용한다.
2. **리뷰 합의(consensus)** 와 **코드 반영(application)** 을 분리한다.
3. `current_step` 하나 대신 **step journal checkpoint** 로 재시작 가능성을 정의한다.
4. worktree 최신화는 부수 규칙이 아니라 **명시적 `sync_pr_head()` 단계** 로 다룬다.
5. 라운드마다 **lead agent를 교대** 하여 리뷰→교차검증→수정의 책임을 단순화한다.

## 현재 구현 경계 (2026-04-03)

현재 저장소 기준으로 구현된 범위는 다음과 같다.

- 상태 파일 스키마와 round / issue / application 전이 로직
- `bin/debate-review` CLI subcommand 집합
- prompt 자산과 persistent mode용 `build-prompt`
- final comment 생성 / 게시
- sync / resume 판단 / 일부 timing 계측

반대로 아직 문서 절차에 머물러 있는 범위는 다음과 같다.

- round loop, agent lifecycle, terminal follow-through를 재현 가능하게 실행하는 orchestration path
- persistent agent create / resume / recovery의 런타임 자동화
- failure 이후 bug report 생성
- terminal 시 PR title/body 갱신
- worktree cleanup

현재 열린 운영 blocker와 completion backlog의 canonical 목록은 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다. 즉, 이 문서의 설계는 여전히 유효하지만 현재 구현물은 "완성된 debate-review 시스템"이 아니라 "상태 엔진 + prompt assets + 운영 절차 문서"에 가깝다.

---

## Section 1: 아키텍처 개요

### 핵심 개념

- **Issue**: 실제 코드/문서 상의 하나의 논점. 여러 Agent가 같은 issue를 독립적으로 보고할 수 있다.
- **Report instance**: 특정 Agent가 특정 라운드에서 issue를 보고한 1회 기록
- **Lead agent**: 해당 라운드에서 리뷰, 응답, 코드 반영 책임을 가진 Agent. 홀수 라운드는 Codex, 짝수 라운드는 CC.
- **Consensus status**: 해당 issue의 타당성에 대해 두 Agent가 합의했는지 여부
- **Application status**: 동일 저장소 PR에서 해당 issue에 대한 코드 반영이 실제로 적용되었는지 여부
- **Recommendation**: 포크 PR에서 push할 수 없어 코드 반영 대신 최종 코멘트로 남기는 권장 수정 항목

### 상위 흐름

```
초기화
  ├─ 사전 조건 확인: 로컬 클론 존재 여부
  ├─ PR 메타데이터 수집: headRefName, headRefOid, headRepositoryOwner
  ├─ target_ref 결정
  │   └─ same-repo / fork 구분 없이 refs/debate-sync/pr-<number>/head 사용
  ├─ 상태 파일 로드 또는 초기화
  └─ Round 1 시작

라운드 루프 (최대 10라운드, lead agent 교대)
  ├─ 홀수 라운드: lead=Codex, cross=CC
  ├─ 짝수 라운드: lead=CC, cross=Codex
  │
  ├─ Step 0: sync_pr_head()
  │          → pre-sync PR HEAD snapshot 기록
  │          → 최신 PR HEAD를 synthetic local ref로 fetch
  │          → worktree를 target_ref로 hard reset
  │
  ├─ Step 1: Lead agent 리뷰
  │   ├─ 1a: 이전 round에서 자신의 report에 대한 미결 rebuttal 처리
  │   │      → 수용 시 report withdrawn, 거부 시 재보고 필수
  │   └─ 1b: PR 리뷰 + raw reports 생성
  │          → stable issue ID로 upsert
  │          → finding 없고 병합 가능 판정 시 → clean pass
  │          → clean pass면 Step 2/3 건너뛰고 Step 4로
  │
  ├─ Step 2: Cross-verifier 평가 (clean pass 시 생략)
  │          → lead agent의 reports를 accept/rebut
  │          → cross-verifier 자신의 새 findings도 보고
  │
  ├─ Step 3: Lead agent 응답 + 코드 반영 (clean pass 시 생략)
  │          → rebuttals 수용/거부 결정
  │          → cross-verifier의 새 findings accept/rebut
  │          → same-repo: accepted issue 코드 반영
  │
  └─ Step 4: 정산
             ├─ 직전 2개 round가 연속 clean pass인가?
             │   (교대 구조상 서로 다른 lead agent)
             ├─ 조건 충족 시 consensus_reached
             └─ 미충족 시 다음 라운드
```

### 역할 분담

- CC: 오케스트레이터, 상태 파일 관리자. 짝수 라운드의 lead agent(리뷰어 + 수정자), 홀수 라운드의 cross-verifier.
- Codex: `codex exec -s danger-full-access` 로 호출되는 서브프로세스. 홀수 라운드의 lead agent(리뷰어 + 수정자), 짝수 라운드의 cross-verifier.

### Lead agent 교대 규칙

| 라운드 | Lead agent | Cross-verifier |
|--------|-----------|----------------|
| 1, 3, 5, ... (홀수) | Codex | CC |
| 2, 4, 6, ... (짝수) | CC | Codex |

### 합의 정의

두 Agent가 각각 lead agent 역할로 PR을 리뷰했을 때, **둘 다 finding 없이 병합 가능하다고 판정**하면 합의에 도달한 것으로 간주한다.

구체적으로: **직전 2개 round가 연속으로 clean pass** 이면 합의 성립. 교대 구조상 이 2개 round의 lead agent는 반드시 서로 다르므로, 양쪽 Agent 모두의 "병합 가능" 판정이 보장된다.

**clean pass 조건:**
- Lead agent의 Step 1 리뷰에서 새 finding이 없다.
- 기존 issue 중 `consensus_status=open` 인 것이 없다.
- same-repo PR: `consensus_status=accepted` 인 모든 issue가 `application_status=applied` 이다.
- 위 조건을 모두 충족하면 lead agent가 "병합 가능"으로 판정한다.

**포크 PR 해석:**
- `consensus_status=accepted` 이고 `application_status=recommended` 인 issue는 **권장 수정 항목** 으로 간주한다.
- 포크 PR에서의 합의는 "PR 코드가 자동 수정되었다"가 아니라 "두 Agent가 같은 권장 수정안에 도달했다"는 의미다.

---

## Section 2: 상태 파일 스키마

상태 파일 경로: `~/.claude/debate-state/<owner>-<repo>-<pr>.json`

### 최상위 스키마

```json
{
  "repo": "owner/repo",
  "repo_root": "/Users/jk/workspace/repo",
  "pr_number": 123,
  "is_fork": false,
  "status": "in_progress",
  "current_round": 1,
  "head": {
    "initial_sha": "abc1234",
    "last_observed_pr_sha": "abc1234",
    "terminal_sha": null,
    "pr_branch_name": "feat/some-feature",
    "target_ref": "refs/debate-sync/pr-123/head",
    "synced_worktree_sha": "abc1234"
  },
  "journal": {
    "round": 1,
    "step": "step3_lead_apply",
    "pre_sync_head_sha": "abc1234",
    "post_sync_head_sha": "def5678",
    "synced_worktree_sha": "abc1234",
    "applied_issue_ids": [],
    "failed_application_issue_ids": [],
    "commit_sha": null,
    "push_verified": false,
    "state_persisted": true
  },
  "issues": {
    "isu_001": {
      "id": "isu_001",
      "issue_key": "criterion:5|file:src/foo.ts|anchor:retryWithExponentialBackoff|kind:unbounded_loop",
      "opened_by": "codex",
      "introduced_in_round": 1,
      "severity": "warning",
      "criterion": 5,
      "file": "src/foo.ts",
      "line": 42,
      "message": "...",
      "reports": [
        {
          "report_id": "rpt_001",
          "agent": "codex",
          "round": 1,
          "file": "src/foo.ts",
          "line": 42,
          "message": "...",
          "status": "open"
        }
      ],
      "consensus_status": "open",
      "consensus_reason": null,
      "accepted_by": ["codex"],
      "application_status": "pending",
      "applied_by": null,
      "application_commit_sha": null
    }
  },
  "rounds": [
    {
      "round": 1,
      "status": "active",
      "lead_agent": "codex",
      "synced_head_sha": "abc1234",
      "clean_pass": false,
      "step1": {
        "rebuttal_responses": [],
        "report_ids": ["rpt_001"],
        "issue_ids_touched": ["isu_001"],
        "verdict": "has_findings"
      },
      "step2": {
        "report_ids": [],
        "issue_ids_touched": [],
        "accepted_report_ids": [],
        "rebuttals": [
          { "report_id": "rpt_001", "issue_id": "isu_001", "reason": "..." }
        ]
      },
      "step3": {
        "withdrawn_report_ids": [],
        "accepted_report_ids": [],
        "rebuttals": [],
        "applied_issue_ids": [],
        "failed_application_issue_ids": [],
        "commit_sha": null,
        "push_verified": false
      },
      "step4": {
        "unresolved_issue_ids": ["isu_001"],
        "recommendation_issue_ids": [],
        "result": "continue"
      }
    }
  ],
  "final_comment_tag": null,
  "final_comment_id": null,
  "started_at": "2026-03-30T10:00:00+09:00",
  "finished_at": null,
  "final_outcome": null
}
```

### `status` 값

| 값 | 의미 |
|----|------|
| `in_progress` | 진행 중 |
| `consensus_reached` | 최종 합의 후 종료 |
| `max_rounds_exceeded` | 10라운드 내 합의 실패 |
| `failed` | 복구 불가 오류 |

### `final_outcome` 값

| 값 | 의미 |
|----|------|
| `consensus` | 합의 성공 |
| `no_consensus` | 10라운드 후 미합의 |
| `error` | 오류 종료 |

### `issue` 필드 의미

- `id`: 상태 파일 내부에서 사용하는 stable issue ID
- `issue_key`: cross-round, cross-agent dedupe를 위한 canonical key. `agent` 를 포함하지 않는다.
- `opened_by`: issue를 처음 제기한 agent. 이력 추적용이며, 코드 반영 책임(mutation owner)은 해당 round의 lead agent가 진다.
- `reports`: 같은 issue를 누가 언제 어떤 문구로 제기했는지 저장하는 report instance 배열
- `reports[].status`: report instance 상태. `open` 또는 `withdrawn`.
- `consensus_status`:
  - `open`: 아직 반대 Agent와 결론이 맞지 않음
  - `accepted`: 두 Agent가 issue 타당성에 동의함
  - `withdrawn`: 제기된 report들이 rebuttal을 통해 철회됨
- `accepted_by`: issue를 타당하다고 판단한 agent들의 집합. issue를 **직접 보고한 agent는 해당 issue를 타당하다고 본 것** 으로 간주하므로, 새 issue 생성 시 제기한 agent 하나로 초기화한다. 가능한 값은 `["cc"]`, `["codex"]`, `["cc","codex"]`.
- `application_status`:
  - `pending`: same-repo PR에서 아직 코드 반영 전
  - `applied`: 코드 반영 및 push 검증 완료
  - `failed`: 코드 반영 시도했으나 실패
  - `recommended`: fork PR이라 recommendation으로만 남음
  - `not_applicable`: withdrawn issue 등 코드 반영 대상이 아님

### `head` 필드 의미

- `initial_sha`: debate-review가 처음 시작된 시점의 PR HEAD SHA. 코멘트 태그(`[debate-review][sha:<initial_sha>]`)의 불변 식별자로 사용한다.
- `last_observed_pr_sha`: 가장 최근 Step 0에서 관측한 PR HEAD SHA.
- `terminal_sha`: 세션이 terminal 상태에 도달했을 때의 PR HEAD SHA. 세션 진행 중에는 `null`. same-repo PR에서는 Step 3 커밋으로 PR HEAD가 `initial_sha`와 달라지므로, 재실행 시 세션 동일성 판정에 `initial_sha` 대신 이 값을 사용한다.
- `pr_branch_name`: PR의 head branch 이름 (`headRefName`). same-repo PR에서 코드 반영 시 push 대상 브랜치로 사용한다.
- `target_ref`: Step 0이 fetch한 synthetic local ref.
- `synced_worktree_sha`: worktree가 마지막으로 hard reset된 SHA.

### 최종 코멘트 관련 필드

- `final_comment_tag`: 게시된 최종 코멘트 식별 태그. 형식: `[debate-review][sha:<initial_sha>]`. `initial_sha` 를 쓰는 이유: same-repo PR에서 Step 3 커밋이 PR HEAD를 바꾸므로 `post_sync_head_sha` 는 라운드마다 달라지지만, `initial_sha` 는 세션 전체에서 불변이다. 게시 전에는 `null`.
- `final_comment_id`: GitHub PR comment ID. 코멘트 게시 후 검증 완료 시 기록. 재시작 시 중복 게시 방지에 사용.

### `rounds[].status` 값

| 값 | 의미 |
|----|------|
| `active` | 현재 유효한 round |
| `completed` | 정산까지 끝난 round |
| `superseded` | 외부 변경으로 더 이상 기준 round로 쓰지 않는 round |

### `journal` 필드 의미

`journal` 은 "지금 어디까지 외부 부작용이 완료되었는가"를 기록한다.

- `step`: 현재 진행 또는 마지막 완료 step
- `pre_sync_head_sha`: 이번 sync 전에 관측된 PR HEAD SHA
- `post_sync_head_sha`: 이번 sync 후 target ref가 가리키는 PR HEAD SHA
- `synced_worktree_sha`: worktree가 실제로 reset된 SHA
- `applied_issue_ids`: Step 3에서 코드 반영에 성공한 issue ID 목록. commit 생성 전에 기록한다.
- `failed_application_issue_ids`: Step 3에서 코드 반영에 실패한 issue ID 목록. commit 생성 전에 기록한다.
- `commit_sha`: `journal.step` 이 가리키는 **현재 mutation step (step3_lead_apply)** 이 생성한 로컬 commit SHA
- `push_verified`: PR HEAD가 `journal.commit_sha` 와 일치함을 확인했는지 여부
- `state_persisted`: 위 결과가 상태 파일까지 기록되었는지 여부

핵심 원칙:
- commit/push 성공과 state write 성공은 별도 checkpoint다.
- 재시작 시 Step 0이 `pre_sync_head_sha` 와 `post_sync_head_sha` 를 모두 남기므로, 이전에 보던 HEAD와 새로 fetch한 HEAD를 구분할 수 있다.
- 재시작 시 commit subject 문자열이 아니라 `journal.commit_sha` 와 PR HEAD 비교로 판단한다.
- `rounds[N].step3.commit_sha` 는 이력 보존용이며, `journal.commit_sha` 는 현재 실행 중인 mutation step의 재시작 checkpoint로만 사용한다.

---

## Completion Notes

이 문서는 canonical architecture를 정의한다. 구현 완료 여부와 운영 backlog의 source of truth는 [2026-04-01-debate-review-persistent-agent-impl.md](./2026-04-01-debate-review-persistent-agent-impl.md)에서 관리한다.

### 1. Persistent mode must be the truth path

기본 모드가 `persistent`인 이상, 새 기능 계약은 persistent step prompt / state routing / restart path에 먼저 반영되어야 한다.

대표 예시:

- duplicate issue withdrawal
- prompt output schema 변경
- Step 3 code application 계약

### 2. Step 3 must be operationally safe

same-repo PR에서는 Step 3이 실제로 브랜치를 변경한다. 따라서 아래 hardening이 필요하다.

- phase1 / phase2 / phase3 resume 보장
- push verification 실패 시 재개 전략

### 3. Terminal operations must be automated

설계상 terminal processing은 단순한 `status` 종료가 아니다.

- final comment 게시
- bug report 작성
- PR metadata 정리
- worktree cleanup

이 중 일부가 문서 절차로만 남아 있으면, 설계는 구현됐다고 볼 수 없다.

### 4. E2E verification must exist

unit test만으로는 이 설계의 가장 중요한 속성을 증명할 수 없다.

필수 시나리오:

- clean pass -> consensus
- accepted issues -> code apply -> push verify
- fork PR recommendation path
- supersede by external push
- persistent resume / recovery
- terminal comment dedupe

---

## Section 3: 라운드 흐름 상세

### Step 0: `sync_pr_head()`

모든 라운드 시작과 모든 재시작 시 가장 먼저 실행한다.

#### 목적

- PR 최신 HEAD를 기준으로 worktree를 정렬한다.
- stale worktree 문제를 제거한다.
- 이후 step이 참조할 `target_ref`, `post_sync_head_sha`, `synced_worktree_sha` 를 고정한다.
- 재시작 시 비교에 쓸 `pre_sync_head_sha` 와 `post_sync_head_sha` 를 분리해 저장한다.

#### 동작

1. 상태 파일에 남아 있는 마지막 PR HEAD를 `journal.pre_sync_head_sha` 로 복사
2. PR 메타데이터 조회
3. `is_fork` 판별
4. synthetic local ref `refs/debate-sync/pr-<number>/head` 로 최신 PR HEAD fetch
5. worktree 생성 또는 재사용
6. worktree를 synthetic ref로 `reset --hard`
7. `head.last_observed_pr_sha`, `head.target_ref`, `head.synced_worktree_sha`, `journal.post_sync_head_sha`, `journal.synced_worktree_sha` 갱신

#### 예시 명령

```bash
# PR 메타데이터
env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> \
  --json headRefName,headRefOid,headRepositoryOwner

# same-repo / fork 공통: 최신 PR HEAD를 synthetic local ref로 fetch
git -C <repo_root> fetch origin \
  pull/<number>/head:refs/debate-sync/pr-<number>/head

# worktree는 PR 브랜치명을 직접 checkout하지 않고 detached worktree로 생성
if [ ! -d "<repo_root>/.worktrees/debate-pr-<number>" ]; then
  git -C <repo_root> worktree add \
    --detach \
    .worktrees/debate-pr-<number> \
    refs/debate-sync/pr-<number>/head
fi
git -C <repo_root>/.worktrees/debate-pr-<number> \
  reset --hard refs/debate-sync/pr-<number>/head
```

### Lead agent 결정

`current_round` 가 홀수이면 `lead_agent=codex`, 짝수이면 `lead_agent=cc`. 이하 문서에서 **L** 은 lead agent, **X** 는 cross-verifier를 가리킨다.

### 리뷰 컨텍스트 구성

Step 1과 Step 2에서 agent에게 리뷰를 요청할 때, 오케스트레이터는 **직전 2개 round의 리뷰 경과**를 context로 함께 전달한다. Round 1에서는 이전 경과가 없으므로 생략한다.

#### 포함 범위

`max(1, current_round - 2)` 부터 `current_round - 1` 까지의 completed/superseded round를 대상으로 한다.

#### 구성 항목

각 round별로 아래 항목을 시간순으로 정리한다:

1. **Round 메타데이터**: round 번호, lead agent, status (`completed`/`superseded`), `clean_pass` 여부
2. **Step 1 결과**: lead agent가 보고한 findings 요약 (issue ID, severity, file, message). clean pass면 "No findings — mergeable" 로 요약.
3. **Step 2 결과** (clean pass가 아닌 경우):
   - cross-verifier의 accept/rebut 판정 (report ID별)
   - cross-verifier가 새로 보고한 findings
4. **Step 3 결과** (clean pass가 아닌 경우):
   - lead agent의 rebuttal 수용/거부 결정
   - lead agent의 cross-verifier findings accept/rebut 판정
   - 코드 반영 결과 (`applied_issue_ids`, `failed_application_issue_ids`)
5. **미해결 issue 현황**: 해당 round 종료 시점의 unresolved issue 목록. Step 4의 unresolved 정의와 동일한 기준을 사용한다:
   - `consensus_status = open`
   - same-repo PR: `consensus_status = accepted` 이고 `application_status ≠ applied`
   - fork PR: 해당 없음 (fork에서는 `accepted` + `recommended`가 정상 종결)

#### 전달 형식

```text
## Review Context (Round <N-2> ~ <N-1>)

### Round <N-2> [lead: <agent>, status: <status>, clean_pass: <bool>]

**Step 1 (<agent> review):**
- isu_001 (warning) src/foo.ts:42 — Unbounded retry loop
- isu_002 (suggestion) src/bar.ts:10 — Duplicated error mapping

**Step 2 (<agent> cross-verification):**
- rpt_001 (isu_001): accepted
- rpt_002 (isu_002): rebutted — "Intentional duplication for readability"
- New finding: isu_003 (warning) src/baz.ts:5 — Missing null check

**Step 3 (<agent> response + apply):**
- Rebuttal on rpt_002: accepted → isu_002 withdrawn
- rpt_003 (isu_003): accepted
- Applied: isu_001, isu_003

**Unresolved issues after round <N-2>:** (none)

### Round <N-1> [lead: <agent>, status: <status>, clean_pass: true]

**Step 1 (<agent> review):**
No findings — mergeable

---
```

#### 생성 책임

컨텍스트 구성은 **오케스트레이터(CC)** 가 상태 파일의 `rounds[]` 와 `issues` 데이터로부터 생성한다. Agent의 원시 출력을 그대로 전달하지 않고, 정규화된 issue ID와 consensus/application 상태를 기준으로 요약한다.

#### 용도별 차이

- **Step 1 (L에게 전달):** L이 이전 라운드에서 어떤 issue가 제기·해결·철회되었는지 파악한다. 특히 직전 round의 `step3.rebuttals` 중 L 자신의 report에 대한 rebuttal이 있으면, Step 1a에서 수용/거부를 결정하는 데 사용한다.
- **Step 2 (X에게 전달):** X가 L의 이번 round findings와 이전 경과를 함께 보고, 이미 논의된 issue에 대한 맥락 있는 accept/rebut 판정을 내린다.

### Step 1: Lead agent 리뷰

Step 1은 두 단계로 구성된다: **(a) 미결 rebuttal 처리**, **(b) 새 리뷰**.

#### Step 1a: 미결 rebuttal 처리

이전 round에서 L이 cross-verifier 역할로 보고한 finding에 대해, 당시 lead agent가 rebuttal을 보냈을 수 있다. 이 rebuttal들은 `rounds[N-1].step3.rebuttals` 에 기록되어 있으며, L에게 전달되는 리뷰 컨텍스트에 포함된다.

L은 자신의 과거 report에 대한 각 rebuttal을 검토하고, report별로 반드시 아래 중 하나를 선택한다:

- **수용 (withdraw):** rebuttal이 타당하다고 판단
  - 해당 `report_id` 의 `status = withdrawn`
  - 해당 issue에 대해 **열린 report 기준으로 issue-level 파생 상태를 즉시 재계산**한다:
    - `accepted_by` = 현재 `status=open` 인 report를 가진 agent 집합
    - 열린 report가 더 이상 없으면:
      - `consensus_status = withdrawn`
      - `consensus_reason = rebuttal reason`
      - `accepted_by = []`
      - `application_status = not_applicable`
    - 열린 report가 남아 있지만 `accepted_by` 가 `["cc","codex"]` 가 아니면:
      - `consensus_status = open`
      - `consensus_reason = null`
      - `application_status` 는 기존 값 유지 (`pending|failed|recommended`)
- **거부 (maintain):** 자신의 finding을 유지
  - 해당 issue를 이번 round에서 **재보고** 해야 한다 (Step 1b에서 raw report에 포함)
  - 재보고하지 않으면 이 issue는 다음 round에도 open으로 남아 clean pass를 차단하므로, 유지 결정 시 반드시 재보고한다

이전 round가 없거나 `rounds[N-1].step3.rebuttals` 가 비어 있으면 이 단계를 건너뛴다.

#### Step 1a 기록

- `rounds[N].step1.rebuttal_responses`: L이 처리한 rebuttal 결과 목록

```json
[
  { "report_id": "rpt_003", "issue_id": "isu_005", "decision": "withdraw" },
  { "report_id": "rpt_004", "issue_id": "isu_006", "decision": "maintain" }
]
```

#### Step 1b: 새 리뷰

L은 PR 최신 상태(title, body, commits, diff, 가이드 문서)와 **리뷰 컨텍스트**(직전 2개 round 경과)를 읽고 raw reports를 생성한다. Step 1a에서 `maintain` 결정한 issue는 이 단계에서 재보고에 포함한다.

출력 형식:

```json
[
  {
    "severity": "critical|warning|suggestion",
    "criterion": 1,
    "file": "src/foo.ts",
    "line": 42,
    "message": "..."
  }
]
```

오케스트레이터는 이 raw report들을 `issue_key` 로 정규화하고 다음 규칙으로 `issues` 에 upsert 한다.

- `issue_key` 는 **오케스트레이터(CC)가 생성** 한다. Agent가 semantic slug를 자유 형식으로 만들지 않는다. 두 Agent의 raw report가 같은 논리적 issue를 가리키는 경우, 오케스트레이터가 동일한 `criterion` 번호와 `kind` 를 부여하여 하나의 `issue_key` 로 통합할 책임이 있다.
- 기본 형식은 `criterion:<N>|file:<repo-relative-path>|anchor:<stable-anchor>|kind:<canonical-kind>` 이다.
- `stable-anchor` 는 심볼명, 함수명, heading, config key, test name처럼 라인 이동에 덜 민감한 식별자를 우선 사용한다. 없으면 `line<N>` 형식으로 라인 번호를 anchor 값으로 사용한다 (예: `anchor:line42`).
- `canonical-kind` 는 아래 어휘 테이블에서 선택한다.

| canonical-kind | 설명 |
|---|---|
| `missing_validation` | 입력값 검증 누락 |
| `missing_error_handling` | 에러 처리 누락 |
| `unbounded_loop` | 종료 조건 없는 루프/재시도 |
| `wrong_target_ref` | 잘못된 참조 대상 |
| `stale_state_transition` | 잘못된 상태 전이 순서 |
| `unused_variable` | 선언 후 미사용 변수/필드 |
| `hardcoded_value` | 하드코딩된 값 |
| `duplicate_logic` | 중복 코드/로직 |
| `security_injection` | SQL/command/XSS 등 인젝션 취약점 |
| `race_condition` | 동시성 문제 |
| `resource_leak` | 파일/연결 등 리소스 미해제 |
| `wrong_scope` | 과도하거나 부족한 접근 범위 |
| `incorrect_algorithm` | 로직/알고리즘 오류 |
| `missing_test` | 테스트 누락 |
| `doc_mismatch` | 문서와 구현 불일치 |

- 위 어휘로 분류할 수 없으면 fallback 형식 `criterion:<N>|file:<repo-relative-path>|anchor:<stable-anchor>|msg:<sha1(normalize(message))[:12]>` 를 사용한다.
  - `normalize(message)`: 소문자 변환 → 연속 공백·특수문자 제거 → 라인 번호·파일 경로 언급 제거
- 같은 `issue_key` 가 이미 있으면 기존 issue ID 재사용
- 없으면 새 issue ID 발급
- 매 raw report마다 별도 `report_id` 를 발급해 `reports[]` 에 추가
- `issue_key` 는 `agent` 를 포함하지 않는다
- 기존 issue에 **새 raw report를 추가한 agent는 그 round에서 해당 issue를 여전히 타당하다고 본 것** 으로 간주하고, `accepted_by` 집합에 그 agent를 추가한다.
- **withdrawn issue reopen 규칙:** 기존 issue의 `consensus_status = withdrawn` 인 상태에서 새 report가 추가되면, 해당 issue를 재개한다:
  - `consensus_status = open`
  - `application_status = pending`
  - `consensus_reason = null`
  - `accepted_by = [<reporting_agent>]` (새 report를 제출한 agent 하나로 재초기화)
  - 이전 round에서의 철회 사유와 무관하게, 새 report는 새로운 코드 맥락에서의 발견으로 취급한다.
- **applied issue re-discovery 규칙:** 기존 issue의 `application_status = applied` 인 상태에서 새 report가 추가되면, 이전 수정이 불충분하다는 새로운 주장이므로 현재 round에서 재합의를 거쳐야 한다:
  - `consensus_status = open`
  - `accepted_by = [<reporting_agent>]` (재발견한 agent 하나로 재초기화)
  - `application_status = pending`
  - `applied_by = null`
  - `application_commit_sha = null`
  - 과거 합의(`accepted`)를 유지하면, 현재 round의 cross-verifier가 rebut해도 Step 3 apply 조건에 걸려 재적용되는 문제가 있다. `open`으로 리셋하여 현재 round의 교차검증(Step 2 accept)을 거친 후에만 재적용이 가능하게 한다.
- 새 issue 생성 시 `opened_by` 는 issue를 처음 제기한 agent로 고정한다
- 새 issue 생성 시 `accepted_by` 는 issue를 처음 제기한 agent 하나로 초기화한다
- 새 issue 생성 시 `application_status=pending` 으로 초기화한다

#### Clean pass 판정

Step 1에서 L이 새 finding을 하나도 생성하지 않았고, 아래 조건을 모두 충족하면 **clean pass** 로 판정한다:

- 기존 issue 중 `consensus_status = open` 인 것이 없다.
- same-repo PR: `consensus_status=accepted` 인 모든 issue가 `application_status=applied` 이다.
- fork PR: `consensus_status=accepted` 인 모든 issue가 `application_status=recommended` 이다.

clean pass 시:
- `rounds[N].clean_pass = true`
- `rounds[N].step1.verdict = "no_findings_mergeable"`
- Step 2/3을 건너뛰고 Step 4로 진행

#### Step 1 기록

- `rounds[N].step1.rebuttal_responses` 기록 (Step 1a 결과)
- `rounds[N].step1.report_ids` 기록 (Step 1b에서 L이 생성한 report ID 목록)
- `rounds[N].step1.issue_ids_touched` 기록 (L이 이번 round에 직접 보고한 issue ID)
- `rounds[N].step1.verdict`:
  - finding이 있거나 Step 1a에서 `maintain` 결정이 있으면 `"has_findings"`
  - 그 외 clean pass 조건 충족 시 `"no_findings_mergeable"`
- `journal.step = step1_lead_review`
- `journal.state_persisted = true`

### PR metadata mutation 정책

이 설계 버전에서는 PR title/description 은 자동 수정하지 않는다. 자동 mutation 범위는 same-repo PR의 코드 변경, commit/push, 최종 PR comment 게시로 제한한다.

### Step 2: Cross-verifier 평가

clean pass가 아닌 경우에만 실행한다. X에게는 L의 이번 round Step 1 결과와 함께 **리뷰 컨텍스트**(직전 2개 round 경과)를 전달한다.

X는 두 가지를 수행한다:

1. **L의 reports 교차검증:** Step 1의 `report_ids` 각각에 대해 반드시 아래 중 하나를 선택한다.
   - `accept`: issue가 타당함
   - `rebut`: issue가 부정확하거나 과도함

2. **X 자신의 새 findings 보고:** X도 독립적으로 PR을 리뷰하고 자신의 raw reports를 생성할 수 있다. upsert 규칙은 Step 1과 동일하다.

교차검증에서 같은 issue를 독립적으로 다시 보고하는 것은 **issue-level support** 로 간주하지만, 그것만으로 L의 개별 report instance가 `accepted_report_ids` 에 자동 기록되지는 않는다. 교차검증은 **항상 명시적으로** 수행해야 한다.

#### 기록 규칙

- `accept`:
  - `rounds[N].step2.accepted_report_ids` 에 `report_id` 추가
  - 해당 report가 가리키는 issue의 `accepted_by` 집합에 X의 agent ID 추가
  - `accepted_by` 집합에 `cc` 와 `codex` 가 모두 있으면 issue의 `consensus_status = accepted`
  - same-repo PR이면 `application_status` 는 유지(`pending`)
  - fork PR이면 `application_status = recommended`
- `rebut`:
  - `rounds[N].step2.rebuttals` 에 `{ report_id, issue_id, reason }` 기록

#### Step 2 기록

- `rounds[N].step2.report_ids` 기록 (X가 새로 생성한 report ID 목록)
- `rounds[N].step2.issue_ids_touched` 기록. 아래 두 출처의 합집합:
  1. X가 이번 round에 **직접 보고한** issue ID
  2. X가 L의 report를 **accept** 한 issue ID
  - rebut만 한 issue는 포함하지 않는다
- `journal.step = step2_cross_review`
- `journal.state_persisted = true`

### Step 3: Lead agent 응답 + 코드 반영

clean pass가 아닌 경우에만 실행한다.

L은 세 가지를 처리한다:

1. **Rebuttal 처리:** Step 2에서 X가 보낸 rebuttals를 검토해 자신의 report를 철회할지 결정
2. **X의 새 findings 평가:** Step 2에서 X가 새로 보고한 reports를 accept/rebut
3. **코드 반영:** same-repo PR에서 accepted issue 수정

#### rebuttal 수용

L이 rebuttal을 수용하면:

- 해당 `report_id` 의 `status = withdrawn`
- 해당 issue에 대해 **열린 report 기준으로 issue-level 파생 상태를 즉시 재계산**한다:
  - `accepted_by` = 현재 `status=open` 인 report를 가진 agent 집합
  - 열린 report가 더 이상 남아 있지 않으면:
    - `consensus_status = withdrawn`
    - `consensus_reason = rebuttal reason`
    - `accepted_by = []` (합의가 아닌 철회이므로 초기화)
    - `application_status = not_applicable`
  - 열린 report가 남아 있지만 `accepted_by` 가 `["cc","codex"]` 가 아니면:
    - `consensus_status = open`
    - `consensus_reason = null`
    - `application_status` 는 기존 값 유지 (`pending|failed|recommended`)

#### X의 새 findings accept/rebut

L이 X의 report를 accept 하면:

- 해당 report가 가리키는 issue의 `accepted_by` 집합에 L의 agent ID 추가
- `accepted_by` 집합에 `cc` 와 `codex` 가 모두 있으면 `consensus_status = accepted`
- same-repo PR이면 `application_status` 유지(`pending`)
- fork PR이면 `application_status = recommended`

L이 X의 report를 rebut 하면:

- `rounds[N].step3.rebuttals` 에 `{ report_id, issue_id, reason }` 기록
- 이 rebuttal은 다음 round에서 X가 lead agent로서 수용 여부를 결정한다.

#### same-repo PR의 코드 반영

L이 실제로 수정하는 대상은 아래 조건을 모두 만족하는 issue:

1. `consensus_status = accepted` (`accepted_by` 에 `cc` 와 `codex` 모두 포함)
2. `application_status = pending | failed`

`opened_by` 와 무관하게, 해당 round의 **lead agent가 모든 accepted issue를 수정**한다. 이전 설계의 `opened_by` 기반 mutation ownership을 제거하고, round 단위 책임으로 단순화한다.

supersede 후 stale issue 방지: supersede 시 `consensus_status=accepted` 가 `open` 으로 재설정되므로, 조건 1이 자연스럽게 stale issue를 걸러낸다.

성공 시:

- `application_status = applied`
- `applied_by = <lead_agent>`
- `application_commit_sha = <commit_sha>`

실패 시:

- `application_status = failed`

포크 PR에서는 코드 수정, commit, push를 모두 건너뛴다.

#### Step 3 기록

- `rounds[N].step3.withdrawn_report_ids` 기록
- `rounds[N].step3.accepted_report_ids` 기록
- `rounds[N].step3.rebuttals` 기록
- `rounds[N].step3.applied_issue_ids` 기록
- `rounds[N].step3.failed_application_issue_ids` 기록

#### Step 3 checkpoint

same-repo PR에서 mutation이 일어나면 아래 순서로 checkpoint를 남긴다.

0. Step 3 시작 직전에 `journal.step=step3_lead_apply`, `journal.applied_issue_ids=[]`, `journal.failed_application_issue_ids=[]`, `journal.commit_sha=null`, `journal.push_verified=false` 로 초기화
1. 코드 반영 시도 후 `journal.applied_issue_ids`, `journal.failed_application_issue_ids` 기록 (commit 생성 전)
2. `commit_sha`
3. `push_verified`
4. `state_persisted`

issue-level 결과를 commit 전에 journal에 기록하므로, push 성공 후 state write가 실패해도 재시작 시 journal만으로 `rounds[N].step3.applied_issue_ids` 와 issue별 `application_status` 를 결정적으로 backfill할 수 있다.

push 검증은 반드시 PR HEAD와 `journal.commit_sha` 비교로 수행한다.

### Step 4: 정산

#### 종료 조건

**연속 clean pass 확인:**

직전 2개의 completed round가 **모두 `clean_pass=true`** 이면 `consensus_reached`. 교대 구조상 이 2개 round의 `lead_agent` 는 반드시 서로 다르므로, 양쪽 Agent 모두의 "병합 가능" 판정이 보장된다.

**finding이 있었던 round의 정산:**

Step 1에서 finding이 있었던 round(`clean_pass=false`)의 경우:

- 이번 round에서 모든 issue가 해결되었더라도 `consensus_reached` 로 간주하지 않는다.
- 수정이 새로운 문제를 도입했을 수 있으므로, 다음 round에서 상대 Agent가 lead로서 검증해야 한다.
- `round < 10` 이면 다음 라운드.
- `round = 10` 이면 `max_rounds_exceeded`.

#### unresolved / recommendation 계산

Step 4에서 `unresolved_issue_ids` 와 `recommendation_issue_ids` 를 아래 기준으로 계산한다.

**same-repo PR의 unresolved:**

아래 중 하나라도 해당하면 unresolved:

- `consensus_status = open`
- `consensus_status = accepted` 이고 `application_status ≠ applied`

**fork PR의 unresolved:**

- `consensus_status = open`

**fork PR의 recommendation:**

- `consensus_status = accepted` 이고 `application_status = recommended`

**공통:** `consensus_status = withdrawn` 인 issue는 unresolved에도 recommendation에도 포함하지 않는다.

#### Step 4 기록

```json
{
  "unresolved_issue_ids": ["isu_001"],
  "recommendation_issue_ids": [],
  "result": "continue"
}
```

`result` 값: `continue`, `consensus_reached`, `max_rounds_exceeded`

Step 4 정산이 끝난 round는 `rounds[N].status = completed` 로 기록한다. 이후 외부 변경이 감지되어 폐기되는 경우에만 `superseded` 로 전환한다.

### 최종 PR 코멘트 형식

최종 코멘트는 **stable issue ID** 단위로 작성한다. 동일 issue가 여러 라운드, 여러 Agent의 report로 재등장해도 한 번만 출력하며, 최신 report 문구와 최신 `consensus_reason` 을 사용한다.

#### 코멘트 태그 및 중복 게시 방지

코멘트 태그 형식: `[debate-review][sha:<initial_sha>]`

게시 전에 반드시 기존 코멘트를 조회해 동일 태그가 있는지 확인한다:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> \
  --json comments --jq '.comments[] | select(.body | startswith("[debate-review][sha:<initial_sha>]")) | .id'
```

- 기존 코멘트가 있으면: 상태 파일의 `final_comment_id` 가 null인 경우 backfill 후 게시 생략
- 없으면: 코멘트 게시 진행

게시 후 검증:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> \
  --json comments --jq '.comments[] | select(.body | startswith("[debate-review][sha:<initial_sha>]")) | .id'
```

검증 성공 시:
- `final_comment_tag = "[debate-review][sha:<initial_sha>]"`
- `final_comment_id = <comment_id>`
- 상태 파일 저장

#### same-repo PR

```text
[debate-review][sha:<initial_sha>] <N>라운드 만에 합의에 도달했습니다.

## Applied Fixes
- src/foo.ts:42 - (reported by Codex, applied by Codex in round 1) <message>
- src/bar.ts:10 - (reported by CC, applied by CC in round 2) <message>

## Withdrawn Findings
- src/baz.ts:21 - <message>
  Reason: <consensus_reason>
```

#### fork PR

```text
[debate-review][sha:<initial_sha>] <N>라운드 만에 합의에 도달했습니다. (fork PR - code push not allowed)

## Recommended Fixes
- src/foo.ts:42 - (reported by Codex) <message>
- src/bar.ts:10 - (reported by CC) <message>

## Withdrawn Findings
- src/baz.ts:21 - <message>
  Reason: <consensus_reason>
```

issue가 하나도 남지 않으면 `Recommended Fixes` 또는 `Applied Fixes` 섹션을 생략하고 `No actionable issues remain.` 문구만 남긴다.

---

## Section 4: 실패 처리 및 재시작

### 실패 유형별 처리 방침

| 실패 유형 | 처리 방식 | 상태 업데이트 |
|-----------|-----------|---------------|
| Step 0 sync 실패 | 즉시 중단, 다음 실행 시 sync부터 재시도 | `journal.step` 유지 |
| Step 1/2 분석 실패 | 해당 step 재시도 | `journal.step` 유지 |
| Codex JSON 파싱 실패 | 해당 step을 실패로 간주하고 원시 응답을 로그에 남긴 뒤 재시도 (동일 step 최대 3회, 초과 시 `status=failed`) | `journal.step` 유지 |
| commit 실패 | 해당 step 중단 | `commit_sha=null` |
| push 실패 | 해당 step 중단 | `push_verified=false` |
| 상태 파일 write 실패 | 외부 부작용은 이미 발생했을 수 있으므로 다음 실행에서 `journal` 기반 backfill 시도 | `state_persisted=false` |
| GitHub 인증/네트워크 오류 | `failed` 또는 run 중단 | 필요 시 `status=failed` |

### 완료된 세션 재실행 규칙

상태 파일 경로는 PR 단위로 고정이지만, debate-review의 **세션 경계는 `head.terminal_sha` 단위** 다.

세션이 terminal 상태(`consensus_reached|max_rounds_exceeded|failed`)에 도달하면, 그 시점의 PR HEAD를 `head.terminal_sha`에 기록한다. same-repo PR에서는 Step 3 커밋이 PR HEAD를 바꾸므로 `terminal_sha ≠ initial_sha`가 일반적이다.

#### terminal_sha 기록 시점

세션이 terminal 상태에 도달할 때 (최종 코멘트 게시 성공 후, 또는 `status=failed` 설정 시):

```
head.terminal_sha = <현재 PR HEAD SHA>
```

PR HEAD 조회: `env -u GITHUB_TOKEN -u GH_TOKEN gh pr view <number> --repo <repo> --json headRefOid --jq .headRefOid`

#### 재실행 판정

- 기존 상태가 **terminal session** 이고, 현재 PR HEAD가 `head.terminal_sha` 와 같으면:
  - 기존 세션 결과를 authoritative 하게 간주한다.
  - 새 session을 시작하지 않고 종료한다.
- 기존 상태가 terminal session 이고, 현재 PR HEAD가 `head.terminal_sha` 와 다르면:
  - **새 debate session 시작** 으로 간주한다.
  - 상태 파일을 아래 값으로 재초기화한다:
    - `status = in_progress`
    - `current_round = 1`
    - `head.initial_sha = <current_pr_head_sha>`
    - `head.last_observed_pr_sha = <current_pr_head_sha>`
    - `head.terminal_sha = null`
    - `head.pr_branch_name = <headRefName>`
    - `head.target_ref = refs/debate-sync/pr-<number>/head`
    - `head.synced_worktree_sha = <current_pr_head_sha>` (Step 0 완료 후)
    - `journal = { round: 1, step: "step0_sync", pre_sync_head_sha: <previous_or_null>, post_sync_head_sha: <current_pr_head_sha>, synced_worktree_sha: <current_pr_head_sha>, applied_issue_ids: [], failed_application_issue_ids: [], commit_sha: null, push_verified: false, state_persisted: true }`
    - `issues = {}`
    - `rounds = []`
    - `final_comment_tag = null`
    - `final_comment_id = null`
    - `started_at = <now>`
    - `finished_at = null`
    - `final_outcome = null`

즉, 동일 PR에서 세션 종료 이후 외부 커밋이 올라오면 이전 debate 세션의 comment tag와 state checkpoint를 재사용하지 않는다. 새 HEAD는 새 세션으로 취급한다. same-repo PR에서 Step 3가 만든 커밋만 있는 경우(= `terminal_sha`와 일치)에는 기존 세션을 올바르게 재사용한다.

### 재시작 규칙

재시작은 항상 아래 순서를 따른다.

1. 상태 파일 로드
2. `sync_pr_head()` 실행
3. `journal.pre_sync_head_sha` 와 `journal.post_sync_head_sha` 비교
4. `journal.commit_sha` 존재 시 PR HEAD가 그 commit SHA와 일치하는지 확인
5. 일치하면 mutation은 이미 반영된 것으로 보고 상태만 backfill:
   - `journal.applied_issue_ids` 의 각 issue: `application_status=applied`, `applied_by=<lead_agent>`, `application_commit_sha=journal.commit_sha`
   - `journal.failed_application_issue_ids` 의 각 issue: `application_status=failed`
   - `rounds[N].step3.applied_issue_ids = journal.applied_issue_ids`
   - `rounds[N].step3.failed_application_issue_ids = journal.failed_application_issue_ids`
   - `rounds[N].step3.commit_sha = journal.commit_sha`
   - `rounds[N].step3.push_verified = true`
6. 일치하지 않으면 해당 step의 mutation을 다시 수행

#### clean checkpoint에서 다음 step으로 진행

mutation backfill이 끝났거나, 현재 `journal.step` 이 mutation step이 아닌 clean checkpoint라면 **마지막으로 성공적으로 persisted된 step 다음 단계로 진행**한다.

- `journal.step = step0_sync` 이고 `state_persisted=true`:
  - 현재 round의 Step 1로 진행
- `journal.step = step1_lead_review` 이고 `state_persisted=true`:
  - `rounds[N].clean_pass = true` 이면 Step 4로 진행
  - 아니면 Step 2로 진행
- `journal.step = step2_cross_review` 이고 `state_persisted=true`:
  - Step 3으로 진행
- `journal.step = step3_lead_apply` 이고 `state_persisted=true`:
  - Step 4로 진행
- `rounds[N].status = completed` 이고 `status = in_progress`:
  - `current_round += 1` 후 다음 round의 Step 0으로 진행

즉, 재시작은 "마지막 persisted checkpoint를 다시 실행"하지 않고, **아직 실행되지 않은 다음 step** 부터 이어서 진행한다. 단, `state_persisted=false` 인 경우에는 위 규칙보다 `journal` 기반 backfill/복구 규칙을 우선 적용한다.

#### 외부 변경 판정

외부 변경은 commit subject 접두사로 추론하지 않는다. 아래 기준을 사용한다.

- `journal.pre_sync_head_sha` 와 `journal.post_sync_head_sha` 가 다름
- 그리고 `journal.post_sync_head_sha` 가 마지막 recorded `application_commit_sha` 또는 `journal.commit_sha` 와 일치하지 않음

이 경우:

- `rounds[N].status = superseded`
- 현재 round를 `superseded` 로 간주
- `current_round += 1`
- 최신 PR HEAD 기준으로 새 round 시작

**외부 변경 시 issue 상태 재설정 규칙:**

superseded가 확정되면 새 round 시작 전에 아래 규칙을 적용한다.

**`consensus_status` 재설정:**

| 기존 `consensus_status` | 재설정 후 | 이유 |
|---|---|---|
| `accepted` | `open` | 외부 push로 코드 맥락이 바뀌었을 수 있으므로 새 round에서 다시 합의 필요 |
| `open` | `open` | 유지 |
| `withdrawn` | `withdrawn` | 철회된 issue는 그대로 유지 |

재설정 시 `accepted_by` 는 빈 배열 `[]` 로 초기화한다. 새 round에서 양측 Agent가 다시 해당 issue를 보고하거나 accept해야 합의가 성립한다.

**`application_status` 재설정:**

| 기존 `application_status` | 재설정 후 | 이유 |
|---|---|---|
| `applied` | `pending` | 외부 push가 수정 내용을 덮었을 수 있음 |
| `failed` | `pending` | 새 HEAD에서 재시도 |
| `pending` | `pending` | 유지 |
| `recommended` | `pending` | 포크 PR이라도 외부 push 후 맥락이 바뀌었을 수 있음. 새 round에서 재평가 후 다시 `recommended` 설정 |
| `not_applicable` | `not_applicable` | withdrawn issue는 그대로 |

**더 이상 재현되지 않는 issue 처리:**

superseded 후 새 round의 Step 1/2에서 한 번도 보고되지 않은 `consensus_status=open` issue는, **Step 4 정산 시** 다음과 같이 처리한다.

**가드 조건:** 이 로직은 **직전 round의 `status`가 `superseded`인 경우에만** 실행한다. 비-superseded round에서는 HEAD가 바뀌지 않았으므로, 이전 round에서 보고된 issue가 현재 round에서 재보고되지 않았더라도 유효성이 유지된다.

1. `rounds[N-1].status == superseded` 인지 확인한다. 아니면 이 절차를 건너뛴다.
2. `step1.issue_ids_touched` ∪ `step2.issue_ids_touched` 에 포함되지 않은 `consensus_status=open` issue를 식별한다.
3. 이 issue들을 `consensus_status = withdrawn` 으로 전환한다.
   - `consensus_reason = "Not reported by either agent in round <N> after HEAD change"`
   - `application_status = not_applicable`
4. 이렇게 종결된 issue는 최종 코멘트의 `## Withdrawn Findings` 에 포함한다 (reason에 자동 종결임이 명시됨).

이 처리가 Step 2 직후가 아닌 Step 4에서 수행되는 이유: Step 3에서 lead agent가 cross-verifier의 findings에 응답하면서 해당 issue를 다시 보고할 가능성이 있기 때문이다. Step 4 시점에서 round 전체의 `issue_ids_touched`가 확정된 후에 판정해야 안전하다.

Note: `withdrawn`은 rebuttal에 의한 철회와 미재현에 의한 자동 종결을 모두 포함한다. `consensus_reason` 으로 구분할 수 있다.

### idempotency 원칙

- Step 0은 같은 SHA에 대해 여러 번 실행되어도 같은 worktree 상태를 만든다.
- Step 3는 `journal.commit_sha` 와 PR HEAD 비교로 "이미 push됨"을 판정한다.
- 최종 코멘트는 `[debate-review][sha:<initial_sha>]` 태그로 식별한다. `initial_sha` 는 세션 전체에서 불변이므로 same-repo PR의 Step 3 커밋이 PR HEAD를 바꿔도 태그가 안정적으로 유지된다. 게시 전 태그 조회 → 없으면 게시 → 검증 후 `final_comment_id` 기록. 재시작 시 `final_comment_id` 가 이미 있으면 게시를 생략한다.

### 10라운드 초과 시 코멘트

```text
[debate-review][sha:<initial_sha>] 10라운드 후 합의에 도달하지 못했습니다.

## Unresolved Issues
- <issue summary>

Manual review required.
```

### 오류 종료 시 코멘트

```text
[debate-review][sha:<initial_sha>] 오류로 인해 리뷰가 중단되었습니다.

Round: <N>
Step: <step>
Error: <error_message>

Manual review required.
```

모든 최종 코멘트(합의 성공, max_rounds, 오류)는 동일한 `[debate-review][sha:<initial_sha>]` 태그를 사용한다. 이를 통해 중복 게시 방지 로직과 `final_comment_tag` 매칭이 세 경우 모두에서 일관되게 작동한다.

---

## Section 5: 워크트리 및 실행 환경

### 사전 조건

로컬 클론이 반드시 존재해야 한다.

`repo_root` 결정 규칙:

1. 호출 인자로 `repo_root` 가 명시되면 그 값을 사용한다.
2. 없으면 `${WORKSPACE_ROOT:-$HOME/workspace}/<repo_name>` 를 시도한다. 여기서 `<repo_name>` 은 `owner/repo` 의 `repo` 부분이다.
3. 위 경로가 없으면 즉시 중단한다. owner/repo 문자열만으로 임의 경로를 추정하지 않는다.

```bash
repo_root="${REPO_ROOT:-${WORKSPACE_ROOT:-$HOME/workspace}/<repo_name>}"
if [ ! -d "$repo_root/.git" ]; then
  echo "ERROR: missing local clone at $repo_root"
  exit 1
fi
```

### target ref 규칙

- same-repo PR: `refs/debate-sync/pr-<number>/head`
- fork PR: `refs/debate-sync/pr-<number>/head`

이 target ref는 Step 0의 단일 source of truth 다.

### Codex 실행 환경

Codex는 worktree 안에서 실행한다.

```bash
cd <repo_root>/.worktrees/debate-pr-<number>
codex exec -s danger-full-access "<prompt>"
```

`danger-full-access` 이유:

- 상태 파일이 `$HOME/.claude/debate-state/` 아래에 있음
- worktree 바깥 경로 접근이 필요함

### CC 실행 환경

CC는 오케스트레이터로서:

- 상태 파일 읽기/쓰기
- `gh` 호출
- same-repo PR의 코드 수정
- 최종 코멘트 게시

를 수행한다.

### GitHub CLI 실행 규칙

모든 `gh` 명령은 아래 형식을 사용한다.

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh <subcommand>
```

### 워크트리 정리

정리 시점:

- `status=consensus_reached` 후 코멘트 게시 완료
- `status=max_rounds_exceeded` 후 코멘트 게시 완료
- `status=failed` 후 코멘트 게시 완료
- 사용자가 중단 요청

정리 명령:

```bash
git -C <repo_root> worktree remove \
  <repo_root>/.worktrees/debate-pr-<number> --force
```

---

## Section 6: 구현 요약

이 구조에서 구현 복잡도가 낮아지는 이유는 다음과 같다.

1. cross-round, cross-agent dedupe를 인덱스가 아니라 stable issue ID가 담당한다.
2. fork PR과 same-repo PR의 차이는 `application_status` 해석 차이로만 남는다.
3. 재시작은 commit message 추정이 아니라 `journal.commit_sha` 와 PR HEAD 비교로 처리한다.
4. stale worktree 문제는 Step 0 하나로 집중된다.
5. 라운드마다 **lead agent를 교대** 하여, 한 round에 리뷰어·수정자가 하나만 존재한다. 이전 설계의 양쪽 Agent가 동시에 리뷰·수정하는 구조에서 발생하던 `opened_by` 기반 mutation ownership, 교차 application 충돌, 상태 차원 간 조합 폭발 문제를 제거한다.

즉, 이 문서는 "라운드 기반 토론"이라는 상위 개념은 유지하면서도, 실제 구현이 부딪히는 다섯 가지 문제를 상태 모델 수준에서 제거하는 방향으로 재설계되었다.
