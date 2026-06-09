---
name: memory-directives-governed
description: Record and maintain persistent user "remember this" instructions. Use this when the user asks you to remember something, not forget it, always follow a rule, or preserve an operational preference across future turns.
---

# Memory Directives Governed

## When to use

다음과 같은 요청이면 이 skill 을 사용한다.
- "기억해줘"
- "잊지 마"
- "앞으로는 항상"
- "다음부터는"
- 반복 실수를 막기 위한 지속 규칙 추가 요청

## Required behavior

1. 지시를 세션 기억만으로 처리하지 않는다.
2. 기존 skill 문서 중 맞는 곳이 있으면 거기에 규칙을 추가한다.
3. 맞는 skill 이 없으면 새 skill 을 만든다.
4. 규칙은 짧고 실행 가능하게 적는다.
5. 어디에 기록했는지 사용자에게 파일 경로로 알린다.

## Preferred location

1. 전역 운영 규칙이면 `~/.codex/skills/` 아래 skill 로 남긴다.
2. 저장소 고유 워크플로우면 해당 저장소 맥락에 맞는 skill 로 남긴다.
3. 단순 교차 참조가 필요하면 전역 `~/AGENTS.md` 에 한 줄 정책을 추가할 수 있다.

## Examples

- `gh` 사용 전 항상 `GITHUB_TOKEN` unset
- PR 완료 기준은 로컬 변경이 아니라 실제 push 와 PR 반영
- 특정 디버깅 흐름은 테스트 우선으로 진행

## Persistent User Directives

- JK 사용자에게 PR 관련 답변을 할 때는 항상 PR 번호를 포함한다.
- JK 사용자가 작업을 지시하면, 별도 중단 지시가 없는 한 구현/문서 변경 후 commit, push, PR 작성까지 진행한다.
- JK 사용자와 작업할 때, 내가 필요하다고 판단한 보완/개선이 아직 `commit`/`push`되지 않았다면 설명만 하지 말고 로컬 워크트리에 실제로 적용한다.
- JK 사용자가 수정 이후 후속 반영을 기대하는 맥락에서는 추가로 발견한 잘못된 코드나 CI 복구 변경도 묻지 말고 바로 `commit`/`push`까지 이어서 처리한다.
- JK 사용자 작업의 완료 기준은 PR 작성만이 아니라 PR 작성 후 CI 상태를 확인하고 정상 통과까지 확인하는 것이다.
- JK 사용자가 `/goal` 기반 장기 작업을 지시한 경우, PR 생성/업데이트 후 계속 작업하기 전에 최신 `origin/main`을 fetch하고, 필요한 경우 작업 브랜치를 최신 main 기준으로 rebase/merge하거나 새 브랜치/워크트리에서 이어간다.
- JK 사용자의 `/goal` 기반 장기 작업 중에는 각 주요 step 전후로 계획 문서 변경 여부와 세부 목표/완료 조건 변경 여부를 다시 확인한다.
- JK 사용자와 git 저장소에서 작업할 때는 항상 별도 git worktree에서만 파일 변경을 만들고, root checkout/main repository workspace는 main branch 추종용으로만 취급하며 어떤 변경도 만들지 않는다.
- JK 사용자의 corp-web-app 작업에서는 사용자가 명시적으로 요청하지 않는 한 로컬에서 `npm run build`를 실행하지 않는다. PR 검증은 로컬 단위 테스트/포맷/응답 확인 후 CI에서 확인한다.
