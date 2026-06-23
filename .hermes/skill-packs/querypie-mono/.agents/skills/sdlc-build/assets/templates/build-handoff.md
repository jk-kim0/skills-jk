# 구현 인수인계

## 다음 단계

- `test`

## 반드시 읽을 문서

- `README.md`
- `metadata.yaml`
- `design/result.md`
- `design/handoff.md`
- `build/tasks.md`
- `build/result.md`
- `build/handoff.md`

## 확정된 결정

- 없음

## 열린 결정

- Blocker: 없음
- Test handoff: 없음
- Release concern: 없음
- Case-wide: 없음

## 검증 우선순위

- 없음

## 금지 사항

- design에서 제외한 범위를 test 단계에서 완료 조건으로 되살리지 않는다.
- build에서 실행하지 못한 검증을 성공한 것으로 간주하지 않는다.
- `.agents/runs/` runtime artifact를 다음 단계의 필수 근거로 두지 않는다.

## 완료 조건

- Test 단계가 build 결과와 변경 파일을 기준으로 자동 또는 수동 검증을 수행한다.
- Test 단계가 build에서 남긴 residual risk를 검증하거나 다음 단계로 명확히 인수인계한다.
- Test 단계가 실패를 발견하면 재현 조건과 영향 범위를 기록한다.

## 참고 근거

- `design/result.md`
- `design/handoff.md`
- `build/tasks.md`
- `build/result.md`
