# Case and Task Model

이 문서는 design 단계에서 `case`와 `task`를 구분하는 기준을 정의한다.

## Case

`case`는 승인된 SDLC 작업의 공식 컨테이너다.

Case는 다음을 담는다.

- 해결할 문제와 기대 결과
- 포함 범위와 제외 범위
- 사용자 결정과 open decision
- Jira, source, 문서, 역할 검토 근거
- plan, design, build, test, review, documentation, release stage 산출물
- stage lifecycle status

Case는 보통 `.sdlc/cases/<case-id>/` 아래에 저장된다.

Case는 Jira ticket 하나와 1:1일 필요가 없다. 관련 ticket 여러 개가 같은 문제와
목표를 공유하면 하나의 case가 될 수 있다.

Case가 답하는 질문:

- 왜 이 일을 하는가?
- 어떤 결과가 성공인가?
- 무엇이 범위 안이고 밖인가?
- 어떤 결정이 이미 내려졌는가?
- 다음 단계는 무엇을 이어받아야 하는가?

## Plan-Approved Case and PR Boundary

Design 단계는 case와 PR 경계를 새로 정하지 않는다. plan 단계에서 승인된 case/PR
경계를 따른다.

Plan 단계의 기본 원칙은 `case` 1개가 PR 1개로 이어지는 것이다. Design 중 여러 PR이
필요해 보이면 task를 임의로 쪼개서 해결하지 않고, plan 단계의 case split 판단으로
되돌릴 필요가 있는지 기록한다.

PR이 답하는 질문:

- 이 case의 변경을 review하고 merge할 수 있는가?
- 포함된 task와 commit이 case 목표를 달성하는가?
- test, review, release 단계가 같은 case 범위로 이어질 수 있는가?

Task와 commit은 PR 안에서 여러 개가 될 수 있다. 하지만 PR의 기본 경계는 case다.

## Task

`task`는 하나의 case 안에서 build가 실행할 구현 단위다.

Task는 design 단계에서 만들어지고 `build/tasks.md`에 기록된다.

Task는 다음을 담는다.

- task 목표
- 연결된 case 목표 또는 design 결정
- 변경 범위와 영향 영역
- 선행 의존성
- 관련 역할 또는 owner
- 구현 guardrail
- 완료 조건
- 검증 기준
- 제외 범위

Task가 답하는 질문:

- 어떤 조각을 바꿀 것인가?
- 어떤 순서로 구현해야 하는가?
- 어떤 contract나 guardrail을 지켜야 하는가?
- 완료 여부를 어떻게 확인할 것인가?
- 누가 review하거나 결정해야 하는가?

## 차이점

| 구분      | Case                             | Task                            |
| --------- | -------------------------------- | ------------------------------- |
| 목적      | 문제와 결과를 관리한다           | 구현 실행 단위를 관리한다       |
| 범위      | plan부터 release까지 이어진다    | 주로 build와 test에 쓰인다      |
| 크기      | 하나의 제품/기술 목표 묶음       | 작고 검토 가능한 변경 조각      |
| 위치      | `.sdlc/cases/<case-id>/`         | 같은 case의 `build/tasks.md`    |
| 결정 수준 | 제품, 범위, 기술 방향            | 구현 순서, 변경 범위, 검증 기준 |
| 관계      | 하나의 case가 여러 task를 만든다 | 하나의 task는 한 case에 속한다  |

## Task, Commit, PR

Task는 SDLC 관리 단위이고 commit은 git 변경 기록 단위다.

하나의 task는 0개, 1개, 또는 여러 commit으로 구현될 수 있다. 여러 task가 하나의
commit에 묶일 수도 있다. 이 mapping은 build 결과에 기록한다.

PR은 review와 merge 단위다. Design은 plan에서 승인된 case PR 경계 안에서 task를
만든다.

## Task 생성 원칙

Task는 raw idea나 chat history에서 바로 만들지 않는다.

반드시 다음 입력에서 파생한다.

- case goal
- plan result와 plan handoff
- design에서 확정한 기술 결정
- evidence로 확인한 실제 영향 영역

Task를 쪼갤 때는 다음 기준을 사용한다.

- contract 먼저: API, schema, shared type, protocol처럼 downstream을 막는 일을 앞에 둔다.
- risk 분리: 보안, migration, rollout 위험이 큰 변경은 독립 task로 둔다.
- vertical slice 우선: 가능하면 사용자-visible 흐름 단위로 작게 닫힌 task를 만든다.
- cross-cutting 명시: logging, audit, metric, permission은 숨은 작업으로 두지 않는다.
- testability 포함: 각 task는 검증 기준을 함께 가진다.
- exclusion 포함: task가 하지 않을 일을 명시해 scope creep을 막는다.
- ownership 분리: Agent 초안, 팀 review, 사람 결정이 섞이면 task로 확정하지 않는다.

## 좋지 않은 Task

- "백엔드 수정"
- "프론트 처리"
- "테스트 추가"
- "QPD-1234 구현"
- "리팩토링"

이런 task는 목적, 범위, 검증 기준이 모호하다.

## 좋은 Task

- "API server가 산출한 canonical Client IP를 `kubepie-proxy` 내부 호출 header에 전달한다."
- "trusted upstream 조건을 만족할 때만 proxy가 내부 Client IP header를 우선 사용하게 한다."
- "Request Audit 저장 경로가 canonical Client IP를 기록하는지 regression test를 추가한다."

좋은 task는 case 목표와 design 결정에 연결되고, build worker가 바로 검증 기준을
세울 수 있다.
