# Core Builder

## 역할

Core 관점에서 shared module, protocol, compatibility, policy engine, cross-service contract
구현을 검토한다.

## 확인할 질문

- shared abstraction이 기존 boundary와 맞는가?
- protocol, schema, enum, error code 변경이 compatible한가?
- downstream consumer가 깨지지 않도록 migration path가 있는가?
- policy, permission, validation logic이 한 곳에 일관되게 적용되는가?
- 새 abstraction이 실제 중복과 복잡도를 줄이는가?

## 산출물

- core contract 변경 요약
- consumer 영향 범위
- compatibility 검증 결과
- 남은 architecture risk
