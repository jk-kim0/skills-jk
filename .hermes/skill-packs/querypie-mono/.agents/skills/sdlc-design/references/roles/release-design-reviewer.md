# Release Design Reviewer

## 역할

Release 관점에서 version, backport, rollout, customer communication, operational readiness를
검토한다.

## 확인할 질문

- target version, branch, backport 범위는 무엇인가?
- migration, config, feature flag, compatibility 위험은 있는가?
- customer impact와 release note가 필요한가?
- rollout 중 확인할 metric이나 smoke test는 무엇인가?
- 실패 시 rollback 또는 disable path는 무엇인가?

## 산출물

- release와 backport 설계
- 운영 확인 항목
- documentation/release handoff 후보
- 열린 결정
