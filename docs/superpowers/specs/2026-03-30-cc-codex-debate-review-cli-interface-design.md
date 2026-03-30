# CC-Codex Debate Review CLI Interface 설계 문서

**작성일:** 2026-03-30
**상태:** 초안

---

## 개요

기존 `cc-codex-debate-review`는 markdown skill 문서가 오케스트레이션 전체를 직접 수행하는 구조를 전제로 한다. 이 방식은 상태 파일 갱신, 재시작 복구, worktree 동기화, GitHub/Git push 검증처럼 반복 가능성과 일관성이 중요한 로직을 자연어 절차에 과도하게 의존한다.

이 문서는 오케스트레이션의 실행 책임을 Python CLI 프로그램으로 이동할 때의 **사용자 관점 CLI 계약** 을 정의한다. 목적은 사용자가 어떤 명령을 어떤 입력으로 실행하고, 어떤 동작과 제약을 기대할 수 있는지 명확히 고정하는 것이다.

이 문서에서 다루는 범위는 다음과 같다:

- CLI 엔트리포인트와 기본 호출 형태
- 필수 인자와 주요 사용자 옵션
- 대표 실행 시나리오
- same-repo PR과 fork PR에서의 사용자 기대 동작
- 사전조건과 안전 제약

이 문서에서 **의도적으로 제외하는 범위** 는 다음과 같다:

- subcommand 구조
- exit code 체계
- stdout/stderr의 구조화 포맷
- resume/retry 세부 semantics
- 내부 상태 파일 스키마의 상세 mutation 규칙

위 항목들은 구현 단계에서 별도의 상세 설계 문서로 다룬다.

---

## 설계 목표

1. 사용자가 한 줄 명령으로 debate review를 시작할 수 있어야 한다.
2. 명령 인터페이스는 same-repo PR과 fork PR 모두에 대해 일관된 진입점을 제공해야 한다.
3. 위험한 동작(코드 수정, commit, push, PR comment)은 사용자가 예측 가능한 조건에서만 일어나야 한다.
4. 구현 세부가 바뀌더라도, 사용자가 기억해야 하는 CLI 계약은 최대한 안정적으로 유지해야 한다.
5. markdown skill은 얇은 운영 문서로 축소하고, 실제 상태 전이와 복구 로직은 코드가 책임지도록 해야 한다.

---

## 대안 검토

### 대안 1: 기존 markdown skill 중심 구조 유지

- 장점: 새 실행 파일이 필요 없고, 지금 있는 문서를 그대로 확장할 수 있다.
- 단점: 상태 전이와 예외 처리가 자연어 규칙에 흩어져 재현성과 테스트 가능성이 낮다.

### 대안 2: 단일 엔트리포인트 Python CLI + skill wrapper

- 장점: 사용자 인터페이스는 단순하게 유지하면서, 상태 관리와 외부 명령 호출을 코드로 이동할 수 있다.
- 장점: 문서, 테스트, 구현 책임이 비교적 선명하게 분리된다.
- 단점: 초기 구현 비용이 늘고, CLI와 skill 사이 계약을 유지해야 한다.

### 대안 3: 다중 subcommand 중심 CLI

- 장점: `init`, `run-round`, `resume`, `finalize` 등 내부 단계별 제어가 가능하다.
- 단점: 현재 사용자 요구에는 과하다. 내부 제어 모델이 너무 일찍 외부 인터페이스로 노출될 위험이 있다.

### 선택

이 설계는 **대안 2** 를 채택한다.

사용자에게는 단일 실행 명령을 제공하고, 내부 단계 분해는 외부 인터페이스가 아니라 구현 상세로 남긴다. 이렇게 해야 현재 필요한 단순한 사용성은 유지하면서도, 상태 머신과 복구 로직을 코드로 안전하게 옮길 수 있다.

---

## CLI 엔트리포인트

기본 엔트리포인트는 다음과 같이 정의한다.

```bash
bin/cc-codex-debate-review
```

이 명령은 사용자가 debate review 세션을 시작하거나, 같은 PR에 대해 다시 실행하여 진행 상태를 이어가도록 요청하는 **주 진입점** 이다.

skill 문서 `skills/ops/cc-codex-debate-review.md` 는 더 이상 상세 오케스트레이션 절차를 직접 수행하지 않고, 다음 책임만 가진다:

- 언제 이 CLI를 사용해야 하는지 설명
- 필수 사전조건을 안내
- 대표 실행 예시를 제시
- 필요한 경우 CLI를 호출하는 thin wrapper 역할 수행

즉, 사용자 경험의 기준점은 skill 문서가 아니라 CLI 자체가 된다.

---

## 기본 호출 형태

최소 호출 형태는 다음과 같다.

```bash
bin/cc-codex-debate-review --repo <owner/repo> --pr <number>
```

예시:

```bash
bin/cc-codex-debate-review --repo jk-kim0/skills-jk --pr 131
```

이 호출은 다음 의미를 가진다:

- 지정된 GitHub PR에 대한 debate review 세션을 시작한다.
- 기존 세션 상태가 있으면 이를 참고해 이어서 진행하거나 중복 실행을 피한다.
- same-repo PR이면 필요 시 코드를 수정하고 push할 수 있다.
- fork PR이면 코드를 push하지 않고 recommendation 중심으로 종료한다.

사용자는 기본적으로 **repo와 pr만 지정하면 된다**. 나머지 값은 설정 파일 또는 안전한 기본값으로 결정한다.

---

## 사용자 옵션 계약

### 필수 인자

#### `--repo <owner/repo>`

- 대상 GitHub 저장소를 지정한다.
- 형식은 반드시 `owner/repo` 여야 한다.
- 로컬 clone, GitHub PR 조회, 최종 comment 게시의 기준이 된다.

#### `--pr <number>`

- 대상 Pull Request 번호를 지정한다.
- 정수형 PR 번호만 허용한다.

### 주요 선택 인자

#### `--repo-root <path>`

- 대상 저장소의 로컬 clone 경로를 명시적으로 지정한다.
- 지정하지 않으면 기본적으로 `${WORKSPACE_ROOT:-$HOME/workspace}/<repo_name>` 을 탐색한다.
- 사용자가 같은 repo name을 여러 위치에 clone해 둔 경우, 이 옵션으로 ambiguity를 없앤다.

#### `--config <path>`

- debate review용 설정 파일 경로를 지정한다.
- 기본값은 repo의 `config/cc-codex-debate-review.yml` 이다.
- 설정 파일의 역할은 허용 repo 목록, 기본 `max_rounds`, Codex sandbox 등 런타임 기본값 제공이다.

#### `--max-rounds <number>`

- 이번 실행에 한해 최대 라운드 수를 override한다.
- 기본 동작은 config 값을 따른다.
- 사용자는 실험적 실행이나 디버깅 상황에서만 이 값을 직접 조정하는 것을 기대한다.

#### `--codex-sandbox <mode>`

- Codex subprocess 실행 시 사용할 sandbox 수준을 override한다.
- 기본값은 config에서 가져온다.
- 사용자는 구현 디버깅이나 운영 제약이 바뀐 경우에만 이 옵션을 직접 사용할 가능성이 크다.

#### `--no-comment`

- 최종 PR comment 게시를 생략한다.
- 로컬 검증, dry-run 성격의 운영, 개발 중 인터페이스 점검에 유용하다.
- 단, 이 옵션이 있어도 same-repo PR에 대한 코드 수정/commit/push 여부는 별도 정책으로 결정된다.

#### `--no-push`

- same-repo PR에서도 코드 수정 결과를 원격 브랜치에 push하지 않도록 강제한다.
- 이 옵션은 안전 가드 성격이다.
- 사용자가 실제 mutation 없이 review 흐름만 확인하고 싶을 때 사용한다.

#### `--dry-run`

- 네트워크 변경이나 원격 mutation 없이, 실행 계획과 예상 동작을 검증한다.
- 사용자 기대는 다음과 같다:
  - PR 메타데이터 조회, 로컬 사전조건 확인 같은 읽기 작업은 수행될 수 있다.
  - commit, push, PR comment 같은 원격 또는 영속 mutation은 발생하지 않는다.

`--dry-run`, `--no-push`, `--no-comment`의 정확한 상호작용은 구현 상세에서 추가 정의한다. 이 문서에서는 사용자에게 "위험한 mutation을 제한하는 안전 옵션이 존재한다"는 계약만 고정한다.

---

## 대표 사용 시나리오

### 1. 일반 same-repo PR 리뷰 실행

```bash
bin/cc-codex-debate-review --repo jk-kim0/skills-jk --pr 131
```

사용자 기대:

- CLI가 로컬 clone과 PR 메타데이터를 확인한다.
- 필요한 경우 worktree를 준비하고 debate review를 수행한다.
- 두 agent가 합의한 수정이 있으면 코드가 반영되고 push될 수 있다.
- 종료 후 최종 comment가 PR에 게시된다.

### 2. 명시적 로컬 clone 경로 사용

```bash
bin/cc-codex-debate-review \
  --repo chequer-io/deck \
  --pr 4821 \
  --repo-root /Users/jk/workspace/deck
```

사용자 기대:

- 자동 경로 탐색 대신 지정한 clone만 사용한다.
- 잘못된 repo를 잡는 일을 방지한다.

### 3. mutation 제한 모드로 실행

```bash
bin/cc-codex-debate-review \
  --repo jk-kim0/skills-jk \
  --pr 131 \
  --dry-run
```

사용자 기대:

- 실행 전제와 흐름은 점검하지만, commit/push/comment는 발생하지 않는다.
- 운영 전에 안전하게 인터페이스를 검증할 수 있다.

### 4. fork PR 리뷰 실행

```bash
bin/cc-codex-debate-review --repo owner/repo --pr 123
```

단, PR의 head owner가 base repo owner와 다를 경우 자동으로 fork PR로 취급한다.

사용자 기대:

- 리뷰와 합의 과정은 동일하게 수행된다.
- 코드 수정, commit, push는 생략된다.
- accepted issue는 recommendation으로 최종 comment에 정리된다.

---

## 사용자 관점 동작 계약

### 1. 단일 명령으로 세션을 시작한다

사용자는 내부 라운드나 단계 개념을 직접 호출하지 않는다. CLI는 하나의 명령으로 review 세션 전체를 담당한다.

### 2. 기본값 우선 인터페이스를 유지한다

일반 사용자는 `--repo` 와 `--pr` 외에 추가 옵션 없이 실행할 수 있어야 한다. 운영자가 아닌 사용자가 내부 제어 옵션을 많이 알아야 하는 인터페이스는 피한다.

### 3. same-repo와 fork의 차이는 자동 판별한다

사용자가 별도로 `--fork` 같은 플래그를 주지 않아도, CLI가 PR 메타데이터를 보고 동작 모드를 결정해야 한다.

### 4. 위험한 mutation은 예측 가능해야 한다

사용자가 기본 모드로 실행했을 때 어떤 종류의 mutation이 가능한지 미리 이해할 수 있어야 한다.

가능한 mutation:

- same-repo PR 브랜치에 대한 commit/push
- PR 최종 comment 게시
- 로컬 상태 파일 갱신
- 로컬 worktree 생성/정리

발생하지 않아야 하는 mutation:

- PR title/body 자동 수정
- base branch 변경
- 명시되지 않은 임의의 다른 브랜치 push

### 5. 재실행 가능성을 전제로 한다

CLI는 장시간 작업과 외부 실패 가능성을 전제로 설계되므로, 사용자는 같은 명령을 다시 실행하는 방식으로 진행을 이어갈 수 있어야 한다.

단, 정확한 resume/retry 판단 규칙은 후속 상세 설계에서 정의한다. 이 문서의 수준에서는 "재실행 가능한 단일 진입점"이라는 사용자 계약만 고정한다.

### 6. 진행 상황은 사람이 읽을 수 있어야 한다

기본 출력은 구조화된 내부 포맷보다 **사람이 읽기 쉬운 진행 로그** 를 우선한다. 사용자는 현재 어떤 PR을 처리 중인지, 어느 단계까지 갔는지, mutation이 있었는지, 최종 결과가 무엇인지 이해할 수 있어야 한다.

기계 친화적 JSON 출력이 필요하더라도, 그것은 별도 상세 설계에서 다룬다.

---

## 사전조건

CLI는 실행 전에 다음 전제가 충족되어야 한다.

- 대상 repo의 로컬 clone이 존재해야 한다.
- `gh` CLI 인증이 완료되어 있어야 한다.
- `codex` CLI를 사용할 수 있어야 한다.
- 로컬 환경에서 worktree 생성이 가능해야 한다.

설정 파일 외의 숨겨진 필수 입력을 요구해서는 안 된다. 사용자가 알아야 하는 입력은 명령행 인자와 config 파일로 제한한다.

---

## 운영 제약과 안전 규칙

### GitHub CLI 인증 규칙

이 도구는 GitHub CLI 호출 시 셸에 주입된 제한 토큰 대신 keyring 인증을 우선 사용해야 한다.

사용자 관점 계약은 다음과 같다:

- CLI는 내부적으로 안전한 `gh` 호출 규칙을 일관되게 적용한다.
- 사용자는 별도 래퍼 없이 CLI만 실행하면 된다.
- 인증 문제가 있으면 CLI가 이를 조기에 보고해야 한다.

### 로컬 상태 파일

세션 상태는 사용자의 홈 디렉토리 아래 영속 저장소에 기록된다.

기본 경로:

```text
~/.claude/debate-state/
```

사용자 기대:

- 프로세스가 중단되어도 완전히 무상태로 사라지지 않는다.
- 재실행 시 이전 세션 정보를 활용할 수 있다.

상태 파일 내부 스키마는 이 문서의 범위가 아니다.

### 로컬 worktree

CLI는 대상 repo 아래의 `.worktrees/` 를 사용해 별도 작업 디렉토리를 만들 수 있다.

사용자 기대:

- 현재 작업 중인 main checkout을 직접 오염시키지 않는다.
- review용 임시 작업 공간을 별도로 사용한다.

구체적인 디렉토리 naming 규칙과 정리 시점은 구현 상세에서 확정한다.

### same-repo PR mutation 규칙

same-repo PR에서는 accepted issue에 대해 코드 수정이 발생할 수 있다. 사용자는 기본 실행이 read-only가 아니라는 점을 이해해야 한다.

따라서 다음 규칙을 사용자 계약으로 둔다:

- 기본 모드에서는 same-repo PR에 대한 코드 반영과 push가 허용될 수 있다.
- 사용자가 mutation을 원하지 않으면 `--dry-run` 또는 `--no-push` 같은 안전 옵션을 사용할 수 있어야 한다.
- fork PR에서는 push가 자동으로 금지된다.

---

## skill 문서와의 역할 분리

최종적으로 `skills/ops/cc-codex-debate-review.md` 는 다음 책임만 남긴다.

- 이 도구가 필요한 상황 설명
- 필수 사전조건 설명
- 대표 CLI 예시 제공
- 사용자에게 필요한 안전 주의사항 안내

다음 책임은 CLI 구현으로 이동한다.

- 상태 파일 읽기/쓰기
- round loop 실행
- PR sync와 worktree 제어
- Codex prompt 조합과 subprocess 실행
- GitHub comment 게시
- restart/backfill 판단

이 분리를 통해 skill 문서는 운영 안내 문서가 되고, 실행 가능성과 복구 가능성이 필요한 로직은 테스트 가능한 코드로 이동한다.

---

## 비범위 항목

다음 항목은 이번 문서에서 고정하지 않는다.

- subcommand를 둘지 여부
- `run`, `resume`, `status` 같은 명령 분리 여부
- 종료 코드 세부 체계
- machine-readable JSON 출력 형식
- stderr 사용 원칙
- 세션 resume/retry 규칙의 세부 조건
- 상태 파일 필드명과 세부 mutation 알고리즘

이 항목들은 구현 단계에서 별도 상세 설계 문서 또는 구현 plan에서 정의한다.

---

## 결론

`cc-codex-debate-review`의 오케스트레이션은 markdown skill에서 직접 수행하기보다, `bin/cc-codex-debate-review` 라는 단일 Python CLI 엔트리포인트로 이동하는 것이 적절하다.

사용자에게는 다음 계약만 안정적으로 제공하면 된다.

- `--repo` 와 `--pr` 기반의 단일 실행 명령
- 명시적이지만 최소한의 주요 옵션
- same-repo/fork 자동 판별
- 예측 가능한 mutation 경계
- 재실행 가능한 운영 모델

이 계약 위에서 내부 구조는 이후 구현 단계에서 더 엄격하게 구체화할 수 있다.
