# Stage Backtrack

Backtrack은 뒤 단계에서 앞 단계의 결정이나 산출물을 짧게 다시 열어야 할 때 사용한다.

목표는 전체 SDLC를 되돌리는 것이 아니라, 진행 중 발견한 질문을 가장 가까운 책임
단계에서 닫고 downstream 산출물을 다시 신뢰 가능한 상태로 만드는 것이다.

## 언제 사용하는가

다음 상황에서는 현재 단계를 계속 진행하지 않고 backtrack을 검토한다.

- build 중 design 결정이 틀렸거나 빠졌다는 사실을 발견했다.
- test 중 구현 문제가 아니라 design 또는 build task 정의 문제가 드러났다.
- review 중 이전 단계의 scope, guardrail, risk 처분을 다시 확정해야 한다.
- documentation 또는 release 중 고객 영향, rollout, 제외 범위를 앞 단계에서 고쳐야 한다.

질문이 현재 단계의 책임이면 backtrack하지 않는다. 현재 단계 문서에 기록하고 처리한다.

## 원칙

- 한 번의 backtrack은 닫아야 할 핵심 질문을 1개로 제한한다.
- 완료된 앞 단계 문서를 조용히 수정하지 않는다.
- 먼저 사용자에게 backtrack 이유, 되돌릴 단계, 확정할 질문을 설명한다.
- 승인되면 core script로 lifecycle status를 이동한다.
- downstream 산출물은 삭제하지 않고 stale 상태로 취급한다.
- 다시 열린 단계는 변경 이유와 downstream 영향 범위를 기록한다.

## 실행

근거 검토와 사용자 티키타카가 필요하면 `sdlc-backtrack` skill을 먼저 사용한다.

현재 단계에서 앞 단계로 되돌리기로 승인되면 다음 script를 사용한다.

```bash
.agents/sdlc/core/scripts/backtrack-stage.sh <case-id> <target-stage> \
  --reason "<왜 되돌리는가>" \
  --question "<이번 loop에서 닫을 질문>"
```

`target-stage`는 현재 단계보다 앞 단계여야 한다.

script는 다음을 수행한다.

- `metadata.yaml`의 `current_stage`를 `target-stage`로 바꾼다.
- `current_status`와 대상 stage status를 `draft`로 바꾼다.
- 대상 이후 현재 단계까지의 downstream stage status를 `blocked`로 바꾼다.
- `README.md`와 대상 stage `result.md`에 backtrack checkpoint를 남긴다.
- `.agents/runs/sdlc-stage/<case-id>/` 아래에 backtrack report를 남긴다.

## 다시 진행하기

되돌린 단계에서는 `prepare-stage.sh <case-id> <target-stage>`로 시작한다.

Agent는 다음을 읽는다.

- 대상 stage의 원래 입력 문서
- `README.md`의 최근 checkpoint
- 대상 stage `result.md`의 backtrack checkpoint
- 필요한 경우 backtrack을 유발한 downstream stage의 `result.md`와 `handoff.md`

질문을 닫으면 일반 stage finish 절차를 따른다.

```bash
.agents/sdlc/core/scripts/finish-stage.sh <case-id> <target-stage>
```

대상 stage가 finalize되면 다음 stage는 다시 `draft`가 된다. Downstream 산출물은 기존
내용을 재사용할 수 있지만, 변경된 결정과 충돌하지 않는지 다시 확인해야 한다.

## 사용자 응답

사용자에게는 내부 상태 전환보다 판단을 먼저 설명한다.

- 어떤 단계에서 어떤 단계로 되돌릴지
- 왜 지금 계속 진행하면 위험한지
- 이번 loop에서 확정할 질문 1개가 무엇인지
- downstream 산출물 중 다시 검토해야 할 범위가 무엇인지

내부 script 이름은 사용자가 절차를 물었거나 실행 근거가 필요할 때만 말한다.
