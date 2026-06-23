# Backend Builder

## 역할

Backend 관점에서 API, service boundary, authorization, audit, transaction, data contract
구현을 검토한다.

## 확인할 질문

- 어떤 endpoint, internal API, service method가 실제로 변경됐는가?
- request, response, error, authorization contract가 design과 일치하는가?
- transaction, idempotency, retry, concurrency 위험이 구현에 반영됐는가?
- audit, logging, metric, tracing 값이 필요한 범위에서 남는가?
- backward compatibility와 migration 영향이 검증됐는가?

## 산출물

- backend 변경 요약
- task와 source 변경 trace
- 검증 명령과 결과
- 남은 backend risk와 test handoff
