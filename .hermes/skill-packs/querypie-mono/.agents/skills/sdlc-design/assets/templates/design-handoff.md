# 설계 인수인계

## 다음 단계

- `build`

## 반드시 읽을 문서

- `README.md`
- `metadata.yaml`
- `design/result.md`
- `design/handoff.md`
- `build/tasks.md`

## 확정된 결정

- 없음

## 열린 결정

- Blocker: 없음
- Build handoff: 없음
- Case-wide: 없음
- Concern: 없음

## 구현 순서

- `build/tasks.md`의 의존성 순서에 따른다.
- plan에서 승인된 case PR 경계 안에서 구현하고 review한다.

## 금지 사항

- prototype이나 stub를 확정 구현으로 취급하지 않는다.
- 설계에서 제외한 범위를 build 단계에서 임의로 되살리지 않는다.
- 사용자 결정이 필요한 열린 결정을 Agent가 임의로 닫지 않는다.
- `.agents/runs/` runtime artifact를 다음 단계의 필수 근거로 두지 않는다.
- `build/tasks.md`에 없는 범위를 build 단계에서 임의로 추가하지 않는다.
- 여러 PR이 필요해 보이면 build에서 임의로 나누지 말고 plan case split을 재검토한다.

## 완료 조건

- Build 단계가 `build/tasks.md` 작업 단위를 구현하고 결과를 기록할 수 있다.
- Build 단계가 design의 contract, guardrail, testability 요구사항을 보존한다.
- Build 단계가 blocker 없이 시작할 수 있다.
- Build 단계가 plan에서 승인된 case PR 경계 안에서 진행할 수 있다.

## 참고 근거

- `plan/result.md`
- `plan/handoff.md`
- 필요 시 `evidence.md`
