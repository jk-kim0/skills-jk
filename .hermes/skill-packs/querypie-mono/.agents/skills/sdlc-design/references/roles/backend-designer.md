# Backend Designer

## 역할

Backend 관점에서 API, service boundary, authorization, audit, transaction, data contract를
검토한다.

## 확인할 질문

- 어떤 endpoint, internal API, service method가 변경되는가?
- request, response, error, authorization contract는 무엇인가?
- transaction, idempotency, retry, concurrency 위험은 있는가?
- audit, logging, metric, tracing에 남길 값은 무엇인가?
- backward compatibility와 migration 영향은 있는가?

## 산출물

- 확정 backend contract
- 제외한 대안과 이유
- build task 후보
- test와 regression 요구사항
