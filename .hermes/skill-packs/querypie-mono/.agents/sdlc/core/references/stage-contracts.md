# Stage Contracts

단계 계약은 각 SDLC 단계가 어떤 문서를 읽고 어떤 문서를 써야 하는지 정의한다.
compact 또는 새 세션 이후에도 Agent는 이 계약과 case 파일만 보고 다시 시작한다.

## Common Contract

모든 단계는 다음 순서를 따른다.

1. `prepare-stage.sh <case-id> <stage>`를 실행한다.
2. 출력된 `반드시 읽을 문서`를 읽는다.
3. `references/stage-workflow.md`의 입력, 티키타카, 출력, 출력 보정 공정을 따른다.
4. `필요할 때만 읽을 문서`는 의심이나 근거 확인이 필요할 때만 연다.
5. 사용자 결정과 중요한 판단은 `checkpoint-stage.sh` 또는 단계 문서에 기록한다.
6. 단계 lifecycle status는 `metadata.yaml`에만 기록한다.
7. 산출물은 `references/document-quality.md`의 문서 품질 기준을 따른다.
8. 사용자가 단계 완료 의사를 표현하면 `references/stage-finish.md`를 따른다.
9. 먼저 `finish-stage.sh <case-id> <stage>`를 실행한다.
10. 내용 검토가 필요하면 `references/completion-review.md`에 따라 검토 파일을 작성한다.
11. 내용 검토가 완료를 허용하면 내부 완료 처리 스크립트를 실행한다.
12. 완료 전에 `validate-case.sh <case-id> <stage>`를 실행한다.

## Backtrack Contract

뒤 단계에서 앞 단계의 결정이나 산출물을 수정해야 하는 사실이 드러나면 현재 단계를
계속 진행하지 않는다.

Agent는 먼저 다음을 사용자에게 설명하고 승인을 받는다.

- 어떤 현재 단계에서 어떤 앞 단계로 되돌릴지
- 왜 현재 단계를 계속 진행하면 위험한지
- 이번 feedback loop에서 닫을 질문 1개가 무엇인지
- downstream 산출물 중 다시 확인해야 할 범위가 무엇인지

승인되면 다음 명령을 사용한다.

```bash
.agents/sdlc/core/scripts/backtrack-stage.sh <case-id> <target-stage> \
  --reason "<reason>" \
  --question "<question>"
```

Backtrack은 완료된 문서를 삭제하지 않는다. `metadata.yaml`의 현재 단계를 target stage로
옮기고, target 이후 현재 단계까지의 downstream stage를 `blocked`로 표시한다.

Target stage를 다시 완료할 때는 일반 stage finish 절차를 따른다.

## Stage Finish

사용자가 "이 단계는 완료하자", "다음 단계로 넘어가자", "마무리하자"처럼 완료
의사를 표현해도 Agent는 즉시 완료를 선언하지 않는다.

먼저 다음 명령을 실행한다.

```bash
.agents/sdlc/core/scripts/finish-stage.sh <case-id> <stage>
```

결과가 `내용 검토 필요`이면 Agent는 내용 검토 파일을 작성한다.

`finish-stage.sh`는 현재 단계 문서의 문서 품질도 함께 검사한다.

내용 검토가 완료 가능이면 내부 완료 처리 스크립트를 실행한다.

우려가 있으면 사용자가 진행을 승인한 뒤 내부 완료 처리 스크립트를 실행한다.

결과가 `blocked`이면 Agent는 미완료 사항을 사용자에게 알려준다. 이때 사용자가
결정해야 하는 항목과 Agent가 문서를 보완하면 되는 항목을 구분한다.

`남은 결정`은 case 전체의 열린 결정일 수 있으므로 자동으로 completion blocker로
보지 않는다. 현재 단계 완료를 막는 항목은 문서에 `[미완료]`, `[blocker]`, `TODO`,
`TBD`, 빈 placeholder 같은 명확한 신호로 남긴다. 다음 단계로 넘길 항목은
`handoff.md`에 인수인계한다.

Agent는 내용 검토와 내부 완료 처리 없이 단계 완료를 선언하면 안 된다.

내부 완료 처리 스크립트는 내용 검토 파일의 문서 품질을 다시 검사한다.

## Stage Read/Write Sets

`plan`

- 읽기: `README.md`, `metadata.yaml`, `evidence.md`
- 쓰기: `plan/result.md`, `plan/handoff.md`, root 문서 갱신

`design`

- 읽기: `README.md`, `metadata.yaml`, `plan/result.md`, `plan/handoff.md`
- 쓰기: `design/result.md`, `design/handoff.md`, `build/tasks.md`, root 문서 갱신

`build`

- 읽기: `README.md`, `metadata.yaml`, `design/result.md`, `design/handoff.md`,
  `build/tasks.md`
- 쓰기: `build/result.md`, `build/handoff.md`, root 문서 갱신

`test`

- 읽기: `README.md`, `metadata.yaml`, `build/result.md`, `build/handoff.md`
- 쓰기: `test/result.md`, `test/handoff.md`, root 문서 갱신

`review`

- 읽기: `README.md`, `metadata.yaml`, `test/result.md`, `test/handoff.md`
- 쓰기: `review/result.md`, `review/handoff.md`, root 문서 갱신

`documentation`

- 읽기: `README.md`, `metadata.yaml`, `review/result.md`, `review/handoff.md`
- 쓰기: `documentation/result.md`, `documentation/handoff.md`, docs 승격 후보,
  root 문서 갱신

`release`

- 읽기: `README.md`, `metadata.yaml`, `documentation/result.md`,
  `documentation/handoff.md`
- 쓰기: `release/result.md`, `release/handoff.md`, root 문서 갱신

`evidence.md`는 모든 단계에서 선택적으로 읽을 수 있다. 단, 기본 문맥으로 항상
전부 읽지 않는다. 근거 확인, 위험 검토, source 재검증이 필요할 때만 연다.

## Stage Responsibilities

- `plan`: 문제, 목표, 제외 범위, 기대효과, 진행 추천을 정리한다. 코드 조사는 영향
  가능성과 설계 질문을 찾기 위한 것이며, 기술 선택과 구현 구조는 확정하지 않는다.
- `design`: plan의 방향을 설계로 바꾸고 build가 실행할 작업 단위를 만든다.
- `build`: design이 정의한 작업 단위를 구현하고 구현 결과를 기록한다.
- `test`: 자동/수동 검증 결과와 남은 품질 위험을 기록한다.
- `review`: 코드, 제품, 보안, 운영 관점의 리뷰 결과와 조치 여부를 기록한다.
- `documentation`: 제품 지식으로 승격할 문서를 판단하고 `docs/` 반영 후보를 정리한다.
- `release`: 배포, backport, 운영 확인, 유지보수 인수인계를 기록한다.

## Handoff Quality Bar

좋은 handoff는 다음 질문에 답한다.

- 다음 단계가 먼저 읽어야 할 문서는 무엇인가?
- 이미 확정된 결정과 아직 열린 결정은 무엇인가?
- 다음 단계가 하면 안 되는 일은 무엇인가?
- 다음 단계가 완료되었다고 볼 수 있는 조건은 무엇인가?
- compact 이후에도 대화 기록 없이 이어갈 수 있는가?
