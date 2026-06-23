# SDLC Backtrack User Guide

이 문서는 사용자가 `sdlc-backtrack`을 어떻게 요청하는지 설명한다.

Backtrack은 뒤 단계에서 앞 단계의 결정을 다시 열어야 할 때 사용한다. 단순히
`metadata.yaml`을 되돌리는 작업이 아니라, 근거가 타당한지 검토하고 어느 방향으로
수정할지 정하는 티키타카 절차다.

## 시작하기

예시는 다음과 같다.

- `sdlc-backtrack으로 MCP 포함 여부를 design에서 다시 봐야 하는지 검토해줘`
- `test 중 발견한 이 문제가 build 문제인지 design backtrack인지 판단해줘`
- `이 근거가 타당하면 어느 단계로 돌아가야 하는지 제안해줘`

case id를 모르면 Agent가 `.sdlc/cases/`에서 현재 진행 중인 case를 찾을 수 있다.

## 사용자가 결정할 것

Agent는 다음을 제안한다.

- backtrack이 필요한지
- target stage가 어디인지
- 이번 loop에서 닫을 질문 1개가 무엇인지
- 가능한 선택지와 추천 방향
- downstream에서 다시 확인해야 할 산출물

사용자는 방향을 승인하거나, 현재 단계 처리, handoff, case split 중 하나를 선택한다.

## 승인 후 일어나는 일

승인되면 Agent가 core backtrack script로 lifecycle status를 이동한다.

그 다음 target stage skill을 사용해 승인된 질문을 닫는다. 예를 들어 design 결정
누락이면 `sdlc-design`으로 돌아가 `design/result.md`, `design/handoff.md`,
`build/tasks.md` 중 필요한 부분을 수정한다.

Downstream 산출물은 삭제하지 않는다. 대신 stale 상태로 보고 다시 검토한다.
