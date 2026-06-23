# Build 작업 단위

## Case 연결

- Case 목표: 없음
- Design 결정: 없음
- Task 분리 기준: 없음
- 제외된 task 후보: 없음
- PR 기준: plan에서 승인된 case PR 경계 안에서 구현한다.

## 작업 단위

- Task ID: `TASK-1`
  - 목표: 없음
  - 연결된 design 결정: 없음
  - 변경 범위: 없음
  - 영향 영역: 없음
  - 선행 의존성: 없음
  - 관련 역할: 없음
  - 위험과 guardrail: 없음
  - 검증 방식: 없음
  - 검증 기준: 없음
  - 완료 조건: 없음
  - 제외 범위: 없음

## 의존성

- 없음

## Task 조정 기준

- 제거: case 목표나 design 결정에 trace되지 않는 task
- 추가: 누락된 영향 영역, 선행 contract, 보안, 운영, QA task
- 병합: 같은 책임과 같은 검증 기준을 가진 task
- 분리: 독립적인 위험, 의존성, owner, 검증 기준이 섞인 task

## 제외 범위

- 없음

## 구현 Guardrail

- design 단계에서 확정한 contract를 변경하지 않는다.
- prototype 결과를 production source에 그대로 복사하지 않는다.
- 보안, 접근성, 운영 guardrail을 구현 과정에서 약화하지 않는다.
- task 안에서 case 목표나 제품 범위를 다시 정의하지 않는다.
- 여러 PR이 필요해 보이면 build에서 임의로 나누지 말고 plan case split을 재검토한다.

## 검증 기준

- 각 작업 단위는 자동 또는 수동 검증 기준을 가진다.
- test 단계로 넘길 regression 위험을 build 결과에 기록한다.
