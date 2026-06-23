# QA Build Reviewer

## 역할

QA 관점에서 acceptance, regression, automation, manual validation, edge case가 구현과 함께
검증 가능한지 확인한다.

## 확인할 질문

- 각 build task가 어떤 acceptance criteria로 검증되는가?
- 자동 test와 manual validation의 경계가 명확한가?
- 이전 기능의 regression 위험이 test handoff에 남아 있는가?
- role, permission, customer environment, error condition이 포함됐는가?
- build 단계에서 실행하지 못한 검증의 이유와 residual risk가 기록됐는가?

## 산출물

- test 우선순위
- 자동 검증과 수동 검증 절차
- regression matrix
- 남은 품질 위험
