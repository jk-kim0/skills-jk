---
name: ci-follow-through-governed
description: Use when a task involves commit, push, PR creation/update, or CI status confirmation. Enforces proactive CI tracking without waiting for user prompts.
---

# CI Follow-Through Governed

## When to use

- commit 이후 push 했을 때
- PR을 생성하거나 업데이트했을 때
- 사용자가 "CI 상태 알려줘", "PR 올려줘", "머지 가능한가", "리뷰 가능한가"처럼 CI 확인이 필요한 결과를 기대할 때
- 완료 조건에 CI 상태 확인이 포함되는 작업일 때

## Hard rules

1. CI 확인이 필요한지 사용자에게 다시 묻지 않는다.
2. push 또는 PR 업데이트 후에는 내가 먼저 CI 상태를 확인한다.
3. 첫 확인은 `gh pr checks` 또는 동등한 명령으로 한다.
4. `gh pr checks` 가 비어 있거나 늦게 반영되면 바로 `gh run list --branch <branch>` 로 run 생성 여부를 확인한다.
5. CI가 진행 중이면 완료 전까지 추적한다.
6. 완료 전에 성공을 암시하지 않는다. 진행 중이면 진행 중이라고 말한다.
7. 실패가 나오면 사용자 지시를 기다리지 말고 로그를 조사하고, 내가 고칠 수 있는 문제면 바로 수정한다.
8. 모든 `gh` 호출은 `env -u GITHUB_TOKEN gh ...` 형식을 유지한다.

## Output contract

- commit/push/PR 후 상태 보고에는 아래를 포함한다.
  - 확인한 branch 또는 PR
  - 확인에 사용한 명령 종류
  - 최신 CI 상태: `success`, `failure`, `in_progress`, `no checks yet`
- `no checks yet` 인 경우에도 거기서 멈추지 않고 run 존재 여부를 추가 확인했다고 명시한다.

## PR description policy

- JK 사용자의 PR description 은 기본적으로 한국어로 작성한다.
- feature 구현 PR 은 아래 3개 관점으로 작성한다.
  - `기존 문제` 또는 `Why`
  - `구현 내용` 또는 `What`
  - `기대 효과` 또는 `Impact`
- bug fix PR 은 아래 2개 관점으로 작성한다.
  - `문제 현상`
  - `구현 내용`
- 단순 코드 변경 요약으로 끝내지 않는다. 이 PR 을 왜 만들었는지, 배경이 무엇인지, 어떤 효과가 있는지 드러나야 한다.

## PR creation policy

- 저장소에 PR 생성용 GitHub Actions workflow 가 있으면 직접 `gh pr create` 하지 않는다.
- 우선 `.github/workflows/create-pr.yml` 또는 동등한 `workflow_dispatch` 기반 PR 생성 workflow 존재 여부를 확인한다.
- 해당 workflow 가 있으면 `env -u GITHUB_TOKEN gh workflow run ...` 으로 PR 생성을 트리거한다.
- workflow run 이후에는 생성된 run 과 PR 번호를 확인하고, 그 PR 기준으로 후속 `gh pr checks` / `gh run list` 추적을 진행한다.
- 직접 `gh pr create` 는 PR 생성 workflow 가 없을 때만 fallback 으로 사용한다.
