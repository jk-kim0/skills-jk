# SDLC Build User Guide

이 문서는 사용자가 `sdlc-build`를 어떻게 요청하고 마무리하는지 설명한다.

사용자는 내부 script, 검사 이름, 상태값을 외울 필요가 없다. 승인된 case id와 원하는
구현 범위를 자연어로 주면 Agent가 필요한 문서를 읽고 구현, 검증, 인수인계를 진행한다.

## 시작하기

Build를 시작하려면 case가 design을 마쳤고 `build/tasks.md`를 가진 상태여야 한다.

예시는 다음과 같다.

- `sdlc-build로 2026-06-08-qpd-5242-qpd-5294-kac-web-client-ip 구현해줘`
- `이 case build 단계 진행해줘`
- `build task 2부터 구현해줘`
- `task 1이 아직 필요한지 보고, 필요하면 구현까지 해줘`

case id를 모르면 Agent가 `.sdlc/cases/`에서 build 준비 상태의 case를 찾을 수 있다.

## 부분 Task 요청

사용자는 전체 build 대신 특정 task만 요청할 수 있다.

Agent는 요청받은 task를 먼저 처리하되, 다음을 `build/result.md`에 남긴다.

- 실행한 task
- 아직 남은 task
- task 간 의존성 때문에 함께 처리한 변경
- 제외하거나 뒤로 넘긴 이유

부분 task 구현은 case 목표를 바꾸지 않는다. 남은 작업은 build 또는 test handoff에
명확히 남긴다.

## Agent에게 위임하기

Build 단계에서 Agent는 잘 정의된 구현의 1차 작성자가 된다.

Agent에게 위임하기 좋은 일은 다음과 같다.

- 작성된 spec을 코드 구조로 옮기기
- 기존 pattern을 따라 service, API, UI, test를 연결하기
- error handling, telemetry, security wrapper 같은 boilerplate 맞추기
- build, lint, test 오류를 보고 scope 안에서 수정하기
- 구현과 함께 test 또는 manual validation 절차 작성하기
- 요청 시 PR message 후보와 changeset 요약 작성하기

사용자는 제품 동작, edge case, 설계 tradeoff, release risk를 판단한다. Agent가 design과
다른 방향이 필요하다고 판단하면 구현을 밀어붙이지 않고 결정을 요청한다.

## 진행 중 확인할 것

사용자는 다음을 확인하면 된다.

- Agent가 실행한 명령이 성공했는가?
- 실패한 명령의 원인이 환경 문제인지 구현 문제인지 구분됐는가?
- 변경이 `build/tasks.md`와 design contract 범위 안에 있는가?
- 보안, 성능, migration, 운영 위험이 숨겨져 있지 않은가?

`AGENTS.md`에 test, lint, build 명령과 local convention이 잘 적혀 있으면 Agent가 더
긴 구현 loop를 안정적으로 수행할 수 있다.

## 마무리하기

Build가 충분하다고 판단되면 사용자는 `마무리해줘`라고 말하면 된다.

Agent는 문서 품질, task 처분, 변경 파일, 검증 결과, 다음 test handoff를 확인한다.

마무리 결과는 다음 셋 중 하나로 안내된다.

- `마무리 완료`: test 단계로 넘길 수 있다.
- `보완 필요`: Agent가 고칠 문서 문제나 사용자가 결정할 항목이 남아 있다.
- `진행 승인 필요`: 우려는 있지만 사용자의 판단으로 다음 단계 진행이 가능하다.

## 산출물 위치

Build 산출물은 다음 위치에 저장된다.

```text
.sdlc/cases/<case-id>/
  README.md
  metadata.yaml
  build/tasks.md
  build/result.md
  build/handoff.md
```

구현 중 임시 조사 자료는 `.agents/runs/sdlc-build/<case-id>/` 아래에 둘 수 있다.

다음 단계가 반드시 알아야 하는 내용은 `.agents/runs/`가 아니라 case 문서에 요약한다.
