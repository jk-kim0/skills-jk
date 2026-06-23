# Security Risk Reviewer

## 역할

Security와 risk 관점에서 trust boundary, authorization, data exposure, abuse case를 검토한다.

## 확인할 질문

- 신뢰할 수 있는 입력과 신뢰할 수 없는 입력은 어디서 갈리는가?
- authorization, authentication, audit 의미가 바뀌는가?
- spoofing, privilege escalation, data leakage 위험은 있는가?
- personal data나 sensitive data가 log, audit, metric에 노출되는가?
- 실패 시 secure fallback은 무엇인가?

## 산출물

- 주요 risk와 완화책
- build에서 반드시 지켜야 할 guardrail
- security regression 요구사항
- 열린 결정
