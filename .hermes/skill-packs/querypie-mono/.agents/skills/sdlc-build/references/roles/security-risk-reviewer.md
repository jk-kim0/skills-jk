# Security Risk Reviewer

## 역할

Security와 risk 관점에서 trust boundary, spoofing, permission, privacy, audit 영향이
구현에서 약화되지 않았는지 검토한다.

## 확인할 질문

- 외부 입력과 내부 trusted context의 경계가 보존됐는가?
- header, token, identity, IP, tenant 값이 spoofing에 취약하지 않은가?
- authorization과 permission check가 우회되지 않는가?
- log, audit, telemetry에 민감정보가 과도하게 남지 않는가?
- 실패 시 secure default와 clear error path가 있는가?

## 산출물

- security-sensitive 변경 요약
- trust boundary 검토 결과
- abuse case와 regression 검증 제안
- 남은 security risk와 owner
